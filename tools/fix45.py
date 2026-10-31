"""2026-10-31 接着补：
- 千冶•刃：x.skHp1（当前生命值 ≤1 时无法施放战技，改用强化普攻）、x.cntHp1（当前生命值 >1 才消耗充能施放额外战技，否则充能留着、受到治疗后再触发）。
- 刃（强化版）：DMG 倍率换成强化版官方参数（普攻 50% 生命上限、无间剑树 130% / 相邻 52%、终结技 150% / 相邻 60% 生命上限、天赋追击 130%），
  终结技加上累计已损失生命值（主目标 120% / 相邻 60%，DMG u.lm / u.la 按等级；1 魂主目标再 +150%，u.e1），
  模拟里记累计已损失生命值：x.lossAcc = [上限 90%, 开大后保留 50%（强化版无尽形寿）, 受到治疗时 25% 治疗数值计入（强化版吞忍百死）]；
  XR 里按满额估的 1 魂那条去掉（改成按实际累计值算）。
这些都只在模拟 / 伤害显示时从模板读，不写到卡片上，所以不用迁移。
用法：python3 tools/fix45.py index.html <StarRailRes index_new/cn 目录>
"""
import re, json, sys
P, O = sys.argv[1], sys.argv[2].rstrip('/') + '/'
s = open(P, encoding='utf-8').read()
SK = json.load(open(O + 'character_skills.json'))
prm = lambda sid: SK[sid]['params']
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
C[1507]['x'] = dict(C[1507]['x'], skHp1=True, cntHp1=True)
C[1205]['x'] = dict(C[1205]['x'], lossAcc=[90, 50, 25])
C[1507]['notes'] = [n for n in C[1507].get('notes', []) if '生命值大于 1' not in n] + ['当前生命值 ≤1 时无法施放战技（自动改用强化普攻），充能满了也要等生命值回到 1 点以上才施放额外战技（受到治疗后马上触发）']
put(m, DB)

m, DMG = grab('DMG')
r4 = lambda v: round(v, 4)
b, b2, u, f = prm('1120501'), prm('1120508'), prm('1120503'), prm('1120504')
d = DMG['1205']
d['b'] = dict(d['b'], v=[r4(x[0]) for x in b], stat='hp', n='支离剑（强化版）')
d['b2'] = dict(d['b2'], v=[r4(x[1]) for x in b2], adj=[r4(x[2]) for x in b2], stat='hp', tg=2, n='无间剑树（强化版）')
d['u'] = dict(d['u'], v=[r4(x[0]) for x in u], adj=[r4(x[2]) for x in u], lm=[r4(x[4]) for x in u], la=[r4(x[5]) for x in u], e1=1.5, stat='hp', tg=2, n='大辟万死（强化版）')
d['f'] = dict(d['f'], v=[r4(x[1]) for x in f], stat='hp', n='倏忽恩赐（强化版）')
put(m, DMG)

m, XR = grab('XR')
XR['1205'] = [x for x in XR['1205'] if x.get('k') != 'e1']
put(m, XR)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
