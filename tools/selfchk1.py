# 2026-11-19 全页自检（tools/selfchk1.py，没改 tv；可重复运行）：
# 1) 归寂「连续行动」标记没写 from，行动轴提示里显示成“undefined → 连续行动”；渲染时 from 为空就只写标签。
# 2) 伤害提示的“× N 个目标”用的是敌人卡数量（enemyCount），实际伤害按当时在场的敌人算（r.targets），两者不一致时提示写错。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('marks.push({ t, uid: actor.id, label: "连续行动", color: "var(--enemy)" })', 'marks.push({ t, uid: actor.id, label: "连续行动", color: "var(--enemy)", from: "" })', 2)
rep('''      if (prev) { prev.label += " " + m.label; prev.tips.push(`${esc(m.from)} → ${m.label}`); continue; }
      MK.push(Object.assign({}, m, { tips: [`${esc(m.from)} → ${m.label}`] }));''', '''      const tip = `${m.from ? esc(m.from) + " → " : ""}${m.label}`;
      if (prev) { prev.label += " " + m.label; prev.tips.push(tip); continue; }
      MK.push(Object.assign({}, m, { tips: [tip] }));''')
rep('const mtxt = r.tg === 3 ? `倍率 ${fmt(r.v * 100, 1)}% × ${enemyCount()} 个目标`', 'const mtxt = r.tg === 3 ? `倍率 ${fmt(r.v * 100, 1)}% × ${r.targets || enemyCount()} 个目标`')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
