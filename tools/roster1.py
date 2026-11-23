# 「角色」页（2026-11-23，用户：“每个角色保存一个面板，单独做一页角色”，选了“全部一起存”）：
# 共享面板库 S.panels 从只存面板数值，扩成每个角色存 面板 + 速度 + 星魂 / 光锥 / 遗器，所有方案共用；
# 卡片上分三项“本方案单独”：面板（原来的 ownPanel）、速度（ownSpd）、装备（ownEq）。
# 老方案保护：配置没有 pv（这版以前存的），第一次和角色库对齐时，速度 / 装备和角色库不一样的卡自动勾“单独”，结果不变。
# 用法：python3 tools/roster1.py index.html
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s
s = s.replace("\r\n", "\n")


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:90])
    s = s.replace(old, new)


# ---------- 面板库：三组 ----------
old_sync = s[s.index("  // 共享面板（2026-10-30 用户要求）"):s.index("  // 角色立绘（StarRailRes 的 character_preview")]
new_sync = """  // 共享面板（2026-10-30 用户要求）：同一个角色（按模板）在所有方案里共用一份，存在 S.panels[模板id]。
  // 2026-11-23 起（「角色」页）分三组：面板数值（PANELF）、速度（spd）、装备（星魂 / 光锥 / 遗器，EQF）；
  // 卡片勾“本方案单独 面板 / 速度 / 装备”（u.ownPanel / ownSpd / ownEq）的那一组不参与。u.pk = 这张卡上次对上的面板键：
  // 键变了（刚载入方案 / 刚换模板）就从角色库拉，没变就把卡片上改过的写回角色库。p.g = {s, e}：这个角色的速度 / 装备组已经建过。
  // 老方案（配置没有 pv，2026-11-23 以前存的）第一次对齐时：速度 / 装备和角色库不一样的卡自动勾“单独”，结果不变。
  const PANELF = ["hp", "atk", "def", "hb", "cr", "cd", "dmg", "el", "er", "mult"];
  const SPDF = ["spd"], EQF = ["eid", "ex", "lc", "lcR", "rA", "rB", "r4", "rP"];
  const PGRP = [["p", PANELF, "ownPanel"], ["s", SPDF, "ownSpd"], ["e", EQF, "ownEq"]];
  const PDEF = { eid: 0, lcR: 1, r4: false, ex: false };   // 等于默认值的不存
  const panelKey = u => { const t = u && u.kind === "ally" && !u.sm ? tidOf(u) : ""; return t ? "t" + t : ""; };
  const pPick = (u, F) => { const o = {}; for (const f of F) { const v = u ? u[f] : undefined; if (v !== undefined && v !== null && v !== "" && v !== PDEF[f]) o[f] = JSON.parse(JSON.stringify(v)); } return o; };
  const pHas = (p, g) => g === "p" ? !!p : !!(p && p.g && p.g[g]);
  function panelSync(s) {
    s = s || S; if (!s.panels || typeof s.panels !== "object") s.panels = {};
    const old = !(num(s.pv) >= 2);
    const same = (u, p, F) => JSON.stringify(pPick(u, F)) === JSON.stringify(pPick(p, F));
    const put = (k, g, F, u) => { const p = Object.assign({}, s.panels[k] || {}); for (const f of F) delete p[f]; Object.assign(p, pPick(u, F)); if (g !== "p") p.g = Object.assign({}, p.g || {}, { [g]: 1 }); s.panels[k] = p; };   // 换成新对象（方案对比的临时配置和这里共用同一批对象）
    const L = s.units.filter(u => { const k = panelKey(u); if (!k) { delete u.pk; return false; } return true; });
    for (const [g, F, own] of PGRP) {
      // ① 已经对上的卡：和角色库不一样 = 刚被改过，写回角色库
      for (const u of L) { const k = panelKey(u); if (!u[own] && u.pk === k && pHas(s.panels[k], g) && !same(u, s.panels[k], F)) put(k, g, F, u); }
      // ② 角色库里还没有这一组：用卡上的建一份
      for (const u of L) { const k = panelKey(u); if (!u[own] && !pHas(s.panels[k], g)) put(k, g, F, u); }
      // 老方案：速度 / 装备和角色库不一样的卡，自动改成本方案单独，不动它的数值
      if (old && g !== "p") for (const u of L) { const k = panelKey(u); if (!u[own] && u.pk !== k && !same(u, s.panels[k], F)) u[own] = true; }
    }
    // ③ 所有卡跟角色库对齐（同一方案里有两张同一角色的卡时也一样）
    let pulled = false;
    for (const u of L) {
      const k = panelKey(u), p = s.panels[k]; let eq = false;
      for (const [g, F, own] of PGRP) {
        if (u[own] || !pHas(p, g) || same(u, p, F)) continue;
        for (const f of F) { if (p[f] !== undefined) u[f] = JSON.parse(JSON.stringify(p[f])); else delete u[f]; }
        pulled = true; if (g === "e") eq = true;
      }
      if (eq) applyEquip(u);
      u.pk = k;
    }
    s.pv = 2;
    return pulled;
  }
"""
s = s.replace(old_sync, new_sync)

