"""tv 177（2026-11-23）：差异清单第 53 批
银狼 1006（强化版）E4（1100604）“施放终结技攻击敌方目标后，目标每有1个负面效果，则额外造成等同于银狼20%攻击力的量子属性附加伤害……对每个目标最多触发5次”：
以前按固定 5 个（100%）；XR 新字段 negN = 按主目标当时的负面效果个数（最多 N 个）乘倍率，edbAll 多记每个敌人的负面效果数 ng（negOf）。没放敌人卡时按 N 个（和以前一样）。

用法：python3 tools/fix177.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 177
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('r:1100604', '目标每有#个负面效果，则额外造成等同于银狼#攻击力的量子属性附加伤害。该效果在每次终结技攻击中对每个目标最多触发#次')
r = [x for x in F.XR['1006'] if x['k'] == 'e4']; assert len(r) == 1
r[0].update({'v': [0.2], 'negN': 5, 'n': '【强化版】E4：终结技后目标每有 1 个负面效果额外 20% 攻击力附加伤害，最多 5 次（按主目标当时的负面效果数）'})
F.rep('slow: Object.fromEntries(ens.map(z => [z.id, (z.buffs || []).some(b => !b.kind && num(b.v) < 0)])), st:',
      'slow: Object.fromEntries(ens.map(z => [z.id, (z.buffs || []).some(b => !b.kind && num(b.v) < 0)])), ng: Object.fromEntries(ens.map(z => [z.id, negOf(z)])), st:')
F.rep('        if (r.e4add && num(o.eid) >= 4) v += r.e4add;',
      '        if (r.negN) { const A6 = rec && rec.eAll, mid6 = A6 && A6.ord ? A6.ord[0] : null; v *= A6 && A6.ng && mid6 != null ? Math.min(num(r.negN), num(A6.ng[mid6])) : num(r.negN); if (!(v > 0)) continue; }   // 按主目标的负面效果个数（银狼 E4，tv 177）\n'
      '        if (r.e4add && num(o.eid) >= 4) v += r.e4add;')
log = """<li><b>2026-11-23（差异清单第 53 批）：tv 177（tools/fix177.py）</b>。银狼 E4 终结技附加伤害按主目标<b>当时的负面效果个数</b>（每个 20%，最多 5 个）算，以前固定按 5 个。没放敌人卡时仍按 5 个。<b>对已有配置</b>：只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 53 批）：tv 177（tools/fix177.py）。银狼 E4 XR negN（edbAll ng）。"""
F.finish('差异清单第 53 批（银狼 E4 按负面效果数）', log, record)
print('done tv', TV)
