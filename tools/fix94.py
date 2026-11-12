"""tv 94：对照 4.7 正式数据（StarRailRes info.json = 4.7.0）。角色 / 光锥 / 遗器没有新增（星神★阿哈和欢愉万相之前已按前瞻做了，倍率与正式数据一致）；
补 4.7 光锥、位面饰品里没做完的效果。新：伤害增益条件 ec.elN（按队里欢愉命途角色数倍乘）、ec.has（队里有这个角色）；效果条件 mel（装备者卡片欢愉度 ≥X%）。
用法：python3 tools/fix94.py index.html <4.7 官方 json 目录>"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 94, sys.argv[2])
F.rep('''      if (x.ms) e.ms = x.ms;''', '''      if (x.ms) e.ms = x.ms; if (x.mel) e.mel = x.mel;''')
F.rep('''      if (eff.ms && !eff.dyn && src && spdOf(src) < num(eff.ms)) return;''', '''      if (eff.mel && src && num(src.el, 0) < num(eff.mel)) return;   // 装备者卡片欢愉度门槛
      if (eff.ms && !eff.dyn && src && spdOf(src) < num(eff.ms)) return;''')
F.rep('''      if (c.pcd != null && num(u.cd, 50) < num(c.pcd) - 1e-9) return 0;''', '''      if (c.pcd != null && num(u.cd, 50) < num(c.pcd) - 1e-9) return 0;
      if (c.has && !U.some(z => z.kind === "ally" && !z.sm && !z.gone && String((tplOf(z) || {}).id) === String(c.has))) return 0;   // 队里有这个角色
      if (c.elN != null) { f0 *= Math.min(num(c.elN), U.filter(z => z.kind === "ally" && !z.sm && z.elation).length); if (!(f0 > 0)) return 0; }   // 按队里「欢愉」命途角色数''')
F.rep('''    if (c.pcd != null) L.push(`暴击伤害 ≥${c.pcd}% 时`);''', '''    if (c.pcd != null) L.push(`暴击伤害 ≥${c.pcd}% 时`);
    if (c.has) L.push("队里有对应角色时");
    if (c.elN != null) L.push(`按队里「欢愉」命途角色数（最多 ${c.elN} 名）`);''')
F.rep('''    if (e.alv) h.push("施加者倒下时消失");''', '''    if (e.alv) h.push("施加者倒下时消失");
    if (num(e.mel) > 0) h.push(`装备者欢愉度 ≥${num(e.mel)}% 时`);''')
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8')); RS = json.load(open(sys.argv[2] + '/relic_sets.json', encoding='utf-8'))
L = {x['id']: x for x in F.DB['lcs']}; R = {x['id']: x for x in F.DB['relics']}
P = lambda i, k: [r4(p[k] * 100) for p in LR[str(i)]['params']]
F.has(LR['22009']['desc'], '队伍中每有1名「欢愉」命途的角色，使装备者的暴击伤害提高#1[i]%，星神★阿哈在场时，装备者的暴击伤害额外提高#2[i]%')
L[22009]['eff'] = [dict(y='dbuf', t='start', tg='self', m='cd', v=P(22009, 0), d=0, bk='lc', ec={'elN': 4}, n='光锥：队伍中每有 1 名「欢愉」命途的角色，暴击伤害提高'),
                   dict(y='dbuf', t='start', tg='self', m='cd', v=P(22009, 1), d=0, bk='lc2', ec={'has': 1511}, n='光锥：星神★阿哈在场时暴击伤害额外提高')]
F.has(LR['23065']['desc'], '对我方其他单体施放战技时，获得#2[i]个笑点，该效果每间隔#3[i]回合最多触发1次，随后使我方全体在本场战斗中造成伤害时无视敌方目标#4[i]%的防御力，该效果无法叠加')
p = L[23065]['eff'][0]; assert p['y'] == 'punch' and p['v'] == [int(x[1]) for x in LR['23065']['params']]
p.update(t='skill', cdt=1, n='即兴巡演：对我方其他单体施放战技时获得笑点（每回合最多 1 次；战技不是对队友放的就关掉）'); p.pop('off', None)
L[23065]['eff'] = [p, dict(y='dbuf', t='skill', tg='team', m='defIg', v=P(23065, 3), d=0, bk='lc', n='即兴巡演：之后我方全体本场战斗造成伤害时无视目标防御力（不叠加）')]
assert RS['329']['desc'][0] == '使装备者的速度提高6%。当装备者的欢愉度大于等于40%时，进入战斗时立刻使行动提前40%。'
R[329]['p2']['eff'] = [dict(y='advance', t='start', tg='self', v=40, mel=40, n='2件：装备者欢愉度 ≥40% 时，进入战斗时行动提前 40%（按卡片上的欢愉度）')]
assert '当装备者的速度大于等于145时，进入战斗后使我方全体击破特攻提高18%' in RS['330']['desc'][0]
R[330]['p2']['eff'] = [dict(y='dbuf', t='start', tg='team', m='be', v=18, d=0, ms=145, bk='r330', n='2件：装备者速度 ≥145 时，进入战斗后我方全体击破特攻提高 18%（不叠加）')]
F.DB['ver'] = '4.7.0'
F.finish('对照 4.7 正式数据', '''<li><b>2026-11-12（4.7）</b>：tv 94（tools/fix94.py）。对照 4.7 正式数据：没有新增角色、光锥、遗器（星神★阿哈、欢愉万相和两把光锥、两套位面饰品之前已按前瞻数据做进来，阿哈的技能倍率与正式数据一致）。补完 4.7 装备的效果：在世界尽头相会吧！（按队里欢愉角色数加暴伤，阿哈在场再加）、当第一声「阿哈」响起（对队友放战技得笑点、之后全队无视防御）、神的瞬息欢愉（欢愉度 ≥40% 自动行动提前 40%）、亚空异容所（原来错写成加速，改成速度 ≥145 时全队击破特攻 +18%）。数据版本号改为 4.7.0。</li>''',
'''2026-11-12：对照 4.7 —— tv 94（tools/fix94.py）。新：ec.elN / ec.has、效果条件 mel。
  未改 / 存疑：只对照了角色 / 光锥 / 遗器名单、阿哈的伤害倍率和这 4 件装备；阿哈的其余机制（愿力、欢愉负债、升格）没有逐条重新对照正式文本''')
s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX94); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX94); for (const u of s.units) if (u.kind === "ally" && !u.sm && (u.lc === 22009 || u.lc === 23065 || u.rP === 329 || u.rP === 330)) applyEquip(u); } finally { S = keep; } }   // 4.7 的光锥 / 位面饰品')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
