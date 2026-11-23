"""tv 168（2026-11-23）：差异清单第 44 批
天国@直播间 324（2 件）：“若在同一回合内消耗大于等于3点战技点，额外使装备者暴击伤害提高32%，持续3回合”：
以前施放战技时、默认关；改成装备者消耗战技点后这个回合已消耗 ≥3（spUse aw self + tsp 3）自动生效，默认开。

用法：python3 tools/fix168.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 168
F = Fix(sys.argv[1], TV, sys.argv[2])
RS = json.load(open(os.path.join(sys.argv[2], 'relic_sets.json'), encoding='utf-8'))
assert '若在同一回合内消耗大于等于3点战技点，额外使装备者暴击伤害提高32%，持续3回合' in RS['324']['desc'][0]
R = {r['id']: r for r in F.DB['relics']}
e = R[324]['p2']['eff'][0]; assert e.get('off') == 1
del e['off']; e.update({'t': 'spUse', 'aw': 'self', 'tsp': 3, 'n': '2件：同一回合消耗 ≥3 个战技点时暴击伤害额外提高 32%，持续 3 回合（自动判断）'})
log = """<li><b>2026-11-23（差异清单第 44 批）：tv 168（tools/fix168.py）</b>。遗器天国@直播间 2 件“同一回合内消耗 ≥3 点战技点时暴伤额外 +32%，持续 3 回合”改成自动判断、默认开（以前要手动开）。<b>对已有配置</b>：只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 44 批）：tv 168（tools/fix168.py）。天国@直播间 spUse + tsp 3。"""
F.finish('差异清单第 44 批（天国@直播间）', log, record)
p = sys.argv[1]; s = open(p, encoding='utf-8', newline='').read()
a0 = f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}'
assert s.count(a0) == 1
s = s.replace(a0, f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); for (const u of s.units) if (u.kind === "ally" && !u.sm && [u.rA, u.rB, u.rP].some(r => +r === 324)) applyEquip(u); }} finally {{ S = keep; }} }}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done tv', TV)
