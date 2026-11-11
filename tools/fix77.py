"""tv 77：零散的击破 / 持续伤害角色效果 —— 雪衣 1214（预兆机杼、摧锋轴承、E4）、同谐主 8005 / 8006（E4、秘技）、大丽花 1321（弃旧恋新按队友添加弱点、秘技）、
桑博 1108（E1、E2、E4）、黑天鹅 1307（E1 按状态和属性、E2）。用法：python3 tools/fix77.py index.html <官方 json 目录>
引擎：
- wkAdd 改成队友触发（teamFire；aw 默认 = 其他人，自己用 aw self），事件里 `wkEn` = 被添加弱点的敌人，目标 "wken"；队友触发过滤 ael（字段 aEl，行动的人是某属性）。
- 伤害增益 tel（字段 tEl）= 只对某些属性的攻击者生效（挂在敌人身上的减抗，按攻击者属性）；ec 的 tq = 主目标韧性 ≥ 上限的 X%；敌人身上的 ec 按那个敌人自己判断。
- dotx 的 dmn = 只引爆层数 ≥N 的。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 77, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
D = lambda **k: dict(dict(y='dbuf', d=0, t='start', tg='self'), **k)

# ================= 引擎 =================
F.rep('''          if (!wkDepth) { wkDepth++; try { for (const e2 of fx(own, "wkAdd")) apply(e2, own, own.color); } finally { wkDepth--; } }   // 装备者为敌人添加弱点时（勿忘她的火焰）''',
      '''          if (!wkDepth) { const pw = wkEn; wkDepth++; wkEn = tg; try { teamFire("wkAdd", own); } finally { wkDepth--; wkEn = pw; } }   // 我方为敌人添加弱点时（队友触发；勿忘她的火焰 aw self、大丽花弃旧恋新 aw all）''')
F.rep('''    let brkBy = null, wkDepth = 0;''', '''    let brkBy = null, wkDepth = 0, wkEn = null;''')
F.rep('''      if (target === "efirst") { const e = U.find(u => u.kind === "enemy"); return e ? [e] : []; }''',
      '''      if (target === "efirst") { const e = U.find(u => u.kind === "enemy"); return e ? [e] : []; }
      if (target === "wken") return wkEn ? [wkEn] : [];   // 刚被添加弱点的敌人（wkAdd 触发里用）''')
F.rep('''          if (e.aE0 && !(who.kind === "ally" && !who.sm && noStdE(who))) continue;''', '''          if (e.aE0 && !(who.kind === "ally" && !who.sm && noStdE(who))) continue;
          if (e.aEl && ELW[(tplOf(ownerOf(who) || who) || {}).elem] !== e.aEl) continue;   // 只算某属性的角色（大丽花弃旧恋新：火属性）''')
# 固定削韧 / 回能看“谁添加的弱点”：自己或触发这次事件的队友
F.rep('''          if (eff.nw && !newWk(tg, own)) continue;''', '''          if (eff.nw && !newWk(tg, own) && !(evTarget && evTarget.kind === "ally" && newWk(tg, evTarget))) continue;''')
F.rep('''            if (eff.nwk && !(brkOn && src && U.some(z => z.kind === "enemy" && !z.gone && newWk(z, ownerOf(src) || src)))) continue;''',
      '''            if (eff.nwk && !(brkOn && src && U.some(z => z.kind === "enemy" && !z.gone && (newWk(z, ownerOf(src) || src) || (evTarget && evTarget.kind === "ally" && newWk(z, evTarget)))))) continue;''')
# 按攻击者属性的减抗、韧性比例条件、敌人身上的 ec
F.rep('''      en = en || U.find(x => x.kind === "enemy" && !x.gone); if (!en) return 0;
      const ds = (en.dots || []).filter(d => !d.gone), m = monOf(en);''', '''      en = u.kind === "enemy" ? u : en || U.find(x => x.kind === "enemy" && !x.gone); if (!en) return 0;   // 挂在敌人身上的按它自己
      const ds = (en.dots || []).filter(d => !d.gone), m = monOf(en);
      if (c.tq != null) { const mx = toughMax(en); if (!(mx > 0) || en.broken || num(en.tcur ?? mx) < mx * num(c.tq) / 100 - 1e-9) return 0; }   // 主目标当前韧性 ≥ 上限的 X%''')
F.rep('''      if (c.dk == null && c.dn == null && c.wb == null && c.wc == null && c.wl == null) return 1;''', '''      if (c.dk == null && c.dn == null && c.wb == null && c.wc == null && c.wl == null && c.tq == null) return 1;''')
F.rep('''return f > 0 ? [b.st, b.sc, dbV(b) * f] : null; }).filter(Boolean)''', '''return f > 0 ? (b.tEl ? [b.st, b.sc, dbV(b) * f, b.tEl] : [b.st, b.sc, dbV(b) * f]) : null; }).filter(Boolean)''')
F.rep('''        if (eff.ec) b.ec = eff.ec;''', '''        if (eff.ec) b.ec = eff.ec; if (eff.tEl) b.tEl = eff.tEl;   // tEl：只对这些属性的攻击者生效''')
F.rep('''      const all = [...U.filter(u => u.kind === "enemy"), EV0].map(dbSnap).filter(x => x.length);''', '''      const all = [...U.filter(u => u.kind === "enemy"), EV0].map(u => dbSnap(u)).filter(x => x.length);''')
F.rep('''    const D = st => dsum(DB0, st, e.key), ED = st => dsum(EDB, st, e.key);''', '''    const EL1 = ({ Physical: "物", Fire: "火", Ice: "冰", Thunder: "雷", Lightning: "雷", Wind: "风", Quantum: "量", Imaginary: "虚" })[(T0 || {}).elem] || "";
    const EDB1 = EDB.some(x => x[3]) ? EDB.filter(x => !x[3] || x[3].includes(EL1)) : EDB;   // 按攻击者属性的减益（黑天鹅 E1）
    const D = st => dsum(DB0, st, e.key), ED = st => dsum(EDB1, st, e.key);''')
F.rep('''if ((eff.mode !== "own" || (own && d.src === own.id)) && (!eff.dk || d.k === eff.dk)) dotHit(tg, d, v / 100, "det");''',
      '''if ((eff.mode !== "own" || (own && d.src === own.id)) && (!eff.dk || d.k === eff.dk) && !(num(eff.dmn) > 0 && num(d.n) < num(eff.dmn))) dotHit(tg, d, v / 100, "det");''')   # dmn：只引爆层数 ≥N 的（这一行后面还有 finally，不能加 // 注释）
F.rep('''      if (x.bby) e.brkSelf = 1;''', '''      if (x.ael) e.aEl = x.ael; if (x.tel) e.tEl = x.tel; if (x.dmn) e.dmn = x.dmn;
      if (x.bby) e.brkSelf = 1;''')
F.rep('''    if (e.ec) h.push("出手时按主目标的状态算");''', '''    if (e.ec) h.push("出手时按主目标的状态算");
    if (e.aEl) h.push(`只算${e.aEl}属性角色`);
    if (e.tEl) h.push(`只对${e.tEl.split("").join(" / ")}属性的攻击生效`);''')
F.s = F.s.replace('["wkAdd", "为敌人添加弱点时"]', '["wkAdd", "我方为敌人添加弱点时"]')
F.rep('''spd: "速度", el: "欢愉度" })[e.srcS]''', '''spd: "速度", el: "欢愉度", be: "击破特攻" })[e.srcS]''')
F.rep('''["el", "= 施放者欢愉度的 X%"]], e.srcS || "")''', '''["el", "= 施放者欢愉度的 X%"], ["be", "= 施放者击破特攻的 X%"]], e.srcS || "")''')

# ================= 勿忘她的火焰：自己添加才算 =================
L = {c['id']: c for c in F.DB['lcs']}
e = [x for x in L[23050]['eff'] if x.get('t') == 'wkAdd']; assert len(e) == 1; e[0]['aw'] = 'self'

# ================= 雪衣 =================
c = C[1214]
hast(1214, '预兆机杼', '提高数值等同于击破特攻的#1[i]%，最多使造成的伤害提高#2[i]%'); hast(1214, '摧锋轴承', '如果敌方目标当前韧性大于等于其自身韧性上限的#1[i]%，施放终结技时造成的伤害提高#2[i]%')
has('r:121404', '施放终结技时，击破特攻提高40%，持续2回合')
old = {e['n'] for e in c['eff']}
for e in c['eff']:
    if (e.get('n') or '').startswith('行迹预兆机杼'): e.pop('off', None); e.update(ss='be', v=100, cap=240, n='行迹预兆机杼：伤害提高，等同于击破特攻的 100%，最多 240%（按卡片击破特攻）')
    if (e.get('n') or '').startswith('行迹摧锋轴承'): e.pop('off', None); e.update(ec={'tq': 50}, n='行迹摧锋轴承：敌方目标当前韧性 ≥ 韧性上限 50% 时，终结技伤害 +10%（按主目标；要放带韧性的敌人）')
on = [n for n, t in F.OLD[1214]]
ren = {a: b for a, b in zip([n for n in on if n.startswith('行迹预兆机杼') or n.startswith('行迹摧锋轴承')], [e['n'] for e in c['eff'] if e['n'].startswith('行迹预兆机杼') or e['n'].startswith('行迹摧锋轴承')])}
F.rebuild(1214, list(c['eff']), rename=ren)
e4 = F.eid(1214, 4); e4['eff'] = e4.get('eff', []) + [dict(y='dbuf', t='ult', tg='self', m='be', v=40, d=2, bk='e4', n='E4：施放终结技时击破特攻 +40%，持续 2 回合')]

# ================= 同谐主 =================
for cid in (8005, 8006):
    has('r:%d04' % cid, '提高数值等同于开拓者15%的击破特攻'); has(str(cid * 100 + 7), '下一次战斗开始时使我方全体的击破特攻提高#1[i]%，持续#2[i]回合')
    c = C[cid]; c['notes'] = [n for n in c.get('notes', []) if '秘技、E4 还没做' not in n]
    F.rebuild(cid, list(c['eff']) + [dict(y='dbuf', t='start', tg='team', m='be', v=30, d=2, bk='mj', off=1, n='秘技即刻！独奏团：战斗开始时我方全体击破特攻 +30%，持续 2 回合（用了秘技再启用）')])
    e4 = F.eid(cid, 4); e4['eff'] = e4.get('eff', []) + [D(tg='others', m='be', ss='be', v=15, bk='e4', n='E4：开拓者在场时，其他队友击破特攻提高开拓者击破特攻的 15%（按卡片击破特攻）')]

# ================= 大丽花 =================
c = C[1321]
hast(1321, '弃旧，恋新', '我方目标为敌方目标添加弱点时，速度提高#3[i]%，持续#4[i]回合。若我方火属性角色施放攻击期间添加过弱点，则攻击后对每个添加弱点的目标额外造成#5[i]点火属性固定削韧')
has('132107', '与处于特殊领域内的敌人进入战斗后，大丽花立即开启战技的结界')
eff = [e for e in c['eff'] if not (e.get('n') or '').startswith('行迹弃旧，恋新')]
old_q = [n for n, t in F.OLD[1321] if n and n.startswith('行迹弃旧，恋新')]
nq = [dict(y='spd', t='wkAdd', aw='all', tg='self', v=30, d=2, bk='qjs', n='行迹弃旧，恋新：我方目标为敌方目标添加弱点时，大丽花速度 +30%，持续 2 回合'),
      dict(y='tfix', t='wkAdd', aw='all', ael='火', tg='wken', v=20, nw=1, bk='qj', n='行迹弃旧，恋新：我方火属性角色（含大丽花）添加弱点时，对被添加弱点的目标额外造成 20 点火属性固定削韧（敌人原本就有这个弱点时不算）'),
      dict(y='energy', t='wkAdd', aw='all', ael='火', tg='self', m='maxp', v=10, ecx=50, nwk=1, ptn=1, n='行迹弃旧，恋新：我方火属性角色添加过弱点时，大丽花恢复 10% 能量上限的能量，最多恢复到 50%（每回合 1 次）')]
mj = [dict(y='state', t='start', tg='self', sn='大丽花结界', v=1, d=3, ts=1, off=1, n='秘技心，是最好的坟茔：进入战斗后立即开启战技的结界（用了秘技再启用，下面两条一起开）'),
      dict(y='dbuf', d=0, t='start', tg='team', m='bef', v=50, bk='st:大丽花结界#mj', off=1, n='秘技：开局结界的我方全体弱点击破效率 +50%'),
      dict(y='dbuf', d=0, t='start', tg='team', m='sbkA', v=1, bk='st:大丽花结界#mja', off=1, n='秘技：开局结界里没破韧的敌人承受的削韧也转超击破')]
c['notes'] = [n for n in c.get('notes', []) if '弃旧，恋新：其他火属性队友' not in n]
F.rebuild(1321, eff + nq + mj, notes=['行迹弃旧，恋新：“攻击后”的固定削韧和回能在添加弱点的那一刻结算；秘技的开战削韧转超击破没做（开战削韧不模拟）'])

# ================= 桑博 =================
c = C[1108]
has('r:110801', '施放战技时，对敌方随机单体额外造成1次伤害'); has('r:110802', '风化状态下的敌方目标被消灭时，使敌方全体有100%的基础概率叠加1层等同于天赋的风化状态')
has('r:110804', '战技击中风化状态大于等于5层的敌方目标时，使其当前承受的风化状态立即产生相当于原伤害8%的伤害')
sk = [e for e in c['eff'] if e.get('y') == 'dot' and e.get('t') == 'skill']; assert len(sk) == 1
c['notes'] = [n for n in c.get('notes', []) if 'E1 多出的 1 段战技' not in n]
F.touch(1108)
e1 = F.eid(1108, 1); e1['eff'] = e1.get('eff', []) + [dict(sk[0], sa=1, n='E1：施放战技时额外造成 1 次伤害，再使目标陷入 1 层风化（按主目标；伤害只算原来 5 段）')]
e2 = F.eid(1108, 2); e2['eff'] = e2.get('eff', []) + [dict({k: v for k, v in sk[0].items() if k not in ('sa',)}, t='kill', tg='enemies', n='E2：风化的敌方目标被消灭时，敌方全体叠加 1 层风化（消灭用手动事件触发）')]
e4 = F.eid(1108, 4); e4['eff'] = e4.get('eff', []) + [dict(y='dotx', t='skill', tg='efirst', v=8, dk='风化', dmn=5, n='E4：战技击中风化 ≥5 层的敌方目标时，其风化立即产生原伤害 8% 的伤害（按主目标）')]
C[1108]['notes'] = [n for n in C[1108].get('notes', [])] + ['E1 多出的 1 段战技伤害没算进伤害数字']

# ================= 黑天鹅 =================
c = C[1307]
has('r:130701', '当黑天鹅处于可战斗状态时，处于风化、裂伤、灼烧、触电状态下的敌方目标对应的风、物理、火、雷属性抗性分别降低25%')
has('r:130702', '【奥迹】状态下的敌方目标被消灭时，有100%的基础概率使相邻目标陷入6层【奥迹】')
e1 = F.eid(1307, 1); e1['eff'] = [x for x in e1['eff'] if x.get('bk') != 'e1'] + [
    dict(y='dbuf', t='start', tg='enemies', m='resRed', v=25, d=0, bk='e1' + k, tel=el, ec={'dk': [k]}, n='E1：处于%s状态的敌方目标%s属性抗性 −25%%（只对%s属性的攻击；【奥迹】视为四种状态都有）' % (k, el if el != '物' else '物理', el if el != '物' else '物理'))
    for k, el in (('风化', '风'), ('裂伤', '物'), ('灼烧', '火'), ('触电', '雷'))]
ax = [e for e in c['eff'] if e.get('y') == 'dot' and e.get('dk') == '奥迹' and (e.get('n') or '').startswith('【强化版】天赋')]; assert len(ax) == 1
e2 = F.eid(1307, 2); e2['eff'] = e2.get('eff', []) + [dict({k: v for k, v in ax[0].items() if k not in ('t', 'tg', 'n', 'sa', 'down', 'dki', 'aw')}, t='kill', tg='eadj', sa=6, n='E2：【奥迹】状态下的敌方目标被消灭时，相邻目标陷入 6 层【奥迹】（消灭用手动事件触发；相邻按第 2、3 个敌人）')]
c['notes'] = [n.replace('、E2 没做', '') for n in c.get('notes', [])]

F.finish('零散的击破 / 持续伤害角色效果（雪衣、同谐主、大丽花、桑博、黑天鹅）', '''<li><b>2026-11-11（雪衣、同谐主、大丽花、桑博、黑天鹅的击破 / 持续伤害效果）</b>：tv 77（tools/fix77.py）。<b>雪衣</b>：预兆机杼按卡片击破特攻自动算（最多 +240%），摧锋轴承按敌人当前韧性 ≥50% 自动判断，E4 终结技击破特攻 +40%。<b>同谐主</b>：E4 其他队友击破特攻 + 开拓者击破特攻的 15%，秘技全队击破特攻 +30%（默认关）。<b>大丽花</b>：弃旧恋新改成任何队友添加弱点都加速，火属性队友（比如流萤强化战技）添加弱点也会触发 20 点固定削韧和回能；秘技开局开结界（默认关）。<b>桑博</b>：E1 多 1 层风化、E2（消灭时，手动事件）、E4 风化 ≥5 层时引爆 8%。<b>黑天鹅</b>：E1 改成只对处于对应状态的敌人、只对对应属性的攻击减抗（以前按所有攻击都减）；E2（消灭时相邻目标 6 层【奥迹】，手动事件）。勿忘她的火焰的回战技点改成只算装备者自己添加的弱点。只在放了敌人卡时有变化。</li>''',
'''2026-11-11：雪衣（1214）、同谐主（8005 / 8006）、大丽花（1321）、桑博（1108）、黑天鹅（1307）—— tv 77（tools/fix77.py）。新：wkAdd 改成队友触发 + 目标 wken + 过滤 ael、伤害增益 tel、ec 的 tq、dotx 的 dmn。
  未改 / 存疑：雪衣终结技“削减的韧性越多伤害越高”仍按满额手动开、【恶报】按削韧量叠层没做；同谐主 E4、雪衣预兆机杼按卡片击破特攻（不含战斗中的加成）；大丽花弃旧恋新的固定削韧仍只算“原本没有的弱点”，速度提高按任意添加；桑博 E1 第 6 段伤害没算；黑天鹅 E6 / 终结技的 50% 额外层数没算。''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX77); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX77); for (const u of s.units) if (u.kind === "ally" && !u.sm && u.lc === 23050) applyEquip(u); } finally { S = keep; } }   // 勿忘她的火焰的触发改了')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
