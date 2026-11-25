"""敌人第 6 批（2026-11-24 晚，每日敌人任务，tv 189）。
用法：python3 -I tools/enemy6.py index.html <官方 ExcelOutput 目录（含 TextMapCHS.json）> <更新日志 li 文件>
官方数据：https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/*.json 和 TextMap/TextMapCHS.json
（目录里要有 MonsterConfig MonsterTemplateConfig MonsterSkillConfig EliteGroup HardLevelGroup StageConfig
 ChallengePeakConfig ChallengePeakGroupConfig TextMapCHS）
（当时推不上仓库，2026-11-25 从项目文档「敌人任务-2026-11-24-敌人第6批-未推送补丁.md」原样合回；index.html 取自 claude.ai 页面第 325 版）

A. STG 新加一组 异相仲裁「落叶归根」（ChallengePeakGroup 10：骑士 1001～1003 + 王棋 1004，关卡 30510011～13 / 30510021）。
   STG 每种保留最近两期：异相仲裁原来只有 Group 11（4.7 骑士 1101～1103、隐藏关卡 1104 王棋归寂）。
   每个敌人按 MonsterID 对到 MON 条目（名字相同或带后缀、技能名集合相同，再按 速度 / 弱点 / 韧性 / 生命 选最像的），
   速度 = 资料速度 × 关卡 EliteGroup.SpeedRatio × HardLevelGroup(关卡组, 等级) / HardLevelGroup(1, 等级)（同 mon149.py），
   关卡配置的弱点 / 韧性和模板不同时才写 w / tn（同 enemy3.py）。先用同一函数重算现有「4.7 骑士」那组，必须和 STG 里的一样。
   这组用到的 12 种敌人 MON 里都有，没有新敌人。
B. 模板默认值按“同名、技能相同、关卡里用得最多的配置”（enemy5.py 的规则，这次扩到速度 / 开局延迟 / 生命 / 韧性）：
   繁花之杪 速度 120→100、生命 325.5→186（官方 2022090，关卡里唯一用到的配置）；肃风之杪 速度 120→100（2022070，同上）；
   序列扑满 速度 120→83、生命 260.4→334.8（8002050 / 8002058 / 8002091，关卡里用到的 3 个配置都是 83 / 334.8）；
   金血忆灵•翼蛇形 速度 144→120、生命 4650→1488（4063010，历战余响 / 深渊 / 差分宇宙 / 主线都是它；另一个 406301001 也是 120）；
   惊梦剧团的十七分熟（错误） 速度 120→100、生命 2511→2092.5（差分宇宙 300301201 用 9 次，3003012 用 2 次）；
   扑满 弱点 冰量虚→物火冰、开局延迟 1→0.5（只在活动 FightFest 里，800205301 用 14 次、另两个各 7 次；速度 83 不变）；
   残破容器 韧性 180→360（MON 的技能是 4032021 / 4032025 那套，这两个模板的所有配置韧性都是 360；180 是另一套技能 4032020 的）。
   核对后不改：反造物主，流溢之恨 韧性 600（历战余响 4035010、深渊 403501001 都是 600，720 只在主线 4035011）；
   堕神之血•亚婆离 180、始作画者，无量塔绘世 120、炽燃徘徊者 100（深渊 / 历战余响用的配置就是这个速度，别的速度只在主线或活动）。
   迁移 fixTpl189：已经放上去、不是“按关卡放”的敌人卡，速度 / 开局还是旧默认值的改成新的（同 fixTpl149）。生命 / 弱点 / 韧性是模拟时从模板读的，
   放好的卡自动跟着变（只影响伤害显示、击破和“我方伤害扣敌人生命值”）。
"""
import sys, json, re, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import Mon, page, grab, num, WK

P, D, LOGF = sys.argv[1], sys.argv[2], sys.argv[3]
TV = 189
M = Mon(D); V = M.V
s, crlf = page(P)
assert f'if (s.tv >= {TV - 1}) return;' in s, '页面 tv 不是 188'
mM = grab(s, 'MON', r'\{'); MON = json.loads(mM.group(2))
mS = grab(s, 'STG', r'\['); STG = json.loads(mS.group(2))
idx = {m['n']: i for i, m in enumerate(MON['m'])}
untag = lambda x: re.sub(r'<[^>]+>', '', x or '')
ST = {st['StageID']: st for st in M.L('StageConfig')}
HL = {(h['HardLevelGroup'], h['Level']): h for h in M.L('HardLevelGroup')}
used = collections.Counter()
for st in ST.values():
    for w in st['MonsterList']:
        for k in w: used[w[k]] += 1
