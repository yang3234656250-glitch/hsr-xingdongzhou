"""tv 179（2026-11-23）：差异清单第 55 批
景元【神君】、托帕【账账】这类“行动算追加攻击”的召唤物（sm.fua），自己行动那一行以前没有伤害（DMGX.mem 没有这些角色，memDmgOf 返回 null），伤害合计也不含。
现在没有 DMGX.mem 规格的 sm.fua 召唤物按主人的追加攻击倍率（DMG f）算；景元 f 是 3 段（66% × 3），按这次实际段数 3 + 【神君段数】（rec.oc = 主人当时的计数）换算。
相邻目标的 25%、E1 的相邻加成没算。

用法：python3 tools/fix179.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 179
F = Fix(sys.argv[1], TV, sys.argv[2])
F.rep('    const T = tplOf(o), sp = T && (DMGX.mem[String(T.id)] || {})[u.sm.key]; if (!sp) return null;',
      '    const T = tplOf(o), sp = T && (DMGX.mem[String(T.id)] || {})[u.sm.key];\n'
      '    if (!sp) {   // 行动算追加攻击的召唤物（景元神君、托帕账账）：按主人的追加攻击倍率（tv 179）\n'
      '      if (!(u.sm && u.sm.fua)) return null; let e = dmgEntry(o, "f"); if (!e) return null;\n'
      '      if (String(T.id) === "1204") e = Object.assign({}, e, { v: num(e.v) * (3 + num(a.oc)) / 3 });   // 神君段数 = 3 + 【神君段数】计数\n'
      '      return dmgCalc(o, e, a);\n'
      '    }')
log = """<li><b>2026-11-23（差异清单第 55 批）：tv 179（tools/fix179.py）</b>。景元【神君】、托帕【账账】自己行动的那一行以前没有伤害（也不算进伤害合计）；现在按主人的追加攻击倍率算，神君按这次实际段数（3 + 【神君段数】，每段 66%）。相邻目标的伤害没算。<b>对已有配置</b>：只影响伤害显示；有景元 / 托帕的方案伤害合计会明显变高。</li>"""
record = """2026-11-23（差异清单第 55 批）：tv 179（tools/fix179.py）。memDmgOf：没有 DMGX.mem 的 sm.fua 召唤物按主人 f，景元按 rec.oc 段数。"""
F.finish('差异清单第 55 批（神君 / 账账行动伤害）', log, record)
print('done tv', TV)
