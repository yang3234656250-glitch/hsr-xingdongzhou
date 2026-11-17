# 4.7 王棋喜剧学家【谐星荟萃】（官方天赋：在行动序列上添加【谐星荟萃】，每次行动时所有喜剧学家一同发起攻击；用户确认这样做）：
# 喜剧学家（敌人卡 xq，没设 = 有 rev 的就算）不再单独跑条；单独一个【谐星荟萃】行动（速度 = 喜剧学家的速度，从 0 开始跑），
# 轮到时场上所有喜剧学家按顺序各出手一次。录像：第一次在 45 行动值。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('    for (const z of U) if (z.rv0Q) { revQ.push({ at: 0, en: z }); delete z.rv0Q; z.rv0F = true; }\n',
    '    for (const z of U) if (z.rv0Q) { revQ.push({ at: 0, en: z }); delete z.rv0Q; z.rv0F = true; }\n'
    '    // 【谐星荟萃】：喜剧学家不单独跑条，这个行动轮到时场上所有喜剧学家一同出手\n'
    '    const XQ = U.filter(z => z.kind === "enemy" && (z.xq ?? num(z.rev) > 0)); for (const z of XQ) z.xqOn = true;\n'
    '    const xqSpd = XQ.length ? spdOf(XQ[0]) : 0; let xqAt = XQ.length && xqSpd > 0 ? 10000 / xqSpd : null;\n')
rep('        if (u.gone || u.paused || (u.sm && u.sm.noTurn)) continue;   // 不在场的召唤物、被暂停的本体、不上行动序列的忆灵（德谬歌、小伊卡）不跑条\n',
    '        if (u.gone || u.paused || (u.sm && u.sm.noTurn)) continue;   // 不在场的召唤物、被暂停的本体、不上行动序列的忆灵（德谬歌、小伊卡）不跑条\n'
    '        if (u.xqOn && !u.xqGo) continue;   // 喜剧学家只在【谐星荟萃】行动时出手\n')
rep('      const next = t + best;\n      if (revQ.length) {',
    '      const next = t + best;\n'
    '      if (xqAt != null && xqAt <= next + 1e-9 && xqAt <= END && !(revQ.length && revQ.some(q => q.at < xqAt - 1e-9)) && !(ei < evs.length && num(evs[ei].av) < xqAt - 1e-9)) {   // 【谐星荟萃】行动（更早的重新登场 / 手动事件先处理）\n'
    '        move(xqAt - t); t = xqAt; xqAt += 10000 / xqSpd;\n'
    '        const al = U.filter(z => z.xqOn && !z.gone); al.forEach((z, i) => { z.xqGo = true; z.dist = 0; z.zpre = t + i * 1e-9; });\n'
    '        addLog(`【谐星荟萃】行动：${al.length ? `${al.length} 个${[...new Set(al.map(z => z.name))].join("、")}一同发起攻击` : "场上没有喜剧学家"}`, false, "var(--enemy)");\n'
    '        continue;\n'
    '      }\n'
    '      if (revQ.length) {')
rep('      move(best); t = next; actor.dist = 0;\n', '      move(best); t = next; actor.dist = 0; if (actor.xqGo) actor.xqGo = false;\n')
if 'data-f="xq"' not in s:
    a = 'data-f="rv0">秘技之后才登场</label>'
    assert s.count(a) == 2, s.count(a)
    s = s.replace(a, a + '<label for="xq-${u.id}" title="勾上 = 不单独跑条，只在【谐星荟萃】行动时和其他同类一起出手（4.7 王棋喜剧学家；【谐星荟萃】速度 = 它的速度，从 0 开始）"><input type="checkbox" id="xq-${u.id}" ${(u.xq ?? num(u.rev) > 0) ? "checked" : ""} data-u="${i}" data-f="xq">随【谐星荟萃】出手</label>')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（没改 tv；tools/xq47.py）</b>。4.7 王棋喜剧学家<b>【谐星荟萃】</b>（官方天赋，你确认的做法）：喜剧学家不再各自跑条，行动序列上单独一个【谐星荟萃】（速度 = 喜剧学家的速度，从 0 开始），轮到时场上所有喜剧学家依次出手；场上没有就空过。录像里第一次在 45 行动值，和这个一致。敌人卡开关「随【谐星荟萃】出手」，有重新登场周期的敌人默认开。对已有配置：只影响放了喜剧学家的方案。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
