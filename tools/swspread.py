# 银狼LV.999 强化普攻【狼尊时刻】的 100 段弹射、【头号补给盲盒】（官方“由敌方全体均分”）按在场敌人平均分配（以前全算主目标）。可重复运行
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b):
    global s
    if b in s: return
    assert s.count(a) == 1, a[:90]; s = s.replace(a, b)
rep('    if (EA && EA.ord && EA.ord.length > 1 && (nAll > 1 || nAdj > 0) && !e.dot && !e.brk) {',
    '    const spread = tidOf(u) === "1506" && (e.key === "b2" || e.key === "box");   // 银狼强普 100 段弹射 / 头号补给盲盒（敌方全体均分）：按在场敌人平均分（段数多，近似均分）\r\n'
    '    if (EA && EA.ord && EA.ord.length > 1 && (nAll > 1 || nAdj > 0 || spread) && !e.dot && !e.brk) {')
rep('      EA.ord.forEach((id, i) => { const w = i === 0 ? e.v + e.rnd : e.tg === 3 ? e.v : e.tg === 2 ? (i <= nAdj ? e.adj : 0) : e.tg === 4 ? e.adj : 0; if (w > 0) W.push([id, w, gOf(id, i)]); });',
    '      EA.ord.forEach((id, i) => { const w = spread ? (num(e.v) + num(e.rnd)) / EA.ord.length : i === 0 ? e.v + e.rnd : e.tg === 3 ? e.v : e.tg === 2 ? (i <= nAdj ? e.adj : 0) : e.tg === 4 ? e.adj : 0; if (w > 0) W.push([id, w, gOf(id, i)]); });')
rep('      mult, multOne: e.v + e.rnd, v: e.v, adj: e.adj, rnd: e.rnd, adjN: nAdj, tg: e.tg, targets: nAll + nAdj, name: e.n, lv: e.lv, key: e.key, adjF, tw };',
    '      mult, multOne: e.v + e.rnd, v: e.v, adj: e.adj, rnd: e.rnd, adjN: nAdj, tg: e.tg, targets: nAll + nAdj, name: e.n, lv: e.lv, key: e.key, adjF, tw, spread: spread && !!tw };')
rep('        if (Array.isArray(d.tw) && d.tw.length) { for (const [id, sh] of d.tw)',
    '        if (d.spread && Array.isArray(d.tw) && d.tw.length > 1) {   // 均分的弹射：打死的目标剩下的段数转到还在场的（没有分阶段的才算打死，有分阶段的照收）\r\n'
    '          let left = d.total, L = d.tw.map(([id, sh]) => [byId[id], sh]).filter(([z]) => z && !z.gone && z.ehx > 0);\r\n'
    '          for (let k = 0; k < 6 && left > 1e-6 && L.length; k++) {\r\n'
    '            const S2 = L.reduce((p, x) => p + x[1], 0); let spill = 0; const keep2 = [];\r\n'
    '            for (const [z, sh] of L) { if (z.gone) continue; const a = left * sh / S2, cap = Math.max(0, z.ehc); if (L.length > 1 && !z.phs && a >= cap) { hurtEnemy(z, cap, killer); spill += a - cap; } else { hurtEnemy(z, a, killer); if (!z.gone) keep2.push([z, sh]); } }\r\n'
    '            left = spill; L = keep2;\r\n'
    '          }\r\n'
    '          return;\r\n'
    '        }\r\n'
    '        if (Array.isArray(d.tw) && d.tw.length) { for (const [id, sh] of d.tw)')
rep('${r.tg === 0 ? "（弹射总倍率）" : ""}', '${r.tg === 0 ? `（弹射总倍率${r.spread ? `，按在场 ${(r.tw || []).length} 个敌人均分` : ""}）` : ""}')
open(p, 'w', encoding='utf8', newline='').write(s)
