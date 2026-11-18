# 4.7 王棋归寂【三面合一】（天赋原文：此阶段内【成】【住】【坏】共享生命值，【成】【住】处于不可被选中状态）。
# 录像第 3 管血：151 成「虚无的愉悦」→ 坏「清除存在的球戏」、178 住「收束命运的博弈」、196 成「三重的蔑视」、约 212 坏「令欢愉终归死寂」→ 住「埋梗时刻」，
# 正好是三面各按自己的出招表第 3、4 招轮流（接着归寂的回合数），各自跑条（速度 = 归寂当前速度）。
# 写法：敌人卡 phm 某一管写成「主形态+另一面+另一面」，转入这管血时另外两面加进 FACE（不可选中、没有生命值，只占行动），
# 各自记回合数 k（从归寂当时的回合数接着轮）；开始位置按敌人卡 fo（每面离第一次出手差多少 %，默认 "0|50"：成跟着【转面】马上出手，住晚半个间隔，按录像）。
# 轮到某一面时借用归寂本体出手（换成那一面的出招表和回合数），不算归寂自己的回合：不结算归寂身上的增益 / 状态 / 回合开始结束、不触发“归寂第 N 次行动后”的开大。
# 「清除存在的球戏」不再自带再次行动（录像里的“再次行动”就是另一面接着出手）。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
C, Z, K = '万色返空主，归寂•「成」', '万色返空主，归寂•「住」', '万色返空主，归寂•「坏」'
OLD = f'{C}|{C}|{K}|{K}'
NEW = f'{C}|{C}|{K}+{C}+{Z}|{K}+{C}+{Z}'
s = s.replace(OLD, NEW)   # 关卡数据和模拟里的默认都换（两处）
# 1) 换形态：第一个名字是主形态，后面的是另外几面
rep('mn = pm[en.ph], m2 = mn && MON.m.find(x => x.n === mn);',
    'fl = String(pm[en.ph] || "").split("+").map(x => x.trim()), mn = fl[0], m2 = mn && MON.m.find(x => x.n === mn);')
rep('addLog(`${en.name} 变成「${m2.n.split("「")[1] || m2.n}：出招表换成这个形态的`, false, "var(--enemy)"); } }\n',
    'addLog(`${en.name} 变成「${m2.n.split("「")[1] || m2.n}：出招表换成这个形态的`, false, "var(--enemy)"); }\n'
    '        if (fl.length > 1 && !FACE.some(f => f.boss === en)) {   // 【三面合一】：另外几面不可选中、共享生命值，各自跑条出手（录像）\n'
    '          const fo = String(en.fo ?? "0|50").split("|").map(x => num(x)), sp0 = Math.max(1e-9, spdOf(en));\n'
    '          fl.slice(1).forEach((nm, i) => { const mf = MON.m.find(x => x.n === nm); if (mf) FACE.push({ boss: en, n: nm.split("「")[1] ? "「" + nm.split("「")[1] : nm, seq: (mf.q || []).slice(), k: en.turns, at: t + num(fo[i]) * 100 / sp0, o: i }); });\n'
    '          addLog(`${en.name}【三面合一】：${fl.slice(1).map(x => "「" + (x.split("「")[1] || x)).join("、")}不可选中，和${m2 ? "「" + (m2.n.split("「")[1] || m2.n) : "本体"}共享生命值，各自按自己的出招表行动`, false, "var(--enemy)");\n'
    '        } }\n')
rep('    const XQ = U.filter(z => z.kind === "enemy" && (z.xq ?? num(z.rev) > 0)); for (const z of XQ) z.xqOn = true;\n',
    '    const XQ = U.filter(z => z.kind === "enemy" && (z.xq ?? num(z.rev) > 0)); for (const z of XQ) z.xqOn = true;\n'
    '    const FACE = [];   // 4.7 归寂【三面合一】的另外几面：{boss, n, seq, k 回合数, at 下次出手}\n')
# 2) 主循环：轮到某一面时借归寂本体出手
rep('      if (revQ.length) { revQ.sort((a, b) => a.at - b.at);',
    '      { const f = FACE.filter(z => !z.boss.gone).sort((a, b) => a.at - b.at || a.o - b.o)[0];   // 【三面合一】：另外几面轮到时借归寂本体出手\n'
    '        if (f && f.at <= next + 1e-9 && f.at <= END && !(revQ.length && revQ.some(q => q.at < f.at - 1e-9)) && !(ei < evs.length && num(evs[ei].av) < f.at - 1e-9)) {\n'
    '          move(f.at - t); t = f.at; f.at = t + 10000 / Math.max(1e-9, spdOf(f.boss)); const b = f.boss; b.faceGo = f; b.fSv = b.dist; b.dist = 0; b.zpre = -Infinity; continue;\n'
    '        } }\n'
    '      if (revQ.length) { revQ.sort((a, b) => a.at - b.at);')
