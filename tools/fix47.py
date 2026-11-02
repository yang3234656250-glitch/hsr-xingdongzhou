"""tv 47：每日校对 2026-11-02（丹恒 1002、银狼【强化版】1006、阿兰 1008、艾丝妲 1009），对照 StarRailRes 原文。
用法：python3 tools/fix47.py index.html
- 丹恒：补战技云骑枪术•疾雨“暴击时 100% 基础概率使目标速度 −12%，持续 2 回合”（E6 额外 −8%，按目标自己的回合，默认关：要暴击才有）；
  伤害：补终结技“目标处于减速状态时伤害倍率提高 120%（12 级 129.6%）”（XR slow，默认不勾）。
- 银狼【强化版】：行迹旁注换成强化版原文（每 10% 效果命中攻击力 +10%，最多 50%；原来误用了旧版“负面 ≥3 个时减抗 +3%”，默认关）；
  天赋【缺陷】持续 3 → 4 回合（强化版行迹生成：+1 回合）；DMG 终结技改成群攻（强化版 1100603 是群攻，原来按单攻）。
- 阿兰：行迹苏生“消灭敌方目标时若当前生命值 ≤30% 回复 20% 生命上限”改成按当前生命值判断（hle 30），默认开启（原来写“模拟里没有生命值”关着）；
  伤害：补 E6“生命值 ≤50% 时终结技对相邻目标的倍率提高到与主目标相同”（XR e6adj，默认不勾，和 E6 增伤一起开）。
- 艾丝妲：E1“施放战技时对随机单体额外造成 1 次伤害”= 1 段 50%（战技总倍率 5 段的 1/5），XR 原来按整个战技 250% 算，改成 ×0.2。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 47
assert f'if (s.tv >= {TV - 1}) return;' in s
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}

# ---------- 丹恒 1002 ----------
c = C[1002]
slow = dict(y='spd', t='skill', tg='enemies', v=-12, m='pct', d=2, cnt='own', lv=[6, -20], off=1,
            n='战技云骑枪术•疾雨：暴击时使目标速度 −12%，持续 2 回合（E6 再 −8%；按目标自己的回合；这里对全部敌人生效，要暴击才有，需要时启用）')
c['eff'].insert(1, slow)
FIX['1002'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [slow['n']], 'sm': {}}

# ---------- 银狼 1006（强化版） ----------
c = C[1006]
qx = next(x for x in c['eff'] if x.get('bk') == 'qx')
o1 = qx['n']; assert qx['d'] == 3 and qx['t'] == 'atk'
qx['d'] = 4
qx['n'] = '【强化版】天赋：【缺陷】防御力 −12%，持续 4 回合（含行迹生成 +1 回合；随机 3 种，按挂上防御缺陷算）'
pz = next(x for x in c['eff'] if x.get('bk') == 'pz')
o2 = pz['n']; assert pz['t'] == 'skill' and pz['m'] == 'resRed'
i = c['eff'].index(pz)
npz = dict(y='dbuf', t='start', tg='self', m='atkP', v=50, d=0, bk='pz', off=1,
           n='【强化版】行迹旁注：每有 10% 效果命中攻击力额外 +10%，最多 +50%（按效果命中 ≥50% 算；面板攻击力里已经算进去或命中不够时别开 / 改数值）')
c['eff'][i] = npz
FIX['1006'] = {'drop': [o1, o2], 'trig': {o1: 'atk', o2: 'skill'}, 'map': {o1: qx['n']}, 'add': [qx['n'], npz['n']], 'sm': {}}

# ---------- 阿兰 1008 ----------
c = C[1008]
h = next(x for x in c['eff'] if x['y'] == 'heal' and x['t'] == 'kill')
o3 = h['n']
h.pop('off', None); h['hle'] = 30
h['n'] = '行迹苏生：消灭敌方目标时若当前生命值 ≤30%，立即回复自身 20% 生命上限'
FIX['1008'] = {'drop': [o3], 'trig': {o3: 'kill'}, 'map': {o3: h['n']}, 'add': [h['n']], 'off0': [o3], 'sm': {}}
put(m, DB)

# ---------- 伤害表 ----------
m, DMG = grab('DMG')
assert DMG['1006']['u']['tg'] == 1
DMG['1006']['u']['tg'] = 3   # 强化版终结技 1100603：对敌方全体造成 380%（12 级 410.4%）
put(m, DMG)

m, XR = grab('XR')
assert '1002' not in XR
XR['1002'] = [dict(k='slow', n='终结技：目标处于减速状态时伤害倍率 +120%（12 级 129.6%；目标减速时勾上）', on=['u'], st='atk', v=[1.2, 1.296], lk='u', off=1)]
XR.setdefault('1008', [])
assert not any(r['k'] == 'e6adj' for r in XR['1008'])
XR['1008'].append(dict(k='e6adj', n='E6：生命值 ≤50% 时终结技对相邻目标的倍率提高到与主目标相同（每个相邻目标 + 主目标倍率 50%；和 E6 增伤一起开）',
                       on=['u'], st='mult', v=[0.5], cnt='adj', e=6, off=1))
e1 = next(r for r in XR['1009'] if r['k'] == 'e1'); assert e1['v'] == [1.0]
e1.update(v=[0.2], n='E1：施放战技时对随机敌方单体额外造成 1 次伤害（1 段 = 战技总倍率的 1/5）')
put(m, XR)

def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:80], s.count(x)); s = s.replace(x, y)
a = re.search(r'  // tv 46：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-02（丹恒、银狼、阿兰、艾丝妲，tools/fix47.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
for k, v in FIX.items():
    for d in v['drop']: assert d in v['trig'], (k, d)
print('ok', {k: (len(v['drop']), len(v['add'])) for k, v in FIX.items()})
