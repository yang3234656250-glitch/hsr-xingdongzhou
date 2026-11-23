"""tv 183（2026-11-23）：差异清单第 59 批
弱点击破的裂伤：官方“每回合开始受到等同于敌方生命上限 16%（精英 / 首领 7%）的物理持续伤害，最多不超过 2 × 等级系数 × 韧性系数”。
以前一律按上限算；现在击破的裂伤记下 hpV（普通 16、精英 / 首领 7，按敌人模板 r 是 B / L / E），
dotDmgOf 对击破伤害也取“敌人生命上限 × X% × (1 + 击破特攻)”和上限的较小值（和卢卡裂伤同一套 hpB / hpV）。

用法：python3 tools/fix183.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 183
F = Fix(sys.argv[1], TV, sys.argv[2])
F.rep('if (el === "物") { dot("裂伤", 200 * tm, 2); extra = "，陷入裂伤 2 回合"; }',
      'if (el === "物") { dot("裂伤", 200 * tm, 2); en.dots[en.dots.length - 1].hpV = big ? 7 : 16; extra = "，陷入裂伤 2 回合"; }   // 敌人生命上限 16%（精英 / 首领 7%），最多不超过上限（tv 183）')
F.rep('    if (brk && d) { d.noPanel = false; d.stat = "击破基础值（80 级）"; }\n',
      '    if (brk && d) { d.noPanel = false; d.stat = "击破基础值（80 级）"; }\n'
      '    if (brk && d && num(r.hpB) > 0 && num(r.hpV) > 0) {   // 击破的裂伤：敌人生命上限 16% / 7%，最多不超过 2 × 等级系数 × 韧性系数，取较小的（tv 183）\n'
      '      const d2 = dmgCalc(u, Object.assign({}, e, { v: num(r.hpV) }), { t: r.t, uid: u.id, db: r.db, edb: r.edb, hpm: r.hpm, ebk: r.ebk }, num(r.hpB) * (1 + (num(u.be) + dsum(r.db, "be", "k")) / 100));\n'
      '      if (d2 && d2.total < d.total) { d2.noPanel = false; d2.stat = "敌人生命上限（未达到击破裂伤上限）"; d = d2; }\n'
      '    }\n')
log = """<li><b>2026-11-23（差异清单第 59 批）：tv 183（tools/fix183.py）</b>。弱点击破造成的裂伤按官方取“敌人生命上限 16%（精英 / 首领 7%）”和上限（2 × 等级系数 × 韧性系数）的较小值，以前一律按上限算。<b>对已有配置</b>：只影响伤害显示；敌人生命值低时（比如普通小怪）裂伤伤害会变小。</li>"""
record = """2026-11-23（差异清单第 59 批）：tv 183（tools/fix183.py）。击破裂伤 hpV 16 / 7，dotDmgOf brk 也取较小值。"""
F.finish('差异清单第 59 批（击破裂伤按敌人生命上限）', log, record)
print('done tv', TV)
