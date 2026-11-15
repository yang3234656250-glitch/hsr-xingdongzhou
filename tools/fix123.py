"""tv 123（2026-11-15）：差异清单第 8 批
艾丝妲 1009 E4：原文「天赋的蓄能层数 ≥2 时，能量恢复效率 +15%」——页面是每回合开始无条件 +15%。
引擎：能量恢复效率（erbuff）也支持已有的 needBk = [bk, 属性, N]（持有这组增益 ≥N 层才生效，和翡翠 E2 同一个字段）

用法：python _src/fix123.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 123
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
anchor = 'if (eff.type === "erbuff") {'
assert F.s.count(anchor) == 1
gate = ('\n          if (Array.isArray(eff.needBk) && src) { const b = src.buffs.find(z => z.key === src.id + ":" + eff.needBk[0] + (eff.needBk[1] === "spd" ? "" : ":d" + eff.needBk[1])); '
        'if (!b || (b.n || 1) < num(eff.needBk[2])) continue; }   // 自己这组增益至少 N 层（艾丝妲 E4：蓄能 ≥2 层）')
F.rep(anchor, anchor + gate)


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


# ---------------- 艾丝妲 E4 ----------------
F.has('r:100904', '天赋的蓄能层数大于等于#时，艾丝妲的能量恢复效率提高#')
r4 = F.eid(1009, 4)
for e in r4['eff']:
    if e.get('y') == 'erbuff':
        e['nbk'] = ['xn', 'atkP', 2]
        e['n'] = 'E4 极光显现之时：天赋的蓄能层数 ≥2 时，艾丝妲的能量恢复效率 +15%，持续 2 回合'

log = """<li><b>2026-11-15（差异清单第 8 批）：tv 123（tools/fix123.py）</b>。<b>艾丝妲 E4</b>「天赋的蓄能层数 ≥2 时，能量恢复效率 +15%」：页面原来每回合开始就无条件 +15%（持续 2 回合）。能量恢复效率效果现在也能用「自己这组增益至少 N 层」这个条件（原本只有伤害增益支持），这条改成蓄能真的 ≥2 层才给。<b>对已有配置</b>：带艾丝妲的方案，蓄能掉到 1 层或 0 层时不再有那 15% 回能效率（回能略慢，开大可能晚一点）；蓄能一直在 2 层以上时不变。</li>"""

record = """2026-11-15（差异清单第 8 批）：tv 123（tools/fix123.py）。引擎：erbuff 复用已有 needBk = [bk, 属性, N]（原来只有伤害增益支持）。改：艾丝妲 E4 加 nbk ["xn","atkP",2]。
  未改 / 存疑：判定看的是艾丝妲自己身上那组蓄能增益（key「1009:xn:datkP」）的层数；E4 的持续 2 回合按艾丝妲自己的回合计时。"""

F.finish('差异清单第 8 批（艾丝妲 E4 蓄能层数门槛）', log, record)
print('done tv', TV)
