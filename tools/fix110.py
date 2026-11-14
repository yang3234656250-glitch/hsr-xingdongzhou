"""tv 110：卡厄斯兰那 —— 用户说明：第 8 个额外回合就在变身的最后，它结束变身也就结束。
所以 8 个额外回合排在变身总长（10000 ÷ (基础速度 × 60%)）里：第 1 个在开大后立刻，第 8 个在末尾，中间 7 个间隔；不再多一行“变身结束”。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 110, sys.argv[2])
C = F.C
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
c = C[1408]; m = c['sm'][0]; assert m['k'] == 'khaslana' and m['spb'] == 8 and m['tail'] == 1
m['spb'] = 7; m.pop('tail')
E = c['eff']; x = find(E, '终结技：变身，整段变身的速度'); o1 = x['n']
x['n'] = '终结技：变身，整段变身的速度 = 白厄基础速度 × 60%（1 魂 66%；基础速度含专武加的），第 1 个额外回合在开大后立刻，第 8 个（最后一击）在变身末尾，中间均分；其他队友离场'
old = [n for n in c['notes'] if n.startswith('卡厄斯兰那卡片上显示的速度')]; assert len(old) == 1
c['notes'] = [n for n in c['notes'] if n not in old] + ['卡厄斯兰那卡片上显示的速度 = 基础速度 × 60% × 7（7 个间隔用），不是游戏里的面板速度；第 8 个额外回合（最后一击）结束变身就结束，队友回场']
F.rebuild(1408, E, rename={o1: x['n']}, notes=c['notes'])
F.finish('卡厄斯兰那最后一击在末尾', '''<li><b>2026-11-14</b>：tv 110（tools/fix110.py）。卡厄斯兰那：第 8 个额外回合（最后一击）就在变身末尾，打完变身结束、队友回场；8 个额外回合之间是 7 个均分的间隔，不再多一行“变身结束”。</li>''',
'''2026-11-14：卡厄斯兰那最后一击在末尾 —— tv 110（tools/fix110.py）。用户说明：第 8 个就是在最后，结束了大招也就结束了。召唤物模板 spb 7、去掉 tail''')
