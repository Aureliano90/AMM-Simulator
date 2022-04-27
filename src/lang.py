import gettext
import os
from src.config import language

APP_NAME = "main"
LOCALE_DIR = os.path.abspath("./locale")
currentDir = os.path.dirname(os.path.realpath(__file__))
lang_zh_CN = gettext.translation(APP_NAME, LOCALE_DIR, ["zh_CN"])
lang_en = gettext.translation(APP_NAME, LOCALE_DIR, ["en"])

if language == 'cn':
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

cancelled_orders = _('Cancelled {} {} orders.')
# "已取消{} {}订单。"

placed_orders = _('Placed {} {} orders.')
# "已下{} {}订单。"

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

main_menu_text = _("""
1   Open new LP
2   Task manager
q   Quit
""")
# """
# 1   创建新LP
# 2   任务管理器
# q   退出
# """

manager_menu = _("""
1   Task list
2   Remove completed tasks
3   Stop all
b   Back""")
# """
# 1   任务列表
# 2   清理已完成
# 3   全部停止
# b   返回"""

manager_sub_menu = _("""
1   Cancel
2   Modify attribute
b   Back""")
# """
# 1   取消
# 2   更改属性
# b   返回"""

wrong_command = _('Wrong command')
# "错误指令"

cancelled = _(' is cancelled.')
# "已取消。"
