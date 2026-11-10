"""tv 61：全面校对第 5 批（万敌 1404、赛飞儿 1406、白厄 1408、海瑟音 1410 核对；刻律德菈 1412、丹恒•腾荒 1414、不死途 1504 重写）。
用法：python3 tools/fix61.py index.html <官方 json 目录>
新功能：伤害增益 stMod（DB smd：[m, k] 把层数变成 ((n − k) mod m) + k，不死途强化追击消耗【婪酣】）；
迁移时给模板新加的召唤物补卡（丹恒•腾荒的【龙灵】）。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 61, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('        if ((v === 0 && bk) || n <= 0) continue;   // stAdd 负数：减层，减到 0 移除',
      '        if (Array.isArray(eff.stMod)) { const o = old ? old.n || 1 : 0, k = num(eff.stMod[1]), m = Math.max(1, num(eff.stMod[0])); n = o <= k ? o : ((o - k) % m) + k; }   // 每 m 层消耗掉，最后加的 k 层不算（不死途强化追击）\n        if ((v === 0 && bk) || n <= 0) continue;   // stAdd 负数：减层，减到 0 移除')
F.rep('const old = tg.buffs.find(b => b.key === kk), n = lim > 0 ?', 'const old = tg.buffs.find(b => b.key === kk); let n = lim > 0 ?')
F.rep('      if (x.sa) e.stAdd = x.sa;', '      if (x.smd) e.stMod = x.smd;    // 伤害增益层数取模（每 m 层消耗）\n      if (x.sa) e.stAdd = x.sa;')
F.rep('''      const T = u.kind === "ally" && !u.sm ? tplOf(u) : null, fx = T && FIX[T.id]; if (!fx) continue;
      const kept = new Set();''', '''      const T = u.kind === "ally" && !u.sm ? tplOf(u) : null, fx = T && FIX[T.id]; if (!fx) continue;
      for (const m of (T.sm || [])) if (!s.units.some(z => z.sm && z.sm.owner === u.id && z.sm.key === m.k)) {   // 模板新加的召唤物：老存档补一张卡（丹恒•腾荒的龙灵）
        const sp0 = m.spd || 100;
        s.units.push({ id: nid(), name: m.n, color: m.color || u.color, kind: "ally", spd: sp0, base: sp0, opening: 0, effects: [],
          sm: { owner: u.id, key: m.k, ratio: m.ratio || 0, life: m.life || 0, start: !!m.start, cd: !!m.cd, pause: !!m.pause, fua: !!m.fua, noTurn: !!m.nt, ...(m.mem ? { mem: true } : {}) } });
      }
      const kept = new Set();''')

F.rep('      else if (actor.sm) atkAct(actor);   // 召唤物 / 忆灵行动算攻击（倒计时不算）',
      '      else if (actor.sm && !(smDef(actor) || {}).na) atkAct(actor);   // 召唤物 / 忆灵行动算攻击（倒计时不算；模板 sm.na = 行动不算攻击，丹恒•腾荒的龙灵）')

F.rep('      tg.st[k] = { left: d > 0 ? d : Infinity, tick: eff.stTick === "start" ? "start" : eff.stTick === "src" && src ? "src" : "end", by: src ? src.id : null };',
      '''      const hadMv = !!(eff.mv && tg.st[k]);
      if (eff.mv) for (const z of U) if (z !== tg && z.st && z.st[k]) endSt(z, k);   // 只能有一个持有者：换目标时旧持有者失去状态（师父、军功、同袍……）
      tg.st[k] = { left: d > 0 ? d : Infinity, tick: eff.stTick === "start" ? "start" : eff.stTick === "src" && src ? "src" : "end", by: src ? src.id : null };
      if (hadMv) return;   // 目标没变：不重复标记''')

# ---- 前几批“先取消原来的、再给新目标”的状态改成 mv（目标没变时不再反复标“结束”）----
for cid, sn in ((1224, '师父'), (1225, '狐祈'), (1313, '蒙福者'), (1314, '收债人')):
    L = C[cid]['eff']
    off = [e for e in L if e.get('y') == 'state' and e.get('sn') == sn and e.get('v') == 0 and e.get('tg') == 'others']
    on = [e for e in L if e.get('y') == 'state' and e.get('sn') == sn and e.get('v') == 1]
    assert len(off) == 1 and len(on) == 1, (cid, sn)
    on[0]['mv'] = 1
    F.rebuild(cid, [e for e in L if e is not off[0]])

# ================= 白厄 1408 =================
c = C[1408]; E = lambda f, r=None: F.eff(1408, f, r)
has('140805', '变身结束时，使我方全体速度提高')
sp = E('天赋：变身结束时我方全体速度 +15%'); o_sp = sp['n']
sp.update(cnt='own', bk='bsend', n='天赋：变身结束时我方全体速度 +15%，持续 1 回合（按每个角色自己的回合）')
F.rebuild(1408, list(c['eff']), rename={o_sp: sp['n']})
has('r:140806', '【火种】的可溢出点数不再拥有上限')
e6 = F.eid(1408, 6); e6['eff'].append(dict(y='ecap', t='start', tg='self', v=100000, n='E6 亘古长升，蚀火残阳：【火种】的可溢出点数不再拥有上限'))
e6['notes'] = [n for n in e6.get('notes', []) if '请把能量上限改大' not in n]

# ================= 海瑟音 1410 =================
c = C[1410]; E = lambda f, r=None: F.eff(1410, f, r)
hast(1410, '征服的剑旗', '战斗开始时，海瑟音展开与终结技效果相同的结界，结界持续3回合')
df = E('终结技：结界内敌方防御力'); o_df = df['n']
df['n'] = '终结技：结界内敌方目标防御力 −25%（3 魂 27%），结界持续 3 回合'
new = []
for e in c['eff']:
    new.append(e)
    if e is df: new.append(dict(df, t='start', n='行迹征服的剑旗：战斗开始时展开与终结技相同的结界（敌方防御力 −25%），持续 3 回合'))
F.rebuild(1410, new, rename={o_df: df['n']}, notes=['天赋的持续伤害、结界的追加持续伤害、行迹盛会的泡沫、E1 / E6 页面不算持续伤害，没做；结界的攻击力降低不影响我方'])
e4 = E('E4', 4); e4['n'] = 'E4 看呀，时间为何流淌：结界持续期间敌方全体全属性抗性 −20%（终结技的结界）'
F.eid(1410, 4)['eff'].append(dict(e4, t='start', n='E4：战斗开始的结界同样使敌方全体全属性抗性 −20%，持续 3 回合'))
e2 = E('E2', 2)
F.eid(1410, 2)['eff'].append(dict(e2, t='start', n='E2 你说浪花为何喧响：战斗开始的结界期间珍珠的琴弦同样对我方全体生效（确认效果命中 ≥120% 时启用）'))

# ================= 刻律德菈 1412 =================
c = C[1412]; E = lambda f, r=None: F.eff(1412, f, r)
p2, p4 = prm('141202', 10), prm('141204', 10)
has('141202', '使指定我方单体角色获得【军功】并使刻律德菈获得1点充能。充能上限#4[i]点。当充能达到#3[i]点时，自动使角色的【军功】升级为【爵位】')
has('141202', '对敌方目标施放战技时触发奇袭。奇袭结束后，消耗#3[i]点充能使【爵位】变回【军功】'); has('141203', '获得#2[i]点充能')
has('141204', '施放普攻或战技时使刻律德菈获得1点充能，奇袭期间无法使刻律德菈获得充能'); has('141204', '【军功】仅对最新被施加的目标生效')
hast(1412, '征服者', '持有【军功】的角色施放普攻或战技时，为刻律德菈恢复'); hast(1412, '见者', '持有【军功】的角色施放终结技时使刻律德菈获得1点充能，该效果单场战斗中可以触发1次')
JG, JW = '军功', '爵位'
BS = ['basic', 'ebasic', 'skill', 'fskill']
s1, cast, atk, cdj, pnj, lz, jz, rx = E('行迹征服者：自身速度 +20'), E('秘技：下一次战斗开始时'), E('天赋：持有【军功】的角色攻击力'), E('战技：持有【爵位】时战技的暴击伤害'), E('战技：持有【爵位】时全属性抗性穿透'), E('行迹来者'), E('行迹见者：暴击率 +100%'), E('额外伤害标记')
o = {k: e['n'] for k, e in dict(s1=s1, atk=atk, cdj=cdj, pnj=pnj, rx=rx).items()}
s1['n'] = '行迹征服者：施放战技时自身速度 +20 点，持续 3 回合'
atk.update(t='skill', tg='skpick', mv=1, n='天赋：持有【军功】的角色攻击力 +刻律德菈攻击力的 24%（5 魂 25.2%；军功 = 卡片“每次战技目标”选的队友）')
rx.update(t='skill', tg='skpick', mv=1, n='额外伤害标记：【军功】持有者施放攻击后刻律德菈额外造成 60% 攻击力的附加伤害')
cdj.update(t='cntUp', nc=6, tg='skpick', n='战技：充能达到 6 点时【军功】升级为【爵位】，战技伤害的暴击伤害 +72%（3 魂 79.2%）'); cdj.pop('off', None)
pnj.update(t='cntUp', nc=6, tg='skpick', n='战技：持有【爵位】时全属性抗性穿透 +10%（3 魂 10.4%）'); pnj.pop('off', None)
new = [
    dict(y='state', t='skill', tg='skpick', sn=JG, v=1, d=0, mv=1, n='战技：使指定我方单体角色获得【军功】（仅对最新被施加的目标生效）'),
    dict(y='count', t='skill', tg='self', v=1, n='战技：刻律德菈获得 1 点充能（上限 8 点）'),
    dict(y='count', t='ult', tg='self', v=2, n='终结技：获得 2 点充能'),
    dict(y='count', t='ally', aw='others', **{'as': JG}, aa=BS, tg='self', v=1, n='天赋：持有【军功】的角色施放普攻或战技时，刻律德菈获得 1 点充能（奇袭期间不获得）'),
    dict(y='energy', t='ally', aw='others', **{'as': JG}, aa=BS, tg='self', v=5, m='er', n='行迹征服者：持有【军功】的角色施放普攻或战技时，为刻律德菈恢复 5 点能量'),
    dict(y='count', t='aUlt', aw='others', **{'as': JG}, ltc=8, first=1, tg='self', v=1, n='行迹见者：充能小于上限时，持有【军功】的角色施放终结技使刻律德菈获得 1 点充能（单场战斗 1 次）'),
    dict(y='state', t='cntUp', nc=6, tg='skpick', sn=JW, v=1, d=0, n='战技：充能达到 6 点时，【军功】自动升级为【爵位】'),
    cdj, pnj,
    dict(y='cast', t='aSk', aw='others', **{'as': JG}, nc=6, ptn=1, tg='evt', v=0, m='skill', n='战技：持有【爵位】的角色施放战技时触发奇袭（立即再施放 1 次战技，不消耗战技点；按官方名词解释，持有者的战技要以敌方为目标）'),
    dict(y='count', t='aSk', aw='others', **{'as': JW}, nc=6, tg='self', v=-6, n='战技：奇袭结束后消耗 6 点充能'),
    dict(cdj, t='aSk', aw='others', **{'as': JW}, v=0, tg='evt', n='战技：奇袭结束后【爵位】的暴击伤害加成取消'),
    dict(pnj, t='aSk', aw='others', **{'as': JW}, v=0, tg='evt', n='战技：奇袭结束后【爵位】的抗性穿透取消'),
    dict(y='state', t='aSk', aw='others', **{'as': JW}, tg='evt', sn=JW, v=0, n='战技：奇袭结束后【爵位】变回【军功】'),
    s1,
    dict(y='spd', t='skill', tg='skpick', v=20, m='flat', d=3, n='行迹征服者：施放战技时持有【军功】的队友速度 +20 点，持续 3 回合'),
    cast, atk, rx, lz, jz,
]
for x in new[11:13]: x.pop('nc', None); x.pop('lv', None)
on = [n for n, t in F.OLD[1412]]
ren = {o['s1']: s1['n'], o['atk']: atk['n'], o['cdj']: cdj['n'], o['pnj']: pnj['n'], o['rx']: rx['n'],
       '行迹征服者：军功持有者速度 +20': new[15]['n'], '行迹征服者（军功持有者普攻 / 战技后）': new[4]['n']}
F.rebuild(1412, new, rename=ren, off0=[o['cdj'], o['pnj'], '行迹征服者（军功持有者普攻 / 战技后）'],
          cnt={'n': '充能', 'at': 0, 'max': 8}, set={'cntName': '充能', 'cntAt': 0, 'cntMax': 8},
          notes=['【军功】目标改变时充能重置为 0、终结技“场上没有军功时给第一位角色”没做（一直对同一个人放战技时没影响）；附加伤害最多 20 次（终结技重置）没限制'])
for r, frag in ((1, 'E1 夺走一切王冠'), (1, 'E1：持有【军功】'), (2, 'E2：持有【军功】'), (6, 'E6：持有【军功】')):
    x = E(frag, r); x['tg'] = 'skpick'
    if x['y'] == 'dbuf': x.update(t='skill', mv=1)
    x['n'] = x['n'].replace('为指定队友 +2 能量', '为指定我方目标恢复 2 点能量')
F.touch(1412)

# ================= 丹恒•腾荒 1414 =================
c = C[1414]; E = lambda f, r=None: F.eff(1414, f, r)
pu, pt = prm('141403', 10), prm('141404', 10)
has('141404', '我方角色成为【同袍】时，丹恒•腾荒会为其召唤【龙灵】，【龙灵】初始拥有#1[i]点速度'); assert 165 in pt
has('141403', '次行动')
hast(1414, '葳蕤', '【同袍】施放攻击时，丹恒•腾荒恢复6点能量，使【龙灵】行动提前15%')
TP, LQ = '同袍', '龙灵强化'
sh1, sh2, adv, en, cast, sx, dd = E('战技：护盾'), E('终结技：护盾'), None, E('行迹葳蕤：同袍施放攻击时 +6 能量'), E('秘技：下一次战斗开始时'), E('行迹神秀'), E('昔涟献予「大地」之诗')
adv = [e for e in c['eff'] if e['n'] == '行迹葳蕤'][0]
o = {k: e['n'] for k, e in dict(adv=adv, en=en, sx=sx, dd=dd, sh1=sh1, sh2=sh2).items()}
sh1['n'] = '战技：为我方全体提供护盾，持续 3 回合'; sh2['n'] = '终结技：为我方全体提供护盾，持续 3 回合'
adv['n'] = '行迹葳蕤：战斗开始时丹恒•腾荒行动提前 40%'
en.update({'as': TP}, n='行迹葳蕤：【同袍】施放攻击时，丹恒•腾荒恢复 6 点能量')
sx.update(tg='skpick', mv=1, n='行迹神秀：施放战技时【同袍】攻击力 +丹恒•腾荒攻击力的 15%（同袍 = 卡片“每次战技目标”选的队友）')
dd.update(tg='skpick', n='昔涟献予「大地」之诗：持有时【同袍】造成的伤害 +24%')
new = [
    dict(y='state', t='skill', tg='skpick', sn=TP, v=1, d=0, mv=1, n='战技：使指定我方单体角色成为【同袍】（仅对战技最新施放的目标生效）'),
    dict(y='summon', t='skill', tg='sm:long', v=0, nr=1, n='天赋：我方角色成为【同袍】时为其召唤【龙灵】（速度 165；已在场就不重新召唤）'),
    sh1, sh2,
    dict(y='shield', t='ally', aw='sm', tg='allies', v=0, n='天赋：【龙灵】行动时为我方全体提供护盾，持续 3 回合'),
    dict(y='count', t='ult', tg='self', m='set', v=2, n='终结技：使【龙灵】获得强化，持续【龙灵】2 次行动'),
    dict(y='fua', t='ally', aw='sm', uc=1, tg='sm:long', v=0, n='终结技：强化的【龙灵】行动时发动追加攻击（80% 攻击力 + 同袍 80% 攻击力的附加伤害，消耗 1 次强化）'),
    adv, en,
    dict(y='advance', t='atk', aw='others', **{'as': TP}, tg='sm:long', v=15, n='行迹葳蕤：【同袍】施放攻击时使【龙灵】行动提前 15%'),
    cast, sx, dd,
]
F.rebuild(1414, new, rename={o[k]: v['n'] for k, v in dict(adv=adv, en=en, sx=sx, dd=dd, sh1=sh1, sh2=sh2).items()},
          cnt={'n': LQ, 'at': 0}, set={'cntName': LQ, 'cntAt': 0},
          sm=[{'k': 'long', 'n': '龙灵', 'spd': 165, 'na': 1}],
          notes=['【龙灵】的追加攻击里【同袍】攻击力的附加伤害、行迹峥嵘的额外护盾和附加伤害、E2 的 200%、E6 终结技时同袍的 330% 附加伤害没算进伤害显示'])
i8 = pu.index(0.8)
assert 'f' not in F.DMG['1414']
F.DMG['1414']['f'] = dict(v=[r4(p[i8]) for p in F.SK['141403']['params']], adj=[], rnd=[], tg=3, el=0, stat='atk', n='强化【龙灵】的追加攻击', max=15)
has('r:141402', '终结技的强化龙灵行动效果额外增加2次，丹恒•腾荒施放终结技后【龙灵】行动提前100%')
e2 = F.eid(1414, 2)
e2['eff'] = [dict(y='count', t='ult', tg='self', v=2, n='E2 守望开拓的赤子：终结技的强化龙灵行动效果额外增加 2 次'),
             dict(y='advance', t='ult', tg='sm:long', v=100, n='E2：施放终结技后【龙灵】行动提前 100%')]
e2['notes'] = []
for r, frag in ((1, 'E1：施放终结技时【同袍】'), (6, 'E6：【同袍】造成伤害时')):
    x = E(frag, r); x['tg'] = 'skpick'
E('E6：【同袍】造成伤害时', 6).update(t='skill', mv=1)

# ================= 不死途 1504 =================
c = C[1504]; E = lambda f, r=None: F.eff(1504, f, r)
p4 = prm('150404', 10)
has('150404', '点充能，最多拥有')
has('150404', '随后消耗1点充能对【饲饵】发动追加攻击')
has('150404', '随后获得2层【婪酣】，最多叠加12层'); has('150402', '若该目标为【饲饵】，则额外对其造成'); has('150402', '并恢复1点战技点')
has('150403', '点充能')
hast(1504, '罪途', '不死途施放战技/终结技时，获得1/2层【婪酣】'); hast(1504, '影肢', '且每有1层【婪酣】，追加攻击造成的伤害额外提高10%')
en0 = [e for e in c['eff'] if e['n'] == '天赋：饲饵被队友攻击后固定回 8'][0]
fu, fuu, se, yz, tl, tlf = E('天赋：饲饵受到其他队友攻击后，消耗 1 点充能追加攻击'), E('终结技：随后立即发动 1 次强化的天赋追加攻击'), E('战技：场上有【饲饵】时'), E('行迹影肢'), E('行迹头狼：我方暴击伤害'), E('行迹头狼：我方追加攻击')
o = {k: e['n'] for k, e in dict(en0=en0, fu=fu, fuu=fuu, yz=yz).items()}
en0.update(aw='others', n='天赋：【饲饵】受到我方其他目标攻击后，不死途固定恢复 8 点能量（按队友的攻击都打到饲饵算）')
fu.update(uc=1, n='天赋：随后消耗 1 点充能对【饲饵】发动追加攻击'); fu.pop('off', None)
fuu['n'] = '终结技：随后立即对【饲饵】发动 1 次获得强化的天赋追加攻击（不消耗充能）'
yz['n'] = '行迹影肢：追加攻击造成的伤害 +80%'
LH = lambda **k: dict(dict(y='dbuf', tg='self', m='dmg', sc='f', v=10, st=12, ste=[2, 18], d=0, bk='lh'), **k)
new = [
    dict(y='count', t='start', tg='self', v=2, n='天赋：初始拥有 2 点充能（最多 3 点）'),
    en0, fu,
    LH(t='fua', sa=2, n='天赋 / 行迹影肢：发动追加攻击后获得 2 层【婪酣】（最多 12 层，2 魂 18 层），每层使追加攻击伤害 +10%'),
    dict(y='sp', t='skill', tg='self', v=1, n='战技：目标已经是【饲饵】时恢复 1 个战技点（按战技目标就是饲饵算，不是时关掉）'),
    LH(t='skill', sa=1, n='行迹罪途：施放战技时获得 1 层【婪酣】'),
    dict(y='count', t='ult', tg='self', v=3, n='终结技：获得 3 点充能'),
    LH(t='ult', sa=2, n='行迹罪途：施放终结技时获得 2 层【婪酣】'),
    fuu,
    LH(t='ult', smd=[4, 2], n='终结技：强化天赋追加攻击每消耗 4 层【婪酣】额外造成 1 次 200% 攻击力的伤害（这里只扣层数，额外伤害没算）'),
    se, yz, tl, tlf,
    dict(y='count', t='start', tg='self', v=1, off=1, n='秘技吃吧，可憎的手：进入战斗时获得 1 点充能（用了秘技再启用）'),
]
F.rebuild(1504, new, rename={o['en0']: en0['n'], o['fu']: fu['n'], o['fuu']: fuu['n'], o['yz']: yz['n']}, off0=[o['fu']],
          cnt={'n': '充能', 'at': 0, 'max': 3}, set={'cntName': '充能', 'cntAt': 0, 'cntMax': 3},
          notes=['【饲饵】按场上一直有（不存在时会自动选生命值最低的敌人）；强化天赋追加攻击消耗【婪酣】的额外伤害、E2 返还 35% 层数没算'])
has('r:150406', '不死途每获得过1层【婪酣】，造成的伤害提高4%，该效果最多叠加30层')
e6 = F.eid(1504, 6); old6 = E('E6：每获得过 1 层婪酣', 6)
E6 = lambda **k: dict(dict(y='dbuf', tg='self', m='dmg', v=4, st=30, d=0, bk='e6d'), **k)
e6['eff'] = [x for x in e6['eff'] if x is not old6] + [
    E6(t='fua', sa=2, n='E6 结局，或许无人生还：每获得过 1 层【婪酣】造成的伤害 +4%，最多 30 层（追加攻击的 2 层）'),
    E6(t='skill', sa=1, n='E6：每获得过 1 层【婪酣】伤害 +4%（战技的 1 层）'),
    E6(t='ult', sa=2, n='E6：每获得过 1 层【婪酣】伤害 +4%（终结技的 2 层）')]

F.finish('全面校对第 5 批（万敌、赛飞儿、白厄、海瑟音、刻律德菈、丹恒•腾荒、不死途）', '''<li><b>2026-11-10（全面校对第 5 批：万敌、赛飞儿、白厄、海瑟音、刻律德菈、丹恒•腾荒、不死途）</b>：逐条对照原文，tv 61（tools/fix61.py）。① <b>不死途</b>：充能按原文（初始 2 点、最多 3 点、终结技 +3），<b>天赋追加攻击默认开启</b>（【饲饵】受到其他队友攻击后回 8 能量并消耗 1 点充能追击；原来默认关、而且任何队友攻击都回 8 能量两次）；补战技“目标已是饲饵时恢复 1 个战技点”、【婪酣】层数（追击 +2、战技 +1、终结技 +2，每层追击伤害 +10%，强化追击每 4 层消耗）、秘技 +1 充能（默认关）、E6 按获得过的层数叠。② <b>刻律德菈</b>：【军功】= “每次战技目标”；充能按原文（战技 +1、终结技 +2、军功持有者施放普攻 / 战技 +1、上限 8），<b>满 6 点升【爵位】，持有者施放战技时触发奇袭（立即再施放 1 次战技）并消耗 6 点</b>，爵位的暴伤 / 穿透跟着自动开关（原来默认关）；行迹征服者的 5 点能量、见者的 1 点充能自动判断。③ <b>丹恒•腾荒</b>：<b>补上【龙灵】（速度 165，战技选【同袍】时召唤）</b>，龙灵行动给全队护盾，终结技后 2 次行动发动追加攻击（E2 再 +2 次并拉条 100%）；【同袍】= “每次战技目标”，行迹葳蕤改成只看【同袍】的攻击（+6 能量、龙灵提前 15%；原来任何队友攻击都算）。老存档会自动补一张龙灵卡。④ <b>白厄</b>：变身结束的全队加速按各自回合 1 回合；E6 火种溢出不设上限自动处理。⑤ <b>海瑟音</b>：补战斗开始时的结界（减防、E4 减抗）。⑥ <b>万敌、赛飞儿</b>：核对无误。<b>对已有配置</b>：不死途 / 刻律德菈 / 丹恒•腾荒的方案行动轴会变。</li>''',
'''2026-11-10（全面校对第 5 批）：万敌（1404）、赛飞儿（1406）、白厄（1408）、海瑟音（1410）、刻律德菈（1412）、丹恒•腾荒（1414）、不死途（1504）—— tv 61（tools/fix61.py）。
  改：见更新日志同日条目。新字段 stMod（smd）；fixTpl 给模板新加的召唤物补卡。
  核对无误：万敌（战技 / 弑王成王消耗生命、充能门槛 100 / 150、终结技 +20、E2 / E4 / E6）；赛飞儿（【老主顾】追击每回合 1 次、战技攻击力、行迹、E1 / E2 / E6）。
  未改 / 存疑：万敌【弑神登神】SPBase 10，模拟里额外回合按战技回 30；白厄“成为其他目标的技能目标时 +1 火种”仍是近似（默认关）、毁伤 / 弑魂之炽没做；刻律德菈的“奇袭”按官方名词解释（立即再施放 1 次战技）做，正文没写；军功换人时充能清零没做；丹恒•腾荒龙灵的同袍附加伤害没算；不死途强化追击的额外伤害和 E2 返还没算。''')
