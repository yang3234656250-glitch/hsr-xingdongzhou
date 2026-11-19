"""敌人第 1 批（tv 149）：添加敌方单位、重建当期深渊关卡 STG、按官方数据改敌人模板速度。
用法：python3 -I tools/mon149.py index.html <官方 ExcelOutput 目录（含 TextMapCHS.json）>
官方数据：https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/*.json 和 TextMap/TextMapCHS.json
目录里要有：MonsterConfig MonsterTemplateConfig MonsterSkillConfig EliteGroup HardLevelGroup StageConfig
ChallengeMazeConfig ChallengeStoryMazeConfig ChallengeBossMazeConfig ChallengeGroupConfig ChallengeStoryGroupConfig
ChallengeBossGroupConfig ChallengePeakConfig TextMapCHS

MON 条目字段怎么来的（对照现有 471 个条目验证过：技能说明 2044 / 2047 条逐字一致）：
  n = MonsterName；r = 模板 Rank（BigBoss B / LittleBoss L / Elite E / Minion、MinionLv2 M）
  s = SpeedBase × SpeedModifyRatio + SpeedModifyValue；w = StanceWeakList（物火冰雷风量虚首字，按原顺序）
  d = InitialDelayRatio（≠1 才写）；tn = StanceBase × StanceModifyRatio
  k = SkillList 里有名字、类型不是“天赋”的技能（按 SkillList 顺序）；p = 有名字的天赋；q = 默认出招（k，蓄力技能后面接它点名的招）
  a / h = 攻击 / 生命基础 × 修正 × 怪物自己的 EliteGroup（同 tools/build_monstat.py）；x = 技能倍率（同 build_monstat.ratios）
  技能 sk = {n, t: SkillTag, sp: SPHitBase, d: SkillDesc（#n[i] 代入 ParamList，去标签，超过 110 字截断加“…”）}
STG 波次：s = 敌人速度 × 关卡 EliteGroup.SpeedRatio × HardLevelGroup(关卡组, 等级).SpeedRatio / HardLevelGroup(1, 等级).SpeedRatio
  （页面再乘等级倍率 MON.hg）；对现有「物竞天择」「取象为文」「支配遗忘」逐个重算一致。
"""
import sys, json, re, collections
P, D = sys.argv[1], sys.argv[2]
TV = 149
L = lambda n: json.load(open(f'{D}/{n}.json', encoding='utf-8'))
TM = L('TextMapCHS')
T = lambda h: TM.get(str(h['Hash'])) if isinstance(h, dict) and 'Hash' in h else (h if isinstance(h, str) else None)
V = lambda d, k, dv=1: (d.get(k) or {}).get('Value', dv)
MC = {m['MonsterID']: m for m in L('MonsterConfig')}
MT = {m['MonsterTemplateID']: m for m in L('MonsterTemplateConfig')}
MS = {r['SkillID']: r for r in L('MonsterSkillConfig')}
EG = {r['EliteGroup']: r for r in L('EliteGroup')}
HL = {(r['HardLevelGroup'], r['Level']): r for r in L('HardLevelGroup')}
ST = {s['StageID']: s for s in L('StageConfig')}
raw = open(P, encoding='utf-8', newline='').read()
crlf = '\r\n' in raw[:200000]
s = raw.replace('\r\n', '\n')
assert f'if (s.tv >= {TV - 1}) return;' in s, '页面 tv 不是 %d' % (TV - 1)

def grab(name, op):
    m = re.search(r'\n(\s*)const ' + name + r' ?= ?(' + op + r'.*?);\n', s); assert m, name; return m
mM, mS = grab('MON', r'\{'), grab('STG', r'\[')
MON, STG = json.loads(mM.group(2)), json.loads(mS.group(2))
idx = {m['n']: i for i, m in enumerate(MON['m'])}

WK = {'Physical': '物', 'Fire': '火', 'Ice': '冰', 'Thunder': '雷', 'Wind': '风', 'Quantum': '量', 'Imaginary': '虚'}
RK = {'BigBoss': 'B', 'LittleBoss': 'L', 'Elite': 'E', 'Minion': 'M', 'MinionLv2': 'M'}
def fmt(v, pct):
    if pct: x = round(v * 100, 4); return (str(int(x)) if float(x).is_integer() else str(x)) + '%'
    return str(int(v)) if float(v).is_integer() else str(round(v, 4))
def desc(sk):
    d = T(sk.get('SkillDesc')) or ''
    pl = [p['Value'] for p in sk.get('ParamList') or []]
    d = re.sub(r'#(\d+)\[([^\]]*)\](%?)', lambda m: fmt(pl[int(m.group(1)) - 1] if int(m.group(1)) - 1 < len(pl) else 0, m.group(3) == '%'), d)
    return re.sub(r'<[^>]+>', '', d)
