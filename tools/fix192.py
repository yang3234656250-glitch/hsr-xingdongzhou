"""tv 192（2026-11-27）：差异清单第 66 批（开拓者 + 光锥 灼尽炼狱的新骸）
1. 开拓者•欢愉 8009 / 8010 终结技（800903 / 801003）“若目标不拥有欢愉技，使其行动提前#3[i]%”：
   #3 在 10 级、12 级都是 0.5（升级的是 #1 暴伤 50% → 54%），页面行动提前写了 lv [5, 54]，5 魂起变成 54%。去掉 lv。
2. 开拓者•记忆 8007 / 8008 忆灵天赋伙伴！一起！（1800703）“迷迷#1%暴击伤害+#2%”：6 级 [0.12, 0.24]，
   3 魂忆灵天赋 +1 级 → 7 级 [0.132, 0.264]。页面 3 魂只换了比例（lv [3, 13.2]），固定部分 hf 仍 24 → 补 lx flat [24, 26.4]。
3. 开拓者•毁灭 8001 / 8002：
   天赋牵制盗垒（800104）“每次击破敌方目标的弱点后，攻击力提高#1%”主语是开拓者自己 → 加 bby（只算自己击破的），
   行迹坚韧（“天赋的效果每层同时使防御力提高”）同样；E6“消灭敌方目标时也会触发天赋”本来就是 kill（只算自己消灭的），不动。
   E2（800102）“施放攻击后，若击中的敌方目标弱点为物理属性，则回复 5% 攻击力的生命值”：以前默认关，改成 ewl 物（按主目标弱点）、默认开。
   E4（800104 星魂）“击中处于弱点击破状态的敌方目标时，暴击率提高25%”：以前是常驻 +25% 默认关，改成 ec brk（按受到攻击的敌人是否破韧）、默认开。
4. 光锥 灼尽炼狱的新骸 23059“装备者回合开始时，固定恢复#2点能量，该效果每个波次可触发1次”：页面每回合都 +20，
   改成 first（每场 1 次；页面只有一个波次）。老存档：装备了的卡片 applyEquip，旧“淬炼”开关状态带到新条目。
   【炼狱】（敌方受到的暴击伤害提高）仍按我方全体暴伤，没改（留在清单里）。

用法：python3 tools/fix192.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 192
F = Fix(sys.argv[1], TV, sys.argv[2])
LR = json.load(open(os.path.join(sys.argv[2], 'light_cone_ranks.json'), encoding='utf-8'))

def chg(cid, e, newn):
    fx = F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
    on = e['n']; t = [t for n, t in F.OLD[cid] if n == on]; assert len(t) == 1, on
    fx['drop'].append(on); fx['trig'][on] = t[0]; fx['map'][on] = newn; e['n'] = newn
    fx['add'].append(newn); fx['keep'] = 1

# ---------- 1. 开拓者•欢愉 ----------
for cid, sid in ((8009, '800903'), (8010, '801003')):
    F.has(sid, '若目标不拥有欢愉技，使其行动提前#3[i]%')
    p10, p12 = F.prm(sid, 10), F.prm(sid, 12)
    assert p10[2] == 0.5 and p12[2] == 0.5 and p10[0] == 0.5 and round(p12[0], 4) == 0.54, (p10, p12)
    e = F.eff(cid, '终结技：目标没有欢愉技时行动提前 50%')
    assert e['y'] == 'advance' and e['v'] == 50 and e['lv'] == [5, 54.0], e
    del e['lv']
    chg(cid, e, '终结技：目标没有欢愉技时行动提前 50%（各级都是 50%）')

# ---------- 2. 开拓者•记忆 ----------
for cid, rk in ((8007, '800703'), (8008, '800803')):
    F.has('1800703', '提高数值等同于迷迷#1[f1]%暴击伤害+#2[f1]%')
    assert F.prm('1800703', 6) == [0.12, 0.24] and [round(x, 4) for x in F.prm('1800703', 7)] == [0.132, 0.264]
    assert any(x['id'] == '1800703' and x['num'] == 1 for x in F.RK[rk]['level_up_skills'])
    e = F.eff(cid, '忆灵天赋：迷迷在场时我方全体暴击伤害')
    assert e['lv'] == [3, 13.2] and e['hf'] == 24 and 'lx' not in e, e
    e['lx'] = {'flat': [24, 26.4]}
    chg(cid, e, '忆灵天赋：迷迷在场时我方全体暴击伤害 +迷迷暴击伤害的 12% + 24%（按开拓者面板暴伤算；3 魂 13.2% + 26.4%）')

# ---------- 3. 开拓者•毁灭 ----------
for cid, pre in ((8001, '8001'), (8002, '8002')):
    F.has(pre + '04', '每次击破敌方目标的弱点后，攻击力提高#1[i]%，该效果最多叠加#2[i]层')
    assert F.prm(pre + '04', 10) == [0.2, 2] and F.prm(pre + '04', 12) == [0.22, 2]
    F.hast(cid, '坚韧', '天赋的效果每层同时使开拓者的防御力提高#1[i]%')
    F.has('r:' + pre + '02', '施放攻击后，若击中的敌方目标弱点为物理属性，则回复等同于开拓者5%攻击力的生命值')
    F.has('r:' + pre + '04', '击中处于弱点击破状态的敌方目标时，暴击率提高25%')
    t = F.eff(cid, '天赋牵制盗垒：每次击破弱点攻击力 +20%，最多 2 层')
    assert t['t'] == 'break' and 'bby' not in t; t['bby'] = 1
    chg(cid, t, '天赋牵制盗垒：每次击破弱点攻击力 +20%，最多 2 层（只算自己击破的）')
    j = F.eff(cid, '行迹坚韧：天赋的效果每层同时使防御力 +10%')
    assert j['t'] == 'break' and 'bby' not in j; j['bby'] = 1
    chg(cid, j, '行迹坚韧：天赋的效果每层同时使防御力 +10%（只算自己击破的）')
    e2 = F.eff(cid, 'E2 因缘假合的人身', 2)
    assert e2['y'] == 'heal' and e2.get('off') == 1 and 'ewl' not in e2
    del e2['off']; e2['ewl'] = '物'
    e2['n'] = 'E2 因缘假合的人身：施放攻击后若击中的敌人弱点为物理属性，回复 5% 攻击力（按主目标有没有物理弱点判断，默认开启；没放敌人卡时不触发）'
    e4 = F.eff(cid, 'E4：击中弱点击破状态的敌人时暴击率', 4)
    assert e4['m'] == 'cr' and e4.get('off') == 1 and 'ec' not in e4
    del e4['off']; e4['ec'] = {'brk': 1}
    e4['n'] = 'E4 凝眸毁灭的瞬间：击中处于弱点击破状态的敌人时暴击率 +25%（按受到攻击的敌人是否处于击破状态，默认开启）'
    F.touch(cid)

# ---------- 4. 灼尽炼狱的新骸 ----------
d = LR['23059']['desc']; assert '装备者回合开始时，固定恢复#2[i]点能量，该效果每个波次可触发1次' in d
assert all(p[1] == 20 for p in LR['23059']['params'])
L = {l['id']: l for l in F.DB['lcs']}
q = [x for x in L[23059]['eff'] if x.get('n') == '淬炼']; assert len(q) == 1; q = q[0]
assert q['y'] == 'energy' and q['t'] == 'turn' and q['v'] == 20 and 'first' not in q
q['first'] = 1
q['n'] = '光锥淬炼：装备者回合开始时固定恢复 20 点能量（每个波次 1 次，页面按每场 1 次）'

log = """<li><b>2026-11-27（差异清单第 66 批）：tv 192（tools/fix192.py）</b>。按官方原文（Mar-7th StarRailRes character_skills / character_ranks / character_skill_trees / light_cone_ranks）：① <b>开拓者•欢愉</b>终结技“若目标不拥有欢愉技，使其行动提前 50%”：这个 50% 在 10 级、12 级都不变（5 魂升级的是暴伤 50% → 54%），以前 5 魂起写成 54%，改回 50%。② <b>开拓者•记忆</b>忆灵天赋伙伴！一起！“迷迷 12% 暴击伤害 + 24%”3 魂（7 级）是 13.2% + 26.4%，以前固定部分没升（仍 24%）。③ <b>开拓者•毁灭</b>天赋牵制盗垒“每次击破敌方目标的弱点后攻击力提高 20%”和行迹坚韧的防御力：改成只算开拓者自己击破的（以前队友击破也叠）；E2“施放攻击后若击中的敌方目标弱点为物理属性，回复 5% 攻击力”按主目标有没有物理弱点自动判断、默认开（以前默认关）；E4“击中处于弱点击破状态的敌方目标时暴击率 +25%”按受到攻击的敌人是否破韧、默认开（以前常驻 +25% 默认关）。④ 光锥<b>灼尽炼狱的新骸</b>“装备者回合开始时固定恢复 20 点能量，<b>该效果每个波次可触发 1 次</b>”：以前每个回合都 +20，现在每场 1 次（页面只有一个波次）。<b>对已有配置</b>：装了灼尽炼狱的新骸的角色从第 2 个回合起每回合少 20 能量，开大会变晚 / 变少；开拓者•欢愉 5 魂以上对非欢愉角色开大时拉条 54% → 50%；其余只影响伤害显示（开拓者•毁灭 E2 的回复会改变当前生命值）。</li>"""
record = """2026-11-27（差异清单第 66 批）：tv 192（tools/fix192.py）。开拓者•欢愉终结技行动提前去掉 lv（各级 50%）；开拓者•记忆迷迷暴伤 lx flat [24, 26.4]；开拓者•毁灭天赋 / 坚韧加 bby，E2 ewl 物默认开，E4 ec brk 默认开；光锥 23059 淬炼 first。"""
F.finish('差异清单第 66 批（开拓者欢愉拉条、记忆 3 魂迷迷、毁灭天赋 / E2 / E4、灼尽炼狱的新骸）', log, record)
p = sys.argv[1]; s = open(p, encoding='utf-8', newline='').read()
a0 = f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}'
assert s.count(a0) == 1
s = s.replace(a0, f'function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ const w0 = new Map(); for (const u of s.units) if (u.kind === "ally" && !u.sm && +u.lc === 23059) {{ const was = (u.effects || []).find(e => e.eq === "lc" && e.note === "淬炼"); w0.set(u, !!(was && was.off)); }} fixTpl(s, TPLFIX{TV}); for (const [u, off] of w0) {{ applyEquip(u); if (off) for (const e of u.effects) if (e.eq === "lc" && /^光锥淬炼：/.test(e.note || "")) e.off = true; }} }} finally {{ S = keep; }} }}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done tv', TV)