# 卡片：本方案单独 面板 / 速度 / 装备
old_row = s[s.index('        ${panelKey(u) ? `<div class="row"><label for="op-${u.id}"'):]
old_row = old_row[:old_row.index("\n") + 1]
new_row = """        ${panelKey(u) ? `<div class="row"><span title="不勾：这些在所有方案里共用（也就是「角色」页里这个角色的配置），改一处所有方案都跟着变；勾上：这张卡只在这个方案里用自己的（取消勾选会换回角色页里的）">本方案单独：</span><label for="op-${u.id}"><input type="checkbox" id="op-${u.id}" ${u.ownPanel ? "checked" : ""} data-u="${i}" data-f="ownPanel"> 面板</label><label for="os-${u.id}"><input type="checkbox" id="os-${u.id}" ${u.ownSpd ? "checked" : ""} data-u="${i}" data-f="ownSpd"> 速度</label><label for="oe-${u.id}"><input type="checkbox" id="oe-${u.id}" ${u.ownEq ? "checked" : ""} data-u="${i}" data-f="ownEq"> 星魂 / 光锥 / 遗器</label><span class="hint">${u.ownPanel && u.ownSpd && u.ownEq ? "都只在这个方案里用" : "没勾的跟「角色」页共用"}</span></div>` : ""}
"""
s = s.replace(old_row, new_row)
rep("""      if (f === "ownPanel") { if (!val) delete u.ownPanel; delete u.pk; structural = true; }   // 取消单独面板 = 换回共用的面板""",
    """      if (f === "ownPanel" || f === "ownSpd" || f === "ownEq") { if (!val) delete u[f]; delete u.pk; structural = true; }   // 取消单独 = 换回「角色」页里的""")

# ---------- 页面切换 + 角色页 ----------
rep("""  <nav class="mtabs" id="mtabs" role="tablist" aria-label="切换显示内容">""",
    """  <nav class="pgtabs" id="pgtabs" aria-label="切换页面"><button type="button" data-pg="axis">行动轴</button><button type="button" data-pg="ros">角色</button></nav>
  <section class="section roster" id="roster" aria-label="角色"></section>

  <nav class="mtabs" id="mtabs" role="tablist" aria-label="切换显示内容">""")

css = """
/* 「角色」页（2026-11-23） */
.pgtabs{ display:flex; gap:6px; margin:10px 0 4px; }
.pgtabs button{ padding:6px 18px; font-weight:600; }
.pgtabs button[aria-selected="true"]{ background:var(--accent); border-color:var(--accent); color:#000; }
.roster{ display:none; }
body[data-pg="ros"] .roster{ display:block; }
body[data-pg="ros"] .main, body[data-pg="ros"] .mtabs{ display:none !important; }
.ros-head{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:10px; }
.ros-grid{ display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:12px; }
.ros-card{ border:1px solid var(--line); border-radius:12px; padding:10px; display:flex; flex-direction:column; gap:7px; background:rgba(255,255,255,.02); min-width:0; }
.ros-card.inteam{ border-color:var(--accent); }
.ros-top{ display:flex; gap:10px; align-items:center; }
.ros-top img.rimg{ width:56px; height:56px; object-fit:cover; object-position:top; border-radius:10px; flex:none; }
.ros-top .rn{ font-weight:700; font-size:15px; }
.ros-card .row{ display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; }
.ros-card input[type=number]{ width:74px; }
.ros-card .pickbtn{ max-width:180px; }
.ros-stats{ display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:6px; }
.ros-stats label{ display:flex; flex-direction:column; font-size:12px; color:var(--muted); gap:2px; }
.ros-stats input{ width:100% !important; }
@media (max-width: 520px){ .ros-grid{ grid-template-columns:1fr; } }
"""
i = s.rindex("</style>")
s = s[:i] + css + s[i:]

