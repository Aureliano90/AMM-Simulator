import amm
from utils import *
from lang import *
import sys

assert sys.version_info >= (3, 8), print('Python version >=3.8 is required.\nYour Python version: ', sys.version)


def main():
    print(datetime_str(datetime.now()))
    try:
        while True:
            coin = input(input_crypto).upper()
            AMM = amm.AMM(coin=coin, accountid=3)
            if AMM.exist:
                break
            else:
                continue
        while True:
            try:
                usdt = float(input(input_lp_size))
                assert usdt >= 0
                break
            except:
                continue
        while True:
            try:
                grid_size = input(input_grid).rstrip('%')
                grid_size = float(grid_size) / 100
                assert grid_size > 0
                break
            except:
                continue
        AMM.lp(usdt, grid_size)
    finally:
        amm.AMM.clean()
    exit()


if __name__ == '__main__':
    main()
