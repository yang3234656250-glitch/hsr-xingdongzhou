"""tv 154（2026-11-23）：差异清单第 30 批（用户：“开始优化差异清单上的东西吧”）
1. 队友给的能量不进【火种】/【新蕊】/【追忆】/ 残梦 / 飞黄 / 愿力（noStdE 的角色）：
   能量效果（固定 / 按充能效率 / 按能量上限 / 按负面效果数 …）的施放者不是目标自己（也不是目标自己的召唤物）时不加能量数值，
   改成触发目标身上的新触发 eGet「受到队友提供的能量恢复时」。“回满”（昔涟激活全体终结技，用户确认回满）不变。
   白厄（1408）行迹身承炎炬万千（1408102）后半“受到队友提供的能量恢复的技能效果时，获得 1 点【火种】”用它补上。
2. “敌方目标进入战斗时 / 入场时”的效果从 t start（开局按 1 个敌人一次）改成 t eIn（tv 150：每个敌人各 1 次，之后登场 / 重新登场的也算），
   目标 enemies → evt（进场的那个敌人；没放敌人卡时挂在虚拟敌人上，和以前一样）：
   黄泉 E4（130804）和 E6 的两条“吃 E4”、翡翠行迹逆回购（+1 层【当品】）、黑天鹅【强化版】行迹杯底端倪（防御降低 / 1 层【奥迹】）、
   银狼LV.999 E6（150606【禁限弱点】）、大丽花 E2（132102【败谢】防御降低 / 共舞者弱点）、那刻夏 E2（140502 抗性降低）。
   大丽花 E2 前半“大丽花在场时，敌方全体全属性抗性降低 20%”是光环，保持开局挂给敌方全体。
   大黑塔天赋“敌方目标进入战斗时施加 1 层【解读】”：登场 / 重新登场的敌人清掉旧层数再给 1 层（引擎，reviveEnemy）。
3. 翡翠 E6（131406）后半“同时翡翠获得【收债人】状态”：场上有【收债人】时，翡翠自己攻击也带【收债人】的 25% 附加伤害（rx jade，出手时判断），
   并按天赋“【收债人】施放攻击后每击中 1 名敌方目标翡翠获得 1 点充能”给自己充能。
4. 行迹面板文字（TRACE 的额外能力）按官方 character_skill_trees 重新生成：参数带 % 的一律 ×100（以前 ≥1 的被当成小数：100% → 1%），
   有强化版的角色显示强化版行迹（同名取强化版节点）。只影响面板文字。

用法：python3 tools/fix154.py index.html <官方 json 目录>
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 154
F = Fix(sys.argv[1], TV, sys.argv[2])


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


def swap(cid, oldn, oldt, newn):
    fx = fix_of(cid)
    fx['drop'].append(oldn); fx['trig'][oldn] = oldt; fx['map'][oldn] = newn; fx['add'].append(newn); fx['keep'] = 1


# ---------------- 1. 队友回能不进特殊资源 + 触发 eGet ----------------
F.hast(1408, '身承炎炬万千', '受到队友提供的能量恢复的技能效果时，获得#点【火种】')
F.rep('        if (eff.type === "energy") {\n          curWhy = `${src && src !== tg ? src.name + "：" : ""}${eff.note || "回能效果"}`;\n',
      '        if (eff.type === "energy") {\n'
      '          if (eff.mode !== "zero" && tg.kind === "ally" && src && src !== tg && (ownerOf(src) || src) !== tg && noStdE(tg)) { healFor(tg, "eGet"); continue; }   // 火种 / 新蕊 / 追忆 / 残梦这类不是能量：队友给的能量不加数值，触发“受到队友提供的能量恢复时”（白厄身承炎炬万千 +1 火种，tv 154）\n'
      '          curWhy = `${src && src !== tg ? src.name + "：" : ""}${eff.note || "回能效果"}`;\n')
F.rep('["cntUp", "计数增加后"]', '["cntUp", "计数增加后"], ["eGet", "受到队友提供的能量恢复时"]', 2)
F.rep('cntUp: "计数增加后",', 'cntUp: "计数增加后", eGet: "受到队友提供的能量恢复时",')
bai = F.C[1408]
NB = '行迹身承炎炬万千：受到队友提供的能量恢复的技能效果时获得 1 点【火种】（队友给的能量本身不算火种）'
assert not any(e.get('n') == NB for e in bai['eff'])
i = [k for k, e in enumerate(bai['eff']) if e.get('n', '').startswith('行迹行向世界终点：变身结束')][0]
bai['eff'].insert(i + 1, {'y': 'energy', 't': 'eGet', 'tg': 'self', 'v': 1, 'm': 'fixed', 'n': NB})
fix_of(1408)['add'].append(NB)

# ---------------- 2. 进入战斗时：start → eIn ----------------
F.has('r:130804', '在敌方目标进入战斗时，使其陷入终结技伤害易伤状态')
F.has('r:150606', '敌方目标进入战斗时，会被植入【禁限弱点】')
F.has('r:132102', '敌方目标入场时，立即陷入【败谢】状态，持续#回合')
F.has('r:140502', '敌方目标入场时，触发#次天赋的弱点添加效果，并使其全属性抗性降低20%')
F.hast(1314, '逆回购', '敌方目标进入战斗时')
F.hast(1307, '杯底端倪', '敌方目标进入战斗时，有#的基础概率陷入#层【奥迹】，并且有#的基础概率陷入战技的防御力降低效果')


def to_ein(e, note=None):
    assert e['t'] == 'start' and e['tg'] == 'enemies', e
    e['t'] = 'eIn'; e['tg'] = 'evt'
    if note: e['n'] = note


# 星魂（迁移时 applyEquip 重建）
for cid, r, bk in [(1308, 4, 'e4'), (1308, 6, 'e6v4b'), (1308, 6, 'e6v4s'), (1506, 6, 'jx'), (1405, 2, 'e2')]:
    z = [x for x in F.eid(cid, r)['eff'] if x.get('bk') == bk]; assert len(z) == 1, (cid, bk)
    to_ein(z[0])
F.eff(1308, 'E4：敌人受到的终结技伤害 +8%', 4)['n'] = 'E4：敌方目标进入战斗时陷入终结技易伤，受到的终结技伤害 +8%（每个敌人进场时各挂一次）'
F.eff(1405, 'E2：敌人入场时全属性抗性 −20%', 2)['n'] = 'E2：敌方目标入场时全属性抗性 −20%（每个敌人进场时各挂一次）'
dz = [x for x in F.eid(1321, 2)['eff'] if x.get('bk') == 'bx']; assert len(dz) == 2
for x in dz:
    to_ein(x)
    x['n'] = x['n'].replace('，持续 3 回合', '，持续 3 回合（每个敌人入场时各一次）')
# 基础效果（按说明换掉，开关保留）
for cid, frag in [(1314, '行迹逆回购：敌方目标进入战斗时获得 1 层【当品】'), (1307, '行迹杯底端倪：敌方目标进入战斗时陷入战技的防御力降低效果'), (1307, '行迹杯底端倪：敌方目标进入战斗时陷入 1 层【奥迹】')]:
    e = F.eff(cid, frag); oldn = e['n']
    if cid == 1314:
        assert e['t'] == 'start' and e['tg'] == 'self'
        e['t'] = 'eIn'; e['n'] = '行迹逆回购：敌方目标进入战斗时获得 1 层【当品】（每个敌人进场时各 1 层，之后登场 / 重新登场的也算；没放敌人卡按 1 个）'
    else:
        to_ein(e, oldn.replace('敌方目标进入战斗时', '敌方目标进入战斗时（每个敌人进场时各一次）', 1))
    swap(cid, oldn, 'start', e['n'])
# 大黑塔：登场 / 重新登场的敌人重新给 1 层【解读】
F.has('140104', '敌方目标进入战斗时，大黑塔对其施加#层【解读】')
F.rep('      fireAll("eIn", en);   // 敌方目标进入战斗时（登场 / 重新登场；银枝慷慨）\n',
      '      if (HT) { en.jd = 0; jdAdd(en, 1); }   // 大黑塔天赋：敌方目标进入战斗时施加 1 层【解读】（重新登场的是新敌人，旧层数不带，tv 154）\n'
      '      fireAll("eIn", en);   // 敌方目标进入战斗时（登场 / 重新登场；银枝慷慨）\n')

# ---------------- 3. 翡翠 E6 后半 ----------------
F.has('r:131406', '同时翡翠获得【收债人】状态')
e6 = F.eid(1314, 6)
assert not any(x.get('bk') == 'rxe6' for x in e6['eff'])
e6['eff'] += [
    {'y': 'dbuf', 't': 'start', 'tg': 'self', 'm': 'rx', 'v': 1, 'sc': 'jade', 'd': 0, 'bk': 'rxe6', 'ec': {'tst': '收债人'},
     'n': 'E6：场上有【收债人】时翡翠也是【收债人】：翡翠攻击后对每个击中的敌方目标造成 25% 攻击力的附加伤害（出手时判断）'},
    {'y': 'count', 't': 'atk', 'aw': 'self', 'ph': 1, 'tg': 'self', 'v': 1, 'ns': '收债人', 'so': 'team',
     'n': 'E6：场上有【收债人】时翡翠自己施放攻击后，每击中 1 名敌方目标也获得 1 点充能（按敌人卡数量）'},
]

# ---------------- 4. 行迹面板文字 ----------------
TRJ, CHJ = F.TR, F.CH
fmt = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')


def sub(desc, ps):
    desc = re.sub(r'<[^>]+>', '', desc)
    return re.sub(r'#(\d+)\[(i|f\d)\](%?)', lambda m: fmt(ps[int(m.group(1)) - 1] * 100) + '%' if m.group(3) == '%' else fmt(ps[int(m.group(1)) - 1]), desc)


m = re.search(r'  const TRACE = (\{.*?\});\n', F.s)
T = json.loads(m.group(1)); nch = 0
for cid, ent in T.items():
    if cid not in CHJ: continue
    d = {}
    for t in CHJ[cid]['skill_trees']:   # 同名取后面的（强化版）
        x = TRJ[t]
        if x.get('desc') and x.get('max_level') == 1: d[x['name']] = re.sub(r'\s+', ' ', sub(x['desc'], (x.get('params') or [[]])[0])).strip()
    for row in ent['m']:
        if row[0] in d and d[row[0]] != re.sub(r'\s+', ' ', row[1]).strip(): row[1] = d[row[0]]; nch += 1
assert 50 <= nch <= 70, nch
assert T['1015']['m'][[r[0] for r in T['1015']['m']].index('守护者')][1].count('120%')
F.s = F.s[:m.start(1)] + json.dumps(T, ensure_ascii=False, separators=(',', ':')) + F.s[m.end(1):]
print('TRACE 改了', nch, '条')

log = """<li><b>2026-11-23（差异清单第 30 批）：tv 154（tools/fix154.py）</b>。依据官方原文（Mar-7th character_skill_trees / character_ranks）。① <b>队友给的能量不再算进【火种】【新蕊】【追忆】、残梦、飞黄、愿力</b>：这些都不是能量，以前停云开大给白厄时火种 3 → 15 直接满。现在别人给的回能对它们不加数值，改为触发新的“受到队友提供的能量恢复时”；<b>白厄</b>行迹身承炎炬万千“受到队友提供的能量恢复的技能效果时，获得 1 点【火种】”用它补上（以前没做）。昔涟“激活全体终结技”的回满不变。② <b>“敌方目标进入战斗时 / 入场时”</b>按每个敌人各一次、之后登场 / 重新登场的敌人也算（以前只在开局挂一次）：黄泉 E4（终结技易伤 8%，含 E6 两条）、翡翠逆回购（+1 层【当品】）、黑天鹅杯底端倪（防御降低、1 层【奥迹】）、银狼LV.999 E6【禁限弱点】、大丽花 E2【败谢】、那刻夏 E2，大黑塔重新登场的敌人重新给 1 层【解读】。③ <b>翡翠 E6</b>“同时翡翠获得【收债人】状态”：场上有【收债人】时翡翠自己的攻击也带 25% 附加伤害、也按击中敌人数充能。④ <b>行迹面板文字</b>：60 条额外能力按官方数据重写（以前 100% 显示成 1%、0.5% 显示成 0.0%，强化版角色显示的是原版行迹）。<b>对已有配置</b>：队里有白厄 / 遐蝶 / 昔涟 / 黄泉 / 飞霄 / 星神★阿哈且队友会给他们回能的方案，他们的开大时机会变（不再被队友直接充满）；有敌人重新登场（喜剧学家这类）时上面那些进场效果多挂几次；只有一个波次的普通方案行动顺序不变。卡片上逆回购 / 杯底端倪按新说明换掉（开关保留），星魂效果重建。</li>"""

record = """2026-11-23（差异清单第 30 批）：tv 154（tools/fix154.py）。改：energy 对 noStdE 目标（施放者不是自己 / 自己的召唤物）不加数值，触发新触发 eGet；白厄身承炎炬万千 eGet +1 火种；进战效果 start → eIn + tg evt（黄泉 E4 / E6、翡翠逆回购、黑天鹅杯底端倪 ×2、银狼LV.999 E6、大丽花 E2 ×2、那刻夏 E2）；reviveEnemy 给大黑塔【解读】1 层；翡翠 E6 rx jade（ec tst 收债人）+ 自己攻击充能；TRACE 额外能力文字重生成。
  没改：大丽花 E2 前半（在场光环，开局给全体）；黑天鹅 E1 四条开局常驻（重新登场的敌人没有）；进战效果在开局 start 效果之后触发（进战秘技伤害吃不到）。"""

F.finish('差异清单第 30 批（队友回能不进火种 / 新蕊、进战效果按每个敌人、翡翠 E6、行迹面板文字）', log, record)
print('done tv', TV)