js = r"""
  // ---------- 「角色」页（2026-11-23）：每个角色一份配置（面板 + 速度 + 星魂 / 光锥 / 遗器），所有方案共用 ----------
  const PG_KEY = STORE + "-pg";
  let pgNow = (() => { try { return localStorage.getItem(PG_KEY) === "ros" ? "ros" : "axis"; } catch (e) { return "axis"; } })();
  const setPg = k => {
    pgNow = k === "ros" ? "ros" : "axis"; document.body.dataset.pg = pgNow;
    document.querySelectorAll("#pgtabs [data-pg]").forEach(b => b.setAttribute("aria-selected", String(b.dataset.pg === pgNow)));
    try { localStorage.setItem(PG_KEY, pgNow); } catch (e) {}
    if (pgNow === "ros") renderRoster(); else { paint.tl = paint.tab = true; paint(); }
  };
  const rosTpl = k => DB.chars.find(c => "t" + c.id === k);
  const rosBase = (T, lcId, f) => { const lc = DB.lcs.find(x => x.id === lcId); return Math.floor(num(T[f]) + (lc && lc[f] != null ? lc[f] : 0) + 1e-9); };
  function renderRoster() {
    const box = $("roster"); if (!box || pgNow !== "ros") return;
    if (!S.panels || typeof S.panels !== "object") S.panels = {};
    const inTeam = k => S.units.filter(u => panelKey(u) === k);
    const keys = Object.keys(S.panels).filter(k => rosTpl(k));
    keys.sort((a, b) => (inTeam(b).length ? 1 : 0) - (inTeam(a).length ? 1 : 0) || rosTpl(a).name.localeCompare(rosTpl(b).name, "zh"));
    const free = DB.chars.filter(c => !S.panels["t" + c.id]).sort((a, b) => a.path.localeCompare(b.path, "zh") || a.name.localeCompare(b.name, "zh"));
    const nf = (k, f, v, ph, lab, step) => `<label>${lab}<input type="number" step="${step || "any"}" data-rs="${esc(k)}" data-rf="${f}" value="${v ?? ""}" placeholder="${ph ?? ""}" aria-label="${lab}"></label>`;
    let h = `<div class="ros-head"><h2 style="margin:0"><b>角色</b>Characters</h2>
      <label for="ros-add">添加角色 <select id="ros-add"><option value="">（选一个）</option>${free.map(c => `<option value="${c.id}">${esc(c.path)} · ${esc(c.name)}</option>`).join("")}</select></label></div>
      <p class="hint">每个角色存一份：面板（生命 / 攻击 / 防御 / 治疗加成 / 暴击 / 爆伤 / 增伤 / 欢愉度 / 充能效率）、速度、星魂、光锥、遗器，所有方案共用。在这里改，或者在行动轴页的角色卡上改，两边是同一份；方案里套用这个角色的模板就会带上这里的配置。某个方案想用别的速度 / 装备，在那张卡上勾“本方案单独”。面板留空 = 按基础值（角色 80 级 + 光锥）。</p>`;
    if (!keys.length) h += `<p class="hint">还没有角色。上面选一个添加，或者在行动轴页给角色卡套用模板。</p>`;
    h += `<div class="ros-grid">`;
    for (const k of keys) {
      const T = rosTpl(k), p = S.panels[k], tm = inTeam(k), img = IMG.ch && IMG.ch[T.id];
      const own = tm.filter(u => u.ownPanel || u.ownSpd || u.ownEq).length;
      h += `<div class="ros-card${tm.length ? " inteam" : ""}">
        <div class="ros-top">${img ? `<img class="rimg" src="${img}" alt="">` : ""}<div style="min-width:0;flex:1"><div class="rn">${esc(T.name)}</div><div class="hint">${esc(T.path)} · 基础速度 ${T.spd}${tm.length ? `　<b style="color:var(--accent)">在当前方案里</b>${own ? `（${own} 张卡有“本方案单独”）` : ""}` : ""}</div></div>
          ${tm.length ? "" : `<button type="button" data-ract="join" data-rk="${esc(k)}">加入当前方案</button>`}</div>
        <div class="row">${nf(k, "spd", p.spd, T.spd, "速度 ", "0.1")}<label>星魂 <select data-rs="${esc(k)}" data-rf="eid">${[0, 1, 2, 3, 4, 5, 6].map(n => `<option value="${n}"${num(p.eid) === n ? " selected" : ""}>${n}</option>`).join("")}</select></label>${T.exe ? `<label title="奇缘星魂「${esc(T.exe.n)}」"><input type="checkbox" data-rs="${esc(k)}" data-rf="ex"${p.ex ? " checked" : ""}> 奇缘星魂</label>` : ""}</div>
        <div class="row"><div class="pickwrap">光锥 ${pickBtn("lc", -1, p.lc)}<select hidden data-rs="${esc(k)}" data-rf="lc" aria-label="光锥">${lcOptions(p.lc)}</select></div><label>叠影 <select data-rs="${esc(k)}" data-rf="lcR">${[1, 2, 3, 4, 5].map(n => `<option value="${n}"${num(p.lcR, 1) === n ? " selected" : ""}>${n}</option>`).join("")}</select></label></div>
        <div class="row"><div class="pickwrap">遗器 ${pickBtn("rA", -1, p.rA)}<select hidden data-rs="${esc(k)}" data-rf="rA" aria-label="遗器套装">${relicOptions(p.rA, false)}</select></div><label><input type="checkbox" data-rs="${esc(k)}" data-rf="r4"${p.r4 ? " checked" : ""}>4件套</label>
          ${p.r4 ? "" : `<div class="pickwrap">+2件 ${pickBtn("rB", -1, p.rB)}<select hidden data-rs="${esc(k)}" data-rf="rB" aria-label="另一套2件">${relicOptions(p.rB, false)}</select></div>`}
          <div class="pickwrap">位面 ${pickBtn("rP", -1, p.rP)}<select hidden data-rs="${esc(k)}" data-rf="rP" aria-label="位面饰品">${relicOptions(p.rP, true)}</select></div></div>
        <div class="ros-stats">${nf(k, "hp", p.hp, T.hp != null ? rosBase(T, p.lc, "hp") : "", "生命")}${nf(k, "atk", p.atk, T.atk != null ? rosBase(T, p.lc, "atk") : "", "攻击")}${nf(k, "def", p.def, T.def != null ? rosBase(T, p.lc, "def") : "", "防御")}
          ${nf(k, "cr", p.cr, 5, "暴击率 %")}${nf(k, "cd", p.cd, 50, "暴击伤害 %")}${nf(k, "dmg", p.dmg, 0, "增伤 %")}
          ${nf(k, "er", p.er, 100, "充能效率 %")}${nf(k, "hb", p.hb, 0, "治疗加成 %")}${T.path === "欢愉" ? nf(k, "el", p.el, 0, "欢愉度 %") : ""}</div>
        <div class="row" style="justify-content:flex-end"><button type="button" class="ghost" data-ract="del" data-rk="${esc(k)}">从角色页删除</button></div>
      </div>`;
    }
    $("roster").innerHTML = h + `</div>`;
  }
  // 改角色页 = 改角色库；跟着角色库的卡（没勾“本方案单独”的那一组）马上换成新的
  const rosTouch = k => { for (const u of S.units) if (panelKey(u) === k) delete u.pk; };
  $("roster").addEventListener("change", e => {
    const t = e.target;
    if (t.id === "ros-add") {
      const id = +t.value; if (!id) return; const T = DB.chars.find(c => c.id === id); if (!T) return;
      S.panels = Object.assign({}, S.panels, { ["t" + id]: { spd: T.spd, g: { s: 1, e: 1 } } });
      renderEditor(); update(); renderRoster(); return;
    }
    if (t.dataset.rs === undefined) return;
    const k = t.dataset.rs, f = t.dataset.rf, p = Object.assign({}, S.panels[k] || {});
    const v = t.type === "checkbox" ? t.checked : t.value === "" ? null : num(t.value);
    if (v === null || v === PDEF[f]) delete p[f]; else p[f] = v;
    if (f === "r4" && v) delete p.rB;
    const g = SPDF.includes(f) ? "s" : EQF.includes(f) ? "e" : "p";
    if (g !== "p") p.g = Object.assign({}, p.g || {}, { [g]: 1 });
    if (g === "s" && p.spd == null) { const T = rosTpl(k); if (T) p.spd = T.spd; }
    S.panels = Object.assign({}, S.panels, { [k]: p });
    rosTouch(k); renderEditor(); update(); renderRoster();
  });
  $("roster").addEventListener("click", e => {
    const b = e.target.closest("[data-ract]"); if (!b) return;
    const k = b.dataset.rk, T = rosTpl(k); if (!T) return;
    if (b.dataset.ract === "join") {
      addUnit("ally"); const u = S.units[S.units.length - 1]; applyDb(u, T.id); delete u.pk;
      renderEditor(); update(); renderRoster(); return;
    }
    if (b.dataset.ract === "del") {
      if (!b.dataset.sure) { b.dataset.sure = "1"; b.textContent = "再点一次确认删除（当前方案里的卡会保留现在的数值）"; return; }
      const P = Object.assign({}, S.panels); delete P[k]; S.panels = P;
      for (const u of S.units) if (panelKey(u) === k) delete u.pk;   // 卡片保留现在的数值，下次同步时用卡上的重新建
      update(); renderRoster();
    }
  });
  $("pgtabs").addEventListener("click", e => { const b = e.target.closest("[data-pg]"); if (b) { setPg(b.dataset.pg); window.scrollTo(0, 0); } });
"""
anchor = "  const addUnit = kind => {"
i = s.index(anchor)
# addUnit 之后插（用到它）
j = s.index('  $("add-ally").onclick = () => addUnit("ally");', i)
j = s.index("\n", j) + 1
s = s[:j] + js + s[j:]

