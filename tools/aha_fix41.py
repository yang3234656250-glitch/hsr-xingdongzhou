"""tv 41：星神★阿哈（1511）按 nanoka.cc 4.6.54 官方数据（static.nanoka.cc/hsr/4.6.54/zh/character/1511.json）补齐。
官方 dump（StarRailRes / TurnBasedGameData）里没有 1511，所以 DMG / DMGX / XR 里 1511 的条目由本脚本直接写（不走 build_dmg / build_dmgx）。
改动：
- 战技：令使改成“施放战技时”给（原来写成每回合）；战技本身是辅助，随后发动 1 次追加攻击（atkSkill 关、加 fua）；令使持有者欢愉度 +20%（5 魂 22%）。
- 行迹愚弄众神的玩笑：战技的追加攻击 +1 战技点；额外 20% 欢愉伤害（XR）。
- 天赋：我方笑点首次达到 40 后（+1 愿力之后）我方全体暴击伤害 +40%（5 魂 44%）3 回合 —— 新触发 p40。
- 行迹盒中蕴藏的世界：速度 ≥125 / ≥150 时欢愉度 +120% / +150%。
- E1 增笑 15%；E4 计入队友好活当赏（代码）；E2 / E3 / E5 / E6 说明；DMGX.lvup 3 魂普攻 +1 / 终结技 +2，5 魂战技 / 天赋 +2（欢愉技 3 / 5 魂各 +1 原来就有）。
- DMG：普攻、战技追加攻击（f）、终结技（200% + 5×60% 随机）、欢愉技 60%，15 级参数照抄官方。
用法：python3 tools/aha_fix41.py index.html"""
import re, json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = open(P, encoding='utf-8').read()
assert 'if (s.tv >= 40) return;' in s, '版本号不对'

def sub1(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)

# ---------- DB ----------
m = re.search(r'const DB = (\{.*?\});\n', s); DB = json.loads(m.group(1))
C = {c['id']: c for c in DB['chars']}; A = C[1511]
OLD_LS = '战技：令使目标每次回合开始时，阿哈 +1 愿力（目标可改）'
NEW_LS = '战技：施放战技时使指定队友获得【「欢愉」令使】（整场，直到换下一个目标），持有者每次回合开始时阿哈 +1 愿力（目标在这里改）'
ls = next(e for e in A['eff'] if e['n'] == OLD_LS); ls['t'] = 'skill'; ls['n'] = NEW_LS
A['notes'] = [x for x in A['notes'] if not x.startswith('天赋：我方笑点首次达到40点后')]
assert not A['notes']
i = A['eff'].index(ls) + 1
NEW = [
    dict(y='dbuf', t='skill', tg='$ally', m='el', v=20, lv=[5, 22], d=0, bk='lingshi', n='战技：【「欢愉」令使】持有者欢愉度 +20%（5 魂 22%；目标要和上一条令使选同一个人）'),
    dict(y='fua', t='skill', tg='self', v=0, n='战技：给出令使后立即发动追加攻击，对敌方全体造成 50% 量子属性欢愉伤害（5 魂 55%）'),
    dict(y='sp', t='fua', tg='self', v=1, n='行迹愚弄众神的玩笑：战技的追加攻击恢复 1 个战技点'),
    dict(y='dbuf', t='p40', tg='team', m='cd', v=40, lv=[5, 44], d=3, bk='p40', n='天赋：我方笑点首次达到 40 点后（先 +1 愿力），我方全体暴击伤害 +40%（5 魂 44%），持续 3 回合；阿哈回合结束后可再次触发'),
    dict(y='dbuf', t='start', tg='self', m='el', v=120, ms=125, d=0, bk='box1', n='行迹盒中蕴藏的世界：速度 ≥125 时欢愉度 +120%（按战斗开始时的速度；卡片欢愉度照面板填时如果面板已经算进去就关掉这两条）'),
    dict(y='dbuf', t='start', tg='self', m='el', v=30, ms=150, d=0, bk='box2', n='行迹盒中蕴藏的世界：速度 ≥150 时欢愉度共 +150%（再 +30%；面板已经算进去就关掉）'),
]
A['eff'][i:i] = NEW
INFO = [
    dict(y='info', t='start', tg='self', n='普攻【点星，开幕！】：对敌方单体 50% 量子属性欢愉伤害（3 魂 55%），已算'),
    dict(y='info', t='ult', tg='self', n='终结技【啊哈！宇宙笑点大爆炸】：阿哈行动提前 20%，阿哈获得【欢愉万相】3 回合（她每回合开始时 −1），对敌方全体 200% 量子属性欢愉伤害，再 5 次随机单体各 60%（3 魂 216% / 64.8%），已算'),
    dict(y='info', t='ult', tg='self', n='固有行迹【欢愉万相★无中生有】：欢愉万相期间我方「欢愉」命途升格（笑点→爽点、好活当赏→绝活共赏，队友的固有行迹生效），阿哈时刻结束时返还消耗爽点的 10%；阿哈暴击率 +12%、无视 30% 防御（2 魂 +20% / 60%），已算'),
    dict(y='info', t='start', tg='self', n='天赋【阿哈正传】：阿哈和队友造成伤害时，敌人额外获得损失生命值 25% 的【欢愉负债】（最多生命上限 10%）—— 敌人生命值不做，没建模'),
    dict(y='info', t='aha', tg='self', n='欢愉技【满月，是神在的时间】：始终在阿哈时刻最后施放，对敌方全体 60% 量子属性欢愉伤害（3 / 5 魂各 +1 级），已算；另按本次阿哈时刻我方非真实伤害总和的 20% 造成真实伤害（敌方全体均分，4 魂 25%），没算'),
    dict(y='info', t='skill', tg='self', n='行迹愚弄众神的玩笑：战技的追加攻击额外造成 20% 欢愉伤害（原文“对应属性”= 令使持有者的属性；按阿哈的欢愉度算 1 段），不算 1 次攻击'),
]
A['eff'].extend(INFO)

