from math import sqrt

from okex_api import *
from utils import *


class AMM(OKExAPI):

    @property
    def __name__(self):
        return 'AMM'

    def __init__(self, coin=None, accountid=3):
        super().__init__(coin=coin, accountid=accountid)

    @run_with_cancel
    async def lp(self, usdt=0, grid_size=0.01):
        begin = timestamp = datetime.utcnow()
        # Risk-free interest rate
        r = 0.05
        grid_num = 20
        min_size = float(self.spot_info['minSz'])
        size_increment = float(self.spot_info['lotSz'])
        size_decimals = num_decimals(self.spot_info['lotSz'])
        tick_size = float(self.spot_info['tickSz'])
        tick_decimals = num_decimals(self.spot_info['tickSz'])
        trade_fee, usdt_balance, spot_ticker, spot_position = await gather(
            self.accountAPI.get_trade_fee(instType='SPOT', instId=self.spot_ID), self.usdt_balance(),
            self.publicAPI.get_specific_ticker(self.spot_ID), self.spot_position())
        taker_fee = float(trade_fee['taker'])
        maker_fee = float(trade_fee['maker'])
        initial_price = last = float(spot_ticker['last'])

        Record = record.Record('AMM')
        # Manage existing LP position
        if usdt == 0:
            mydict = Record.find_last(dict(account=self.accountid, instrument=self.coin, op='open'))
            k = mydict['k']
            begin = mydict['timestamp']
            initial_price = mydict['price']
        # Open new LP position
        else:
            assert usdt_balance > usdt / 2, fprint(lang.insufficient_USDT)
            # n1*n2=k n1=sqrt(k/p1) v=2*n1*p1=2*sqrt(k*p1)
            k = (usdt / 2) ** 2 / initial_price
            mydict = dict(account=self.accountid, instrument=self.coin, timestamp=timestamp, k=k, op='open',
                          price=initial_price)
            Record.mycol.insert_one(mydict)

        n1 = ni = sqrt(k / last)
        if spot_position < ni:
            spot_size = round_to((ni - spot_position) / (1 + taker_fee), size_increment)
            if spot_size >= min_size:
                spot_order = await self.tradeAPI.take_spot_order(instId=self.spot_ID, side='buy', size=spot_size,
                                                                 tgtCcy='base_ccy', order_type='market')
                assert spot_order['ordId'] != '-1', fprint(spot_order)
                if usdt == 0:
                    spot_order = await self.tradeAPI.get_order_info(instId=self.spot_ID, order_id=spot_order['ordId'])
                    spot_filled = float(spot_order['accFillSz']) + float(spot_order['fee'])
                    spot_price = float(spot_order['avgPx'])
                    spot_fee = float(spot_order['fee']) * spot_price
                    spot_notional = - k * spot_filled / spot_position / (spot_position + spot_filled)
                    mydict = dict(account=self.accountid, instrument=self.coin, timestamp=timestamp, op='buy', k=k,
                                  cash_notional=- spot_filled * spot_price, spot_notional=spot_notional, fee=spot_fee)
                    Record.mycol.insert_one(mydict)

        def stat():
            pipeline = [
                {'$match': {'account': self.accountid, 'instrument': self.coin, 'timestamp': {'$gt': begin}}},
                {'$group': {'_id': '$instrument', 'cash_notional': {'$sum': '$cash_notional'},
                            'spot_notional': {'$sum': '$spot_notional'}, 'fee': {'$sum': '$fee'}}}]
            res = [x for x in Record.mycol.aggregate(pipeline)]
            if res:
                cash_notional = res[0]['cash_notional']
                spot_notional = res[0]['spot_notional']
                fee_total = res[0]['fee']
                spot_price = k / n1 ** 2
                lp_value = 2. * k / n1
                lp_pnl = cash_notional - spot_notional + fee_total
                period = (datetime.utcnow() - begin).total_seconds() / 86400 / 365
                theta = lp_pnl / period
                gamma = - 0.5 * n1 / spot_price
                # theta + 0.5 * sigma**2 * spot_price**2 * gamma + r * (spot_price * delta - lp_value) == 0
                sigma2 = - (theta - r * 0.5 * lp_value) / (0.5 * spot_price ** 2 * gamma)
                if sigma2 > 0:
                    sigma = sqrt(sigma2)
                    fprint(f'LP APR={theta / lp_value:7.2%}')
                    fprint(lang.rv.format(sigma))
                else:
                    fprint(f'{sigma2=:7.2%}, {(theta - r * 0.5 * lp_value) / lp_value=:7.2%}')
                    fprint(f'{2. * sqrt(k * initial_price):8.2f}, {cash_notional + fee_total:8.2f},'
                           f' {spot_notional:8.2f}, {lp_value:8.2f}')

        stat()

        async def cancel_orders():
            pending = await self.tradeAPI.pending_order(instType='SPOT', instId=self.spot_ID, state='live')
            orders = [dict(instId=self.spot_ID, ordId=order['ordId']) if order['ordId']
                      else dict(instId=self.spot_ID, clOrdId=order['clOrdId']) for order in pending]
            if orders:
                await self.tradeAPI.batch_cancel(orders)
                fprint(lang.cancelled_orders.format(len(orders)))

        await cancel_orders()

        grids = []
        a = sqrt(1 + grid_size)
        b = 1 / a

        async def init_grids():
            nonlocal grids
            orders = []
            grids.append(dict(index=grid_num // 2, price=last, order=None))
            index = grid_num // 2 + 1
            sell_price = round_to(last * a ** 2, tick_size)
            sell_size = round_to(ni * (1 - b), size_increment)
            while sell_size >= min_size and abs(index - grid_num // 2) <= grid_num // 2:
                order = dict(instId=self.spot_ID, tdMode='cash', side='sell', ordType='limit',
                             clOrdId=self.coin + 'grid' + str(index), px=float_str(sell_price, tick_decimals),
                             sz=float_str(sell_size, size_decimals))
                orders.append(order)
                grid = dict(index=index, price=sell_price, order=order)
                grids.append(grid)
                index += 1
                sell_price = round_to(sell_price * a ** 2, tick_size)
                sell_size = round_to(sell_size * b, size_increment)

            index = grid_num // 2 - 1
            buy_price = round_to(last * b ** 2, tick_size)
            buy_size = round_to(ni * (a - 1) / (1 + maker_fee), size_increment)
            while buy_size >= min_size and abs(index - grid_num // 2) <= grid_num // 2:
                order = dict(instId=self.spot_ID, tdMode='cash', side='buy', ordType='limit',
                             clOrdId=self.coin + 'grid' + str(index), px=float_str(buy_price, tick_decimals),
                             sz=float_str(buy_size, size_decimals))
                orders.append(order)
                grid = dict(index=index, price=buy_price, order=order)
                grids.append(grid)
                index -= 1
                buy_price = round_to(buy_price * b ** 2, tick_size)
                buy_size = round_to(buy_size * a, size_increment)
            grids.sort(key=lambda x: x['index'])

            if orders:
                orders = await self.tradeAPI.batch_order(orders)
                for order in orders:
                    assert order['sCode'] == '0', fprint(order)
            else:
                sell_size = round_to(ni * (1 - b), size_increment)
                buy_size = round_to(ni * (a - 1) / (1 + maker_fee), size_increment)
                fprint(f'{sell_size >= min_size=}, {buy_size >= min_size=}')
                fprint(lang.use_larger_grid)

        await init_grids()
        index = grid_num // 2

        async def move_grids():
            nonlocal grids, ni, last
            grids = []
            await cancel_orders()
            ni = n1
            last = k / n1 ** 2
            await init_grids()

        kwargs = OKExAPI._key()
        kwargs['channels'] = [dict(channel='orders', instType='SPOT', instId=self.spot_ID)]

        try:
            async for current_order in subscribe(self.private_url, **kwargs):
                current_order = current_order['data'][0]
                timestamp = utcfrommillisecs(current_order['uTime'])
                fprint(datetime_str(utc_to_local(timestamp)), current_order['clOrdId'], current_order['side'],
                       current_order['px'], current_order['state'])
                # 下单成功
                if current_order['state'] == 'filled':
                    index = current_order['clOrdId'][current_order['clOrdId'].find('grid') + 4:]
                    index = int(index)
                    n1 = ni * pow(b, index - grid_num // 2)
                    spot_price = float(current_order['avgPx'])
                    spot_fee = float(current_order['fee'])
                    if current_order['side'] == 'sell':
                        spot_filled = float(current_order['accFillSz'])
                        cash_notional = spot_filled * spot_price
                        spot_notional = k * spot_filled / n1 / (n1 + spot_filled)
                        mydict = dict(account=self.accountid, instrument=self.coin, timestamp=timestamp,
                                      op='sell', cash_notional=cash_notional, spot_notional=spot_notional,
                                      fee=spot_fee, k=k)
                        Record.mycol.insert_one(mydict)

                        if abs(index - grid_num // 2) == grid_num // 2:
                            await move_grids()
                        else:
                            buy_price = round_to(k / (n1 * a) ** 2, tick_size)
                            buy_size = round_to(n1 * (a - 1) / (1 + maker_fee), size_increment)
                            buy_price = float_str(buy_price, tick_decimals)
                            buy_size = float_str(buy_size, size_decimals)
                            kwargs = dict(instId=self.spot_ID, side='buy', size=buy_size, price=buy_price,
                                          order_type='limit', client_oid=self.coin + 'grid' + str(index - 1))
                            buy_order = create_task(self.tradeAPI.take_spot_order(**kwargs))
                            buy_order = await buy_order
                            assert buy_order['ordId'] != '-1', fprint(buy_order)
                    elif current_order['side'] == 'buy':
                        spot_filled = float(current_order['accFillSz']) + spot_fee
                        cash_notional = - spot_filled * spot_price
                        spot_notional = - k * spot_filled / n1 / (n1 - spot_filled)
                        mydict = dict(account=self.accountid, instrument=self.coin, timestamp=timestamp,
                                      op='buy', cash_notional=cash_notional, spot_notional=spot_notional,
                                      fee=spot_fee, k=k)
                        Record.mycol.insert_one(mydict)

                        if abs(index - grid_num // 2) == grid_num // 2:
                            await move_grids()
                        else:
                            sell_price = round_to(k / (n1 * b) ** 2, tick_size)
                            sell_price = float_str(sell_price, tick_decimals)
                            sell_size = round_to(n1 * (1 - b), size_increment)
                            sell_size = float_str(sell_size, size_decimals)
                            kwargs = dict(instId=self.spot_ID, side='sell', size=sell_size, price=sell_price,
                                          order_type='limit', client_oid=self.coin + 'grid' + str(index + 1))
                            sell_order = create_task(self.tradeAPI.take_spot_order(**kwargs))
                            sell_order = await sell_order
                            assert sell_order['ordId'] != '-1', fprint(sell_order)
                    else:
                        fprint(current_order)

                    stat()

        except asyncio.CancelledError:
            fprint(datetime_str(datetime.now()))
            n1 = ni * pow(b, index - grid_num // 2)
            price = round_to(k / n1 ** 2, tick_size)
            fprint(f'{lang.grid_index}={index} {lang.spot_size}={n1:.{size_decimals}f} '
                   f'{lang.price}={price:.{tick_decimals}f}')
            orders = []
            for grid in grids:
                if grid['order']:
                    orders.append(
                        self.tradeAPI.get_order_info(instId=self.spot_ID, client_oid=grid['order']['clOrdId']))
            assert len(orders) <= 60
            orders = await gather(*orders)
            for order in orders:
                if order['state'] != 'live':
                    index = order['clOrdId'][order['clOrdId'].find('grid') + 4:]
                    index = int(index)
                    n1 = ni * pow(b, index - grid_num // 2)
                    price = round_to(k / n1 ** 2, tick_size)
                    fprint(f"{lang.grid_index}={index} {lang.spot_size}={n1:.{size_decimals}f} "
                           f"{lang.price}={price:.{tick_decimals}f} {lang.side}={order['side']} "
                           f"{lang.state}={order['state']}")
            await cancel_orders()
