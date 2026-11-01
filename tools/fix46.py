"""tv 46：每日校对 2026-11-01（三月七 1001、姬子 1003、瓦尔特【强化版】1004、卡芙卡【强化版】1005），对照 StarRailRes 原文。
用法：python3 tools/fix46.py index.html
- 三月七：天赋反击每回合次数 4 魂起自动 2 → 3（lvX allyCap，原来要手改）；补 E2 进入战斗时为生命值百分比最低的我方目标提供护盾（lowhp）。
- 姬子：天赋按原文——充能满 3 点后“我方目标施放攻击后”才发动追加攻击并消耗全部充能（原来是充满当场就打）；补秘技不完全燃烧（敌方受到火属性伤害 +10%，2 回合，默认关）。
- 瓦尔特【强化版】：补秘技画地为牢（进战敌方禁锢：行动延后 20%、速度 −10% 1 回合，默认关）；
  伤害：行迹审判 / E1 / E6 的附加伤害按“战技伤害倍率”= 单段 72% 算（原来按 5 段合计 360% 算，大了 5 倍），E1 普攻 50% / 战技 80% 分开。
- 卡芙卡【强化版】：天赋追加攻击按原文做成可触发次数（最多 2 次、开局 2 次，卡芙卡回合结束时恢复 1 次，行迹荆棘：施放终结技后恢复 1 次），
  原来按“每回合 2 次”近似。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 46
assert f'if (s.tv >= {TV - 1}) return;' in s
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}
E = lambda c: {r['r']: r for r in c['eid']}

# ---------- 三月七 1001 ----------
c = C[1001]
t = next(x for x in c['eff'] if x['n'].startswith('天赋：持有护盾的队友受到攻击后反击'))
o = t['n']
t['n'] = '天赋少女的特权：持有护盾的我方目标受到攻击后反击（每回合 2 次，4 魂起自动 3 次）'
t['lx'] = {'allyCap': [2, 3]}; t['le'] = 4
e = E(c)
e[4]['notes'] = [n for n in e[4].get('notes', []) if '每回合最多' not in n]
c['eid'].append({'r': 2, 'eff': [dict(y='shield', t='start', tg='lowhp', v=0, n='E2 记忆中的它：进入战斗时为当前生命值百分比最低的我方目标提供护盾（三月七 24% 防御力 +320，3 回合）')], 'notes': []})
c['eid'].sort(key=lambda r: r['r'])
FIX['1001'] = {'drop': [o], 'trig': {o: 'hit'}, 'map': {o: t['n']}, 'add': [t['n']], 'sm': {}}

# ---------- 姬子 1003 ----------
c = C[1003]
f = next(x for x in c['eff'] if x['y'] == 'fua' and x['t'] == 'cnt')
o = f['n']
f.clear(); f.update(y='fua', t='atk', aw='all', tg='self', v=0, uc=3,
                    n='天赋乘胜追击：充能达到上限 3 点时，我方目标施放攻击后立即追加攻击，并消耗全部充能')
c['cnt'] = {'n': '充能', 'at': 0, 'max': 3}
c['notes'] = [n for n in c.get('notes', []) if '下一次我方攻击' not in n]
tech = dict(y='dbuf', t='start', tg='enemies', m='vuln', v=10, d=2, bk='hjt', off=1,
            n='秘技不完全燃烧：进入战斗时敌方受到的火属性伤害 +10%，持续 2 回合（只该算火属性，这里对全部伤害生效：队里只有姬子等火属性角色打伤害时再启用）')
c['eff'].append(tech)
FIX['1003'] = {'drop': [o], 'trig': {o: 'cnt'}, 'map': {o: f['n']}, 'add': [f['n'], tech['n']],
               'set': {'cntAt': 0, 'cntMax': 3}, 'sm': {}}

# ---------- 瓦尔特 1004 ----------
c = C[1004]
t1 = dict(y='delay', t='start', tg='enemies', v=20, off=1, n='秘技画地为牢：进入战斗时敌方陷入禁锢，行动延后 20%（用了秘技再启用）')
t2 = dict(y='spd', t='start', tg='enemies', v=-10, d=1, m='pct', off=1, n='秘技画地为牢：禁锢状态下速度 −10%，持续 1 回合（用了秘技再启用）')
c['eff'] += [t1, t2]
FIX['1004'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [t1['n'], t2['n']], 'sm': {}}

# ---------- 卡芙卡 1005 ----------
c = C[1005]
f = next(x for x in c['eff'] if x['y'] == 'fua')
o = f['n']
i = c['eff'].index(f)
nf = dict(y='fua', t='atk', aw='others', tg='self', v=0, uc=1, n='【强化版】天赋：队友施放攻击后立即追加攻击（消耗 1 次可触发次数）')
n1 = dict(y='count', t='start', tg='self', v=2, n='【强化版】天赋：追加攻击最多可触发 2 次（战斗开始时有 2 次）')
n2 = dict(y='count', t='ally', aw='self', tg='self', v=1, n='【强化版】天赋：卡芙卡回合结束时恢复 1 次可触发次数（最多 2 次）')
n3 = dict(y='count', t='ult', tg='self', v=1, n='【强化版】行迹荆棘：施放终结技后恢复 1 次天赋追加攻击可触发次数')
c['eff'][i:i + 1] = [n1, nf, n2, n3]
c['cnt'] = {'n': '追击次数', 'at': 0, 'max': 2}
FIX['1005'] = {'drop': [o], 'trig': {o: 'atk'}, 'map': {o: nf['n']}, 'add': [n1['n'], nf['n'], n2['n'], n3['n']],
               'set': {'cntName': '追击次数', 'cntAt': 0, 'cntMax': 2}, 'sm': {}}
put(m, DB)

# ---------- 瓦尔特附加伤害（XR）：战技伤害倍率 = 单段 72%，DMG 里的 s 是 5 段合计，所以除以 5 ----------
m, XR = grab('XR')
L = XR['1004']; K = {x['k']: x for x in L}
K['sp2'].update(v=[0.24], n='行迹审判：战技额外 1 次附加伤害，等于战技伤害倍率（单段 72%）的 120%')
K['e6'].update(v=[0.2], n='E6：施放战技时对随机敌方单体额外造成 1 次伤害（1 段战技伤害）')
K['e1'].update(on=['b'], v=[0.5], n='E1：终结技后 2 次普攻 / 战技额外附加伤害：普攻为普攻倍率 50%（需要时勾上，会对所有普攻都算）')
i = L.index(K['e1'])
L.insert(i + 1, dict(K['e1'], k='e1s', on=['s'], v=[0.16], n='E1：终结技后 2 次普攻 / 战技额外附加伤害：战技为战技伤害倍率（单段 72%）的 80%（需要时勾上，会对所有战技都算）'))
put(m, XR)

def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:80], s.count(x)); s = s.replace(x, y)
a = re.search(r'  // tv 45：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-01（三月七、姬子、瓦尔特、卡芙卡，tools/fix46.py）\n'
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
