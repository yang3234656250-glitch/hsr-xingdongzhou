"""tv 83：嘲讽、虚弱（敌人造成的伤害降低）、更多受到的伤害降低、按护盾生效的增益、角色倒下时它给的“在场时”增益和状态一起消失。
用法：python3 tools/fix83.py index.html <官方 json 目录>
引擎：敌人身上的状态【嘲讽】（by = 施加者）：敌人的单体 / 扩散攻击改打施加者（施加者倒下就按卡片设置）；群攻不变。
dbuf 新属性 wkn（虚弱：敌人造成的伤害降低，挂在敌人身上，同一个敌人身上的相加）：敌人打我方时 × (1 − 虚弱)。
伤害增益条件 ec：sh = 1（持有护盾）/ "own"（持有这个增益来源给的护盾）/ 组名；shn = [上限, "o" 不算自己 | "a" 算自己] 按持有护盾的角色数倍乘；st = 持有者有这个状态。
“我方全体（含之后登场的）”的增益现在也检查 ec（以前没有带条件的全队增益）。效果字段 alv：施加者倒下时这个增益消失；倒下的角色身上的状态全部结束（跟着状态走的增益一起消失）。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 83, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('''      if (x.shk) e.shk = x.shk;''', '''      if (x.alv) e.alv = 1;   // 施加者倒下时这个增益消失（符玄【避厄】）
      if (x.shk) e.shk = x.shk;''')
F.rep('''        if (eff.ec) b.ec = eff.ec; if (eff.tEl) b.tEl = eff.tEl;''', '''        if (eff.ec) b.ec = eff.ec; if (eff.tEl) b.tEl = eff.tEl; if (eff.alv) b.alv = 1;''')
F.rep('''      if (c.sh && !(shOf(u) > 0)) return 0;   // 持有者持有护盾时（记忆的质料减伤）
      if (c.be != null && beOf(u) + beTeam() < num(c.be) - 1e-9) return 0;
      if (c.dk == null && c.dn == null && c.wb == null && c.wc == null && c.wl == null && c.tq == null) return 1;''', '''      if (c.sh && shTrack) { const ok = c.sh === "own" ? Object.entries(u.shd || {}).some(([k, z]) => k.startsWith(b.src + ":") && z.v > 0) : shOf(u, c.sh === 1 || c.sh === true ? null : c.sh) > 0; if (!ok) return 0; }   // 持有者持有护盾（own = 这个增益的来源给的护盾；其他字符串 = 这一组，砂金【坚垣筹码】）
      if (c.st && !hasSt(u, c.st)) return 0;   // 持有者有这个状态（白露【生息】）
      let f0 = 1;
      if (Array.isArray(c.shn)) { const n = !shTrack ? num(c.shn[0]) : U.filter(z => z.kind === "ally" && !z.sm && !z.gone && (c.shn[1] !== "o" || z !== u) && shOf(z) > 0).length; f0 = Math.min(num(c.shn[0]), n); if (!(f0 > 0)) return 0; }   // 按持有护盾的角色数（o = 不算自己）
      if (c.be != null && beOf(u) + beTeam() < num(c.be) - 1e-9) return 0;
      if (c.dk == null && c.dn == null && c.wb == null && c.wc == null && c.wl == null && c.tq == null) return f0;''')
F.rep('''      let f = 1;
      if (c.dn != null) f *= Math.min(num(c.dn), ds.length);''', '''      let f = f0;
      if (c.dn != null) f *= Math.min(num(c.dn), ds.length);''')
F.rep('''(!b.path || (tplOf(ownerOf(u) || u) || {}).path === b.path && !u.sm)).map(b => [b.st, b.sc, dbV(b)]) : []);''',
      '''(!b.path || (tplOf(ownerOf(u) || u) || {}).path === b.path && !u.sm)).map(b => { const f = b.ec ? ecF(b, u, en) : 1; return f > 0 ? [b.st, b.sc, dbV(b) * f] : null; }).filter(Boolean) : []);   // 全队增益也按持有者检查条件''')
F.rep('''        if (eff.type === "break" || eff.type === "kill" || eff.type === "hit") { fireEv(eff.type, tg);''', '''        if (eff.type === "hit" && tg.gone) continue;   // 群攻中途倒下的不再挨打
        if (eff.type === "break" || eff.type === "kill" || eff.type === "hit") { fireEv(eff.type, tg);''')
F.rep('''const onEnemy = ["vuln", "defRed", "resRed"].includes(eff.mode)''', '''const onEnemy = ["vuln", "defRed", "resRed", "wkn"].includes(eff.mode)''')
F.rep('''      d *= drOf(tg);''', '''      d *= drOf(tg) * (src && src.kind === "enemy" ? Math.max(0, 1 - dbSnap(src).reduce((p, x) => p + (x[0] === "wkn" ? num(x[2]) : 0), 0) / 100) : 1);   // 受到的伤害降低（相乘）× 敌人的虚弱''')
F.rep('''      tg.gone = true; tg.shd = {}; marks.push({ t, uid: tg.id, label: "倒下", color: "var(--enemy)", from: tg.name });''',
      '''      tg.gone = true; tg.shd = {}; marks.push({ t, uid: tg.id, label: "倒下", color: "var(--enemy)", from: tg.name });
      for (const z of [...U, EV0, TEAM0]) z.buffs = z.buffs.filter(b => !(b.alv && b.src === tg.id));   // 它在场时才有的增益（符玄【避厄】）
      for (const k of Object.keys(tg.st || {})) endSt(tg, k);   // 它身上的状态结束（符玄【穷观阵】和跟着它的【鉴知】）''')
F.rep('''        const main = actor.atkWho === "all" ? null : actor.atkWho === "rot" ? pool[(actor.turns - 1) % Math.max(1, pool.length)] : pool.find(x => x.id === actor.atkWho);''',
      '''        const tzs = actor.st && actor.st["嘲讽"], tz = tzs && tzs.by && byId[tzs.by] && pool.includes(byId[tzs.by]) ? byId[tzs.by] : null, aw = tz ? tz.id : actor.atkWho;   // 嘲讽：单体 / 扩散攻击改打施加嘲讽的角色
        const main = aw === "all" ? null : aw === "rot" ? pool[(actor.turns - 1) % Math.max(1, pool.length)] : pool.find(x => x.id === aw);''')
F.rep('''          if (HITALL.includes(sk.t) || actor.atkWho === "all") tgs =''', '''          if (HITALL.includes(sk.t) || aw === "all") tgs =''')
F.rep('''          const tgs = actor.atkWho === "all" ? pool : main ? [main] : [];''', '''          const tgs = aw === "all" ? pool : main ? [main] : [];''')
F.rep('''    if (e.ec) h.push(e.ec.sh ? "持有护盾时生效" : "出手时按主目标的状态算");''',
      '''    if (e.ec) h.push(e.ec.sh === "own" ? "持有自己给的护盾时生效" : e.ec.sh ? "持有护盾时生效" : Array.isArray(e.ec.shn) ? `按持有护盾的${e.ec.shn[1] === "o" ? "队友" : "角色"}数算（最多 ${e.ec.shn[0]} 名）` : e.ec.st ? `持有【${e.ec.st}】时生效` : "出手时按主目标的状态算");
    if (e.alv) h.push("施加者倒下时消失");''')
F.rep('''["shB", "提供的护盾量 %"]''', '''["shB", "提供的护盾量 %"], ["wkn", "虚弱：敌人造成的伤害降低 %"]''')
F.rep('''shB: "提供的护盾量", cr: "暴击率"''', '''shB: "提供的护盾量", wkn: "虚弱", cr: "暴击率"''')
F.rep('''shB: "提供的护盾量%", cr: "暴击率"''', '''shB: "提供的护盾量%", wkn: "虚弱%", cr: "暴击率"''')
F.rep('''（几个护盾按最大的算；符玄【穷观阵】先分走 65%）''', '''（几个护盾按最大的算；符玄【穷观阵】先分走 65%；敌人被虚弱时伤害降低；被嘲讽的敌人单体攻击打施加者）''')

def setx(e, **kw):
    for k, v in kw.items():
        if v is None: e.pop(k, None)
        else: e[k] = v
    return e
TZ = '嘲讽'

# ---- 开拓者•存护：战技嘲讽 ----
for cid in (8003, 8004):
    k = str(cid); has(k + '02', '此外有#2[i]%基础概率使敌方全体陷入嘲讽状态，持续#3[i]回合')
    sk = prm(k + '02', 10); assert sk[1] == 1 and sk[2] == 1
    c = C[cid]; E = c['eff']
    o = [e for e in E if e.get('m') == 'dr' and e.get('bk') == 'zj']; assert len(o) == 1; on = o[0]['n']
    nn = '战技：施放后开拓者受到的伤害降低 50%，持续 1 回合'; o[0]['n'] = nn
    i = E.index(o[0]); E.insert(i, dict(y='state', t='skill', tg='enemies', sn=TZ, v=1, d=1, n='战技：100% 基础概率使敌方全体陷入嘲讽，持续 1 回合（被嘲讽的敌人单体攻击打开拓者）'))
    c['notes'] = ['嘲讽按必定命中算；受到的伤害降低和护盾只在“敌人打我方掉血”开着时影响生命值']
    F.rebuild(cid, E, rename={on: nn})

# ---- 万敌：终结技嘲讽目标和相邻目标 ----
has('140403', '并使目标与相邻目标陷入嘲讽状态，持续#4[i]回合'); assert prm('140403', 10)[3] == 2
c = C[1404]; E = c['eff']; i = next(k for k, e in enumerate(E) if e.get('t') == 'ult')
E[i:i] = [dict(y='state', t='ult', tg='efirst', sn=TZ, v=1, d=2, n='终结技：使目标陷入嘲讽，持续 2 回合（被嘲讽的敌人单体攻击打万敌）'),
          dict(y='state', t='ult', tg='eadj', sn=TZ, v=1, d=2, n='终结技：使相邻目标陷入嘲讽，持续 2 回合')]
F.rebuild(1404, E)

# ---- 千冶•刃：普攻 / 强化普攻嘲讽目标；结界中受到的伤害降低 ----
has('150701', '并使目标陷入嘲讽状态，持续1回合'); has('150708', '并使目标陷入嘲讽状态，持续1回合')
hast(1507, '千锻魂', '结界持续期间，被敌方攻击的概率提高，自身受到的伤害降低#2[i]%');
c = C[1507]; E = c['eff']
E += [dict(y='state', t='basic', tg='efirst', sn=TZ, v=1, d=1, n='普攻 / 强化普攻：使目标陷入嘲讽，持续 1 回合'),
      dict(y='dbuf', t='ult', tg='self', m='dr', v=50, d=0, bk='st:无量忿怒#dr', ns='!无量忿怒', n='行迹千锻魂：结界持续期间受到的伤害降低 50%')]
F.rebuild(1507, E)

# ---- 波提欧：【绝命对峙】的敌人陷入嘲讽 ----
has('131502', '处于【绝命对峙】的敌方目标陷入嘲讽状态'); assert prm('131502', 10)[2] == 2
c = C[1315]; E = c['eff']; i = next(k for k, e in enumerate(E) if e.get('sn') == '绝命对峙')
E.insert(i + 1, dict(y='state', t='skill', tg='efirst', sn=TZ, v=1, d=2, ts='src', n='战技：【绝命对峙】的敌人陷入嘲讽，持续 2 回合（波提欧每回合开始时 −1）'))
c['notes'] = [n for n in c.get('notes', []) if '蛇之上行' not in n] + ['行迹蛇之上行（受到未处于【绝命对峙】目标的伤害降低）没做']
F.rebuild(1315, E)

# ---- 受到的伤害降低 ----
has('110704', '克拉拉在史瓦罗的保护下受到敌方目标攻击的伤害降低#3[i]%'); assert r4(prm('110704', 10)[2]) == 0.1
c = C[1107]; c['eff'].append(dict(y='dbuf', t='start', tg='self', m='dr', v=10, d=0, bk='slw', n='天赋：在史瓦罗的保护下受到的伤害降低 10%'))
c['notes'] = c.get('notes', []) + ['E4 受到攻击后受到的伤害降低 30%（持续到下个回合开始）没做']
F.rebuild(1107, c['eff'])
hast(1211, '鳞渊福泽', '拥有【生息】的角色受到的伤害降低#1[i]%')
c = C[1211]; c['eff'].append(dict(y='dbuf', t='start', tg='team', m='dr', v=10, d=0, bk='lyf', ec={'st': '生息'}, n='行迹鳞渊福泽：拥有【生息】的角色受到的伤害降低 10%'))
F.rebuild(1211, c['eff'])
has('r:141404', '【同袍】受到的伤害降低20%')
e4 = F.eid(1414, 4); e4['eff'] = [x for x in e4['eff'] if x.get('m') != 'dr'] + [dict(y='dbuf', t='skill', tg='skpick', m='dr', v=20, d=0, bk='e4', mv=1, n='E4 金石立誓，此身为舟：【同袍】受到的伤害降低 20%')]
c = C[1208]; z = [e for e in c['eff'] if e.get('m') == 'dr']; assert len(z) == 1; z[0]['alv'] = 1
c['notes'] = [n.replace('；符玄倒下后【避厄】没有自动去掉', '；符玄倒下时【避厄】【穷观阵】【鉴知】一起消失') for n in c['notes']]
F.rebuild(1208, c['eff'])

# ---- 虚弱 ----
has('140602', '有#6[i]%的基础概率使指定敌方单体及其相邻目标陷入虚弱状态，造成的伤害降低#3[i]%'); p = prm('140602', 10); assert r4(p[2]) == 0.1 and p[3] == 2
c = C[1406]; E = c['eff']; i = next(k for k, e in enumerate(E) if e.get('t') == 'skill')
E.insert(i, dict(y='dbuf', t='skill', tg='enemies', m='wkn', v=10, d=2, bk='xr', n='战技：指定敌方单体及其相邻目标陷入虚弱，造成的伤害降低 10%，持续 2 回合（按命中算；页面按敌方全体）'))
F.rebuild(1406, E)
has('110507', '虚弱状态下的敌方目标对我方造成的伤害降低#2[i]%，持续#3[i]回合'); p = prm('110507', 1); assert r4(p[1]) == 0.3 and p[2] == 1
c = C[1105]; c['eff'].append(dict(y='dbuf', t='start', tg='enemies', m='wkn', v=30, d=1, bk='tech', off=1, n='秘技催眠研习：进入战斗后敌方全体陷入虚弱，造成的伤害降低 30%，持续 1 回合（用了秘技再启用）'))
F.rebuild(1105, c['eff'])
has('r:120304', '结界生效时使敌方目标陷入虚弱状态，造成的伤害降低12%')
e4 = F.eid(1203, 4); e4['eff'] = [x for x in e4['eff'] if x.get('m') != 'wkn'] + [dict(y='dbuf', t='cnt', tg='enemies', m='wkn', v=12, d=0, bk='st:结界#e4', n='E4 荆冠审判：结界生效时敌人陷入虚弱，造成的伤害降低 12%（结界结束时消失）')]

# ---- 按护盾生效的增益 ----
c = C[1304]
has('r:130401', '持有【坚垣筹码】的我方目标暴击伤害提高20%'); has('r:130406', '每有1个队友持有护盾，砂金造成的伤害提高50%，最高不超过150%')
e1 = F.eid(1304, 1); z = [x for x in e1['eff'] if x.get('y') == 'dbuf' and x.get('m') == 'cd']; assert len(z) == 1
setx(z[0], ec={'sh': 'jy'}, n='E1：持有【坚垣筹码】的我方目标暴击伤害 +20%')
e6 = F.eid(1304, 6); z = [x for x in e6['eff'] if x.get('y') == 'dbuf' and x.get('m') == 'dmg']; assert len(z) == 1
setx(z[0], v=50, ec={'shn': [3, 'o']}, n='E6 猎鹿游戏：每有 1 个队友持有护盾，砂金造成的伤害 +50%（最多 150%）')
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8'))
L = {x['id']: x for x in F.DB['lcs']}
F.has(LR['21053']['desc'], '使装备者提供的护盾量提高#1[i]%，我方目标持有护盾时，造成的伤害提高#2[i]%'); P = LR['21053']['params']
L[21053]['eff'] = [dict(y='dbuf', t='start', tg='self', m='shB', v=[r4(p[0] * 100) for p in P], d=0, bk='lcs', n='光锥：提供的护盾量提高 12%'),
                   dict(y='dbuf', t='start', tg='team', m='dmg', v=[r4(p[1] * 100) for p in P], d=0, bk='lc', ec={'sh': 1}, n='光锥：我方目标持有护盾时造成的伤害提高 12%')]
L[21053]['notes'] = []
F.has(LR['21043']['desc'], '场上每有一名持有护盾的角色，装备者造成的伤害提高#2[i]%'); P = LR['21043']['params']
L[21043]['eff'] = [dict(y='dbuf', t='start', tg='self', m='dmg', v=[r4(p[1] * 100) for p in P], d=0, bk='lc', ec={'shn': [4, 'a']}, n='光锥：场上每有 1 名持有护盾的角色，造成的伤害提高 4%')]
RS = json.load(open(sys.argv[2] + '/relic_sets.json', encoding='utf-8'))
assert RS['128']['desc'] == ['提供的护盾量提高10%。', '使装备者提供的护盾量提高12%，我方目标持有装备者提供的护盾时，暴击伤害提高15%。'], RS['128']['desc']
R = {x['id']: x for x in F.DB['relics']}
R[128]['p2']['eff'] = [dict(y='dbuf', t='start', tg='self', m='shB', v=10, d=0, bk='r2', n='2件：提供的护盾量提高 10%')]
R[128]['p4']['eff'] = [dict(y='dbuf', t='start', tg='self', m='shB', v=12, d=0, bk='r4s', n='4件：提供的护盾量再提高 12%'),
                       dict(y='dbuf', t='start', tg='team', m='cd', v=15, d=0, bk='r', ec={'sh': 'own'}, n='4件：持有装备者提供的护盾时暴击伤害提高 15%')]

F.finish('嘲讽、虚弱、更多减伤、按护盾生效的增益', '''<li><b>2026-11-11（嘲讽、虚弱）</b>：tv 83（tools/fix83.py）。<b>嘲讽</b>：被嘲讽的敌人，单体 / 扩散攻击改打施加嘲讽的角色（群攻不变；施加者倒下后恢复卡片设置）——开拓者•存护战技（敌方全体 1 回合）、万敌终结技（目标和相邻 2 回合）、千冶•刃普攻 / 强化普攻（1 回合）、波提欧【绝命对峙】。<b>虚弱</b>（新增益属性：敌人造成的伤害降低）：赛飞儿战技 10%、罗刹 E4 结界期间 12%、娜塔莎秘技 30%（默认关）。<b>受到的伤害降低</b>补了克拉拉天赋 10%、白露【生息】10%、丹恒•腾荒 E4【同袍】20%、千冶•刃结界 50%。<b>按护盾生效</b>：砂金 E1（持有【坚垣筹码】暴伤 +20%）、E6（每个持盾队友 +50%）、愿旅途永远坦然、两个人的演唱会、自匿星芒的隐士（含提供的护盾量）现在按模拟里谁真的有护盾算。符玄倒下时【避厄】【穷观阵】【鉴知】一起消失；倒下的角色身上的状态都会结束。对已有配置：带这些角色时，敌人打谁会因为嘲讽变化（受击回能、反击跟着变）；砂金 E6 / 光锥的伤害按实际持盾人数算，可能比原来的“按一直有护盾”低。</li>''',
'''2026-11-11：嘲讽、虚弱、减伤、按护盾生效的增益 —— tv 83（tools/fix83.py）。新：敌人状态【嘲讽】、dbuf wkn、ec.sh（own / 组）/ shn / st、全队增益检查 ec、效果字段 alv、倒下时结束状态。
  未改 / 存疑：嘲讽按必定命中；云璃终结技的嘲讽（持续到下一个任意回合结束）和【格挡】减伤没做；赛飞儿的虚弱按敌方全体；克拉拉 E4、素裳 E2、波提欧蛇之上行、真珠【好活当赏】抵御值、罗刹 E2 护盾没做；“被敌方攻击的概率提高”（杰帕德、三月七、玲可、千冶•刃结界）是概率，没做''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX83); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX83); for (const u of s.units) if (u.kind === "ally" && !u.sm && (u.lc === 21053 || u.lc === 21043 || u.rA === 128 || u.rB === 128)) applyEquip(u); } finally { S = keep; } }   // 愿旅途永远坦然、两个人的演唱会、自匿星芒的隐士改了')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
