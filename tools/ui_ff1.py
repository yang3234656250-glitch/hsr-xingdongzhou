# 借鉴绯绯狐工具箱的三处界面（2026-11-23，没改 tv，不改模拟结果）：
# ① 使用说明加「同一行动值的结算顺序」（按引擎实际顺序写）；
# ② 回能记录：addEnergy 多记 w（这次应得的量）和 sq（排在哪条记录之前），行动顺序表可显示每次能量变化和被上限截掉的部分；
#    拉条溢出：pull() 返回溢出的距离，拉条标记带 pov（溢出 %），行动轴标记右上角红点、提示里写溢出多少；
# ③ 行动顺序按轮分组：轮次标题可点击收起 / 展开（本机记住），标题写本轮行动次数，没有行动的轮也画出来，表尾写共多少条。
# 用法：python3 tools/ui_ff1.py index.html
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s
s = s.replace("\r\n", "\n")


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:80])
    s = s.replace(old, new)


# ---- 模拟：只多记字段 ----
rep("if (was > 0 && u.dist === 0 && u.zpre == null) { u.zpre = t + was / Math.max(1e-9, spdOf(u)); u.zseq = ++zc; } };",
    "if (was > 0 && u.dist === 0 && u.zpre == null) { u.zpre = t + was / Math.max(1e-9, spdOf(u)); u.zseq = ++zc; } return Math.max(0, d - was); };   // 返回拉满后多出的距离（溢出，只给显示用）")
rep('if (eff.type === "advance") { pull(tg, v * 100); marks.push({ t, uid: tg.id, label: "+" + v + "%", color: srcColor, from: src ? src.name : "事件" }); }',
    'if (eff.type === "advance") { const ov = pull(tg, v * 100); marks.push({ t, uid: tg.id, label: "+" + v + "%", color: srcColor, from: src ? src.name : "事件", pov: ov > 1e-6 ? ov / 100 : undefined, sq: seq - 0.5, self: tg === curActor || undefined }); }   // pov：溢出的拉条 %（行动轴角标、回能记录）')
rep("""      const before = u.e;
      u.e = Math.max(0, Math.min(c.capE, u.e + amt * (useER ? erOf(u) / 100 : 1)));
      eH[u.id].push({ t, v: u.e, d: u.e - before, why: curWhy });""",
    """      const before = u.e, g = amt * (useER ? erOf(u) / 100 : 1);
      u.e = Math.max(0, Math.min(c.capE, u.e + g));
      eH[u.id].push({ t, v: u.e, d: u.e - before, why: curWhy, w: g, sq: seq - 0.5 });   // w = 这次应得的量（比 d 多的部分被上限截掉）；sq = 排在行动顺序哪条之前（只给显示用）""")
rep('eH[u.id].push({ t, v: u.e, d: u.e - b0, why: "开大消耗" }); }',
    'eH[u.id].push({ t, v: u.e, d: u.e - b0, why: "开大消耗", sq: seq - 0.5 }); }')

# ---- 行动轴：拉条溢出角标 ----
rep("""      const tip = `${m.from ? esc(m.from) + " → " : ""}${m.label}`;
      if (prev) { prev.label += " " + m.label; prev.tips.push(tip); continue; }""",
    """      const tip = `${m.from ? esc(m.from) + " → " : ""}${m.label}${m.pov ? `（${m.self ? "正在行动，" : ""}溢出 ${fmt(m.pov)}%，不累积到下一次行动）` : ""}`;
      if (prev) { prev.label += " " + m.label; prev.tips.push(tip); if (m.pov) prev.pov = num(prev.pov) + m.pov; continue; }""")
rep("""        <text x="${cx + 7}" y="${cy + 3.5}" font-size="9.5" fill="${m.key ? "var(--fg)" : "var(--muted)"}">${m.label}</text>""",
    """        <text x="${cx + 7}" y="${cy + 3.5}" font-size="9.5" fill="${m.key ? "var(--fg)" : "var(--muted)"}">${m.label}</text>${m.pov ? `<circle cx="${cx + 4.5}" cy="${cy - 5}" r="2.6" fill="var(--enemy)" stroke="var(--panel)" stroke-width="1"></circle>` : ""}""")

# ---- 行动顺序表：回能记录 + 按轮收起 ----
rep("""<button type="button" id="heal-log" class="ghost" aria-pressed="true" title="行动顺序里每次治疗的数值">治疗记录：显示</button>""",
    """<button type="button" id="heal-log" class="ghost" aria-pressed="true" title="行动顺序里每次治疗的数值">治疗记录：显示</button><button type="button" id="e-log" class="ghost" aria-pressed="false" title="行动顺序里每次能量变化：来源、变化前后、被能量上限截掉的部分；拉条溢出也列在这里">回能记录：隐藏</button>""")

