"""tv 175（2026-11-23）：差异清单第 51 批
加拉赫 1301 天赋（130104）“陷入【酩酊】状态的目标每次受到我方角色攻击后，会回复攻击者”、行迹敬请干杯（【酒花奔涌】攻击陷入【酩酊】的目标时）：
以前条件是任意敌人有【酩酊】（ns + so enemy）；新条件 hst（DB 同名，字段 hitSt）= 这次攻击击中的敌人里有带这个状态的。

用法：python3 tools/fix175.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 175
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('130104', '陷入【酩酊】状态的目标每次受到我方角色攻击后')
fx = F.FIX.setdefault('1301', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
for frag, t in [('天赋：陷入【酩酊】的敌人受到我方攻击后', 'atk'), ('行迹敬请干杯：【酒花奔涌】攻击陷入【酩酊】的目标时', 'ebasic')]:
    e = F.eff(1301, frag); oldn = e['n']
    assert e.get('ns') == '酩酊' and e.get('so') == 'enemy'
    del e['ns']; del e['so']; e['hst'] = '酩酊'; e['n'] = oldn + '（按这次攻击击中的敌人有没有【酩酊】）'
    fx['drop'].append(oldn); fx['trig'][oldn] = t; fx['map'][oldn] = e['n']; fx['add'].append(e['n'])
fx['keep'] = 1
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.hst) e.hitSt = x.hst;')
F.rep('      if (eff.evSt) {', '      if (eff.hitSt && !hitEns().some(z => hasSt(z, eff.hitSt))) return;   // 这次攻击击中的敌人有这个状态（加拉赫【酩酊】，tv 175）\n      if (eff.evSt) {')
log = """<li><b>2026-11-23（差异清单第 51 批）：tv 175（tools/fix175.py）</b>。加拉赫天赋 / 行迹敬请干杯的回复：按这次攻击<b>击中的敌人</b>有没有【酩酊】判断（以前任意敌人有【酩酊】就算）。<b>对已有配置</b>：多敌人、只有部分敌人有【酩酊】时回复次数会变；终结技给全体挂【酩酊】的情况不变。</li>"""
record = """2026-11-23（差异清单第 51 批）：tv 175（tools/fix175.py）。加拉赫 hst 酩酊（hitSt）。"""
F.finish('差异清单第 51 批（加拉赫【酩酊】按击中的敌人）', log, record)
print('done tv', TV)
