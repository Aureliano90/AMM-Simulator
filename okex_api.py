import okex.account as account
import okex.public as public
import okex.trade as trade
import config
import record
from utils import *
from asyncio import create_task, gather
from websocket import subscribe, subscribe_without_login


@call_coroutine
# @debug_timer
class OKExAPI(object):
    """基本OKEx功能类
    """
    api_initiated = False
    asleep = 0.
    __key = None

    @property
    def __name__(self):
        return 'OKExAPI'

    def __init__(self, coin: str = None, accountid=3):
        self.accountid = accountid

        if not OKExAPI.api_initiated:
            apikey = config.Key(accountid)
            api_key = apikey.api_key
            secret_key = apikey.secret_key
            passphrase = apikey.passphrase
            OKExAPI.__key = dict(api_key=api_key, passphrase=passphrase, secret_key=secret_key)
            if accountid == 3:
                OKExAPI.accountAPI = account.AccountAPI(api_key, secret_key, passphrase, test=True)
                OKExAPI.tradeAPI = trade.TradeAPI(api_key, secret_key, passphrase, test=True)
                OKExAPI.publicAPI = public.PublicAPI(test=True)
                # OKExAPI.public_url = 'wss://wspap.okx.com:8443/ws/v5/public'
                # OKExAPI.private_url = 'wss://wspap.okx.com:8443/ws/v5/private'
                OKExAPI.public_url = 'wss://wspap.okex.com:8443/ws/v5/public?brokerId=9999'
                OKExAPI.private_url = 'wss://wspap.okex.com:8443/ws/v5/private?brokerId=9999'
            else:
                OKExAPI.accountAPI = account.AccountAPI(api_key, secret_key, passphrase, False)
                OKExAPI.tradeAPI = trade.TradeAPI(api_key, secret_key, passphrase, False)
                OKExAPI.publicAPI = public.PublicAPI()
                # OKExAPI.public_url = 'wss://ws.okx.com:8443/ws/v5/public'
                # OKExAPI.private_url = 'wss://ws.okx.com:8443/ws/v5/private'
                OKExAPI.public_url = 'wss://ws.okex.com:8443/ws/v5/public'
                OKExAPI.private_url = 'wss://ws.okex.com:8443/ws/v5/private'
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
            except Exception as e:
                fprint(f'{self.__name__}__await__({self.coin}) error')
                fprint(e)
                self.exist = False
                fprint(lang.nonexistent_crypto.format(self.coin))
        else:
            self.exist = False
        return self

    @staticmethod
    def clean():
        if hasattr(OKExAPI, 'accountAPI'):
            OKExAPI.accountAPI.__del__()
        if hasattr(OKExAPI, 'tradeAPI'):
            OKExAPI.tradeAPI.__del__()
        if hasattr(OKExAPI, 'publicAPI'):
            OKExAPI.publicAPI.__del__()

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