W = lambda mid: ''.join(WK[x] for x in M.MC[mid].get('StanceWeakList', []))
SKN = lambda mid: {y for y in (untag(M.T(M.MS[x]['SkillName'])) for x in M.MC[mid].get('SkillList', []) if x in M.MS and M.T(M.MS[x].get('SkillName'))) if y.strip()}
MSK = lambda m: {x for x in (MON['sk'][i]['n'] for i in m.get('k', []) + m.get('p', [])) if x.strip()}
def feat(mid):
    t = M.MT[M.MC[mid]['MonsterTemplateID']]; st = M.stats(mid)
    return {'s': num(M.rawspd(M.MC[mid])), 'w': W(mid), 'tn': st['tn'], 'd': V(t, 'InitialDelayRatio', 1), 'h': st['h']}
byn = collections.defaultdict(list)
for mid, mc in M.MC.items():
    if mc['MonsterTemplateID'] in M.MT: byn[M.name(mid)].append(mid)

# ---------- A. STG 异相仲裁「落叶归根」 ----------
def pick(mid):
    n = M.name(mid); f = feat(mid)
    c = [i for i, m in enumerate(MON['m']) if m['n'] == n and MSK(m) == SKN(mid)] or \
        [i for i, m in enumerate(MON['m']) if m['n'].startswith(n + '（') and m['n'] not in byn and MSK(m) == SKN(mid)]   # 官方名字优先；页面加的后缀（官方没有这个名字）才看
    assert c, ('MON 里没有', n, mid)
    sc = lambda i: (MON['m'][i]['s'] == f['s']) + (MON['m'][i].get('w', '') == f['w']) + (MON['m'][i].get('tn') == f['tn']) + (MON['m'][i].get('h') == f['h'])
    best = max(c, key=sc); assert [sc(i) for i in c].count(sc(best)) == 1, ('对不准', n, c)
    return best
def wave(st):
    out = []
    for w in st['MonsterList']:
        wv = []
        for k in sorted(w, key=lambda k: int(k.replace('Monster', ''))):
            mid = w[k]; mc = M.MC[mid]; lv = st['Level']; i = pick(mid); m = MON['m'][i]
            sp = M.rawspd(mc) * V(M.EG.get(st.get('EliteGroup'), {}), 'SpeedRatio') * V(HL[(st.get('HardLevelGroup', 1), lv)], 'SpeedRatio') / V(HL[(1, lv)], 'SpeedRatio')
            e = {'n': m['n'], 'i': i, 's': round(sp, 2), 'lv': lv}
            if W(mid) != m.get('w', ''): e['w'] = W(mid)
            if M.stats(mid)['tn'] != m.get('tn'): e['tn'] = M.stats(mid)['tn']
            wv.append(e)
        out.append(wv)
    return out
PK = {p['ID']: p for p in M.L('ChallengePeakConfig')}
PG = {g['ID']: g for g in M.L('ChallengePeakGroupConfig')}
assert PG[10]['PreLevelIDList'] == [1001, 1002, 1003] and PG[10]['BossLevelID'] == 1004 and M.T(PG[10]['Title']) == '落叶归根'
assert PG[11]['PreLevelIDList'] == [1101, 1102, 1103] and PG[11]['BossLevelID'] == 1104
peak = lambda pids: [{'f': i + 1, 'h': [[w for ev in PK[pid]['EventIDList'] for w in wave(ST[ev])]]} for i, pid in enumerate(pids)]
labels = [g['g'] for g in STG]
assert labels == ['混沌回忆「物竞天择」', '混沌回忆「漆黑残响」', '虚构叙事「取象为文」', '虚构叙事「虚事成理」', '末日幻影「支配遗忘」', '末日幻影「领航冥茫」',
                  '异相仲裁·4.7 骑士（一～三）', '异相仲裁·4.7 王棋（隐藏关卡）归寂'], labels
kn = STG[6]
assert peak([1101, 1102, 1103]) == kn['f'], '重算 4.7 骑士对不上（验证公式）'
LBL = '异相仲裁「落叶归根」（1～3 骑士，4 王棋）'
grp = {'g': LBL, 'f': peak([1001, 1002, 1003, 1004])}
STG.insert(6, grp)

# ---------- B. 模板默认值 ----------
def top(name):
    m = MON['m'][idx[name]]; sk = MSK(m)
    ids = [x for x in byn[name] if used[x] and SKN(x) == sk]
    cnt = collections.Counter()
    for x in ids: cnt[json.dumps(feat(x), sort_keys=True)] += used[x]
    return json.loads(cnt.most_common(1)[0][0]), ids
