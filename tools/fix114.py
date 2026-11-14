"""tv 114：附加伤害按它自己的属性算（用户：按实际来）。
XR 条目新字段 el = 属性字、rnd = 随机单体：和这次攻击属性不同时——
- 抗性按敌人自己的弱点：敌人卡选了怪物 / 填了弱点（含战斗中被添加的弱点）就看有没有这个属性的弱点（有 = 0，没有 = 伤害设置里的抗性）；没有弱点资料时跟“命中弱点”勾选一致；
  随机单体按当时在场的所有敌人平均，否则按主目标；只对别的属性的减抗 / 穿透不算（增益 / 减益的 tEl）。
- 增伤去掉卡片上填的面板“增伤 %”（那是本属性的属性伤害提高），只留效果给的增伤。
敌人快照 eAll 现在一个敌人也记，并多记每个敌人的弱点（w）。白厄 2 魂的抗性穿透标上只对物理。昔涟【永续的燃烧】附加伤害标成火属性、随机单体。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 114, sys.argv[2])
C = F.C
F.rep('''      const ens = U.filter(u => u.kind === "enemy" && !u.gone); if (ens.length < 2) return undefined;
      return { ord: ens.map(z => z.id), m: Object.fromEntries(ens.map(z => [z.id, dbSnap(z)])), bk: Object.fromEntries(ens.map(z => [z.id, toughMax(z) > 0 ? !!z.broken : null])) };''',
'''      const ens = U.filter(u => u.kind === "enemy" && !u.gone); if (!ens.length) return undefined;
      const wkOf = z => { const m = monOf(z); if (!m || !m.w) return null; return String(m.w) + (z.wk || []).filter(q => !q.st || (byId[q.own] && hasSt(byId[q.own], q.st))).map(q => q.el === "all" ? "物火冰雷风量虚" : String(q.el)).join(""); };   // 弱点属性（没资料 = null）
      return { ord: ens.map(z => z.id), m: Object.fromEntries(ens.map(z => [z.id, dbSnap(z)])), bk: Object.fromEntries(ens.map(z => [z.id, toughMax(z) > 0 ? !!z.broken : null])), w: Object.fromEntries(ens.map(z => [z.id, wkOf(z)])) };''')
F.rep('''          const dm = self ? c.dmgM : 1 + num(cw.dmg, 0) / 100;
          amt = sv * v * cn * dm * crit * c.defM * c.resM * c.vulnM * c.toughM;''',
'''          const xEl = r.el && r.el !== c.el1;   // 和这次攻击不同属性（永续的燃烧的火属性附加伤害）：抗性按敌人对这个属性的弱点，增伤不吃面板的本属性伤害提高
          const dm = self ? (xEl ? c.dmgMx : c.dmgM) : 1 + num(cw.dmg, 0) / 100;
          amt = sv * v * cn * dm * crit * c.defM * (xEl ? c.resMEl(r.el, !!r.rnd) : c.resM) * c.vulnM * c.toughM;''')
F.rep('''    const xr = (isLv && !e.el) || e.dot ? null : riderDmg(u, e, rec, DB0, { base, mainDmg, oneHit, dmgM, critM, defM, resM, vulnM, toughM, elStat, laughB, bg, inAha, nAll, nAdj });''',
'''    // 别的属性的附加伤害：抗性按敌人自己的弱点（随机单体按在场敌人平均），只对别的属性的减抗 / 穿透不算
    const resMEl = (el, rnd) => {
      const EA0 = rec && rec.eAll, W = EA0 && EA0.w, ids = W ? (rnd ? EA0.ord : EA0.ord.slice(0, 1)) : [null];
      const fl = L => (L || []).filter(x => !x[3] || String(x[3]).includes(el)), pen = num(cfg.pen) + dsum(fl(DB0), "resPen", e.key) + spkPen;
      let s = 0;
      for (const id of ids) {
        const w = id != null ? W[id] : null, weak = swE >= 6 || (w == null ? !!cfg.weak : w.includes(el));
        const rr = dsum(fl(id != null && EA0.m[id] ? EA0.m[id] : EDB), "resRed", e.key);
        s += Math.min(2, Math.max(0.1, 1 - ((weak ? 0 : num(cfg.res)) - pen - rr) / 100));
      }
      return s / ids.length;
    };
    const dmgMx = (e.el || isLv || b2el || e.brk) ? 1 : 1 + (bonus - num(u.dmg, 0)) / 100;
    const xr = (isLv && !e.el) || e.dot ? null : riderDmg(u, e, rec, DB0, { base, mainDmg, oneHit, dmgM, critM, defM, resM, vulnM, toughM, elStat, laughB, bg, inAha, nAll, nAdj, el1: EL1, resMEl, dmgMx });''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
e2 = F.eid(1408, 2); x = find(e2['eff'], 'E2：卡厄斯兰那物理属性抗性穿透 +20%'); x['tel'] = '物'
y = find(e2['eff'], 'E2：变身结束，穿透取消'); y['tel'] = '物'
F.touch(1408)
r = [z for z in F.XR['1415'] if z['k'] == 'fs']; assert len(r) == 1; r = r[0]
r.update(el='火', rnd=1); r['n'] = '献予「负世」之诗【永续的燃烧】：卡厄斯兰那施放攻击后 5 次火属性附加伤害，每次随机单体 10% 攻击力（3 魂 11%；抗性按每个敌人有没有火弱点，增伤不吃面板的物理伤害提高）'
F.finish('附加伤害按自己的属性算', '''<li><b>2026-11-14</b>：tv 114（tools/fix114.py）。昔涟【永续的燃烧】的附加伤害按火属性算：抗性看每个敌人有没有火弱点（敌人卡选了怪物或填了弱点时；没有资料就跟“命中弱点”的勾选一致），随机单体按在场敌人平均；卡片上填的面板“增伤 %”（物理伤害提高）不再算进去；白厄 2 魂的物理抗性穿透也不再算进去。</li>''',
'''2026-11-14：附加伤害按自己的属性算 —— tv 114（tools/fix114.py）。用户：永续的燃烧火属性附加伤害按实际来。新：XR 字段 el / rnd，eAll 快照一个敌人也记、多了 w（每个敌人的弱点属性），白厄 2 魂穿透标 tel 物。
  未改 / 存疑：只有 XR 写了 el 的附加伤害按自己的属性算（目前只有永续的燃烧）；易伤没分属性''')