rep("""  $("heal-log").addEventListener("click", () => { healLogOn = !healLogOn; try { localStorage.setItem(HLOG_KEY, healLogOn ? "1" : "0"); } catch (e) {} healLogUi(); update(); });""",
    """  $("heal-log").addEventListener("click", () => { healLogOn = !healLogOn; try { localStorage.setItem(HLOG_KEY, healLogOn ? "1" : "0"); } catch (e) {} healLogUi(); update(); });
  // 回能记录（默认隐藏，本机记住）
  const ELOG_KEY = STORE + "-elog";
  let eLogOn = (() => { try { return localStorage.getItem(ELOG_KEY) === "1"; } catch (e) { return false; } })();
  const eLogUi = () => { $("e-log").setAttribute("aria-pressed", String(eLogOn)); $("e-log").textContent = eLogOn ? "回能记录：显示" : "回能记录：隐藏"; };
  eLogUi();
  $("e-log").addEventListener("click", () => { eLogOn = !eLogOn; try { localStorage.setItem(ELOG_KEY, eLogOn ? "1" : "0"); } catch (e) {} eLogUi(); update(); });
  // 行动顺序按轮收起（本机显示偏好，存收起的轮次）
  const OCYC_KEY = STORE + "-ocyc";
  let ocycFold = (() => { try { return new Set(JSON.parse(localStorage.getItem(OCYC_KEY) || "[]")); } catch (e) { return new Set(); } })();
  $("t-order").addEventListener("click", e => {
    const tr = e.target.closest("tr[data-cyc]"); if (!tr) return;
    const c = Number(tr.dataset.cyc); if (ocycFold.has(c)) ocycFold.delete(c); else ocycFold.add(c);
    try { localStorage.setItem(OCYC_KEY, JSON.stringify([...ocycFold])); } catch (err) {}
    update();
  });
  $("t-order").addEventListener("keydown", e => { if ((e.key === "Enter" || e.key === " ") && e.target.closest("tr[data-cyc]")) { e.preventDefault(); e.target.closest("tr[data-cyc]").click(); } });""")

# renderOrder：日志、回能记录、行动按 seq 合并，按轮分组
old_head = """    let cur = -1, li = 0;
    const logs = healLogOn ? R.log : R.log.filter(l => !l.heal);
    actions.forEach((a, i) => {
      while (li < logs.length && logs[li].seq < a.seq) {
        const l = logs[li++];
        const fd = !dmgOn ? null : l.fm ? fuaDmgOf(l.fm, byId[l.fm.uid]) : l.um ? ultDmgOf(l.um, byId[l.um.uid]) : l.em ? elskDmgOf(l.em, byId[l.em.uid]) : l.dd ? dotSum(l.dd, byId) : null;
        h += `<tr><td></td><td class="num">${fmt(l.t, 2)}</td><td class="logcell" colspan="${cols - 2}" style="color:${l.bad ? "var(--enemy)" : l.color ? esc(l.color) : "var(--sw)"};font-weight:600">${esc(l.text)}${fd ? `｜伤害 <b>${dmgFmt(fd.total)}</b>` : ""}</td></tr>`;
      }
      if (a.cycle !== cur) {
        cur = a.cycle;
        const end = cur === 0 ? S.c0 : S.c0 + S.cn * cur;
        h += `<tr class="cyc"><td colspan="${cols}">第 ${cur} 轮　·　AV ≤ ${end}</td></tr>`;
      }
      const u = byId[a.uid];"""
