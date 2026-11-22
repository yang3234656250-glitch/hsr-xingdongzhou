"""tv 152（2026-11-22）：差异清单第 28 批（赛飞儿终结技倍率 / 追加攻击削韧、波提欧幽灵装填、翡翠 E6、缇宝 E4 秘技神启）
1. 赛飞儿 1406 终结技（官方 140603）：“对指定敌方单体造成等同于赛飞儿#1%攻击力的量子属性伤害。之后……
   并对指定敌方单体及其相邻目标造成等同于赛飞儿#4%攻击力的量子属性伤害……”
   主目标 = #1 + #4（10 级 120% + 40% = 160%），相邻 = #4（40%，DMGX.adj 里已有）。DMG 1406 u 以前只有 #1。
   （天赋记录值的真实伤害没做，仍记在差异清单。）
2. 赛飞儿 1406 天赋追加攻击削韧：官方 AvatarSkillConfig 140604 ShowStanceList [60, 0, 0]（游戏里 20 点）。
   TGH 1406 以前没有 f（生成削韧表时倍率表还没有赛飞儿的追加攻击），补 f = [60, 0, 0]；以后重跑 build_tgh.py 也会得到同样的值。
3. 波提欧 1315 行迹幽灵装填（官方 1315101）：“使自身暴击率/暴击伤害提高，提高数值等同于击破特攻的#1%/#3%，最多使暴击率/暴击伤害提高#2%/#4%。”
   参数 [0.1, 0.3, 0.5, 1.5]。以前按满额 30% / 150% 写（说明“没有击破特攻数值”，过时）；
   改成按卡片击破特攻算（ss "be"，暴击率 10% 最多 30%，暴击伤害 50% 最多 150%）。仍默认关：游戏面板里如果已经算进去就别开。
4. 翡翠 1314 E6（官方 131406）：“场上有【收债人】状态的角色时，翡翠量子属性抗性穿透提高20%，同时翡翠获得【收债人】状态。”
   以前开局常驻 +20%；新加伤害增益条件 ec.tst（任意在场的我方角色有这个状态，出手时判断），这条改成只在场上有【收债人】时生效。
   后半句“翡翠获得【收债人】状态”（自己攻击时的附加伤害 / 充能）仍只做了回合开始 +3 层【当品】，不改。
5. 缇宝 1403 E4（官方 140304）：“【神启】持续期间，我方全体造成伤害时无视目标18%的防御力。”
   秘技（140307）“进入战斗时获得【神启】，持续#1回合”以前只给抗性穿透；补一条战斗开始时的 E4 无视防御（默认关，和秘技那条一起开）。

用法：python3 tools/fix152.py index.html <官方 json 目录（含 AvatarSkillConfig.json）>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 152
F = Fix(sys.argv[1], TV, sys.argv[2])


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


def swap(cid, oldn, oldt, newn, mapto):
    fx = fix_of(cid)
    fx['drop'].append(oldn); fx['trig'][oldn] = oldt; fx['map'][oldn] = mapto; fx['add'].append(newn); fx['keep'] = 1


# ---------------- 1. 赛飞儿终结技倍率 ----------------
F.has('140603', '对指定敌方单体造成等同于赛飞儿#攻击力的量子属性伤害。之后，对指定敌方单体造成等同于当前天赋记录值#的真实伤害，并对指定敌方单体及其相邻目标造成等同于赛飞儿#攻击力的量子属性伤害')
P = F.SK['140603']['params']
U = F.DMG['1406']['u']
assert len(U['v']) == len(P) == 15 and all(abs(U['v'][i] - P[i][0]) < 1e-6 for i in range(15)), U['v']
assert not U['adj'] and U['tg'] == 2
DMGX = F.grab('DMGX')
assert all(abs(DMGX['adj']['1406']['u'][i] - P[i][3]) < 1e-6 for i in range(15))
U['v'] = [round(P[i][0] + P[i][3], 4) for i in range(15)]
assert abs(U['v'][9] - 1.6) < 1e-9

# ---------------- 2. 赛飞儿追加攻击削韧 ----------------
A = {str(r['SkillID']): r for r in json.load(open(sys.argv[2] + '/AvatarSkillConfig.json', encoding='utf-8')) if r.get('Level') == 1}
st = [int(round(x.get('Value', 0))) for x in A['140604']['ShowStanceList']]
assert st == [60, 0, 0], st
m = re.search(r'const TGH = (\{.*?\});', F.s)
TGH = json.loads(m.group(1))
assert 'f' not in TGH['1406'] and 'f' in F.DMG['1406']
TGH['1406']['f'] = st
F.s = F.s[:m.start(1)] + json.dumps(TGH, ensure_ascii=False, separators=(',', ':')) + F.s[m.end(1):]

# ---------------- 3. 波提欧幽灵装填 ----------------
F.hast(1315, '幽灵装填', '使自身暴击率/暴击伤害提高，提高数值等同于击破特攻的#/#，最多使暴击率/暴击伤害提高#/#')
assert F.TR['1315101']['params'][0] == [0.1, 0.3, 0.5, 1.5]
for frag, mm, v, cap, newn in [
        ('行迹幽灵装填：暴击率', 'cr', 10, 30, '行迹幽灵装填：暴击率提高，等同于击破特攻的 10%，最多 30%（按卡片击破特攻；游戏面板的暴击率里如果已经算进去就别开）'),
        ('行迹幽灵装填：暴击伤害', 'cd', 50, 150, '行迹幽灵装填：暴击伤害提高，等同于击破特攻的 50%，最多 150%（按卡片击破特攻；游戏面板的暴击伤害里如果已经算进去就别开）')]:
    e = F.eff(1315, frag)
    assert e['y'] == 'dbuf' and e['t'] == 'start' and e['m'] == mm and e['v'] == cap and e.get('off') == 1, e
    oldn = e['n']
    e.update({'v': v, 'ss': 'be', 'cap': cap, 'n': newn})
    swap(1315, oldn, 'start', newn, newn)

# ---------------- 4. 翡翠 E6 ----------------
F.has('r:131406', '场上有【收债人】状态的角色时，翡翠量子属性抗性穿透提高#，同时翡翠获得【收债人】状态')
e6 = F.eid(1314, 6)
z = [x for x in e6['eff'] if x['y'] == 'dbuf' and x.get('m') == 'resPen']
assert len(z) == 1 and z[0]['t'] == 'start' and z[0]['v'] == 20 and 'ec' not in z[0]
z[0]['ec'] = {'tst': '收债人'}
z[0]['n'] = 'E6：场上有【收债人】状态的角色时，翡翠量子属性抗性穿透 +20%（出手时判断）'

# 引擎：伤害增益条件 ec.tst = 任意在场的我方角色 / 忆灵有这个状态
F.rep('      if (c.has && !U.some(z => z.kind === "ally" && !z.sm && !z.gone && String((tplOf(z) || {}).id) === String(c.has))) return 0;   // 队里有这个角色\n',
      '      if (c.has && !U.some(z => z.kind === "ally" && !z.sm && !z.gone && String((tplOf(z) || {}).id) === String(c.has))) return 0;   // 队里有这个角色\n'
      '      if (c.tst && !U.some(z => z.kind === "ally" && !z.gone && hasSt(z, c.tst))) return 0;   // 场上有我方目标持有这个状态（翡翠 E6【收债人】，tv 152）\n')
F.rep('    if (c.has) L.push("队里有对应角色时");\n',
      '    if (c.has) L.push("队里有对应角色时");\n    if (c.tst) L.push(`场上有【${c.tst}】状态的我方目标时`);\n')

# ---------------- 5. 缇宝 E4（秘技进战的【神启】） ----------------
F.has('r:140304', '【神启】持续期间，我方全体造成伤害时无视目标#的防御力')
F.has('140307', '使用秘技后，进入战斗时获得【神启】，持续#回合')
tq = F.eff(1403, '秘技开心你就拍拍手')
assert tq['t'] == 'start' and tq['d'] == 3 and tq.get('off') == 1
e4 = F.eid(1403, 4)
assert len(e4['eff']) == 1 and e4['eff'][0]['t'] == 'skill' and e4['eff'][0]['m'] == 'defIg'
e4['eff'].append({'y': 'dbuf', 't': 'start', 'tg': 'team', 'm': 'defIg', 'v': 18, 'd': 3, 'bk': 'e4', 'off': 1,
                  'n': 'E4：秘技进入战斗时获得的【神启】期间，我方全体无视目标 18% 防御力（3 回合，和秘技那条一起开）'})

log = """<li><b>2026-11-22（差异清单第 28 批）：tv 152（tools/fix152.py）</b>。依据官方原文（Mar-7th character_skills / character_skill_trees / character_ranks）和 DimbreathBot AvatarSkillConfig。① <b>赛飞儿终结技</b>（140603）“对指定敌方单体造成 120% 攻击力……之后……对指定敌方单体及其相邻目标造成 40% 攻击力的量子属性伤害”：主目标倍率改成 120% + 40% = 160%（以前只算 120%），相邻 40% 不变；天赋记录值的真实伤害仍没做。② <b>赛飞儿天赋追加攻击削韧</b>：官方 140604 削韧 [60, 0, 0]（游戏里 20 点），以前削韧表没有这一项（追加攻击不削韧），补上。③ <b>波提欧行迹幽灵装填</b>（1315101）“暴击率 / 暴击伤害提高，数值等同于击破特攻的 10% / 50%，最多 30% / 150%”：以前按满额写，改成按卡片击破特攻算；仍默认关（游戏面板里如果已经算进去就别开）。④ <b>翡翠 E6</b>（131406）“场上有【收债人】状态的角色时，翡翠量子属性抗性穿透提高 20%”：以前开局一直有，新加伤害增益条件“场上有某状态的我方目标时”（ec.tst），出手时判断。⑤ <b>缇宝 E4</b>（140304）“【神启】持续期间，我方全体无视目标 18% 防御力”：以前只挂在战技上，补上秘技进战获得【神启】时的一条（默认关，和秘技那条一起开）。<b>对已有配置</b>：①③④⑤只影响伤害显示；② 放了有量子弱点的敌人卡时，赛飞儿的追加攻击会削韧，击破可能提前，行动顺序会变；没放敌人卡的行动顺序不变。老存档的波提欧两条按新说明换掉（开关保留），翡翠 / 缇宝的星魂效果重建。</li>"""

record = """2026-11-22（差异清单第 28 批）：tv 152（tools/fix152.py）。改：赛飞儿终结技主目标倍率 #1 + #4（DMG 1406 u）、追加攻击削韧 TGH 1406 f [60, 0, 0]；波提欧幽灵装填按击破特攻（ss be + cap，仍默认关）；翡翠 E6 抗性穿透加 ec.tst 收债人（新条件）；缇宝 E4 补秘技进战【神启】的无视防御（默认关）。
  核对无误：赛飞儿终结技相邻 40%（DMGX.adj）、战技 [60, 0, 30] / 终结技 [90, 0, 60] 削韧；缇宝 E4 战技那条。存疑：幽灵装填在游戏面板里是否已显示（默认关保留）。"""

F.finish('差异清单第 28 批（赛飞儿 / 波提欧 / 翡翠 E6 / 缇宝 E4）', log, record)
print('done tv', TV)
