"""tv 182（2026-11-23）：差异清单第 58 批
驭空 1207 天赋 120704“施放普攻……并使本次攻击的削韧值提高100%”：x.tghAdd [["b", 30, 0]]（TGH 普攻 30 → 60）。
“1 回合后可再次触发”的冷却没做（和 XR 天赋附加伤害 tf 一样按每次普攻都触发）。

用法：python3 tools/fix182.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 182
F = Fix(sys.argv[1], TV, sys.argv[2])
S = json.load(open(os.path.join(sys.argv[2], 'character_skills.json'), encoding='utf-8'))
assert '并使本次攻击的削韧值提高#2[i]%' in S['120704']['desc'] and S['120704']['params'][0][1] == 1
assert F.s.count('"1207":{"b":[30,0,0],"u":[90,0,0]}') == 1
c = F.C[1207]; x = c.setdefault('x', {}); assert 'tghAdd' not in x
x['tghAdd'] = [['b', 30, 0]]
F.touch(1207)
log = """<li><b>2026-11-23（差异清单第 58 批）：tv 182（tools/fix182.py）</b>。驭空天赋“施放普攻时本次攻击的削韧值提高 100%”：普攻削韧 30 → 60（10 → 20 点）。“1 回合后可再次触发”的冷却没做，和天赋附加伤害一样按每次普攻都触发。<b>对已有配置</b>：驭空打普攻时破韧更早；平时只放战技的不变。</li>"""
record = """2026-11-23（差异清单第 58 批）：tv 182（tools/fix182.py）。驭空 x.tghAdd b +30（冷却没做）。"""
F.finish('差异清单第 58 批（驭空天赋削韧）', log, record)
print('done tv', TV)
