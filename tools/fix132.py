"""tv 132（2026-11-15）：差异清单第 17 批
佩拉 1106：
  1. 天赋「施放攻击后，若敌方目标处于负面效果，恢复 10 点能量」原来手动勾、不判断负面效果；
     引擎：条件 negMin（主目标身上的负面效果数 ≥N），energy 效果也能用。
  2. E6「攻击后目标有负面效果时 40% 攻击力附加伤害」XR 行原来「按一直有负面」；
     引擎：XR 行支持 negAny（主目标身上有负面效果才算），用伤害显示里按敌人记的减益快照判断。

用法：python _src/fix132.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 132
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 1：条件 negMin ----------------
old = 'if (!eff.eWl && !eff.eDk && !eff.eBr) return true;'
assert F.s.count(old) == 1, F.s.count(old)
F.rep(old, 'if (!eff.eWl && !eff.eDk && !eff.eBr && !eff.negMin) return true;')
old2 = 'if (eff.eDk && !(en.dots || []).some(d => !d.gone && [].concat(eff.eDk).some(k => k === "own" ? d.src === H.id : dkIs(d.k, k)))) return false;'
assert F.s.count(old2) == 1, F.s.count(old2)
F.rep(old2, old2 + ' if (eff.negMin && !(negOf(en) >= num(eff.negMin))) return false;   // 主目标身上的负面效果数 ≥N（佩拉天赋）')
old3 = 'if (eff.mBe != null || eff.mAtk != null || eff.eWl || eff.eDk || eff.eBr || eff.uPk) { const H = src ? (ownerOf(src) || src) : null; if (!H || !condX(eff, H)) return; }'
assert F.s.count(old3) == 1, F.s.count(old3)
F.rep(old3, 'if (eff.mBe != null || eff.mAtk != null || eff.eWl || eff.eDk || eff.eBr || eff.uPk || eff.negMin) { const H = src ? (ownerOf(src) || src) : null; if (!H || !condX(eff, H)) return; }')

# ---------------- 引擎 2：XR 行 negAny ----------------
anchor = 'if (r.eHpLe != null)'
assert F.s.count(anchor) == 1, F.s.count(anchor)
F.rep(anchor, 'if (r.negAny) { const A1 = rec && rec.eAll, mid1 = A1 && A1.ord ? A1.ord[0] : null, L1 = A1 && A1.m && mid1 != null ? A1.m[mid1] : null; if (!L1 || !L1.length) continue; }   // 主目标身上有负面效果（佩拉 E6）\n        ' + anchor)

F.rep('if (x.ku) e.killU = 1;',
      'if (x.ku) e.killU = 1; if (x.nmin != null) e.negMin = x.nmin;   // 主目标负面效果数 ≥N（佩拉天赋）')


# ---------------- 数据 ----------------
F.has('1106102', '若敌方目标处于负面效果状态，则额外恢复#点能量') if False else None
F.hast(1106, '追歼', '施放攻击后若目标处于负面效果状态') if False else None

# 1. 佩拉天赋：按主目标有负面判断、默认开
e = F.eff(1106, '天赋（攻击有负面效果的目标）')
oldn = e['n']
e['nmin'] = 1
e.pop('off', None)
e['n'] = '天赋：施放攻击后，若敌方目标处于负面效果状态，恢复 10 点能量（5 魂 11；按主目标身上的负面效果判断，每次攻击 1 次，默认开启）'
fx = F.FIX.setdefault('1106', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
fx['drop'].append(oldn)
fx['add'].append(e['n'])
fx['trig'][oldn] = 'atk'
fx['map'][oldn] = e['n']
fx.setdefault('off0', []).append(e['n'])

# 2. 佩拉 E6：XR 行按主目标有负面判断
row = next(x for x in F.XR['1106'] if x['k'] == 'e6')
row['negAny'] = True
row['n'] = 'E6：攻击后目标有负面效果时，造成 40% 攻击力的冰属性附加伤害（按主目标身上实际有没有负面效果判断）'

log = """<li><b>2026-11-15（差异清单第 17 批）：tv 132（tools/fix132.py）</b>。<b>佩拉</b>两条都改成按「目标身上有没有负面效果」判断：① <b>天赋</b>「施放攻击后，若敌方目标处于负面效果状态，额外恢复 10 点能量」原来手动勾、不管负面（默认关），现在按主目标的负面效果判断并默认开启。② <b>E6</b>「攻击后目标有负面效果时造成 40% 攻击力的冰属性附加伤害」原来「按一直有负面」都算，现在按主目标身上有没有负面判断。<b>对已有配置</b>：带佩拉的方案，天赋的回能只在目标真的挂上负面后才给（回能可能少一点、开大可能晚）；E6 的附加伤害也只在有负面时才算（伤害略降）。行动轴可能跟着变。</li>"""

record = """2026-11-15（差异清单第 17 批）：tv 132（tools/fix132.py）。引擎：条件 negMin（主目标负面数 ≥N，energy 等普通效果可用）、XR 行 negAny。改：佩拉天赋加 nmin 1、默认开；E6 XR 行加 negAny。
  未改 / 存疑：XR 的 negAny 用伤害显示里按敌人记的减益快照判断（有减益就算），不等同于完整的负面效果计数；佩拉 E6 的「攻击后」仍按本页的攻击类型判断。"""

F.finish('差异清单第 17 批（佩拉天赋 / E6 按目标负面效果判断）', log, record)
print('done tv', TV)
