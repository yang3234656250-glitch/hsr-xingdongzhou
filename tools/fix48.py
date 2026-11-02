"""tv 48：用户 2026-11-02 看完每日校对后定的三条。
用法：python3 tools/fix48.py index.html
- 艾丝妲终结技星空祝言（100903“使我方全体速度提高 50 点，持续 2 回合”）的加速按每个队友各自的回合计时
  （count own：每个队友在自己回合结束时 −1，额外回合不算）；原来按艾丝妲的回合。
- 丹恒战技减速只对单体：新目标 efirst =“敌方单体（第一个敌人）”，原来对敌方全体。
- 银狼【强化版】天赋【缺陷】的速度 −6%（1100604，12 级 6.6%）做进模拟：持续 4 回合（含行迹生成 +1），按敌人自己的回合；
  普攻 / 战技挂在单体（efirst），终结技（群攻）挂在敌方全体。缺陷是 3 种随机一种，所以默认关闭。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 48
assert f'if (s.tv >= {TV - 1}) return;' in s
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]

def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:80], s.count(x)); s = s.replace(x, y)
m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
c = C[1009]
u = next(x for x in c['eff'] if x['y'] == 'spd' and x['t'] == 'ult')
o = u['n']; assert o == '终结技' and 'cnt' not in u
u['cnt'] = 'own'
u['n'] = '终结技星空祝言：我方全体速度 +50（5 魂 52.8），持续 2 回合（按每个队友自己的回合）'
FIX = {'1009': {'drop': [o], 'trig': {o: 'ult'}, 'map': {o: u['n']}, 'add': [u['n']], 'sm': {}}}

c = C[1002]
d = next(x for x in c['eff'] if x['y'] == 'spd' and x['t'] == 'skill')
o2 = d['n']; assert d['tg'] == 'enemies'
d['tg'] = 'efirst'
d['n'] = '战技云骑枪术•疾雨：暴击时使目标（敌方单体）速度 −12%，持续 2 回合（E6 再 −8%；按目标自己的回合；默认第一个敌人，可在目标里换；要暴击才有，需要时启用）'
FIX['1002'] = {'drop': [o2], 'trig': {o2: 'skill'}, 'map': {o2: d['n']}, 'add': [d['n']], 'sm': {}}

c = C[1006]
qx = next(x for x in c['eff'] if x.get('bk') == 'qx')
i = c['eff'].index(qx) + 1
s1 = dict(y='spd', t='basic', o='skill', tg='efirst', v=-6, m='pct', d=4, cnt='own', lv=[3, -6.6], bk='qxspd', off=1,
          n='【强化版】天赋：【缺陷】速度 −6%（普攻 / 战技的目标，敌方单体），持续 4 回合（含行迹生成 +1；3 种缺陷随机一种，按挂上速度缺陷算，需要时启用）')
s2 = dict(y='spd', t='ult', tg='enemies', v=-6, m='pct', d=4, cnt='own', lv=[3, -6.6], bk='qxspd', off=1,
          n='【强化版】天赋：【缺陷】速度 −6%（终结技打到的敌方全体），持续 4 回合（含行迹生成 +1；3 种缺陷随机一种，按挂上速度缺陷算，需要时启用）')
c['eff'][i:i] = [s1, s2]
FIX['1006'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [s1['n'], s2['n']], 'sm': {}}
put(m, DB)

# 新目标 efirst：敌方单体（第一个敌人卡）
rep('      if (target === "enemies") return U.filter(u => u.kind === "enemy");\n',
    '      if (target === "enemies") return U.filter(u => u.kind === "enemy");\n'
    '      if (target === "efirst") { const e = U.find(u => u.kind === "enemy"); return e ? [e] : []; }   // 敌方单体：第一个敌人卡（丹恒战技减速、银狼缺陷）\n')
rep('["enemies", "敌方全体"], ["sm", "我的召唤物"]]', '["enemies", "敌方全体"], ["efirst", "敌方单体（第一个敌人）"], ["sm", "我的召唤物"]]')
rep('(e.target === "enemies" && u.kind === "enemy");', '(e.target === "enemies" && u.kind === "enemy") || (e.target === "efirst" && u === S.units.find(x => x.kind === "enemy"));')
a = re.search(r'  // tv 47：', s)
s = s[:a.start()] + (f'  // tv {TV}：艾丝妲终结技加速按队友各自的回合、丹恒减速对单体、银狼缺陷减速（tools/fix48.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok')
