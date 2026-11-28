"""tv 193（2026-11-28）：差异清单第 67 批（光锥 献给明日的色彩、欢愉满溢祝福、金血铭刻的时代、理想燃烧的地狱）
官方原文和参数：Mar-7th StarRailRes index_new/cn/light_cone_ranks.json（参数 params[叠影-1]）。

1. 献给明日的色彩 23055“……为装备者固定恢复#2[i]点能量，并为我方全体回复等同于装备者防御力#5[i]%的生命值”：
   #2 五档都是 10。页面回能那条 v 写成 [10, 12.5, 15, 17.5, 20]（抄了 #5 那一列），改成 10；
   另一条同样数值、默认关的重复回能（“挥墨（对我方全体施放欢愉技时）”）删掉。回复（#5 10%～20%）、易伤（#4 22%～44%，3 回合）核对无误。
2. 欢愉满溢祝福 24006“当装备者对我方单体角色施放战技或终结技后，使目标欢愉度提高#2[i]%，持续#3[i]回合”：
   以前一条 skill 或 ult、目标 ultpick（战技那次也给大招目标）；拆成两条：战技 → skpick（卡片“每次战技目标”）、终结技 → ultpick。
3. 金血铭刻的时代 23048“装备者对我方单体角色施放战技后，使目标造成的战技伤害提高#4[f1]%，持续#5[i]回合”：目标 $ally → skpick。
   施放终结技攻击后恢复 1 个战技点、#4 54%～108%、3 回合核对无误。
4. 理想燃烧的地狱 23046“进入战斗时，若我方的战技点上限大于等于#2[i]点，使装备者的攻击力提高#3[i]%”：
   以前默认关、要手动开；新条件 spg（字段 spGe：这场战斗的战技点上限 ≥N 才生效），默认开。
   战斗开始时带 spGe 的效果放在其他被动之后、进战自动施放之前生效（花火 / Archer / 远坂凛 / 花花世界迷人眼的战技点上限都是战斗开始时加的，
   这样不管队伍顺序都能看到加完的上限）。
老存档：装了这几把光锥的卡片 applyEquip；24006 / 23048 旧条目关着的，新条目也关着；23048 旧条目目标是别的队友而卡片没选过“每次战技目标”、
卡上也没有别的 skpick 效果时，把那个队友记成第 1 次战技的目标（之后沿用），结果不变。
用法：python3 tools/fix193.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 193
F = Fix(sys.argv[1], TV, sys.argv[2])
LR = json.load(open(os.path.join(sys.argv[2], 'light_cone_ranks.json'), encoding='utf-8'))
L = {l['id']: l for l in F.DB['lcs']}
col = lambda lid, k: [p[k] for p in LR[str(lid)]['params']]
r4 = lambda v: round(v * 100, 4)

# ---------- 1. 献给明日的色彩 ----------
d = LR['23055']['desc']
assert '装备者对我方全体施放欢愉技时，使敌方全体受到的伤害提高#4[i]%，持续#3[i]回合，为装备者固定恢复#2[i]点能量，并为我方全体回复等同于装备者防御力#5[i]%的生命值' in d, d
assert col(23055, 1) == [10] * 5 and [r4(x) for x in col(23055, 4)] == [10, 12.5, 15, 17.5, 20] and [r4(x) for x in col(23055, 3)] == [22, 27.5, 33, 38.5, 44] and col(23055, 2) == [3] * 5
E = L[23055]['eff']
en = [x for x in E if x['y'] == 'energy']; assert len(en) == 2, en
a = [x for x in en if x['n'] == '挥墨：欢愉技对我方全体施放时固定回能（真珠）']; b = [x for x in en if x['n'] == '挥墨（对我方全体施放欢愉技时）']
assert len(a) == 1 and len(b) == 1 and a[0]['v'] == [10, 12.5, 15, 17.5, 20] and b[0].get('off') == 1
a[0]['v'] = 10
E.remove(b[0])
h = [x for x in E if x['y'] == 'heal']; assert len(h) == 1 and h[0]['v'] == [10, 12.5, 15, 17.5, 20] and h[0]['m'] == 'def'
v = [x for x in E if x['y'] == 'dbuf']; assert len(v) == 1 and v[0]['v'] == [22, 27.5, 33, 38.5, 44] and v[0]['d'] == 3

# ---------- 2. 欢愉满溢祝福 ----------
d = LR['24006']['desc']; assert '当装备者对我方单体角色施放战技或终结技后，使目标欢愉度提高#2[i]%，持续#3[i]回合' in d, d
assert [r4(x) for x in col(24006, 1)] == [12, 15, 18, 21, 24] and col(24006, 2) == [2] * 5
E = L[24006]['eff']; assert len(E) == 1
o = E[0]; assert o['t'] == 'skill' and o['o'] == 'ult' and o['tg'] == 'ultpick' and o['m'] == 'el' and o['v'] == [12, 15, 18, 21, 24] and o['d'] == 2
N24S = '光锥：对我方单体施放战技后目标欢愉度提高，持续 2 回合（目标按“每次战技目标”）'
N24U = '光锥：对我方单体施放终结技后目标欢愉度提高，持续 2 回合（目标按“每次大招目标”）'
OLD24 = o['n']
s1 = dict(o); del s1['o']; s1['tg'] = 'skpick'; s1['n'] = N24S
u1 = dict(o); u1['t'] = 'ult'; del u1['o']; u1['n'] = N24U
L[24006]['eff'] = [s1, u1]

# ---------- 3. 金血铭刻的时代 ----------
d = LR['23048']['desc']; assert '施放终结技攻击后恢复#3[i]个战技点，装备者对我方单体角色施放战技后，使目标造成的战技伤害提高#4[f1]%，持续#5[i]回合' in d, d
assert col(23048, 2) == [1] * 5 and [r4(x) for x in col(23048, 3)] == [54, 67.5, 81, 94.5, 108] and col(23048, 4) == [3] * 5
q = [x for x in L[23048]['eff'] if x['y'] == 'dbuf']; assert len(q) == 1; q = q[0]
assert q['tg'] == '$ally' and q['t'] == 'skill' and q['sc'] == 's' and q['d'] == 3
OLD48 = q['n']; N48 = '光锥：对我方单体施放战技后目标战技伤害提高，持续 3 回合（目标按“每次战技目标”）'
q['tg'] = 'skpick'; q['n'] = N48

# ---------- 4. 理想燃烧的地狱 ----------
d = LR['23046']['desc']; assert '进入战斗时，若我方的战技点上限大于等于#2[i]点，使装备者的攻击力提高#3[i]%' in d, d
assert col(23046, 1) == [6] * 5 and [r4(x) for x in col(23046, 2)] == [40, 50, 60, 70, 80]
q = [x for x in L[23046]['eff'] if x.get('t') == 'start']; assert len(q) == 1; q = q[0]
assert q['m'] == 'atkP' and q.get('off') == 1 and 'spg' not in q
del q['off']; q['spg'] = 6
q['n'] = '光锥：进入战斗时若我方战技点上限 ≥6，攻击力提高（按这场战斗的战技点上限自动判断）'

# ---------- 引擎 ----------
F.rep('      if (x.mxe) e.minMaxE = x.mxe;   //', '      if (x.spg) e.spGe = x.spg;   // 这场战斗的战技点上限 ≥N 才生效（理想燃烧的地狱，tv 193）\n      if (x.mxe) e.minMaxE = x.mxe;   //')
F.rep('      if (eff.maxSP != null && eff.maxSP !== "" && sp > num(eff.maxSP)) return;',
      '      if (num(eff.spGe) > 0 && spMax < num(eff.spGe)) return;   // 战技点上限 ≥N 才生效（tv 193）\n      if (eff.maxSP != null && eff.maxSP !== "" && sp > num(eff.maxSP)) return;')
F.rep('      for (const [u, L] of S0) for (const e of L) if (!preEff(e) && e.type !== "cast") apply(e, u, u.color);\n',
      '      for (const [u, L] of S0) for (const e of L) if (!preEff(e) && e.type !== "cast" && !(num(e.spGe) > 0)) apply(e, u, u.color);\n'
      '      for (const [u, L] of S0) for (const e of L) if (!preEff(e) && e.type !== "cast" && num(e.spGe) > 0) apply(e, u, u.color);   // 看战技点上限的放在所有被动（含战技点上限 +N）之后（tv 193）\n')

log = """<li><b>2026-11-28（差异清单第 67 批）：tv 193（tools/fix193.py）</b>。按官方光锥原文和 5 档参数（Mar-7th StarRailRes light_cone_ranks）：① <b>献给明日的色彩</b>“对我方全体施放欢愉技时……为装备者固定恢复 10 点能量”：这个 10 五档都一样，以前回能写成 10 / 12.5 / 15 / 17.5 / 20（抄成了回复生命值的防御力 % 那一列），改成 10；另一条同样数值、默认关的重复回能删掉。② <b>欢愉满溢祝福</b>“对我方单体角色施放战技或终结技后，使目标欢愉度提高”：以前战技那次也给“每次大招目标”，拆成两条：战技按卡片“每次战技目标”、终结技按“每次大招目标”。③ <b>金血铭刻的时代</b>“对我方单体角色施放战技后，使目标造成的战技伤害提高”：目标从模板里的第一个队友改成“每次战技目标”。④ <b>理想燃烧的地狱</b>“进入战斗时，若我方的战技点上限 ≥6 点，攻击力提高 40%～80%”：以前默认关要手动开，现在按这场战斗的战技点上限自动判断、默认开（新条件 spGe；战斗开始时这类效果排在其他被动之后，花火 / Archer / 远坂凛 / 花花世界迷人眼加的上限都算进去）。<b>对已有配置</b>：装了献给明日的色彩 2～5 叠影的角色每次对全体施放欢愉技少回 2.5～10 点能量（1 叠影不变），开大可能变晚；其余三条只影响伤害显示（欢愉度 / 战技增伤给谁、理想燃烧的地狱的攻击力）。老存档自动迁移：旧条目关着的新条目也关着，金血铭刻的时代原来给的是哪个队友就记成第 1 次战技的目标。</li>"""
record = """2026-11-28（差异清单第 67 批）：tv 193（tools/fix193.py）。光锥 23055 回能 v 10、删重复条目；24006 拆成 skill → skpick / ult → ultpick；23048 $ally → skpick；23046 新条件 spg（spGe）默认开。"""
F.finish('差异清单第 67 批（献给明日的色彩回能、欢愉满溢祝福 / 金血铭刻的时代战技目标、理想燃烧的地狱战技点上限）', log, record)

p = sys.argv[1]; s = open(p, encoding='utf-8', newline='').read()
a0 = f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}'
assert s.count(a0) == 1
J = json.dumps
body = ('const LCS = [23055, 24006, 23048, 23046]; '
        'for (const u of s.units) { if (!(u.kind === "ally" && !u.sm && LCS.includes(+u.lc))) continue; '
        'const ef = u.effects || [], was = n => ef.find(e => e.eq === "lc" && e.note === n); '
        f'const o24 = was({J(OLD24, ensure_ascii=False)}), o48 = was({J(OLD48, ensure_ascii=False)}); '
        'const skOther = ef.some(e => !e.eq && e.target === "skpick"); '
        'if (o48 && o48.target && o48.target !== "skpick" && s.units.some(x => x.id === o48.target) && !skOther && !(Array.isArray(u.skTargets) && u.skTargets.some(Boolean))) u.skTargets = [o48.target]; '
        'applyEquip(u); '
        f'if (o24 && o24.off) for (const e of u.effects) if (e.eq === "lc" && (e.note === {J(N24S, ensure_ascii=False)} || e.note === {J(N24U, ensure_ascii=False)})) e.off = true; '
        f'if (o48 && o48.off) for (const e of u.effects) if (e.eq === "lc" && e.note === {J(N48, ensure_ascii=False)}) e.off = true; '
        '} ')
s = s.replace(a0, f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); {body}}} finally {{ S = keep; }} }}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done tv', TV)
