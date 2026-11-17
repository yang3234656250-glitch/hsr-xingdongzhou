# 用户说明：同时拉条 100% 时按拉条前的先后：拉条前归寂比【粉墨登场】先轮到，拉条后归寂也先行动。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('        pull(en, 10000); sumT0 = t;\n'
    '        const due = revQ.filter(q => q.en.gone).map(q => (q.at = t, q.en));   // 主循环里额外回合之后、下一个正常行动之前处理\n',
    '        const bossLeft = en.dist / Math.max(1e-9, spdOf(en)), P0 = Math.max(...U.filter(z => z.kind === "enemy" && num(z.rev) > 0).map(z => num(z.rev)), 0);\n'
    '        const sumLeft = P0 > 0 ? sumT0 + Math.ceil((t + 1e-6 - sumT0) / P0) * P0 - t : Infinity;   // 拉条前【粉墨登场】还要多久\n'
    '        const bossFirst = bossLeft < sumLeft;   // 拉条前谁先轮到，拉条后还是谁先（用户说明）\n'
    '        pull(en, 10000); sumT0 = t;\n'
    '        const due = revQ.filter(q => q.en.gone).map(q => (q.at = t + (bossFirst ? 1e-6 : 0), q.en));   // 主循环里额外回合之后处理；归寂原本在前就排在归寂这次行动之后\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
