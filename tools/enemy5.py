"""敌人第 5 批（2026-11-23 晚的定时任务做在 claude.ai 页面上，没推上仓库；2026-11-23 按页面更新日志重写这个脚本合回仓库）。
没改 tv：只改数据（MON、STG）。用法：python3 -I tools/enemy5.py index.html <官方 ExcelOutput 目录（含 TextMapCHS.json）> <更新日志 li 文件>
官方数据：https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/*.json 和 TextMap/TextMapCHS.json

合回时逐条和 claude.ai 页面核对过（Artifact edit_version 探测：页面里有完全相同的文字）：
  改了 q 的 10 个条目、改了弱点的 9 个条目、MON.m 末尾 3 个新条目和 MON.sk 末尾 19 个新技能、STG 去掉的弱点覆盖。

A. 新敌人（monlib.build，追加在 MON.m / MON.sk 末尾，顺序如下）：
   自动机兵•灰熊（完整）（模拟宇宙）1013014、自动机兵•齿狼（完整）（模拟宇宙）1013024、魔王爪牙 4032023（速度 0：不出招、不写倍率，天赋放 p）。
B. 9 个模板的弱点改成关卡里用得最多的配置；STG 里和新弱点相同的“按关卡”覆盖去掉（24 处）。
C. 「锁定」后的出招：目标锁定 / 瞄准指令 / 协力指令 → 砍伐指令，灭世纪的预兆 → 裂魂寒流：每个锁定技能后面（出招表循环）紧接 X。
   齿狼类 8 个、可可利亚 2 个；有几个锁定技能的条目按页面上的结果（见 QFIX）。
"""
import sys, json, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import Mon, page, grab

P, D, LI = sys.argv[1], sys.argv[2], sys.argv[3]
M = Mon(D)
s, crlf = page(P)
mM = grab(s, 'MON', r'\{'); MON = json.loads(mM.group(2))
assert '自动机兵•齿狼（完整）（模拟宇宙）' not in [m['n'] for m in MON['m']], '已经跑过'
M0 = json.loads(mM.group(2))
idx = {m['n']: i for i, m in enumerate(MON['m'])}

W = {'虚卒•掠夺者': '物雷', '银鬃近卫': '风量', '隐秘的行刺者': '火冰量', '幻胧': '火冰风', '地狱笑话': '风虚', '失真': '物雷',
     '感染的学生': '物虚', '云骑幻象': '物雷量', '虫群•真蛰虫（完整）': '冰量虚'}
for n, w in W.items(): MON['m'][idx[n]]['w'] = w

a = M.build(MON, 1013014, '自动机兵•灰熊（完整）（模拟宇宙）'); MON['m'].append(a)
b = M.build(MON, 1013024, '自动机兵•齿狼（完整）（模拟宇宙）'); MON['m'].append(b)
c = M.build(MON, 4032023)
assert c['n'] == '魔王爪牙' and c['s'] == 0
ks = c['k'] + c.get('p', []); c['k'] = [i for i in ks if MON['sk'][i]['t'] != '天赋']; p = [i for i in ks if MON['sk'][i]['t'] == '天赋']
if p: c['p'] = p
else: c.pop('p', None)
c['q'] = []; c.pop('x', None); MON['m'].append(c)

LK = {'目标锁定': '砍伐指令', '瞄准指令': '砍伐指令', '协力指令': '砍伐指令', '灭世纪的预兆': '裂魂寒流'}
QFIX = {'自动机兵•齿狼（完整）': [575, 836, 837, 836, 838, 836, 839, 840], '自动机兵•齿狼（错误）': [842, 575, 842, 576, 577, 837],
        '自动机兵•齿狼（完整）（模拟宇宙）': [1341, 1340, 1342, 1340, 1343, 1340, 1344, 1345]}
ch = []
for m in MON['m']:
    if 'q' not in m: continue
    locks = [i for i in m['q'] if MON['sk'][i]['n'] in LK and MON['sk'][i]['t'] == '锁定']
    if not locks: continue
    X = next((i for i in m['q'] if MON['sk'][i]['n'] == LK[MON['sk'][locks[0]]['n']]), None)
    if X is None: continue
    q0 = list(m['q'])
    if m['n'] in QFIX: m['q'] = QFIX[m['n']]
    else: m['q'].remove(X); m['q'].insert(m['q'].index(locks[0]) + 1, X)
    if m['q'] != q0: ch.append(m['n'])
assert len(ch) == 10, ch

s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]

# STG：和新弱点一样的覆盖去掉
mS = grab(s, 'STG', r'\['); STG = json.loads(mS.group(2))
chw = {k for k in range(len(M0['m'])) if M0['m'][k].get('w') != MON['m'][k].get('w')}
n = 0
def walk(o):
    global n
    if isinstance(o, dict):
        if 'i' in o and 'lv' in o and o['i'] in chw and o.get('w') == MON['m'][o['i']].get('w'): del o['w']; n += 1
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    else: return
walk(STG)
assert n == 24, n
s = s[:mS.start(2)] + json.dumps(STG, ensure_ascii=False, separators=(',', ':')) + s[mS.end(2):]

# 更新日志（页面上原样的那一条）
li = open(LI, encoding='utf-8').read().strip()
anchor = '<li><b>2026-11-23（借鉴绯绯狐工具箱的三处显示，没改 tv）</b>'   # 页面上它排在这一条后面
assert s.count(anchor) == 1 and li not in s
j = s.index('</li>', s.index(anchor)) + 5
s = s[:j] + '\n' + li + s[j:]

if crlf: s = s.replace('\n', '\r\n')
open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok', ch)
