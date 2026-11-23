"""tv 159（2026-11-23）：差异清单第 35 批
白厄 1408 行迹身承炎炬万千（1408102）“受到队友提供的治疗效果或护盾时，造成的伤害提高45%，持续4回合。该效果单个回合内不可重复触发”：
以前“受到治疗 / 护盾时”不分来源（卡厄斯兰那给自己的回复也算），也没有“单个回合不可重复”。
引擎：doHeal / 持续治疗 / doShield 触发“受到治疗 / 护盾时”时记下施放者（healBy）；新条件 hfo（DB 同名）= 施放者（召唤物按主人）不是效果持有者自己才生效。
白厄这条加 hfo + ptn 1（任意单位的一个回合里最多一次）。

用法：python3 tools/fix159.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 159
F = Fix(sys.argv[1], TV, sys.argv[2])
F.hast(1408, '身承炎炬万千', '受到队友提供的治疗效果或护盾时，造成的伤害提高#，持续#回合。该效果单个回合内不可重复触发')
e = F.eff(1408, '行迹身承炎炬万千：受到队友的治疗或护盾时'); oldn = e['n']
e['hfo'] = 1; e['ptn'] = 1; e['n'] = '行迹身承炎炬万千：受到队友提供的治疗或护盾时造成的伤害 +45%，持续 4 回合（自己 / 卡厄斯兰那给的不算；单个回合内不重复触发）'
fx = F.FIX.setdefault('1408', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
fx['drop'].append(oldn); fx['trig'][oldn] = 'heal'; fx['map'][oldn] = e['n']; fx['add'].append(e['n']); fx['keep'] = 1

F.rep('      for (const [tg] of parts) healFor(tg, "heal");\n',
      '      { const hb0 = healBy; healBy = src; try { for (const [tg] of parts) healFor(tg, "heal"); } finally { healBy = hb0; } }   // 记下治疗者（hfo：队友提供的才算，tv 159）\n')
F.rep('        if (!x.eff.hotX) { healFor(u, "heal");', '        if (!x.eff.hotX) { { const hb0 = healBy; healBy = x.src; try { healFor(u, "heal"); } finally { healBy = hb0; } }')
F.rep('      for (const tg of all) healFor(tg, "shield");', '      { const hb0 = healBy; healBy = src; try { for (const tg of all) healFor(tg, "shield"); } finally { healBy = hb0; } }')
F.rep('    const healFor = (tg, kind) => {', '    let healBy = null;   // 正在结算的治疗 / 护盾的施放者（hfo 条件用）\n    const healFor = (tg, kind) => {')
F.rep('      if (eff.evSt) {', '      if (eff.hFo && healBy !== undefined) { const H0 = healBy ? (ownerOf(healBy) || healBy) : null, H1 = src ? (ownerOf(src) || src) : null; if (!H0 || H0 === H1) return; }   // 只算队友提供的治疗 / 护盾（白厄身承炎炬万千）\n      if (eff.evSt) {')
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.hfo) e.hFo = 1;')

log = """<li><b>2026-11-23（差异清单第 35 批）：tv 159（tools/fix159.py）</b>。白厄行迹身承炎炬万千“受到<b>队友</b>提供的治疗或护盾时伤害 +45%，单个回合内不可重复触发”：以前自己 / 卡厄斯兰那给的回复也算，现在只算队友，并且一个回合最多一次（新条件“只算队友提供的”）。<b>对已有配置</b>：只影响白厄的伤害显示。</li>"""
record = """2026-11-23（差异清单第 35 批）：tv 159（tools/fix159.py）。白厄身承炎炬万千 hfo + ptn 1；引擎 healBy / hFo。"""
F.finish('差异清单第 35 批（白厄身承炎炬万千按队友来源）', log, record)
print('done tv', TV)
