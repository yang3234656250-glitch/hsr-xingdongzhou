"""tv 52：每日校对 2026-11-06（卢卡 1111、青雀 1201、罗刹 1203、景元 1204），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix52.py index.html（需要 /tmp/sr/character_skills.json）
- 卢卡：
  · 官方数据里卢卡没有强化版技能（没有 11111xx），效果名去掉“【强化版】”。
  · 【斗志】做成计数（开局 1 层、最多 4 层）：普攻【直冲拳】+1（【斗志】≥2 时普攻会强化，所以只在 <2 时）、战技 +1、终结技 +2、强化普攻 −2；
    行迹循环制动“每获得 1 层【斗志】额外恢复 3 点能量”按每次实际获得的层数（原来只在战技 +3，普攻和终结技漏了；已有 4 层时不获得、不回能）。
    秘技“额外获得 1 层”、E2“战技击中物理弱点 +1 层”默认关闭；E4 补上普攻获得的那层。
  · DMG b2（直冲碎天拳）原来是普攻的 100%，改成 3 段直冲拳 + 碎天拳（6 级 3×20% + 80% = 140%）；行迹粉碎斗志（每段直冲拳 50% 再多 1 段）按期望进 XR。
- 青雀：行迹抢杠改成施放强化普攻后（原来是普攻 + 默认关）并默认开；行迹争番加“单场只触发 1 次”；
  E2 抽牌回能改成我方目标回合开始时（含自己，原来是队友行动后）；E6 改成施放强化普攻后、默认开。
- 罗刹：战技的“我方任意单体当前生命值 ≤50% 时立即对其触发 1 次战技效果（不耗战技点，2 回合后可再次触发）”原来没做：
  hpLoss（任意我方目标）+ 新条件 hlv（事件对象当前生命值 ≤50%）→ 回复 + 【白花之刻】+1 + 冷却状态 2 回合（罗刹回合开始时 −1），默认开启；
  秘技“下一次战斗开始时立即触发天赋”= 开局展开结界（默认关）。
- 景元：E2 改成【神君】行动后（原来是神君回合开始时）；补秘技“神君第 1 回合 +3 段”（默认关）。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 52
assert f'if (s.tv >= {TV - 1}) return;' in s
SK = json.load(open('/tmp/sr/character_skills.json'))
prm = lambda sid: SK[sid]['params']
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:90], s.count(x)); s = s.replace(x, y)
def find(L, pred):
    R = [x for x in L if pred(x)]; assert len(R) == 1, R; return R[0]

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}

# ---------- 卢卡 1111 ----------
c = C[1111]
assert 'cnt' not in c and '11111' not in ''.join(k for k in SK if k.startswith('11111'))
c['cnt'] = {'n': '斗志', 'at': 0, 'max': 4}
old = find(c['eff'], lambda x: x['y'] == 'energy' and x['t'] == 'skill'); o_old = old['n']
assert o_old.startswith('【强化版】') and old['v'] == 3
ini = dict(y='count', t='start', tg='self', m='set', v=1, n='天赋：战斗开始时卢卡持有 1 层【斗志】')
tq_e = dict(y='energy', t='start', tg='self', v=3, m='er', ltc=4, off=1, n='秘技抢先者：进入战斗后额外获得 1 层【斗志】，行迹循环制动 +3 能量（用了秘技再启用）')
tq_c = dict(y='count', t='start', tg='self', v=1, off=1, n='秘技抢先者：进入战斗后额外获得 1 层【斗志】（用了秘技再启用）')
b_e = dict(y='energy', t='basic', tg='self', v=3, m='er', ltc=2, n='行迹循环制动：普攻【直冲拳】获得 1 层【斗志】时额外 +3 能量（【斗志】≥2 时普攻会强化为直冲碎天拳，不获得）')
b_c = dict(y='count', t='basic', tg='self', v=1, ltc=2, n='天赋：施放普攻【直冲拳】后获得 1 层【斗志】（【斗志】≥2 时普攻会强化为直冲碎天拳）')
s_e = dict(y='energy', t='skill', tg='self', v=3, m='er', ltc=4, n='行迹循环制动：战技获得 1 层【斗志】时额外 +3 能量（已有 4 层时不获得）')
s_c = dict(y='count', t='skill', tg='self', v=1, n='天赋：施放战技【裂伤拳】后获得 1 层【斗志】（最多 4 层）')
eb = dict(y='count', t='ebasic', tg='self', v=-2, n='强化普攻直冲碎天拳：消耗 2 层【斗志】')
u_e1 = dict(y='energy', t='ult', tg='self', v=3, m='er', ltc=4, n='行迹循环制动：终结技获得【斗志】（第 1 层）时额外 +3 能量')
u_c1 = dict(y='count', t='ult', tg='self', v=1, n='终结技：获得 2 层【斗志】（第 1 层）')
u_e2 = dict(y='energy', t='ult', tg='self', v=3, m='er', ltc=4, n='行迹循环制动：终结技获得【斗志】（第 2 层）时额外 +3 能量')
u_c2 = dict(y='count', t='ult', tg='self', v=1, n='终结技：获得 2 层【斗志】（第 2 层）')
i = c['eff'].index(old)
c['eff'][i:i + 1] = [ini, tq_e, tq_c, b_e, b_c, s_e, s_c, eb, u_e1, u_c1, u_e2, u_c2]
assert not any(e['r'] == 2 for e in c['eid'])
e2 = {'r': 2, 'eff': [], 'notes': []}; c['eid'].append(e2); c['eid'].sort(key=lambda e: e['r'])
e2['eff'] = [dict(y='energy', t='skill', tg='self', v=3, m='er', ltc=4, off=1, n='E2：战技击中物理弱点的敌人时再获得 1 层【斗志】，行迹循环制动 +3 能量（敌人弱点是物理时启用）'),
             dict(y='count', t='skill', tg='self', v=1, off=1, n='E2：战技击中物理弱点的敌人时再获得 1 层【斗志】（敌人弱点是物理时启用）')]
e4 = next(e for e in c['eid'] if e['r'] == 4)
assert len(e4['eff']) == 3
e4['eff'].insert(0, dict(y='dbuf', t='basic', tg='self', m='atkP', v=5, st=4, d=0, bk='e4', ltc=2, n='E4：普攻【直冲拳】获得 1 层【斗志】时攻击力 +5%（最多 4 层）'))
c['notes'] = (c.get('notes') or []) + ['【斗志】≥2 时游戏里普攻会自动强化为直冲碎天拳：这里仍由你在“平时 / 每次行动”里选强普；选了普攻而【斗志】≥2 时不获得【斗志】']
new = [ini['n'], tq_e['n'], tq_c['n'], b_e['n'], b_c['n'], s_e['n'], s_c['n'], eb['n'], u_e1['n'], u_c1['n'], u_e2['n'], u_c2['n']]
FIX['1111'] = {'drop': [o_old], 'trig': {o_old: 'skill'}, 'map': {o_old: s_e['n']}, 'add': new, 'sm': {}}

# ---------- 青雀 1201 ----------
c = C[1201]
p = prm('120102'); assert p[9][1] == 0.28 and p[11][1] == 0.308
assert prm('120104')[11][0] == 0.792
qg = find(c['eff'], lambda x: x['n'] == '行迹抢杠（强化普攻后）'); o_qg = qg['n']
assert qg['t'] == 'basic' and qg.get('off')
qg.pop('off'); qg['t'] = 'ebasic'; qg['n'] = '行迹抢杠：施放强化普攻后速度 +10%，持续 1 回合'
zf = find(c['eff'], lambda x: x['n'].startswith('行迹争番')); o_zf = zf['n']
zf['first'] = 1; zf['n'] = '行迹争番：施放战技时恢复 1 个战技点（单场战斗只能触发 1 次）'
e2 = next(e for e in c['eid'] if e['r'] == 2)
a = find(e2['eff'], lambda x: x['t'] == 'ally')
a.update(t='aTurn', aw='all', n='E2：我方目标回合开始时青雀抽牌，立即恢复 1 点能量')
find(e2['eff'], lambda x: x['t'] == 'skill')['n'] = 'E2：战技抽牌，立即恢复 1 点能量'
e6 = next(e for e in c['eid'] if e['r'] == 6)['eff'][0]
assert e6['t'] == 'basic' and e6.get('off')
e6.pop('off'); e6['t'] = 'ebasic'; e6['n'] = 'E6：施放强化普攻后恢复 1 个战技点'
c['notes'] = (c.get('notes') or []) + ['终结技获得 4 张同花色琼玉牌后，下个回合开始进入【暗杠】（不能施放战技、普攻强化）：这里没有自动切换，请在“每次行动”里把那次选成强普']
FIX['1201'] = {'drop': [o_qg, o_zf], 'trig': {o_qg: 'basic', o_zf: 'skill'}, 'map': {o_qg: qg['n'], o_zf: zf['n']},
               'add': [qg['n'], zf['n']], 'off0': [o_qg], 'sm': {}}

# ---------- 罗刹 1203 ----------
c = C[1203]
sh = find(c['eff'], lambda x: x['y'] == 'heal' and x['t'] == 'skill')
p = prm('120302'); assert p[9][:4] == [0.6, 800, 0.5, 2] and p[11][:2] == [0.64, 890]
assert sh['v'] == 60 and sh['hf'] == 800 and sh['lv'] == [3, 64] and sh['lx'] == {'flat': [800, 890]}
CD = '白花的祈望冷却'
cond = dict(t='hpLoss', ew='any', hlv=50, ns='!' + CD)
ah = dict(y='heal', tg='evt', m='atk', v=60, hf=800, lv=[3, 64], lx={'flat': [800, 890]}, **cond,
          n='战技：我方任意单体当前生命值 ≤50% 时，罗刹立即对其触发 1 次战技效果（回复，不消耗战技点）')
ac = dict(y='count', tg='self', v=1, **cond, n='战技：自动触发的战技效果同样获得 1 层【白花之刻】')
ast = dict(y='state', tg='self', sn=CD, v=1, d=2, ts=1, **cond, n='战技：自动触发后 2 回合内不能再次触发（罗刹每回合开始时 −1）')
k = c['eff'].index(find(c['eff'], lambda x: x['y'] == 'count' and x['t'] == 'skill')) + 1
c['eff'][k:k] = [ah, ac, ast]
tq = dict(y='state', t='start', tg='self', sn='结界', d=2, v=1, off=1, n='秘技愚者的悲悯：下一次战斗开始时立即触发天赋，展开结界 2 回合（用了秘技再启用）')
c['eff'].append(tq)
FIX['1203'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [ah['n'], ac['n'], ast['n'], tq['n']], 'sm': {}}

# ---------- 景元 1204 ----------
c = C[1204]
assert prm('120407')[0][0] == 3
i = max(k for k, x in enumerate(c['eff']) if x['y'] == 'spd') + 1
TQ = [dict(y='spd', t='start', tg='sm:lord', v=10, m='flat', d=1, st=7, bk='lord', cnt='own', off=1,
           n=f'秘技摄召威灵：神君第 1 回合 +1 段（+10 速度，第 {j} 段，用了秘技再启用）') for j in (1, 2, 3)]
c['eff'][i:i] = TQ
e2 = next(e for e in c['eid'] if e['r'] == 2)['eff'][0]
assert e2['t'] == 'smTurn'
e2.pop('sk'); e2.update(t='ally', aw='sm', n='E2：神君行动后景元普攻、战技、终结技伤害 +20%，持续 2 回合')
FIX['1204'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [x['n'] for x in TQ], 'sm': {}}
put(m, DB)

# ---------- DMG / XR ----------
m, D = grab('DMG')
ps = prm('111108'); b2 = D['1111']['b2']; assert b2['v'][5] == 1.0
b2['v'] = [round(3 * q[0] + q[1], 4) for q in ps]; assert b2['v'][5] == 1.4
put(m, D)
m, X = grab('XR')
assert '1111' not in X
X['1111'] = [dict(k='fz', n='行迹粉碎斗志：强化普攻的每段直冲拳有 50% 固定概率再多 1 段（按期望 1.5 段 = 直冲碎天拳总倍率的 3/14）', on=['b2'], st='mult', v=[round(1.5 / 7, 4)])]
put(m, X)

# ---------- 新条件 hlv：事件对象（生命值降低的那个）当前生命值 ≤ X% ----------
rep("      if (x.hle) e.hpLE = x.hle;                  // 自己当前生命值 ≤ X% 才生效（符玄天赋）\n",
    "      if (x.hle) e.hpLE = x.hle;                  // 自己当前生命值 ≤ X% 才生效（符玄天赋）\n"
    "      if (x.hlv) e.hpLEv = x.hlv;                 // 事件对象当前生命值 ≤ X% 才生效（罗刹战技自动触发）\n")
rep("      if (num(eff.anyLE) > 0 && !U.some(",
    "      if (num(eff.hpLEv) > 0) { const T = evTarget, c = T && evHc != null ? evHc : T ? hpCur(T) : null, mx = T ? hpNow(T) : null; if (c == null || !(mx > 0) || c > mx * num(eff.hpLEv) / 100 + 1e-6) return; }   // 事件对象当前生命值 ≤ X%（按事件发生时）\n"
    "      if (num(eff.anyLE) > 0 && !U.some(")
rep("+ (num(e.anyLE) > 0 ? `（有角色生命 ≤${num(e.anyLE)}%）` : \"\")",
    "+ (num(e.hpLEv) > 0 ? `（事件对象生命 ≤${num(e.hpLEv)}%）` : \"\") + (num(e.anyLE) > 0 ? `（有角色生命 ≤${num(e.anyLE)}%）` : \"\")")

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-06（卢卡、青雀、罗刹、景元，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
