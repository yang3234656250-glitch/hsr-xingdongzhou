"""tv 165（2026-11-23）：差异清单第 41 批（光锥）
1. 于夜色中 23001：“当装备者在战斗中速度大于100时，每超过10点，普攻和战技造成的伤害提高6%，同时终结技的暴击伤害提高12%，该效果可叠加6层”：
   以前按战斗开始时的速度线性算（每 1 点 0.6%）；改成每 10 点一档（stp 10）、出手时按当时速度重算（dy）。
2. 当一颗星照亮夜空 23060：“【启航】达到3层时，每层【启航】使终结技伤害提高20%”：补一条（施放助战技后【启航】≥3 层时终结技伤害 +60%，持续 2 回合，needBk qh）。
3. 游戏尘寰 23021【彩焰】：官方原文就是“装备者每恢复1个战技点”，页面只算装备者自己恢复的是对的（核对无误，清单勾掉）。

用法：python3 tools/fix165.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 165
F = Fix(sys.argv[1], TV, sys.argv[2])
LR = json.load(open(os.path.join(sys.argv[2], 'light_cone_ranks.json'), encoding='utf-8'))
assert '每超过#2[i]点' in LR['23001']['desc'] and LR['23001']['params'][0][1] == 10
assert '【启航】达到#5[i]层时，每层【启航】使终结技伤害提高#6[i]%' in LR['23060']['desc']
L = {l['id']: l for l in F.DB['lcs']}
n = 0
for e in L[23001]['eff']:
    if e.get('ss') == 'spd':
        e['stp'] = 10; e['dy'] = 1; e['n'] = e['n'].replace('（按战斗开始时的速度，线性近似）', '（每 10 点一档，按出手时的速度）'); n += 1
assert n == 3, n
qh = [e for e in L[23060]['eff'] if e.get('bk') == 'qh']; assert len(qh) == 1
ups = [round(x * 100, 4) for x in [p[5] for p in LR['23060']['params']]]
L[23060]['eff'].append({'y': 'dbuf', 't': 'aSup', 'aw': 'all', 'tg': 'self', 'm': 'dmg', 'sc': 'u', 'v': [3 * u for u in ups], 'd': 2, 'bk': 'qh3', 'nbk': ['qh', 'dmg', 3],
                        'n': '光锥【启航】：达到 3 层时每层终结技伤害提高（3 层合计），持续 2 回合'})
L[23060]['notes'] = []

log = """<li><b>2026-11-23（差异清单第 41 批）：tv 165（tools/fix165.py）</b>。光锥：① 于夜色中“速度大于 100 时每超过 10 点，普攻 / 战技伤害 +6%、终结技暴伤 +12%（最多 6 层）”改成每 10 点一档、按出手时的速度算（以前按开局速度线性算）；② 当一颗星照亮夜空补“【启航】3 层时每层终结技伤害 +20%”；③ 游戏尘寰【彩焰】核对原文无误。<b>对已有配置</b>：只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 41 批）：tv 165（tools/fix165.py）。于夜色中 stp 10 + dy；当一颗星照亮夜空启航 3 层终结技增伤（nbk）；游戏尘寰核对无误。"""
F.finish('差异清单第 41 批（于夜色中、当一颗星照亮夜空）', log, record)
# 迁移：装了这两把光锥的卡片重建装备效果
p = sys.argv[1]; s = open(p, encoding='utf-8', newline='').read()
a = f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}'
assert s.count(a) == 1
s = s.replace(a, f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); for (const u of s.units) if (u.kind === "ally" && !u.sm && [23001, 23060].includes(+u.lc)) applyEquip(u); }} finally {{ S = keep; }} }}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done tv', TV)
