"""tv 112：卡厄斯兰那每个额外回合可以手动选技能；【灾厄•弑魂焚诏】按原文做；境界内离场的队友不再被敌人攻击。
- 卡厄斯兰那卡片上“每个额外回合”：自动（毁伤 ≥4 支柱，否则强化普攻）/ 强化普攻 / 支柱 / 灾厄；最后一个固定“最后一击”（自动，不能操控）。存在召唤物卡的 kOv（键 = 第几次变身-第几个额外回合）。
- 支柱：消耗最多 4 点【毁伤】，每点 4 次随机单体伤害，消耗满 4 点才有全体均分的那段、2 魂额外回合；没有【毁伤】时改用强化普攻。
- 灾厄：获得等同于敌方数量的【毁伤】和 1 层【弑魂之炽】（4 魂 +4 层），敌方全体立即行动；【弑魂之炽】期间卡厄斯兰那受到的伤害 −75%，敌人每行动 1 次 +1 层；
  被拉动的敌人都行动完后立即反击（战技伤害，每层倍率 +20%），之后解除；额外回合开始时仍持有也立即反击。变身结束时没反击的就没了。
- 召唤物模板 rot 之外的新字段 zh = [伤害表键, 每层 %, 4 魂额外层数, 减伤 %]。直接伤害记录新字段 mul（倍率乘数）。
- 敌人攻击的目标池去掉被境界 / 离场暂停的角色（domP、stP：白厄变身期间的队友、离场的貊泽）。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 112, sys.argv[2])
C, has = F.C, F.has
# ---- 引擎 ----
F.rep('''        const pool = U.filter(x => x.kind === "ally" && !x.sm && !x.gone);
        const tzs = actor.st''', '''        const pool = U.filter(x => x.kind === "ally" && !x.sm && !x.gone && !x.domP && !x.stP);   // 离场的（境界里的队友、离场的貊泽）不会被攻击
        const tzs = actor.st''')
F.rep('''        if (!was && sd.rot) u.rot = num(sd.rot[0]); if (!was) u.tailOn = false; }''', '''        if (!was && sd.rot) u.rot = num(sd.rot[0]); if (!was) u.tailOn = false;
        if (!was && sd.rot) { u.kNo = num(u.kNo) + 1; u.kTurn = 0; delete u.kz; } }   // 第几次变身 / 这次变身的第几个额外回合（手动选技能用）''')
F.rep('''    const summonOn = (u, src, color) => {''', '''    // 卡厄斯兰那【弑魂之炽】：反击（战技伤害，每层倍率 +X%），之后解除；kzEnd 只解除不反击（变身结束时）
    const kzEnd = k => { const z = k.kz; if (!z) return null; delete k.kz; const o = byId[k.sm.owner]; if (o) o.buffs = o.buffs.filter(b => b.key !== "kz:" + k.id); return z; };
    const kzBoom = (k, why) => {
      const z = kzEnd(k), o = byId[k.sm.owner], zh = (smDef(k) || {}).zh; if (!z || !o || !zh) return;
      const e0 = U.find(x => x.kind === "enemy" && !x.gone), mul = 1 + z.n * num(zh[1]) / 100;
      const r = { t, uid: o.id, en: e0 ? e0.id : null, k: `弑魂之炽反击（${z.n} 层）`, sup: String(zh[0]), mul, db: dbSnap(o), edb: edbSnap(e0), eAll: edbAll(), seq: seq++, ebk: ebkNow() }; dotRecs.push(r);
      marks.push({ t, uid: k.id, label: `反击（弑魂之炽 ${z.n} 层）`, color: k.color, from: k.name });
      addLog(`${k.name} ${why}：反击（【弑魂之炽】${z.n} 层，倍率 ×${Math.round(mul * 100) / 100}）`, false, k.color, o.id); log[log.length - 1].dd = [r];
    };
    const summonOn = (u, src, color) => {''')
F.rep('''      u.gone = true; u.dist = Infinity;
      { const fk''', '''      u.gone = true; u.dist = Infinity;
      if (u.kz) kzEnd(u);   // 变身结束：没来得及反击的【弑魂之炽】直接没了
      { const fk''')
OLD = '''      else if (actor.sm && (smDef(actor) || {}).rot) {   // 卡厄斯兰那：毁伤够就放【支柱•死星天裁】，否则强化普攻；最后一个额外回合只发动最后一击
        const R = smDef(actor).rot, o = byId[actor.sm.owner], lab = s => marks.push({ t, uid: actor.id, label: s, color: actor.color, from: actor.name });
        if (actor.tailOn) { rec.smk = "-"; lab("变身结束"); }
        else if (num(actor.life) === 1) { rec.smk = "-"; lab("最后一击"); }
        else if (num(actor.rot) >= num(R[3])) { actor.rot -= num(R[3]); rec.smk = R[2]; lab(`支柱•死星天裁（毁伤剩 ${actor.rot}）`);
          if (o && num(o.eid) >= 2) { actor.life += 1; actor.dist = 0; actor.zseq = ++zc; lab("2 魂：额外回合"); }
          atkAct(actor); }
        else { actor.rot = num(actor.rot) + num(R[1]); lab(`强化普攻（毁伤 ${actor.rot}）`); atkAct(actor); }
      }
'''
NEW = '''      else if (actor.sm && (smDef(actor) || {}).rot) {   // 卡厄斯兰那：每个额外回合按卡片上选的（默认自动：毁伤 ≥4 支柱，否则强化普攻）；最后一个额外回合自动发动最后一击
        const D = smDef(actor), R = D.rot, o = byId[actor.sm.owner], lab = s => marks.push({ t, uid: actor.id, label: s, color: actor.color, from: actor.name });
        actor.kTurn = num(actor.kTurn) + 1; rec.kNo = num(actor.kNo) || 1; rec.kTurn = actor.kTurn; rec.kKey = `${rec.kNo}-${rec.kTurn}`;
        if (actor.kz) kzBoom(actor, "额外回合开始时仍持有【弑魂之炽】");
        if (actor.tailOn) { rec.smk = "-"; lab("变身结束"); }
        else if (num(actor.life) === 1) { rec.smk = "-"; rec.kAct = "fin"; lab("最后一击"); }
        else {
          const auto = num(actor.rot) >= num(R[3]) ? "pl" : "eb"; let a = (actor.kOv && actor.kOv[rec.kKey]) || auto; rec.kAuto = auto;
          if (a === "zh" && !D.zh) a = auto;
          if (a === "pl" && !(num(actor.rot) > 0)) { lab("没有【毁伤】，改用强化普攻"); a = "eb"; }
          rec.kAct = a;
          if (a === "pl") { const n = Math.min(num(actor.rot), num(R[3])); actor.rot -= n; rec.smk = R[2]; rec.smn = n; lab(`支柱•死星天裁（消耗 ${n} 点毁伤，剩 ${actor.rot}）`);
            if (o && num(o.eid) >= 2 && n >= num(R[3])) { actor.life += 1; actor.dist = 0; actor.zseq = ++zc; lab("2 魂：额外回合"); }   // 2 魂：单次消耗达到 4 点
            atkAct(actor); }
          else if (a === "zh") {   // 灾厄：毁伤 + 敌人数，1 层弑魂之炽（4 魂 +4），敌方全体立即行动；这次本身没有伤害
            const ens = U.filter(z => z.kind === "enemy" && !z.gone), Z = D.zh;
            actor.rot = num(actor.rot) + ens.length; rec.smk = "-";
            if (actor.kz) kzEnd(actor);
            actor.kz = { n: 1 + (o && num(o.eid) >= 4 ? num(Z[2]) : 0), wait: ens.map(z => z.id) };
            if (o && num(Z[3]) > 0) o.buffs.push({ key: "kz:" + actor.id, kind: "d", st: "dr", sc: "", src: actor.id, v: num(Z[3]), n: 1 });   // 弑魂之炽期间受到的伤害降低（敌人打的是白厄这张卡）
            lab(`灾厄•弑魂焚诏（毁伤 ${actor.rot}，弑魂之炽 ${actor.kz.n} 层，敌方全体立即行动）`);
            for (const z of ens) pull(z, 10000);
            if (!ens.length) kzBoom(actor, "没有敌人");
          }
          else { actor.rot = num(actor.rot) + num(R[1]); rec.smk = undefined; lab(`强化普攻（毁伤 ${actor.rot}）`); atkAct(actor); }
        }
      }
'''
F.rep(OLD, NEW)
F.rep('''      if (!isCd(actor) && actor.kind !== "aha") settle();   // 任意目标行动后''', '''      if (!isCd(actor) && actor.kind !== "aha") settle();   // 任意目标行动后
      if (actor.kind === "enemy" && !rec.frz) for (const k of U) if (k.kz && !k.gone) {   // 【弑魂之炽】：敌人每行动 1 次 +1 层；被灾厄拉动的敌人都行动完后立即反击
        k.kz.n++; k.kz.wait = k.kz.wait.filter(id => id !== actor.id && byId[id] && !byId[id].gone);
        if (!k.kz.wait.length) kzBoom(k, "敌方行动完毕");
      }''')
F.rep('''    if (r.sup) { const e = dmgEntry(u, r.sup); return (r.__dmg = e ? dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk, lsCut: r.lsCut }) : null); }''',
'''    if (r.sup) { let e = dmgEntry(u, r.sup); if (e && num(r.mul) > 0 && r.mul !== 1) e = Object.assign({}, e, { v: num(e.v) * r.mul, adj: num(e.adj) * r.mul, rnd: num(e.rnd) * r.mul });   // mul：倍率乘数（弑魂之炽层数）
      return (r.__dmg = e ? dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk, lsCut: r.lsCut }) : null); }''')
F.rep('''    if (sp.k === "owner") { if (a.smk === "-") return null; const e = dmgEntry(o, a.smk || sp.key); if (!e) return null; const r = dmgCalc(o, e, a);''',
'''    if (sp.k === "owner") { if (a.smk === "-") return null; let e = dmgEntry(o, a.smk || sp.key); if (!e) return null;
      { const R0 = (T.sm || []).find(m => m.k === u.sm.key), R = R0 && R0.rot; if (R && a.smk === R[2] && a.smn != null && a.smn < num(R[3])) e = Object.assign({}, e, { v: 0, rnd: num(e.rnd) * a.smn / num(R[3]) }); }   // 支柱没消耗满 4 点：只有每点 4 次的随机伤害
      const r = dmgCalc(o, e, a);''')
# ---- 界面 ----
F.rep('''data-smf="noTurn">不上行动序列（只有额外回合，比如德谬歌、小伊卡）</label>` : ""}''', '''data-smf="noTurn">不上行动序列（只有额外回合，比如德谬歌、小伊卡）</label>` : ""}
          ${sm && kRotOf(u) ? `<div class="turn-acts k-acts" data-ki="${i}"></div>` : ""}''')
F.rep('''    renderTurnActs(R);''', '''    renderTurnActs(R); renderKActs(R);''')
F.rep('''  function renderTurnActs(R) {''', '''  // 卡厄斯兰那（召唤物模板 rot）：每个额外回合选 自动 / 强化普攻 / 支柱 / 灾厄；最后一个额外回合固定最后一击
  function kRotOf(u) { const o = u && u.sm && S.units.find(x => x.id === u.sm.owner), T = o && tplOf(o), d = T && (T.sm || []).find(m => m.k === u.sm.key); return !!(d && d.rot); }
  function renderKActs(R) {
    document.querySelectorAll(".k-acts").forEach(box => {
      const i = +box.dataset.ki, u = S.units[i]; if (!u) return;
      const acts = R.actions.filter(a => a.uid === u.id && a.kKey);
      if (!acts.length) { box.innerHTML = `<span class="hint">每个额外回合：显示范围内变身后在这里选</span>`; return; }
      const nm = { eb: "强普", pl: "支柱", zh: "灾厄" };
      box.innerHTML = `<span class="hint">每个额外回合：</span>` + acts.map(a => {
        const lab = `${a.kNo > 1 ? a.kNo + "-" : ""}${a.kTurn}`, when = `第 ${a.kNo} 次变身的第 ${a.kTurn} 个额外回合，AV ${fmt(a.t, 2)}`;
        if (a.kAct === "fin") return `<span class="ta fixed" title="${when}：自动发动最后一击，不能操控">${lab}<b>最后一击</b></span>`;
        if (!a.kAct) return "";
        const ov = !!(u.kOv && u.kOv[a.kKey]);
        const opts = [["auto", `自动（${nm[a.kAuto] || "强普"}）`], ["eb", "强化普攻"], ["pl", "支柱"], ["zh", "灾厄"]];
        return `<span class="ta-wrap"><label class="ta${ov ? " ov" : ""}" title="${when}${ov ? "（单独指定过）" : ""}；实际：${nm[a.kAct] || ""}">${lab}<select data-kact="${i}" data-k="${a.kKey}" aria-label="${when}的行动">${opt(opts, ov ? u.kOv[a.kKey] : "auto")}</select></label></span>`;
      }).join("");
    });
  }
  function renderTurnActs(R) {''')
F.rep('''    if (t.dataset.tact !== undefined) {''', '''    if (t.dataset.kact !== undefined) {   // 卡厄斯兰那每个额外回合：选回“自动”就删掉单独指定
      const u = S.units[+t.dataset.kact], k = t.dataset.k;
      u.kOv = Object.assign({}, u.kOv);
      if (t.value === "auto") delete u.kOv[k]; else u.kOv[k] = t.value;
      if (!Object.keys(u.kOv).length) delete u.kOv;
      renderEditor(); update(); return;
    }
    if (t.dataset.tact !== undefined) {''')
# ---- 模板 ----
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('140809', '获得等同于敌方全体数量的【毁伤】和1层【弑魂之炽】，随后使敌方全体立即行动')
has('140809', '敌方目标攻击或行动后叠加1层【弑魂之炽】。上述敌方目标行动完毕后，立即发动反击')
has('140809', '每层【弑魂之炽】使本次反击的伤害倍率提高原倍率的#5[i]%'); has('140809', '若卡厄斯兰那的额外回合开始时仍持有【弑魂之炽】，立即发动反击')
P = F.SK['140809']['params']; assert all(p[1] == 0.75 and p[4] == 0.2 and p[2] == 4 for p in P)
has('r:140804', '施放【灾厄•弑魂焚诏】时，额外获得4层【弑魂之炽】')
d2 = F.DMG['1408']['s2']; assert d2['tg'] == 3 and abs(d2['v'][9] - P[9][0]) < 1e-9 and abs(d2['rnd'][9] - P[9][2] * P[9][3]) < 1e-6
c = C[1408]; m = c['sm'][0]; assert m['k'] == 'khaslana'; m['zh'] = ['s2', 20, 4, 75]
c['notes'] = [n for n in c['notes'] if not n.startswith('变身期间每个额外回合自动选技能')] + ['卡厄斯兰那卡片上可以给每个额外回合选技能：自动（【毁伤】≥4 放支柱，否则强化普攻）/ 强化普攻 / 支柱（最多消耗 4 点）/ 灾厄；最后一个额外回合自动发动最后一击，不能选']
F.rebuild(1408, c['eff'], notes=c['notes'])
F.finish('卡厄斯兰那手动选技能、灾厄', '''<li><b>2026-11-14</b>：tv 112（tools/fix112.py）。卡厄斯兰那卡片上可以给每个额外回合选技能（自动 / 强化普攻 / 支柱 / 灾厄），最后一个额外回合固定是自动的最后一击。【灾厄•弑魂焚诏】按原文做了：获得敌人数量的【毁伤】和【弑魂之炽】，敌方全体立即行动，行动完后反击（每层倍率 +20%，4 魂多 4 层），期间受到的伤害 −75%。支柱没攒满 4 点【毁伤】也能放（伤害按消耗的点数）。另外白厄变身期间离场的队友、离场的貊泽不再被敌人攻击。</li>''',
'''2026-11-14：卡厄斯兰那手动选技能、灾厄 —— tv 112（tools/fix112.py）。新：召唤物卡 kOv、召唤物模板 zh、直接伤害记录 mul；敌人攻击目标池去掉 domP / stP。
  未改 / 存疑：支柱在 0 点【毁伤】时改用强化普攻（游戏里能不能放没确认）；反击不触发“攻击后”类效果；敌人“攻击”和“行动”各叠 1 层还是合计 1 层没确认，这里每次行动 1 层''')
