"""tv 167（2026-11-23）：差异清单第 43 批（光锥 / 遗器）
1. “同类效果无法叠加”：伤害增益新字段 gk（DB 同名）= 增益键不带施放者（"g:bk"），两个人装同一件只算一份、后来的覆盖前面的。
   用在 追逐风的时候 21056（我方全体击破伤害）、机心戏梦的钟表匠 118 4 件（我方全体击破特攻）、星火悄然闪耀 23061【闪耀王冠】、花花世界迷人眼 23053【推流】。
2. 星火悄然闪耀 23061：“我方任意角色在自身同一回合内累计消耗大于等于4点战技点时，装备者获得【闪耀王冠】，持续3回合”：
   以前开局常驻、默认关；改成我方消耗战技点时（spUse aw all）这个回合已消耗 ≥4（tsp 4）才生效，持续 3 回合，默认开。
3. 花花世界迷人眼 23053：“装备者每消耗1个战技点……无视防御 5%，最多 4 层；若在同一回合内消耗大于等于4个战技点则使装备者获得【推流】”：
   无视防御改成每消耗 1 个战技点叠 1 层（spUse aw self，以前按施放战技）；【推流】改成装备者消耗战技点后这个回合已消耗 ≥4 才生效，默认开。

用法：python3 tools/fix167.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 167
F = Fix(sys.argv[1], TV, sys.argv[2])
LR = json.load(open(os.path.join(sys.argv[2], 'light_cone_ranks.json'), encoding='utf-8'))
assert '同类技能无法重复生效' in LR['21056']['desc'] and '同类效果无法叠加' in LR['23061']['desc'] and '同类光锥效果无法叠加' in LR['23053']['desc']
assert '在自身同一回合内累计消耗大于等于#3[i]点战技点时' in LR['23061']['desc'] and LR['23061']['params'][0][2] == 4 and LR['23061']['params'][0][3] == 3
L = {l['id']: l for l in F.DB['lcs']}
R = {r['id']: r for r in F.DB['relics']}
e = L[21056]['eff'][0]; e['gk'] = 1
e = R[118]['p4']['eff'][0]; assert e['bk'] == 'wm'; e['gk'] = 1
a, b = L[23061]['eff']
for x in (a, b):
    assert x.get('off') == 1; del x['off']; x.update({'t': 'spUse', 'aw': 'all', 'tsp': 4, 'gk': 1})
a['n'] = '光锥【闪耀王冠】：我方同一回合累计消耗 ≥4 个战技点时我方全体无视防御，持续 3 回合（同类效果不叠加）'
b['n'] = '光锥【闪耀王冠】：持有时装备者战技伤害提高，持续 3 回合'
sp, di, tl = L[23053]['eff']
assert di['bk'] == 'lc' and tl.get('off') == 1
di.update({'t': 'spUse', 'aw': 'self', 'n': '光锥：装备者每消耗 1 个战技点欢愉伤害无视防御，最多 4 层'})
del tl['off']; tl.update({'t': 'spUse', 'aw': 'self', 'tsp': 4, 'gk': 1, 'n': '光锥【推流】：装备者同一回合消耗 ≥4 个战技点后我方全体欢愉度提高（同类光锥效果不叠加）'})
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.gk) e.gk = 1;')
F.rep('      const bk = eff.bk ? String(eff.bk) : "", key = (src ? src.id : "ev") + ":" + (bk ? bk + (bk.startsWith("st:") ? "#d" + eff.mode : ":d" + eff.mode) : "d:" + eff.id);',
      '      const bk = eff.bk ? String(eff.bk) : "", key = (eff.gk ? "g" : src ? src.id : "ev") + ":" + (bk ? bk + (bk.startsWith("st:") ? "#d" + eff.mode : ":d" + eff.mode) : "d:" + eff.id);   // gk：同类效果无法叠加（键不带施放者，tv 167）')

log = """<li><b>2026-11-23（差异清单第 43 批）：tv 167（tools/fix167.py）</b>。光锥 / 遗器：① “同类效果无法叠加”的几件（追逐风的时候、机心戏梦的钟表匠 4 件、星火悄然闪耀、花花世界迷人眼【推流】）两人同时装备只算一份。② 星火悄然闪耀【闪耀王冠】改成我方同一回合累计消耗 ≥4 个战技点时自动获得 3 回合（以前要手动开、一直有）。③ 花花世界迷人眼：无视防御按每消耗 1 个战技点叠层；【推流】改成装备者同一回合消耗 ≥4 个战技点时自动获得。<b>对已有配置</b>：只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 43 批）：tv 167（tools/fix167.py）。dbuf 新字段 gk（全局键）；星火悄然闪耀 spUse + tsp 4；花花世界迷人眼 spUse + tsp 4。"""
F.finish('差异清单第 43 批（同类效果不叠加、星火悄然闪耀、花花世界迷人眼）', log, record)
p = sys.argv[1]; s = open(p, encoding='utf-8', newline='').read()
a0 = f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}'
assert s.count(a0) == 1
s = s.replace(a0, f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); for (const u of s.units) if (u.kind === "ally" && !u.sm && ([21056, 23061, 23053].includes(+u.lc) || [u.rA, u.rB, u.rP].some(r => +r === 118))) applyEquip(u); }} finally {{ S = keep; }} }}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done tv', TV)
