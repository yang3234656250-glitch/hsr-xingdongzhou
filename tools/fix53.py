"""tv 53：每日校对 2026-11-07（刃 1205、素裳 1206、驭空 1207），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix53.py index.html（需要 /tmp/sr/character_skills.json）
- 刃【强化版】：数值、触发、回能（普攻 20 / 无间剑树 30 / 战技 0 / 终结技 5 / 天赋追击 10 + 行迹 15）、战技 BPNeed 1 都对；
  只改说明：E2 旁注“1 / 6 魂按生命值的部分没算”和 E6 旁注“追加攻击增伤不做”已经过时（E1 在 DMG.u.e1、E6 在 XR e6 里算了）。
- 素裳：E6“天赋的加速效果可以叠加，最多 2 层，且进入战斗后立即获得 1 层”原来漏了：天赋加速改成共用增益键（bk sush、6 魂起 2 层），
  E6 补开局 1 层；伤害显示补【剑势】附加伤害（33% 概率 100% 攻击力，按期望 0.33；终结技 2 回合内战技额外 2 次判定、每次 50%，
  用 rx 标记 sush 判断），逐寇（剑势伤害每次 +2.5%，最多 10 层）没算。
- 驭空：【鸣弦号令】按原文做成计数（上限 2）+ 状态：战技获得 2 层；每次我方其他目标回合结束 −1，驭空自己施放普攻的回合结束也 −1
  （施放战技的回合不移除）；归零时移除状态。全队攻击力、终结技暴击率 / 暴击伤害、E4 增伤都跟着状态走（原来按到驭空下回合 / 1 回合）；
  行迹气壮（持有时我方目标行动后 +2 能量）改成按状态默认开启；秘技“主动攻击进入战斗时获得 2 层”（默认关）；
  E6“施放终结技时先获得 1 层”（pre，先于终结技的暴击判定）；E2“我方任意单体能量等于上限时 +5 能量，每个单体 1 次，
  驭空施放终结技后重置”用新触发 eMax（我方角色能量从未满变成满时）；E1 进战全队加速按每个角色自己的回合（cnt own，和艾丝妲一样）。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 53
assert f'if (s.tv >= {TV - 1}) return;' in s
SK = json.load(open('/tmp/sr/character_skills.json'))
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

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}

# ---------- 刃 1205（只改过时的说明）----------
c = C[1205]
assert prm('1120503')[9][0] == 1.5 and prm('1120503')[9][4] == 1.2 and prm('1120504')[9][1] == 1.3
e2 = next(e for e in c['eid'] if e['r'] == 2)['eff'][0]
assert '没算' in e2['n']
e2['n'] = 'E2：【地狱变】期间暴击率 +15%'
e6 = next(e for e in c['eid'] if e['r'] == 6)
assert '追加攻击增伤不做' in e6['notes'][0]
e6['notes'] = ['E6 命留魂销，复返此身：充能的层数上限降低至 4 层（已按星魂自动把计数器“满 5 点”改成 4 点）；天赋追加攻击额外 + 生命上限 50% 的伤害在伤害显示里算']
FIX['1205'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}}

# ---------- 素裳 1206 ----------
c = C[1206]
p = prm('120604'); assert p[9][0] == 0.2 and p[11][0] == 0.21 and p[9][1] == 2
tf = find(c['eff'], lambda x: x['y'] == 'spd' and x['t'] == 'break'); o_tf = tf['n']
assert tf['v'] == 20 and tf['d'] == 2 and tf['lv'] == [3, 21.0]
tf.update(bk='sush', ste=[6, 2], n='天赋：场上有敌方目标的弱点被击破时速度 +20%，持续 2 回合（E6 起可叠 2 层）')
pu = prm('120603'); assert pu[9][1:4] == [2, 0.5, 0.3] and pu[11][3] == 0.324, pu[9]
rx = dict(y='dbuf', t='ult', tg='self', m='rx', sc='sush', v=1, d=2, bk='ult', n='终结技：持续 2 回合内施放战技时额外增加 2 次【剑势】判定（伤害显示用的标记）')
k = c['eff'].index(find(c['eff'], lambda x: x['y'] == 'dbuf' and x['t'] == 'ult')) + 1
c['eff'].insert(k, rx)
assert not any(e['r'] == 6 for e in c['eid'])
c['eid'].append({'r': 6, 'eff': [dict(y='spd', t='start', tg='self', m='pct', v=20, lv=[3, 21.0], d=2, bk='sush', st=2,
                                       n='E6 上善若水：进入战斗后立即获得 1 层天赋的加速效果（速度 +20%，持续 2 回合）')], 'notes': []})
c['eid'].sort(key=lambda e: e['r'])
FIX['1206'] = {'drop': [o_tf], 'trig': {o_tf: 'break'}, 'map': {o_tf: tf['n']}, 'add': [tf['n'], rx['n']], 'sm': {}}

# ---------- 驭空 1207 ----------
c = C[1207]
ps = prm('120702'); assert ps[9] == [2, 0.8] and ps[11] == [2, 0.88], ps[9]
pu = prm('120703'); assert pu[9][1:] == [0.28, 0.65] and pu[11][1:] == [0.294, 0.702], (pu[9], pu[11])
assert 'cnt' not in c
c['cnt'] = {'n': '鸣弦号令', 'at': 0, 'max': 2}
ST = '鸣弦号令'; BK = 'st:' + ST
o_q = find(c['eff'], lambda x: x['y'] == 'energy' and x['t'] == 'ally')['n']
o_a = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'atkP')['n']
o_cr = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'cr')['n']
o_cd = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'cd')['n']
cy = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'dmg')
T1 = dict(y='count', t='start', tg='self', m='set', v=2, off=1, n='秘技云鸢逐风：主动攻击进入战斗时驭空获得 2 层【鸣弦号令】（用了秘技再启用）')
T2 = dict(y='state', t='start', tg='self', sn=ST, v=1, d=0, off=1, n='秘技云鸢逐风：进入战斗时持有【鸣弦号令】（和上一条一起开关）')
S1 = dict(y='count', t='skill', tg='self', m='set', v=2, n='战技：获得 2 层【鸣弦号令】（最多 2 层）')
S2 = dict(y='state', t='skill', tg='self', sn=ST, v=1, d=0, n='战技：持有【鸣弦号令】（层数归零时移除）')
A = dict(y='dbuf', t='skill', o='start', ns=ST, tg='team', m='atkP', v=80, lv=[3, 88], d=0, bk=BK, n='战技：驭空持有【鸣弦号令】时我方全体攻击力 +80%')
U1 = dict(y='dbuf', t='ult', ns=ST, tg='team', m='cr', v=28, lv=[5, 29.4], d=0, bk=BK, n='终结技：施放时若持有【鸣弦号令】，我方全体暴击率 +28%（跟着【鸣弦号令】）')
U2 = dict(y='dbuf', t='ult', ns=ST, tg='team', m='cd', v=65, lv=[5, 70.2], d=0, bk=BK, n='终结技：同时我方全体暴击伤害 +65%（跟着【鸣弦号令】）')
Q = dict(y='energy', t='ally', aw='all', ns=ST, tg='self', v=2, m='er', n='行迹气壮：持有【鸣弦号令】时，每当我方目标行动后驭空额外恢复 2 点能量')
R1 = dict(y='count', t='ally', aw='others', tg='self', v=-1, n='战技：每次我方其他目标回合结束时移除 1 层【鸣弦号令】')
R2 = dict(y='count', t='ally', aw='self', aa=['basic', 'ebasic'], tg='self', v=-1, n='战技：驭空自己的回合结束时也移除 1 层（施放战技获得【鸣弦号令】的回合不移除）')
Z = dict(y='state', t='cnt0', tg='self', sn=ST, v=0, n='战技：【鸣弦号令】层数归零时移除')
c['eff'] = [T1, T2, S1, S2, A, U1, U2, Q, R1, R2, Z, cy]
e1 = next(e for e in c['eid'] if e['r'] == 1)['eff'][0]
assert e1['t'] == 'start' and e1['v'] == 10 and e1['d'] == 2 and 'cnt' not in e1
e1.update(cnt='own', n='E1 天舶飞将，枕弧待战：进入战斗时我方全体速度 +10%，持续 2 回合（按每个角色自己的回合）')
e2 = next(e for e in c['eid'] if e['r'] == 2)
assert not e2['eff']
e2['eff'] = [dict(y='energy', t='eMax', aw='all', pw=1, acR='ult', tg='self', v=5, m='er',
                  n='E2 青霄驰骋，驱驭苍穹：我方任意单体能量达到上限时驭空额外恢复 5 点能量（每个单体 1 次，驭空施放终结技后重置）')]
e2['notes'] = []
e4 = next(e for e in c['eid'] if e['r'] == 4)['eff'][0]
assert e4['m'] == 'dmg' and e4['v'] == 30
e4.update(t='skill', o='ult', ns=ST, d=0, bk=BK, n='E4 百里闻风，九曲响镝：持有【鸣弦号令】时驭空造成的伤害 +30%')
assert not any(e['r'] == 6 for e in c['eid'])
c['eid'].append({'r': 6, 'eff': [
    dict(y='count', t='ult', tg='self', v=1, pre=1, n='E6 弦栝如雷，铣珧激荡：施放终结技时先获得 1 层【鸣弦号令】'),
    dict(y='state', t='ult', tg='self', sn=ST, v=1, d=0, pre=1, n='E6：先持有【鸣弦号令】（终结技的暴击率 / 暴击伤害就能生效）'),
    dict(y='dbuf', t='ult', ns=ST, pre=1, tg='team', m='atkP', v=80, lv=[3, 88], d=0, bk=BK, n='E6：持有【鸣弦号令】时我方全体攻击力 +80%（终结技获得的那层）')], 'notes': []})
c['eid'].sort(key=lambda e: e['r'])
c['notes'] = (c.get('notes') or []) + ['【鸣弦号令】“每次我方目标回合结束时移除 1 层”：行动后的气壮回能先算、再移除（同一次行动里谁先结算原文没写）；额外回合也算一个回合']
newN = [x['n'] for x in c['eff'] if x is not cy]
FIX['1207'] = {'drop': [o_q, o_a, o_cr, o_cd], 'trig': {o_q: 'ally', o_a: 'skill', o_cr: 'ult', o_cd: 'ult'},
               'map': {o_q: Q['n'], o_a: A['n'], o_cr: U1['n'], o_cd: U2['n']}, 'add': newN, 'off0': [o_q], 'sm': {}}
put(m, DB)

# ---------- XR：素裳【剑势】 ----------
m, X = grab('XR')
assert '1206' not in X
p2 = prm('120602'); assert p2[9][2] == 0.33 and p2[9][1] == 1 and abs(p2[11][1] - 1.1) < 1e-9, p2[9]
X['1206'] = [dict(k='js', n='战技【剑势】：33% 概率附加 100% 攻击力的伤害（按期望 0.33；目标弱点击破时必定发动，可在卡片上改）', on=['s'], st='atk', v=[0.33, 0.363], lk='s'),
             dict(k='js2', n='终结技【剑势】额外判定：2 次 × 33% × 原伤害 50%（终结技后 2 回合内的战技）', on=['s'], st='atk', v=[0.33, 0.363], lk='s', who='flag', flag='sush', self=1)]
put(m, X)

# ---------- 新触发 eMax：我方角色能量从未满变成满时（驭空 E2）----------
rep("    function addEnergy(u, amt, useER) {\n",
    "    let eMaxDepth = 0;\n    function addEnergy(u, amt, useER) {\n")
rep("      if (u.cntSrc === \"energy\" && u.e - before > 0) addCnt(u, u.e - before);",
    "      if (!noStdE(u) && before < c.maxE - 1e-9 && u.e >= c.maxE - 1e-9 && eMaxDepth < 2) { eMaxDepth++; try { teamFire(\"eMax\", u); } finally { eMaxDepth--; } }   // 我方角色能量达到上限时（驭空 E2；追忆 / 新蕊这类不算）\n"
    "      if (u.cntSrc === \"energy\" && u.e - before > 0) addCnt(u, u.e - before);")
rep('const TEAMT = ["ally", "atk", "aSk", "aUlt", "aFua", "aTurn", "hgive", "aHeal", "aGive"];',
    'const TEAMT = ["ally", "atk", "aSk", "aUlt", "aFua", "aTurn", "hgive", "aHeal", "aGive", "eMax"];')
rep('"hpLoss", "aHeal", "aGive"];', '"hpLoss", "aHeal", "aGive", "eMax"];')
rep('["aGive", "我方提供治疗或护盾时"], ["hpLoss", "我方目标生命值降低时"]',
    '["aGive", "我方提供治疗或护盾时"], ["eMax", "我方角色能量达到上限时"], ["hpLoss", "我方目标生命值降低时"]', 2)
rep('cntUp: "计数增加后"', 'cntUp: "计数增加后", eMax: "我方角色能量达到上限时"')

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-07（刃、素裳、驭空，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
