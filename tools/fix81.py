"""tv 81：模拟敌我掉血（伤害设置里的两个开关，默认关）。
用法：先 python3 tools/build_monstat.py index.html <敌人数据目录>（敌人攻击力 / 生命值 / 技能倍率），再 python3 tools/fix81.py index.html <官方 json 目录>
① 敌人打我方（S.dg.eHit）：敌人模板按官方数据：攻击力 = 1 级攻击力（基础 × 修正 × 精英组）× 等级成长；伤害 = 攻击力 × 技能倍率 × 防御区（1 − 防御 / (防御 + 200 + 10 × 敌人等级)）；
   扩散按主 / 相邻倍率，弹射按总段数平均分给被打的人。扣我方当前生命值，降到 0 = 受到致命攻击：触发“我方目标受到致命攻击时”（fatal）的效果，没被救回 = 倒下（不再行动，召唤物一起离场）。
② 我方伤害扣敌人生命值（S.dg.eHp）：每次行动 / 开大 / 追击 / 持续伤害 / 击破 / 助战技的伤害（和伤害显示同一套算法）在模拟里扣到敌人身上，
   群攻每个敌人按单体倍率、扩散按相邻倍率、弹射算主目标；生命值打空 = 被消灭（离场，击杀者 +10 能量、触发“消灭敌人”效果），敌人全部消灭时战斗结束。
敌人卡可以改攻击力（eatk）、生命值（ehp）；手动敌人只有填了生命值才会被打死。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 81, sys.argv[2])
C, has, hast = F.C, F.has, F.hast

# ================= 设置 =================
F.rep('''  const DGC = { lv: 95, res: 20, vuln: 0, defR: 0, pen: 0, weak: false, broken: false, noBrk: false, v: 1 };''',
      '''  const DGC = { lv: 95, res: 20, vuln: 0, defR: 0, pen: 0, weak: false, broken: false, noBrk: false, eHit: false, eHp: false, v: 1 };''')
F.rep('''<input type="checkbox" id="dg-nobrk" data-dg="noBrk"> 不模拟韧性和击破</label>''', '''<input type="checkbox" id="dg-nobrk" data-dg="noBrk"> 不模拟韧性和击破</label>
                  <label for="dg-ehit" title="勾上 = 敌人模板按官方攻击力和技能倍率打我方，扣当前生命值；降到 0 时触发“受到致命攻击时”的效果，没被救回就倒下（不再行动）。我方的生命值、防御力请在卡片上填面板"><input type="checkbox" id="dg-ehit" data-dg="eHit"> 敌人打我方掉血</label>
                  <label for="dg-ehp" title="勾上 = 我方伤害（和伤害显示同一套算法）扣敌人生命值，打空就被消灭：离场、击杀者回 10 点能量、触发“消灭敌人”的效果；敌人全部消灭时战斗结束。会让行动轴跟着你填的面板变"><input type="checkbox" id="dg-ehp" data-dg="eHp"> 我方伤害扣敌人生命值（打空 = 消灭）</label>''')

# ================= 模拟：敌人属性 / 掉血 / 消灭 =================
F.rep('''    const brkOn = !(S.dg && S.dg.noBrk);''', '''    const brkOn = !(S.dg && S.dg.noBrk);
    const eHitOn = !!(S.dg && S.dg.eHit), eHpOn = !!(S.dg && S.dg.eHp);   // 模拟敌我掉血
    const eLvOf = en => Math.max(1, Math.min(MON.hl ? MON.hl.length : 1, Math.round(num(en.lv, 95))));
    const eAtkOf = en => { if (num(en.eatk) > 0) return num(en.eatk); const m = monOf(en); return m && m.a && MON.hl ? m.a * MON.hl[eLvOf(en) - 1][0] : 0; };
    const eHpMaxOf = en => { if (num(en.ehp) > 0) return num(en.ehp); const m = monOf(en); return m && m.h && MON.hl ? m.h * MON.hl[eLvOf(en) - 1][1] : 0; };
    const allyDefM = (tg, en) => { const d0 = num(statVal(tg, "def")) + num(statVal(tg, "defB")) * dsum(dbSnap(tg), "defP", "") / 100; return 1 - d0 / (d0 + 200 + 10 * eLvOf(en)); };   // 我方防御区
    const fatalOf = tg => {   // 受到致命攻击：先看有没有效果救回来，没有就倒下
      teamFire("fatal", tg, () => (hpCur(tg) ?? 1) <= 1e-6);
      if ((hpCur(tg) ?? 1) > 1e-6) { marks.push({ t, uid: tg.id, label: "免于倒下", color: tg.color, from: tg.name }); return; }
      tg.gone = true; marks.push({ t, uid: tg.id, label: "倒下", color: "var(--enemy)", from: tg.name });
      addLog(`${tg.name} 倒下（无法战斗）`, true);
      for (const z of U) if (z.sm && z.sm.owner === tg.id && !z.gone) summonOff(z);
    };
    const takeHit = (tg, d, src) => {   // 敌人攻击扣生命值
      const cur = hpCur(tg); if (cur == null) { fireEv("hpLoss", tg); return; }
      const lost = dropHp(tg, d, false) || 0;
      addLog(`${tg.name} 受到 ${src ? src.name : "敌人"} 的攻击 −${Math.round(lost)}（剩 ${Math.round(tg.hc)}）`, false, src ? src.color : "var(--enemy)", tg.id);
      if (lost > 1e-6) { fireEv("hpLoss", tg, lost); syncMirror(tg, true); }
      if (tg.hc <= 1e-6) fatalOf(tg);
    };''')
F.rep('''          batchFx(() => { for (const tg of tgs) apply({ id: actor.id + "-hit", type: "hit", target: tg.id, value: num(sk.sp) }, actor, actor.color); });   // 群攻打到的几个人算同一次（小伊卡一起治疗）''',
'''          const xr = eHitOn ? ((monOf(actor) || {}).x || {})[seq[(actor.turns - 1) % seq.length]] : null, eA = xr ? eAtkOf(actor) : 0;   // 敌人技能倍率（官方）
          const dmgTo = tg => !xr || !(eA > 0) ? 0 : eA * (num(xr[2]) > 1 ? num(xr[0]) * num(xr[2]) / Math.max(1, tgs.length) : tg === main || !main || HITALL.includes(sk.t) ? num(xr[0]) : num(xr[1])) * allyDefM(tg, actor);
          batchFx(() => { for (const tg of tgs) apply({ id: actor.id + "-hit", type: "hit", target: tg.id, value: num(sk.sp), dmg: dmgTo(tg) }, actor, actor.color); });   // 群攻打到的几个人算同一次（小伊卡一起治疗）''')
F.rep('''if (eff.type === "hit" && tg.kind === "ally") fireEv("hpLoss", tg); continue; }''', '''if (eff.type === "hit" && tg.kind === "ally") { if (num(eff.dmg) > 0) takeHit(tg, num(eff.dmg), src); else fireEv("hpLoss", tg); } continue; }''')
F.rep('''        const ready = U.filter(u => hasEnergy(u) && (eCfg(u).autoUlt''', '''        const ready = U.filter(u => !u.gone && hasEnergy(u) && (eCfg(u).autoUlt''')
F.rep('''      if (target === "enemies") return U.filter(u => u.kind === "enemy");''', '''      if (target === "enemies") return U.filter(u => u.kind === "enemy" && !u.gone);''')
F.rep('''      if (target === "efirst") { const e = U.find(u => u.kind === "enemy"); return e ? [e] : []; }''', '''      if (target === "efirst") { const e = U.find(u => u.kind === "enemy" && !u.gone); return e ? [e] : []; }''')
F.rep('''      if (target === "eadj") return U.filter(u => u.kind === "enemy").slice(1, 3);''', '''      if (target === "eadj") return U.filter(u => u.kind === "enemy" && !u.gone).slice(1, 3);''')
# 每场战斗最多 N 次
F.rep('''      if (eff.first) { const k = (src ? src.id : "ev") + ":first:" + eff.id; if (firedMap[k]) return; firedMap[k] = 1; }''',
      '''      if (eff.first) { const k = (src ? src.id : "ev") + ":first:" + eff.id; if (firedMap[k]) return; firedMap[k] = 1; }
      if (num(eff.lim) > 0) { const k = (src ? src.id : "ev") + ":lim:" + eff.id; if ((firedMap[k] || 0) >= num(eff.lim)) return; firedMap[k] = (firedMap[k] || 0) + 1; }   // 每场战斗最多 N 次''')
F.rep('''      if (x.ael) e.aEl = x.ael;''', '''      if (x.lim) e.lim = x.lim;   // 每场战斗最多 N 次
      if (x.ael) e.aEl = x.ael;''')
# 我方伤害扣敌人生命值
F.rep('''    while (guard++ < 3000 && U.length) {''', '''    // 我方伤害扣敌人生命值：每轮开头把新出现的伤害记录（行动 / 开大 / 追击 / 欢愉技 / 持续伤害等）算出来扣到敌人身上
    let iA = 0, iU = 0, iM = 0, iD = 0;
    const SU = eHpOn ? Object.fromEntries(allUnits().map(z => [z.id, z])) : null;
    if (eHpOn) for (const z of U) if (z.kind === "enemy") { const mx = eHpMaxOf(z); if (mx > 0) { z.ehx = mx; z.ehc = mx; } }
    const killEnemy = (en, killer) => {
      en.ehc = 0; en.gone = true; marks.push({ t, uid: en.id, label: "被消灭", color: "var(--enemy)", from: killer ? killer.name : "" });
      addLog(`${en.name} 被${killer ? " " + killer.name + " " : ""}消灭`, false, killer ? killer.color : "var(--enemy)");
      if (killer && killer.kind === "ally") fireEv("kill", killer);
    };
    const hurtEnemy = (en, a, killer) => { if (!en || en.gone || !(en.ehx > 0) || !(a > 0)) return; en.ehc -= a; if (en.ehc <= 1e-6) killEnemy(en, killer); };
    const settleDmg = () => {
      if (!eHpOn) return;
      const keep = R_REF; R_REF = { actions, marks, ultMarks, punch, scoreH, log, spans, dots: dotRecs, heal: healTot, END };
      const go = (d, uid, en1) => {
        if (!d || !(d.total > 0)) return;
        const w = SU[uid], ow = w && w.sm ? SU[w.sm.owner] || w : w, killer = ow ? byId[ow.id] : null;
        const ens = U.filter(z => z.kind === "enemy" && !z.gone && z.ehx > 0); if (!ens.length) return;
        const main = en1 && !en1.gone && en1.ehx > 0 ? en1 : ens[0], others = ens.filter(z => z !== main);
        if (!(num(d.mult) > 0) || d.dot || d.brk) { hurtEnemy(main, d.total, killer); return; }
        const per = d.total / d.mult;
        if (d.tg === 3) { for (const z of [main, ...others]) hurtEnemy(z, per * num(d.v), killer); hurtEnemy(main, per * num(d.rnd), killer); return; }
        hurtEnemy(main, per * (num(d.v) + num(d.rnd)), killer);
        const adjs = d.tg === 2 ? others.slice(0, 2) : d.tg === 4 ? others : [];
        for (const z of adjs.slice(0, Math.max(0, Math.round(num(d.adjN))))) hurtEnemy(z, per * num(d.adj), killer);
      };
      const one = (rec, f) => { try { return f(); } catch (e) { return null; } finally { delete rec.__dmg; } };
      try {
        for (; iA < actions.length; iA++) { const x = actions[iA]; if (x.uid === "aha") { go(one(x, () => elationDmgOf(x)), null); continue; } const w = SU[x.uid]; if (!w || w.kind !== "ally") continue; go(one(x, () => dmgOf(x, w)), x.uid); }
        for (; iU < ultMarks.length; iU++) { const m = ultMarks[iU]; const w = SU[m.uid]; if (w) go(one(m, () => ultDmgOf(m, w)), m.uid); }
        for (; iM < marks.length; iM++) { const m = marks[iM], w = SU[m.uid]; if (!w || w.kind !== "ally") continue; if (m.key && /追击/.test(m.label)) go(one(m, () => fuaDmgOf(m, w)), m.uid); else if (m.elv) go(one(m, () => elskDmgOf(m, w)), m.uid); }
        for (; iD < dotRecs.length; iD++) { const r = dotRecs[iD], w = SU[r.uid]; if (!w) continue; go(one(r, () => dotDmgOf(r, w)), r.uid, byId[r.en]); }
      } finally { R_REF = keep; }
    };
    while (guard++ < 3000 && U.length) {
      settleDmg();
      if (eHpOn && U.some(z => z.kind === "enemy") && !U.some(z => z.kind === "enemy" && !z.gone)) { addLog(`行动值 ${fmt(t)}：敌人全部被消灭，战斗结束`, false); break; }
      if (eHitOn && !U.some(z => z.kind === "ally" && !z.sm && !z.gone)) { addLog(`行动值 ${fmt(t)}：我方全员倒下`, true); break; }''')
F.rep('''    if (guard > 3000) { stats.cap = true;''', '''    settleDmg();
    if (guard > 3000) { stats.cap = true;''')
# 触发：受到致命攻击时
F.rep('''"dotHit", "wkAdd", "aSup"];''', '''"dotHit", "wkAdd", "aSup", "fatal"];''')
n0 = F.s.count('["aSup", "我方使用助战技时"]'); assert n0 == 3, n0
F.s = F.s.replace('["aSup", "我方使用助战技时"]', '["aSup", "我方使用助战技时"], ["fatal", "我方目标受到致命攻击时"]')
# 敌人卡：攻击力 / 生命值
F.rep('''placeholder="${(m => m && m.tn ? m.tn : 0)(MON.m.find(m => m.n === u.mon))}" data-u="${i}" data-f="tough" style="width:60px"></label>''',
'''placeholder="${(m => m && m.tn ? m.tn : 0)(MON.m.find(m => m.n === u.mon))}" data-u="${i}" data-f="tough" style="width:60px"></label>
          ${S.dg && (S.dg.eHit || S.dg.eHp) ? (m => { const L = MON.hl ? MON.hl[Math.max(1, Math.min(MON.hl.length, Math.round(num(u.lv, 95)))) - 1] : null; return `<label for="ea-${u.id}" title="敌人攻击力（官方：1 级攻击力 × 等级成长；清空 = 用官方的）">攻击力 <input type="number" id="ea-${u.id}" min="0" step="1" value="${u.eatk ?? ""}" placeholder="${m && m.a && L ? Math.round(m.a * L[0]) : 0}" data-u="${i}" data-f="eatk" style="width:70px"></label>
          <label for="eh-${u.id}" title="敌人生命值（官方：1 级生命值 × 等级成长；深渊等关卡另有加成，可以自己改；清空 = 用官方的）">生命值 <input type="number" id="eh-${u.id}" min="0" step="1000" value="${u.ehp ?? ""}" placeholder="${m && m.h && L ? Math.round(m.h * L[1]) : 0}" data-u="${i}" data-f="ehp" style="width:96px"></label>`; })(MON.m.find(m => m.n === u.mon)) : ""}''')
F.rep('''data-u="${i}" data-f="wks" style="width:76px"></label>''', '''data-u="${i}" data-f="wks" style="width:76px"></label>
          ${S.dg && S.dg.eHp ? `<label for="eh-${u.id}" title="敌人生命值（手动敌人没有官方数据，填了才会被打死）">生命值 <input type="number" id="eh-${u.id}" min="0" step="1000" value="${u.ehp ?? ""}" placeholder="不模拟" data-u="${i}" data-f="ehp" style="width:96px"></label>` : ""}''')
F.rep('''      el.addEventListener(ev, () => { S.dg[k] = el.type === "checkbox" ? el.checked : num(el.value, DGC[k]); update(); });''', '''      el.addEventListener(ev, () => { S.dg[k] = el.type === "checkbox" ? el.checked : num(el.value, DGC[k]); if (k === "eHit" || k === "eHp") renderEditor(); update(); });   // 掉血开关：敌人卡要多出攻击力 / 生命值''')
F.rep('''  const NUMF = new Set(["tough", "be",''', '''  const NUMF = new Set(["tough", "be", "eatk", "ehp",''')
F.rep('''      if (f === "tough" && el.value === "") delete u.tough;''', '''      if (f === "tough" && el.value === "") delete u.tough;
      if ((f === "eatk" || f === "ehp") && el.value === "") delete u[f];''')

# ================= 受到致命攻击时的效果 =================
def fix_fatal(cid, pred, rank=None, **upd):
    c = C[cid]
    L = c['eff'] if rank is None else F.eid(cid, rank)['eff']
    X = [e for e in L if pred(e)]; assert len(X) == 1, (cid, rank, len(X))
    e = X[0]; old = e.get('n')
    for k in ('off', 'ew', 'first'): e.pop(k, None)
    e.update(t='fatal', **upd)
    return old, e
chg = {}
o, e = fix_fatal(1104, lambda e: (e.get('n') or '').startswith('天赋不屈之身'), aw='self', first=1, n='天赋不屈之身：受到致命攻击时不倒下，立即回复自身生命上限 50%（3 魂 55%）的生命值（每场 1 次）'); chg[1104] = {o: e['n']}
has('110404', '该效果单场战斗中只能触发1次')
o, e = fix_fatal(1211, lambda e: '致命' in (e.get('n') or ''), aw='others', lim=1, xe=6, n='天赋：队友受到致命攻击时不倒下，白露立即为其回复生命值（每场 1 次）'); chg[1211] = {o: e['n']}
e6 = dict(e, lim=2, n='E6：队友受到致命攻击时的治疗每场可以触发 2 次'); e6.pop('xe', None); E6 = F.eid(1211, 6); E6['eff'] = E6.get('eff', []) + [e6]
o, e = fix_fatal(1404, lambda e: '致命' in (e.get('n') or ''), aw='self', n='天赋：【血仇】期间受到致命攻击不倒下，回复自身 50% 生命上限（退出【血仇】、清空充能还没做）')
chg[1404] = {o: e['n']}
o, e = fix_fatal(1408, lambda e: '致命' in (e.get('n') or ''), aw='self', n='天赋：变身期间卡厄斯兰那受到致命攻击时不倒下，回复自身 25% 生命上限（立即发动最后一击还没做）'); chg[1408] = {o: e['n']}
o, e = fix_fatal(1507, lambda e: '致命' in (e.get('n') or ''), aw='self', ns='无量忿怒', n='终结技：【无量忿怒】中受到致命攻击不倒下，回复自身生命值（退出结界还没做）'); chg[1507] = {o: e['n']}
for cid, mp in chg.items(): F.rebuild(cid, list(C[cid]['eff']), rename=mp)
fix_fatal(1008, lambda e: '致命' in (e.get('n') or ''), rank=4, aw='self', first=1, n='E4 绝处反击：受到致命攻击时不倒下，回复至 25% 生命上限（每场 1 次）')
fix_fatal(1208, lambda e: '致命' in (e.get('n') or ''), rank=2, aw='all', tg='evt', ns='穷观阵', first=1, n='E2 柔兆：【穷观阵】开启时，受到致命伤害的我方目标不倒下，回复其 70% 生命上限（每场 1 次）')
fix_fatal(1217, lambda e: '致命' in (e.get('n') or ''), rank=2, aw='all', tg='evt', lim=2, n='E2 判官书符，镇尾锁灵：拥有【禳命】时我方目标受到致命攻击不倒下，回复其 50% 生命上限（每场 2 次；【禳命】回合 −1 还没做）')
fix_fatal(1503, lambda e: '致命' in (e.get('n') or ''), rank=1, aw='all', tg='evt', lim=2, n='E1：我方目标受到致命伤害不倒下，回复其 50% 生命上限（每场 2 次）')

F.finish('模拟敌我掉血（敌人打我方、我方伤害扣敌人生命值）', '''<li><b>2026-11-11（模拟敌我掉血）</b>：tv 81（tools/fix81.py、tools/build_monstat.py）。「伤害设置」里多了两个开关，默认都关（不勾的方案完全不变）：<b>敌人打我方掉血</b>——敌人模板按官方攻击力（1 级攻击力 × 等级成长）和技能倍率打我方，过我方防御区，扣当前生命值；降到 0 = 受到致命攻击，先触发“我方目标受到致命攻击时”的效果（杰帕德、白露、阿兰 E4、符玄 E2、藿藿 E2、真珠 E1、万敌、白厄、千冶•刃已改成这个触发并默认开启），没被救回就倒下、不再行动；<b>我方伤害扣敌人生命值</b>——每次行动、开大、追击、持续伤害、击破、助战技的伤害（和伤害显示同一套算法）在模拟里扣敌人生命值，打空就被消灭：离场、击杀者回 10 点能量、触发“消灭敌人”的效果，敌人全部被消灭时战斗结束。敌人卡上可以改攻击力、生命值（深渊等关卡另有生命加成，官方基础值偏低时自己填）。行动轴会跟着你填的面板数值变：没填面板时伤害偏低、生命值偏低。</li>''',
'''2026-11-11：模拟敌我掉血 —— tv 81（tools/fix81.py、tools/build_monstat.py）。新：S.dg.eHit / eHp、MON.hl / m.a / m.h / m.x、敌人卡 eatk / ehp、触发 fatal、效果字段 lim。
  未改 / 存疑：敌人技能倍率取 ParamList 第 1 个数（扩散第 2 个数是相邻倍率、弹射按段数平均分），部分技能（按生命值算、多段、召唤物、反击）不准；敌人的增伤、我方减伤、护盾吸收、抗性没算（护盾效果没有数值）；关卡（深渊）的生命值加成没算；我方伤害按记录分到主目标 / 相邻 / 全体（群攻按场上敌人卡数量算倍率，死掉的敌人那份浪费）；伤害每轮开头结算一次（同一回合里被打死的敌人在这一回合剩下的效果里仍可能被当成目标）；只有一波敌人；藿藿 E2 的【禳命】回合 −1、万敌退出【血仇】、白厄最后一击、千冶•刃退出结界没做。''')
