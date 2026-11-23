"""tv 176（2026-11-23）：差异清单第 52 批
艾丝妲 1009 天赋（100904）“每击中1名不同的敌方目标获得1层蓄能，若受到攻击的敌方目标弱点为火属性，则额外获得1层蓄能”：
以前火弱点额外 1 层只看主目标（ewl）；新字段 phw（DB 同名，字段 phW）= 配 ph：只数击中的敌人里有这个属性弱点的（每个 1 层）。

用法：python3 tools/fix176.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 176
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('100904', '若受到攻击的敌方目标弱点为火属性，则额外获得#层蓄能')
e = F.eff(1009, '天赋：被攻击的敌人（主目标）有火属性弱点时额外获得 1 层蓄能'); oldn = e['n']
assert e.get('ewl') == '火'
del e['ewl']; e['ph'] = 1; e['phw'] = '火'; e['n'] = '天赋：每个受到攻击的敌人有火属性弱点时额外获得 1 层蓄能'
fx = F.FIX.setdefault('1009', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
fx['drop'].append(oldn); fx['trig'][oldn] = 'atk'; fx['map'][oldn] = e['n']; fx['add'].append(e['n']); fx['keep'] = 1
F.rep('      if (x.ph) e.perHit = true;', '      if (x.ph) e.perHit = true; if (x.phw) e.phW = x.phw;')
F.rep('        let n = hitN(evTarget && evTarget.kind === "ally" ? evTarget : src);\n',
      '        let n = hitN(evTarget && evTarget.kind === "ally" ? evTarget : src);\n'
      '        if (eff.phW) { n = hitEns().filter(z => { const m = monOf(z); return (m && m.w && m.w.includes(eff.phW)) || hasWk(z, eff.phW); }).length; if (!(n > 0)) return; }   // 只数有这个属性弱点的（艾丝妲天赋，tv 176）\n')
log = """<li><b>2026-11-23（差异清单第 52 批）：tv 176（tools/fix176.py）</b>。艾丝妲天赋：火弱点的额外 1 层蓄能按<b>每个</b>受到攻击、有火弱点的敌人算（以前只看主目标，最多 1 层）。<b>对已有配置</b>：多个火弱点敌人时蓄能叠得更快（只影响伤害）。</li>"""
record = """2026-11-23（差异清单第 52 批）：tv 176（tools/fix176.py）。艾丝妲天赋 ph + phw 火。"""
F.finish('差异清单第 52 批（艾丝妲天赋火弱点逐个算）', log, record)
print('done tv', TV)