# update() 末尾刷新角色页；页面打开时恢复上次的页
rep("""    renderTurnActs(R); renderKActs(R); renderEActs(R);
  }""", """    renderTurnActs(R); renderKActs(R); renderEActs(R);
    if (pgNow === "ros" && !$("roster").contains(document.activeElement)) renderRoster();   // 「角色」页（撤销、云端同步后跟着刷新；正在里面输入时不打断）
  }""")
rep("""  { const before = JSON.stringify(S); panelSync(S); if (before === lastSaved) lastSaved = JSON.stringify(S); }""",
    """  { const before = JSON.stringify(S); panelSync(S); if (before === lastSaved) lastSaved = JSON.stringify(S); }
  setPg(pgNow);""")

# 使用说明 + 更新日志
rep("""            <li><b>同一行动值的结算顺序</b>""", """            <li><b>「角色」页</b>：页面最上面切到「角色」，每个角色存一份面板、速度、星魂、光锥、遗器，所有方案共用；方案里套用这个角色的模板就带上这份配置。角色卡上“本方案单独”勾上哪一项（面板 / 速度 / 星魂·光锥·遗器），那一项就只在这个方案里用自己的。以前存的方案第一次打开时，速度 / 装备和角色页不一样的卡会自动勾“单独”，原来的结果不变。</li>
            <li><b>同一行动值的结算顺序</b>""")
