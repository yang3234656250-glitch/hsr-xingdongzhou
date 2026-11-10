"""tv 56：每日校对 2026-11-10（寒鸦 1215、椒丘 1218、云璃 1221、貊泽 1223），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix56.py index.html（需要 /tmp/sr/character_skills.json、characters.json）
- 寒鸦：战技【承负】做成计数 + 状态（记在寒鸦身上 = 场上有承负目标）：寒鸦施放战技后获得【承负】并清零计数；
  我方目标施放普攻 / 战技 / 终结技攻击后（追加攻击不算）计数 +1，第 2、4 次时恢复 1 个战技点、寒鸦 +2 能量（行迹还阳）、
  触发者攻击力 +10% 1 回合（行迹录事）；第 4 次后【承负】解除（原来完全没做，战技点和能量都少算）。秘技开局【承负】（默认关）。
  终结技的速度 / 攻击力增益改成按目标自己的回合计（cnt own，同艾丝妲终结技），并补 E4“终结技持续时间 +1 回合”（原来漏了）。
- 云璃：终结技“消耗 120 点能量”、能量上限 240：开大所需 120、最多存 240、开局 50% × 240 = 120（原来按 240 开大）；
  伤害显示：终结技倍率按【勘破•灭】220% + 相邻 110% + 6 × 72%（原来是 2 × 220%），E1 / E6 / 终结技爆伤 / E2 / 行迹真刚改成作用到勘破。
- 椒丘：E6【烬煨】上限 9 层，补上多出 4 层的受到伤害 +22%（按 5 魂数值 5.5% × 4）。
- 貊泽：补 E6“天赋的追加攻击倍率 +25%”（XR）。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 56
assert f'if (s.tv >= {TV - 1}) return;' in s
SK = json.load(open('/tmp/sr/character_skills.json'))
CH = json.load(open('/tmp/sr/characters.json'))
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

# ---------- 寒鸦 1215 ----------
c = C[1215]; CF = '承负'
p2 = prm('121502'); assert p2[9] == [2.4, 2]          # 2 次后恢复 1 个战技点
assert '施放2次普攻、战技、终结技后' in SK['121502']['desc'] and '触发#2[i]次战技点恢复效果后自动解除' in SK['121502']['desc']
p3 = prm('121503'); assert p3[9] == [0.6, 2, 0.2] and p3[11] == [0.648, 2, 0.21]
old = c['eff']; sp_ = find(old, lambda x: x['y'] == 'spd'); at_ = find(old, lambda x: x['y'] == 'dbuf' and x['m'] == 'atkP')
o_sp, o_at = sp_['n'], at_['n']
sp_.update(bk='hyu', cnt='own', n='终结技：指定我方单体速度 + 寒鸦速度的 20%（5 魂 21%），持续 2 回合（按目标自己的回合）')
at_.update(cnt='own', n='终结技：指定我方单体攻击力 +60%（5 魂 64.8%），持续 2 回合（按目标自己的回合）')
ATK = ['basic', 'ebasic', 'skill', 'fskill', 'ult']
new = [
    dict(y='count', t='ally', aw='self', aa=['skill'], tg='self', m='set', v=0, n='战技：施放后使目标陷入【承负】，重新计数（承负记在寒鸦身上，只对最新的目标生效）'),
    dict(y='state', t='ally', aw='self', aa=['skill'], tg='self', sn=CF, v=1, d=0, n='战技：敌方目标陷入【承负】（触发 2 次战技点恢复后解除）'),
    dict(y='count', t='atk', aw='all', aa=ATK, ns=CF, tg='self', v=1, n='战技：我方目标对【承负】目标施放普攻 / 战技 / 终结技攻击后计 1 次（追加攻击不算；按都打到承负目标算）'),
    dict(y='sp', t='atk', aw='all', aa=ATK, ns=CF, nc=2, ltc=3, tg='self', v=1, n='战技：【承负】每计满 2 次，为我方恢复 1 个战技点（第 1 次）'),
    dict(y='energy', t='atk', aw='all', aa=ATK, ns=CF, nc=2, ltc=3, tg='self', v=2, m='er', n='行迹还阳：【承负】战技点恢复触发时寒鸦恢复 2 点能量（第 1 次）'),
    dict(y='dbuf', t='atk', aw='all', aa=ATK, ns=CF, nc=2, ltc=3, tg='evt', m='atkP', v=10, d=1, cnt='own', bk='lushi', n='行迹录事：触发【承负】战技点恢复的我方单位攻击力 +10%，持续 1 回合（第 1 次）'),
    dict(y='sp', t='atk', aw='all', aa=ATK, ns=CF, nc=4, tg='self', v=1, n='战技：【承负】每计满 2 次，为我方恢复 1 个战技点（第 2 次）'),
    dict(y='energy', t='atk', aw='all', aa=ATK, ns=CF, nc=4, tg='self', v=2, m='er', n='行迹还阳：【承负】战技点恢复触发时寒鸦恢复 2 点能量（第 2 次）'),
    dict(y='dbuf', t='atk', aw='all', aa=ATK, ns=CF, nc=4, tg='evt', m='atkP', v=10, d=1, cnt='own', bk='lushi', n='行迹录事：触发【承负】战技点恢复的我方单位攻击力 +10%，持续 1 回合（第 2 次）'),
    dict(y='state', t='atk', aw='all', aa=ATK, ns=CF, nc=4, tg='self', sn=CF, v=0, n='战技：【承负】触发 2 次战技点恢复后自动解除'),
    dict(y='count', t='atk', aw='all', aa=ATK, nc=4, tg='self', m='set', v=0, n='战技：【承负】解除后计数清零'),
]
TECH = [
    dict(y='count', t='start', tg='self', m='set', v=0, off=1, n='秘技判冥：进入战斗后对敌方随机单体附上【承负】（计数清零；用了秘技再启用，和下一条一起开）'),
    dict(y='state', t='start', tg='self', sn=CF, v=1, d=0, off=1, n='秘技判冥：进入战斗后对敌方随机单体附上【承负】（用了秘技再启用）'),
]
assert '进入战斗后对敌方随机单体附上等同于战技效果的【承负】' in SK['121507']['desc']
c['eff'] = [sp_, at_] + new + [x for x in old if x is not sp_ and x is not at_] + TECH
c['cnt'] = {'n': CF, 'at': 0, 'max': 4}
c['notes'] = [n for n in c.get('notes', []) if '还阳' not in n] + ['行迹幽府（持有【承负】的目标被消灭时额外恢复 1 个战技点）没做；【承负】按我方所有普攻 / 战技 / 终结技都打到承负目标算']
e4 = [e for e in c['eid'] if e['r'] == 4]
assert not e4 and '终结技的持续时间额外增加1回合' in json.dumps(json.load(open('/tmp/sr/character_ranks.json'))['121504'], ensure_ascii=False)
c['eid'].append({'r': 4, 'eff': [
    dict(sp_, d=3, n='E4 四谛：终结技速度增益持续时间 +1 回合（3 回合，按目标自己的回合）'),
    dict(at_, d=3, n='E4 四谛：终结技攻击力增益持续时间 +1 回合（3 回合，按目标自己的回合）')], 'notes': []})
c['eid'].sort(key=lambda e: e['r'])
FIX['1215'] = {'drop': [o_sp, o_at], 'trig': {o_sp: 'ult', o_at: 'ult'}, 'map': {o_sp: sp_['n'], o_at: at_['n']},
               'add': [sp_['n'], at_['n']] + [x['n'] for x in new] + [x['n'] for x in TECH], 'sm': {},
               'set': {'cntName': CF, 'cntAt': 0, 'cntMax': 4}}

# ---------- 云璃 1221 ----------
c = C[1221]
pu = prm('122103'); assert pu[9] == [2.2, 1, 0, 6, 0, 1.1, 0.72, 120] and CH['1221']['max_sp'] == 240 and c['sp'] == 240
c['x'].update(maxE=120, capE=240, startE=100)
cdu = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'cd'); o_cd = cdu['n']
cdu.update(sc='u', n='终结技：下一次反击（【勘破】）暴击伤害 +100%（勘破的伤害显示在开大上）')
zg = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['bk'] == 'zg')
ZG2 = dict(zg, t='ult', n='行迹真刚：终结技之后的【勘破•斩 / 灭】也是反击，施放时攻击力 +30%（勘破的伤害显示在开大上）')
c['eff'].insert(c['eff'].index(zg) + 1, ZG2)
for e in c['eid']:
    for x in e['eff']:
        if e['r'] in (1, 6): assert x['sc'] == 'f'; x['sc'] = 'u'
    if e['r'] == 1: e['eff'][0]['n'] = 'E1：勘破•斩 / 勘破•灭伤害 +20%（勘破的伤害显示在开大上）'
    if e['r'] == 2:
        x = e['eff'][0]; assert x['m'] == 'defIg' and x['sc'] == 'f'
        x['n'] = 'E2：反击无视敌方 20% 防御力（天赋反击）'
        e['eff'].append(dict(x, sc='u', bk='e2u', n='E2：反击无视敌方 20% 防御力（终结技的勘破）'))
c['notes'] = (c.get('notes') or []) + ['终结技【格挡】期间被攻击才是【勘破•灭】，没被攻击时回合结束放【勘破•斩】：模拟里勘破不另算一次反击（不另回能、不触发队友“追加攻击后”），伤害按【勘破•灭】显示在开大上']
FIX['1221'] = {'drop': [o_cd], 'trig': {o_cd: 'ult'}, 'map': {o_cd: cdu['n']}, 'add': [cdu['n'], ZG2['n']], 'sm': {},
               'set': {'maxE': 120, 'capE': 240, 'startE': 100}}

# ---------- 椒丘 1218 ----------
c = C[1218]
pt = prm('121804'); assert pt[9][1:3] == [0.15, 0.05] and r4(pt[11][2]) == 0.055
e6 = find(c['eid'], lambda e: e['r'] == 6)
e6['eff'].append(dict(y='dbuf', t='atk', aw='self', tg='enemies', m='vuln', v=r4(4 * pt[11][2] * 100), d=2, bk='jw6',
                      n='E6：【烬煨】上限 9 层，多出的 4 层受到的伤害再 +22%（按叠满 9 层、5 魂每层 5.5% 算）'))
FIX['1218'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}}
put(m, DB)

# ---------- DMG / XR ----------
m, D = grab('DMG')
d = D['1221']['u']; assert d['v'][9] == 4.4
d.update(v=[r4(p[0]) for p in pu], adj=[r4(p[5]) for p in pu], rnd=[r4(p[6] * p[3]) for p in pu], tg=2, n='剑为地纪，刃惊天宗（按【勘破•灭】）')
assert d['v'][9] == 2.2 and d['adj'][9] == 1.1 and d['rnd'][9] == 4.32 and d['v'][11] == 2.376
put(m, D)
m, X = grab('XR')
assert '1221' not in X
X['1221'] = [dict(k='e1', n='E1 沉锋离垢：【勘破•灭】额外伤害次数 +3（3 × 72%，3 魂 77.76%）', on=['u'], st='atk', v=[r4(3 * pu[9][6]), r4(3 * pu[11][6])], lk='u', e=1)]
assert not any(r['k'] == 'e6' for r in X['1223'])
assert '天赋的追加攻击的伤害倍率提高25%' in json.dumps(json.load(open('/tmp/sr/character_ranks.json'))['122306'], ensure_ascii=False)
X['1223'].append(dict(k='e6', n='E6 丹心：天赋的追加攻击伤害倍率 +25%', on=['f'], st='atk', v=[0.25], e=6))
put(m, X)

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-10（寒鸦、云璃、椒丘，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
