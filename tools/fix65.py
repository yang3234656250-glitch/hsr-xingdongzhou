"""tv 65：持续伤害第 1 批（引擎 + 卡芙卡【强化版】1005、黑天鹅【强化版】1307）。
用法：python3 tools/fix65.py index.html <官方 json 目录>
引擎：效果类型 dot（给敌人挂持续伤害：dk 名字、数值 = 倍率 %、vps 每层另加 %、stm 倍率 × 层数、stack 层数上限、over 可暂时超过上限、half 结算后层数减半、
kst 敌人有这个状态时不减半、dig 无视防御 %、adj[0] 结算时相邻目标另受的倍率 %、持续 = 敌人的回合数，0 = 一直在）、dotx（引爆：目标身上的持续伤害立即结算数值 %，
方式 own = 只引爆自己挂的）；敌人回合开始时结算（en.dots），每次结算 / 引爆记到 R.dots 给伤害显示；新触发 dotHit（敌方目标受到持续伤害时，事件对象 = 那个敌人，
down = 只算自己挂的）；新目标 eadj（第 2、3 个敌人 = 相邻目标）。伤害层：dotDmgOf（不暴击）、伤害类型 d = 持续伤害（增伤 / 易伤可以只对它）。
没放敌人卡时没有持续伤害（挂不上去）。基础概率一律按命中算。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 65, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
def lvE(cid, base):   # 几魂给这个技能加等级（强化版跟着原技能）
    for r in range(1, 7):
        for z in (F.RK[str(cid * 100 + r)].get('level_up_skills') or []):
            if str(z.get('id')) == str(base): return r
    raise KeyError(base)

# ================= 引擎 =================
F.rep('["spChg", "我方消耗或恢复战技点时"]', '["spChg", "我方消耗或恢复战技点时"], ["dotHit", "敌方目标受到持续伤害时"]', 2)
F.rep('spChg: "我方消耗或恢复战技点时"', 'spChg: "我方消耗或恢复战技点时", dotHit: "敌方目标受到持续伤害时"')
F.rep('"spUse", "spChg"];', '"spUse", "spChg", "dotHit"];', 2)
F.rep('state: "状态", hpup: "生命上限",', 'state: "状态", dot: "持续伤害", dotx: "引爆持续伤害", hpup: "生命上限",')
F.rep('["state", "状态"], ["hpup", "生命上限"],', '["state", "状态"], ["dot", "持续伤害（挂在敌人身上）"], ["dotx", "引爆持续伤害"], ["hpup", "生命上限"],')
F.rep('      if (x.nu) e.nthU = true;', '      if (x.dk) e.dk = x.dk; if (x.vps != null) e.vps = x.vps; if (x.stm) e.stm = 1; if (x.half) e.half = 1; if (x.kst) e.keepSt = x.kst; if (x.dig) e.defIg = x.dig; if (x.over) e.over = 1; if (x.down) e.dotOwn = 1;   // 持续伤害（dot / dotx / dotHit）\n      if (x.nu) e.nthU = true;')
F.rep('''      if (target === "efirst") { const e = U.find(u => u.kind === "enemy"); return e ? [e] : []; }''',
      '''      if (target === "efirst") { const e = U.find(u => u.kind === "enemy"); return e ? [e] : []; }
      if (target === "eadj") return U.filter(u => u.kind === "enemy").slice(1, 3);   // 相邻目标：第 2、3 个敌人卡''')
F.rep('    const addLog = (text, bad, color, uid, heal) => log.push({ t, text, bad, color, uid, heal: !!heal, seq: seq++ });',
      '''    const addLog = (text, bad, color, uid, heal) => log.push({ t, text, bad, color, uid, heal: !!heal, seq: seq++ });
    // ---------- 持续伤害：挂在敌人身上（en.dots），敌人回合开始时结算；每次结算 / 引爆记一条到 dotRecs，渲染层按它算伤害 ----------
    const dotRecs = []; let dotDepth = 0, dotBag = null;
    const dotMult = d => (num(d.v) * (d.stm ? d.n : 1) + num(d.vps) * d.n) / 100;
    const dotHit = (en, d, k, why) => {
      const o = byId[d.src]; if (!o || !(k > 0)) return;
      const mk = m => { const r = { t, uid: o.id, en: en.id, k: d.k, mult: m, stat: d.stat, why, db: dbSnap(o), edb: edbSnap(), defIg: num(d.defIg), seq: seq++ }; const h = hpNow(o); if (h != null) r.hpm = h; dotRecs.push(r); if (dotBag) dotBag.push(r); return r; };
      mk(dotMult(d) * k);
      if (why === "turn" && num(d.adjV) > 0) { const nA = Math.min(2, U.filter(x => x.kind === "enemy" && !x.gone).length - 1); if (nA > 0) mk(num(d.adjV) / 100 * nA).adj = nA; }   // 结算时相邻目标另受一次（黑天鹅【奥迹】）
      if (dotDepth >= 2) return;
      dotDepth++; const pT = evTarget, pA = evAmt; evTarget = en; evAmt = null;
      try { for (const u of U) if (u.kind === "ally" && !u.gone) for (const e of fx(u, "dotHit")) { if (e.dotOwn && (ownerOf(u) || u).id !== d.src) continue; apply(e, u, u.color); } }
      finally { evTarget = pT; evAmt = pA; dotDepth--; }
    };
    const dotBagLog = (bag, head, color) => { if (!bag.length) return; const by = {}; for (const r of bag) { const k = (byId[r.uid] || {}).name + "【" + r.k + "】"; by[k] = (by[k] || 0) + 1; } addLog(head + Object.entries(by).map(([k, n]) => k + (n > 1 ? " ×" + n : "")).join("、"), false, color); log[log.length - 1].dd = bag; };
    const dotTick = en => {   // 敌人回合开始：身上的持续伤害各结算一次，回合数 −1
      if (!en.dots || !en.dots.length) return;
      const bag = [], keep = dotBag; dotBag = bag;
      try {
        for (const d of en.dots.slice()) {
          dotHit(en, d, 1, "turn");
          if (d.half && !(d.keepSt && hasSt(en, d.keepSt))) d.n = Math.max(1, Math.floor(d.n / 2));
          if (d.cap > 0 && d.n > d.cap) d.n = d.cap;
          if (d.left > 0 && --d.left <= 0) d.gone = true;
        }
        en.dots = en.dots.filter(d => !d.gone);
      } finally { dotBag = keep; }
      dotBagLog(bag, en.name + " 回合开始，持续伤害结算：", en.color);
    };''')
F.rep('      if (actor.kind === "enemy") fireAll("eturn", actor);   // 敌方回合开始（持续伤害结算之类）',
      '      if (actor.kind === "enemy") { dotTick(actor); fireAll("eturn", actor); }   // 敌方回合开始：持续伤害结算，再触发“敌方回合开始时”')
F.rep('        if (eff.type === "spmax") {', '''        if (eff.type === "dot") {   // 给敌人挂持续伤害（同一个人的同一组 bk 是同一个，再挂 = 刷新回合、叠层）
          const own = src ? (ownerOf(src) || src) : null; if (!own || tg.kind !== "enemy") continue;
          const key = own.id + ":" + (eff.bk || eff.id), lim = Math.max(1, Math.round(num(eff.stack, 1))), add = Math.max(1, Math.round(num(eff.stAdd, 1)));
          tg.dots = tg.dots || []; let d = tg.dots.find(z => z.key === key);
          if (!d) tg.dots.push(d = { key, src: own.id, n: 0 });
          Object.assign(d, { k: eff.dk || "持续伤害", v, vps: num(eff.vps), stm: !!eff.stm, stat: eff.srcS || "atk", half: !!eff.half, keepSt: eff.keepSt || "", defIg: num(eff.defIg), adjV: num(eff.adjV), cap: lim, left: Math.max(0, Math.round(num(eff.duration))) });
          d.n = eff.over ? d.n + add : Math.min(lim, d.n + add);
          continue;
        }
        if (eff.type === "dotx") {   // 引爆：目标身上的持续伤害立即产生 v% 的伤害（方式 own = 只算自己挂的），不扣回合数
          if (tg.kind !== "enemy" || !tg.dots || !tg.dots.length) continue;
          const own = src ? (ownerOf(src) || src) : null, bag = [], keep = dotBag; dotBag = bag;
          try { for (const d of tg.dots.slice()) if (eff.mode !== "own" || (own && d.src === own.id)) dotHit(tg, d, v / 100, "det"); } finally { dotBag = keep; }
          dotBagLog(bag, (src ? src.name : "事件") + " 引爆 " + tg.name + " 的持续伤害（" + v + "%）：", srcColor);
          continue;
        }
        if (eff.type === "spmax") {''')
F.rep('    return { actions, marks, END, punch, scoreH, log, spans, stats, swOn: !!swU, finalScore: sw.score, eH, ultMarks, skMarks, heal: healTot };',
      '    return { actions, marks, END, punch, scoreH, log, spans, stats, swOn: !!swU, finalScore: sw.score, eH, ultMarks, skMarks, heal: healTot, dots: dotRecs };')
# ---- 伤害层 ----
F.rep('const SCK = { b: "b", b2: "b", s: "s", s2: "s", u: "u", u2: "u", f: "f", m: "m", e: "e", e2: "e" };', 'const SCK = { b: "b", b2: "b", s: "s", s2: "s", u: "u", u2: "u", f: "f", m: "m", e: "e", e2: "e", d: "d" };')
F.rep('["m", "忆灵造成的"], ["e", "欢愉技"]];', '["m", "忆灵造成的"], ["e", "欢愉技"], ["d", "持续伤害"]];')
F.rep('bonus = num(u.dmg, 0) + D("dmg"), defI = D("defIg");', 'bonus = num(u.dmg, 0) + D("dmg"), defI = D("defIg") + num(e.defIg);')
F.rep('    const critM = 1 + Math.min(1, Math.max(0, cr) / 100) * Math.max(0, cd) / 100;', '    const critM = e.dot ? 1 : 1 + Math.min(1, Math.max(0, cr) / 100) * Math.max(0, cd) / 100;   // 持续伤害不暴击')
F.rep('    if (YG && !rec.__box && (e.key !== "e" || rec.uid === "aha") && bangerAt(YG, rec) > 0) {', '    if (YG && !rec.__box && !e.dot && (e.key !== "e" || rec.uid === "aha") && bangerAt(YG, rec) > 0) {')
F.rep('    const xr = isLv && !e.el ? null : riderDmg(', '    const xr = (isLv && !e.el) || e.dot ? null : riderDmg(')
F.rep('  // 阿哈时刻里每个欢愉角色放一次欢愉技\n  function elationDmgOf(a) {', '''  // 一次持续伤害结算 / 引爆（R.dots 里的一条）：倍率在模拟里算好了（含层数、引爆比例），这里按来源角色当时的增益算，不暴击
  function dotDmgOf(r, u) {
    if (!r || !u || u.kind !== "ally") return null;
    if (r.__dmg !== undefined) return r.__dmg;
    const e = { v: r.mult, adj: 0, rnd: 0, tg: 1, el: 0, stat: r.stat || "atk", key: "d", n: r.k, lv: 0, dot: true, defIg: r.defIg };
    return (r.__dmg = dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, hpm: r.hpm }));
  }
  const dotSum = (list, by) => { let s = 0; for (const r of list || []) { const d = dotDmgOf(r, by[r.uid]); if (d) s += d.total; } return s > 0 ? { total: s } : null; };
  // 阿哈时刻里每个欢愉角色放一次欢愉技
  function elationDmgOf(a) {''')
F.rep(': l.em ? elskDmgOf(l.em, byId[l.em.uid]) : null;', ': l.em ? elskDmgOf(l.em, byId[l.em.uid]) : l.dd ? dotSum(l.dd, byId) : null;', 2)
F.rep('''      for (const m of R.marks) if (m.elv && m.t <= lim + 1e-6) { const d = elskDmgOf(m, by[m.uid]); if (d) sum += d.total; }
      return sum;''', '''      for (const m of R.marks) if (m.elv && m.t <= lim + 1e-6) { const d = elskDmgOf(m, by[m.uid]); if (d) sum += d.total; }
      for (const r of R.dots || []) if (r.t <= lim + 1e-6) { const d = dotDmgOf(r, by[r.uid]); if (d) sum += d.total; }   // 持续伤害
      return sum;''')
F.rep('''    for (const m of R.marks) { if (!m.elv) continue; const c = cycleOf(m.t); if (c < 0 || c >= n) continue; const d = elskDmgOf(m, byId2[m.uid]); if (d) per[c] += d.total; }
''', '''    for (const m of R.marks) { if (!m.elv) continue; const c = cycleOf(m.t); if (c < 0 || c >= n) continue; const d = elskDmgOf(m, byId2[m.uid]); if (d) per[c] += d.total; }
    for (const r of R.dots || []) { const c = cycleOf(r.t); if (c < 0 || c >= n) continue; const d = dotDmgOf(r, byId2[r.uid]); if (d) per[c] += d.total; }   // 持续伤害
''')

# ================= 卡芙卡【强化版】1005 =================
c = C[1005]
has('1100503', '有#2[i]%的基础概率使受到攻击的敌方目标陷入触电状态，并使其当前承受的持续伤害类负面状态立即产生相当于原伤害#5[i]%的伤害。触电状态持续#3[i]回合')
has('1100503', '触电状态下，敌方目标每回合开始时受到等同于卡芙卡#4[i]%攻击力的雷属性持续伤害')
has('1100502', '其当前承受的所有持续伤害立即产生相当于原伤害#2[i]%或#4[i]%的伤害')
has('1100504', '有#2[i]%的基础概率使受到攻击的敌方目标陷入与终结技相同的触电状态，持续#3[i]回合')
hast(1005, '荆棘', '天赋的追加攻击可以使目标当前承受的所有持续伤害类负面状态立即产生相当于原伤害#1[i]%的伤害')
has('r:100504', '当敌方目标承受的由卡芙卡造成的触电状态产生伤害时，额外为卡芙卡恢复2点能量')
has('r:100506', '触电状态的伤害倍率提高156%，并使触电状态的持续时间增加1回合'); has('r:100501', '使目标受到的持续伤害提高30%，持续2回合'); has('r:100502', '我方全体造成的持续伤害提高25%')
eu, es = lvE(1005, 100503), lvE(1005, 100502)
u10, u12, s10, s12 = prm('1100503', 10), prm('1100503', 12), prm('1100502', 10), prm('1100502', 12)
assert r4(u10[3]) == 2.9 and u10[2] == 2 and r4(u10[4]) == 1.2 and r4(s10[1]) == 0.75 and r4(s10[3]) == 0.5
SD = lambda **k: dict(dict(y='dot', dk='触电', v=r4(u10[3] * 100), lv=[eu, r4(u12[3] * 100)], d=2, bk='sd'), **k)
new = list(c['eff']) + [
    dict(y='dotx', t='skill', tg='efirst', v=r4(s10[1] * 100), lv=[es, r4(s12[1] * 100)], n='【强化版】战技：指定敌方单体当前承受的所有持续伤害立即产生 75%% 的伤害（%d 魂 78%%）' % es),
    dict(y='dotx', t='skill', tg='eadj', v=r4(s10[3] * 100), lv=[es, r4(s12[3] * 100)], n='【强化版】战技：相邻目标当前承受的所有持续伤害立即产生 50%% 的伤害（%d 魂 52%%）' % es),
    SD(t='ult', tg='enemies', n='【强化版】终结技：使受到攻击的敌方目标陷入触电状态 2 回合，每回合开始受到 290%% 攻击力的雷属性持续伤害（%d 魂 318.27%%；基础概率按命中算）' % eu),
    dict(y='dotx', t='ult', tg='enemies', v=r4(u10[4] * 100), lv=[eu, r4(u12[4] * 100)], n='【强化版】终结技 + 行迹折磨：敌方全体当前承受的所有持续伤害立即产生 120%% 的伤害（%d 魂 124%%）' % eu),
    SD(t='fua', tg='efirst', n='【强化版】天赋：追加攻击使受到攻击的敌方目标陷入与终结技相同的触电状态，持续 2 回合'),
    dict(y='dotx', t='fua', tg='efirst', v=80, n='行迹荆棘：天赋的追加攻击使目标当前承受的所有持续伤害立即产生 80% 的伤害'),
    SD(t='start', tg='enemies', off=1, n='秘技宽恕无关慈悲：进入战斗后敌方每个单体目标陷入与终结技相同的触电状态，持续 2 回合（用了秘技再启用）'),
]
F.rebuild(1005, new, notes=[n for n in c.get('notes', []) if '持续伤害' not in n and '触电' not in n])
F.eid(1005, 1)['eff'].append(dict(y='dbuf', t='fua', tg='enemies', m='vuln', sc='d', v=30, d=2, bk='e1d', n='E1：天赋触发追加攻击时使目标受到的持续伤害 +30%，持续 2 回合（按敌方全体）'))
F.eid(1005, 2)['eff'].append(dict(y='dbuf', t='start', tg='team', m='dmg', sc='d', v=25, d=0, bk='e2d', n='E2：卡芙卡在场时我方全体造成的持续伤害 +25%'))
e4 = F.eid(1005, 4); e4['eff'] = [dict(y='energy', t='dotHit', down=1, tg='self', v=2, m='er', n='E4：敌方目标承受的由卡芙卡造成的触电状态产生伤害时，额外恢复 2 点能量')]
v6 = r4(u12[3] * 100 + 156) if eu <= 6 else r4(u10[3] * 100 + 156)
F.eid(1005, 6)['eff'] += [SD(t='ult', tg='enemies', v=v6, lv=None, d=3, n='E6：终结技的触电伤害倍率 +156%%（共 %s%%），持续时间 +1 回合' % v6),
                          SD(t='fua', tg='efirst', v=v6, lv=None, d=3, n='E6：天赋追加攻击的触电同样倍率 +156%、持续 3 回合')]
for e in F.eid(1005, 6)['eff']:
    if e.get('lv') is None: e.pop('lv', None)

# ================= 黑天鹅【强化版】1307 =================
c = C[1307]
has('1130704', '敌方目标每受到1次持续伤害，有#2[i]%的基础概率陷入1层【奥迹】')
has('1130704', '每回合开始时受到等同于黑天鹅#1[i]%攻击力的风属性持续伤害，随后层数减半。每层【奥迹】使此伤害倍率提高#3[f1]%。【奥迹】可以叠加#8[i]层，层数达到上限后可继续叠加，产生伤害后移除超出上限的层数')
has('1130704', '【奥迹】造成的伤害无视目标#7[i]%的防御力。仅在敌方目标回合开始【奥迹】造成伤害时，相邻目标额外受到1次等同于黑天鹅#5[i]%攻击力的风属性持续伤害')
has('1130703', '并且【奥迹】回合开始造成伤害后层数不会减半'); hast(1307, '杯底端倪', '敌方目标进入战斗时，有#1[i]%的基础概率陷入1层【奥迹】')
has('r:130706', '当敌方目标受到黑天鹅的队友的攻击时，黑天鹅有65%的基础概率使目标陷入1层【奥迹】')
et = lvE(1307, 130704); t10, t12 = prm('1130704', 10), prm('1130704', 12)
assert r4(t10[0]) == 2.4 and r4(t10[2]) == 0.12 and r4(t10[4]) == 1.8 and r4(t10[6]) == 0.2 and t10[7] == 50
AJ = lambda **k: dict(dict(y='dot', dk='奥迹', v=r4(t10[0] * 100), lv=[et, r4(t12[0] * 100)], vps=r4(t10[2] * 100), lx={'vps': [r4(t10[2] * 100), r4(t12[2] * 100)], 'adjV': [r4(t10[4] * 100), r4(t12[4] * 100)]},
                          adj=[r4(t10[4] * 100), 0], st=50, over=1, half=1, kst='揭露', dig=20, d=0, bk='aj'), **k)
new = list(c['eff']) + [
    AJ(t='start', tg='enemies', n='行迹杯底端倪：敌方目标进入战斗时陷入 1 层【奥迹】（基础概率按命中算）。【奥迹】：敌人每回合开始受到 240% + 每层 12% 攻击力的风属性持续伤害（无视 20% 防御），相邻目标另受 180%，随后层数减半（【揭露】期间不减半），最多 50 层'),
    AJ(t='dotHit', tg='evt', n='【强化版】天赋：敌方目标每受到 1 次持续伤害，陷入 1 层【奥迹】（基础概率按命中算）'),
    AJ(t='start', tg='enemies', off=1, n='秘技取此真相，弃舍表征：战斗开始时敌方每个单体目标再陷入 1 层【奥迹】（之后每次概率减半，这里按 1 层；用了秘技再启用）'),
]
F.rebuild(1307, new, notes=['【奥迹】要放了敌人卡才有；每次叠层的基础概率都按命中算，终结技【揭露】“50% 固定概率额外多 1 层”、E2 没做'])
F.eid(1307, 6)['eff'] = [e for e in F.eid(1307, 6)['eff']] + [AJ(t='atk', aw='others', tg='efirst', n='E6：敌方目标受到黑天鹅的队友的攻击时陷入 1 层【奥迹】（按主目标；基础概率按命中算，“50% 固定概率额外多 1 层”没算）')]
F.eid(1307, 6)['notes'] = [n for n in F.eid(1307, 6).get('notes', []) if '奥迹' not in n]
F.touch(1307)

F.finish('持续伤害第 1 批（引擎 + 卡芙卡、黑天鹅）', '''<li><b>2026-11-10（持续伤害第 1 批：卡芙卡、黑天鹅）</b>：开始算持续伤害，tv 65（tools/fix65.py）。① <b>机制</b>：持续伤害挂在<b>敌人卡</b>上，敌人每个回合开始时结算一次、回合数 −1；“引爆”= 立即按比例结算一次、不扣回合数。行动顺序表里多一行“××回合开始，持续伤害结算：卡芙卡【触电】…｜伤害”，计入每轮“伤害合计”、方案对比和配速助手的全队伤害。持续伤害不暴击，吃增伤 / 易伤 / 减防 / 抗性；新伤害类型“持续伤害”可以单独加增伤。<b>没放敌人卡就没有持续伤害</b>；基础概率一律按命中算。② <b>卡芙卡【强化版】</b>：终结技给敌方全体触电（290% 攻击力，2 回合）并引爆全部持续伤害 120%；战技引爆主目标 75% / 相邻 50%；天赋追加攻击给目标触电并引爆 80%（行迹荆棘）；E1 持续伤害易伤 30%、E2 全队持续伤害 +25%、E4 触电每次造成伤害 +2 能量（现在自动算，原来是默认关闭的近似）、E6 触电倍率 +156%、多 1 回合。③ <b>黑天鹅【强化版】</b>：【奥迹】按层数算（240% + 每层 12%，无视 20% 防御，相邻目标另受 180%，结算后层数减半，【揭露】期间不减半，最多 50 层）；敌人每受到 1 次持续伤害 +1 层，进入战斗 1 层，E6 队友攻击 +1 层。<b>对已有配置</b>：有敌人卡而且队里有卡芙卡 / 黑天鹅的方案，伤害合计会变大，卡芙卡 4 魂的能量会变（开大可能提前）；其他不变。</li>''',
'''2026-11-10（持续伤害第 1 批）：卡芙卡【强化版】（1005）、黑天鹅【强化版】（1307）—— tv 65（tools/fix65.py）。
  改：见更新日志同日条目。新效果类型 dot / dotx、触发 dotHit、目标 eadj、R.dots、dotDmgOf、伤害类型 d。
  未改 / 存疑：基础概率都按命中；黑天鹅【奥迹】减半后至少留 1 层（原文没写 1 层减半后是否消失）、终结技“50% 固定概率额外 1 层”、E2 没做；卡芙卡 E1 易伤按敌方全体；持续伤害的目标按敌人卡顺序（第 1 个 = 主目标，第 2、3 个 = 相邻）。其他有持续伤害的角色（海瑟音、桑博、桂乃芬、椒丘、希露瓦、卢卡、虎克、姬子、艾丝妲等）还没做。''')
