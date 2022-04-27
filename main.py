from src import menu
import sys

assert sys.version_info >= (3, 8), print('Python version >=3.8 is required.\nYour Python version: ', sys.version)


def main():
    menu.main_menu(accountid=3)


if __name__ == '__main__':
    main()
