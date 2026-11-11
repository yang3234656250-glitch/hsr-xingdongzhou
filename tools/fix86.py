"""tv 86：“下一次攻击”的增益在那次攻击后用掉；按回合 / 按受击增减层；属性门槛按“每超过 N 点”分档。
用法：python3 tools/fix86.py index.html <官方 json 目录>
引擎：
- 伤害增益字段 nx：持有者下一次（这类）攻击之后移除。"a" = 任意攻击；或 ["b","b2","s","u","f","e","m"]（普攻 / 强化普攻 / 战技 / 终结技 / 追加攻击 / 欢愉技 / 召唤物）。
  每个“行动类事件”（任意单位回合开始、开大、追加攻击、欢愉技、秘技施放）开始时 actSeq +1；增益记下获得时的 actSeq，
  持有者攻击时（atkAct 开头，伤害快照之后）移除更早获得的、类型对得上的 nx 增益——同一次行动里获得的不算。
- 新触发 tend（自己回合结束时）。
- 伤害增益字段 stp：按施放者属性算的数值（ss）先把属性按 stp 向下取整（“每超过 100 点”分档，原来是线性）。
- 伤害增益条件 ec.pcd：持有者卡片暴击伤害 ≥X%。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 86, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('''      if (x.fps) e.fPost = 1;''', '''      if (x.nx) e.nxt = x.nx; if (x.stp) e.stp = x.stp;   // 下一次攻击后移除；属性按每 N 点分档
      if (x.fps) e.fPost = 1;''')
F.rep('''        if (eff.ec) b.ec = eff.ec; if (eff.tEl) b.tEl = eff.tEl; if (eff.alv) b.alv = 1;''', '''        if (eff.ec) b.ec = eff.ec; if (eff.tEl) b.tEl = eff.tEl; if (eff.alv) b.alv = 1; if (eff.nxt) { b.nx = eff.nxt; b.at = actSeq; }''')
F.rep('''        const r = x * v / 100 + num(eff.flat);
        return num(eff.dcap) > 0 ? Math.min(num(eff.dcap), Math.max(0, r)) : r;''', '''        const r = (num(eff.stp) > 0 ? Math.floor(x / num(eff.stp) + 1e-9) * num(eff.stp) : x) * v / 100 + num(eff.flat);   // stp：每超过 N 点才算一档
        return num(eff.dcap) > 0 ? Math.min(num(eff.dcap), Math.max(0, r)) : r;''')
F.rep('''    const atkAct = (who, fromFua, act) => { toughHit(''', '''    let actSeq = 0;   // 行动类事件计数：nx 增益只被之后的攻击用掉
    const nxUse = (who, k) => { if (who && who.buffs && who.buffs.some(b => b.nx)) who.buffs = who.buffs.filter(b => !(b.nx && b.at < actSeq && (b.nx === "a" || [].concat(b.nx).includes(k)))); };
    const atkAct = (who, fromFua, act) => { nxUse(who, fromFua ? "f" : ACT2K[act] || "m"); toughHit(''')
F.rep('''      actor.turns++; turnSeq++; ntSeq++;''', '''      actor.turns++; turnSeq++; ntSeq++; actSeq++;''')
F.rep('''    const doFua = (u, color, why, as) => {
      if (!u || u.kind !== "ally" || u.gone || isCd(u) || fuaDepth >= 4) return;''', '''    const doFua = (u, color, why, as) => {
      if (!u || u.kind !== "ally" || u.gone || isCd(u) || fuaDepth >= 4) return;
      actSeq++;''')
a = F.s.index('    const castOther = (u, why) => {'); b = F.s.index('\n', a)
F.s = F.s[:b + 1] + '      actSeq++;\n' + F.s[b + 1:]
a = F.s.index('    const castUlt = where => {'); b = F.s.index('\n', a)
F.s = F.s[:b + 1] + '      actSeq++;\n' + F.s[b + 1:]
a = F.s.index('    const castAct = (u, k, src) => {'); b = F.s.index('\n', a)
F.s = F.s[:b + 1] + '      actSeq++;\n' + F.s[b + 1:]
F.rep('''      for (const u of U) if (u.kind === "ally" && u.elation) {
        if (se > 0 && !u.punchAt)''', '''      for (const u of U) if (u.kind === "ally" && u.elation) {
        actSeq++;
        if (se > 0 && !u.punchAt)''')
F.rep('''      tickSt(actor, "end"); tickSh(actor);''', '''      if (actor.kind === "ally") for (const e of fx(actor, "tend")) apply(e, actor, actor.color);   // 自己回合结束时
      tickSt(actor, "end"); tickSh(actor);''')
F.rep('''hit2: "受到攻击后（伤害结算后）"''', '''hit2: "受到攻击后（伤害结算后）", tend: "自己回合结束时"''')
F.rep('''["turn", "每"], ''', '''["turn", "每"], ["tend", "自己回合结束时"], ''')
F.rep('''      if (c.ef && !(hasEnergy(u)''', '''      if (c.pcd != null && num(u.cd, 50) < num(c.pcd) - 1e-9) return 0;   // 卡片暴击伤害 ≥X%
      if (c.ef && !(hasEnergy(u)''')
F.rep('''    if (c.ef) L.push("能量满时");''', '''    if (c.ef) L.push("能量满时");
    if (c.pcd != null) L.push(`暴击伤害 ≥${c.pcd}% 时`);''')
F.rep('''    if (num(e.dExt) > 0) h.push(''', '''    if (e.nxt) h.push(`持有者下一次${e.nxt === "a" ? "攻击" : [].concat(e.nxt).map(k => ({ b: "普攻", b2: "强化普攻", s: "战技", u: "终结技", f: "追加攻击", e: "欢愉技", m: "召唤物攻击" })[k] || k).join(" / ")}后移除`);
    if (num(e.stp) > 0) h.push(`属性每 ${num(e.stp)} 点算一档`);
    if (num(e.dExt) > 0) h.push(''')
assert F.s.count('["turn", "每"], ["tend"') == 1

def setx(e, **kw):
    for k, v in kw.items():
        if v is None: e.pop(k, None)
        else: e[k] = v
    return e
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
RS = json.load(open(sys.argv[2] + '/relic_sets.json', encoding='utf-8'))
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8'))
R = {x['id']: x for x in F.DB['relics']}; L = {x['id']: x for x in F.DB['lcs']}
P = lambda i, k: [r4(p[k] * 100) for p in LR[str(i)]['params']]

# ---- 遗器 ----
assert '当装备者施放攻击或受到攻击后，其在本场战斗中攻击力提高5%，最多叠加5层' in RS['105']['desc'][1]
e = find(R[105]['p4']['eff'], '4件：施放攻击后'); e['n'] = '4件：施放攻击后本场战斗攻击力提高 5%，最多 5 层'
R[105]['p4']['eff'].append(dict(e, t='hit', aw=None, n='4件：受到攻击后同样叠 1 层'))
R[105]['p4']['eff'][-1].pop('aw')
assert '施放终结技后的下一次攻击造成的火属性伤害提高12%' in RS['107']['desc'][1]
setx(find(R[107]['p4']['eff'], '4件：施放终结技后下一次攻击'), d=0, nx='a', n='4件：施放终结技后下一次攻击的火属性伤害提高 12%')
assert '施放终结技后，下一次施放战技时造成的伤害额外提高25%' in RS['122']['desc'][1]
setx(find(R[122]['p4']['eff'], '4件：施放终结技后下一次战技'), d=0, nx=['s'], n='4件：施放终结技后下一次战技伤害额外提高 25%')
assert '装备者回合开始时/施放终结技后，移除1层该效果' in RS['131']['desc'][1]
E = R[131]['p4']['eff']; setx(find(E, '4件：施放战技时再叠 1 层'), n='4件：施放战技时再叠 1 层')
for bk, sc in (('r', 's'), ('r2', 'u')):
    E += [dict(y='dbuf', t='turn', tg='self', m='dmg', v=18, sc=sc, st=3, d=0, bk=bk, sa=-1, n='4件：回合开始时移除 1 层（%s）' % ('战技' if sc == 's' else '终结技')),
          dict(y='dbuf', t='ult', tg='self', m='dmg', v=18, sc=sc, st=3, d=0, bk=bk, sa=-1, n='4件：施放终结技后移除 1 层（%s）' % ('战技' if sc == 's' else '终结技'))]
assert '当装备者的暴击伤害大于等于120%时，进入战斗后装备者的暴击率提高60%，持续到施放首次攻击后结束' in RS['305']['desc'][0]
setx(find(R[305]['p2']['eff'], '2件：暴伤 ≥120%'), d=0, nx='a', off=None, ec={'pcd': 120}, n='2件：暴击伤害 ≥120% 时进入战斗后暴击率提高 60%，到首次攻击后结束')

# ---- 光锥 ----
F.has(LR['23010']['desc'], '触发追加攻击时，消耗【梦身】，使追加攻击造成的伤害提高#3[i]%')
setx(find(L[23010]['eff'], '光锥【梦身】'), d=0, nx=['f'], n='光锥【梦身】：施放战技或终结技后下一次追加攻击伤害提高')
F.has(LR['23014']['desc'], '当队友受到攻击或消耗生命值后，装备者获得1层【月蚀】，最多叠加#2[i]层。每层【月蚀】使装备者下一次攻击造成的伤害提高#3[f1]%。叠满#2[i]层时，额外使该次攻击无视目标#4[i]%的防御力。该效果在装备者施放攻击后解除')
L[23014]['eff'] = [dict(y='dbuf', t='hpLoss', ew='others', tg='self', m='dmg', v=P(23014, 2), st=3, d=0, bk='lc', nx='a', n='光锥【月蚀】：队友受到攻击或消耗生命值后叠 1 层，每层下一次攻击伤害提高，最多 3 层（攻击后解除）'),
                   dict(y='dbuf', t='hpLoss', ew='others', tg='self', m='defIg', v=P(23014, 3), d=0, bk='lc2', nx='a', nbk=['lc', 'dmg', 3], n='光锥【月蚀】：叠满 3 层时这次攻击无视目标防御力')]
L[23014]['notes'] = ['队友受到攻击按“生命值降低时”算（被护盾全部挡住时不算）']
F.has(LR['23009']['desc'], '当装备者受到攻击或装备者消耗自身生命值后，造成的伤害提高#3[i]%，该效果在装备者施放攻击后解除')
setx(find(L[23009]['eff'], '光锥：受到攻击或消耗生命值后'), d=0, nx='a', off=None, n='光锥：受到攻击或消耗生命值后伤害提高，施放攻击后解除')
F.has(LR['24004']['desc'], '施放攻击后，每击中一名敌方目标，使攻击力额外提高#2[i]%，该效果最多叠加5次，持续至下次攻击后')
setx(find(L[24004]['eff'], '光锥：攻击后每击中 1 名敌人'), v=P(24004, 1), st=5, ph=1, nx='a', n='光锥：攻击后每击中 1 名敌人攻击力额外提高，最多 5 层，持续到下次攻击后')
F.has(LR['23056']['desc'], '战斗开始时或装备者每累计施放#2[i]次追加攻击，使装备者获得【影噬】，持续#3[i]回合')
E = L[23056]['eff']; a0, a1 = find(E, '光锥【影噬】：战斗开始时'), find(E, '光锥【影噬】：敌方全体')
a0['n'] = '光锥【影噬】：战斗开始时攻击力提高，持续 3 回合'
E += [dict(a0, t='fua', nth=4, n='光锥【影噬】：每累计施放 4 次追加攻击再获得一次（攻击力）'), dict(a1, t='fua', nth=4, n='光锥【影噬】：每累计施放 4 次追加攻击再获得一次（敌人受到的伤害）')]
F.has(LR['23031']['desc'], '装备者施放追加攻击时，获得1层【流光】，最多叠加#3[i]层。每层【流光】使装备者造成的终结技伤害无视目标#2[i]%的防御力。装备者回合结束时，移除1层【流光】')
e = find(L[23031]['eff'], '光锥【流光】'); setx(e, d=0, n='光锥【流光】：施放追加攻击时叠 1 层，每层终结技无视防御，最多 2 层')
L[23031]['eff'].append(dict(e, t='tend', sa=-1, n='光锥【流光】：自己回合结束时移除 1 层'))
F.has(LR['21024']['desc'], '当装备者受到伤害后该效果失效，下个回合结束时该效果恢复')
E = L[21024]['eff']; sp, dm = find(E, '驱散余寒'), find(E, '光锥：进入战斗后伤害提高')
setx(sp, bk='cs', n='光锥：进入战斗后速度提高'); setx(dm, n='光锥：进入战斗后伤害提高')
E += [dict(sp, t='hit2', v=0, n='光锥：受到伤害后速度提高失效'), dict(dm, t='hit2', v=0, n='光锥：受到伤害后伤害提高失效'),
      dict(sp, t='tend', n='光锥：回合结束时速度提高恢复'), dict(dm, t='tend', n='光锥：回合结束时伤害提高恢复')]
L[21024]['notes'] = ['“受到伤害”按受到攻击后算（被护盾挡住也算）；失效后在下一个自己回合结束时恢复']

# ---- 角色 ----
has('r:122406', '施放终结技后，下一次强化普攻造成的暴击伤害提高50%'); has('r:121202', '施放终结技后，下一次强化战技的伤害提高80%')
e6 = F.eid(1224, 6); setx(find(e6['eff'], 'E6：施放终结技后下一次强化普攻'), d=0, nx=['b2'], n='E6：施放终结技后下一次强化普攻暴击伤害 +50%')
e2 = F.eid(1212, 2); setx(find(e2['eff'], 'E2：施放终结技后下一次强化战技'), d=0, nx=['s'], n='E2：施放终结技后下一次强化战技伤害 +80%')
# 属性门槛分档
for cid, pre, stp, n in [(1304, '行迹杠杆', 100, '行迹杠杆：防御力超过 1600 时每超过 100 点暴击率 +2%，最多 +48%（按卡片面板防御力）'),
                         (1412, '行迹来者', 100, '行迹来者：攻击力超过 2000 时每超过 100 点暴击伤害 +18%，最多 +360%（按卡片面板攻击力）'),
                         (1501, '行迹甜蜜！笑点签售会', 100, '行迹甜蜜！笑点签售会：攻击力超过 2000 时每超过 100 点欢愉度 +5%，最多 +80%（按卡片面板攻击力）'),
                         (8009, '行迹快哉快哉', 200, '行迹快哉快哉：攻击力高于 1000 时每超过 200 点欢愉度 +10%，最多 +60%（按卡片面板攻击力）'),
                         (8010, '行迹快哉快哉', 200, '行迹快哉快哉：攻击力高于 1000 时每超过 200 点欢愉度 +10%，最多 +60%（按卡片面板攻击力）')]:
    e = find(C[cid]['eff'], pre); o = e['n']; setx(e, stp=stp, n=n); F.rebuild(cid, C[cid]['eff'], rename={o: n})

LCS = [23010, 23014, 23009, 24004, 23056, 23031, 21024]
F.finish('“下一次攻击”的增益、按回合增减层', '''<li><b>2026-11-11（下一次攻击、按回合增减层）</b>：tv 86（tools/fix86.py）。“下一次攻击”的增益现在真的在那次攻击之后移除（原来按 2 ~ 3 回合近似）：熔岩锻铸的火匠、识海迷坠的学者、拂晓之前【梦身】、三月七（巡猎）6 魂、镜流 2 魂、星体差分机（暴伤 ≥120% 自动判断）、到不了的彼岸、此身为剑【月蚀】（队友掉血叠层、满 3 层无视防御）、不息的演算（按击中人数叠层，到下次攻击后）。按回合 / 受击增减层：星如我见的领航员（回合开始、开大后 −1 层）、我将，巡征追猎（回合结束 −1 层）、街头出身的拳王（受到攻击也叠层）、一场谎言的终幕（每 4 次追加攻击再获得【影噬】）、春水初生（受到伤害后失效、回合结束恢复，含速度）。砂金杠杆、刻律德菈来者、火花、开拓者（欢愉）的属性门槛改成“每超过 N 点”分档（原来线性）。新触发“自己回合结束时”。对已有配置：这些增益比原来的近似更短（用一次就没），伤害会有变化；春水初生的速度会在受击后消失，行动顺序会变。</li>''',
'''2026-11-11：下一次攻击、按回合增减层 —— tv 86（tools/fix86.py）。新：dbuf nx / stp、actSeq、触发 tend、ec.pcd。
  未改 / 存疑：nx 只看持有者自己的攻击（全队的“我方下一次攻击”没做）；同一次行动里先触发的追加攻击会先用掉 nx 增益；镜流 2 魂按“下一次战技”；佩拉追歼（解除敌人增益）、丹恒天赋（成为技能目标）、云璃【勘破】仍是近似''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX86); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX86); for (const u of s.units) if (u.kind === "ally" && !u.sm && (' + ' || '.join('u.lc === %d' % i for i in LCS) + ' || [105, 107, 122, 131].includes(u.rA) || u.rP === 305)) applyEquip(u); } finally { S = keep; } }   // “下一次攻击”的光锥 / 遗器')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
