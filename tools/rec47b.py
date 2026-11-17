# 4.7 王棋录像对照第 2 批（用户回复，没改 tv，可重复运行）：
# ① 银狼每次强普算 1 个【怪怪怪味豆】：+3 笑点（S.sw.bean，没设 = 1；施放时、扣次数之前加，所以最后一次强普的也先算进隐藏分）
# ② 额外阿哈时刻（爻光终结技、秘技、骰子给的）的伤害快照以前在欢愉技效果之前记：爻光欢愉技给的【凶星低语】、
#    “首次施放欢愉技时全队欢愉度 +10%”这类都没吃到（普通阿哈时刻是之后重新记的）。现在欢愉技效果之后再记一次。
# ③ 爻光固有行迹【欢愉万相★心灵感应】：升格时【大吉大利】倍率提高原倍率的 20%（阿哈 2 魂 40%），以前漏了
# ④ 会重新登场的敌人（喜剧学家）开局不在场，0 行动值在进战秘技（爻光战技、阿哈的额外阿哈时刻）之后才召唤（敌人卡开关 rv0，没设 = 开）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# ① 怪味豆
rep('    const spendCharge = () => {',
    '    // 每次强普按 W.bean 个【怪怪怪味豆】算（各 +3 笑点；用户定的，盲盒本来是随机的）\n'
    '    const beanP = rec => { const n = num(W.bean, 1); if (n > 0 && rec && rec.act === "ebasic") addPunch(3 * n, "怪味豆"); };\n'
    '    const spendCharge = () => {')
rep('        if (rec.ult) { rec.scU = sw.score; spendCharge(); }   // scU：施放时的隐藏分（伤害按它算；最后一次强普扣完次数后隐藏分会被清空）',
    '        if (rec.ult) { rec.scU = sw.score; beanP(rec); spendCharge(); }   // scU：施放时的隐藏分（伤害按它算；最后一次强普扣完次数后隐藏分会被清空）')
rep('        if (rec.ult) { rec.scU = sw.score; spendCharge(); }\n', '        if (rec.ult) { rec.scU = sw.score; beanP(rec); spendCharge(); }\n')
rep('      if (actor === swU && rec.ult) { rec.scU = sw.score; spendCharge(); }', '      if (actor === swU && rec.ult) { rec.scU = sw.score; beanP(rec); spendCharge(); }')
rep('        ${sn("skillPunch", "未开大战技笑点 +", \'min="0" step="1"\')}',
    '        ${sn("skillPunch", "未开大战技笑点 +", \'min="0" step="1"\')}\n'
    '        <label for="s-bean" title="【狼尊时刻】里的头号补给盲盒是随机的；这里按每次强普出 N 个【怪怪怪味豆】算，每个 +3 笑点（用户定的，默认 1）">每次强普怪味豆 <input type="number" id="s-bean" value="${W.bean ?? 1}" data-s="bean" min="0" step="1" style="width:50px"> 个（各 +3 笑点）</label>')
# ② 额外阿哈时刻：欢愉技效果之后再记快照
rep('        onAha(); // 欢愉技 effects still happen here, but their punchlines go to the pool instead of this instant\'s fixed count',
    '        onAha(); // 欢愉技 effects still happen here, but their punchlines go to the pool instead of this instant\'s fixed count\n'
    '        reSnap(rec, A);   // 伤害吃得到这次欢愉技给的【凶星低语】、首次欢愉技的欢愉度等（普通阿哈时刻也是之后再记）')
# ③ 大吉大利升格
rep('      yaoEl = Math.max(elStat, num(YG.el, 0));',
    '      if (rec.wx) { const AH = S.units.find(x => x.kind === "ally" && !x.sm && tidOf(x) === "1511"); yaoV *= 1 + (AH && num(AH.eid) >= 2 ? 0.4 : 0.2); }   // 固有行迹【欢愉万相★心灵感应】：升格时倍率提高原倍率的 20%（阿哈 2 魂 40%）\n'
    '      yaoEl = Math.max(elStat, num(YG.el, 0));')
# ④ 喜剧学家开局秘技之后才登场
rep('    if (swU && pool > 0) setScore(sw.score + pool, "开局笑点");\n',
    '    if (swU && pool > 0) setScore(sw.score + pool, "开局笑点");\n'
    '    if (eHpOn) for (const z of U) if (z.kind === "enemy" && num(z.rev) > 0 && (z.rv0 ?? true)) { z.gone = true; z.rv0Q = true; }   // 召唤出来的（喜剧学家）：进战秘技之后、0 行动值才登场\n')
rep('    const revQ = [];   // 等着重新登场的敌人（【粉墨登场】）\n',
    '    const revQ = [];   // 等着重新登场的敌人（【粉墨登场】）\n'
    '    for (const z of U) if (z.rv0Q) { revQ.push({ at: 0, en: z }); delete z.rv0Q; z.rv0F = true; }\n')
rep('      marks.push({ t, uid: en.id, label: "重新登场", color: "var(--enemy)", from: "" });\n'
    '      addLog(`${en.name} 重新登场（每 ${fmt(num(en.rev), 1)} 行动值一次；生命值 ${Math.round(en.ehc)}）`, false, "var(--enemy)");',
    '      const first = en.rv0F; en.rv0F = false;\n'
    '      marks.push({ t, uid: en.id, label: first ? "登场" : "重新登场", color: "var(--enemy)", from: "" });\n'
    '      addLog(first ? `${en.name} 登场（进战秘技之后召唤；之后被消灭每 ${fmt(num(en.rev), 1)} 行动值重新登场）` : `${en.name} 重新登场（每 ${fmt(num(en.rev), 1)} 行动值一次；生命值 ${Math.round(en.ehc)}）`, false, "var(--enemy)");')
if 'data-f="rv0"' not in s:
    a = 'data-f="rev" style="width:64px"> 行动值重新登场</label>'
    assert s.count(a) == 2, s.count(a)
    s = s.replace(a, a + '<label for="r0-${u.id}" title="勾上 = 开局不在场，0 行动值在进战秘技（爻光战技、阿哈的额外阿哈时刻等）之后才召唤（4.7 王棋的喜剧学家，用户说明）"><input type="checkbox" id="r0-${u.id}" ${(u.rv0 ?? true) ? "checked" : ""} data-u="${i}" data-f="rv0">秘技之后才登场</label>')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（没改 tv；tools/rec47b.py）</b>。4.7 王棋录像对照第 2 批（按你的回复）：① 银狼<b>每次强普算 1 个【怪怪怪味豆】</b>（+3 笑点，银狼设置里可改个数，0 = 不算）。② <b>额外阿哈时刻</b>（爻光终结技 / 秘技 / 骰子给的）的伤害以前在欢愉技效果之前记，吃不到这次爻光欢愉技给的【凶星低语】和“首次施放欢愉技全队欢愉度 +10%”；现在之后再记（普通阿哈时刻本来就是这样）。③ 爻光固有行迹【欢愉万相★心灵感应】升格时【大吉大利】倍率 +20%（阿哈 2 魂 +40%）以前漏了。④ 会重新登场的敌人（喜剧学家）<b>开局不在场，0 行动值在进战秘技之后才召唤</b>（敌人卡开关「秘技之后才登场」，默认开）。对已有配置：有银狼的队伍笑点 / 隐藏分变多；只影响开了敌人掉血、放了喜剧学家的方案（④）；②③ 只影响伤害。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
