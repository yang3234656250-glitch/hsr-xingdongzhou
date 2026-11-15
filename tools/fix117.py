"""tv 117（2026-11-15）：差异清单第 2 批
① 姬子 1003 秘技不完全燃烧：敌方受到火属性伤害 +10% 只对火属性攻击生效（tel），并从默认关改成默认开
② 瓦尔特 1004【强化版】行迹惩戒：我方攻击【失重】目标时伤害 +10% 加上条件（ec est 失重），原来没判断失重

用法：python _src/fix117.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 117
F = Fix('星铁行动轴.html', TV, '_src')


def rename_eff(cid, frag, r=None, off0=None, drop_off=False, **chg):
    e = F.eff(cid, frag, r=r)
    old = e['n']
    trig = e.get('t')
    e.update(chg)
    if drop_off:
        e.pop('off', None)
    new = e['n']
    fx = F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
    fx['drop'].append(old)
    fx['add'].append(new)
    fx['trig'][old] = trig
    if new != old:
        fx['map'][old] = new
    if off0:
        fx.setdefault('off0', []).append(new)
    return old, new


# ① 姬子秘技：只算火属性攻击，默认开
rename_eff(
    1003, '秘技不完全燃烧',
    tel='火',
    n='秘技不完全燃烧：进入战斗时敌方受到的火属性伤害 +10%，持续 2 回合（只对火属性攻击生效，默认开启）',
    drop_off=True, off0=True,
)

# ② 瓦尔特行迹惩戒：只对身上有【失重】的敌人生效
rename_eff(
    1004, '【强化版】行迹惩戒：我方攻击【失重】目标时伤害',
    ec={'est': '失重'},
    n='【强化版】行迹惩戒：我方攻击【失重】状态下的敌方目标时伤害 +10%，最多 10 层，持续 2 回合（按每次攻击 1 层；只对身上有【失重】的敌人生效）',
)

log = """<li><b>2026-11-15（差异清单第 2 批）：tv 117（tools/fix117.py）</b>。两条：① <b>姬子</b>秘技【不完全燃烧】原文是「敌方目标受到的<b>火属性</b>伤害提高 10%」，页面原来对全部伤害生效、所以只能默认关着；现在伤害增益支持按属性过滤，这条改成只对火属性攻击生效并<b>默认开启</b>。② <b>瓦尔特【强化版】</b>行迹惩戒原文是攻击「处于【失重】状态下的敌方目标」时增伤，页面原来没判断【失重】（对谁都加），现在按目标身上有没有【失重】判断。<b>对已有配置</b>：姬子这条只影响伤害显示（队里没有火属性以外的人打伤害时数字不变）；瓦尔特这条会少算对没【失重】目标的增伤，伤害数字降一点，行动轴不变。旧配置载入时自动换成新写法（姬子这条按原文改成默认开）。</li>"""

record = """2026-11-15（差异清单第 2 批）：tv 117（tools/fix117.py）。改：姬子秘技不完全燃烧加 tel 火 + 默认开（off0）；瓦尔特行迹惩戒加 ec est 失重。
  未改 / 存疑：姬子秘技的 10% 是敌方易伤（vuln），按攻击者属性过滤；如果游戏里是「火属性伤害」乘区而非易伤，数字会有细微差别（原文写的是「受到的火属性伤害提高」，按易伤算）。"""

F.finish('差异清单第 2 批（姬子秘技火属性 / 瓦尔特惩戒失重）', log, record)
print('done tv', TV)
