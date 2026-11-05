"""tv 51：每日校对 2026-11-05（克拉拉 1107、桑博 1108、虎克 1109、玲可 1110），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix51.py index.html（需要 /tmp/sr/character_skills.json）
- 克拉拉：
  · 终结技“强化效果可生效 2 次”（E6 再 +1）原来没做次数（一条默认关闭、不限次数的“任意队友受击反击”）→ 计数【强化反击】：
    终结技设为 2（6 魂 3）；任意我方目标受到攻击后，计数 ≥1 时史瓦罗反击（同一时刻 1 次），施放追加攻击时计数 −1；
    天赋反击只在没有强化次数时触发（克拉拉受击时只反击 1 次）；默认开启（没有敌人攻击时不会触发）。
  · DMG：战技 s 原来是 120% + 120% 加在一起（按敌人全有反击标记），改成主倍率 #1，标记那段放进 XR mk（默认勾上，按全部敌人有标记，结果和原来一样）；
    强化反击的倍率 +160%（5 魂 172.8%）和相邻目标 50% 进 XR（rx 标记 clu，只在强化反击时算）。
- 桑博：XR E1 原来 v 1.0 = 再算一整次 5 段战技，改成 1 段（0.2，和艾丝妲 E1 一样）；补秘技“进入战斗时敌方每个单体行动延后 25%”（默认关）。
- 虎克：终结技“下一次施放的战技得到强化”→ 状态【强化战技】（终结技获得，施放战技时移除），强化战技用 110909 倍率（主 280% / 相邻 80%，3 魂 308% / 88%），天赋附加伤害 XR 也算强化战技；
  E1“战技强化后伤害 +20%”改成只算强化战技（es）。
- 玲可：战技目标获得状态【求生反应】（2 回合，按目标自己的回合）；行迹提前勘测改成“持有【求生反应】的目标受到攻击后 +2 能量”默认开启；
  E1 改成为当前生命值 ≤50% 的目标治疗时 +20%（hbup low，持续治疗也算），默认开启。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 51
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

# ---------- 克拉拉 1107 ----------
c = C[1107]
u = prm('110703'); assert u[9][1] == 1.6 and u[11][1] == 1.728 and u[9][3] == 0.25 and u[9][4] == 2
assert prm('110704')[9][1] == 1.6 and prm('110704')[11][1] == 1.76
assert 'cnt' not in c
c['cnt'] = {'n': '强化反击', 'at': 0}
tf = find(c['eff'], lambda x: x['y'] == 'fua' and x['n'].startswith('天赋'))
o_tf = tf['n']; tf['ltc'] = 1
tf['n'] = '天赋：克拉拉受到攻击后史瓦罗反击（有【强化反击】次数时改由下面的强化反击代替）'
uf = find(c['eff'], lambda x: x['y'] == 'fua' and x['n'].startswith('终结技'))
o_uf = uf['n']; assert uf.get('off') and uf['ew'] == 'any'
uf.pop('off'); uf['nc'] = 1; uf['pt'] = 1
uf['n'] = '终结技：有【强化反击】次数时，任意我方目标受到攻击后史瓦罗立即反击（同一时刻 1 次）'
i = c['eff'].index(uf)
cs = dict(y='count', t='ult', tg='self', m='set', v=2, lv=[6, 3], n='终结技：史瓦罗的反击得到强化，【强化反击】次数设为 2（6 魂施放终结技时额外 +1 = 3）')
cm = dict(y='count', t='fua', tg='self', v=-1, nc=1, n='终结技：每次强化反击消耗 1 次【强化反击】')
rx1 = dict(y='dbuf', t='ult', tg='self', m='rx', sc='clu', v=1, d=0, bk='clu', n='额外伤害标记：【强化反击】期间反击倍率 +160% 并对相邻目标造成主目标 50% 的伤害')
rx0 = dict(y='dbuf', t='cnt0', tg='self', m='rx', sc='clu', v=0, d=0, bk='clu', n='额外伤害标记：【强化反击】次数用完')
c['eff'][i:i] = [cs]
c['eff'][i + 2:i + 2] = [cm, rx1, rx0]
e6 = next(e for e in c['eid'] if e['r'] == 6)
e6['eff'][0]['n'] = 'E6：我方其他目标遭到攻击后 50% 固定概率反击（概率，需要时启用；“终结技额外 +1 次强化反击”已写在终结技计数里）'
FIX['1107'] = {'drop': [o_tf, o_uf], 'trig': {o_tf: 'hit', o_uf: 'hit'}, 'map': {o_tf: tf['n'], o_uf: uf['n']},
               'add': [tf['n'], cs['n'], uf['n'], cm['n'], rx1['n'], rx0['n']], 'off0': [o_uf], 'sm': {}}

# ---------- 桑博 1108 ----------
c = C[1108]
tq = dict(y='delay', t='start', tg='enemies', v=25, off=1, n='秘技你最闪亮：主动攻击目盲的敌人进入战斗时，敌方每个单体行动延后 25%（用了秘技再启用）')
c['eff'].append(tq)
FIX['1108'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [tq['n']], 'sm': {}}

# ---------- 虎克 1109 ----------
c = C[1109]
i = next(k for k, x in enumerate(c['eff']) if x['n'] == '行迹玩火')
s1 = dict(y='state', t='ult', tg='self', sn='强化战技', v=1, d=0, n='终结技：施放后下一次施放的战技得到强化（状态【强化战技】）')
s0 = dict(y='state', t='skill', tg='self', sn='强化战技', v=0, d=0, n='终结技：施放强化战技后移除【强化战技】')
c['eff'][i:i] = [s1, s0]
e1 = next(e for e in c['eid'] if e['r'] == 1)['eff'][0]
assert e1['sc'] == 's'; e1['sc'] = 'es'; e1['n'] = 'E1：强化战技造成的伤害 +20%'
FIX['1109'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [s1['n'], s0['n']], 'sm': {}}

# ---------- 玲可 1110 ----------
c = C[1110]
k = next(k for k, x in enumerate(c['eff']) if x['y'] == 'hpup')
st = dict(y='state', t='skill', tg='$ally', sn='求生反应', v=1, d=2, n='战技：目标获得【求生反应】，持续 2 回合（按目标自己的回合）')
c['eff'][k:k] = [st]
en = find(c['eff'], lambda x: x['y'] == 'energy' and x['t'] == 'hit')
o_en = en['n']; assert en.get('off')
en.pop('off'); en['ns'] = '求生反应'; en['so'] = 'evt'
en['n'] = '行迹提前勘测：持有【求生反应】的目标受到攻击后，玲可立即恢复 2 点能量'
e1 = next(e for e in c['eid'] if e['r'] == 1)['eff'][0]
assert e1['y'] == 'hbup' and e1['m'] == 'out' and e1['v'] == 20
e1.pop('off'); e1['m'] = 'low'; e1['ovT'] = 50
e1['n'] = 'E1 远行雪杖的清晨：为当前生命值 ≤50% 的目标治疗时治疗量 +20%（持续治疗也算，按治疗前的生命值）'
FIX['1110'] = {'drop': [o_en], 'trig': {o_en: 'hit'}, 'map': {o_en: en['n']}, 'add': [st['n'], en['n']], 'off0': [o_en], 'sm': {}}
put(m, DB)

# ---------- DMG / XR ----------
m, D = grab('DMG')
cl = D['1107']['s']; ps = prm('110702'); assert abs(cl['v'][9] - 2.4) < 1e-9
cl['v'] = [round(p[0], 4) for p in ps]
ps = prm('110909'); assert ps[9][0] == 2.8 and ps[9][4] == 0.8 and ps[11][0] == 3.08
D['1109']['s2'] = {'v': [round(p[0], 4) for p in ps], 'adj': [round(p[4], 4) for p in ps], 'rnd': [], 'tg': 2, 'el': 0, 'stat': 'atk', 'n': '嘿！记得虎克吗（强化）', 'max': 15}
put(m, D)
m, X = grab('XR')
X['1107'] = [
    dict(k='mk', n='战技：对每个带【反击标记】的敌人额外造成一次战技倍率的伤害（按敌人都有标记，没有标记时取消勾选）', on=['s'], st='mult', v=[1.0], cnt='N'),
    dict(k='cu', n='终结技【强化反击】：反击倍率 +160%', on=['f'], who='flag', flag='clu', self=1, st='atk', v=[1.6, 1.728], lk='u'),
    dict(k='ca1', n='终结技【强化反击】：相邻目标受到主目标 50% 的伤害（第 1 个相邻，敌人 ≥2 个）', on=['f'], who='flag', flag='clu', self=1, st='atk', v=[1.6, 1.744], lk='u', minN=2),
    dict(k='ca2', n='终结技【强化反击】：相邻目标受到主目标 50% 的伤害（第 2 个相邻，敌人 ≥3 个）', on=['f'], who='flag', flag='clu', self=1, st='atk', v=[1.6, 1.744], lk='u', minN=3)]
e1 = find(X['1108'], lambda r: r['k'] == 'e1'); assert e1['v'] == [1.0]
e1.update(v=[0.2], n='E1：施放战技时对随机敌方单体额外造成 1 次伤害（1 段 = 战技总倍率的 1/5）')
tf = find(X['1109'], lambda r: r['k'] == 'tf'); assert tf['on'] == ['b', 's', 'u']
tf['on'] = ['b', 's', 's2', 'u']   # 强化战技也算天赋附加伤害
put(m, X)
rep('const S2ST = { "1407": a => !!a.mIn,', 'const S2ST = { "1109": a => (a.sts || []).includes("强化战技"), "1407": a => !!a.mIn,')

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-05（克拉拉、桑博、虎克、玲可，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
