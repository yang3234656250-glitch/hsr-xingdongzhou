"""tv 121（2026-11-15）：差异清单第 6 批
艾丝妲 1009：E2「施放终结技时，下回合不会减少蓄能层数」+ E6「天赋每回合减少的蓄能层数降低 1」
原来每回合一律 −3 层，两条星魂都没做。
引擎：增益叠层支持 e6n（6 魂时负的 stAdd 少减 1）、turnSkip（有某状态下这次不减）

用法：python _src/fix121.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 121
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
anchor = '        const old = tg.buffs.find(b => b.key === kk);'
assert F.s.count(anchor) == 1
F.rep(anchor, '        if (eff.turnSkip && src && hasSt(src, eff.turnSkip) && num(eff.stAdd) < 0) continue;   // 艾丝妲 E2：有「蓄能不减」时这次不减\n' + anchor)
F.rep('let n = lim > 0 ? Math.min(lim, (old ? old.n || 1 : 0) + (Math.round(num(eff.stAdd, 1)) || 1)) : 1;',
      'let n = lim > 0 ? Math.min(lim, (old ? old.n || 1 : 0) + (Math.round(num(eff.stAdd, 1) + (eff.e6n && src && num(src.eid) >= 6 ? 1 : 0)) || 1)) : 1;')
F.rep('if (x.sa) e.stAdd = x.sa;',
      'if (x.sa) e.stAdd = x.sa; if (x.e6n) e.e6n = 1; if (x.turnSkip) e.turnSkip = x.turnSkip;   // 6 魂少减 1 层 / 有某状态时这次不减（艾丝妲）')


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


# ---------------- 艾丝妲 ----------------
F.has('r:100902', '施放终结技时，艾丝妲下回合不会减少蓄能层数')
F.has('r:100906', '天赋每回合减少的蓄能层数降低#')
rename_eff(
    1009, '天赋：从自身的第 2 回合开始，每回合开始时蓄能 −3 层',
    e6n=1, turnSkip='蓄能不减',
    n='天赋：从自身的第 2 回合开始，每回合开始时蓄能 −3 层（6 魂只减 2 层；有 E2 的「蓄能不减」时这次不减）',
)
r2 = F.eid(1009, 2)
r2['eff'].append({
    'y': 'state', 't': 'ult', 'tg': 'self', 'sn': '蓄能不减', 'd': 1, 'v': 1,
    'n': 'E2 月见圆缺之意：施放终结技后，下回合不会减少蓄能层数',
})

log = """<li><b>2026-11-15（差异清单第 6 批）：tv 121（tools/fix121.py）</b>。<b>艾丝妲</b>两条星魂原来都没做（每回合一律蓄能 −3 层）：① <b>E2 月见圆缺之意</b>「施放终结技时，艾丝妲下回合不会减少蓄能层数」——开大后给一个 1 回合的「蓄能不减」状态，那一次减层跳过。② <b>E6 眠于银河之下</b>「天赋每回合减少的蓄能层数降低 1」——6 魂时每回合只减 2 层。<b>对已有配置</b>：带艾丝妲、并且打了几轮的方案，蓄能层数会比以前高（攻击力增益更高），行动轴可能跟着变（艾丝妲自己的伤害 / 拉条不受影响，主要是全队攻击力）。没开艾丝妲星魂的方案数字会略有不同（6 魂前不变，E2 要开大后那一回合才变）。</li>"""

record = """2026-11-15（差异清单第 6 批）：tv 121（tools/fix121.py）。引擎：增益叠层 e6n（6 魂负 stAdd 少减 1）、turnSkip（有该状态时这次不减）+ 模板字段透传。改：艾丝妲 −3 层那条加 e6n / turnSkip；E2 补「蓄能不减」状态行。
  未改 / 存疑：E2 的「下回合」按状态持续 1 回合近似（艾丝妲自己的回合计时）；E4「蓄能层数 ≥2 时能量恢复效率 +15%」仍是每回合无条件 +15%（还没按层数判断）。"""

F.finish('差异清单第 6 批（艾丝妲 E2 / E6 蓄能层数）', log, record)
print('done tv', TV)
