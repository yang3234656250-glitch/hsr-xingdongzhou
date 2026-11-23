"""tv 171（2026-11-23）：差异清单第 47 批
1. 新效果类型 bg（获得 N 点【好活当赏】）：模拟里记到结果的 bgFx（{uid, t, seq, v}），伤害层 bangGrants 当成一条好活当赏（和技能给的一样按该角色 2 个回合）。
   砂金•戏浪 1513 秘技（151307?）“进入战斗后获得 20 点【好活当赏】”、真珠 1503 秘技“进入战斗后获得 20 点【好活当赏】”用它（都按秘技：用了再启用，默认关）。
2. 丹恒•饮月 1213 E1（121301）“使【亢心】的可叠加层数增加4层”：补 4 层（+40%，5 魂 +44%），和天赋那条一样默认关（满层时启用）。

用法：python3 tools/fix171.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 171
F = Fix(sys.argv[1], TV, sys.argv[2])
S = json.load(open(os.path.join(sys.argv[2], 'character_skills.json'), encoding='utf-8'))
assert '点【好活当赏】' in S['151307']['desc'] and S['151307']['params'][0][2] == 20
assert '真珠获得#2[i]点【好活当赏】' in S['150307']['desc'] and S['150307']['params'][0][1] == 20
F.has('r:121301', '使【亢心】的可叠加层数增加#层')

c = F.C[1513]
e = F.eff(1513, '秘技于静水掀起风浪：进入战斗后获得 2 点【热意】和 20 点好活当赏'); oldn = e['n']
e['n'] = '秘技于静水掀起风浪：进入战斗后获得 2 点【热意】（用了秘技再启用）'
i = c['eff'].index(e)
NB = '秘技于静水掀起风浪：进入战斗后获得 20 点【好活当赏】（用了秘技再启用）'
c['eff'].insert(i + 1, {'y': 'bg', 't': 'start', 'tg': 'self', 'v': 20, 'off': 1, 'n': NB})
fx = F.FIX.setdefault('1513', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
fx['drop'].append(oldn); fx['trig'][oldn] = 'start'; fx['map'][oldn] = e['n']; fx['add'] += [e['n'], NB]; fx['keep'] = 1

c = F.C[1503]
e = F.eff(1503, '秘技：进入战斗后获得 20 点【好活当赏】并【深度学习】'); oldn = e['n']
e['n'] = '秘技：进入战斗后获得【深度学习】（按 2 次强化普攻算）；20 点【好活当赏】见下一条'
i = c['eff'].index(e)
NP = '秘技：进入战斗后获得 20 点【好活当赏】（用了秘技再启用）'
c['eff'].insert(i + 1, {'y': 'bg', 't': 'start', 'tg': 'self', 'v': 20, 'off': 1, 'n': NP})
fx = F.FIX.setdefault('1503', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
fx['drop'].append(oldn); fx['trig'][oldn] = 'start'; fx['map'][oldn] = e['n']; fx['add'] += [e['n'], NP]; fx['keep'] = 1

kx = F.eff(1213, '天赋：每段攻击后亢心伤害 +10%')
e1 = F.eid(1213, 1)
assert not any(x.get('bk') == 'kx1' for x in e1['eff'])
e1['eff'].append({'y': 'dbuf', 't': 'start', 'tg': 'self', 'm': 'dmg', 'v': 40, 'lv': [5, 44], 'd': 0, 'bk': 'kx1', 'off': 1, 'n': 'E1：【亢心】可叠加层数 +4（满 10 层时再 +40%，5 魂 +44%；和天赋那条一起满层时启用）'})

F.rep('    const bgUse = [];   // 真珠消耗掉的【好活当赏】', '    const bgUse = [];   // 真珠消耗掉的【好活当赏】\n    const bgFx = [];   // 效果直接给的【好活当赏】（type bg，tv 171）')
F.rep('dots: dotRecs, bgUse };', 'dots: dotRecs, bgUse, bgFx };')
F.rep('        if (eff.type === "force") {', '        if (eff.type === "bg") { if (tg.kind === "ally" && v > 0) { bgFx.push({ uid: tg.id, t, seq, v }); addLog(`${tg.name}获得 ${v} 点【好活当赏】（${eff.note || "效果"}）`, false, null, tg.id); } continue; }   // 获得好活当赏（只给伤害层）\n        if (eff.type === "force") {')
F.rep('    if (BG) for (const a of R.actions) {', '    for (const x of R.bgFx || []) if (x.uid === u.id) g.push({ amt: num(x.v), from: x.t, seq: num(x.seq, 0) + 0.5, ...ex(x.t, num(x.seq, 0) + 0.5) });   // 效果直接给的（秘技等，tv 171）\n    if (BG) for (const a of R.actions) {')

log = """<li><b>2026-11-23（差异清单第 47 批）：tv 171（tools/fix171.py）</b>。① 新效果“获得好活当赏”：砂金•戏浪、真珠的秘技“进入战斗后获得 20 点【好活当赏】”现在会算进伤害（秘技效果，用了秘技再启用）。② 丹恒•饮月 E1【亢心】可叠加层数 +4（满层再 +40%，和天赋那条一起手动启用）。<b>对已有配置</b>：只影响伤害显示；行动顺序表多一行“获得好活当赏”的日志（打开秘技时）。</li>"""
record = """2026-11-23（差异清单第 47 批）：tv 171（tools/fix171.py）。效果类型 bg（bgFx → bangGrants）；砂金•戏浪 / 真珠秘技好活当赏；丹恒•饮月 E1 亢心 +4 层。"""
F.finish('差异清单第 47 批（秘技好活当赏、丹恒•饮月 E1）', log, record)
print('done tv', TV)
