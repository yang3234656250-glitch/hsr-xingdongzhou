"""tv 181（2026-11-23）：差异清单第 57 批（光锥）
血火啊，燃烧前路 23039：“若该效果消耗的生命值高于500点，可使伤害额外提高30%”只加在这次战技 / 终结技上；
以前那条额外增伤对所有伤害生效（近似）。拆成战技（sc s）和终结技（sc u）两条，仍默认关（消耗的生命值高于 500 时启用：6% 生命上限 > 500 ≈ 生命上限 8334 以上，叠影越高门槛越低）。

用法：python3 tools/fix181.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 181
F = Fix(sys.argv[1], TV, sys.argv[2])
LR = json.load(open(os.path.join(sys.argv[2], 'light_cone_ranks.json'), encoding='utf-8'))
assert '若该效果消耗的生命值高于#4[i]点，可使伤害额外提高#5[i]%' in LR['23039']['desc']
P = LR['23039']['params']
L = {l['id']: l for l in F.DB['lcs']}
E = L[23039]['eff']
c = [x for x in E if x.get('bk') == 'lc3']; assert len(c) == 1 and c[0].get('off') == 1; c = c[0]
v = [round(p[4] * 100, 4) for p in P]; assert c['v'] == v, (c['v'], v)
i = E.index(c)
E[i:i + 1] = [dict(c, sc='s', n='光锥：消耗的生命值高于 500 点时，这次战技伤害额外提高（满足时启用）'),
              dict(c, sc='u', bk='lc4', n='光锥：消耗的生命值高于 500 点时，这次终结技伤害额外提高（满足时启用）')]
log = """<li><b>2026-11-23（差异清单第 57 批）：tv 181（tools/fix181.py）</b>。血火啊，燃烧前路：“消耗的生命值高于 500 点时伤害额外提高”拆成战技、终结技各一条，只加在战技 / 终结技伤害上（以前这条对所有伤害生效）。仍默认关（满足时启用）。<b>对已有配置</b>：装备了这把光锥的卡片自动更新（开关保留旧那条的状态）；只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 57 批）：tv 181（tools/fix181.py）。血火啊，燃烧前路 lc3 拆成 sc s / sc u（lc4）。"""
F.finish('差异清单第 57 批（血火啊，燃烧前路）', log, record)
p = sys.argv[1]; s = open(p, encoding='utf-8', newline='').read()
a0 = f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}'
assert s.count(a0) == 1
s = s.replace(a0, f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); for (const u of s.units) if (u.kind === "ally" && !u.sm && +u.lc === 23039) {{ const was = (u.effects || []).find(e => e.eq === "lc" && /对所有伤害生效/.test(e.note || "")); applyEquip(u); if (was && !was.off) for (const e of u.effects) if (e.eq === "lc" && /消耗的生命值高于 500 点时/.test(e.note || "")) delete e.off; }} }} finally {{ S = keep; }} }}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done tv', TV)
