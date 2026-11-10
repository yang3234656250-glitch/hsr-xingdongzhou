"""tv 57：全面校对第 1 批（灵砂 1222、三月七•巡猎 1224、忘归人 1225、银枝 1302），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix57.py index.html <官方 json 目录>
新功能：效果字段 perHit（DB ph：数值 × 这次攻击击中的敌人数，叠层的增益改成叠这么多层；敌人数按敌人卡，没放按 1 个）、
lifeCap（DB lfc：召唤物行动次数最多累计到几次）；开大记录带 eb / ec（开大前能量 / 这次扣的能量），银枝按它选两种终结技。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 57, sys.argv[2])
C, prm, has = F.C, F.prm, F.has

# ================= 引擎 =================
F.rep('if (eff.type === "life") { if (tg.sm && !tg.gone && num(tg.life) > 0) tg.life = num(tg.life) + Math.round(v); continue; }',
      'if (eff.type === "life") { if (tg.sm && !tg.gone && num(tg.life) > 0) { tg.life = num(tg.life) + Math.round(v); if (num(eff.lifeCap) > 0) tg.life = Math.min(Math.round(num(eff.lifeCap)), tg.life); } continue; }')
F.rep('      if (num(eff.hpGE) > 0 && eff.type !== "spd" && src && !hpOk(src, eff.hpGE)) return;',
      '''      if (eff.perHit && !phIn) {   // 每击中 1 个敌方目标：数值 × 这次攻击击中的敌人数；叠层的增益改成叠这么多层（tv 57）
        const n = hitN(evTarget && evTarget.kind === "ally" ? evTarget : src);
        if (n > 1 && (eff.type === "dbuf" || eff.type === "spd") && num(eff.stack) > 0) { phIn = true; try { for (let i = 1; i < n; i++) applyIn(eff, src, srcColor); } finally { phIn = false; } }
        else val *= n;
      }
      if (num(eff.hpGE) > 0 && eff.type !== "spd" && src && !hpOk(src, eff.hpGE)) return;''')
F.rep('    const applyIn = (eff, src, srcColor) => {\n',
      '''    // 这次攻击击中几个敌人（每击中 1 个敌方目标 …）：按行动者这次用的技能的目标类型和敌人卡数量；没放敌人卡按 1 个
    let phIn = false;
    const hitN = a => {
      const who = a && a.sm ? byId[a.sm.owner] || a : a, N = U.filter(x => x.kind === "enemy" && !x.gone).length || 1;
      const k = { basic: "b", ebasic: "b2", skill: "s", fskill: "s", ult: "u", fua: "f" }[a && a.lastAct], e = who && k ? dmgEntry(who, k) : null, tg = e ? e.tg : 1;
      return tg === 3 || tg === 4 ? N : tg === 2 ? Math.min(3, N) : 1;
    };
    const applyIn = (eff, src, srcColor) => {\n''')
F.rep('      if (x.first) e.first = true;', '      if (x.ph) e.perHit = true;     // 每击中 1 个敌方目标：数值 × 击中的敌人数（银枝、翡翠）\n      if (x.lfc) e.lifeCap = x.lfc;  // 召唤物行动次数最多累计到几次（灵砂的浮元 5 次）\n      if (x.first) e.first = true;')
F.rep('{ const b0 = u.e; u.e = Math.max(0, u.e - eCfg(u).ultCost); eH[u.id].push({ t, v: u.e, d: u.e - b0, why: "开大消耗" }); }',
      '{ const b0 = u.e; u.e = Math.max(0, u.e - eCfg(u).ultCost); u.ueb = b0; u.uec = b0 - u.e; eH[u.id].push({ t, v: u.e, d: u.e - b0, why: "开大消耗" }); }')
F.rep('ultMarks.push({ t, uid: u.id, n: u.ultN, target: usesPick ? pickFor(u) : null,', 'ultMarks.push({ t, uid: u.id, n: u.ultN, eb: u.ueb, ec: u.uec, target: usesPick ? pickFor(u) : null,')
F.rep('const U2ST = { "1507": m => (m.sts || []).includes("无量忿怒") };', 'const U2ST = { "1507": m => (m.sts || []).includes("无量忿怒"), "1302": m => num(m.ec) >= 180 - 1e-6 };')

# ================= 灵砂 1222 =================
c = C[1222]; E = lambda f, r=None: F.eff(1222, f, r)
has('122204', '初始拥有#1[i]点速度以及#7[i]次行动次数'); has('122204', '最多累计#5[i]次行动次数'); has('122204', '施放战技会增加#7[i]次')
assert prm('122204', 10)[4] == 5 and prm('122204', 10)[6] == 3
has('122203', '使【浮元】行动提前'); assert '召唤' not in F.SK['122203']['desc']
has('122207', '下一次战斗开始时立即召唤【浮元】')
sm_old, ult_sm = E('战技：浮元登场 / 刷新'), E('终结技：浮元登场 / 刷新')
life = dict(y='life', t='skill', tg='sm:fuyuan', v=3, lfc=5, n='天赋：【浮元】在场时施放战技，行动次数 +3（最多累计 5 次）')
smn = dict(y='summon', t='skill', tg='sm:fuyuan', v=0, nr=1, n='天赋：施放战技时召唤【浮元】（速度 90，初始 3 次行动次数；已在场就不重新召唤）')
tech = [dict(y='summon', t='start', tg='sm:fuyuan', v=0, off=1, n='秘技流翠散云：下一次战斗开始时立即召唤【浮元】（用了秘技再启用）')]
new = []
for e in c['eff']:
    if e is ult_sm: continue
    if e is sm_old: new += [life, smn]; continue
    new.append(e)
E('终结技：浮元行动提前 100%')['n'] = '终结技：使【浮元】行动提前 100%（终结技不召唤浮元，浮元不在场时无效）'
F.rebuild(1222, new + tech, rename={sm_old['n']: smn['n'], '终结技：浮元行动提前 100%': '终结技：使【浮元】行动提前 100%（终结技不召唤浮元，浮元不在场时无效）'},
          notes=(c.get('notes') or []) + ['终结技【醇醉】（击破伤害 +25%）、E1 弱点击破效率、E2 击破特攻 +40% 只影响击破伤害，页面不算击破，没做'])
has('122204', '【浮元】行动时发动追加攻击'); has('r:122206', '【浮元】攻击时，额外造成')
e4 = E('E4', 4); e4.update(tg='lowhp', n='E4 横垂宝幄，半拂琼筵：【浮元】行动时为当前生命值最低的我方目标回复 40% 攻击力（按当前生命值自动选）')
F.touch(1222)
F.xr(1222, [dict(k='e6', n='E6 晓兰深藏，宿香暗贮：【浮元】攻击时额外造成 4 次 50% 攻击力的伤害（随机单体）', on=['f'], st='atk', v=[2.0], e=6)])

# ================= 三月七•巡猎 1224 =================
c = C[1224]; E = lambda f, r=None: F.eff(1224, f, r)
has('122401', '随后获得#2[i]点充能'); has('122404', '【师父】施放攻击或终结技后，三月七每次获得最多#4[i]点充能')
has('122404', '充能大于等于#1[i]点时，三月七立即行动'); has('122404', '施放强化普攻后，消耗#1[i]点充能。充能上限#3[i]点')
assert prm('122404', 10)[0] == 7 and prm('122404', 10)[2] == 10 and prm('122402', 10)[0] == 0.1 and r4(prm('122402', 12)[0]) == 0.108
has('122402', '仅战技最新的施放目标被视为三月七的【师父】'); has('122407', '下一次战斗开始时三月七恢复#2[i]点能量')
MS, EB = '师父', '强化普攻'
ATKS = ['basic', 'ebasic', 'skill', 'fskill', 'fua']
adv = E('行迹惊鸿'); adv['n'] = '行迹惊鸿：战斗开始时行动提前 25%'
tf = E('天赋：充能满 7 点立即行动时伤害 +80%'); wb = E('行迹斡波')
wb.update(tg='skpick', n='行迹斡波：施放强化普攻后【师父】暴击伤害 +60%，持续 2 回合（师父 = 战技最新的目标；击破特攻 +36% 页面不算）')
new = [
    adv,
    dict(y='spd', t='skill', tg='others', v=0, m='pct', d=0, bk='shifu', n='战技：换【师父】时，原来的【师父】失去速度加成'),
    dict(y='state', t='skill', tg='others', sn=MS, v=0, n='战技：仅战技最新的施放目标被视为【师父】（先取消原来的）'),
    dict(y='spd', t='skill', tg='skpick', v=10, lv=[3, 10.8], m='pct', d=0, bk='shifu', n='战技：【师父】速度 +10%（3 魂 10.8%；师父 = 卡片上“每次战技目标”选的队友）'),
    dict(y='state', t='skill', tg='skpick', sn=MS, v=1, d=0, n='战技：使除自身以外的我方指定单体成为【师父】'),
    dict(y='count', t='ally', aw='self', aa=['basic'], tg='self', v=1, n='普攻：施放后获得 1 点充能'),
    dict(y='count', t='atk', aw='others', **{'as': MS}, aa=ATKS, tg='self', v=1, n='天赋：【师父】施放攻击后获得 1 点充能（每次最多 1 点；师父的终结技算在下一条）'),
    dict(y='count', t='aUlt', aw='others', **{'as': MS}, tg='self', v=1, n='天赋：【师父】施放终结技后获得 1 点充能'),
    dict(y='advance', t='cntUp', nc=7, ns='!' + EB, tg='self', v=100, n='天赋：充能 ≥7 点时三月七立即行动'),
    dict(y='force', t='cntUp', nc=7, ns='!' + EB, tg='self', v=1, m='ebasic', n='天赋：充能 ≥7 点时普攻得到强化且无法施放战技（下一次行动固定强化普攻）'),
    dict(y='state', t='cntUp', nc=7, ns='!' + EB, tg='self', sn=EB, v=1, d=0, n='天赋：充能 ≥7 点，进入强化（施放强化普攻后解除）'),
    dict(y='count', t='ally', aw='self', aa=['ebasic'], tg='self', v=-7, n='天赋：施放强化普攻后消耗 7 点充能（充能上限 10 点）'),
    dict(y='state', t='ally', aw='self', aa=['ebasic'], tg='self', sn=EB, v=0, n='天赋：施放强化普攻后解除强化'),
    tf, wb,
    dict(y='energy', t='start', tg='self', v=30, m='er', off=1, n='秘技一气化三餐：下一次战斗开始时恢复 30 点能量（用了秘技再启用；队友每用 1 次秘技 +1 充能、最多 3 点，请自己调计数）'),
]
old_tf = [e['n'] for e in c['eff'] if '师父攻击后 +1 充能' in e['n'] or '充能 ≥7 立即行动' in e['n'] or '充能满 7 立即行动时普攻强化' in e['n'] or '师父速度 +10%' in e['n']]
assert len(old_tf) == 4
F.rebuild(1224, new, rename={'行迹惊鸿': adv['n'], '战技：师父速度 +10%（一直生效）': new[3]['n'], '天赋：师父攻击后 +1 充能（按任意队友攻击近似）': new[6]['n'],
                             '天赋：充能 ≥7 立即行动': new[8]['n'], '天赋：充能满 7 立即行动时普攻强化': new[9]['n'],
                             '行迹斡波：施放强化普攻后【师父】暴击伤害 +60%，持续 2 回合（师父 = 模板里的第一个队友）': wb['n']},
          cnt={'n': '充能', 'at': 0, 'max': 10}, set={'cntName': '充能', 'cntAt': 0, 'cntMax': 10},
          notes=['战技：按【师父】命途的附加伤害 / 削韧、行迹玲珑、终结技“下一次强化普攻初始段数 +2”只影响伤害，段数按初始 3 段显示'])
assert '该效果每回合最多触发1次' in F.RK['122402']['desc'] and '每当【师父】施放普攻或战技攻击敌方目标后，三月七立即发动追加攻击' in F.RK['122402']['desc']
e2 = F.eid(1224, 2)
e2['eff'] = [
    dict(y='fua', t='atk', aw='others', **{'as': MS}, aa=['basic', 'ebasic', 'skill', 'fskill'], ac=1, tg='self', v=0, n='E2 白刃耀雪舞骇浪：【师父】施放普攻或战技攻击后，三月七立即发动追加攻击（每回合最多 1 次）'),
    dict(y='count', t='atk', aw='others', **{'as': MS}, aa=['basic', 'ebasic', 'skill', 'fskill'], ac=1, tg='self', v=1, n='E2：这次追加攻击后获得 1 点充能'),
]
e1 = E('E1', 1); e1['n'] = 'E1 初花学剑动星芒：场上存在【师父】时三月七速度 +10%（施放战技后一直生效）'
assert 'f' not in F.DMG['1224']
F.DMG['1224']['f'] = dict(v=[0.6] * 15, adj=[], rnd=[], tg=1, n='E2 白刃耀雪舞骇浪（追加攻击）')

# ================= 忘归人 1225 =================
c = C[1225]; E = lambda f, r=None: F.eff(1225, f, r)
p2 = prm('122502', 10); assert p2[0] == 3 and p2[3] == 0.18 and p2[4] == 2 and r4(prm('122502', 12)[3]) == 0.2
has('122502', '使自身进入【炽灼】状态，持续#1[i]回合，忘归人每回合开始时持续回合数减1'); has('122502', '【狐祈】仅对忘归人战技最新的施放目标生效')
has('122502', '持有【狐祈】的我方目标每次施放攻击时'); has('122507', '进入战斗后忘归人行动提前#2[i]%')
assert F.SK['122507']['params'][0][3] == 0.4
HQ, CZ = '狐祈', '炽灼'
dl, spf = E('行迹青丘重光'), E('行迹涂山玄设')
dl['n'] = '行迹青丘重光：我方目标造成弱点击破后，额外使敌方目标行动延后 15%'
new = [
    dict(y='state', t='skill', tg='others', sn=HQ, v=0, n='战技：【狐祈】仅对战技最新的施放目标生效（先取消原来的）'),
    dict(y='state', t='skill', tg='skpick', sn=HQ, v=1, d=0, n='战技：使指定我方单体获得【狐祈】（卡片上“每次战技目标”选的队友；击破特攻 +30% 页面不算）'),
    dict(y='state', t='skill', tg='self', sn=CZ, v=1, d=3, ts=1, n='战技：自身进入【炽灼】状态，持续 3 回合（忘归人每回合开始时 −1）'),
    dict(y='force', t='skill', tg='self', v=2, m='ebasic', n='战技：【炽灼】状态下普攻获得强化（施放战技后的 2 次行动用强化普攻；想再放战技在“每次行动”里改）'),
    dict(y='dbuf', t='atk', aw='all', **{'as': HQ}, ns=CZ, tg='enemies', m='defRed', v=18, lv=[3, 20], d=2, bk='zz', n='战技：【炽灼】期间持有【狐祈】的我方目标每次施放攻击时，敌方目标防御力 −18%（3 魂 20%），持续 2 回合'),
    dl, spf,
    dict(y='advance', t='start', tg='self', v=40, off=1, n='秘技炤炤彻旷：进入战斗后忘归人行动提前 40%（用了秘技再启用）'),
    dict(y='dbuf', t='start', tg='enemies', m='defRed', v=18, lv=[3, 20], d=2, bk='zz', off=1, n='秘技炤炤彻旷：进入战斗后敌方每个单体目标陷入与战技相同的防御力降低状态，持续 2 回合（用了秘技再启用）'),
]
F.rebuild(1225, new, rename={'行迹青丘重光：被击破的敌人再延后 15%': dl['n'], '战技：【炽灼】期间【狐祈】目标攻击时敌人防御力 −18%（按战技后 3 回合近似）': new[4]['n']},
          notes=['天赋【云火昭】、超击破伤害、行迹玑星太素（击破特攻）、E1 / E4 / E6 的弱点击破效率和击破伤害只影响击破，页面不算击破，没做'])
assert '当忘归人处于【炽灼】状态时，【狐祈】效果对我方全体生效' in F.RK['122506']['desc']
F.eid(1225, 6)['eff'] = [dict(y='dbuf', t='atk', aw='all', ns=CZ, tg='enemies', m='defRed', v=18, lv=[3, 20], d=2, bk='zz', n='E6 肇素未来，晦明兴灭：【炽灼】状态时【狐祈】对我方全体生效（任意我方目标攻击时敌方防御力 −18%，持续 2 回合）')]
e2a = E('E2 瑞应之來', 2); e2a['n'] = 'E2 瑞应之來，必昭有德：施放终结技后我方全体行动提前 24%'
e2b = E('E2：有敌人弱点被击破', 2); e2b['n'] = 'E2：当有敌方目标的弱点被击破时，忘归人恢复 3 点能量'

# ================= 银枝 1302 =================
c = C[1302]; E = lambda f, r=None: F.eff(1302, f, r)
pt = prm('130204', 10); assert pt == [3, 0.025, 10] and r4(prm('130204', 12)[1]) == 0.028
has('130204', '每击中1个敌方目标，为银枝恢复#1[i]点能量并获得1层【升格】')
assert prm('130203', 10)[1] == 90 and prm('130214', 10)[3] == 180 and F.CH['1302']['max_sp'] == 180
has('130207', '并使银枝恢复#4[i]点能量'); assert F.SK['130207']['params'][0][2] == 15
en, cr, kk, yq = E('天赋（按每次击中 1 个敌人）'), E('天赋：每击中 1 个敌人获得 1 层【升格】'), E('行迹慷慨'), E('行迹勇气')
o_en, o_cr, o_kk = en['n'], cr['n'], kk['n']
en.update(ph=1, n='天赋：施放普攻 / 战技 / 终结技时每击中 1 个敌方目标恢复 3 点能量（按敌人卡数量，没放敌人按 1 个）')
cr.update(ph=1, n='天赋：每击中 1 个敌方目标获得 1 层【升格】，暴击率 +2.5%（3 魂 2.8%），最多 10 层（4 魂 12 层；按敌人卡数量）', ste=[4, 12])
kk['n'] = '行迹慷慨：敌方目标进入战斗时恢复 2 点能量（按 1 个敌人进战）'
qc = dict(cr, t='turn', n='行迹虔诚：回合开始时立即获得 1 层【升格】'); qc.pop('aw'); qc.pop('ph')
new = [en, cr, qc, kk, yq,
       dict(y='energy', t='start', tg='self', v=15, m='er', off=1, n='秘技纯粹高洁宣言：进入战斗时恢复 15 点能量（用了秘技再启用）')]
F.rebuild(1302, new, rename={o_en: en['n'], o_cr: cr['n'], o_kk: kk['n']}, x={'capE': 180},
          set={'capE': 180},
          notes=['终结技有两种：消耗 90 点的【驻于花庭，赐与尽美】和消耗 180 点的【驻「我」华庭，授予至勋】。模板按 180 点开大（伤害按后者）；想用 90 点的，把卡片“能量上限”改成 90（最多存 180）'])
e1 = E('E1', 1); e1.update(ph=1, ste=[4, 12], n='E1 审美王国的缺口：每层【升格】额外使暴击伤害 +4%（层数同天赋）')
assert '战斗开始时，获得2层【升格】，并使天赋的效果可叠加上限提高2层' in F.RK['130204']['desc']
def no_hit(d, **kw):
    d = dict(d, **kw); d.pop('aw', None); d.pop('ph', None); return d
F.eid(1302, 1)['eff'] = [e1, no_hit(e1, t='turn', n='E1：行迹虔诚给的【升格】同样 +4% 暴击伤害')]
F.eid(1302, 4)['eff'] = [no_hit(cr, t='start', n='E4 号角的奉献：战斗开始时获得 2 层【升格】（第 1 层；叠加上限 +2 层已算进天赋）'),
                         no_hit(cr, t='start', n='E4 号角的奉献：战斗开始时获得 2 层【升格】（第 2 层）'),
                         no_hit(e1, t='start', n='E4：开局的 2 层【升格】同样有 E1 的 +4% 暴击伤害（第 1 层）'),
                         no_hit(e1, t='start', n='E4：开局的 2 层【升格】同样有 E1 的 +4% 暴击伤害（第 2 层）')]
e6 = E('E6', 6); e6['n'] = 'E6 「你」的光芒：施放终结技时无视敌方目标 30% 的防御力'

F.finish('全面校对第 1 批（灵砂、三月七•巡猎、忘归人、银枝）', LOG := '''<li><b>2026-11-10（全面校对第 1 批：灵砂、三月七•巡猎、忘归人、银枝）</b>：按“所有效果都和游戏原文相同”逐条对照 StarRailRes 技能 / 行迹 / 星魂 / 秘技原文，去掉“按……近似”的写法，tv 57（tools/fix57.py）。① <b>灵砂</b>：【浮元】按原文“初始 3 次行动次数、在场时施放战技 +3 次、最多累计 5 次”（原来每次战技都重置成 3 次）；<b>终结技不召唤浮元</b>，只让在场的浮元行动提前 100%（原来终结技也会召唤 / 刷新）；E4 治疗目标改成当前生命值最低的；补秘技（开局召唤浮元，默认关）和 E6 浮元额外 4 次 50% 伤害。② <b>三月七•巡猎</b>：【师父】= 你在卡片“每次战技目标”里选的队友（换师父时旧师父失去加速）；充能按原文：<b>普攻后 +1</b>（原来漏了）、<b>只有【师父】施放攻击或终结技后 +1</b>（原来任何队友攻击都 +1）、充能上限 10、≥7 点立即行动并强化普攻、强化普攻后扣 7 点（多出的保留，原来满 7 清零）；E2 追加攻击改成只看【师父】的普攻 / 战技、每回合 1 次，默认开启；补秘技 +30 能量（默认关）。③ <b>忘归人</b>：战技做成状态：【狐祈】给“每次战技目标”、自身【炽灼】3 回合（每回合开始 −1），炽灼期间之后 2 次行动用强化普攻；减防按原文“持有【狐祈】的目标每次施放攻击时”敌方防御力 −18% 2 回合（原来是战技后固定 3 回合），E6 炽灼期间任意我方攻击都触发；补秘技行动提前 40% + 减防（默认关）。④ <b>银枝</b>：天赋“每击中 1 个敌方目标”恢复 3 能量、+1 层【升格】现在<b>按敌人卡数量算</b>（群攻打 5 个 = 15 能量、5 层；没放敌人卡仍按 1 个）；补行迹虔诚（回合开始 +1 层）、E4（开局 2 层、上限 12 层）、秘技 +15 能量（默认关）；终结技按消耗能量区分两种（180 点 = 280% + 6×95%，原来伤害按 160% 显示）。新功能：效果字段“每击中 1 个敌方目标”（ph）、召唤物行动次数上限（lfc）。<b>对已有配置</b>：用到这四个角色的方案行动轴会变（按你的要求以原文为准）；其他角色不变。</li>''',
'''2026-11-10（全面校对第 1 批）：灵砂（1222）、三月七•巡猎（1224）、忘归人（1225）、银枝（1302）—— 用户要求“所有效果都和游戏文本相同，不用在意方案流程”，逐条对照 StarRailRes 原文与 AvatarSkillConfig（普攻 20 / 战技 30 / 终结技 5；三月七强普 30 不回战技点、E2 追击 5；忘归人强普 20 回战技点），tv 57（tools/fix57.py + tools/fixlib.py）。
  改：见更新日志同日条目。新字段 perHit（ph）、lifeCap（lfc），ultMarks 带 eb / ec（U2ST 1302 按扣 180 点选 u2）。
  未改 / 存疑：击破相关（击破特攻、弱点击破效率、超击破、【云火昭】、【醇醉】）页面不算击破，都没做；三月七按师父命途的附加伤害和强普额外段数（60% 概率）没做；银枝行迹慷慨按 1 个敌人进战；灵砂 E1 减防仍默认关。''')
