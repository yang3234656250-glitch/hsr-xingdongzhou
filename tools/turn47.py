# 4.7 王棋录像对照第 3 批（用户说明，没改 tv，可重复运行）：
# ① 真珠欢愉技【渲染理性，解构欢愉】“我方全体下一次攻击后对攻击目标额外造成欢愉伤害”：阿哈时刻里真珠的欢愉技最先施放
#    （官方 ElationSkill 优先级 104，录像一致），后面其他人的欢愉技就是这“下一次攻击”。以前阿哈时刻里不算，留给之后的普通攻击。
#    现在阿哈时刻里每个有伤害的欢愉技（银狼只在无敌玩家里）对每个击中的目标加这一段，这些人之后的普通攻击不再有。
#    录像开场：爻光欢愉技 10.2 万，页面加上后约 10 万。
# ② 归寂【转面】（用户说明：转面会拉条归寂和召唤喜剧学家 100%）：每次转阶段，归寂立刻行动（掷骰子）后重新跑条，
#    【粉墨登场】也立刻行动：被消灭的喜剧学家马上重新登场，之后按这一刻起每 65.88 行动值召唤。敌人卡开关 tf（没设 = 跟骰子开关）。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# ① 阿哈时刻里加真珠的那段
rep('''    let total = parts.reduce((x, p) => x + p.r.total, 0);
    // 星神★阿哈欢愉技【满月''',
'''    // 真珠欢愉技【渲染理性，解构欢愉】在阿哈时刻里最先施放（官方优先级 104）：后面每个人的欢愉技就是“下一次攻击”，对每个击中的目标额外一段欢愉伤害
    { const PZ = allUnits().find(z => z.kind === "ally" && !z.sm && tidOf(z) === "1503" && z.elation), pr = PZ && (XR["1503"] || []).find(r => r.flag === "prl");
      if (pr && xrOn(PZ, pr)) {
        const nEl = S.units.filter(x => x.kind === "ally" && !x.sm && x.elation).length;
        let v = xrV(PZ, pr); if (pr.elN) v = num(xrV(PZ, Object.assign({}, pr, { v: pr.elN[Math.max(0, Math.min(4, nEl) - 1)] }))); if (pr.e4x && num(PZ.eid) >= 4) v *= pr.e4x;
        for (const p of parts) { if (p.u === PZ) continue; const r = p.r, N = Math.max(1, num(r.targets, 1)), cnt = r.tg === 3 ? N : tidOf(p.u) === "1506" ? N * (1 - Math.pow(1 - 1 / N, 6)) : 1;
          const amt = LVBASE * v * cnt * num(r.elM, 1) * num(r.critM, 1) * num(r.defM, 1) * num(r.resM, 1) * num(r.vulnM, 1) * num(r.toughM, 1);
          if (amt > 0) { r.prl = amt; r.prlV = v; r.total += amt; } } } }
    let total = parts.reduce((x, p) => x + p.r.total, 0);
    // 星神★阿哈欢愉技【满月''')
rep('''    return "欢愉技：" + el.parts.map(p => `${esc(p.u.name)} ${Math.round(p.r.total).toLocaleString()}${p.r.trueAmt ?''',
    '''    return "欢愉技：" + el.parts.map(p => `${esc(p.u.name)} ${Math.round(p.r.total).toLocaleString()}${p.r.prl ? `（含真珠欢愉技给的 ${Math.round(p.r.prlV * 100)}% 欢愉伤害 ${Math.round(p.r.prl).toLocaleString()}）` : ""}${p.r.trueAmt ?''')
# 之后普通攻击里的真珠那段：欢愉技有伤害的人已经在阿哈时刻里用掉了
rep('        if (who === "flag" && !DB0.some(x => x[0] === "rx" && x[1] === r.flag && x[2] > 0)) continue;\n',
    '        if (who === "flag" && !DB0.some(x => x[0] === "rx" && x[1] === r.flag && x[2] > 0)) continue;\n'
    '        if (r.flag === "prl" && u.elation && u.elDmg !== "no" && dmgEntry(u, "e") && (tidOf(u) !== "1506" || (R_REF && R_REF.spans.some(sp => inSpan(rec, sp))))) continue;   // 真珠欢愉技那段：自己欢愉技有伤害的，阿哈时刻里就用掉了\n')