def ratios(sk, tag):   # 和 tools/build_monstat.py 一样
    pl = [p['Value'] for p in sk.get('ParamList') or []]
    d = re.sub(r'<[^>]+>', '', T(sk.get('SkillDesc')) or '') if sk.get('SkillDesc') else ''
    if not pl or sk.get('DamageType') in (None, 'None') or '伤害' not in d: return None
    x = pl[0]
    if tag in ('弹射', '扫射'):
        n = next((v for v in pl[1:] if v >= 2 and float(v).is_integer()), 1)
        return [round(x, 4), round(x, 4), int(n)]
    x2 = pl[1] if tag in ('扩散',) and len(pl) > 1 and pl[1] < x else x
    return [round(x, 4), round(x2, 4), 1]
def rawspd(mc):
    t = MT[mc['MonsterTemplateID']]; return V(t, 'SpeedBase', 0) * V(mc, 'SpeedModifyRatio') + V(mc, 'SpeedModifyValue', 0)
def num(v): return int(v) if float(v).is_integer() else round(v, 4)

def build_mon(mid, name=None, qfix=None, nox=()):
    """按 MonsterID 生成一个 MON 条目，技能追加到 MON.sk 末尾。qfix：[(蓄力技能名, 它点名的招)]；nox：不写倍率的技能名（伤害不是这一招打出来的）"""
    mc = MC[mid]; t = MT[mc['MonsterTemplateID']]; eg = EG.get(mc['EliteGroup'], {})
    o = {'n': name or T(mc['MonsterName']), 'r': RK[t['Rank']], 's': num(rawspd(mc)),
         'w': ''.join(WK[x] for x in mc.get('StanceWeakList', []))}
    if V(t, 'InitialDelayRatio', 1) != 1: o['d'] = V(t, 'InitialDelayRatio', 1)
    act, pas, xr = [], [], {}
    for sid in mc.get('SkillList', []):
        sk = MS.get(sid)
        if not sk or not T(sk.get('SkillName')): continue
        typ, tag = T(sk.get('SkillTypeDesc')), T(sk.get('SkillTag'))
        d = desc(sk)
        e = {'n': T(sk['SkillName']), 't': tag, 'sp': num(V(sk, 'SPHitBase', 0)), 'd': d if len(d) <= 110 else d[:110] + '…'}
        i = len(MON['sk']); MON['sk'].append(e)
        (pas if typ == '天赋' else act).append(i)
        if typ != '天赋' and e['n'] not in nox:
            r = ratios(sk, tag)
            if r: xr[str(i)] = r
    o['k'] = act
    if pas: o['p'] = pas
    q = list(act)
    for a, b in qfix or []:
        ia = next(i for i in q if MON['sk'][i]['n'] == a); ib = next(i for i in q if MON['sk'][i]['n'] == b)
        assert MON['sk'][ia]['t'] == '蓄力' and f'【{b}】' in MON['sk'][ia]['d'], (a, b)
        q.remove(ib); q.insert(q.index(ia) + 1, ib)
    o['q'] = q
    o['tn'] = num(V(t, 'StanceBase', 0) * V(mc, 'StanceModifyRatio'))
    o['a'] = round(V(t, 'AttackBase', 0) * V(mc, 'AttackModifyRatio') * V(eg, 'AttackRatio'), 4)
    o['h'] = round(V(t, 'HPBase', 0) * V(mc, 'HPModifyRatio') * V(eg, 'HPRatio'), 4)
    if xr: o['x'] = xr
    return o

# ---------- A. 新敌人 ----------
NEW = [
    # 末日幻影「领航冥茫」上半首领（关卡 420561～420564 用 501402401～04，速度、韧性、技能和 5014024 相同）
    (5014024, None, [], ()),
    # 异相仲裁 4.7 骑士（一）（ChallengePeak 1101，关卡 30511011）
    (5033010, None, [('拟态发光诱饵', '原初的圣餐')], ()),
    # 贪欢的神颅：主线 5035010（两阶段）；历战余响 5035012（关卡 1052100～1052106，三阶段，加了第三阶段的技能）
    (5035010, None, [], ('神的餐前甜点',)),
    (5035012, '贪欢的神颅（历战余响）', [], ('神的餐前甜点',)),
]
added = []
for mid, nm, qf, nox in NEW:
    o = build_mon(mid, nm, qf, nox)
    assert o['n'] not in idx, ('重名', o['n'])
    idx[o['n']] = len(MON['m']); MON['m'].append(o); added.append((o['n'], mid))
# 同名的几种配置速度、韧性一样（v 不写）
for mid in (5014024, 5033010, 5035010):
    nm = T(MC[mid]['MonsterName'])
    sp = {rawspd(m) for m in MC.values() if T(m['MonsterName']) == nm}
    assert len(sp) == 1, (nm, sp)

# ---------- B. 速度和官方数据不一致的旧条目 ----------
SPDFIX = {'初号机': (144, 300205201), '托帕幻象': (200, 1004015), '奇想林中的蕉研组（完整）': (70, 3004022)}
MONFIX = {}
for n, (old, mid) in SPDFIX.items():
    m = MON['m'][idx[n]]; assert m['s'] == old and 'v' not in m, (n, m['s'])
    sp = {rawspd(x) for x in MC.values() if T(x['MonsterName']) == n}; assert len(sp) == 1, (n, sp)
    new = num(sp.pop()); assert new == num(rawspd(MC[mid])) and new != old
    m['s'] = new; MONFIX[n] = [old, new]

