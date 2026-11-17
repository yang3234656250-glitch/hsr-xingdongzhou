# 战斗开始时的效果按 3 轮生效：先所有人“先生效”的（pre），再其他的，最后“进战自动施放”（cast）；4.7 王棋【阿哈帮大忙了】速度 +12 改成先生效（可重复运行）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('    for (const u of U) for (const e of fx(u, "start")) apply(e, u, u.color);\r\n    checkPunchE();',
    '    {   // 战斗开始：先所有人“先生效”的（阿哈帮大忙了的速度、治疗加成等），再其他被动，最后“进战自动施放战技”（爻光秘技），这样按速度 / 欢愉度算的效果拿到的是进战后的数值\r\n'
    '      const S0 = U.map(u => [u, fx(u, "start")]);\r\n'
    '      for (const [u, L] of S0) for (const e of L) if (preEff(e) && e.type !== "cast") apply(e, u, u.color);\r\n'
    '      for (const [u, L] of S0) for (const e of L) if (!preEff(e) && e.type !== "cast") apply(e, u, u.color);\r\n'
    '      for (const [u, L] of S0) for (const e of L) if (e.type === "cast") apply(e, u, u.color);\r\n'
    '    }\r\n    checkPunchE();')
for f in (p, 'tools/stg47fx.py'):
    pass
a = '{ trigger: "start", type: "spd", mode: "flat", value: 12, duration: 0, note: "关卡·阿哈帮大忙了（敌人有贪饕时）：速度 +12" },'
b = '{ trigger: "start", type: "spd", mode: "flat", value: 12, duration: 0, pre: true, note: "关卡·阿哈帮大忙了（敌人有贪饕时）：速度 +12" },'
if a in s: s = s.replace(a, b)
open(p, 'w', encoding='utf8', newline='').write(s)
t = open('tools/stg47fx.py', encoding='utf8').read()
if a in t: open('tools/stg47fx.py', 'w', encoding='utf8').write(t.replace(a, b))
