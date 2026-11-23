"""tv 186（2026-11-23）：差异清单第 62 批
藿藿 E6（1121706）“为我方目标提供治疗时，使目标造成的伤害提高50%，持续2回合”：以前用 aHeal（任何人的治疗都算）。
新条件 hme（效果字段 hMe）：触发事件是治疗时，只算持有者（或持有者的忆灵 / 召唤物）提供的治疗；
aHeal 两处（立即治疗、持续治疗结算）在 teamFire 时记下 healBy = 治疗者。

用法：python3 tools/fix186.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 186
F = Fix(sys.argv[1], TV, sys.argv[2])
R = json.load(open(os.path.join(sys.argv[2], 'character_ranks.json'), encoding='utf-8'))
assert R['1121706']['desc'] == '为我方目标提供治疗时，使目标造成的伤害提高50%，持续2回合。'
c = F.C[1217]; e6 = [x for x in c['eid'] if x['r'] == 6][0]['eff']; assert len(e6) == 1 and e6[0]['t'] == 'aHeal'
e6[0]['hme'] = 1
e6[0]['n'] = 'E6 同休共戚，相须而行：为我方目标提供治疗时，使被治疗的目标造成的伤害 +50%，持续 2 回合（只算藿藿的治疗）'
F.touch(1217)
F.rep('if (x.hfo) e.hFo = 1;', 'if (x.hfo) e.hFo = 1; if (x.hme) e.hMe = 1;')
F.rep('      if (eff.hFo && healBy !== undefined) {',
      '      if (eff.hMe && healBy !== undefined) { const H0 = healBy ? (ownerOf(healBy) || healBy) : null, H1 = src ? (ownerOf(src) || src) : null; if (!H0 || H0 !== H1) return; }   // 只算自己（含自己的忆灵 / 召唤物）提供的治疗（藿藿 E6，tv 186）\n'
      '      if (eff.hFo && healBy !== undefined) {')
F.rep('      for (const [tg, a] of parts) teamFire("aHeal", tg, null, a);   // 我方目标受到治疗后（遐蝶收容的暗潮按治疗数值转化新蕊）',
      '      { const hb0 = healBy; healBy = src; try { for (const [tg, a] of parts) teamFire("aHeal", tg, null, a); } finally { healBy = hb0; } }   // 我方目标受到治疗后（遐蝶收容的暗潮按治疗数值转化新蕊）；记下治疗者（hme，tv 186）')
F.rep('try { healFor(u, "heal"); } finally { healBy = hb0; } } teamFire("aHeal", u, null, a); giveHeal(x.src, [u]); }',
      'try { healFor(u, "heal"); teamFire("aHeal", u, null, a); } finally { healBy = hb0; } } giveHeal(x.src, [u]); }')
log = """<li><b>2026-11-23（差异清单第 62 批）：tv 186（tools/fix186.py）</b>。藿藿 6 魂“为我方目标提供治疗时，目标伤害 +50%”只算藿藿自己的治疗了，以前队伍里任何人的治疗都会触发。效果新条件“只算自己提供的治疗”。<b>对已有配置</b>：6 魂藿藿和别的奶妈同队时，别人的治疗不再给这 +50%。</li>"""
record = """2026-11-23（差异清单第 62 批）：tv 186（tools/fix186.py）。新条件 hme / hMe；aHeal 时记 healBy。"""
F.finish('差异清单第 62 批（藿藿 6 魂只算自己的治疗）', log, record)
print('done tv', TV)