new_head = """    let cur = -1, li = 0, hid = false;
    const logs0 = healLogOn ? R.log : R.log.filter(l => !l.heal);
    // 回能记录：每次能量变化（来源、前后、被上限截掉的部分）和拉条溢出，按发生的先后插进日志
    const eRows = [];
    if (eLogOn) {
      for (const [id, L] of Object.entries(R.eH || {})) { const u = byId[id]; if (!u) continue;
        for (const x of L) { if (x.sq == null) continue; const cut = x.w != null && x.w > 0 ? x.w - x.d : 0;
          if (Math.abs(x.d) < 1e-9 && cut < 0.05) continue;
          const nm = typeof eName === "function" ? eName(u) : "能量", mx = eCfg(u).maxE;
          eRows.push({ t: x.t, seq: x.sq, elog: 1, uid: id, color: u.color, cut: cut >= 0.05 ? cut : 0,
            text: `${u.name} ${nm}${x.d >= 0 ? "+" : "−"}${fmt(Math.abs(x.d), 1)}${x.why ? `（${x.why}）` : ""} → ${fmt(x.v, 1)}/${mx}${cut >= 0.05 ? `，上限截掉 ${fmt(cut, 1)}` : ""}` }); } }
      for (const m of R.marks) if (m.pov && m.sq != null && byId[m.uid]) eRows.push({ t: m.t, seq: m.sq, elog: 1, uid: m.uid, color: byId[m.uid].color, cut: 0, pull: m.pov,
        text: `${byId[m.uid].name} 被 ${m.from} 拉条 ${m.label.replace(/^\\+/, "")}：${m.self ? "正在行动，" : ""}溢出 ${fmt(m.pov)}%（不累积到下一次行动）` });
    }
    const logs = eRows.length ? logs0.concat(eRows).sort((p, q) => p.seq - q.seq) : logs0;
    const cycN = {}; for (const a of actions) cycN[a.cycle] = (cycN[a.cycle] || 0) + 1;
    const cycEnd = c => c === 0 ? S.c0 : S.c0 + S.cn * c;
    const head = c => { hid = ocycFold.has(c); return `<tr class="cyc" data-cyc="${c}" tabindex="0" style="cursor:pointer" title="点击${hid ? "展开" : "收起"}这一轮" aria-expanded="${!hid}"><td colspan="${cols}">${hid ? "▸" : "▾"} 第 ${c} 轮　·　AV ≤ ${cycEnd(c)}　·　${cycN[c] ? `${cycN[c]} 次行动` : "本轮没有行动"}${hid ? "（已收起）" : ""}</td></tr>`; };
    const toCyc = c => { if (c <= cur) return; for (let k = cur + 1; k <= c; k++) h += head(k); cur = c; };
    const logRow = l => {
      if (l.elog) return `<tr class="elog"><td></td><td class="num">${fmt(l.t, 2)}</td><td class="logcell" colspan="${cols - 2}" style="color:${esc(l.color)};opacity:.85">${l.pull ? "⤴ " : "⚡ "}${esc(l.text)}${l.cut || l.pull ? ` <span class="bp" style="color:var(--enemy)">溢出</span>` : ""}</td></tr>`;
      const fd = !dmgOn ? null : l.fm ? fuaDmgOf(l.fm, byId[l.fm.uid]) : l.um ? ultDmgOf(l.um, byId[l.um.uid]) : l.em ? elskDmgOf(l.em, byId[l.em.uid]) : l.dd ? dotSum(l.dd, byId) : null;
      return `<tr><td></td><td class="num">${fmt(l.t, 2)}</td><td class="logcell" colspan="${cols - 2}" style="color:${l.bad ? "var(--enemy)" : l.color ? esc(l.color) : "var(--sw)"};font-weight:600">${esc(l.text)}${fd ? `｜伤害 <b>${dmgFmt(fd.total)}</b>` : ""}</td></tr>`;
    };
    const emitLog = l => { toCyc(Math.max(cur, cycleOf(l.t))); if (!hid) h += logRow(l); };
    actions.forEach((a, i) => {
      while (li < logs.length && logs[li].seq < a.seq) emitLog(logs[li++]);
      toCyc(a.cycle);
      if (hid) return;
      const u = byId[a.uid];"""
rep(old_head, new_head)

old_tail = """    while (li < logs.length) {
      const l = logs[li++];
      const fd = !dmgOn ? null : l.fm ? fuaDmgOf(l.fm, byId[l.fm.uid]) : l.um ? ultDmgOf(l.um, byId[l.um.uid]) : l.em ? elskDmgOf(l.em, byId[l.em.uid]) : l.dd ? dotSum(l.dd, byId) : null;
      h += `<tr><td></td><td class="num">${fmt(l.t, 2)}</td><td class="logcell" colspan="${cols - 2}" style="color:${l.bad ? "var(--enemy)" : l.color ? esc(l.color) : "var(--sw)"};font-weight:600">${esc(l.text)}${fd ? `｜伤害 <b>${dmgFmt(fd.total)}</b>` : ""}</td></tr>`;
    }
    if (!actions.length) h += `<tr><td colspan="${cols}" style="color:var(--muted)">显示范围内没有行动。添加单位或增加显示轮次。</td></tr>`;"""