FIX = {   # 名字: {字段: [旧, 新]}，新值必须等于 top() 算出来的
    '繁花之杪': {'s': [120, 100], 'h': [325.5, 186]},
    '肃风之杪': {'s': [120, 100]},
    '序列扑满': {'s': [120, 83], 'h': [260.4001, 334.8]},
    '金血忆灵•翼蛇形': {'s': [144, 120], 'h': [4650.0, 1488]},
    '惊梦剧团的十七分熟（错误）': {'s': [120, 100], 'h': [2511, 2092.4992]},
    '扑满': {'w': ['冰量虚', '物火冰'], 'd': [1, 0.5]},
}
for n, ch in FIX.items():
    m = MON['m'][idx[n]]; t, ids = top(n)
    for k, (a, b) in ch.items():
        assert m.get(k, 1 if k == 'd' else None) == a, (n, k, m.get(k))
        assert t[k] == b, (n, k, t[k], b)
        if k == 'd' and b == 1: m.pop('d', None)
        else: m[k] = b
    assert all(m.get(k, 1 if k == 'd' else None) == t[k] for k in ('s', 'w', 'tn', 'd')), (n, t)
    if 'v' in m: assert m['s'] in m['v'], (n, m['v'])
# 残破容器：MON 的技能 = 4032021 / 4032025 那套，这两个模板所有配置韧性 360
m = MON['m'][idx['残破容器']]; sk = MSK(m)
same = [x for x in byn['残破容器'] if SKN(x) == sk]
assert same and {M.MC[x]['MonsterTemplateID'] for x in same} == {4032021, 4032025} and {M.stats(x)['tn'] for x in same} == {360}, same
assert {M.stats(x)['tn'] for x in byn['残破容器'] if SKN(x) != sk} == {180}
assert m['tn'] == 180; m['tn'] = 360; FIX['残破容器'] = {'tn': [180, 360]}
# 核对不改的
assert top('反造物主，流溢之恨')[0]['tn'] == 720 and MON['m'][idx['反造物主，流溢之恨']]['tn'] == 600
assert {M.stats(x)['tn'] for x in (4035010, 403501001)} == {600} and M.stats(4035011)['tn'] == 720
for n, sp in (('堕神之血•亚婆离', 180), ('始作画者，无量塔绘世', 120), ('炽燃徘徊者', 100)):
    assert MON['m'][idx[n]]['s'] == sp
# STG 里这些模板（按关卡放的卡带自己的速度；弱点 / 韧性和模板一样就不写）：现有 w / tn 覆盖重新检查
chg = {idx[n] for n in FIX}
def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('i'), int) and o['i'] in chg:
            mm = MON['m'][o['i']]
            for k in ('w', 'tn'):
                if k in o and o[k] == mm.get(k): del o[k]
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(STG)

s = s[:mS.start(2)] + json.dumps(STG, ensure_ascii=False, separators=(',', ':')) + s[mS.end(2):]
mM = grab(s, 'MON', r'\{')
s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]

# ---------- 迁移 ----------
MF = {n: {k: v for k, v in ch.items() if k in ('s', 'd')} for n, ch in FIX.items()}
MF = {n: v for n, v in MF.items() if v}
def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:120], s.count(x)); s = s.replace(x, y)
a = re.search(rf'  // tv {TV - 1}：', s); assert a
s = s[:a.start()] + (f'  // tv {TV}：敌人第 6 批：敌人模板默认速度 / 开局延迟按关卡里用得最多的官方配置（tools/enemy{TV - 183}.py）。只改已经放上去、不是按关卡放的、还是旧默认值的敌人卡\n'
    f'  const MONFIX{TV} = ' + json.dumps(MF, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ for (const u of s.units || []) {{ const f = u.kind === "enemy" && u.mon && !u.stg ? MONFIX{TV}[u.mon] : null; if (!f) continue; '
    f'if (f.s && num(u.monS) === f.s[0]) {{ const old = Math.round(f.s[0] * monRatio(u.lv) * 1000) / 1000; u.monS = f.s[1]; const nw = monSpeed(u); if (num(u.spd) === old) u.spd = nw; if (num(u.base) === old) u.base = nw; }} '
    f'if (f.d && num(u.opening, 0) === Math.round((1 - f.d[0]) * 100)) u.opening = Math.round((1 - f.d[1]) * 100); }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); if (!(s.tv >= {TV})) fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')

log = open(LOGF, encoding='utf-8').read().strip()
ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('STG', [g['g'] for g in STG])
for f in grp['f']: print(' 第', f['f'], '层', [[(e['n'], e['s'], e['lv'], e.get('w'), e.get('tn')) for e in w] for w in f['h'][0]])
print('FIX', FIX); print('MONFIX', MF)