# ② 转面
rep('    const revQ = [];   // 等着重新登场的敌人（【粉墨登场】）\n',
    '    const revQ = [];   // 等着重新登场的敌人（【粉墨登场】）\n'
    '    let sumT0 = 0;   // 【粉墨登场】的起点（转面时拉条 100% 会重新从这一刻算）\n')
rep('if (num(en.rev) > 0) { const P = num(en.rev); revQ.push({ at: Math.ceil((t + 1e-6) / P) * P, en }); }',
    'if (num(en.rev) > 0) { const P = num(en.rev); revQ.push({ at: sumT0 + Math.ceil((t + 1e-6 - sumT0) / P) * P, en }); }')
rep('      if ((en.lastR ?? en.dice) && en.ph === en.phs.length - 1) {',
    '      if (en.tf ?? en.dice) {   // 4.7 王棋归寂【转面】（用户说明）：归寂拉条 100%（立刻行动掷骰子，之后重新跑条）；【粉墨登场】拉条 100%，被消灭的喜剧学家马上重新登场\n'
    '        en.dist = 10000; sumT0 = t;\n'
    '        const due = revQ.splice(0, revQ.length).map(q => q.en).filter(z => z.gone);\n'
    '        for (const z of due) reviveEnemy(z);\n'
    '        addLog(`${en.name}【转面】：归寂拉条 100%（掷骰子后重新跑条），【粉墨登场】拉条 100%${due.length ? `，${due.length} 个${[...new Set(due.map(z => z.name))].join("、")}马上重新登场` : ""}`, false, "var(--enemy)");\n'
    '      }\n'
    '      if ((en.lastR ?? en.dice) && en.ph === en.phs.length - 1) {')
if 'data-f="tf"' not in s:
    a = 'data-f="lastR">最后一管血按 R</label>'
    assert s.count(a) == 2, s.count(a)
    s = s.replace(a, a + '<label for="tf-${u.id}" title="4.7 王棋归寂【转面】（用户说明）：每次转阶段归寂拉条 100%（立刻行动掷骰子，之后重新跑条），【粉墨登场】拉条 100%：被消灭的召唤敌人（喜剧学家）马上重新登场，之后从这一刻起按周期召唤"><input type="checkbox" id="tf-${u.id}" ${(u.tf ?? !!u.dice) ? "checked" : ""} data-u="${i}" data-f="tf">转面拉条</label>')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（没改 tv；tools/turn47.py）</b>。4.7 王棋录像对照第 3 批。① <b>真珠欢愉技</b>“我方全体下一次攻击后额外造成欢愉伤害”：阿哈时刻里真珠的欢愉技最先放（官方欢愉技优先级 104，录像一致），后面其他人的欢愉技就是这“下一次攻击”，现在每个有伤害的欢愉技对每个击中的目标加这一段（银狼只在无敌玩家里）；这些人之后的普通攻击不再有这段（以前是阿哈时刻里不算、留给之后到真珠下回合前的所有攻击）。录像开场爻光欢愉技 10.2 万，页面现在约 10 万。② 归寂<b>【转面】</b>（你说的）：每次转阶段归寂拉条 100%（立刻行动掷骰子、之后重新跑条），【粉墨登场】拉条 100%：被消灭的喜剧学家马上重新登场，之后从这一刻起每 65.88 行动值召唤。敌人卡开关「转面拉条」，没设就跟骰子开关。对已有配置：有真珠的欢愉队伤害分布变了（阿哈时刻变高、普通攻击变低）；②只影响放了 4.7 王棋归寂、开了敌人掉血的方案。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
