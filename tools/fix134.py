"""tv 134（2026-11-15）：差异清单第 19 批
给「额外伤害」补一个条件：主目标身上有某种持续伤害（dotAny）。
① 希露瓦 1103 天赋附加伤害 XR tf：原来「按敌人都触电算」→ 加 dotAny 触电
② 虎克 1109 天赋附加伤害 XR tf：原来「按一直有灼烧」→ 加 dotAny 灼烧

用法：python _src/fix134.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 134
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎：edbAll 带每个敌人身上的持续伤害 ----------------
old = 'uh: Object.fromEntries(U.filter(z => z.kind === "ally" && !z.sm).map(z => [z.id, hpPct(z)])) };'
assert F.s.count(old) == 1, F.s.count(old)
F.rep(old, 'uh: Object.fromEntries(U.filter(z => z.kind === "ally" && !z.sm).map(z => [z.id, hpPct(z)])), dot: Object.fromEntries(ens.map(z => [z.id, (z.dots || []).filter(d => !d.gone).map(d => d.k)])) };   // dot：每个敌人身上挂着的持续伤害种类（额外伤害按它判断）')

# ---------------- 引擎：XR 行支持 dotAny ----------------
anchor = 'if (r.negAny)'
assert F.s.count(anchor) == 1, F.s.count(anchor)
F.rep(anchor, 'if (r.dotAny) { const A2 = rec && rec.eAll, mid2 = A2 && A2.ord ? A2.ord[0] : null, L2 = A2 && A2.dot && mid2 != null ? A2.dot[mid2] : null; if (!L2 || ![].concat(r.dotAny).some(k => L2.some(z => z === k || String(z).includes(k)))) continue; }   // 主目标身上有这种持续伤害（希露瓦 / 虎克的附加伤害）\n        ' + anchor)

# ---------------- 数据 ----------------
for cid, key, dot, note in [
    (1103, 'tf', '触电', '天赋：攻击后对触电的敌人额外造成 72% 攻击力的附加伤害（5 魂 79.2%；按主目标身上有没有触电判断，有才算）'),
    (1109, 'tf', '灼烧', '天赋：攻击灼烧状态的敌人时，追加 1 次 100% 攻击力的附加伤害（5 魂 110%；按主目标身上有没有灼烧判断，有才算）'),
]:
    row = next(x for x in F.XR[str(cid)] if x['k'] == key)
    row['dotAny'] = dot
    row['n'] = note

log = """<li><b>2026-11-15（差异清单第 19 批）：tv 134（tools/fix134.py）</b>。「额外伤害」新增条件「主目标身上有某种持续伤害」（本页伤害显示现在带着每个敌人身上挂的持续伤害种类）：① <b>希露瓦</b>天赋附加伤害原来「按敌人都触电算」，现在按主目标身上有没有触电判断；② <b>虎克</b>天赋附加伤害原来「按一直有灼烧」，现在按主目标身上有没有灼烧判断。<b>对已有配置</b>：带这两人的方案，附加伤害只在目标真的挂着触电 / 灼烧时才算（伤害会降一段）；其他不变。</li>"""

record = """2026-11-15（差异清单第 19 批）：tv 134（tools/fix134.py）。引擎：edbAll 带 dot（每个敌人的持续伤害种类）、XR 行 dotAny。改：希露瓦 tf 加 dotAny 触电；虎克 tf 加 dotAny 灼烧。
  未改 / 存疑：希露瓦的天赋附加伤害在游戏里是「对每个触电的敌人各打一次」，这里按主目标是否触电判断、伤害仍按场上敌人总数（cnt N）算；虎克同理按主目标判断。"""

F.finish('差异清单第 19 批（希露瓦 / 虎克附加伤害按持续伤害状态判断）', log, record)
print('done tv', TV)
