"""tv 50：每日校对 2026-11-04（希露瓦 1103、杰帕德 1104、娜塔莎 1105、佩拉 1106），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix50.py index.html（需要 /tmp/sr/character_skills.json）
- 希露瓦：全部核对无误，不改。
- 杰帕德：
  · 行迹统领“【不屈之身】触发后，杰帕德的能量立即恢复至 100%”原来漏了 → energy full（t hit、first，和天赋那条一样默认关）；
  · E6“触发天赋时杰帕德立即行动，且当前生命值的回复量额外增加自身生命上限的 50%”原来只写在 notes → advance 100 + 额外 heal 50%（默认关）；
  · 行迹战意“提高等同于自身当前防御力 35% 的攻击力，每回合开始时刷新”原来漏了 → dbuf atkF ss def 35%（只影响伤害）；
  · 秘技有情之证“下一次战斗开始时为我方全体提供护盾，持续 2 回合”原来漏了 → shield start allies（默认关，护盾数值不做）。
- 娜塔莎：
  · 天赋生机焕发原来是默认关闭的固定 +50%，改成 hbup low（为当前生命值 ≤30% 的目标治疗时 +50%，5 魂 55%，持续治疗也算），默认开；
  · E1 遍识药理加条件 hle 30（受到攻击后当前生命值 ≤30% 才回复），默认开；
  · E2 临床研学目标改成新目标 hp30（当前生命值 ≤30% 的每个我方目标），默认开。
- 佩拉：全部数值核对无误；行迹追歼（下一次攻击增伤 20%）没有“只算下一次攻击”的写法，只记在 notes。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 50
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

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}
def find(L, pred):
    R = [x for x in L if pred(x)]; assert len(R) == 1, R; return R[0]

# ---------- 杰帕德 1104 ----------
c = C[1104]
tal = prm('110404')
assert abs(tal[9][0] - 0.5) < 1e-9 and abs(tal[11][0] - 0.55) < 1e-9
hl = find(c['eff'], lambda x: x['y'] == 'heal' and x['t'] == 'hit')
o_hl = hl['n']; assert hl['v'] == 50 and hl['lv'] == [3, 55] and hl.get('first') and hl.get('off')
hl['n'] = '天赋不屈之身：受到致命攻击时不倒下，立即回复自身生命上限 50%（3 魂 55%）的生命值（每场 1 次；敌人伤害不做，需要时启用）'
i = c['eff'].index(hl) + 1
tl = dict(y='energy', t='hit', tg='self', v=0, m='full', first=1, off=1, n='行迹统领：【不屈之身】触发后能量立即恢复至 100%（和天赋那条一起启用）')
zy = dict(y='dbuf', t='start', tg='self', m='atkF', ss='def', v=35, d=0, bk='zy', n='行迹战意：攻击力提高自身当前防御力的 35%，每回合开始时刷新（按卡片面板防御力）')
sh = dict(y='shield', t='start', tg='allies', v=0, off=1, n='秘技有情之证：下一次战斗开始时为我方全体提供护盾，持续 2 回合（用了秘技再启用；护盾数值不做）')
c['eff'][i:i] = [tl, zy, sh]
e6 = next(e for e in c['eid'] if e['r'] == 6)
assert not e6.get('eff')
e6['eff'] = [dict(y='advance', t='hit', tg='self', v=100, first=1, off=1, n='E6 不屈的决意：触发天赋时杰帕德立即行动（和天赋那条一起启用）'),
             dict(y='heal', t='hit', tg='self', m='hp', v=50, first=1, off=1, n='E6 不屈的决意：触发天赋时生命值回复量额外 +自身生命上限的 50%（和天赋那条一起启用）')]
e6['notes'] = []
FIX['1104'] = {'drop': [o_hl], 'trig': {o_hl: 'hit'}, 'map': {o_hl: hl['n']}, 'add': [hl['n'], tl['n'], zy['n'], sh['n']], 'sm': {}}

# ---------- 娜塔莎 1105 ----------
c = C[1105]
tal = prm('110504')
assert abs(tal[9][0] - 0.3) < 1e-9 and abs(tal[9][1] - 0.5) < 1e-9 and abs(tal[11][1] - 0.55) < 1e-9
hb = find(c['eff'], lambda x: x['y'] == 'hbup')
o_hb = hb['n']; assert hb['t'] == 'start' and hb.get('off')
hb.pop('off'); hb['m'] = 'low'; hb['ovT'] = 30
hb['n'] = '天赋生机焕发：为当前生命值 ≤30% 的目标提供治疗时治疗量 +50%（5 魂 55%；持续治疗也算，按治疗前的生命值）'
e1 = next(e for e in c['eid'] if e['r'] == 1)['eff'][0]
assert e1['t'] == 'hit' and e1['v'] == 15 and e1['hf'] == 400
e1.pop('off'); e1['hle'] = 30
e1['n'] = 'E1 遍识药理：受到攻击后若当前生命值 ≤30%，对自身施放 1 次治疗，回复 15% 生命上限 +400（每场 1 次）'
e2 = next(e for e in c['eid'] if e['r'] == 2)['eff'][0]
assert e2['t'] == 'ult' and e2['v'] == 6 and e2['hf'] == 160 and e2['ho'] == 1
e2.pop('off'); e2['tg'] = 'hp30'
e2['n'] = 'E2 临床研学：施放终结技时对当前生命值 ≤30% 的我方目标附加 1 回合持续治疗，目标回合开始时回复娜塔莎 6% 生命上限 +160'
FIX['1105'] = {'drop': [o_hb], 'trig': {o_hb: 'start'}, 'map': {o_hb: hb['n']}, 'add': [hb['n']], 'off0': [o_hb], 'sm': {}}

# ---------- 佩拉 1106 ----------
c = C[1106]
c.setdefault('notes', []).append('行迹追歼：施放战技解除增益效果时，下一次攻击造成的伤害提高 20%（“只算下一次攻击”没法表示，没做）')
put(m, DB)

# ---------- 代码：新目标 hp30 ----------
rep('      if (target === "lowhp" || target === "hp50") {', '      if (target === "lowhp" || target === "hp50" || target === "hp30") {')
rep('        if (target === "hp50") return L.filter(x => x[1] <= 0.5 + 1e-9).map(x => x[0]);',
    '        if (target === "hp50") return L.filter(x => x[1] <= 0.5 + 1e-9).map(x => x[0]);\n        if (target === "hp30") return L.filter(x => x[1] <= 0.3 + 1e-9).map(x => x[0]);   // 当前生命值 ≤30% 的每个我方目标（娜塔莎 E2）')
rep('["hp50", "当前生命值 ≤50% 的我方目标"], ', '["hp50", "当前生命值 ≤50% 的我方目标"], ["hp30", "当前生命值 ≤30% 的我方目标"], ')

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-04（希露瓦、杰帕德、娜塔莎、佩拉，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