# ---------- STG：每种取最近两期 ----------
MZ = collections.defaultdict(list)
for n in ('ChallengeMazeConfig', 'ChallengeStoryMazeConfig', 'ChallengeBossMazeConfig'):
    for m in L(n): MZ[m['GroupID']].append(m)
GN = {g['GroupID']: T(g['GroupName']) for n in ('ChallengeGroupConfig', 'ChallengeStoryGroupConfig', 'ChallengeBossGroupConfig') for g in L(n)}
def wave(st):
    out = []
    for w in st['MonsterList']:
        wv = []
        for k in sorted(w, key=lambda k: int(k.replace('Monster', ''))):
            mc = MC[w[k]]; nm = T(mc['MonsterName']); lv = st['Level']
            sp = rawspd(mc) * V(EG.get(st.get('EliteGroup'), {}), 'SpeedRatio') * V(HL[(st.get('HardLevelGroup', 1), lv)], 'SpeedRatio') / V(HL[(1, lv)], 'SpeedRatio')
            assert nm in idx, ('MON 里没有', nm, w[k]); wv.append({'n': nm, 'i': idx[nm], 's': round(sp, 2), 'lv': lv})
        out.append(wv)
    return out
def group(gid, label):
    f = []
    for m in sorted(MZ[gid], key=lambda m: m['Floor']):
        f.append({'f': m['Floor'], 'h': [[w for ev in m.get(f'EventIDList{h}', []) for w in wave(ST[ev])] for h in (1, 2)]})
    return {'g': label, 'f': f}
# 现有的「物竞天择」「取象为文」「支配遗忘」按同一方法重算必须完全一致（验证公式）
for gid, lab in ((1036, '混沌回忆「物竞天择」'), (2027, '虚构叙事「取象为文」'), (3021, '末日幻影「支配遗忘」')):
    old = next(g for g in STG if g['g'] == lab); assert group(gid, lab) == old, lab
assert GN[1037] == '漆黑残响' and GN[2028] == '虚事成理' and GN[3022] == '领航冥茫' and GN[3023] == '领航冥茫'
assert group(3022, 'x')['f'] == group(3023, 'x')['f']   # 3023 和 3022 的关卡一样，只放一份
PK = {p['ID']: p for p in L('ChallengePeakConfig')}
knights = {'g': '异相仲裁·4.7 骑士（一～三）', 'f': [{'f': i, 'h': [[w for ev in PK[pid]['EventIDList'] for w in wave(ST[ev])]]} for i, pid in ((1, 1101), (2, 1102), (3, 1103))]}
old47 = next(g for g in STG if g['g'].startswith('异相仲裁·4.7 王棋'))
k47 = wave(ST[PK[1104]['EventIDList'][0]])[0][0]; o47 = old47['f'][0]['h'][0][0][0]
assert (k47['n'], k47['s'], k47['lv']) == (o47['n'], o47['s'], o47['lv']), (k47, o47)   # 王棋按同一方法算速度也一致
labels = [g['g'] for g in STG]
assert labels == ['混沌回忆「来生泅渡」', '混沌回忆「物竞天择」', '虚构叙事「立界开篇」', '虚构叙事「取象为文」', '末日幻影「支配遗忘」', '末日幻影（3022）', '异相仲裁·4.7 王棋（隐藏关卡）归寂'], labels
G = {g['g']: g for g in STG}
STG = [G['混沌回忆「物竞天择」'], group(1037, '混沌回忆「漆黑残响」'), G['虚构叙事「取象为文」'], group(2028, '虚构叙事「虚事成理」'),
       G['末日幻影「支配遗忘」'], group(3022, '末日幻影「领航冥茫」'), knights, old47]

# ---------- 写回 ----------
s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]
mS = grab('STG', r'\[')
s = s[:mS.start(2)] + json.dumps(STG, ensure_ascii=False, separators=(',', ':')) + s[mS.end(2):]

def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:100], s.count(x)); s = s.replace(x, y)
a = re.search(rf'  // tv {TV - 1}：', s); assert a
s = s[:a.start()] + (f'  // tv {TV}：敌人第 1 批：敌人模板速度按官方数据（tools/mon{TV}.py）。只改已经放上去、速度没被手改过的敌人卡\n'
    f'  const MONFIX{TV} = ' + json.dumps(MONFIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ for (const u of s.units || []) {{ const f = u.kind === "enemy" && u.mon ? MONFIX{TV}[u.mon] : null; if (!f || num(u.monS) !== f[0]) continue; '
    f'const old = Math.round(f[0] * monRatio(u.lv) * 1000) / 1000; u.monS = f[1]; const nw = monSpeed(u); if (num(u.spd) === old) u.spd = nw; if (num(u.base) === old) u.base = nw; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); if (!(s.tv >= {TV})) fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')

log = open(sys.argv[3], encoding='utf-8').read().strip() if len(sys.argv) > 3 else None
if log:
    ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
    s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('新敌人', added, '速度', MONFIX, 'STG', [g['g'] for g in STG], 'MON', len(MON['m']), 'sk', len(MON['sk']))
