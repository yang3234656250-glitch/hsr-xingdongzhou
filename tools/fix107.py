"""tv 107：卡厄斯兰那（白厄变身）按原文重做。
- 召唤物模板新字段：dom = 在场时其他我方目标全部离场（暂停、不能开大）；now = 登场后立刻行动；spb = 速度固定为本体基础速度 × ratio；
  rot = [初始毁伤, 强化普攻 +N, 满毁伤时用的伤害键, 需要几点]：每个额外回合自动选【支柱•死星天裁】（毁伤够）或强化普攻；最后一个额外回合只发动最后一击。
- count 方式 rot：给召唤物加【毁伤】。伤害表键 s3。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 107, sys.argv[2])
C, has = F.C, F.has
F.rep('''      if (u.sm.pause && o) o.paused = true;''', '''      if (u.sm.pause && o) o.paused = true;
      { const sd = smDef(u) || {};
        if (sd.dom) for (const z of U) if (z.kind === "ally" && z !== u && z !== o && !z.paused) { z.paused = true; z.domP = u.id; }   // 境界：其他我方目标离场且无法行动（白厄【时墟铁墓】）
        if (!was && sd.now) { u.dist = 0; u.zseq = ++zc; }   // 登场后立刻行动
        if (!was && sd.rot) u.rot = num(sd.rot[0]); }''')
F.rep('''      if (u.sm.pause) o.paused = false;''', '''      if (u.sm.pause) o.paused = false;
      for (const z of U) if (z.domP === u.id) { z.paused = false; delete z.domP; }''')
F.rep('''      if (o && o !== u && !o.sm) { const s0 = spdOf(o)''', '''      if (o && o !== u && !o.sm && u.spbF === undefined) { const T0 = tplOf(o), d0 = T0 && (T0.sm || []).find(m => m.k === u.sm.key); u.spbF = !!(d0 && d0.spb); }
      if (o && o !== u && !o.sm && u.spbF) return Math.max(1, num(o.base, 100) * num(u.sm.ratio) / 100);   // 速度固定为本体基础速度的 X%，不吃加速（卡厄斯兰那）
      if (o && o !== u && !o.sm) { const s0 = spdOf(o)''')
F.rep('''        const ready = U.filter(u => !u.gone && hasEnergy(u)''', '''        const ready = U.filter(u => !u.gone && !u.domP && hasEnergy(u)''')
F.rep('''      else if (actor.sm && !(smDef(actor) || {}).na) atkAct(actor);''', '''      else if (actor.sm && (smDef(actor) || {}).rot) {   // 卡厄斯兰那：毁伤够就放【支柱•死星天裁】，否则强化普攻；最后一个额外回合只发动最后一击
        const R = smDef(actor).rot, o = byId[actor.sm.owner], lab = s => marks.push({ t, uid: actor.id, label: s, color: actor.color, from: actor.name });
        if (num(actor.life) === 1) { rec.smk = "-"; lab("最后一击"); }
        else if (num(actor.rot) >= num(R[3])) { actor.rot -= num(R[3]); rec.smk = R[2]; lab(`支柱•死星天裁（毁伤剩 ${actor.rot}）`);
          if (o && num(o.eid) >= 2) { actor.life += 1; actor.dist = 0; actor.zseq = ++zc; lab("2 魂：额外回合"); }
          atkAct(actor); }
        else { actor.rot = num(actor.rot) + num(R[1]); lab(`强化普攻（毁伤 ${actor.rot}）`); atkAct(actor); }
      }
      else if (actor.sm && !(smDef(actor) || {}).na) atkAct(actor);''')
F.rep('''          if (eff.mode === "mod") {   // 每 |v| 点消耗一轮''', '''          if (eff.mode === "rot") { if (tg.sm) tg.rot = Math.max(0, num(tg.rot) + v); continue; }   // 给召唤物加【毁伤】（卡厄斯兰那）
          if (eff.mode === "mod") {   // 每 |v| 点消耗一轮''')
F.rep('''    if (sp.k === "owner") { const e = dmgEntry(o, sp.key); return e ? dmgCalc(o, e, a) : null; }''', '''    if (sp.k === "owner") { if (a.smk === "-") return null; const e = dmgEntry(o, a.smk || sp.key); if (!e) return null; const r = dmgCalc(o, e, a);
      if (a.smk === "s3" && String(T.id) === "1408" && num(o.eid) >= 6) { const add = r.total * 0.36; r.total += add; r.xr = r.xr || { sum: 0, parts: [] }; r.xr.parts.push({ n: "6 魂：本次攻击总伤害 36% 的真实伤害", amt: add }); r.xr.sum += add; }
      return r; }''')
F.rep('''const LVK = { b: "b", b2: "b", s: "s", s2: "s",''', '''const LVK = { b: "b", b2: "b", s: "s", s2: "s", s3: "s",''')
F.rep('''const SCK = { b: "b", b2: "b", s: "s", s2: "s",''', '''const SCK = { b: "b", b2: "b", s: "s", s2: "s", s3: "s",''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('140803', '境界内的其他队友离场且无法行动'); has('140803', '速度固定为卡厄斯兰那基础速度的#3[i]%')
has('140805', '变身时获得#1[i]点【毁伤】'); assert F.SK['140805']['params'][0][0] == 4
has('140808', '获得#3[i]点【毁伤】'); assert F.SK['140808']['params'][0][2] == 2
has('140811', '每消耗1点【毁伤】造成#3[i]次伤害，每次对敌方随机单体造成等同于卡厄斯兰那#2[f1]%攻击力的物理属性伤害。消耗#4[i]点【毁伤】时，额外造成等同于卡厄斯兰那#1[i]%攻击力的物理属性伤害，由敌方全体均分')
has('r:140802', '单次施放【支柱•死星天裁】消耗【毁伤】点数达到4点时，获得1个额外回合'); has('r:140806', '额外造成等同于本次攻击总伤害值36%的真实伤害')
P = F.SK['140811']['params']; assert len(P) == 15 and P[0][2] == 4 and P[0][3] == 4
F.DMG['1408']['s3'] = {"v": [p[0] for p in P], "adj": [], "rnd": [round(p[1] * 16, 4) for p in P], "tg": 0, "el": 0, "stat": "atk", "n": "支柱•死星天裁（消耗 4 点毁伤）", "max": 15}
c = C[1408]; m = c['sm'][0]; assert m['k'] == 'khaslana'; m.update(dom=1, now=1, spb=1, rot=[4, 2, 's3', 4])
E = c['eff']
x = find(E, '终结技：变身，卡厄斯兰那 8 次行动'); o1 = x['n']; x['n'] = '终结技：变身，卡厄斯兰那 8 个额外回合（速度固定 = 白厄基础速度 × 60%，1 魂 66%；变身后立刻行动；其他队友离场）'
y = find(E, '秘技终结之始：进入战斗后为我方队友恢复 25 点能量'); o2 = y['n']; y['n'] = '秘技终结之始：进入战斗后为我方队友恢复 25 点能量（用了秘技再启用）'
E.insert(E.index(y) + 1, dict(y='count', t='smOn', sk='khaslana', tg='sm:khaslana', m='rot', v=2, off=1, n='秘技终结之始：获得 2 点【毁伤】（记到第一次变身上；用了秘技再启用）'))
c['notes'] = (c.get('notes') or []) + ['变身期间每个额外回合自动选技能：【毁伤】≥4 点放【支柱•死星天裁】（消耗 4 点），否则放强化普攻（+2 点）；【灾厄•弑魂焚诏】不会自动放；最后一个额外回合只发动最后一击']
F.rebuild(1408, E, rename={o1: x['n'], o2: y['n']}, notes=c['notes'])
F.finish('卡厄斯兰那重做', '''<li><b>2026-11-13</b>：tv 107（tools/fix107.py）。白厄变身按原文重做：变身后卡厄斯兰那立刻行动；速度固定为白厄基础速度的 60%（1 魂 66%），不再跟着面板速度；变身期间其他队友离场，不行动也不开大；每个额外回合自动选技能（【毁伤】≥4 点放【支柱•死星天裁】，否则强化普攻 +2 点），最后一个额外回合只发动最后一击；2 魂支柱后的额外回合、6 魂 36% 真实伤害也算了。</li>''',
'''2026-11-13：卡厄斯兰那重做 —— tv 107（tools/fix107.py）。新：召唤物模板字段 dom / now / spb / rot，count 方式 rot，伤害表键 s3。
  未改 / 存疑：“变身后立刻行动”没有实测；【灾厄•弑魂焚诏】不自动放；1 魂“每消灭 1 个敌人速度比例 +1.5%”没做；昔涟【永续的燃烧】的 4 点毁伤没做（官方数据里没找到原文）；离场队友身上排着的额外回合没处理''')
