"""tv 136（2026-11-15）：差异清单第 21 批
椒丘 1218 E6：原文「【烬煨】的层数上限提升至 9，每层【烬煨】会使目标的全属性抗性降低 3%」。
  页面原来按「叠满 9 层」写死：抗性 −27%、多出的 4 层易伤 +22%。
  引擎：条件 dkSt = [持续伤害名, 减去层数, 上限] —— 按目标身上这种持续伤害的实际层数当倍数。
  改：抗性那条 v 改成 3（×实际层数）；易伤那条 v 改成 5（×(层数−5)，最多 4 层 = 20%，加上天赋 5 层 35% 共 55%，和原文对得上）。

用法：python _src/fix136.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 136
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎：条件 dkSt ----------------
old = 'c.est == null && c.dfr == null && c.dbf == null && c.dbn == null && c.nwk == null) return f0;'
assert F.s.count(old) == 1, F.s.count(old)
F.rep(old, 'c.est == null && c.dfr == null && c.dbf == null && c.dbn == null && c.nwk == null && c.dkSt == null) return f0;')

old2 = 'if (c.dk && !ds.some(d => [].concat(c.dk).some(k => k === "own" ? d.src === b.src : dkIs(d.k, k)))) return 0;'
assert F.s.count(old2) == 1, F.s.count(old2)
F.rep(old2, old2 + '\n      if (Array.isArray(c.dkSt)) { const d0 = ds.find(d => dkIs(d.k, c.dkSt[0])), n0 = d0 ? Math.min(num(c.dkSt[2], 99), Math.max(0, (d0.n || 1) - num(c.dkSt[1], 0))) : 0; if (!(n0 > 0)) return 0; f0 *= n0; }   // 按这种持续伤害的实际层数（椒丘 E6 烬煨）')

# ---------------- 数据：椒丘 E6 两条改成按层数 ----------------
F.has('r:121806', '【烬煨】的层数上限提升至#，每层【烬煨】会使目标的全属性抗性降低#')
for e in F.C[1218]['eid']:
    for z in e['eff']:
        n = z.get('n') or ''
        if n.startswith('E6：【烬煨】上限 9 层，每层全属性抗性'):
            z['v'] = 3
            z['ec'] = {'dkSt': ['烬煨', 0, 9]}
            z['n'] = 'E6：【烬煨】上限 9 层，每层使目标全属性抗性 −3%（按实际层数算，最多 9 层）'
            F.touch(1218)
        elif n.startswith('E6：【烬煨】上限 9 层，多出的 4 层'):
            z['v'] = 5
            z['ec'] = {'dkSt': ['烬煨', 5, 4]}
            z['n'] = 'E6：超过 5 层的【烬煨】每层再使目标受到的伤害 +5%（最多 4 层 = 20%，和天赋 5 层的 35% 相加）'
            F.touch(1218)

log = """<li><b>2026-11-15（差异清单第 21 批）：tv 136（tools/fix136.py）</b>。<b>椒丘 E6</b>「【烬煨】层数上限提升至 9，每层使目标全属性抗性 −3%」原来按「叠满 9 层」写死（抗性 −27%、多出的 4 层易伤 +22%）。现在新增「按某种持续伤害的实际层数」这个条件：抗性那条 = 3% × 实际层数（最多 9 层）；易伤那条 = 5% × 超过 5 层的部分（最多 4 层），和天赋「5 层 35%」相加，9 层时正好 55%。<b>对已有配置</b>：带椒丘且开了 6 魂的方案，烬煨层数不足时抗性 / 易伤会按实际层数少算（伤害略降），叠满时不变。</li>"""

record = """2026-11-15（差异清单第 21 批）：tv 136（tools/fix136.py）。引擎：条件 dkSt = [持续伤害名, 减去层数, 上限]（倍数）。改：椒丘 E6 抗性 −27 改 3 × 层数；易伤 +22 改 5 × (层数−5)。
  未改 / 存疑：天赋那条「5 层 35%」仍是写死的（层数不足 5 时按满额），要一起按层算可以照这个方式再改。"""

F.finish('差异清单第 21 批（椒丘 E6 烬煨按实际层数）', log, record)
print('done tv', TV)
