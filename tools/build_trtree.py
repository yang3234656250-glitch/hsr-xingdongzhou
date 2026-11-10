"""生成 const TRTREE（行迹面板节点图用）：每个角色 10 个属性强化节点各自接在谁后面。
用法：python3 tools/build_trtree.py <官方 json 目录> index.html
来源：StarRailRes character_skill_trees 的 anchor（Point09～18 = 属性强化，Point06～08 = 额外能力）和 pre_points。
编码：10 个字符，依次对应 TRACE[id].s 里有数值的 10 项；"-" = 直接接在核心技能上，A / B / C = 接在第 1 / 2 / 3 个额外能力后，0～9 = 接在第几个属性强化后。
"""
import sys, json, re
off, path = sys.argv[1], sys.argv[2]
C = json.load(open(off + '/characters.json', encoding='utf-8')); ST = json.load(open(off + '/character_skill_trees.json', encoding='utf-8'))
s = open(path, encoding='utf-8').read()
TR = json.loads(re.search(r'const TRACE ?= ?(\{.*?\});\n', s).group(1))
out = {}; bad = []
for cid, d in TR.items():
    c = C.get(cid)
    if not c: bad.append((cid, 'no official')); continue
    nodes = {k: ST[k] for k in c['skill_trees'] if k in ST}
    num = lambda k: int(nodes[k]['anchor'].replace('Point', ''))
    stats = sorted([k for k in nodes if 9 <= num(k) <= 18], key=num); abil = sorted([k for k in nodes if 6 <= num(k) <= 8], key=num)
    names = [n for n, v in d['s'] if v]
    if [nodes[k]['name'] for k in stats] != names or [nodes[k]['name'] for k in abil] != [m[0] for m in d['m']]: bad.append((cid, 'name mismatch', [nodes[k]['name'] for k in stats][:3], names[:3])); continue
    code = ''
    for k in stats:
        pp = nodes[k].get('pre_points') or []
        p = pp[0] if pp else None
        code += '-' if p is None else 'ABC'[abil.index(p)] if p in abil else str(stats.index(p)) if p in stats else '-'
    out[cid] = code
line = 'const TRTREE = ' + json.dumps(out, separators=(',', ':')) + ';'
if re.search(r'\n  const TRTREE = \{.*?\};\n', s): s = re.sub(r'\n  const TRTREE = \{.*?\};\n', lambda m: '\n  ' + line + '\n', s, count=1)
else:
    i = s.index('\n  const TRACE = '); j = s.index('\n', i + 1); s = s[:j + 1] + '  ' + line + '\n' + s[j + 1:]
open(path, 'w', encoding='utf-8').write(s)
from collections import Counter
print(len(out), 'chars; skipped', bad); print(Counter(out.values()).most_common(12))
by = {}
for cid, code in out.items(): by.setdefault(C[cid]['path'], Counter())[code] += 1
print({k: dict(v) for k, v in by.items()})
