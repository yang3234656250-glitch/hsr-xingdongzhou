"""界面第 1 轮：行迹面板改成节点图、角色卡改成“属性列表 + 装备栏位”的排法（只改界面，不改数据和模拟）。
用法：python3 tools/ui1.py index.html
行迹节点图：核心技能在中轴（普攻 / 战技在上方两侧，终结技 → 天赋 → 秘技往下），三个额外能力在左、右、下，10 个属性强化按官方行迹树的连接关系挂在后面
（TRTREE：每个命途一套，来自 StarRailRes character_skill_trees 的 pre_points，tools/build_trtree.py 可以重新核对）。图标是页面自己画的文字圆点，没有用游戏素材。
"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------- 行迹面板：HTML ----------
rep('''      <section class="tr-sec">
        <h4>技能 <em>SKILLS</em></h4>
        <div class="tr-skills" id="tr-skills"></div>
      </section>''', '''      <section class="tr-sec">
        <h4>行迹 <em>TRACES</em></h4>
        <div class="tr-sum" id="tr-minor-sum"></div>
        <div class="tr-tree" id="tr-skills"></div>
        <p class="tr-tip" id="tr-tip"></p>
      </section>''')
i0 = s.index('      <details class="tr-sec tr-fold" id="tr-minor-box">'); i1 = s.index('</details>', i0) + len('</details>\n')
s = s[:i0] + s[i1:]

# ---------- 行迹面板：JS ----------
rep('''      $("tr-minor").innerHTML = ""; $("tr-minor-sum").textContent = "";''', '''      $("tr-minor-sum").innerHTML = "";''')
a0 = s.index('      $("tr-minor-sum").textContent = [...sum].map('); a1 = s.index('    }\n    m.hidden = false;', a0)
s = s[:a0] + '''      $("tr-minor-sum").innerHTML = sum.size ? `<span class="tr-sum-t">额外属性加成</span>` + [...sum].map(([k, v]) => `<span class="tr-chip"><b>${esc(k.replace(/%$/, ""))}</b>+${fmt(v, 1).replace(/\\.0$/, "")}${k.endsWith("%") ? "%" : ""}</span>`).join("") : "";
''' + s[a1:]
rep('''    trIdx = i;
    trSkill = null;
    renderTraceSkills();''', '''    trIdx = i;
    trSkill = null; trAb = -1;
    renderTraceSkills();''')
rep('  let trSkill = null;', '  let trSkill = null, trAb = -1;   // trAb = 点了第几个额外能力（只看这个能力的效果），-1 = 没点')
b0 = s.index('  function renderTraceSkills() {'); b1 = s.index('  function closeTrace() {', b0)
s = s[:b0] + r'''  // 行迹节点图。TRTREE：每个命途 10 个属性强化各接在谁后面（官方行迹树 pre_points；"-" = 接在核心技能上，A / B / C = 第 1 / 2 / 3 个额外能力，数字 = 第几个属性强化）
  const TRTREE = { "存护": "-A1-B4-C77", "巡猎": "-A1-B4-C77", "智识": "-A11B44CC-", "毁灭": "-A12B45C77", "同谐": "-A10B40C77", "丰饶": "-A12B45CC-", "虚无": "-A12B45CC0", "记忆": "-00AABBC78", "欢愉": "--AAB45C78" };
  const statGlyph = n => /^伤害强化/.test(n) ? "伤" : ({ "攻击": "攻", "防御": "防", "生命": "生", "速度": "速", "暴击率": "暴", "暴击伤害": "爆", "击破": "破", "效果命中": "命", "效果抵抗": "抗", "欢愉度": "欢" })[n.replace(/强化$/, "")] || n.slice(0, 1);
  const statLabel = n => n.replace(/^伤害强化•(.+)$/, "$1伤害").replace(/强化$/, "").replace(/^(攻击|防御)$/, "$1力").replace(/^生命$/, "生命值");
  function trLayout(u, T, d) {
    const hasMemo = u.effects.some(e => effSrc(e) === "memo" && inTr(e)) || (T && T.path === "记忆");
    const P = { basic: [27, 9], skill: [73, 9], ult: [50, 22], talent: [50, 36], tech: [50, 50] };
    const tops = [hasMemo && "memo", u.elation && "elation"].filter(Boolean);
    tops.forEach((k, j) => { P[k] = [tops.length > 1 ? 43 + j * 14 : 50, 6.5]; });
    const links = [["basic", "ult"], ["skill", "ult"], ["ult", "talent"], ["talent", "tech"]].concat(tops.map(k => [k, "ult"]));
    const ab = d ? d.m.slice(0, 3) : [], st = d ? d.s.filter(([n, v]) => v).slice(0, 10) : [];
    const AB = { A: [13.5, 23], B: [86.5, 23], C: [50, 64] };
    ["A", "B", "C"].forEach((k, j) => { if (ab[j]) { P[k] = AB[k]; links.push([k === "A" ? "basic" : k === "B" ? "skill" : "tech", k]); } });
    const code = (T && TRTREE[T.path]) || "-A1-B4-C77", kids = {};
    st.forEach((x, j) => { let par = code[j] || "-"; if (/[ABC]/.test(par) && !P[par]) par = "-"; (kids[par] = kids[par] || []).push(j); });
    const cl = v => Math.max(6.5, Math.min(93.5, v));
    const grow = (par, at) => {   // 一层一层往外放：at(层, 第几个, 这层几个, 上一级的位置) → 位置
      let layer = (kids[par] || []).map(j => [j, P[par]]), dep = 1;
      while (layer.length && dep < 6) { const nx = []; layer.forEach(([j, pp], q) => { P["s" + j] = at(dep, q, layer.length, pp); links.push([/[ABC]/.test(par) || dep > 1 ? (dep > 1 ? "s" + code[j] : par) : par, "s" + j]); for (const c of kids[String(j)] || []) nx.push([c, P["s" + j]]); }); layer = nx; dep++; }
    };
    if (P.A) grow("A", (dp, q, n) => [cl(AB.A[0] + (q - (n - 1) / 2) * 15), AB.A[1] + 14 * dp]);
    if (P.B) grow("B", (dp, q, n) => [cl(AB.B[0] + (q - (n - 1) / 2) * 15), AB.B[1] + 14 * dp]);
    if (P.C) grow("C", (dp, q, n, pp) => dp <= 2 ? [50 + (q - (n - 1) / 2) * 24, AB.C[1] + 11.5 * dp] : [pp[0] + (pp[0] >= 50 ? 15 : -15), pp[1]]);
    (kids["-"] || []).forEach((j, q) => {   // 直接接在核心技能上的：放在天赋 / 秘技两侧，再往下长
      const side = q % 2 ? 1 : -1, row = Math.floor(q / 2); P["r" + j] = [50 + side * 20.5, 50 + row * 12]; P["s" + j] = P["r" + j]; links.push(["talent", "s" + j]);
      let layer = (kids[String(j)] || []).map(c => [c, j]), dep = 1;
      while (layer.length && dep < 5) { const nx = []; layer.forEach(([c, pj], q2) => { P["s" + c] = [cl(P["r" + j][0] + (q2 - (layer.length - 1) / 2) * 14), P["r" + j][1] + 13 * dep]; links.push(["s" + pj, "s" + c]); for (const g of kids[String(c)] || []) nx.push([g, c]); }); layer = nx; dep++; }
    });
    return { P, links, ab, st, tops };
  }
  function renderTraceSkills() {
    const u = S.units[trIdx];
    if (!u) return;
    const T = tplOf(u), d = T ? TRACE[String(T.id)] : null, L = trLayout(u, T, d), P = L.P;
    const cnt = key => u.effects.filter(e => effSrc(e) === key && inTr(e)).length;
    const pos = (k, r) => `left:${P[k][0]}%;top:calc(${P[k][1]}% - ${r}px)`;
    const TL = Object.fromEntries(TR_TILES.map(([k, ic, lb]) => [k, [ic, lb]]));
    let h = `<svg class="tn-lines" aria-hidden="true">${L.links.filter(([a, b]) => P[a] && P[b]).map(([a, b]) => `<line x1="${P[a][0]}%" y1="${P[a][1]}%" x2="${P[b][0]}%" y2="${P[b][1]}%"/>`).join("")}</svg><span class="tn-halo" aria-hidden="true"></span>`;
    for (const key of ["basic", "skill", "ult", "talent", "tech"].concat(L.tops)) {
      const n = cnt(key), lv = T ? trLv(u, key) : 0, [ic, lb] = TL[key];
      h += `<button type="button" class="tn sk${key === "ult" ? " big" : ""}${trSkill === key ? " on" : ""}${n ? "" : " idle"}" style="${pos(key, key === "ult" ? 30 : 26)}" data-skill="${key}" title="${esc(lb)}：${n ? n + " 条需要模拟的效果，点开查看" : "没有需要模拟的效果"}"><i>${esc(ic)}</i><b>${esc(lb)}</b><span>${lv ? "Lv." + lv : ""}${lv && n ? " · " : ""}${n ? n + " 条" : ""}</span></button>`;
    }
    L.ab.forEach(([nm, desc], j) => { const k = "ABC"[j]; if (!P[k]) return; const n = u.effects.filter(e => effSrc(e) === "trace" && inTr(e) && String(e.note || "").includes(nm)).length;
      h += `<button type="button" class="tn ab${trSkill === "trace" && trAb === j ? " on" : ""}${n ? "" : " idle"}" style="${pos(k, 22)}" data-skill="trace" data-ab="${j}" title="${esc(nm)}：${esc(desc)}"><i>◆</i><b>${esc(nm)}</b><span>${n ? n + " 条" : ""}</span></button>`; });
    L.st.forEach(([nm, v], j) => { if (!P["s" + j]) return; h += `<span class="tn st" style="${pos("s" + j, 15)}" title="${esc(nm)} ${esc(v)}（已经算在游戏面板里）"><i>${esc(statGlyph(nm))}</i><b>${esc(statLabel(nm))}</b><span>${esc(v)}</span></span>`; });
    if (!d && T == null) h += `<p class="tr-empty tn-none">这张卡没套用角色模板，只有技能节点。</p>`;
    $("tr-skills").innerHTML = h;
    const a = trSkill === "trace" && trAb >= 0 ? L.ab[trAb] : null;
    $("tr-tip").innerHTML = a ? `<b>◆ ${esc(a[0])}</b>${esc(a[1])}` : `点技能或额外能力的圆点，下面只看它的效果；再点一次回到全部。小圆点是属性强化，已经算在游戏面板里，卡片上的速度、生命、攻击照面板填就行，不要再加一遍。`;
  }
''' + s[b1:]
rep('''    const list = u.effects.map((e, j) => [e, j]).filter(([e]) => effSrc(e) === trSkill && inTr(e));
    if (!list.length) {
      box.innerHTML = `<p class="tr-empty">${SRCL[trSkill]}没有需要模拟的效果。</p>`;''',
    '''    const abN = trSkill === "trace" && trAb >= 0 ? (((tplOf(u) && TRACE[String(tplOf(u).id)]) || { m: [] }).m[trAb] || [])[0] : null;   // 点了某个额外能力：只看说明里带这个名字的
    const list = u.effects.map((e, j) => [e, j]).filter(([e]) => effSrc(e) === trSkill && inTr(e) && (!abN || String(e.note || "").includes(abN)));
    if (!list.length) {
      box.innerHTML = `<p class="tr-empty">${abN ? "「" + esc(abN) + "」" : SRCL[trSkill]}没有需要模拟的效果${abN ? "（只影响页面不算的内容，或已经并进别的效果）" : ""}。</p><div class="eg-head tr-one"><button type="button" class="ghost" data-skill="__all" title="回到全部技能的列表">显示全部 ›</button></div>`;''')
rep('''    const k = b.dataset.skill;
    trSkill = (k === "__all" || trSkill === k) ? null : k;''', '''    const k = b.dataset.skill, ab = b.dataset.ab != null ? +b.dataset.ab : -1;
    trSkill = (k === "__all" || (trSkill === k && trAb === ab)) ? null : k; trAb = trSkill ? ab : -1;''')

# ---------- 角色卡：标签行 + 分区标题 + 装备栏位 ----------
rep('''            <div class="spd-big"><input type="number" id="sn-${u.id}" min="1" step="0.1" value="${u.spd}" data-u="${i}" data-f="spd" aria-label="速度"><i>SPD</i></div>
          </div>''', '''            <div class="uh-bot">
              <div class="uh-tags">${(T => T && u.kind === "ally" && !u.sm ? [T.path, ELEMN[T.elem], num(u.eid) ? "星魂 " + num(u.eid) : "", T.sp ? "能量 " + T.sp : ""].filter(Boolean).map(t => `<span>${esc(t)}</span>`).join("") : u.sm ? `<span>召唤物</span>` : u.kind === "enemy" ? `<span>敌方</span>` : "")(tplOf(u))}</div>
              <div class="spd-big"><input type="number" id="sn-${u.id}" min="1" step="0.1" value="${u.spd}" data-u="${i}" data-f="spd" aria-label="速度"><i>SPD</i></div>
            </div>
          </div>''')
rep('''        ${u.kind === "ally" && !u.sm ? `<div class="row stat-row">${STATS.map(''', '''        ${u.kind === "ally" && !u.sm ? `<div class="sec-t">属性 <em>照游戏面板填</em></div><div class="row stat-row">${STATS.map(''')
rep('''        <div class="row">
          <label for="b-${u.id}">基础速度''', '''        <div class="sec-t">基础 <em>模板 / 开局</em></div>
        <div class="row base-row">
          <label for="b-${u.id}">基础速度''')
rep('''        ${u.kind !== "ally" ? "" : `<div class="row">
          <div class="pickwrap">光锥''', '''        ${u.kind !== "ally" ? "" : `<div class="sec-t">装备 <em>光锥 / 遗器</em></div><div class="row eq-row">
          <div class="pickwrap">光锥''')
rep('''        <div class="row">
          <div class="pickwrap">遗器''', '''        <div class="row eq-row">
          <div class="pickwrap">遗器''')
rep('  const ELEMN = { Physical:', '  var ELEMN = { Physical:') if False else None
# ELEMN 在 renderEditor 之后才定义（const），渲染时已经初始化；保险起见确认它在模块顶层
assert s.index('  const ELEMN = {') > 0

# ---------- CSS ----------
css = r'''
/* ===== 界面第 1 轮：行迹节点图 ===== */
.tr-sheet{ grid-template-columns:132px minmax(0,1fr); width:min(1000px,100%); }
.tr-sum{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:-2px 0 8px; }
.tr-sum-t{ font-size:11px; letter-spacing:.14em; color:#9fd7e4; margin-right:2px; }
.tr-chip{ font-family:var(--f-num); font-size:12px; color:var(--gold); padding:1px 9px; border-radius:999px; border:1px solid rgba(232,200,138,.32); background:rgba(232,200,138,.07); white-space:nowrap; }
.tr-chip b{ font-family:var(--f-body); font-weight:500; color:#d7e6ee; margin-right:4px; }
.tr-tree{ position:relative; height:620px; border:1px solid rgba(122,206,224,.16); border-radius:12px; overflow:hidden;
  background:radial-gradient(60% 46% at 50% 38%, rgba(64,110,170,.20), transparent 70%), linear-gradient(180deg, rgba(10,16,30,.72), rgba(5,9,18,.86)); }
.tn-lines{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }
.tn-lines line{ stroke:rgba(150,214,232,.34); stroke-width:1.4; }
.tn-halo{ position:absolute; left:50%; top:36%; width:min(46%,300px); aspect-ratio:1; transform:translate(-50%,-50%); border-radius:50%; pointer-events:none;
  border:1px solid rgba(150,214,232,.10); box-shadow:0 0 0 22px rgba(150,214,232,.025), inset 0 0 60px rgba(111,227,236,.05); }
.tn{ position:absolute; width:92px; margin-left:-46px; padding:0; border:none; background:none; box-shadow:none; border-radius:0; clip-path:none;
  display:flex; flex-direction:column; align-items:center; gap:3px; color:inherit; font:inherit; letter-spacing:0; text-align:center; }
button.tn{ cursor:pointer; }
button.tn:hover{ background:none; box-shadow:none; }
.tn i{ font-style:normal; display:flex; align-items:center; justify-content:center; border-radius:50%; flex:none; transition:box-shadow .15s, border-color .15s, transform .15s; }
.tn b{ font-size:12px; font-weight:600; color:#eef6fa; line-height:1.2; text-shadow:0 1px 3px #000; white-space:nowrap; }
.tn span{ font-family:var(--f-num); font-size:10px; color:var(--muted); line-height:1.1; white-space:nowrap; min-height:11px; }
.tn.sk i{ width:52px; height:52px; font:600 21px/1 var(--f-display); color:#fff; border:2px solid var(--gold);
  background:radial-gradient(circle at 32% 26%, rgba(232,200,138,.34), rgba(14,20,36,.96) 70%); box-shadow:0 0 0 4px rgba(8,13,26,.9), 0 0 0 5px rgba(232,200,138,.22); }
.tn.sk.big i{ width:60px; height:60px; font-size:24px; }
.tn.ab i{ width:44px; height:44px; font-size:15px; color:#bff3e2; border:2px solid #5fd3b0;
  background:radial-gradient(circle at 32% 26%, rgba(95,211,176,.30), rgba(12,20,34,.96) 70%); box-shadow:0 0 0 4px rgba(8,13,26,.9), 0 0 0 5px rgba(95,211,176,.2); }
.tn.st{ width:64px; margin-left:-32px; gap:2px; }
.tn.st i{ width:30px; height:30px; font-size:12px; color:#e6eef4; border:1.5px solid rgba(230,240,246,.8); background:#0c1424; box-shadow:0 0 0 3px rgba(8,13,26,.9); }
.tn.st b{ font-size:10.5px; font-weight:500; color:#cfdde6; }
.tn.st span{ font-size:10.5px; color:var(--gold); }
.tn.idle i{ border-color:rgba(160,180,200,.42); background:#0b1220; color:#8fa2b4; box-shadow:0 0 0 4px rgba(8,13,26,.9); }
.tn.idle b{ color:#9fb0c0; }
button.tn:hover i{ transform:scale(1.06); box-shadow:0 0 0 4px rgba(8,13,26,.9), 0 0 18px rgba(111,227,236,.5); }
.tn.on i{ border-color:var(--accent); color:#fff; box-shadow:0 0 0 4px rgba(8,13,26,.9), 0 0 0 6px rgba(111,227,236,.55), 0 0 22px rgba(111,227,236,.55); }
.tn.on b{ color:var(--accent); }
.tn-none{ position:absolute; left:12px; right:12px; bottom:10px; margin:0; }
.tr-tip{ margin:10px 2px 0; font-size:12px; line-height:1.6; color:#a9bccd; }
.tr-tip b{ color:#bff3e2; margin-right:8px; font-weight:600; }
@media (max-width:760px){
  .tr-sheet{ grid-template-columns:1fr; }
  .tr-tree{ height:590px; margin:0 -6px; }
  .tn{ width:76px; margin-left:-38px; }
  .tn.sk i{ width:46px; height:46px; font-size:19px; } .tn.sk.big i{ width:54px; height:54px; font-size:22px; }
  .tn.ab i{ width:40px; height:40px; }
  .tn b{ font-size:11px; } .tn.st{ width:54px; margin-left:-27px; } .tn.st i{ width:28px; height:28px; } .tn.st b, .tn.st span{ font-size:10px; }
}
/* ===== 界面第 1 轮：角色卡 = 立绘 + 属性列表 + 装备栏位 ===== */
.unit-head{ padding:12px 12px 10px; gap:14px; min-height:132px; }
.unit-head .portrait{ width:96px; height:120px; border-radius:8px; object-position:50% 6%; }
.unit-head .portrait.ph{ font-size:40px; }
.unit-head .swatch{ left:92px; top:114px; }
.uh-bot{ display:flex; align-items:flex-end; justify-content:space-between; gap:8px; }
.uh-tags{ display:flex; flex-wrap:wrap; gap:5px; min-width:0; }
.uh-tags span{ font-size:11px; padding:1px 8px; border-radius:999px; color:#e9f3f8; background:rgba(4,9,18,.5); border:1px solid rgba(255,255,255,.26); white-space:nowrap; }
.sec-t{ display:flex; align-items:center; gap:8px; margin:6px 0 -2px; font-size:11px; font-weight:600; letter-spacing:.2em; color:#9fd7e4; }
.sec-t em{ font-style:normal; font-weight:400; font-size:10px; letter-spacing:.08em; color:rgba(159,215,228,.5); }
.sec-t::after{ content:""; flex:1; height:1px; background:linear-gradient(90deg, rgba(122,206,224,.34), transparent); }
.unit .stat-row, .unit .dmg-row{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:0 16px; align-items:stretch; }
.unit .stat-row > label, .unit .dmg-row > label{ display:flex; justify-content:space-between; align-items:center; gap:6px; padding:4px 2px; font-size:13px; color:#d5e2ea; border-bottom:1px solid rgba(190,225,240,.10); }
.unit .stat-row > label input[type=number], .unit .dmg-row > label input[type=number]{ width:86px !important; text-align:right; border:none; background:none; padding:1px 2px; font-size:15px; font-weight:600; color:#fff; border-radius:4px; }
.unit .stat-row > label input[type=number]:focus, .unit .dmg-row > label input[type=number]:focus{ background:rgba(111,227,236,.10); box-shadow:none; }
.unit .stat-row > label input::placeholder, .unit .dmg-row > label input::placeholder{ color:rgba(160,180,200,.55); font-weight:500; }
.unit .dmg-row{ margin-top:-8px; }
.unit .dmg-row > .lab{ display:none; }
.unit .dmg-row > details{ grid-column:1 / -1; padding:5px 2px 0; }
.unit .base-row label{ font-size:11.5px; }
.unit .base-row input[type=number]{ font-size:12px; }
.unit .eq-row{ display:grid; grid-template-columns:repeat(auto-fit,minmax(138px,1fr)); gap:8px; align-items:stretch; }
.unit .eq-row + .eq-row{ margin-top:-2px; }
.unit .eq-row .pickwrap{ flex-direction:column; align-items:stretch; gap:3px; font-size:10.5px; letter-spacing:.12em; color:var(--muted); min-width:0; }
.unit .eq-row .pickbtn{ max-width:none; width:100%; min-height:46px; padding:5px 8px; border-radius:8px; border:1px solid var(--line); letter-spacing:0; font-size:12.5px;
  background:linear-gradient(120deg, rgba(232,200,138,.10), rgba(10,16,30,.6) 46%); justify-content:flex-start; }
.unit .eq-row .pickbtn:hover{ border-color:var(--accent); }
.unit .eq-row .pickbtn span{ white-space:normal; line-height:1.25; text-align:left; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.unit .eq-row .eqimg{ height:36px; } .unit .eq-row .eqimg.rel{ width:36px; }
.unit .eq-row > label{ align-self:end; padding-bottom:4px; }
@media (max-width:420px){ .unit-head .portrait{ width:84px; height:108px; } .unit-head .swatch{ left:80px; top:102px; } }
'''
k = s.index('</style>'); s = s[:k] + css + s[k:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
