"""敌人第 3 批（2026-11-21 晚，每日敌人任务，没改 tv：新字段都是“没有就是旧行为”）。
用法：python3 -I tools/enemy3.py index.html <官方 ExcelOutput 目录（含 TextMapCHS.json）> [更新日志 li 文件]
官方数据：https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/*.json 和 TextMap/TextMapCHS.json
（目录里要有 MonsterConfig MonsterTemplateConfig MonsterSkillConfig EliteGroup HardLevelGroup StageConfig
 ChallengeMazeConfig ChallengeStoryMazeConfig ChallengeBossMazeConfig ChallengePeakConfig TextMapCHS）
（2026-11-22 从项目文档「敌人任务-2026-11-21-敌人第3批-未推送补丁.md」抄回仓库；页面改动已经从 claude.ai 页面原样合回，不用再跑。
 原脚本按 tv 151 的页面写的，开头的 tv 断言在 tv 152 之后的页面上会失败。）

A. 新敌人：
  - 速度 0、自己不行动的本体（官方 SpeedBase 没有 = 0）：昔在、今在、永在的剧目（3004010）、昔在、今在、永在的剧目（完整）（3004011）、
    末日兽（8015010）、毁灭的容器，卡厄斯兰那（4034020）、朱明三不（300401002）。MON 条目 s = 0、q = []（本体不出招），
    标签是「天赋」的技能放进 p。页面：applyMon 遇到 s = 0 写 u.noAct = true（换别的模板时删掉），模拟选行动者时跳过 noAct（不上行动轴）。
    靠别的东西行动的部分（剧目的【宣诫】、末日兽的反物质引擎 / 两只手）不在这里：【宣诫】在官方数据里不是单独的怪物，速度查不到。
  - 天谴先锋（虚构叙事）（401301201，模板 4013012）：虚构叙事「取象为文」「虚事成理」用的版本，没有【快从坟墓中苏生】（召唤），生命值不同；
    STG 里这两期的天谴先锋改指向它（名字仍显示“天谴先锋”）。
B. 怪物效果：
  - MON.sk 新字段 ag（1 = 施放后再行动 1 次）：罪血眈视“施放该技能后再行动1次”。模拟里 actor.again = true（和 4.7 连续行动同一套：马上再行动，标“连续行动”）。
  - MON.sk 新字段 pl（"o" = 施放后除自身外的敌方全体立即行动 = 行动提前 100%）：起床铃声“使除自身外的敌方全体立即行动”、
    鼓劲“使敌方除【银鬃尉官（错误）】外的目标……立即行动”、棋快一着（4 种）“使敌方全体立即行动”（浮烟自己算不算“全体”没写清，先只拉其他敌人，等用户确认）。
  - 弱点 / 韧性按官方关卡实际用的配置：MON 里有 16 个敌人的弱点或韧性取自没有任何关卡用到的配置（比如天谴先锋 冰雷风，关卡里全是 冰雷量），
    改成关卡里用到的（多个时取用得最多的）；蚀蛰虫整条换成关卡用的 8022030（速度 118、韧性 90、只有角击 / 蚀亡语）。
    STG 每个敌人和关卡实际 MonsterID 比，弱点 / 韧性和 MON 不一样的写进波次条目 w / tn；“换上这一波敌人”时写到敌人卡 u.stw（弱点）/ u.tough（韧性）。
    monOf：有 u.stw 时用它代替模板弱点。
"""
import sys, json, re, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import Mon, page, grab, num, WK

P, D = sys.argv[1], sys.argv[2]
M = Mon(D); L = M.L; V = M.V
s, crlf = page(P)
assert 'if (s.tv >= 151) return;' in s and 'if (s.tv >= 152) return;' not in s, '页面 tv 不是 151'
assert 'u.noAct' not in s and 'sk.ag' not in s and 'u.stw' not in s, '已经跑过'
mM = grab(s, 'MON', r'\{'); MON = json.loads(mM.group(2))
mS = grab(s, 'STG', r'\['); STG = json.loads(mS.group(2))
idx = {m['n']: i for i, m in enumerate(MON['m'])}
nm0 = len(MON['m']); sk0 = len(MON['sk'])
untag = lambda x: re.sub(r'<[^>]+>', '', x or '')