def eid(r):
    e = next((e for e in A['eid'] if e['r'] == r), None)
    if not e: e = {'r': r, 'eff': [], 'notes': []}; A['eid'].append(e)
    return e
eid(1)['eff'].append(dict(y='dbuf', t='start', tg='team', m='lm', v=15, d=0, bk='ahae1', n='E1：星神★阿哈在场时我方全体欢愉伤害增笑 15%'))
eid(2)['eff'].append(dict(y='info', t='start', tg='self', n='E2 在祂的眼睛和你之间：「欢愉」命途升格加强 —— 欢愉万相期间阿哈暴击率 +20%、无视 60% 防御（代替 12% / 30%），队友固有行迹用强化数值，已算'))
eid(3)['eff'].append(dict(y='info', t='start', tg='self', n='E3 牌叠起，令悲喜轮回：终结技 +2 级、普攻 +1 级、欢愉技 +1 级（伤害倍率已按星魂换）'))
eid(4)['eff'].append(dict(y='info', t='start', tg='self', n='E4 黑箱一个玩笑的命运：阿哈造成的欢愉伤害额外计入队友持有的【好活当赏】总和的 100%（已算）；欢愉技真实伤害倍率 +25%（真实伤害没算）'))
eid(5)['eff'].append(dict(y='info', t='start', tg='self', n='E5 台前幕后，是我非我：战技 +2、天赋 +2、欢愉技 +1 级（令使欢愉度 22%、追加攻击 55%、天赋暴伤 44%，已按星魂换）'))
eid(6)['eff'].append(dict(y='info', t='start', tg='self', n='E6：敌方目标始终至少有生命上限 20% 的【欢愉负债】（没建模）'))
A['eid'].sort(key=lambda z: z['r'])
A['x']['atkSkill'] = False
s = s[:m.start(1)] + json.dumps(DB, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]

# ---------- DMG / DMGX / XR ----------
def jline(name):
    i = s.index(f'const {name}=') + len(f'const {name}=')
    o, end = json.JSONDecoder().raw_decode(s, i); return o, i, end
def jput(name, o):
    global s
    _, i, end = jline(name); s = s[:i] + json.dumps(o, ensure_ascii=False, separators=(',', ':')) + s[end:]
B = [0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7]
SK = [0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.40625, 0.4375, 0.46875, 0.5, 0.525, 0.55, 0.575, 0.6, 0.625]
UA = [1.2, 1.28, 1.36, 1.44, 1.52, 1.6, 1.7, 1.8, 1.9, 2, 2.08, 2.16, 2.24, 2.32, 2.4]
UR = [0.36, 0.384, 0.408, 0.432, 0.456, 0.48, 0.51, 0.54, 0.57, 0.6, 0.624, 0.648, 0.672, 0.696, 0.72]
EL = [0.3, 0.33, 0.36, 0.39, 0.42, 0.45, 0.4875, 0.525, 0.5625, 0.6, 0.63, 0.66, 0.69, 0.72, 0.75]
r5 = lambda x: round(x, 6)
D, _, _ = jline('DMG')
D['1511'] = {
    'b': dict(v=B, adj=[], rnd=[], tg=1, el=1, stat='lv', n='点星，开幕！', max=10),
    'f': dict(v=SK, adj=[], rnd=[], tg=3, el=1, stat='lv', n='此乃令使，阿哈认证™（追加攻击）', max=15),
    'u': dict(v=UA, adj=[], rnd=[r5(5 * x) for x in UR], tg=3, el=1, stat='lv', n='啊哈！宇宙笑点大爆炸', max=15),
    'e': dict(v=EL, adj=[], rnd=[], tg=3, el=1, stat='lv', n='满月，是神在的时间', max=15),
}
jput('DMG', D)
X, _, _ = jline('DMGX'); X['lvup']['1511'] = {'b': 3, 'u': 3, 's': 5, 't': 5}; jput('DMGX', X)
R, _, _ = jline('XR')
R['1511'] = [{'k': 'ls', 'n': '行迹愚弄众神的玩笑：战技的追加攻击额外造成 20% 欢愉伤害（按 1 段算，不视为攻击）', 'on': ['f'], 'kind': 'el', 'v': [0.2]}]
jput('XR', R)

