"""伤害倍率表补漏（2026-11-10 自检：DMG 每个数组和官方技能参数逐列比对后发现的 5 处）。用法：python3 tools/fix_dmg2.py index.html <官方 json 目录>
黑天鹅【强化版】普攻用成了旧版倍率、战技没有倍率；乱破强化普攻没有倍率；赛飞儿战技没有倍率；丹恒•腾荒终结技倍率不是官方值。只改伤害显示，不影响模拟。"""
import sys, json, re
p, off = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8').read()
SK = json.load(open(off + '/character_skills.json', encoding='utf-8'))
m = re.search(r'\n(\s*)const DMG ?= ?(\{.*?\});\n', s); D = json.loads(m.group(2))
r4 = lambda x: round(x + 1e-12, 4)
col = lambda sid, c: [r4(row[c]) for row in SK[sid]['params']]
E = lambda sid, v, adj, tg: dict(v=v, adj=adj, rnd=[], tg=tg, el=0, stat='atk', n=SK[sid]['name'], max=SK[sid]['max_level'])
# 黑天鹅【强化版】
assert D['1307']['b']['v'][5] == 0.6 and col('1130701', 0)[5] == 1.0
D['1307']['b']['v'] = col('1130701', 0)
assert 's' not in D['1307'] and col('1130702', 0)[9] == 0.9
D['1307']['s'] = E('1130702', col('1130702', 0), col('1130702', 0), 2)
# 乱破强化普攻：前 2 段主目标 #1、相邻 #2，第 3 段全体 #3 → 主目标 2×#1 + #3，相邻 2×#2 + #3（更远的敌人只吃第 3 段，没单独算）
P = SK['131718']['params']; assert 'b2' not in D['1317'] and P[5][:3] == [1, 0.5, 1]
D['1317']['b2'] = E('131718', [r4(2 * r[0] + r[2]) for r in P], [r4(2 * r[1] + r[2]) for r in P], 2)
# 赛飞儿战技
assert 's' not in D['1406'] and col('140602', 0)[9] == 2 and col('140602', 1)[9] == 1
D['1406']['s'] = E('140602', col('140602', 0), col('140602', 1), 2)
# 丹恒•腾荒终结技
assert D['1414']['u']['v'][9] == 4.8 and col('141403', 0)[9] == 3
D['1414']['u']['v'] = col('141403', 0)
s = s[:m.start(2)] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[m.end(2):]
i = s.index('id="changelog"'); j = s.index('<li>', i)
s = s[:j] + '''<li><b>2026-11-10（伤害倍率自检）</b>：把伤害倍率表里每个角色每个技能每一级的数值和官方技能参数逐列比对了一遍（320 组对上），发现并改掉 5 处：① 黑天鹅【强化版】普攻用成了旧版倍率（60% → 100%）；② 黑天鹅战技没有倍率（补 90% 扩散）；③ 乱破强化普攻【忍具•降魔花弁】没有倍率（补：主目标 2×100% + 100%，相邻 2×50% + 100%）；④ 赛飞儿战技没有倍率（补 200% + 相邻 100%）；⑤ 丹恒•腾荒终结技倍率写成了 480%，官方是 300%。只影响伤害显示，行动轴不变（tools/fix_dmg2.py）。</li>
            ''' + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
