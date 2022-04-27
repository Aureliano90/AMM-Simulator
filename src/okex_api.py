from okex.account import AccountAPI
from okex.public import PublicAPI
from okex.trade import TradeAPI
from src.config import Key
from src.manager import *
from asyncio import create_task, gather

manager = Manager()


@call_coroutine
# @debug_timer
class OKExAPI:
    """基本OKEx功能类
    """
    api_initiated = False
    __key = None

    def __init__(self, coin: str = None, accountid=3):
        self.accountid = accountid

        if not OKExAPI.api_initiated:
            apikey = Key(accountid)
            api_key = apikey.api_key
            secret_key = apikey.secret_key
            passphrase = apikey.passphrase
            OKExAPI.__key = dict(api_key=api_key, passphrase=passphrase, secret_key=secret_key)
            if accountid == 3:
                OKExAPI.accountAPI = AccountAPI(api_key, secret_key, passphrase, test=True)
                OKExAPI.tradeAPI = TradeAPI(api_key, secret_key, passphrase, test=True)
                OKExAPI.publicAPI = PublicAPI(test=True)
                OKExAPI.public_url = 'wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999'
                OKExAPI.private_url = 'wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999'
            else:
                OKExAPI.accountAPI = AccountAPI(api_key, secret_key, passphrase, False)
                OKExAPI.tradeAPI = TradeAPI(api_key, secret_key, passphrase, False)
                OKExAPI.publicAPI = PublicAPI()
                OKExAPI.public_url = 'wss://ws.okx.com:8443/ws/v5/public'
                OKExAPI.private_url = 'wss://ws.okx.com:8443/ws/v5/private'
                # OKExAPI.public_url = 'wss://wsaws.okx.com:8443/ws/v5/public'
                # OKExAPI.private_url = 'wss://wsaws.okx.com:8443/ws/v5/private'
            OKExAPI.api_initiated = True

        self.coin = coin
        if coin:
            assert isinstance(coin, str)
            self.spot_ID = coin + '-USDT'
            self.swap_ID = coin + '-USDT-SWAP'
            self.spot_info = None
            self.swap_info = None
            self.exitFlag = False
            self.exist = True
        else:
            self.exist = False

    def __await__(self):
        """异步构造函数\n
        await OKExAPI()先召唤__init__()，然后是awaitable __await__()。

        :return: OKExAPI
        """
        if self.coin:
            try:
                self.spot_info = create_task(self.spot_inst())
                yield from self.spot_info
                self.spot_info = self.spot_info.result()
                self.min_size = float(self.spot_info['minSz'])
                self.size_increment = float(self.spot_info['lotSz'])
                self.size_decimals = num_decimals(self.spot_info['lotSz'])
                self.tick_size = float(self.spot_info['tickSz'])
                self.tick_decimals = num_decimals(self.spot_info['tickSz'])
            except Exception as e:
                fprint(f'{type(self).__name__}__await__({self.coin}) error')
                fprint(e)
                self.exist = False
                fprint(lang.nonexistent_crypto.format(self.coin))
        else:
            self.exist = False
        return self

    @staticmethod
    async def aclose():
        if hasattr(OKExAPI, 'accountAPI'):
            await OKExAPI.accountAPI.aclose()
        if hasattr(OKExAPI, 'tradeAPI'):
            await OKExAPI.tradeAPI.aclose()
        if hasattr(OKExAPI, 'publicAPI'):
            await OKExAPI.publicAPI.aclose()

    @staticmethod
    def _key():
        return OKExAPI.__key

    async def spot_inst(self):
        return await self.publicAPI.get_specific_instrument('SPOT', self.spot_ID)

    async def swap_inst(self, swap_ID=None):
        if not swap_ID: swap_ID = self.swap_ID
        return await self.publicAPI.get_specific_instrument('SWAP', swap_ID)

    async def usdt_balance(self):
        """获取USDT保证金
        """
        return await self.spot_position('USDT')

    # @call_coroutine
    async def spot_position(self, coin=None):
        """获取现货余额
        """
        if not coin: coin = self.coin
        data: list = (await self.accountAPI.get_coin_balance(coin))['details']
        return float(data[0]['availEq']) if data else 0.