i = s.find('<details id="changelog">'); j = s.find("<li", i)
entry = """<li><b>2026-11-23（「角色」页，没改 tv）</b>。用户：“每个角色保存一个面板，单独做一页角色”（参考绯绯狐工具箱），选了面板、速度、星魂、光锥、遗器全部一起存。① 页面最上面新加「行动轴 / 角色」切换。「角色」页列出角色库里的每个角色（当前方案里有的排前面、加框），可以改速度、星魂、奇缘星魂、光锥和叠影、遗器、生命 / 攻击 / 防御 / 暴击 / 爆伤 / 增伤 / 充能效率 / 治疗加成 / 欢愉度（面板留空 = 按基础值，灰字就是基础值），“添加角色”“加入当前方案”“从角色页删除”。② 原来的共享面板（只有面板数值）扩成三组：面板、速度、星魂 / 光锥 / 遗器；角色卡上“本方案单独”分三个勾。在卡片上改也会写回角色页，所有没勾“单独”的方案一起变（配速助手“设成”也一样）。③ 老方案保护：这版以前存的配置（没有 pv）第一次和角色库对齐时，速度或装备和角色库不一样的卡自动勾上对应的“单独”，数值不动；当前配置是第一份，用它建角色库。对已有配置：当前方案的行动顺序完全不变；载入其他老方案也不变（不一样的都会自动勾“单独”），想让它们跟角色页走就把勾去掉。</li>
"""
s = s[:j] + entry + "            " + s[j:]

if crlf:
    s = s.replace("\n", "\r\n")
open(p, "w", encoding="utf-8", newline="").write(s)
print("ok")