used = collections.Counter()
for st in L('StageConfig'):
    for w in st['MonsterList']:
        for k in w: used[w[k]] += 1
W = lambda mid: ''.join(WK[x] for x in M.MC[mid].get('StanceWeakList', []))
TN = lambda mid: M.stats(mid)['tn']
SKN = lambda mid: sorted(y for y in (untag(M.T(M.MS[x]['SkillName'])) for x in M.MC[mid].get('SkillList', []) if x in M.MS and M.T(M.MS[x].get('SkillName'))) if y.strip())
byn = collections.defaultdict(list)
for mid, mc in M.MC.items():
    if mc['MonsterTemplateID'] in M.MT: byn[M.name(mid)].append(mid)

# ---------- A1. 速度 0 的本体 ----------
ZERO = [(3004010, [3004012, 300401001]), (3004011, []), (8015010, [8015011]), (4034020, []), (300401002, [])]
added = []
for mid, same in ZERO:
    o = M.build(MON, mid)
    assert o['n'] not in idx, ('已有', o['n'])
    assert o['s'] == 0 and V(M.MT[M.MC[mid]['MonsterTemplateID']], 'SpeedBase', 0) == 0, mid
    assert used[mid], ('关卡没用到', mid)
    for x in same: assert M.name(x) == o['n'] and num(M.rawspd(M.MC[x])) == 0 and SKN(x) == SKN(mid), x
    ks = o['k'] + o.get('p', [])
    o['k'] = [i for i in ks if MON['sk'][i]['t'] != '天赋']
    p = [i for i in ks if MON['sk'][i]['t'] == '天赋']
    if p: o['p'] = p
    else: o.pop('p', None)
    o['q'] = []                  # 本体不出招
    o.pop('x', None)             # 本体不出招，不写倍率（为同一律献舞由【宣诫】施放）
    idx[o['n']] = len(MON['m']); MON['m'].append(o); added.append((o['n'], mid, o['r'], o.get('w', ''), o['h']))
# 同名的“昔在、今在、永在的剧目”3 个配置：3004010（混沌回忆 1015～1026）作为条目，其他两个技能一样、生命值不同（关卡里另按难度算）

# ---------- A2. 天谴先锋（虚构叙事） ----------
o = M.build(MON, 401301201, '天谴先锋（虚构叙事）')
assert o['n'] not in idx
assert [MON['sk'][i]['n'] for i in o['q']] == ['从天帷斩向黎明', '从黎明杀往天帷', '像威猛暴怒的雄狮', '在滔滔血海中沉溺'], o['q']
assert '快从坟墓中苏生' not in SKN(401301201) and '快从坟墓中苏生' in SKN(4013010)
idx[o['n']] = len(MON['m']); MON['m'].append(o); added.append((o['n'], 401301201, o['r'], o['w'], o['h']))
TQ = o

# ---------- B1. 再行动 1 次 / 其他敌人立即行动 ----------
AG = [i for i, k in enumerate(MON['sk']) if '施放该技能后再行动1次' in k['d']]
assert sorted(MON['sk'][i]['n'] for i in AG) == ['罪血眈视'] * len(AG) and len(AG) >= 2, AG
for i in AG: MON['sk'][i]['ag'] = 1
PL = {}
for i, k in enumerate(MON['sk']):
    d = k['d']
    if re.fullmatch(r'使除自身外的敌方全体立即行动。', d) or re.match(r'使敌方除【[^】]+】外的目标[^。]*立即行动', d) or re.match(r'使敌方全体立即行动', d):
        PL[i] = k['n']
assert sorted(set(PL.values())) == ['棋快一着', '棋快一着•变着', '棋快一着•杀着', '棋快一着•紧着', '起床铃声', '鼓劲'], PL
for i in PL: MON['sk'][i]['pl'] = 'o'
# 鼓劲：除【银鬃尉官（错误）】外 = 除自身外（只有银鬃尉官（错误）有这招）
for i, n in PL.items():
    if n == '鼓劲': assert [m['n'] for m in MON['m'] if i in m.get('k', [])] == ['银鬃尉官（错误）']

