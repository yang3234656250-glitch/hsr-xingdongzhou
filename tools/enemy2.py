"""敌人第 2 批（2026-11-20，没改 tv）：新敌人 5 个 + 敌人技能按原文选目标（新字段 MON.sk[].ht）+ PoleMos600 补攻击 / 生命 / 倍率。
用法：python3 -I tools/enemy2.py index.html <官方 ExcelOutput 目录（含 TextMapCHS.json）> [更新日志 li 文件]
官方数据：https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/*.json 和 TextMap/TextMapCHS.json
（目录里要有 MonsterConfig MonsterTemplateConfig MonsterSkillConfig EliteGroup StageConfig TextMapCHS）

MON.sk 新字段 ht（没有 = 旧行为，按标签 t）：选目标和算伤害时按这个标签（"群攻" / "扩散" / "单攻"）。
用在标签不是攻击类、但原文写了“对我方全体 / 单体（及相邻）造成伤害”的技能，和标签是「扫射」的技能
（“从我方队伍左侧起发动数次攻击，优先对我方全体目标逐个攻击1次，剩余次数随机攻击我方单体目标”：每人至少挨 1 次，
按群攻选目标；剩下的随机次数不模拟，伤害仍按 倍率 × 次数 ÷ 人数 均分，和弹射一样）。

注意：这个脚本当时（2026-11-20 敌人任务）推不上仓库，结果先发布到了 claude.ai 页面；2026-11-21 每日校对把页面上的
结果原样合回仓库（index.html 已经是跑完后的样子），脚本按项目文档补进来作记录，不要在已经包含这批的页面上再跑一次
（开头的断言会因为新敌人已存在而失败）。
"""
import sys, json, re, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import Mon, page, grab, num

P, D = sys.argv[1], sys.argv[2]
M = Mon(D)
s, crlf = page(P)
assert 'if (s.tv >= 150) return;' in s and 'if (s.tv >= 151) return;' not in s, '页面 tv 不是 150'
mM = grab(s, 'MON', r'\{')
MON = json.loads(mM.group(2))
idx = {m['n']: i for i, m in enumerate(MON['m'])}
SKN = len(MON['sk'])

# ---------- 0. 公共函数和 mon149.py 一致：重建上一批的「含辛茹苦的列车长」必须和页面里的一样 ----------
chk = M.build({'sk': list(MON['sk'])}, 5014024)
old = MON['m'][idx['含辛茹苦的列车长']]
for k in ('n', 'r', 's', 'w', 'tn', 'a', 'h'): assert chk.get(k) == old.get(k), (k, chk.get(k), old.get(k))
tmp = {'sk': list(MON['sk'])}; chk = M.build(tmp, 5014024)
assert [tmp['sk'][i] for i in chk['k'] + chk.get('p', [])] == [MON['sk'][i] for i in old['k'] + old.get('p', [])]

# 关卡里用到的 MonsterID（判断同名的几种配置哪些真的出现过）
used = collections.defaultdict(set)
for st in M.L('StageConfig'):
    for w in st['MonsterList']:
        for k in w: used[w[k]].add(st.get('StageType'))
def sig(mid):
    return tuple(M.T(M.MS[x]['SkillName']) for x in M.MC[mid].get('SkillList', []) if x in M.MS and M.T(M.MS[x].get('SkillName')))

# ---------- A. 新敌人 ----------
NEW = [
    # 「哲学的胎儿」疯狂：主线（关卡 205710850～56 都用 5035020）；同名的 5035021（韧性 960）没有关卡用到，不加
    (5035020, None, None, (), [5035020]),
    # 喜剧的残渣：主线小怪（和狂兽的胚芽一起，70 个关卡）
    (5032040, None, None, (), [5032040]),   # 503204001（生命值减半的同名配置）没有关卡用到
    # 至高，至阳，天空的化身：历战余响（关卡 1052070～76，4015011）和异相仲裁（30502021 / 22，401501101）用的是 20 个技能的版本，
    # 页面原来的条目是主线 401501001（13 个技能）。“自灰烬彼岸 / 落灭死残星 / 烬灰死寂•诸神屠灭”原文是“固定数值伤害”（按【黑潮同步率】），不写倍率
    (4015011, '至高，至阳，天空的化身（历战余响）', {'击三千里之火': '群攻', '鸣三千里之雷': '群攻'}, ('自灰烬彼岸', '落灭死残星', '烬灰死寂•诸神屠灭'), [4015011, 401501101]),
    # 杰帕德：末日幻影「冽风骑士」（3001）/「冥茫冽风」（3012）第 3 层上半（关卡 4201xx～4204xx，1004026 模板），弱点、韧性、技能和主线不同
    (100402601, '杰帕德（末日幻影）', None, (), [100402601, 100402602, 100402603, 100402604]),
    # 金血忆灵•裁定忘却之形：虚构叙事「造象立说」（2023）第 4 层下半（关卡 30321042，4064014），韧性 720、7 个技能
    (4064014, '金血忆灵•裁定忘却之形（虚构叙事）', None, (), [4064014]),
]
added = []
for mid, nm, ht, nox, same in NEW:
    o = M.build(MON, mid, nm, None, nox, ht)
    assert o['n'] not in idx, ('重名', o['n'])
    for x in same:   # 同一种的几个配置：速度、韧性、弱点、技能一样
        assert x in used, ('关卡没用到', x)
        assert num(M.rawspd(M.MC[x])) == o['s'] and M.stats(x)['tn'] == o['tn'] and sig(x) == sig(mid), x
    idx[o['n']] = len(MON['m']); MON['m'].append(o); added.append((o['n'], mid, o['s'], o['tn'], o['w']))
