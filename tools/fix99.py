"""tv 99：刻律德菈【军功】换目标时充能重置为 0。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 99, sys.argv[2])
C, has = F.C, F.has
has('141204', '【军功】仅对最新被施加的目标生效，目标改变时使刻律德菈充能重置为0点')
c = C[1412]; E = c['eff']; i = next(k for k, e in enumerate(E) if e.get('t') == 'skill')
E.insert(i, dict(y='count', t='skill', tg='self', m='set', v=0, ns='!军功', so='sk', n='天赋：【军功】的目标改变时充能重置为 0（这次战技的目标还没有【军功】）'))
c['notes'] = [x.replace('【军功】目标改变时充能重置为 0、终结技', '终结技') for x in c.get('notes', [])]
F.rebuild(1412, E)
F.finish('刻律德菈军功换目标重置充能', '''<li><b>2026-11-13</b>：tv 99（tools/fix99.py）。刻律德菈：战技换了【军功】目标时充能重置为 0（一直对同一个人放战技时没有变化）。</li>''',
'''2026-11-13：刻律德菈军功换目标 —— tv 99（tools/fix99.py）。
  未改 / 存疑：终结技“场上没有军功时给第一位角色”、附加伤害 20 次上限没做''')