# ---------- B2. 弱点 / 韧性取自没有关卡用到的配置的 ----------
fixW, fixT = {}, {}
for m in MON['m'][:nm0]:
    ids = [x for x in byn.get(m['n'], []) if used[x]]
    if not ids: continue
    cw, ct = collections.Counter(), collections.Counter()
    for x in ids: cw[W(x)] += used[x]; ct[TN(x)] += used[x]
    if m.get('w', '') not in cw: fixW[m['n']] = (m.get('w'), cw.most_common(1)[0][0], dict(cw))
    t0 = m.get('tn') or 0
    if t0 not in ct: fixT[m['n']] = (m.get('tn'), ct.most_common(1)[0][0], dict(ct))
EXW = {'天谴先锋', '丰饶灵兽•长右', '自动机兵•甲虫', '无想面具', '毁灭扑满', '银枝', '奇想林中的蕉研组', '忆域迷因「狂怒褪去之壳」', '蕉研组的谐乐蕉师', '蚀蛰虫'}
EXT = {'奇想林中的蕉研组', '幼蛰虫', '乐变化天人•终', '杰帕德（幻象）', '蕉研组的助蕉', '蕉研组的筑梦蕉师', '蕉研组的财富蕉师', '蕉研组的谐乐蕉师', '蚀蛰虫'}
assert set(fixW) == EXW, set(fixW) ^ EXW
assert set(fixT) == EXT, set(fixT) ^ EXT
# 蚀蛰虫：MON 条目是没有关卡用到的 8022031（速度 110、韧性 180、多两个天赋），整条换成关卡用的 8022030
sz = MON['m'][idx['蚀蛰虫']]
assert sz['s'] == 110 and sz.get('v') == [110, 118] and [MON['sk'][i]['n'] for i in sz['k']] == ['角击'] and [MON['sk'][i]['n'] for i in sz['p']] == ['蚀亡语', '滋养', '扰乱']
tmp = {'sk': list(MON['sk'])}; ref = M.build(tmp, 8022030)
assert [tmp['sk'][i]['n'] for i in ref['k']] == ['角击'] and [tmp['sk'][i]['n'] for i in ref['p']] == ['蚀亡语']
assert tmp['sk'][ref['k'][0]] == MON['sk'][sz['k'][0]] and tmp['sk'][ref['p'][0]] == MON['sk'][sz['p'][0]]
assert sz['x'][str(sz['k'][0])] == [1.6, 1.6, 1] and ref['x'][str(ref['k'][0])] == [3.2, 3.2, 1]   # 角击倍率：8022031 是 1.6，关卡用的 8022030 是 3.2
sold = {k: sz.get(k) for k in ('s', 'w', 'tn', 'a', 'h', 'p')}
sz.update(s=ref['s'], w=ref['w'], tn=ref['tn'], a=ref['a'], h=ref['h'], p=[sz['p'][0]])
sz['x'] = {str(sz['k'][0]): ref['x'][str(ref['k'][0])]}   # 只留主动技能的倍率（原来还有天赋蚀亡语的 0.08，天赋不出招）
assert {x for x in byn['蚀蛰虫'] if used[x]} == {8022030}
for n, (old, new, c) in fixW.items():
    if n == '蚀蛰虫': continue
    m = MON['m'][idx[n]]; assert m.get('w') == old
    if n != '银枝': assert c[new] >= 0.95 * sum(c.values()), (n, c)   # 银枝：关卡里有 3 种弱点（物火冰 61 / 物冰量 14 / 物冰风 7），取最多的，STG 里按关卡另写
    if new: m['w'] = new
    else: m.pop('w', None)
for n, (old, new, c) in fixT.items():
    if n == '蚀蛰虫': continue
    m = MON['m'][idx[n]]; assert m.get('tn') == old and c[new] == sum(c.values()), (n, c)
    m['tn'] = new