assert 5035021 not in used and sig(5035021) == sig(5035020)
assert num(M.rawspd(M.MC[100402605])) == 240 and 100402605 not in used   # 速度 240 的那个没有关卡用到

# ---------- B1. 敌人技能按原文选目标（ht） ----------
HT = {   # 下标: (技能名, 原标签, ht, 是否去掉倍率)
    81: ('击三千里之火', '扫射', '群攻', False), 86: ('鸣三千里之雷', '扫射', '群攻', False), 1052: ('送出哀泣的飞矢', '扫射', '群攻', False),
    152: ('不磨不灭的灾厄', '强化', '群攻', False), 281: ('不磨不灭的灾厄', '强化', '群攻', False),
    # 于痛苦的芬芳中死去：原文是“【衰亡伤害】，该伤害【不致命】”，官方参数 0.05 / 0.145 不像是攻击力倍率，倍率去掉（只算受击回能 / 受到攻击）
    293: ('于痛苦的芬芳中死去', '强化', '群攻', True), 297: ('于痛苦的芬芳中死去', '强化', '群攻', True), 446: ('于痛苦的芬芳中死去', '强化', '群攻', True),
    475: ('于痛苦的芬芳中死去', '强化', '群攻', True), 509: ('于痛苦的芬芳中死去', '强化', '群攻', True),
    1104: ('引爆扩散', '妨害', '扩散', False),   # “对指定我方单体及相邻目标造成风属性伤害”
    784: ('吞噬衍生物', '锁定', '单攻', False),   # “对指定我方单体造成冰属性伤害”
}
for i, (n, t, h, dx) in HT.items():
    k = MON['sk'][i]; assert (k['n'], k['t']) == (n, t) and 'ht' not in k and not k.get('ha'), (i, k)
    assert ('全体' in k['d']) == (h == '群攻') or t == '扫射', (i, k['d'])
    k['ht'] = h
    if dx:
        for m in MON['m']:
            if i in m.get('k', []) and str(i) in m.get('x', {}): del m['x'][str(i)]
# 剩下标签不是攻击类、原文却有“对……我方……造成……伤害”的：都是随机 / 特殊目标，先不动（记在差异清单）
rest = [(i, k['n']) for i, k in enumerate(MON['sk']) if k['t'] not in ('单攻', '群攻', '扩散', '弹射', '横扫', '分摊', '天赋', '扫射')
        and not k.get('ha') and not k.get('ht') and re.search(r'对[^，。]*我方[^，。]*造成[^，。]*伤害', k['d'])]
print('未处理', rest)

# ---------- B2. PoleMos600自主防御程序：名字里官方有 <unbreak> 标签，build_monstat.py 当时没对上，缺 a / h / x ----------
pm = MON['m'][idx['PoleMos600自主防御程序']]
assert 'a' not in pm and 'h' not in pm and 'x' not in pm
assert [mid for mid in M.MC if M.name(mid) == 'PoleMos600自主防御程序'] == [401401101]
tmp = {'sk': list(MON['sk'])}; ref = M.build(tmp, 401401101)
assert (ref['s'], ref['tn'], ref['w']) == (pm['s'], pm['tn'], pm['w'])
pairs = list(zip(pm['k'], ref['k'])); assert len(pm['k']) == len(ref['k'])
for a, b in pairs: assert MON['sk'][a]['n'] == tmp['sk'][b]['n'] and MON['sk'][a]['d'] == tmp['sk'][b]['d'], (a, b)
pm['a'], pm['h'] = ref['a'], ref['h']
pm['x'] = {str(a): ref['x'][str(b)] for a, b in pairs if str(b) in ref.get('x', {})}

# ---------- 写回 MON ----------
s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]

def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:100], s.count(x)); s = s.replace(x, y)
rep('if (HITALL.includes(sk.t) || sk.ha || aw === "all") tgs = HIT1.concat(HIT3, HITALL).includes(sk.t) ? pool : [];',
    'const tT = sk.ht || sk.t;   // sk.ht：按这个标签选目标、算伤害（标签是扫射 / 强化 / 锁定 / 妨害、原文写了打谁的，敌人第 2 批 tools/enemy2.py）\n'
    '          if (HITALL.includes(tT) || sk.ha || aw === "all") tgs = HIT1.concat(HIT3, HITALL).includes(tT) ? pool : [];')
rep('else if (HIT1.includes(sk.t)) tgs = main ? [main] : [];', 'else if (HIT1.includes(tT)) tgs = main ? [main] : [];')
rep('else if (HIT3.includes(sk.t) && main) {', 'else if (HIT3.includes(tT) && main) {')
rep('tg === main || !main || HITALL.includes(sk.t) || sk.ha ? num(xr[0])', 'tg === main || !main || HITALL.includes(tT) || sk.ha ? num(xr[0])')
rep('ZRT = ["单攻", "扩散", "弹射", "群攻", "横扫", "分摊"];', 'ZRT = ["单攻", "扩散", "弹射", "群攻", "横扫", "分摊", "扫射"];')

log = open(sys.argv[3], encoding='utf-8').read().strip() if len(sys.argv) > 3 else None
if log:
    ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
    s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('新敌人', added)
print('ht', {i: (MON['sk'][i]['n'], MON['sk'][i]['ht']) for i in HT}, '新技能', SKN, '→', len(MON['sk']))
print('PoleMos', pm['a'], pm['h'], pm['x'])
print('MON', len(MON['m']))
