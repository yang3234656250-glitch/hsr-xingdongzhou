"""tv 166（2026-11-23）：差异清单第 42 批（光锥）
1. 纵然山河万程 23051：“【卫戍】……若目标拥有召唤物则造成的伤害额外提高12%”：补一条（我方角色里有召唤物的，ths）。
2. 将光阴织成黄金 23036：“装备者和装备者的忆灵在攻击后使装备者获得1层【织锦】……叠加至上限时，每层【织锦】额外使造成的普攻伤害提高9%”：
   忆灵攻击后也叠层（aw sm，和装备者共用一组）；叠满 6 层时的普攻增伤改成自动（攻击后【织锦】≥6 层时生效，nbk），默认开。

用法：python3 tools/fix166.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 166
F = Fix(sys.argv[1], TV, sys.argv[2])
LR = json.load(open(os.path.join(sys.argv[2], 'light_cone_ranks.json'), encoding='utf-8'))
assert '若目标拥有召唤物则造成的伤害额外提高#3[i]%' in LR['23051']['desc']
assert '装备者和装备者的忆灵在攻击后使装备者获得1层【织锦】' in LR['23036']['desc']
L = {l['id']: l for l in F.DB['lcs']}
P = LR['23051']['params']
e = [x for x in L[23051]['eff'] if x.get('bk') == 'lc']; assert len(e) == 1
e[0]['n'] = '光锥【卫戍】：施放终结技时我方全体伤害提高，持续 3 回合'
L[23051]['eff'].append({'y': 'dbuf', 't': 'ult', 'tg': 'allies', 'ths': 1, 'm': 'dmg', 'v': [round(p[2] * 100, 4) for p in P], 'd': 3, 'bk': 'lc4',
                        'n': '光锥【卫戍】：拥有召唤物的目标伤害额外提高，持续 3 回合'})
E = L[23036]['eff']
a, b, c = E
assert a['bk'] == 'lc' and b['bk'] == 'lc2' and c['bk'] == 'lc3' and c.get('off') == 1
a['n'] = '光锥【织锦】：装备者攻击后暴击伤害提高，最多 6 层'
b['n'] = '光锥【织锦】：装备者攻击后，装备者的忆灵同样提高'
a2 = dict(a, aw='sm', n='光锥【织锦】：装备者的忆灵攻击后也获得 1 层（和装备者共用）')
b2 = dict(b, aw='sm', n='光锥【织锦】：装备者的忆灵攻击后，忆灵同样提高')
c2 = {'y': 'dbuf', 't': 'atk', 'aw': 'self', 'tg': 'self', 'm': 'dmg', 'v': c['v'], 'sc': 'b', 'd': 0, 'bk': 'lc3', 'nbk': ['lc', 'cd', 6],
      'n': '光锥：【织锦】叠满 6 层时普攻伤害提高（攻击后满 6 层时自动生效）'}
L[23036]['eff'] = [a, b, a2, b2, c2, dict(c2, aw='sm')]
L[23036]['notes'] = [n for n in L[23036].get('notes', []) if '忆灵攻击叠层' not in n]

log = """<li><b>2026-11-23（差异清单第 42 批）：tv 166（tools/fix166.py）</b>。光锥：① 纵然山河万程【卫戍】补“拥有召唤物的目标伤害额外 +12%”；② 将光阴织成黄金：忆灵攻击后也叠【织锦】，叠满 6 层的普攻增伤自动生效（以前要手动开）。<b>对已有配置</b>：只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 42 批）：tv 166（tools/fix166.py）。纵然山河万程 ths 额外部分；将光阴织成黄金 aw sm 叠层 + nbk 叠满普攻增伤。"""
F.finish('差异清单第 42 批（纵然山河万程、将光阴织成黄金）', log, record)
p = sys.argv[1]; s = open(p, encoding='utf-8', newline='').read()
a0 = f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}'
assert s.count(a0) == 1
s = s.replace(a0, f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); for (const u of s.units) if (u.kind === "ally" && !u.sm && [23051, 23036].includes(+u.lc)) applyEquip(u); }} finally {{ S = keep; }} }}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done tv', TV)
