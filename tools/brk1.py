"""击破第 1 步：韧性条、弱点击破、击破伤害和击破附带的状态。用法：python3 tools/brk1.py index.html（先跑 tools/build_tgh.py 生成削韧表和敌人韧性）
模拟：敌人套了模板（或卡片上填了“韧性”）才有韧性条；我方攻击按官方削韧值（TGH：[主目标, 全体, 相邻]）削韧，只对弱点属性生效；
削到 0 = 击破：敌人行动延后 25%，按击破者的属性附带效果（物理裂伤 / 火灼烧 / 雷触电 / 风风化各 2 回合，冰冻结跳过 1 个回合后行动提前 50%，
量子纠缠再延后 20%×(1+击破特攻)，虚数禁锢再延后 30%×(1+击破特攻) 并减速 10%），触发我方“弱点击破时”的效果；敌人下一个回合开始时韧性恢复。
伤害：击破伤害 = 3767.55（80 级）× 属性系数 × (0.5 + 韧性/120) × (1 + 击破特攻) × 防御 × 抗性 × 易伤，不暴击、不吃增伤；
击破的持续伤害同样按 3767.55 × (1 + 击破特攻)。角色卡新增“击破特攻 %”，伤害增益新增类型“击破特攻”。
韧性没破时伤害 ×0.9 改成按模拟里敌人当时的状态（没有韧性条的敌人仍看“伤害设置”里的“已击破”）。伤害设置里可以关掉“模拟韧性和击破”。
没做：超击破、击破效率、无视弱点削韧、弱点植入、纠缠叠层、不同首领的多条韧性。
"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------------- 模拟 ----------------
rep('    const dotRecs = [], dotdCnt = {}; let dotDepth = 0, dotBag = null;', '''    const dotRecs = [], dotdCnt = {}; let dotDepth = 0, dotBag = null;
    // ---------- 韧性和弱点击破（敌人套了模板或填了韧性才有；伤害设置里可以关）----------
    const brkOn = !(S.dg && S.dg.noBrk);
    const ELW = { Physical: "物", Fire: "火", Ice: "冰", Thunder: "雷", Lightning: "雷", Wind: "风", Quantum: "量", Imaginary: "虚" };
    const BRKM = { 物: 2, 火: 2, 冰: 1, 雷: 1, 风: 1.5, 量: 0.5, 虚: 0.5 };
    const monOf = en => { if (en.__mon === undefined) en.__mon = (en.mon && MON.m.find(m => m.n === en.mon)) || null; return en.__mon; };
    const toughMax = en => { if (en.__tm === undefined) { const m = monOf(en); en.__tm = !brkOn ? 0 : en.tough != null && en.tough !== "" ? Math.max(0, num(en.tough)) : m && m.tn ? m.tn : 0; } return en.__tm; };
    const ebkNow = () => { const en = U.find(x => x.kind === "enemy" && !x.gone && toughMax(x) > 0); return en ? !!en.broken : undefined; };   // 伤害显示用：主目标（第一个有韧性的敌人）现在破了没有
    const beOf = o => num(o.be) + (o.buffs || []).reduce((p, b) => p + (b.kind === "d" && b.st === "be" ? num(b.v) : 0), 0);   // 击破特攻 %（卡片 + 增益）
    const doBreak = (en, o, el, mx) => {
      en.tcur = 0; en.broken = true;
      const tm = 0.5 + mx / 120, be = beOf(o), m = monOf(en), big = !!(m && /^[BLE]$/.test(m.r || ""));
      marks.push({ t, uid: en.id, label: "击破", color: o.color, from: o.name });
      const r = { t, uid: o.id, en: en.id, k: "击破", mult: BRKM[el] * tm, stat: "brk", why: "break", db: dbSnap(o), edb: edbSnap(), defIg: 0, seq: seq++, ebk: true };
      dotRecs.push(r);
      let extra = "";
      const dot = (k, v, left, n) => { en.dots = (en.dots || []).filter(z => z.key !== o.id + ":brk:" + k); en.dots.push({ key: o.id + ":brk:" + k, src: o.id, k, v, vps: 0, stm: n > 1, n: n || 1, stat: "brk", half: false, keepSt: "", defIg: 0, adjV: 0, cap: 5, left }); };
      en.dist += 2500;   // 弱点击破：行动延后 25%
      if (el === "物") { dot("裂伤", 200 * tm, 2); extra = "，陷入裂伤 2 回合"; }
      else if (el === "火") { dot("灼烧", 100, 2); extra = "，陷入灼烧 2 回合"; }
      else if (el === "雷") { dot("触电", 200, 2); extra = "，陷入触电 2 回合"; }
      else if (el === "风") { dot("风化", 100, 2, big ? 3 : 1); extra = `，陷入风化 ${big ? 3 : 1} 层 2 回合`; }
      else if (el === "冰") { en.frozen = true; dot("冻结", 100, 1); extra = "，冻结（跳过下一个回合，之后行动提前 50%）"; }
      else if (el === "量") { const d = 20 * (1 + be / 100); en.dist += d * 100; dot("纠缠", 60 * tm, 1); extra = `，纠缠：行动再延后 ${fmt(d, 1)}%`; }
      else if (el === "虚") { const d = 30 * (1 + be / 100); en.dist += d * 100; extra = `，禁锢：行动再延后 ${fmt(d, 1)}%、速度 −10%`;
        apply({ id: "brk-imp-" + en.id, type: "spd", mode: "pct", value: -10, duration: 1, count: "own", target: en.id, bk: "brkimp", note: "禁锢" }, o, o.color); }
      addLog(`${o.name} 击破 ${en.name} 的弱点（${el}属性）：行动延后 25%${extra}`, false, o.color); log[log.length - 1].dd = [r];
      fireEv("break", en);   // 我方“弱点击破时”的效果
    };
    const toughHit = (who, key) => {
      if (!brkOn || !key || !who) return;
      const o = ownerOf(who) || who, T0 = o.kind === "ally" ? tplOf(o) : null; if (!T0) return;
      const tb = TGH[T0.id]; if (!tb) return;
      if ((key === "s" || key === "u") && tb[key + "2"]) { try { const f = (key === "s" ? S2ST : U2ST)[String(T0.id)]; if (f && f({ sts: o.st ? Object.keys(o.st).filter(k => o.st[k]) : [], mIn: U.some(x => x.sm && x.sm.owner === o.id && x.sm.mem && !x.gone) })) key += "2"; } catch (e) { /* 按普通版 */ } }
      const v = tb[key]; if (!v) return;
      const el = ELW[T0.elem] || "";
      U.filter(x => x.kind === "enemy" && !x.gone).forEach((en, i) => {
        const mx = toughMax(en); if (!(mx > 0) || en.broken) return;
        const m = monOf(en); if (m && m.w && el && !m.w.includes(el)) return;   // 不是弱点属性：不削韧
        const amt = num(v[1]) + (i === 0 ? num(v[0]) : i <= 2 ? num(v[2]) : 0); if (!(amt > 0)) return;
        if (en.tcur == null) en.tcur = mx;
        en.tcur -= amt;
        if (en.tcur <= 1e-9) doBreak(en, o, el || "物", mx);
      });
    };''')
rep('    const atkAct = (who, fromFua) => teamFire("atk", who, fromFua ? e => !e.nf : null);',
    '''    const ACT2K = { basic: "b", ebasic: "b2", skill: "s", fskill: "s", ult: "u", el: "e" };
    const atkAct = (who, fromFua, act) => { toughHit(who, fromFua ? "f" : ACT2K[act]); teamFire("atk", who, fromFua ? e => !e.nf : null); };   // 攻击：先削韧（可能击破），再触发“攻击后”''')
rep('        if (isAtk(u, k)) atkAct(u);', '        if (isAtk(u, k)) atkAct(u, false, k);')
rep('      if (u.atkUlt !== false) atkAct(u);', '      if (u.atkUlt !== false) atkAct(u, false, "ult");')
rep('      if (swU.atkUlt !== false) atkAct(swU);', '      if (swU.atkUlt !== false) atkAct(swU, false, "ult");')
rep('        if (dmg === "yes" || (dmg === "ult" && u === swU && sw.inUlt)) atkAct(u);', '        if (dmg === "yes" || (dmg === "ult" && u === swU && sw.inUlt)) atkAct(u, false, "el");')
rep('        if (isAtk(swU, rec.act)) atkAct(swU);', '        if (isAtk(swU, rec.act)) atkAct(swU, false, rec.act);')
rep('        else if (isAtk(u, rec.act)) atkAct(u);', '        else if (isAtk(u, rec.act)) atkAct(u, false, rec.act);')
rep('      if (rec.act) { rec.sp = sp; if (isAtk(actor, rec.act)) atkAct(actor); }', '      if (rec.act) { rec.sp = sp; if (isAtk(actor, rec.act)) atkAct(actor, false, rec.act); }')
# 敌人回合开始：韧性恢复、冻结
rep('      if (actor.kind === "enemy") { dotTick(actor); fireAll("eturn", actor); }   // 敌方回合开始：持续伤害结算，再触发“敌方回合开始时”',
    '''      if (actor.kind === "enemy") {   // 敌方回合开始：韧性恢复 → 持续伤害结算 → “敌方回合开始时”
        if (actor.broken) { actor.broken = false; actor.tcur = toughMax(actor); marks.push({ t, uid: actor.id, label: "韧性恢复", color: actor.color, from: actor.name }); }
        if (actor.frozen) { actor.frozen = false; rec.frz = true; addLog(`${actor.name} 被冻结：跳过这个回合，之后行动提前 50%`, false, actor.color); }
        dotTick(actor); fireAll("eturn", actor);
      }''')
rep('      if (actor.kind === "enemy" && actor.atkWho) {', '      if (actor.kind === "enemy" && actor.atkWho && !rec.frz) {')
rep('      endTurn(actor);\n      tickSt(actor, "end");   // 状态默认在持有者回合结束时 −1', '      endTurn(actor);\n      if (rec.frz) pull(actor, 5000);   // 冻结解除后行动提前 50%\n      tickSt(actor, "end");   // 状态默认在持有者回合结束时 −1')
# 伤害显示用：当时敌人破了没有
rep('      rec.sts = a.st ? Object.keys(a.st).filter(k => a.st[k]) : [];\n      const o = a.sm ? byId[a.sm.owner] : null;', '      rec.sts = a.st ? Object.keys(a.st).filter(k => a.st[k]) : [];\n      rec.ebk = ebkNow();   // 伤害显示：这时主目标的韧性破了没有（没有韧性条 = undefined，看伤害设置）\n      const o = a.sm ? byId[a.sm.owner] : null;')
rep('db: dbSnap(u), edb: edbSnap(), pAt: pool })', 'db: dbSnap(u), edb: edbSnap(), pAt: pool, ebk: ebkNow() })')
rep('const r = { t, uid: o.id, en: en.id, k: d.k, mult: m, stat: d.stat, why, db: dbSnap(o), edb: edbSnap(), defIg: num(d.defIg), seq: seq++ };', 'const r = { t, uid: o.id, en: en.id, k: d.k, mult: m, stat: d.stat, why, db: dbSnap(o), edb: edbSnap(), defIg: num(d.defIg), seq: seq++, ebk: toughMax(en) > 0 ? !!en.broken : undefined };')

rep('pAt: pool, hpm: hpNow(ownerOf(u)) ?? undefined });', 'pAt: pool, hpm: hpNow(ownerOf(u)) ?? undefined, ebk: ebkNow() });')   # 追击标记
# ---------------- 伤害层 ----------------
rep('    const toughM = cfg.broken ? 1 : 0.9;   // 韧性条没破：伤害 ×0.9', '    const toughM = (rec && rec.ebk != null ? rec.ebk : cfg.broken) ? 1 : 0.9;   // 韧性条没破：伤害 ×0.9（模拟了韧性就按当时的状态，否则看伤害设置）')
rep('    const critM = e.dot ? 1 : 1 + ', '    const critM = e.dot || e.brk ? 1 : 1 + ')
rep('    const dmgM = (e.el || isLv || b2el) ? 1 : 1 + bonus / 100;', '    const dmgM = (e.el || isLv || b2el || e.brk) ? 1 : 1 + bonus / 100;   // 击破伤害不吃增伤')
rep('''    const e = { v: r.mult, adj: 0, rnd: 0, tg: 1, el: 0, stat: r.stat || "atk", key: "d", n: r.k, lv: 0, dot: true, defIg: r.defIg };
    return (r.__dmg = dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, hpm: r.hpm }));''',
    '''    const brk = r.stat === "brk";   // 击破伤害 / 击破的持续伤害：基础值 = 80 级击破基础值 × (1 + 击破特攻)，不暴击、不吃增伤
    const e = { v: r.mult, adj: 0, rnd: 0, tg: 1, el: 0, stat: brk ? "atk" : r.stat || "atk", key: brk ? "k" : "d", n: r.k, lv: 0, dot: true, brk, defIg: r.defIg };
    const d = dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, hpm: r.hpm, ebk: r.ebk }, brk ? LVBRK * (1 + (num(u.be) + dsum(r.db, "be", "k")) / 100) : undefined);
    if (brk && d) { d.noPanel = false; d.stat = "击破基础值（80 级）"; }
    return (r.__dmg = d);''')
rep('  // 一次持续伤害结算 / 引爆（R.dots 里的一条）', '  const LVBRK = 3767.5533;   // 80 级角色的击破基础值\n  // 一次持续伤害结算 / 引爆（R.dots 里的一条）')
rep('const SCK = { b: "b", b2: "b", s: "s", s2: "s", u: "u", u2: "u", f: "f", m: "m", e: "e", e2: "e", d: "d" };', 'const SCK = { b: "b", b2: "b", s: "s", s2: "s", u: "u", u2: "u", f: "f", m: "m", e: "e", e2: "e", d: "d", k: "k" };')
rep('["e", "欢愉技"], ["d", "持续伤害"]];', '["e", "欢愉技"], ["d", "持续伤害"], ["k", "击破伤害"]];')
rep('rx: "额外伤害标记", vuln:', 'rx: "额外伤害标记", be: "击破特攻", vuln:', 2)
rep('const DBM = [["atkP", "攻击力 %"],', 'const DBM = [["be", "击破特攻 %"], ["atkP", "攻击力 %"],')
rep('const DGC = { lv: 95, res: 20, vuln: 0, defR: 0, pen: 0, weak: false, broken: false, v: 1 };', 'const DGC = { lv: 95, res: 20, vuln: 0, defR: 0, pen: 0, weak: false, broken: false, noBrk: false, v: 1 };')

# ---------------- 界面 ----------------
rep('''<label for="dg-broken" title="韧性条没破时伤害 ×0.9；破了勾上"><input type="checkbox" id="dg-broken" data-dg="broken"> 已击破</label>''',
    '''<label for="dg-broken" title="韧性条没破时伤害 ×0.9；破了勾上。敌人有韧性条（套了模板）时按模拟里的实际状态，不看这里"><input type="checkbox" id="dg-broken" data-dg="broken"> 已击破</label>
                  <label for="dg-nobrk" title="勾上 = 不模拟韧性条：敌人不会被击破、不会因为击破推后行动，也没有击破伤害"><input type="checkbox" id="dg-nobrk" data-dg="noBrk"> 不模拟韧性和击破</label>''')
rep('''          ${u.stg ? `<span class="hint">来自 ${esc(u.stg)}</span>` : ""}<span class="hint">资料速度''',
    '''          <label for="tg-${u.id}" title="韧性（官方数值，30 = 游戏里的 10 点；同名敌人不同关卡可能不一样，可以自己改；清空 = 用模板的）">韧性 <input type="number" id="tg-${u.id}" min="0" step="30" value="${u.tough ?? ""}" placeholder="${(m => m && m.tn ? m.tn : 0)(MON.m.find(m => m.n === u.mon))}" data-u="${i}" data-f="tough" style="width:60px"></label>
          ${u.stg ? `<span class="hint">来自 ${esc(u.stg)}</span>` : ""}<span class="hint">资料速度''')
a = '''data-u="${i}" data-f="el" style="width:58px"></label>'''
rep(a, a + '''
          <label for="beo-${u.id}" title="击破特攻 %：照游戏面板填；击破伤害和击破的持续伤害会乘 (1 + 击破特攻)">击破特攻 % <input type="number" id="beo-${u.id}" min="0" step="0.1" value="${u.be ?? ""}" placeholder="0" data-u="${i}" data-f="be" style="width:58px"></label>''')
rep('const NUMF = new Set(["hp", "atk", "def",', 'const NUMF = new Set(["tough", "be", "hp", "atk", "def",')
rep('      if (f === "lv" && u.mon) { u.spd = u.base = monSpeed(u); structural = true; }', '      if (f === "tough" && el.value === "") delete u.tough;   // 清空 = 用模板的韧性\n      if (f === "be" && el.value === "") delete u.be;\n      if (f === "lv" && u.mon) { u.spd = u.base = monSpeed(u); structural = true; }')
i = s.index('id="changelog"'); j = s.index('<li>', i)
s = s[:j] + '''<li><b>2026-11-11（击破第 1 步：韧性条、弱点击破、击破伤害）</b>：tools/build_tgh.py、tools/brk1.py。① <b>敌人有韧性条了</b>：套了模板的敌人按官方数值带韧性（敌人卡上“韧性”可以改；471 个里 15 个没有数据，要自己填），自己加的空白敌人没有。② 我方攻击按官方削韧值削韧（每个技能主目标 / 全体 / 相邻各多少），<b>只对弱点属性有效</b>；削到 0 就是<b>击破</b>：行动轴上标“击破”，敌人行动延后 25%，并按击破者的属性附带效果——物理裂伤、火灼烧、雷触电、风风化（各 2 回合，敌人回合开始结算）、冰冻结（跳过 1 个回合，之后行动提前 50%）、量子纠缠（再延后 20% ×（1 + 击破特攻））、虚数禁锢（再延后 30% ×（1 + 击破特攻）、速度 −10%）；敌人下一个回合开始时韧性恢复。我方“弱点击破时”的效果现在会自动触发，不用再手动加事件。③ <b>击破伤害</b>进伤害合计：3767.55 × 属性系数 ×（0.5 + 韧性 ÷ 120）×（1 + 击破特攻），不暴击、不吃增伤；角色卡新增“击破特攻 %”。④ “韧性没破 ×0.9”改成按模拟里敌人当时破没破。⑤ 伤害设置里可以勾“不模拟韧性和击破”关掉这一整套。<b>对已有配置</b>：<b>套了模板的敌人会被击破、行动会被推后</b>，这类方案的行动顺序会变；没放敌人或只放空白敌人的方案不变。还没做：超击破、击破效率、无视弱点削韧、弱点植入（银狼、流萤等）、纠缠叠层。</li>
            ''' + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