rep('      move(best); t = next; actor.dist = 0; if (actor.xqGo) actor.xqGo = false;\n',
    '      move(best); t = next; actor.dist = 0; if (actor.xqGo) actor.xqGo = false;\n'
    '      const FG = actor.faceGo || null; if (FG) { actor.faceGo = null; actor.tSv = actor.turns; actor.turns = FG.k; FG.k++; actor.seqSv = actor.seq; actor.seq = FG.seq; }   // 另一面出手：换成它的回合数和出招表（turns++ 之后 = 这一面的第 k 次）\n')
rep('      for (const k of Object.keys(teamCnt)) if (k.split("|")[1] === actor.id && !k.endsWith("|R") && !k.endsWith("|RU")) delete teamCnt[k];',
    '      if (!FG) for (const k of Object.keys(teamCnt)) if (k.split("|")[1] === actor.id && !k.endsWith("|R") && !k.endsWith("|RU")) delete teamCnt[k];')
rep('      for (const u of U) u.buffs = u.buffs.filter(b => !(b.src === actor.id && b.expire <= actor.turns));\n'
    '      EV0.buffs = EV0.buffs.filter(b => !(b.src === actor.id && b.expire <= actor.turns));\n'
    '      TEAM0.buffs = TEAM0.buffs.filter(b => !(b.src === actor.id && b.expire <= actor.turns));\n'
    '      tickSt(actor, "start");',
    '      if (!FG) { for (const u of U) u.buffs = u.buffs.filter(b => !(b.src === actor.id && b.expire <= actor.turns));\n'
    '      EV0.buffs = EV0.buffs.filter(b => !(b.src === actor.id && b.expire <= actor.turns));\n'
    '      TEAM0.buffs = TEAM0.buffs.filter(b => !(b.src === actor.id && b.expire <= actor.turns));\n'
    '      tickSt(actor, "start"); }')
rep('      ultChecks(actor.id, actor.turns, "in");\n', '      if (!FG) ultChecks(actor.id, actor.turns, "in");\n')
rep('      rec.wx = wxActive(); annRec(rec); actions.push(rec);\n      if (actor.kind === "enemy") {   // 敌方回合开始：',
    '      if (FG) rec.face = FG.n;\n      rec.wx = wxActive(); annRec(rec); actions.push(rec);\n      if (actor.kind === "enemy" && !FG) {   // 敌方回合开始：')
rep('      if (!actor.gone) actor.dist = 10000;   // 回合开始时就离场的',
    '      if (FG) { actor.dist = actor.fSv; actor.seq = actor.seqSv; } else if (!actor.gone) actor.dist = 10000;   // 另一面出手不占归寂本体的行动条；回合开始时就离场的')
rep('      endTurn(actor);\n      if (rec.frz) pull(actor, 5000);', '      if (!FG) endTurn(actor);\n      if (rec.frz) pull(actor, 5000);')
rep('      tickSt(actor, "end"); tickSh(actor);   // 状态默认', '      if (!FG) { tickSt(actor, "end"); tickSh(actor); }   // 状态默认')
rep('      ultChecks(actor.id, actor.turns, "after");\n      checkUlts();\n    }\n',
    '      if (FG) actor.turns = actor.tSv; else ultChecks(actor.id, actor.turns, "after");   // 另一面出手不算归寂自己的回合\n      checkUlts();\n    }\n')
# 3) 球戏不再自带再次行动
rep('            actor.again = true; const zt = pool.find', '            const zt = pool.find')
rep('（行动延后 ${num(actor.qxDl ?? 8)}%，按录像推算），归寂再次行动`', '（行动延后 ${num(actor.qxDl ?? 8)}%，按录像推算）`')
# 显示：另一面出手的行在“动作”列写面名
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/face47.py）</b>。4.7 王棋归寂<b>【三面合一】</b>（天赋原文：成、住、坏共享生命值，成、住不可选中）：第 3、4 管血时「成」「住」两面也各自跑条出手（速度同归寂），借归寂出招，按各自形态的出招表接着归寂的回合数轮。录像第 3 管血正好对上：151 成·虚无的愉悦 → 坏·清除存在的球戏，178 住·收束命运的博弈，196 成·三重的蔑视，约 212 坏·令欢愉终归死寂 → 住·埋梗时刻。开始位置：成跟着【转面】马上出手（排在坏前面）、住晚半个间隔（按录像，敌人卡字段 fo 可改）。另外两面出手不算归寂自己的回合（不结算它身上的增益 / 状态，“归寂第 N 次行动后”的开大时机只认本体）。上一条「球戏自带再次行动」撤掉：录像里的“再次行动”就是另一面接着出手。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