# ---------- B3. STG：每个敌人按关卡实际 MonsterID 写弱点 / 韧性 ----------
ST = {x['StageID']: x for x in L('StageConfig')}
EGc = {r['EliteGroup']: r for r in L('EliteGroup')}
HL = {(r['HardLevelGroup'], r['Level']): r for r in L('HardLevelGroup')}
MZ = collections.defaultdict(list)
for n in ('ChallengeMazeConfig', 'ChallengeStoryMazeConfig', 'ChallengeBossMazeConfig'):
    for m in L(n): MZ[m['GroupID']].append(m)
PK = {p['ID']: p for p in L('ChallengePeakConfig')}
def wave(st):
    out = []
    for w in st['MonsterList']:
        for k in sorted(w, key=lambda k: int(k.replace('Monster', ''))):
            mc = M.MC[w[k]]; lv = st['Level']
            sp = M.rawspd(mc) * V(EGc.get(st.get('EliteGroup'), {}), 'SpeedRatio') * V(HL[(st.get('HardLevelGroup', 1), lv)], 'SpeedRatio') / V(HL[(1, lv)], 'SpeedRatio')
            out.append((w[k], M.name(w[k]), round(sp, 2), lv))
    return out
def mids(label):
    G = {'混沌回忆「物竞天择」': 1036, '混沌回忆「漆黑残响」': 1037, '虚构叙事「取象为文」': 2027, '虚构叙事「虚事成理」': 2028,
         '末日幻影「支配遗忘」': 3021, '末日幻影「领航冥茫」': 3022}
    if label in G:
        return [[[x for ev in m.get(f'EventIDList{h}', []) for x in wave(ST[ev])] for h in (1, 2)] for m in sorted(MZ[G[label]], key=lambda m: m['Floor'])]
    if label == '异相仲裁·4.7 骑士（一～三）':
        return [[[x for ev in PK[pid]['EventIDList'] for x in wave(ST[ev])]] for pid in (1101, 1102, 1103)]
    return None
cnt = collections.Counter(); redir = collections.Counter()
for g in STG:
    ms = mids(g['g'])
    if ms is None: assert g['g'].startswith('异相仲裁·4.7 王棋'); continue
    assert len(ms) == len(g['f']), g['g']
    for f, mf in zip(g['f'], ms):
        assert len(f['h']) == len(mf)
        for hw, hm in zip(f['h'], mf):
            flat = [e for w in hw for e in w]
            assert len(flat) == len(hm), (g['g'], f['f'])
            for e, (mid, n, sp, lv) in zip(flat, hm):
                assert (e['n'], e['s'], e['lv']) == (n, sp, lv), (g['g'], e, n, sp, lv)
                m = MON['m'][e['i']]
                if m['n'] != n: assert m['n'].startswith(n + '（'), (m['n'], n)   # 已经指向带后缀的条目
                if SKN(mid) != sorted(y for y in (untag(MON['sk'][i]['n']) for i in m.get('k', []) + m.get('p', [])) if y.strip()):
                    assert n == '天谴先锋' and mid == 401301201, (g['g'], n, mid)
                    e['i'] = idx['天谴先锋（虚构叙事）']; m = TQ; redir[g['g']] += 1
                wv, tv = W(mid), TN(mid)
                if wv != m.get('w', ''): e['w'] = wv; cnt['w'] += 1
                if tv != (m.get('tn') or 0): e['tn'] = tv; cnt['tn'] += 1

# ---------- 写回 ----------
s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]
mS = grab(s, 'STG', r'\[')
s = s[:mS.start(2)] + json.dumps(STG, ensure_ascii=False, separators=(',', ':')) + s[mS.end(2):]

