"""tv 91：白厄变身期间被救后立即最后一击并结束变身；真珠用【好活当赏】作抵御值抵挡伤害、我方生命值 ≤50% 时减伤。
用法：python3 tools/fix91.py index.html <官方 json 目录>
- dismiss 效果字段 lsc（lsCut）：离场前把“剩余行动数 × lsc%”记到主人最近一次开大记录（um.lsCut），dmgCalc 里终结技倍率 ×(1 − lsCut)
  （白厄：最后一击的 960% 记在开大那一行；每剩余 1 个额外回合倍率 −12.5%）。
- 模板 x.guard = [抵挡 %, 每点好活当赏的抵御值]（真珠）：takeHit 里在符玄分担之后、护盾之前抵挡；
  当时的【好活当赏】用 bangerAt（临时 R_REF）算，消耗记在 bgUse（R.bgUse），bangerAt 对真珠减去之前消耗的。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 91, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

F.rep('''      if (x.smr) e.stModR = x.smr;''', '''      if (x.lsc) e.lsCut = x.lsc;   // 离场时按剩余行动数削减主人终结技（最后一击）的倍率
      if (x.smr) e.stModR = x.smr;''')
F.rep('''        if (eff.type === "dismiss") { summonOff(tg); continue; }''', '''        if (eff.type === "dismiss") { if (num(eff.lsCut) > 0 && tg && tg.sm && !tg.gone) { const um = [...ultMarks].reverse().find(m => m.uid === tg.sm.owner); if (um) { um.lsCut = Math.min(1, num(tg.life) * num(eff.lsCut) / 100); delete um.__dmg; addLog(`${byId[tg.sm.owner].name} 立即发动最后一击（还剩 ${num(tg.life)} 个额外回合，倍率 −${Math.round(um.lsCut * 1000) / 10}%，伤害记在开大那一行）`, false, srcColor, tg.sm.owner); } } summonOff(tg); continue; }''')
F.rep('''    if (tidOf(u) === "1510" && e.key === "z2"''', '''    if (rec && num(rec.lsCut) > 0 && e.key === "u") mult *= 1 - num(rec.lsCut);   // 提前发动的最后一击（白厄）
    if (tidOf(u) === "1510" && e.key === "z2"''')
# 真珠抵御值
F.rep('''      const ab = shAbsorb(tg, d), lost = d - ab > 1e-9 ? dropHp(tg, d - ab, false) || 0 : 0;''', '''      let gd = 0; const GZ = U.find(z => z.kind === "ally" && !z.sm && !z.gone && tx(z).guard) || null;   // 真珠：消耗【好活当赏】（抵御值）抵挡一部分伤害
      if (GZ && tg.kind === "ally" && d > 0) {
        const g = tx(GZ).guard, keep = R_REF; let have = 0;
        R_REF = { actions, marks, ultMarks, punch, scoreH, log, spans, dots: dotRecs, heal: healTot, END, bgUse };
        try { have = bangerAt(GZ, { t, seq }); } catch (e) { have = 0; } finally { R_REF = keep; }
        gd = Math.min(d * num(g[0]) / 100, have * num(g[1]));
        if (gd > 1e-6) { d -= gd; bgUse.push({ uid: GZ.id, t, seq, amt: gd / num(g[1]) }); } else gd = 0;
      }
      const ab = shAbsorb(tg, d), lost = d - ab > 1e-9 ? dropHp(tg, d - ab, false) || 0 : 0;''')
F.rep('''      let txt = `${tg.name} 受到 ${src ? src.name : "敌人"} 的攻击 ${amt(ab, lost, tg.hc, !(shOf(tg) > 0))}`, fl = 0;''', '''      let txt = `${tg.name} 受到 ${src ? src.name : "敌人"} 的攻击 ${gd > 0 ? `${GZ.name}抵挡 ${Math.round(gd)}（消耗 ${Math.round(gd / num(tx(GZ).guard[1]) * 10) / 10} 点【好活当赏】） ` : ""}${amt(ab, lost, tg.hc, !(shOf(tg) > 0))}`, fl = 0;''')
F.rep('''    const takeHit = (tg, d, src) => {''', '''    const bgUse = [];   // 真珠消耗掉的【好活当赏】
    const takeHit = (tg, d, src) => {''')
F.rep('''ultMarks, skMarks, heal: healTot, dots: dotRecs };''', '''ultMarks, skMarks, heal: healTot, dots: dotRecs, bgUse };''')
F.rep('''    if (tidOf(u) === "1503") v = Math.min(50, v);   // 真珠天赋：持有上限 50 点''', '''    if (tidOf(u) === "1503") {   // 真珠天赋：持有上限 50 点；减去之前当抵御值消耗掉的
      v = Math.min(50, v);
      for (const x of (R_REF && R_REF.bgUse) || []) if (x.uid === u.id && (x.t < t - 1e-9 || (Math.abs(x.t - t) < 1e-9 && num(x.seq) <= sq))) v -= x.amt;
      v = Math.max(0, v);
    }''')
assert F.s.index('    const bgUse = [];') < F.s.index('    const settleDmg = ')

def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
# 白厄
has('140805', '卡厄斯兰那受到致命攻击时不会陷入无法战斗状态，而是回复等同于自身生命上限#2[i]%的生命值并立即发动最后一击。每剩余1个卡厄斯兰那的额外回合，最后一击的伤害倍率减少原倍率的#3[f1]%')
assert r4(prm('140805', 10)[2]) == 0.125
c = C[1408]; E = c['eff']; h = find(E, '天赋：变身期间卡厄斯兰那受到致命攻击时不倒下'); o = h['n']
n = '天赋：变身期间卡厄斯兰那受到致命攻击时不倒下，回复自身 25% 生命上限'; h['n'] = n
E.insert(E.index(h) + 1, dict(y='dismiss', t='fatal', aw='self', tg='sm:khaslana', v=0, fps=1, ns='变身', lsc=12.5, n='天赋：被救下后立即发动最后一击并结束变身（每剩余 1 个额外回合，最后一击倍率 −12.5%）'))
c['notes'] = c.get('notes', []) + ['最后一击的 960% 伤害记在开大那一行；变身期间被打倒提前发动时，那一行的伤害按剩余额外回合数削减']
F.rebuild(1408, E, rename={o: n})
# 真珠
has('150304', '每点【好活当赏】等同于#5[i]点抵御值，我方目标受到伤害时，真珠可消耗抵御值为我方目标抵挡#2[i]%的伤害'); has('150304', '我方目标当前生命值百分比小于等于#1[i]%时，受到的伤害降低#4[i]%')
p = prm('150304', 10); assert r4(p[0]) == 0.5 and r4(p[1]) == 0.6 and r4(p[3]) == 0.3 and p[4] == 200
c = C[1503]; E = c['eff']; h = find(E, '天赋：可用【好活当赏】抵挡'); o = h['n']
n = '天赋：我方目标受到伤害时消耗【好活当赏】抵挡 60% 的伤害（每点 = 200 点抵御值；“敌人打我方掉血”开着时生效，消耗掉的好活当赏不再算进伤害）；真珠的【好活当赏】持续无限、上限 50 点'; h['n'] = n
E.append(dict(y='dbuf', t='start', tg='team', m='dr', v=30, d=0, bk='zzdr', alv=1, ec={'hp': ['le', 50]}, n='天赋：我方目标当前生命值 ≤50% 时受到的伤害降低 30%'))
F.rebuild(1503, E, x={'guard': [60, 200]})

F.finish('白厄提前最后一击、真珠抵御值', '''<li><b>2026-11-12（白厄、真珠）</b>：tv 91（tools/fix91.py）。白厄变身期间被打到致命：回复 25% 生命上限后<b>立即发动最后一击并结束变身</b>，最后一击（伤害记在开大那一行）按剩余的额外回合数每个 −12.5% 倍率。真珠：我方目标受到伤害时消耗【好活当赏】当抵御值，抵挡 60% 的伤害（每点 200 点抵御值），消耗掉的好活当赏之后不再算进欢愉伤害；我方目标生命值 ≤50% 时受到的伤害降低 30%。两项都要开“敌人打我方掉血”。</li>''',
'''2026-11-12：白厄提前最后一击、真珠抵御值 —— tv 91（tools/fix91.py）。新：dismiss lsc / um.lsCut、x.guard、bgUse（R.bgUse）。
  未改 / 存疑：真珠抵挡放在符玄分担之后、护盾之前（官方没写顺序）；消耗后的【好活当赏】按“min(50, 累计) − 已消耗”算；白厄最后一击仍显示在开大那一行''')
