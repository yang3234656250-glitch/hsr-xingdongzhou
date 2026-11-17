# 银狼【无敌玩家】的起止只按行动值判断，同一行动值上先后发生的事分不清：
# 爻光开大触发的额外阿哈时刻在银狼开大之前放完（录像 4.7 王棋 26 行动值就是这样），
# 但因为行动值一样，阿哈时刻里银狼的欢愉技被当成结界里的【崩坏级伤害演示】（83 万），1 魂结界易伤也算上了；
# 实际结界外是【殿堂级操作回放】，只加隐藏分没有伤害。结束那头同理（第 3 次强普后同一行动值的阿哈时刻算成结界里）。
# 现在 spans 记下开始 / 结束时的序号 sa / sb，带序号的记录（行动、欢愉技标记）按序号判断先后。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('pending: extra, from: t, e2lvl: extra });', 'pending: extra, from: t, sa: seq, e2lvl: extra });')
rep('      sw.inUlt = false; spans.push({ a: sw.from, b: t });', '      sw.inUlt = false; spans.push({ a: sw.from, b: t, sa: sw.sa, sb: seq });')
rep('    if (sw.inUlt) spans.push({ a: sw.from, b: END, open: true });', '    if (sw.inUlt) spans.push({ a: sw.from, b: END, open: true, sa: sw.sa });')
rep('    const spansNow = () => sw.inUlt ? [...spans, { a: sw.from, b: END, open: true }] : spans;',
    '    const spansNow = () => sw.inUlt ? [...spans, { a: sw.from, b: END, open: true, sa: sw.sa }] : spans;')
rep('  function elationDmgOf(a) {',
    '  // x 在不在这段无敌玩家里：行动值在范围内；同一行动值上按序号分先后（x 和这段都带序号时）\n'
    '  function inSpan(x, sp) {\n'
    '    if (!(x.t >= sp.a - 1e-9 && x.t <= sp.b + 1e-9)) return false;\n'
    '    if (x.seq == null) return true;\n'
    '    if (sp.sa != null && Math.abs(x.t - sp.a) < 1e-9 && x.seq < sp.sa) return false;\n'
    '    if (sp.sb != null && Math.abs(x.t - sp.b) < 1e-9 && x.seq >= sp.sb) return false;\n'
    '    return true;\n'
    '  }\n'
    '  function elationDmgOf(a) {')
rep('      const sp = R_REF.spans.find(z => rec.t >= z.a - 1e-9 && rec.t <= z.b + 1e-9);', '      const sp = R_REF.spans.find(z => inSpan(rec, z));')
rep('a => a.act === "skill" && a.t >= sp.a - 1e-9 && (a.t < rec.t', 'a => a.act === "skill" && inSpan(a, sp) && (a.t < rec.t')
rep('R_REF && rec && R_REF.spans.some(sp => rec.t >= sp.a - 1e-9 && rec.t <= sp.b + 1e-9);', 'R_REF && rec && R_REF.spans.some(sp => inSpan(rec, sp));')
rep('!(R_REF && R_REF.spans.some(sp => m.t >= sp.a - 1e-9 && m.t <= sp.b + 1e-9))) return null;', '!(R_REF && R_REF.spans.some(sp => inSpan(m, sp)))) return null;')
rep('!(R_REF && R_REF.spans.some(sp => a.t >= sp.a - 1e-9 && a.t <= sp.b + 1e-9))) continue;', '!(R_REF && R_REF.spans.some(sp => inSpan(a, sp)))) continue;')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（修正，没改 tv；tools/spanseq.py）</b>。银狼【无敌玩家】以前只按行动值判断起止，<b>同一行动值上先放的阿哈时刻</b>（比如爻光开大触发的额外阿哈时刻放完，再开银狼大招）也被当成在结界里：银狼的欢愉技算成【崩坏级伤害演示】、1 魂结界易伤也算上。实际结界外是【殿堂级操作回放】，只加隐藏分、没有伤害。现在同一行动值按发生的先后分；结束那头（第 3 次强普后同一行动值的事）同样处理。拿 4.7 王棋录像对出来的：录像里那次阿哈时刻总伤害 122.6 万，页面以前 BOSS 一个就扣了 173 万。对已有配置：只影响和银狼开大 / 退出无敌玩家在同一行动值、但排在它前 / 后面的阿哈时刻和攻击。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
