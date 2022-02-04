import gettext
import os
import config

APP_NAME = "main"
LOCALE_DIR = os.path.abspath("locale")
currentDir = os.path.dirname(os.path.realpath(__file__))
lang_zh_CN = gettext.translation(APP_NAME, LOCALE_DIR, ["zh_CN"])
lang_en = gettext.translation(APP_NAME, LOCALE_DIR, ["en"])

if config.language == 'cn':
    lang_zh_CN.install()
else:
    lang_en.install()

input_crypto = _('Input crypto\n')
# "输入币种\n"

input_lp_size = _('Input LP position size in USDT. Input 0 to resume.\n')
# "输入LP大小，单位USDT。输入0恢复现有仓位。\n"

input_grid = _('Input grid size, i.e. 1%\n')
# "输入网格大小，如1%\n"

insufficient_USDT = _('Insufficient USDT')
# 'USDT余额不足'

input_q_abort = _('Input q to abort\n')
# "输入q中止\n"

nonexistent_account = _('Account does not exist.')
# "账户不存在。"

nonexistent_crypto = _('Crypto {:s} does not exist.')
# "{:s}币种不存在。"

rv = _('Realized volatility={:7.2%}')
# "实现波动率={:7.2%}"

cancelled_orders = _('Cancelled {} orders.')
# "已取消{}订单。"

use_larger_grid = _('Use larger grid.')
# "用更大网格。"

grid_index = _('Grid index')
# "格子"

spot_size = _('Spot size')
# "现货仓位"

price = _('Price')
# "价格"

side = _('Side')
# "方向"

state = _('State')
# "状态"
