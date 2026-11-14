"""tv 111：白厄最后一击的伤害挪到它真正发动的时候。
原文：最后的卡厄斯兰那的额外回合开始时立即发动最后一击（自动，不能操控，不是普攻 / 战技）。之前这次伤害记在白厄开大那一行（开大时的增益），
现在召唤物模板新字段 fin = 伤害表键：这个召唤物离场（变身结束）时直接造成一次这个键的伤害（终结技伤害，按当时的增益，消灭敌人算“终结技消灭”）；
有 fin 的角色开大那一行不再算伤害。被致命攻击提前结束时的倍率削减（每剩 1 个额外回合 −12.5%）也记在这次伤害上。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 111, sys.argv[2])
C = F.C
F.rep('''      u.gone = true; u.dist = Infinity;''', '''      u.gone = true; u.dist = Infinity;
      { const fk = (smDef(u) || {}).fin, o0 = byId[u.sm.owner];   // 离场时直接造成一次伤害（白厄最后一击：变身结束 = 最后一击，按这时的增益）
        if (fk && o0) { const e0 = U.find(z => z.kind === "enemy" && !z.gone);
          const r = { t, uid: o0.id, en: e0 ? e0.id : null, k: "最后一击", sup: String(fk), db: dbSnap(o0), edb: edbSnap(e0), eAll: edbAll(), seq: seq++, ebk: ebkNow() };
          if (num(u.lsCutF) > 0) r.lsCut = num(u.lsCutF); delete u.lsCutF; dotRecs.push(r);
          addLog(`${o0.name}「最后一击」造成伤害${r.lsCut ? `（倍率 −${Math.round(r.lsCut * 1000) / 10}%）` : ""}`, false, o0.color, o0.id); log[log.length - 1].dd = [r]; } }''')
F.rep('''        if (eff.type === "dismiss") { if (num(eff.lsCut) > 0 && tg && tg.sm && !tg.gone) { const um''', '''        if (eff.type === "dismiss" && num(eff.lsCut) > 0 && tg && tg.sm && !tg.gone && (smDef(tg) || {}).fin) {   // 提前结束：最后一击的倍率削减记到离场时的那次伤害上
          tg.lsCutF = Math.min(1, num(tg.life) * num(eff.lsCut) / 100);
          addLog(`${byId[tg.sm.owner].name} 立即发动最后一击（还剩 ${num(tg.life)} 个额外回合）`, false, srcColor, tg.sm.owner); summonOff(tg); continue; }
        if (eff.type === "dismiss") { if (num(eff.lsCut) > 0 && tg && tg.sm && !tg.gone) { const um''')
F.rep('''    if (r.sup) { const e = dmgEntry(u, r.sup); return (r.__dmg = e ? dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk }) : null); }''',
'''    if (r.sup) { const e = dmgEntry(u, r.sup); return (r.__dmg = e ? dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk, lsCut: r.lsCut }) : null); }''')
F.rep('''        for (; iD < dotRecs.length; iD++) { const r = dotRecs[iD], w = SU[r.uid]; if (!w) continue; go(one(r, () => dotDmgOf(r, w)), r.uid, byId[r.en]); }''',
'''        for (; iD < dotRecs.length; iD++) { const r = dotRecs[iD], w = SU[r.uid]; if (!w) continue; killK = r.sup === "u" ? "u" : "a"; try { go(one(r, () => dotDmgOf(r, w)), r.uid, byId[r.en]); } finally { killK = "a"; } }   // 终结技键的直接伤害（最后一击）消灭敌人算“终结技消灭”''')
F.rep('''  function ultDmgOf(m, u) {
    if (!u || tidOf(u) === "1506") return null;''', '''  function ultDmgOf(m, u) {
    if (!u || tidOf(u) === "1506") return null;
    { const T = tplOf(u); if (T && (T.sm || []).some(x => x.fin === "u")) return null; }   // 终结技伤害在召唤物离场时才造成（白厄最后一击），开大那一行不算''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
F.has('140803', '最后的卡厄斯兰那的额外回合开始时立即发动最后一击，造成等同于卡厄斯兰那#1[i]%攻击力的物理属性终结技伤害，由敌方全体均分')
c = C[1408]; m = c['sm'][0]; assert m['k'] == 'khaslana'; m['fin'] = 'u'
E = c['eff']
x = find(E, '终结技：变身，整段变身的速度'); o1 = x['n']
x['n'] = '终结技：变身，整段变身的速度 = 白厄基础速度 × 60%（1 魂 66%；基础速度含专武加的），第 1 个额外回合在开大后立刻，第 8 个在变身末尾，中间均分；其他队友离场。第 8 个额外回合自动发动最后一击（终结技伤害），不是普攻 / 战技'
y = find(E, '天赋：被救下后立即发动最后一击并结束变身'); o2 = y['n']
y['n'] = '天赋：被救下后立即发动最后一击并结束变身（每剩余 1 个额外回合，最后一击倍率 −12.5%；伤害记在这时）'
c['notes'] = [n for n in c['notes'] if not n.startswith('终结技：最后的卡厄斯兰那的额外回合开始时立即发动最后一击')] + ['最后一击（终结技伤害）记在变身结束那一刻，按那时的增益算；白厄开大那一行本身没有伤害']
F.rebuild(1408, E, rename={o1: x['n'], o2: y['n']}, notes=c['notes'])
F.finish('白厄最后一击按发动时刻算', '''<li><b>2026-11-14</b>：tv 111（tools/fix111.py）。白厄的最后一击改到它真正发动的时候算：第 8 个额外回合自动发动（不是普攻 / 战技），伤害记在那一刻、按那时的增益，消灭敌人算终结技消灭；白厄开大那一行本身不再有伤害。被致命攻击提前结束时同样在那一刻发动，倍率按剩余额外回合削减。</li>''',
'''2026-11-14：白厄最后一击按发动时刻算 —— tv 111（tools/fix111.py）。新：召唤物模板字段 fin（离场时造成一次这个键的伤害）。
  未改 / 存疑：最后一击不触发“攻击后”类效果（昔涟【永续的燃烧】附加伤害等）；卡厄斯兰那第 1～7 个额外回合仍是自动选技能，还不能手动指定''')
