# 用户说明：每一波喜剧学家被召唤时，【谐星荟萃】重新从头跑条（第一波 0 召唤 → 45；第一波被打死后 65.88 召唤的第二波 → 111）；整波死光就没有这个行动。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('    const reviveEnemy = en => {   // 被消灭的敌人重新登场：满血、减益清空、从头跑条\n      if (!en.gone) return;\n',
    '    const reviveEnemy = en => {   // 被消灭的敌人重新登场：满血、减益清空、从头跑条\n      if (!en.gone) return;\n'
    '      if (en.xqOn && !U.some(z => z.xqOn && !z.gone)) xqAt = t + 10000 / xqSpd;   // 新的一波喜剧学家：【谐星荟萃】从头跑条\n')
rep('const xqSpd = XQ.length ? num(XQ[0].xqS, 220) : 0; let xqAt = XQ.length && xqSpd > 0 ? 10000 / xqSpd : null;',
    'const xqSpd = XQ.length ? num(XQ[0].xqS, 220) : 0; let xqAt = XQ.length && xqSpd > 0 && XQ.some(z => !z.gone) ? 10000 / xqSpd : null;')
# 整波死光：killEnemy 里 en.gone = true 那一行之后
i = s.index('    const killEnemy = (en, killer) => {')
if 'xqAt = null' not in s[i:i+3000]:
    j = s.index('\r\n', i) + 2; k = s.index('\r\n', j) + 2
    s = s[:k] + '      if (en.xqOn && !U.some(z => z.xqOn && !z.gone)) xqAt = null;   // 这一波喜剧学家全被消灭：【谐星荟萃】从行动序列上消失\r\n' + s[k:]
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