new_tail = """    while (li < logs.length) emitLog(logs[li++]);
    if (actions.length) toCyc(Math.max(0, Math.round(num(S.cycles, 1)) - 1));   // 后面没有行动的轮也画出标题
    if (!actions.length) h += `<tr><td colspan="${cols}" style="color:var(--muted)">显示范围内没有行动。添加单位或增加显示轮次。</td></tr>`;
    else {   // 表尾：一共多少条，免得把“收起 / 隐藏”看成“没算”
      const hl = healLogOn ? 0 : R.log.filter(l => l.heal).length, cuts = {};
      for (const [id, L] of Object.entries(R.eH || {})) for (const x of L) if (x.w != null && x.w - x.d >= 0.05 && byId[id]) cuts[id] = (cuts[id] || 0) + x.w - x.d;
      const ct = Object.entries(cuts).map(([id, v]) => `${byId[id].name} ${fmt(v, 1)}`).join("、");
      h += `<tr class="otail"><td colspan="${cols}" style="color:var(--muted);font-size:12px">显示到 AV ${fmt(R.END)}｜共 ${actions.length} 次行动、${R.log.length} 条记录${hl ? `（治疗记录隐藏了 ${hl} 条）` : ""}${ocycFold.size ? `｜收起了 ${[...ocycFold].filter(c => c <= cur).length} 轮` : ""}${ct ? `｜能量被上限截掉：${ct}` : ""}</td></tr>`;
    }"""
rep(old_tail, new_tail)

# ---- 使用说明：同一行动值的结算顺序 ----
rep("""            <li><b>召唤物和计数</b>：""",
    """            <li><b>同一行动值的结算顺序</b>（页面就是按这个算的）：① <b>进战</b>：开局效果分三轮（先结算排在最前的效果，再其他开局效果，最后“进战自动施放战技”的秘技）→ 敌人进入战斗 → 开怪秘技伤害 → 满能量的自动开大。② <b>真正的追加攻击</b>在触发它的那次攻击里立即结算，排在下面所有事之前（“视为追加攻击”的按原来的位置）。③ <b>一个正常回合</b>：增益到期 → “每回合开始时 −1”的状态 → 统一结算（小伊卡）→ 安排在“××回合中”的大招 → 这些大招带来的额外回合 / 额外阿哈时刻（在这个角色行动之前处理完）→ 回合开始效果 → 行动（施放时效果、回能、攻击）→ 回合结束的状态 → 安排在“××第 N 次行动后”的大招 → 满能量自动开大和连开排队的大招。④ <b>排队的额外回合</b>，每次处理一项：银狼被打断后的再次施放 → 银狼额外强普 → 角色额外回合（按获得的先后）→ 额外阿哈时刻；每项结束后同样先看“之后”安排的大招，再看自动开大。⑤ 都处理完才选下一个跑满行动条的单位；<b>手动事件、敌人重新登场</b>在同一行动值时排在单位行动之前；几个单位同时被拉到 0，按拉条前的先后行动。同一处安排了几个大招时，按“开大时机”下方拖出来的顺序。</li>
            <li><b>回能记录和溢出</b>：行动顺序表头的“回能记录”打开后，每次能量变化都列一行（来源、变化后 / 上限），被能量上限截掉的部分标“溢出”，表尾汇总每人一共被截掉多少。拉条把行动条拉满后多出的部分不会留到下一次行动，行动轴上这个拉条标记右上角有红点，鼠标放上去看溢出多少。轮次标题点一下可以收起 / 展开那一轮。</li>
            <li><b>召唤物和计数</b>：""")

# 更新日志
rep("""        <details id="changelog">""", """        <details id="changelog">""")
i = s.find('<details id="changelog">'); j = s.find("<li", i)
entry = """<li><b>2026-11-23（借鉴绯绯狐工具箱的三处显示，没改 tv）</b>。① 使用说明新加「同一行动值的结算顺序」：进战、追加攻击、一个正常回合、排队的额外回合、手动事件和同时拉到 0 的先后，按页面引擎实际的顺序写（没有改顺序）。② 行动顺序表头新加「回能记录」（默认隐藏，本机记住）：每次能量变化一行，写来源、变化后 / 上限，被能量上限截掉的部分标“溢出”，表尾汇总每人被截掉多少；拉条把行动条拉满后多出的部分（不累积到下一次行动）也列在这里，行动轴上这个拉条标记右上角加红点，提示里写溢出多少。③ 行动顺序按轮分组：轮次标题写本轮行动次数，点一下收起 / 展开（本机记住）；显示范围内没有行动的轮也画标题；表尾写“显示到 AV ×｜共 × 次行动、× 条记录”，治疗记录隐藏时写隐藏了几条。对已有配置：模拟只多记了几个显示用的字段，行动顺序、能量、战技点、开大次数完全不变。</li>
"""
s = s[:j] + entry + "            " + s[j:]

if crlf:
    s = s.replace("\n", "\r\n")
open(p, "w", encoding="utf-8", newline="").write(s)
print("ok")
