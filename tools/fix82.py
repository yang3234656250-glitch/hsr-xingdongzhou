"""tv 82：护盾有数值、能抵挡伤害；符玄【穷观阵】分担；受到的伤害降低（dbuf 新属性 dr）；提供的护盾量（shB）。
用法：python3 tools/fix82.py index.html <官方 json 目录>
引擎：护盾效果的“方式”= def / atk / hp（按施放者当前属性，面板 + 增益 %）时有数值：护盾量 = 属性 × % + 固定值，再 ×（1 + 提供的护盾量 shB）。
u.shd = { 施放者id:组 → { v, left } }；组 = 效果字段 shk（没有就按效果 id），同一组再次获得时刷新；shCap = 可以叠加，最多同组 shBase 效果（战技）护盾量的 X%。
几个护盾同时在时按最大的抵挡，受到伤害时每个护盾都扣同样的量；持有者回合结束时 −1 回合（和状态一样，自己回合内获得的这回合算第 1 回合）；倒下时清空。
敌人打我方（takeHit）：伤害 × 受到的伤害降低（dbuf dr，相乘）→ 符玄【穷观阵】（模板 x.share = [状态, %]）分走护盾抵挡之前的 65% → 目标护盾抵挡 → 扣生命值。
护盾始终记录（不管掉血开关），掉血开关开着时才会被打掉。条件字段 hasSh（e / s / !s，:组）= 事件对象 / 自己持有护盾时才生效（队伍里没有算数值的护盾时不检查）；
cdT = 触发后过 N 个自己的回合才能再触发；目标 lowsh = 护盾值最低的我方目标；伤害增益条件 ec.sh = 持有者持有护盾时。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 82, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎：数据映射 =================
F.rep('''      if (x.lim) e.lim = x.lim;   // 每场战斗最多 N 次''', '''      if (x.lim) e.lim = x.lim;   // 每场战斗最多 N 次
      if (x.shk) e.shk = x.shk; if (x.shc) e.shCap = x.shc; if (x.shb) e.shBase = 1; if (x.hsh) e.hasSh = x.hsh; if (x.cdt) e.cdT = x.cdt;   // 护盾的组 / 叠加上限（战技护盾量的 %）/ 作为上限基准；条件：持有护盾；触发后 N 回合内不再触发''')
F.rep('''  const HEALM = ["hp", "atk", "def", "thp", "lost", "flat"];''', '''  const HEALM = ["hp", "atk", "def", "thp", "lost", "flat"];
  const SHM = ["def", "atk", "hp"], SHL = { def: "防御力", atk: "攻击力", hp: "生命上限" };   // 护盾按施放者哪项属性算（没有 = 只触发“受到护盾时”）''')
F.rep('''for (const k of ["value", "mode", "flat", "hot", "hotX", "adjV", "adjF", "hpx", "hpm", "lvE", "lvV", "lvV0", "lvX"])''',
      '''for (const k of ["value", "mode", "flat", "hot", "hotX", "adjV", "adjF", "hpx", "hpm", "lvE", "lvV", "lvV0", "lvX", "duration", "shk", "shCap", "shBase", "hasSh", "cdT"])''')

# ================= 引擎：模拟 =================
a = '''    const allyDefM = (tg, en) => {'''
i = F.s.index(a); j = F.s.index('\n', i)
F.s = F.s[:j + 1] + '''    // ---------- 护盾（tv 82）：u.shd = { "施放者id:组": { v, left } }；几个护盾同时在时按最大的抵挡，受到伤害时每个护盾都扣；持有者回合结束时 −1 回合 ----------
    const stNow = (u, k) => { if (!u) return 0; if (k === "hp") return num(hpNow(u)); return num(statVal(u, k)) + num(statVal(u, k + "B")) * dsum(dbSnap(u), k + "P", "") / 100; };   // 当前属性：面板 + 增益的 %（按基础值）
    const shAmt = (o, m, p, f) => (stNow(o, m) * p / 100 + f) * (1 + dsum(dbSnap(o), "shB", "") / 100);   // 护盾量 =（属性 × % + 固定值）×（1 + 提供的护盾量）
    const shOf = (u, key) => { let m = 0; for (const [k, z] of Object.entries((u && u.shd) || {})) if (!key || k.endsWith(":" + key)) m = Math.max(m, z.v); return m; };
    const shTrack = U.some(u => u.kind === "ally" && (u.effects || []).some(e => e.type === "shield" && SHM.includes(e.mode) && !e.off));   // 队伍里有算数值的护盾，“持有护盾”这个条件才检查
    const shPut = (tg, eff, o, v) => {
      const k = o.id + ":" + (eff.shk || eff.id), Z = tg.shd || (tg.shd = {}), old = Z[k], a = shAmt(o, eff.mode, v, num(eff.flat));
      let nv = a;
      if (eff.shk && num(eff.shCap) > 0 && old) {   // 同一组可以叠加，最多战技护盾量的 X%（砂金【坚垣筹码】、丹恒•腾荒）
        const b = (o.effects || []).find(x => x.type === "shield" && x.shBase && x.shk === eff.shk) || eff;
        nv = Math.max(a, Math.min(shAmt(o, b.mode, num(b.value), num(b.flat)) * num(eff.shCap) / 100, old.v + a));
      }
      const d = Math.round(num(eff.duration));
      Z[k] = { v: nv, left: d > 0 ? d : Infinity };
      return nv;
    };
    const shLabel = eff => { const l = healLabel(eff); return l === "治疗" ? "护盾" : l; };
    const doShield = (eff, src, srcColor, v) => {
      const o = src ? ownerOf(src) : null;
      const all = resolve(eff.target, src).filter(tg => tg && !(eff.tgTpl && ![].concat(eff.tgTpl).map(Number).includes((tplOf(tg) || {}).id)));
      const tgs = all.filter(u => u.kind === "ally" && !u.gone && !isCd(u) && !(u.sm && !u.sm.mem) && !(eff.target === "evt" && isOut(u)));   // 能拿到护盾的：在场的角色和忆灵
      if (o && tgs.length) {
        const parts = tgs.map(tg => [tg, shPut(tg, eff, o, v)]), same = parts.length > 2 && parts.every(([, a]) => Math.round(a) === Math.round(parts[0][1])), d = Math.round(num(eff.duration));
        addLog(`${o.name}「${shLabel(eff)}」护盾 ${same ? `我方 ${parts.length} 人各 ${Math.round(parts[0][1])}` : parts.map(([tg, a]) => `${tg.name} ${Math.round(a)}`).join("、")}${d > 0 ? `（${d} 回合）` : ""}`, false, srcColor, null, true);
      }
      for (const tg of all) healFor(tg, "shield");
      if (all.length && o && o.kind === "ally" && hgDepth <= 2) { hgDepth++; try { teamFire("aGive", o); } finally { hgDepth--; } }   // 一次护盾效果算一次“提供护盾”
    };
    const tickSh = u => { for (const [k, z] of Object.entries(u.shd || {})) if (--z.left <= 0) delete u.shd[k]; };
    const shAbsorb = (tg, d) => { const m = shOf(tg); if (!(m > 0) || !(d > 0)) return 0; for (const [k, z] of Object.entries(tg.shd)) { z.v -= d; if (z.v <= 1e-6) delete tg.shd[k]; } return Math.min(d, m); };
    const drOf = tg => dbSnap(tg).reduce((m, x) => x[0] === "dr" ? m * Math.max(0, 1 - num(x[2]) / 100) : m, 1);   // 受到的伤害降低（几个来源相乘）
''' + F.s[j + 1:]
F.rep('''      tg.gone = true; marks.push({ t, uid: tg.id, label: "倒下"''', '''      tg.gone = true; tg.shd = {}; marks.push({ t, uid: tg.id, label: "倒下"''')
F.rep('''    const takeHit = (tg, d, src) => {   // 敌人攻击扣生命值
      const cur = hpCur(tg); if (cur == null) { fireEv("hpLoss", tg); return; }
      const lost = dropHp(tg, d, false) || 0;
      addLog(`${tg.name} 受到 ${src ? src.name : "敌人"} 的攻击 −${Math.round(lost)}（剩 ${Math.round(tg.hc)}）`, false, src ? src.color : "var(--enemy)", tg.id);
      if (lost > 1e-6) { fireEv("hpLoss", tg, lost); syncMirror(tg, true); }
      if (tg.hc <= 1e-6) fatalOf(tg);
    };''', '''    const takeHit = (tg, d, src) => {   // 敌人攻击扣生命值：× 受到的伤害降低 → 符玄【穷观阵】分走护盾抵挡之前的 65% → 护盾抵挡 → 扣生命值
      const cur = hpCur(tg); if (cur == null) { fireEv("hpLoss", tg); return; }
      d *= drOf(tg);
      const FX = U.find(z => z !== tg && z.kind === "ally" && !z.sm && !z.gone && tx(z).share && hasSt(z, tx(z).share[0]) && hpCur(z) != null) || null;
      const fd = FX ? d * num(tx(FX).share[1]) / 100 : 0; d -= fd;
      const ab = shAbsorb(tg, d), lost = d - ab > 1e-9 ? dropHp(tg, d - ab, false) || 0 : 0;
      const amt = (a, l, h, brk) => `${a > 0 ? `护盾抵挡 ${Math.round(a)}${brk ? "（护盾破碎）" : ""}` : ""}${l > 1e-6 || !(a > 0) ? `${a > 0 ? " " : ""}−${Math.round(l)}` : ""}（剩 ${Math.round(h)}）`;
      let txt = `${tg.name} 受到 ${src ? src.name : "敌人"} 的攻击 ${amt(ab, lost, tg.hc, !(shOf(tg) > 0))}`, fl = 0;
      if (FX && fd > 0) { const fab = shAbsorb(FX, fd); fl = fd - fab > 1e-9 ? dropHp(FX, fd - fab, false) || 0 : 0; txt += `；${FX.name}【${tx(FX).share[0]}】分担 ${Math.round(fd)}：${amt(fab, fl, FX.hc, !(shOf(FX) > 0))}`; }
      addLog(txt, false, src ? src.color : "var(--enemy)", tg.id);
      // 受到致命攻击：先看能不能救回来（救不回来就倒下），这一下不再触发“生命值降低时”（符玄天赋原文：受到致命攻击时无法触发）
      for (const [z, l] of [[tg, lost], [FX, fl]]) {
        if (!z || !(l > 1e-6)) continue;
        if (z.hc <= 1e-6) { fatalOf(z); syncMirror(z, true); }
        else { fireEv("hpLoss", z, l); syncMirror(z, true); }
      }
    };''')
F.rep('''      if (eff.type === "heal" && HEALM.includes(eff.mode)) { doHeal(eff, src, srcColor); return; }''', '''      if (eff.type === "heal" && HEALM.includes(eff.mode)) { doHeal(eff, src, srcColor); return; }
      if (eff.type === "shield" && SHM.includes(eff.mode)) { doShield(eff, src, srcColor, val); return; }   // 有数值的护盾（没选方式的只触发“受到护盾时”，走下面）''')
F.rep('''      if (num(eff.hpLE) > 0 && src) { const c = evTarget === src''', '''      if (eff.hasSh && shTrack) { const c = String(eff.hasSh), neg = c[0] === "!", [w, key] = (neg ? c.slice(1) : c).split(":"), T = w === "e" ? evTarget : src; if ((shOf(T, key) > 0) === neg) return; }   // 持有护盾才生效（e = 事件对象，s = 自己；! = 没有护盾才生效；:组 = 只看这一组）
      if (num(eff.hpLE) > 0 && src) { const c = evTarget === src''')
a = '''      if (num(eff.lim) > 0) { const k = (src ? src.id : "ev") + ":lim:" + eff.id;'''
i = F.s.index(a); j = F.s.index('\n', i); assert F.s.count(a) == 1
F.s = F.s[:j + 1] + '''      if (num(eff.cdT) > 0 && src) { const k = src.id + ":cd:" + eff.id; if (firedMap[k] != null && num(src.turns) < firedMap[k] + num(eff.cdT)) return; firedMap[k] = num(src.turns); }   // 触发后要过 N 个自己的回合才能再触发（记忆的质料）
''' + F.s[j + 1:]
F.rep('''      tickSt(actor, "end");''', '''      tickSt(actor, "end"); tickSh(actor);''')
F.rep('''      const c = b.ec;
''', '''      const c = b.ec;
      if (c.sh && !(shOf(u) > 0)) return 0;   // 持有者持有护盾时（记忆的质料减伤）
''')
F.rep('''      if (target === "elow") {''', '''      if (target === "lowsh") {   // 护盾值最低的我方目标（没有护盾算 0；一样低时按队伍顺序）
        let b = null, bv = Infinity;
        for (const u of U) if (u.kind === "ally" && !u.gone && !isCd(u) && !isOut(u) && (!u.sm || u.sm.mem)) { const v = shOf(u); if (v < bv - 1e-9) { b = u; bv = v; } }
        return b ? [b] : [];
      }
      if (target === "elow") {''')
# 新触发 hit2：受到攻击后（伤害结算之后；hit 在扣血之前）
F.rep('''if (eff.type === "hit" && tg.kind === "ally") { if (num(eff.dmg) > 0) takeHit(tg, num(eff.dmg), src); else fireEv("hpLoss", tg); }''',
      '''if (eff.type === "hit" && tg.kind === "ally") { if (num(eff.dmg) > 0) takeHit(tg, num(eff.dmg), src); else fireEv("hpLoss", tg); if (!tg.gone) fireEv("hit2", tg); }''')
F.rep('''["hit", "受到攻击时"], ''', '''["hit", "受到攻击时"], ["hit2", "受到攻击后（伤害结算后）"], ''', 2)
F.rep('''hit: "受到攻击时"''', '''hit: "受到攻击时", hit2: "受到攻击后（伤害结算后）"''')
F.rep('''["kill", "hit", "hpLoss"].some(k => e.trigger === k || e.or === k)''', '''["kill", "hit", "hit2", "hpLoss"].some(k => e.trigger === k || e.or === k)''')
F.rep('''const EVTT = ["break", "kill", "hit", ''', '''const EVTT = ["break", "kill", "hit", "hit2", ''')
F.rep('''["lowhp", "生命值百分比最低的我方目标"], ''', '''["lowhp", "生命值百分比最低的我方目标"], ["lowsh", "护盾值最低的我方目标"], ''')

# ================= 编辑器 =================
F.rep('''${["shield", "extra", "summon", "dismiss", "fua", "cast", "state", "pend"].includes(e.type) || (e.type === "energy"''',
      '''${(e.type === "shield" && !SHM.includes(e.mode)) || ["extra", "summon", "dismiss", "fua", "cast", "state", "pend"].includes(e.type) || (e.type === "energy"''')
F.rep('''e.type === "heal" || e.type === "hpup" || e.type === "hpcost" ? "0.1" : "1"}" value="${e.value}" data-u="${i}" data-e="${j}" data-f="value" aria-label="${e.type === "heal" ? "治疗百分比" :''',
      '''e.type === "heal" || e.type === "shield" || e.type === "hpup" || e.type === "hpcost" ? "0.1" : "1"}" value="${e.value}" data-u="${i}" data-e="${j}" data-f="value" aria-label="${e.type === "heal" ? "治疗百分比" : e.type === "shield" ? "护盾百分比" :''')
F.rep('''e.type === "shield" ? "（让目标触发“受到护盾时”的效果）"''', '''e.type === "shield" ? shieldEd(u, e, i, j)''')
F.rep('''  const hpupEd = (u, e, i, j) => {''', '''  const shieldEd = (u, e, i, j) => {
    const m = SHM.includes(e.mode) ? e.mode : "";
    return `<select id="eshm-${e.id}" data-u="${i}" data-e="${j}" data-f="mode" aria-label="护盾按什么算">${opt([["def", "% 防御力"], ["atk", "% 攻击力"], ["hp", "% 生命上限"], ["", "不计数值"]], m)}</select>`
      + (m ? ` + <input type="number" id="eshf-${e.id}" min="0" step="1" value="${num(e.flat)}" data-u="${i}" data-e="${j}" data-f="flat" aria-label="固定值" style="width:64px"> 持续<input type="number" id="ed-${e.id}" min="0" step="1" value="${num(e.duration)}" data-u="${i}" data-e="${j}" data-f="duration" aria-label="持续回合" title="目标自己的回合结束时 −1；“敌人打我方掉血”开着时抵挡伤害" style="width:42px">回合` : "（只让目标触发“受到护盾时”的效果）")
      + (m && e.shk && num(e.shCap) > 0 ? `<span class="hint">同一组可以叠加，最多战技护盾量的 ${num(e.shCap)}%</span>` : "")
      + (m ? `<span class="hint" data-pv="${i}:${j}">${healPreview(u, e)}</span>` : "");
  };
  const hpupEd = (u, e, i, j) => {''')
F.rep('''      if (f === "type" && val === "heal" && !HEALM.includes(e.mode)) { e.mode = "hp"; e.value = 10; e.flat = 0; }''',
      '''      if (f === "type" && val === "heal" && !HEALM.includes(e.mode)) { e.mode = "hp"; e.value = 10; e.flat = 0; }
      if (f === "type" && val === "shield" && !SHM.includes(e.mode)) { e.mode = "def"; e.value = 20; e.flat = 0; e.duration = 3; }''')
F.rep('''    if (e.type === "heal") return `${t} → ${healSum(e)}${c}`;''', '''    if (e.type === "heal") return `${t} → ${healSum(e)}${c}`;
    if (e.type === "shield" && SHM.includes(e.mode)) return `${t} → 护盾 ${num(e.value)}% ${SHL[e.mode]}${num(e.flat) ? " +" + num(e.flat) : ""}${num(e.duration) > 0 ? ` ${num(e.duration)} 回合` : ""}${c}`;''')
F.rep('''    const m = e.mode; if (!HEALM.includes(m)) return "";''', '''    if (e.type === "shield") {   // 护盾：按这张卡（召唤物用主人）的面板属性，不含增益和提供的护盾量加成
      if (!SHM.includes(e.mode)) return "";
      const H = (u.sm && S.units.find(x => x.id === u.sm.owner)) || u, b = cardStat(H, e.mode);
      if (b == null) return `（${esc(H.name)}没有${SHL[e.mode]}数值，填了面板才能算）`;
      return `≈ ${Math.round(b * num(e.value) / 100 + num(e.flat))}（按面板${SHL[e.mode]}）`;
    }
    const m = e.mode; if (!HEALM.includes(m)) return "";''')
F.rep('''    if (e.tEl) h.push(`只对${e.tEl.split("").join(" / ")}属性的攻击生效`);
    if (e.tEl) h.push(num(e.tEl) > 0 ? "只对欢愉角色" : "只对非欢愉角色");''', '''    if (e.tEl && !/^-?\\d/.test(String(e.tEl))) h.push(`只对${e.tEl.split("").join(" / ")}属性的攻击生效`);
    if (e.tEl && /^-?\\d/.test(String(e.tEl))) h.push(num(e.tEl) > 0 ? "只对欢愉角色" : "只对非欢愉角色");
    if (e.hasSh) { const c = String(e.hasSh), neg = c[0] === "!", [w, key] = (neg ? c.slice(1) : c).split(":"); h.push(`${w === "e" ? "事件对象" : "自己"}${neg ? "没有" : "持有"}${key ? "这一组" : ""}护盾时才生效`); }
    if (num(e.cdT) > 0) h.push(`触发后 ${num(e.cdT)} 个自己的回合内不再触发`);''')
F.rep('''    if (e.ec) h.push("出手时按主目标的状态算");''', '''    if (e.ec) h.push(e.ec.sh ? "持有护盾时生效" : "出手时按主目标的状态算");''')
F.rep('''["defP", "防御力 %"]''', '''["defP", "防御力 %"], ["dr", "受到的伤害降低 %（敌人打我方）"], ["shB", "提供的护盾量 %"]''')
F.rep('''defP: "防御力", cr: "暴击率"''', '''defP: "防御力", dr: "受到的伤害降低", shB: "提供的护盾量", cr: "暴击率"''')
F.rep('''defP: "防御力%", cr: "暴击率"''', '''defP: "防御力%", dr: "受到的伤害降低%", shB: "提供的护盾量%", cr: "暴击率"''')
F.rep('''勾上 = 敌人模板按官方攻击力和技能倍率打我方，扣当前生命值；''', '''勾上 = 敌人模板按官方攻击力和技能倍率打我方，乘我方受到的伤害降低，先由护盾抵挡（几个护盾按最大的算；符玄【穷观阵】先分走 65%），再扣当前生命值；''')

# ================= 数据 =================
def setx(e, **kw):
    for k, v in kw.items():
        if v is None: e.pop(k, None)
        else: e[k] = v
    return e

# 三月七
c = C[1001]
has('100102', '为指定我方单体提供能够抵消等同于三月七#1[i]%防御力+#4[i]伤害的护盾，持续#2[i]回合')
hast(1001, '加护', '战技提供的护盾持续时间增加#1[i]回合')
p10, p12 = prm('100102', 10), prm('100102', 12); assert r4(p10[0]) == 0.57 and p10[3] == 760 and p10[1] == 3 and r4(p12[0]) == 0.608 and p12[3] == 845.5
N1 = '战技：为指定我方单体提供护盾（三月七 57% 防御力 +760，5 魂 60.8% +845.5），持续 4 回合（含行迹加护 +1）'
setx(c['eff'][0], n=N1, m='def', v=57, lv=[5, 60.8], hf=760, lx={'flat': [760, 845.5]}, d=4)
assert c['eff'][1]['n'].startswith('天赋少女的特权'); c['eff'][1]['hsh'] = 'e'
F.rebuild(1001, c['eff'], rename={'战技：护盾': N1})
has('r:100102', '进入战斗时，为当前生命值百分比最低的我方目标提供等同于三月七24%防御力+320的护盾，持续3回合')
e2 = F.eid(1001, 2); assert e2['eff'][0]['y'] == 'shield'
setx(e2['eff'][0], m='def', v=24, hf=320, d=3, n='E2 记忆中的它：进入战斗时为当前生命值百分比最低的我方目标提供护盾（三月七 24% 防御力 +320），持续 3 回合')

# 杰帕德
c = C[1104]
has('110403', '为我方全体提供能够抵消等同于杰帕德#1[i]%防御力+#3[i]伤害的护盾，持续#2[i]回合')
p10, p12 = prm('110403', 10), prm('110403', 12); assert r4(p10[0]) == 0.45 and p10[2] == 600 and p10[1] == 3 and r4(p12[0]) == 0.48 and p12[2] == 667.5
t = prm('110407', 1); assert r4(t[0]) == 0.24 and t[1] == 2 and t[2] == 150
NU = '终结技：为我方全体提供护盾（杰帕德 45% 防御力 +600，3 魂 48% +667.5），持续 3 回合'
NT = '秘技有情之证：下一次战斗开始时为我方全体提供护盾（24% 防御力 +150），持续 2 回合（用了秘技再启用）'
setx(c['eff'][0], n=NU, m='def', v=45, lv=[3, 48], hf=600, lx={'flat': [600, 667.5]}, d=3)
assert c['eff'][4]['n'].startswith('秘技有情之证'); OT = c['eff'][4]['n']
setx(c['eff'][4], n=NT, m='def', v=24, hf=150, d=2)
F.rebuild(1104, c['eff'], rename={'终结技：护盾': NU, OT: NT})

# 砂金
c = C[1304]
has('130402', '为我方全体提供能够抵消等同于砂金#1[f1]%防御力+#2[i]伤害的护盾【坚垣筹码】，持续#3[i]回合。重复获得【坚垣筹码】时，护盾量可以叠加，最高不超过当前战技提供的护盾量的#4[i]%')
hast(1304, '热手', '战斗开始时，为我方全体提供护盾【坚垣筹码】，护盾量等同于战技提供的护盾量的#2[i]%，持续#1[i]回合')
hast(1304, '宾果！', '砂金在发动天赋的追加攻击后，为我方全体提供能够抵消等同于砂金#1[i]%防御力+#2[i]伤害的【坚垣筹码】，并为护盾值最低的我方目标额外提供能够抵消等同于砂金#4[i]%防御力+#5[i]伤害的【坚垣筹码】，持续3回合')
has('r:130401', '施放终结技后，为我方全体提供护盾【坚垣筹码】，护盾量等同于战技提供的护盾量的100%，持续3回合')
p10, p12 = prm('130402', 10), prm('130402', 12); assert r4(p10[0]) == 0.24 and p10[1] == 320 and p10[2] == 3 and p10[3] == 2 and r4(p12[0]) == 0.256 and p12[1] == 356
JY = dict(m='def', v=24, lv=[5, 25.6], hf=320, lx={'flat': [320, 356]}, d=3, shk='jy', shc=200)
L0 = {e['n']: e for e in c['eff']}
o0, o1, o2, o6 = c['eff'][0]['n'], c['eff'][1]['n'], c['eff'][2]['n'], c['eff'][6]['n']
assert o1.startswith('行迹热手') and o2.startswith('天赋：持有【坚垣筹码】') and o6.startswith('行迹宾果！：发动天赋的追加攻击后')
S0 = '战技：为我方全体提供护盾【坚垣筹码】（砂金 24% 防御力 +320，5 魂 25.6% +356），持续 3 回合；可以叠加，最多战技护盾量的 200%'
S1 = '行迹热手：战斗开始时为我方全体提供护盾【坚垣筹码】（等同于战技护盾量），持续 3 回合'
S2 = '天赋：持有【坚垣筹码】的我方单体受到攻击后，砂金获得 1 点【盲注】'
S6 = '行迹宾果！：发动天赋的追加攻击后为我方全体提供【坚垣筹码】（7.2% 防御力 +96），持续 3 回合'
S6b = '行迹宾果！：同时为护盾值最低的我方目标额外提供【坚垣筹码】（7.2% 防御力 +96）'
setx(c['eff'][0], n=S0, shb=1, **JY)
setx(c['eff'][1], n=S1, **JY)
setx(c['eff'][2], n=S2, hsh='e:jy')
assert c['eff'][3]['n'].startswith('天赋：砂金自己持有【坚垣筹码】'); c['eff'][3]['hsh'] = 'e:jy'
assert c['eff'][4]['n'].startswith('行迹宾果！：持有【坚垣筹码】的队友'); c['eff'][4]['hsh'] = 'e:jy'
setx(c['eff'][6], n=S6, m='def', v=7.2, hf=96, d=3, shk='jy', shc=200)
c['eff'].insert(7, dict(y='shield', t='fua', tg='lowsh', m='def', v=7.2, hf=96, d=3, shk='jy', shc=200, n=S6b))
c['notes'] = ['天赋的追加攻击每段恢复 1 点能量（7 段 = 7 点，E4 再多 3 段）；效果抵抗、抵抗控制没算',
              '【坚垣筹码】：战技 / 热手 / E1 都按战技护盾量，宾果按 7.2% +96；同一组叠加，最多战技护盾量（按砂金当前防御力）的 200%']
F.rebuild(1304, c['eff'], rename={o0: S0, o1: S1, o2: S2, o6: S6})
e1 = F.eid(1304, 1); z = [x for x in e1['eff'] if x['y'] == 'shield']; assert len(z) == 1
setx(z[0], n='E1 囚徒博弈：施放终结技后为我方全体提供护盾【坚垣筹码】（等同于战技护盾量），持续 3 回合', **JY)

# 丹恒•腾荒
c = C[1414]
has('141402', '为我方全体提供能够抵消等同于丹恒•腾荒#1[f1]%攻击力+#2[i]伤害的护盾，持续#3[i]回合。重复获得丹恒•腾荒的护盾时，护盾量可以叠加，最高不超过当前战技提供的护盾量的#4[i]%')
has('141403', '为我方全体提供能够抵消等同于丹恒•腾荒#4[f1]%攻击力+#5[i]伤害的护盾，持续#6[i]回合')
has('141404', '【龙灵】行动时，解除我方全体的#6[i]个负面效果，并提供能够抵消等同于丹恒•腾荒#1[f1]%攻击力+#2[i]伤害的护盾，持续#3[i]回合。丹恒•腾荒和【龙灵】提供的护盾量可以叠加，最高不超过丹恒•腾荒战技提供的护盾量的#4[i]%')
hast(1414, '峥嵘', '【龙灵】行动时，额外为当前护盾值最低的我方目标提供能够抵消等同于丹恒•腾荒#2[i]%攻击力+#3[i]伤害的护盾')
s10, s12 = prm('141402', 10), prm('141402', 12); assert r4(s10[0]) == 0.2 and s10[1] == 400 and s10[2] == 3 and s10[3] == 3 and r4(s12[0]) == 0.212 and s12[1] == 445
u10, u12 = prm('141403', 10), prm('141403', 12); assert r4(u10[3]) == 0.2 and u10[4] == 400 and u10[5] == 3 and r4(u12[3]) == 0.212 and u12[4] == 445
t10, t12 = prm('141404', 10), prm('141404', 12); assert r4(t10[0]) == 0.1 and t10[1] == 200 and t10[2] == 3 and r4(t12[0]) == 0.106 and t12[1] == 222.5
D0, D1, D2 = c['eff'][2]['n'], c['eff'][3]['n'], c['eff'][4]['n']; assert D0.startswith('战技：为我方全体') and D1.startswith('终结技：为我方全体') and D2.startswith('天赋：【龙灵】行动时')
N0 = '战技：为我方全体提供护盾（丹恒•腾荒 20% 攻击力 +400，5 魂 21.2% +445），持续 3 回合；可以叠加，最多战技护盾量的 300%'
N1 = '终结技：为我方全体提供护盾（20% 攻击力 +400，3 魂 21.2% +445），持续 3 回合'
N2 = '天赋：【龙灵】行动时为我方全体提供护盾（10% 攻击力 +200，5 魂 10.6% +222.5），持续 3 回合'
setx(c['eff'][2], n=N0, m='atk', v=20, lv=[5, 21.2], hf=400, lx={'flat': [400, 445]}, d=3, shk='dh', shc=300, shb=1)
setx(c['eff'][3], n=N1, m='atk', v=20, lv=[3, 21.2], hf=400, lx={'flat': [400, 445]}, d=3, shk='dh', shc=300)
setx(c['eff'][4], n=N2, m='atk', v=10, lv=[5, 10.6], hf=200, lx={'flat': [200, 222.5]}, d=3, shk='dh', shc=300)
c['eff'].insert(5, dict(y='shield', t='ally', aw='sm', tg='lowsh', m='atk', v=5, hf=100, d=3, shk='dh', shc=300, n='行迹峥嵘：【龙灵】行动时额外为护盾值最低的我方目标提供护盾（5% 攻击力 +100）'))
c['notes'] = [n.replace('行迹峥嵘的额外护盾和附加伤害', '行迹峥嵘的附加伤害') for n in c.get('notes', [])]
F.rebuild(1414, c['eff'], rename={D0: N0, D1: N1, D2: N2})

# 开拓者•存护
for cid in (8003, 8004):
    c = C[cid]; k = str(cid)
    has(k + '04', '开拓者施放普攻、战技、终结技后，为我方全体提供能够抵消等同于开拓者#1[f1]%防御力+#4[i]伤害的护盾，持续#2[i]回合')
    has(k + '07', '使用秘技后，下一次战斗开始时给自身提供能够抵消等同于开拓者#1[i]%防御力+#2[i]伤害的护盾，持续#3[i]回合')
    has(k + '02', '施放战技后，开拓者受到的伤害降低#1[i]%')
    hast(cid, '强援弱', '施放战技后，我方全体受到的伤害降低#2[i]%，持续#3[i]回合')
    hast(cid, '行胜思', '回合开始时，若开拓者持有护盾保护，则攻击力提高#2[i]%并恢复#1[i]点能量，持续到行动结束')
    has('r:' + k + '02', '触发天赋时，为我方全体提供的护盾能够额外抵消等同于开拓者防御力2%+27的伤害')
    p10, p12 = prm(k + '04', 10), prm(k + '04', 12); assert r4(p10[0]) == 0.06 and p10[3] == 80 and p10[1] == 2 and r4(p12[0]) == 0.064 and p12[3] == 89
    tq = prm(k + '07', 1); assert r4(tq[0]) == 0.3 and tq[1] == 384 and tq[2] == 1
    sk = prm(k + '02', 10); assert r4(sk[0]) == 0.5 and sk[2] == 1
    E = c['eff']
    assert E[6]['n'].startswith('天赋筑城者遗宝：施放普攻、战技后') and E[7]['n'].startswith('天赋筑城者遗宝：施放终结技后') and E[8]['n'].startswith('秘技守护者召令') and E[9]['n'].startswith('行迹行胜思') and E[11]['n'].startswith('行迹行胜思')
    o7, o9, o11 = E[7]['n'], E[9]['n'], E[11]['n']
    ZC = dict(m='def', v=6, lv=[3, 6.4], hf=80, lx={'flat': [80, 89]}, d=2, shk='zc', xe=2)
    n7 = '天赋筑城者遗宝：施放终结技后为我方全体提供护盾（6% 防御力 +80，3 魂 6.4% +89），持续 2 回合'
    n9 = '行迹行胜思：回合开始时持有护盾则恢复 5 点能量'
    n11 = '行迹行胜思：回合开始时持有护盾则攻击力 +15%，持续到行动结束'
    setx(E[6], **ZC); setx(E[7], n=n7, **ZC)
    setx(E[8], m='def', v=30, hf=384, d=1)
    setx(E[9], n=n9, hsh='s', off=None); setx(E[11], n=n11, hsh='s', off=None)
    E += [dict(y='dbuf', t='skill', tg='self', m='dr', v=50, d=1, bk='zj', n='战技：施放后开拓者受到的伤害降低 50%，持续 1 回合（嘲讽没做：敌人打谁按敌人卡设置）'),
          dict(y='dbuf', t='skill', tg='team', m='dr', v=15, d=1, bk='qyr', n='行迹强援弱：施放战技后我方全体受到的伤害降低 15%，持续 1 回合')]
    c['notes'] = ['战技的嘲讽没做（敌人打谁按敌人卡的设置）；受到的伤害降低和护盾只在“敌人打我方掉血”开着时影响生命值']
    F.rebuild(cid, E, rename={o7: n7, o9: n9, o11: n11}, off0=[o9, o11])
    e2 = F.eid(cid, 2)
    E2 = dict(m='def', v=8, lv=[3, 8.4], hf=107, lx={'flat': [107, 116]}, d=2, shk='zc')
    e2['eff'] = [x for x in e2['eff'] if x.get('y') != 'shield'] + [
        dict(y='shield', t='basic', o='skill', tg='allies', n='E2 古老寒铁的坚守：施放普攻、战技后的护盾额外 +2% 防御力 +27（合计 8% +107，3 魂 8.4% +116），持续 2 回合', **E2),
        dict(y='shield', t='ult', tg='allies', n='E2：施放终结技后的护盾同样额外 +2% 防御力 +27（合计 8% +107，3 魂 8.4% +116）', **E2)]

# 符玄
c = C[1208]
has('120802', '开启【穷观阵】，使符玄队友所承受的未受护盾抵挡之前的伤害的#1[i]%分摊给符玄')
has('120804', '当符玄处于可战斗状态时，为我方全体附加【避厄】。【避厄】状态下的我方目标受到的伤害降低#1[f1]%')
q = prm('120802', 10); assert r4(q[0]) == 0.65
b10, b12 = prm('120804', 10), prm('120804', 12); assert r4(b10[0]) == 0.18 and r4(b12[0]) == 0.196
c['eff'].append(dict(y='dbuf', t='start', tg='team', m='dr', v=18, lv=[3, 19.6], d=0, bk='bie', n='天赋：符玄在场时我方全体获得【避厄】，受到的伤害降低 18%（3 魂 19.6%）'))
c['notes'] = c.get('notes', []) + ['【穷观阵】分担：“敌人打我方掉血”开着时，队友受到的伤害（护盾抵挡之前）的 65% 由符玄承担（再由符玄自己的护盾抵挡）；符玄倒下后【避厄】没有自动去掉']
F.rebuild(1208, c['eff'], x={'share': ['穷观阵', 65]})

# 光锥：记忆的质料；遗器：净庭教宗的圣骑士 4 件
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8'))
F.has(LR['24002']['desc'], '当装备者受到攻击后，如果自身未持有护盾，则获得1个等同于装备者#2[i]%生命上限的护盾，持续#3[i]回合。该效果每#4[i]回合只能触发1次。如果装备者持有护盾，则使自身受到的伤害降低#5[i]%')
P = LR['24002']['params']; assert all(p[2] == 2 and p[3] == 3 for p in P)
L = {x['id']: x for x in F.DB['lcs']}
L[24002]['eff'] = [dict(y='shield', t='hit2', ew='self', tg='self', m='hp', v=[r4(p[1] * 100) for p in P], d=2, hsh='!s', cdt=3, n='光锥：受到攻击后若自身没有护盾，获得生命上限 16% 的护盾，持续 2 回合（每 3 回合 1 次）'),
                   dict(y='dbuf', t='start', tg='self', m='dr', v=[r4(p[4] * 100) for p in P], d=0, bk='lc', ec={'sh': 1}, n='光锥：持有护盾时受到的伤害降低 12%')]
L[24002]['notes'] = ['效果抵抗没算；“受到攻击后”按这一下伤害结算之后有没有护盾判断（触发：受到攻击后（伤害结算后））']
RS = json.load(open(sys.argv[2] + '/relic_sets.json', encoding='utf-8'))
assert RS['103']['desc'][1] == '使装备者提供的护盾量提高20%。', RS['103']['desc']
R = {x['id']: x for x in F.DB['relics']}
R[103]['p4']['eff'] = [dict(y='dbuf', t='start', tg='self', m='shB', v=20, d=0, bk='r', n='4件：提供的护盾量提高 20%')]

F.finish('护盾数值和抵挡、符玄分担、受到的伤害降低', '''<li><b>2026-11-11（护盾）</b>：tv 82（tools/fix82.py）。<b>护盾有数值了</b>：护盾效果可以选“按 防御力 / 攻击力 / 生命上限 的 % + 固定值、持续几回合”，模板按官方数值补齐——三月七（战技 57% +760，含行迹加护 4 回合；E2 开局护盾）、杰帕德（终结技、秘技）、砂金（【坚垣筹码】战技 / 热手 / 宾果 / E1，可叠加到战技护盾量的 200%；宾果额外给护盾最低的目标）、丹恒•腾荒（战技 / 终结技 / 龙灵，可叠加到 300%；峥嵘额外给护盾最低的目标）、开拓者•存护（天赋护盾、E2 +2% +27、秘技）。护盾量按施放者<b>当前</b>属性（面板 + 增益）算，再乘“提供的护盾量”（净庭教宗 4 件 +20%）。<b>抵挡伤害</b>：开了“敌人打我方掉血”时，敌人的伤害先乘<b>受到的伤害降低</b>（新的增益属性：符玄【避厄】18%、开拓者•存护战技 50% / 强援弱 15%、记忆的质料持盾时 12%），符玄【穷观阵】分走 65%（护盾抵挡之前），再由护盾抵挡（几个护盾按最大的算），剩下的扣生命值；行动记录里写“护盾抵挡 N（护盾破碎）”。护盾在持有者回合结束时 −1 回合，倒下时清空。<b>条件</b>：三月七反击、砂金【盲注】现在要求被打 / 追击的目标真的持有护盾（【坚垣筹码】），开拓者•存护行胜思改成默认开、回合开始时有护盾才生效；记忆的质料没有护盾时受击获得护盾（每 3 回合 1 次）。对已有配置：上面这些角色的护盾效果会换成有数值的版本（你改过触发的保留触发）；掉血开关关着时只多了护盾记录，行动顺序只在三月七 / 砂金 / 存护主的“持有护盾”条件不满足时变化。</li>''',
'''2026-11-11：护盾数值和抵挡 —— tv 82（tools/fix82.py）。新：护盾方式 def / atk / hp、触发 hit2、字段 shk / shCap / shBase / hasSh / cdT、目标 lowsh、dbuf dr / shB、伤害增益条件 ec.sh、模板 x.share（符玄）。
  未改 / 存疑：护盾持续回合按持有者回合结束 −1（自己回合内获得的这回合算第 1 回合，和状态一样）；同一组再次获得时直接刷新为新数值（没写叠加的）；新触发 hit2（受到攻击后，伤害结算后；原来的 hit 在扣血之前）只给记忆的质料用了，三月七 / 砂金的“持有护盾的目标受到攻击后”仍按被打之前有没有护盾判断；三月七战技的嘲讽、存护主的嘲讽没做；符玄倒下后【避厄】还在；自匿星芒的隐士 / 砂金 E1 / E6 的“持有护盾时”增益仍按一直有护盾算''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX82); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX82); for (const u of s.units) if (u.kind === "ally" && !u.sm && (u.lc === 24002 || (u.rA === 103 && u.r4))) applyEquip(u); } finally { S = keep; } }   // 记忆的质料、净庭教宗 4 件改了')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
