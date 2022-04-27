from src.lang import *
from src.amm import *

loop = asyncio.get_event_loop()


@call_coroutine
async def main_menu(accountid: int):
    try:
        assert isinstance(accountid, int)
        print(datetime_str(datetime.now()))
        fprint(f'{accountid=}')
        while (command := await ainput(loop, main_menu_text)) != 'q':
            if command == '1':
                while True:
                    coin = (await ainput(loop, input_crypto)).upper()
                    amm = await AMM(coin=coin, accountid=accountid)
                    if amm.exist:
                        break
                    else:
                        continue
                while True:
                    try:
                        usdt = float(await ainput(loop, input_lp_size))
                        assert usdt >= 0
                        break
                    except:
                        continue
                while True:
                    try:
                        grid_size = (await ainput(loop, input_grid)).rstrip('%')
                        grid_size = float(grid_size) / 100
                        assert grid_size > 0
                        break
                    except:
                        continue
                await amm.lp(usdt, grid_size)
            elif command == '2':
                await manager.menu()
            elif command == 'q':
                break
            else:
                print(wrong_command)
        await manager.stop()
    finally:
        await AMM.aclose()
    exit()
