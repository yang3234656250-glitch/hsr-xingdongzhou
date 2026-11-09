"""tv 55：每日校对 2026-11-09（符玄 1208、镜流【强化版】1212、丹恒•饮月 1213、雪衣 1214），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix55.py index.html（需要 /tmp/sr/character_skills.json、character_ranks.json）
- 符玄：行迹太乙式盘“【穷观阵】开启时施放战技额外 +20 能量”加上状态条件（原来每次战技都 +20；第一次开阵那次不算）；
  【鉴知】暴击率和 E1 暴击伤害改成跟着【穷观阵】（bk st:穷观阵，原来固定 3 回合）；E4“处于【穷观阵】的我方其他目标受到攻击后”
  加状态条件、只算其他目标（新 evWho others）；补秘技“进入战斗时自动开启【穷观阵】，持续 2 回合”（默认关）。
- 镜流【强化版】（1121201～1121209）：【朔望】按原文做成计数（上限 4，E6 5），原来是“每 5 次战技一轮、开局从 3 算”的循环近似：
  无罅飞光后 +1、终结技攻击结束后 +1、我方目标累计受到伤害或消耗生命值 20 次 +1（新字段 nth：每第 N 次才生效）；
  有 2 层时进入【转魄】（状态，直到朔望归零）：额外 +1 层（E6 再 +1，用“设为 3 / 4”）、行动提前 100%、只能施放寒川映月、
  暴击率 +50%（3 魂 52%）、死境终结技增伤 +20%；寒川映月行动后 −1 朔望，归零退出并移除【月色】；
  【月色】按转魄内我方目标每次生命值降低 +1 层（每层暴伤 +44%，3 魂 48.4%，最多 5 层），原来按叠满；
  剑首：无罅飞光 +15、寒川映月 +8（原来一律 +15）；寒川映月本身回能 30（卡片战技回能 20 是无罅飞光的，另补 10）；
  转魄中普攻也消耗队友生命值；秘技 +15 能量、+1 朔望（默认关）。DMG 换成强化版的生命上限倍率；补 E1 单体额外 100% 攻击力（XR）。
- 丹恒•饮月：战技 BPNeed −1 → skillSP 0（去掉“+1 战技点抵消”）；终结技获得 2 个【逆鳞】（E2 +1，秘技 +1 默认关），
  强化普攻先用【逆鳞】抵扣战技点（计数，上限 3）。
- 雪衣：E6【恶报】上限 8 → 6（cnt.le）；DMG 追加攻击原来只写了 1 次 90%，改成 3 次总倍率 270%（12 级 297%）。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 55
assert f'if (s.tv >= {TV - 1}) return;' in s
SK = json.load(open('/tmp/sr/character_skills.json'))
RK = json.load(open('/tmp/sr/character_ranks.json'))
prm = lambda sid: SK[sid]['params']
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:90], s.count(x)); s = s.replace(x, y)
def find(L, pred):
    R = [x for x in L if pred(x)]; assert len(R) == 1, R; return R[0]
r4 = lambda v: round(v, 4)

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}

# ---------- 符玄 1208 ----------
c = C[1208]; QG = '穷观阵'; BQ = 'st:' + QG
p2 = prm('120802'); assert p2[9] == [0.65, 0, 3, 0.06, 0.12] and abs(p2[11][4] - 0.132) < 1e-9
assert '【穷观阵】开启时，符玄施放战技将额外恢复' in json.dumps(json.load(open('/tmp/sr/character_skill_trees.json'))['1208101'], ensure_ascii=False)
en = find(c['eff'], lambda x: x['y'] == 'energy' and x['t'] == 'skill'); o_en = en['n']
assert c['eff'].index(en) < c['eff'].index(find(c['eff'], lambda x: x['y'] == 'state'))   # 先判断再开阵：第一次开阵那次不算
en.update(ns=QG, n='行迹太乙式盘：【穷观阵】开启时施放战技额外 +20 能量（开阵前已经有【穷观阵】才算）')
cr = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'cr'); o_cr = cr['n']
assert cr['d'] == 3 and cr['lv'] == [3, 13.2]
cr.update(bk=BQ, d=0, n='战技：处于【穷观阵】的我方全体获得【鉴知】，暴击率 +12%（跟着【穷观阵】）')
hp = find(c['eff'], lambda x: x['y'] == 'hpup')
pt = prm('120807'); assert pt[0] == [20, 2]
T1 = dict(y='state', t='start', tg='self', sn=QG, d=2, v=1, off=1, n='秘技岁记否泰，固守四郭：进入战斗时自动开启【穷观阵】，持续 2 回合（用了秘技再启用）')
T2 = dict({k: v for k, v in hp.items() if k != 'n'}, t='start', off=1, n='秘技：开局【穷观阵】期间我方全体【鉴知】生命上限提高（用了秘技再启用）')
T3 = dict({k: v for k, v in cr.items() if k != 'n'}, t='start', off=1, n='秘技：开局【穷观阵】期间【鉴知】暴击率 +12%（用了秘技再启用）')
c['eff'] += [T1, T2, T3]
e1 = next(e for e in c['eid'] if e['r'] == 1)['eff']; z = e1[0]; assert z['m'] == 'cd' and z['v'] == 30
z.update(bk=BQ, d=0, n='E1 司危：【鉴知】暴击伤害 +30%（跟着【穷观阵】）')
e1.append(dict(z, t='start', off=1, n='E1：秘技开局的【鉴知】也暴击伤害 +30%（用了秘技再启用）'))
e4 = next(e for e in c['eid'] if e['r'] == 4)['eff'][0]; assert e4['t'] == 'hit' and e4['v'] == 5
e4.update(ew='others', ns=QG, n='E4 格泽：处于【穷观阵】的我方其他目标受到攻击后，符玄恢复 5 点能量')
FIX['1208'] = {'drop': [o_en, o_cr], 'trig': {o_en: 'skill', o_cr: 'skill'}, 'map': {o_en: en['n'], o_cr: cr['n']},
               'add': [en['n'], cr['n'], T1['n'], T2['n'], T3['n']], 'sm': {}}

# ---------- 镜流【强化版】 1212 ----------
c = C[1212]; ZP = '转魄'; BZ = 'st:' + ZP; SW = '朔望'
pt = prm('1121204'); assert pt[9] == [0.3, 0.05, 0.44, 5, 2, 1, 0.5, 20] and abs(pt[11][2] - 0.484) < 1e-9 and abs(pt[11][6] - 0.52) < 1e-9
assert 'SkillP' not in json.dumps(prm('1121209'))
old = c['eff']; hc = old[0]; assert hc['y'] == 'hpcost' and hc['v'] == 5 and hc['ns'] == ZP
drop = [x['n'] for x in old[1:]]; trig = {x['n']: x['t'] for x in old[1:]}
assert len(drop) == 13
new = [
    hc,
    dict(y='hpcost', t='basic', tg='oc', v=5, m='max', ns=ZP, n='【强化版】天赋：【转魄】状态下施放普攻也消耗队友各 5% 生命上限的生命值（最多降到 1 点）'),
    dict(y='energy', t='skill', tg='self', v=15, m='er', ns='!' + ZP, n='【强化版】行迹剑首：施放【无罅飞光】后额外 +15 能量'),
    dict(y='energy', t='skill', tg='self', v=8, m='er', ns=ZP, n='【强化版】行迹剑首：施放【寒川映月】后额外 +8 能量'),
    dict(y='energy', t='skill', tg='self', v=10, m='er', ns=ZP, n='【强化版】战技寒川映月本身回能 30（卡片上“战技回能 20”是无罅飞光的，这里补 10）'),
    dict(y='count', t='ally', aw='self', aa='skill', ns='!' + ZP, tg='self', v=1, n='【强化版】战技无罅飞光：获得 1 层【朔望】'),
    dict(y='count', t='ally', aw='self', au=1, aa='ult', tg='self', v=1, n='【强化版】终结技：攻击结束后获得 1 层【朔望】'),
    dict(y='count', t='ally', aw='self', aa='fskill', ns=ZP, tg='self', v=-1, n='【强化版】战技寒川映月：消耗 1 层【朔望】（归零时退出【转魄】）'),
    dict(y='count', t='hpLoss', ew='any', nth=20, tg='self', v=1, n='【强化版】天赋：我方目标累计受到伤害或消耗生命值 20 次后获得 1 层【朔望】'),
    dict(y='count', t='cntUp', ns='!' + ZP, nc=2, tg='self', m='set', v=3, lv=[6, 4], n='【强化版】天赋：拥有 2 层【朔望】时进入【转魄】，额外获得 1 层【朔望】（E6 再 +1）'),
    dict(y='advance', t='cntUp', ns='!' + ZP, nc=2, tg='self', v=100, n='【强化版】天赋：进入【转魄】时行动提前 100%'),
    dict(y='force', t='cntUp', ns='!' + ZP, nc=2, tg='self', v=999, m='fskill', n='【强化版】天赋：【转魄】中战技强化为【寒川映月】且仅能使用该战技（不耗战技点）'),
    dict(y='dbuf', t='cntUp', ns='!' + ZP, nc=2, tg='self', m='cr', v=50, lv=[3, 52], d=0, bk=BZ, n='【强化版】天赋：【转魄】状态暴击率 +50%（3 魂 52%）'),
    dict(y='dbuf', t='cntUp', ns='!' + ZP, nc=2, tg='self', m='dmg', v=20, sc='u', d=0, bk=BZ, n='【强化版】行迹死境：【转魄】状态下终结技伤害 +20%'),
    dict(y='state', t='cntUp', ns='!' + ZP, nc=2, tg='self', sn=ZP, v=1, d=0, n='【强化版】天赋：进入【转魄】（持续到【朔望】归零）'),
    dict(y='dbuf', t='hpLoss', ew='any', ns=ZP, tg='self', m='cd', v=44, lv=[3, 48.4], st=5, d=0, bk=BZ + '#ys',
         n='【强化版】天赋：【转魄】内我方目标受到伤害或消耗生命值时获得 1 层【月色】，每层暴击伤害 +44%（3 魂 48.4%），最多 5 层'),
    dict(y='state', t='cnt0', tg='self', sn=ZP, v=0, n='【强化版】天赋：【朔望】为 0 时退出【转魄】并移除所有【月色】'),
    dict(y='force', t='cnt0', tg='self', v=0, m='fskill', n='【强化版】天赋：退出【转魄】，战技恢复为【无罅飞光】'),
    dict(y='energy', t='start', tg='self', v=15, m='er', off=1, n='秘技古镜照神：进入战斗后恢复 15 点能量（用了秘技再启用）'),
    dict(y='count', t='start', tg='self', v=1, off=1, n='秘技古镜照神：进入战斗后获得 1 层【朔望】（用了秘技再启用；冻结没做）'),
]
assert prm('1121207')[0][5] == 15
c['eff'] = new
c['cnt'] = {'n': SW, 'at': 0, 'max': 4, 'lm': [6, 5]}
E6 = next(e for e in c['eid'] if e['r'] == 6)
assert E6['eff'][0]['v'] == 50 and E6['eff'][1]['v'] == 0
o6 = [x['n'] for x in E6['eff']]
E6['eff'] = [dict(y='dbuf', t='cntUp', ns=ZP, tg='self', m='cd', v=50, d=0, bk=BZ + '#e6', n='E6 蚀变于娄：【转魄】状态下暴击伤害 +50%（【朔望】上限 +1 和额外 1 层写在天赋里）')]
c['notes'] = (c.get('notes') or []) + ['【强化版】行迹霜魄（获得【朔望】时已到上限，下一次攻击无视 25% 防御）、效果抵抗没做；20 次计数里“每个目标每次受到攻击最多计算 1 次”按每次生命值降低算']
FIX['1212'] = {'drop': drop, 'trig': trig, 'map': {}, 'add': [x['n'] for x in new[1:]], 'sm': {},
               'set': {'cntName': SW, 'cntAt': 0, 'cntMax': 4}}

# ---------- 丹恒•饮月 1213 ----------
c = C[1213]; NL = '逆鳞'
pu = prm('121303'); assert pu[9] == [3, 1.4, 2, 3]
assert prm('121307')[0] == [1, 20, 1.2]
o1 = find(c['eff'], lambda x: x['y'] == 'sp' and x['t'] == 'skill')['n']
o2 = find(c['eff'], lambda x: x['y'] == 'sp' and x['t'] == 'ebasic')['n']
c['eff'] = [x for x in c['eff'] if x['n'] not in (o1, o2)]
N1 = dict(y='sp', t='ebasic', tg='self', v=-1, ltc=1, n='强化普攻：瞬华消耗 1 个战技点（有【逆鳞】时先用【逆鳞】抵扣；天矢阴 / 盘拏耀跃耗 2 / 3 点，回能 35 / 40，请自己改）')
N2 = dict(y='count', t='ebasic', tg='self', v=-1, nc=1, n='终结技【逆鳞】：可用来抵扣战技点消耗（这次强化普攻用 1 个【逆鳞】代替战技点）')
N3 = dict(y='count', t='ult', tg='self', v=2, n='终结技：获得 2 个【逆鳞】（最多持有 3 个）')
N4 = dict(y='count', t='start', tg='self', v=1, off=1, n='秘技掣空如虹：进入战斗后获得 1 个【逆鳞】（用了秘技再启用）')
c['eff'] = c['eff'][:1] + [N1, N2, N3] + c['eff'][1:] + [N4]
c['x']['skillSP'] = 0
c['cnt'] = {'n': NL, 'at': 0, 'max': 3}
e2 = next(e for e in c['eid'] if e['r'] == 2)
e2['eff'].append(dict(y='count', t='ult', tg='self', v=1, n='E2 九斿：施放终结技后额外获得 1 个【逆鳞】'))
c['notes'] = [n for n in c.get('notes', []) if '战技龙力自在只是强化普攻' not in n] + ['战技龙力自在只是强化普攻，不消耗战技点也不视为使用战技（官方 BPNeed −1）；模板默认每回合放强化普攻（瞬华）']
FIX['1213'] = {'drop': [o1, o2], 'trig': {o1: 'skill', o2: 'ebasic'}, 'map': {o2: N1['n']}, 'add': [N1['n'], N2['n'], N3['n'], N4['n']], 'sm': {},
               'set': {'cntName': NL, 'cntAt': 0, 'cntMax': 3, 'skillSP': 0}}

# ---------- 雪衣 1214 ----------
c = C[1214]
assert '6层' in RK['121406']['desc'] if '121406' in RK else True
assert c['cnt'] == {'n': '恶报', 'at': 8}
c['cnt']['le'] = [6, 6]
FIX['1214'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}}
put(m, DB)

# ---------- DMG / XR ----------
m, D = grab('DMG')
d = D['1212']
d['b'] = dict(d['b'], v=[r4(x[0]) for x in prm('1121201')], stat='hp', n='流影方晖（强化版）')
d['s'] = dict(d['s'], v=[r4(x[0]) for x in prm('1121202')], stat='hp', n='无罅飞光（强化版）')
d['s2'] = dict(d['s2'], v=[r4(x[0]) for x in prm('1121209')], adj=[r4(x[2]) for x in prm('1121209')], stat='hp', n='寒川映月（强化版）')
d['u'] = dict(d['u'], v=[r4(x[0]) for x in prm('1121203')], adj=[r4(x[2]) for x in prm('1121203')], stat='hp', n='昙华生灭，天河泻梦（强化版）')
assert d['b']['v'][5] == 0.5 and d['s']['v'][9] == 1.5 and d['s2']['v'][9] == 1.5 and d['s2']['adj'][9] == 0.75 and d['u']['v'][9] == 1.8 and d['u']['adj'][9] == 0.9
d = D['1214']['f']; pf = prm('121404'); assert pf[9][1] == 0.9 and d['v'][9] == 0.9
d['v'] = [r4(3 * x[1]) for x in pf]; d['n'] = '十王圣断，业报恒常（3 次随机单体）'
assert d['v'][9] == 2.7 and d['v'][11] == 2.97
put(m, D)
m, X = grab('XR')
assert '1212' not in X
X['1212'] = [dict(k='e1', n='E1 月犯天关：施放终结技或强化战技时若只攻击了 1 个敌方目标，额外造成 1 次镜流 100% 攻击力的伤害', on=['u', 's2'], st='atk', v=[1], e=1, eqN=1)]
put(m, X)

# ---------- 新字段 ----------
rep("      if (x.hfe) e.hpFEv = x.hfe;",
    "      if (x.hfe) e.hpFEv = x.hfe;\n"
    "      if (x.nth) e.nth = x.nth;                   // 每第 N 次满足条件才生效（镜流：我方目标累计 20 次生命值降低获得 1 层朔望）")
rep("      if (eff.skip1) { const k = (src ? src.id : \"ev\") + \":skip1:\" + eff.id; if (!firedMap[k]) { firedMap[k] = 1; return; } }   // 每场第 1 次不生效",
    "      if (eff.skip1) { const k = (src ? src.id : \"ev\") + \":skip1:\" + eff.id; if (!firedMap[k]) { firedMap[k] = 1; return; } }   // 每场第 1 次不生效\n"
    "      if (num(eff.nth) > 1) { const k = (src ? src.id : \"ev\") + \":nth:\" + eff.id; firedMap[k] = (firedMap[k] || 0) + 1; if (firedMap[k] % Math.round(num(eff.nth))) return; }   // 每第 N 次才生效（镜流 20 次）")
rep("      if (w === \"exsm\") return !own;\n",
    "      if (w === \"exsm\") return !own;\n      if (w === \"others\") return !!tg && tg !== u;   // 除自己外的我方目标（符玄 E4）\n")
rep('["char", "任何角色（不含召唤物 / 忆灵）"], ["any", "任何队友都算"]];',
    '["char", "任何角色（不含召唤物 / 忆灵）"], ["others", "除自己外的我方目标"], ["any", "任何队友都算"]];')
rep("+ (num(e.hpFEv) > 0 ? `（事件对象生命 ≥${num(e.hpFEv)}%）` : \"\")",
    "+ (num(e.hpFEv) > 0 ? `（事件对象生命 ≥${num(e.hpFEv)}%）` : \"\") + (num(e.nth) > 1 ? `（每第 ${num(e.nth)} 次）` : \"\")")

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-09（符玄、镜流、丹恒•饮月、雪衣，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