def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:120], s.count(x)); s = s.replace(x, y)
# applyMon：速度 0 的本体不上行动轴；换模板时清掉关卡弱点
rep('    u.seq = (m.q || []).slice(); if (u.seq.length && !u.atkWho) u.atkWho = "rot";   // 默认出招顺序，单体技能轮流打\n',
    '    u.seq = (m.q || []).slice(); if (u.seq.length && !u.atkWho) u.atkWho = "rot";   // 默认出招顺序，单体技能轮流打\n'
    '    if (m.s === 0) u.noAct = true; else delete u.noAct;   // 速度 0、自己不行动的本体（昔在、今在、永在的剧目、末日兽……）：不上行动轴（敌人第 3 批）\n'
    '    delete u.stw;   // 关卡配置的弱点只跟“换上这一波敌人”放上来的那个模板\n')
rep('if (u.gone || u.paused || (u.sm && u.sm.noTurn)) continue;',
    'if (u.gone || u.paused || (u.sm && u.sm.noTurn) || u.noAct) continue;')
# monOf：关卡弱点
rep('const monOf = en => { if (en.__mon === undefined) en.__mon = (en.mon && MON.m.find(m => m.n === en.mon)) || (en.wks ? { w: String(en.wks) } : null); return en.__mon; };',
    'const monOf = en => { if (en.__mon === undefined) en.__mon = (en.mon && (m0 => m0 && en.stw != null ? Object.assign({}, m0, { w: String(en.stw) }) : m0)(MON.m.find(m => m.n === en.mon))) || (en.wks ? { w: String(en.wks) } : null); return en.__mon; };   // stw：按关卡实际配置的弱点（敌人第 3 批）')
# 换上这一波敌人：关卡配置的弱点 / 韧性
rep('u.monS = m.s; u.lv = m.lv; u.spd = u.base = monSpeed(u); u.name = m.n;',
    'u.monS = m.s; u.lv = m.lv; u.spd = u.base = monSpeed(u); u.name = m.n; if (m.w != null) u.stw = m.w; if (m.tn != null) u.tough = m.tn;')
# 卡片：弱点显示关卡的；速度 0 的写明不上行动轴
rep('${(m => m && m.w ? ` · 弱点 ${m.w}` : "")(MON.m.find(m => m.n === u.mon))}',
    '${(m => m && (u.stw ?? m.w) ? ` · 弱点 ${u.stw ?? m.w}${u.stw != null ? "（按关卡）" : ""}` : "")(MON.m.find(m => m.n === u.mon))}${u.noAct ? " · 速度 0：本体自己不行动，不上行动轴" : ""}')
# 敌人出招：再行动 1 次、其他敌人立即行动
rep('          enemyDebuff(actor, tgs, (actor.skx || {})[skIdx], "sk" + skIdx);\n',
    '          enemyDebuff(actor, tgs, (actor.skx || {})[skIdx], "sk" + skIdx);\n'
    '          if (sk.pl === "o") {   // MON.sk.pl：施放后除自身外的敌方全体立即行动（起床铃声、鼓劲、棋快一着；敌人第 3 批）\n'
    '            const oe = U.filter(z => z.kind === "enemy" && z !== actor && !z.gone && !z.noAct);\n'
    '            for (const z of oe) pull(z, 10000);\n'
    '            addLog(`${actor.name}【${sk.n}】：${oe.length ? oe.map(z => z.name).join("、") + " 立即行动（行动提前 100%）" : "场上没有其他敌人"}`, false, "var(--enemy)");\n'
    '          }\n'
    '          if (sk.ag && !FG) actor.again = true;   // MON.sk.ag：施放后再行动 1 次（罪血眈视；敌人第 3 批）\n')

log = open(sys.argv[3], encoding='utf-8').read().strip() if len(sys.argv) > 3 else None
if log:
    ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
    s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('新敌人', added)
print('ag', AG, 'pl', PL)
print('弱点', {n: (o_, n_) for n, (o_, n_, c) in fixW.items()})
print('韧性', {n: (o_, n_) for n, (o_, n_, c) in fixT.items()})
print('蚀蛰虫', sold, '→', {k: sz.get(k) for k in sold})
print('STG', dict(cnt), '天谴先锋改指向', dict(redir), 'MON', nm0, '→', len(MON['m']), 'sk', sk0, '→', len(MON['sk']))
