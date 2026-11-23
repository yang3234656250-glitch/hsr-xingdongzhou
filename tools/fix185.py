"""tv 185（2026-11-23）：差异清单第 61 批
知更鸟 E6（130906）“【月隐的午夜】效果最多触发 8 次，每次施放终结技时重置触发次数”：
XR xz 的 cdE（+450% 暴伤）以前对【协奏】期间每一次附加伤害都生效。加 XR 字段 cdN 8：按 R_REF 数知更鸟最近一次开大之后、
这次攻击之前我方的攻击次数（回合行动按 atkSkill / atkUlt 判断是不是攻击、开大、追击标记），满 8 次后不再加暴伤。
同一行动值上的先后：回合行动按序号；开大 / 追击标记没有序号，按行动值严格先后算。

用法：python3 tools/fix185.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 185
F = Fix(sys.argv[1], TV, sys.argv[2])
R = json.load(open(os.path.join(sys.argv[2], 'character_ranks.json'), encoding='utf-8'))
assert '效果最多触发8次，每次施放终结技时重置触发次数' in R['130906']['desc']
xz = [r for r in F.XR['1309'] if r['k'] == 'xz']; assert len(xz) == 1 and xz[0]['cdE'] == [6, 450] and 'cdN' not in xz[0]
xz[0]['cdN'] = 8
F.rep('          if (r.crit) crit = 1 + Math.min(1, r.crit[0] / 100) * (r.crit[1] + (r.cdE && num(o.eid) >= r.cdE[0] ? r.cdE[1] : 0)) / 100;',
      '          if (r.crit) crit = 1 + Math.min(1, r.crit[0] / 100) * (r.crit[1] + (r.cdE && num(o.eid) >= r.cdE[0] && !(r.cdN && atkSinceUlt(o, rec) >= r.cdN) ? r.cdE[1] : 0)) / 100;   // cdN：每次开大后最多 N 次（知更鸟 E6，tv 185）')
F.rep('  function riderDmg(u, e, rec, DB0, c) {',
      '  // 持有者 o 最近一次开大之后、rec 之前，我方一共攻击了几次（回合行动 / 开大 / 追击；tv 185 知更鸟 E6 的 8 次上限）\n'
      '  function atkSinceUlt(o, rec) {\n'
      '    if (!R_REF || !rec) return 0;\n'
      '    const by = Object.fromEntries(allUnits().map(z => [z.id, z])), X = z => (tplOf(z) || {}).x || {};\n'
      '    let tU = null; for (const m of R_REF.ultMarks || []) if (m.uid === o.id && m.t <= rec.t + 1e-9 && m !== rec && (tU == null || m.t > tU)) tU = m.t;\n'
      '    if (tU == null) return 0;\n'
      '    const before = (z, sq) => z.t < rec.t - 1e-9 || (Math.abs(z.t - rec.t) < 1e-9 && sq && z.seq != null && rec.seq != null && z.seq < rec.seq);\n'
      '    let n = 0;\n'
      '    for (const a of R_REF.actions || []) { const w = by[a.uid]; if (!w || w.kind !== "ally" || a === rec || !(a.t >= tU - 1e-9) || !before(a, true)) continue;\n'
      '      if (w.sm ? !(w.sm.fua || w.sm.mem) : !a.act || ((a.act === "skill" || a.act === "fskill") && (w.atkSkill === false || X(w).atkSkill === false))) continue; n++; }\n'
      '    for (const m of R_REF.ultMarks || []) { const w = by[m.uid]; if (!w || w.kind !== "ally" || m === rec || !(m.t > tU + 1e-9) || !before(m)) continue; if (w.atkUlt === false || X(w).atkUlt === false) continue; n++; }\n'
      '    for (const m of R_REF.marks || []) { if (m === rec || !m.key || !/追击/.test(m.label || "") || !(m.t >= tU - 1e-9) || !before(m)) continue; const w = by[m.uid]; if (w && w.kind === "ally") n++; }\n'
      '    return n;\n'
      '  }\n'
      '  function riderDmg(u, e, rec, DB0, c) {')
log = """<li><b>2026-11-23（差异清单第 61 批）：tv 185（tools/fix185.py）</b>。知更鸟 6 魂“【月隐的午夜】效果最多触发 8 次，每次施放终结技时重置”：协奏附加伤害的 +450% 暴伤只给每次开大后我方的前 8 次攻击（回合行动、开大、追击都算），以前协奏期间每次都给。<b>对已有配置</b>：只影响 6 魂知更鸟的伤害显示。</li>"""
record = """2026-11-23（差异清单第 61 批）：tv 185（tools/fix185.py）。XR cdN + atkSinceUlt（知更鸟 E6 8 次）。"""
F.finish('差异清单第 61 批（知更鸟 6 魂 8 次上限）', log, record)
print('done tv', TV)
