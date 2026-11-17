# 行动顺序底层规则（用户说明）：几个单位都被拉条到 0 时，按拉条前的先后行动——拉条前谁先轮到，拉条后还是谁先。
# 以前是“后拉条的先走”（zseq）。现在 pull 记下拉条前本该行动的时刻 zpre，同一时刻比 zpre（小的先）；
# 登场立刻行动 / 直接给的额外回合（dist 直接设 0）记 −Infinity，排最前。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('    const pull = (u, d) => { const was = u.dist; u.dist = Math.max(0, was - d); if (was > 0 && u.dist === 0) u.zseq = ++zc; };',
    '    const pull = (u, d) => { const was = u.dist; u.dist = Math.max(0, was - d); if (was > 0 && u.dist === 0 && u.zpre == null) { u.zpre = t + was / Math.max(1e-9, spdOf(u)); u.zseq = ++zc; } };   // 拉条前本该行动的时刻（同时被拉到 0 的按它排先后）')
rep('        if (!was && sd.now) { u.dist = 0; u.zseq = ++zc; }', '        if (!was && sd.now) { u.dist = 0; u.zseq = ++zc; u.zpre = -Infinity; }')
rep('actor.life += 1; actor.dist = 0; actor.zseq = ++zc;', 'actor.life += 1; actor.dist = 0; actor.zseq = ++zc; actor.zpre = -Infinity;')
rep('        else if (dt <= best + 1e-9 && (u.zseq || 0) > (actor.zseq || 0)) { actor = u; best = Math.min(best, dt); } // 同一时刻：后拉条的先走',
    '        else if (dt <= best + 1e-9 && (u.zpre ?? t + dt) < (actor.zpre ?? t + best) - 1e-12) { actor = u; best = Math.min(best, dt); } // 同一时刻：按拉条前的先后（拉条前谁先轮到，拉条后还是谁先）')
rep('      actor.zseq = 0;\n', '      actor.zseq = 0; actor.zpre = null;\n')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（行动顺序底层规则，没改 tv；tools/pullord.py）</b>。几个单位被拉条到同一时刻时，<b>按拉条前的先后行动</b>：拉条前谁先轮到，拉条后还是谁先（你说的）。以前是“后被拉条的先走”。“登场立刻行动”和直接给的额外回合照旧排最前。对已有配置：同一时刻有两个以上单位被拉满的地方，先后可能变。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