# ---------- 代码 ----------
sub1('else if (!u.punchUsed) { u.punchUsed = true; curWhy = `我方笑点首次达到 ${at}`; addEnergy(u, 1, false); }',
     'else if (!u.punchUsed) { u.punchUsed = true; curWhy = `我方笑点首次达到 ${at}`; addEnergy(u, 1, false); fireCnt(u, "p40"); }   // 星神★阿哈天赋：随后全队暴伤（触发 p40）')
sub1('cnt0: "计数归零时", ', 'cnt0: "计数归零时", p40: "笑点首次达到阈值时", ')
assert s.count('["cnt0", "计数归零时"]') == 2
s = s.replace('["cnt0", "计数归零时"]', '["cnt0", "计数归零时"], ["p40", "笑点首次达到阈值时（阿哈天赋）"]')
sub1("    let bg = inAha ? num(rec.consumed, 0) : bangerAt(u, rec);\n",
     "    let bg = inAha ? num(rec.consumed, 0) : bangerAt(u, rec);\n"
     "    // 星神★阿哈 4 魂：她造成的欢愉伤害额外计入队友持有的【好活当赏】总和的 100%\n"
     "    if (tidOf(u) === \"1511\" && num(u.eid) >= 4) for (const x of S.units) if (x !== u && x.kind === \"ally\" && !x.sm) bg += bangerAt(x, rec);\n")

# ---------- 迁移 tv 41 ----------
FIX = {"1511": {"drop": [], "map": {}, "trig": {}, "add": [x['n'] for x in NEW], "set": {"atkSkill": False}}}
sub1('  const fixTpl40 = s => { fixTpl(s, TPLFIX40); };\n',
     '  const fixTpl40 = s => { fixTpl(s, TPLFIX40); };\n'
     '  const TPLFIX41 = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
     '  const fixTpl41 = s => {   // 星神★阿哈：令使改成施放战技时（保留用户选的目标），令使欢愉度跟令使同一个目标\n'
     f'    for (const u of s.units) {{ const T = u.kind === "ally" && !u.sm ? tplOf(u) : null; if (!T || T.id !== 1511) continue; for (const e of u.effects) if (!e.eq && e.note === {json.dumps(OLD_LS, ensure_ascii=False)}) {{ if (e.trigger === "turn") e.trigger = "skill"; e.note = {json.dumps(NEW_LS, ensure_ascii=False)}; }} }}\n'
     '    fixTpl(s, TPLFIX41);\n'
     f'    for (const u of s.units) {{ const T = u.kind === "ally" && !u.sm ? tplOf(u) : null; if (!T || T.id !== 1511) continue; const a = u.effects.find(e => !e.eq && e.note === {json.dumps(NEW_LS, ensure_ascii=False)}), b = u.effects.find(e => !e.eq && e.note === {json.dumps(NEW[0]["n"], ensure_ascii=False)}); if (a && b) b.target = a.target; }}\n'
     '  };\n')
sub1('    if (s.tv >= 40) return;\n', '    if (s.tv >= 41) return;\n')
sub1('    if (!(s.tv >= 40)) fixTpl40(s);\n    s.tv = 40;\n', '    if (!(s.tv >= 40)) fixTpl40(s);\n    if (!(s.tv >= 41)) fixTpl41(s);\n    s.tv = 41;\n')
sub1('  if (!(S.tv >= 40)) { migrateTpl(S); lastSaved = JSON.stringify(S); }', '  if (!(S.tv >= 41)) { migrateTpl(S); lastSaved = JSON.stringify(S); }')
sub1('fixTpl39(s); } finally { S = keep; } s.tv = 39; return; }', 'if (!(s.tv >= 39)) fixTpl39(s); if (!(s.tv >= 40)) fixTpl40(s); if (!(s.tv >= 41)) fixTpl41(s); } finally { S = keep; } s.tv = 41; return; }')   # 老存档的快速路径之前停在 39
open(P, 'w', encoding='utf-8').write(s)
print('ok')
