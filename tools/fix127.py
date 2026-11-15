"""tv 127（2026-11-15）：差异清单第 12 批
桑博 1108 E6「天赋施加的风化状态的伤害倍率提高 15%」——原来没做（三条风化都没有 6 魂数值）。
引擎：持续伤害的 v6 支持数组 [不含 5 魂, 含 5 魂]，因为桑博的风化有 lv（5 魂 57.2%）。

用法：python _src/fix127.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 127
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
old = 'v: (num(own.eid) >= 6 && eff.v6 != null ? num(eff.v6) : v)'
assert F.s.count(old) == 1
F.rep(old, 'v: (num(own.eid) >= 6 && eff.v6 != null ? (Array.isArray(eff.v6) ? num(eff.v6[num(own.eid) >= 5 ? 1 : 0]) : num(eff.v6)) : v)')


def rename_eff(cid, frag, r=None, off0=None, drop_off=False, **chg):
    e = F.eff(cid, frag, r=r)
    oldn = e['n']
    trig = e.get('t')
    e.update(chg)
    if drop_off:
        e.pop('off', None)
    new = e['n']
    fx = F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
    fx['drop'].append(oldn)
    fx['add'].append(new)
    fx['trig'][oldn] = trig
    if new != oldn:
        fx['map'][oldn] = new
    if off0:
        fx.setdefault('off0', []).append(new)
    return oldn, new


# ---------------- 桑博 E6 ----------------
F.has('r:110806', '天赋施加的风化状态的伤害倍率提高#')
# 52% × 1.15 = 59.8；5 魂 57.2% × 1.15 = 65.78
for frag in ['天赋：普攻击中后使目标陷入风化', '天赋：战技 5 段', '天赋：终结技击中敌方全体后使目标陷入风化']:
    oldn, newn = rename_eff(
        1108, frag,
        v6=[59.8, 65.78],
        n=(F.eff(1108, frag)['n']).replace('（行迹圈套；基础概率按命中算）', '（行迹圈套；基础概率按命中算；6 魂时 59.8%，5 魂 65.78%）'),
    )

log = """<li><b>2026-11-15（差异清单第 12 批）：tv 127（tools/fix127.py）</b>。<b>桑博 E6</b>「天赋施加的风化状态的伤害倍率提高 15%」原来没做：三条风化（普攻 / 战技 / 终结技）现在都带上 6 魂数值——52% × 1.15 = <b>59.8%</b>，5 魂的 57.2% × 1.15 = <b>65.78%</b>（持续伤害的 6 魂专用数值现在支持「不含 5 魂 / 含 5 魂」两档）。<b>对已有配置</b>：只有 6 魂桑博受影响（风化每跳多 15%），行动轴不变。</li>"""

record = """2026-11-15（差异清单第 12 批）：tv 127（tools/fix127.py）。引擎：持续伤害 v6 支持数组 [不含 5 魂, 含 5 魂]。改：桑博三条风化加 v6 [59.8, 65.78]。
  未改 / 存疑：桑博 E4「战技击中风化 ≥5 层时立即产生原伤害 8%」还是没做（要判断敌人身上风化的层数阈值，dotx 目前没有这个条件）。"""

F.finish('差异清单第 12 批（桑博 E6 风化伤害 +15%）', log, record)
print('done tv', TV)
