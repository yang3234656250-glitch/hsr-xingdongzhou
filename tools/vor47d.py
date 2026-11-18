# 用户：归寂最后一段（贪饕血条）没有喜剧学家 → 转进贪饕血条时喜剧学家全部退场，【粉墨登场】不再召唤，【谐星荟萃】消失。没改 tv；可重复运行。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('''    const reviveEnemy = en => {   // 被消灭的敌人重新登场：满血、减益清空、从头跑条
      if (!en.gone) return;''', '''    let noRev = false;   // 4.7 归寂最后一段（贪饕血条）没有喜剧学家（用户说明）
    const reviveEnemy = en => {   // 被消灭的敌人重新登场：满血、减益清空、从头跑条
      if (!en.gone || noRev) return;''')
rep('''      if (vorOn(en)) { const st = num(en.vorSt, 0);''', '''      if (vorOn(en) && en.dice) {   // 归寂最后一段没有喜剧学家（用户说明）：在场的退场，【粉墨登场】不再召唤
        const out = U.filter(z => z.kind === "enemy" && z !== en && num(z.rev) > 0 && !z.gone); noRev = true; revQ.length = 0; xqAt = null;
        for (const z of out) { z.gone = true; z.ehc = 0; marks.push({ t, uid: z.id, label: "退场", color: "var(--enemy)", from: "" }); }
        addLog(`${en.name} 最后一段（贪饕血条）没有喜剧学家${out.length ? `：${out.length} 个喜剧学家退场` : ""}，【粉墨登场】不再召唤`, false, "var(--enemy)");
      }
      if (vorOn(en)) { const st = num(en.vorSt, 0);''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/vor47d.py）</b>：用户说明：归寂最后一段（贪饕血条）没有喜剧学家。转进这一段时在场的喜剧学家退场，【粉墨登场】不再召唤，【谐星荟萃】消失；伤害全打在归寂身上。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
