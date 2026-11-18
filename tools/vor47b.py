# 【贪饕侵蚀】改按 B 站“逻忆央的远方”《崩铁贪饕污染4机制解析》的整理（用户提供截图）：
# 欢愉伤害：原伤害 ×4，其中 1 份是看得见的伤害（红血），多出的 3 份变成灰血（压掉的生命上限）；非欢愉 ×2，1 份红血 1 份灰血。
# 4 级：灰血至少 77%（欢愉负债也算进去，“有阿哈仍然是 100%”）才能消灭；红血打空前灰血不够就回满（红血 = 生命上限 − 灰血 − 负债）。
# 没改 tv；可重复运行（在 vor47.py 之后）。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('''    const hurtEnemy = (en, a, killer) => { if (!en || en.gone || !(en.ehx > 0) || !(a > 0)) return;
      const lost''', '''    const hurtEnemy = (en, a, killer) => { if (!en || en.gone || !(en.ehx > 0) || !(a > 0)) return;
      let gr = 0; if (en.vmx != null) { const r = (curEl ? num(en.vorRe, 75) : num(en.vorR, 50)) / 100, m = 1 / Math.max(0.01, 1 - r); gr = a * (m - 1); a *= m; }   // 【贪饕】欢愉伤害 ×4（3 份变灰血），其他 ×2（1 份变灰血）
      const lost''')
rep('''      if (en.vmx != null) { const r = curEl ? num(en.vorRe, 75) : num(en.vorR, 50), was = en.vmx; en.vmx = Math.max(0, en.vmx - a * r / 100); const th = num(en.vorAt, 25) / 100 * en.ehx;   // 【贪饕】每次伤害压制生命上限
        if (was > th && en.vmx <= th) {''', '''      if (en.vmx != null) { const was = en.vmx - debtOf(en); en.vmx = Math.max(0, en.vmx - gr); const th = num(en.vorAt, 23) / 100 * en.ehx;   // 【贪饕】灰血：压掉的生命上限
        if (was > th && en.vmx - debtOf(en) <= th) {''')
s = s.replace('生命上限被压制到 ${num(en.vorAt, 25)}% 以下：之后生命值打空就会被消灭', '灰血（含欢愉负债）达到 ${100 - num(en.vorAt, 23)}%：之后生命值打空就会被消灭')
rep('''if (en.vmx != null && en.vmx > num(en.vorAt, 25) / 100 * en.ehx + 1e-6) { vorRevive(en); return; }''',
    '''if (en.vmx != null && en.vmx - debtOf(en) > num(en.vorAt, 23) / 100 * en.ehx + 1e-6) { vorRevive(en); return; }''')
s = s.replace('（生命上限已被压制到 ${fmt(en.vmx / en.ehx * 100, 1)}%，压到 ${num(en.vorAt, 25)}% 以下才能消灭）', '（灰血含欢愉负债 ${fmt(100 - (en.vmx - debtOf(en)) / en.ehx * 100, 1)}%，要 ${100 - num(en.vorAt, 23)}% 才能消灭；回满后生命值 ${fmt(en.ehc / en.ehx * 100, 1)}%）')
rep('''if (vorOn(en)) { const st = num(en.vorSt, 70); en.vmx = st > 0 ? st / 100 * en.ehx : en.ehx; en.ehc = Math.min(en.ehc, en.vmx);   // 【贪饕侵蚀】最后一管血：生命上限降到 vorSt%（录像 70%），之后按伤害压制''',
    '''if (vorOn(en)) { const st = num(en.vorSt, 0); en.vmx = en.ehx; if (st > 0) en.ehc = Math.min(en.ehc, st / 100 * en.ehx);   // 【贪饕侵蚀】最后一管血：伤害按 ×4 / ×2 打红血，多出的变灰血；vorSt = 手动指定开始 %''')
s = s.replace("最后一管血从 ${fmt(en.ehc / en.ehx * 100, 1)}% 开始；之后每次伤害额外压制生命上限（欢愉伤害 ${num(en.vorRe, 75)}%，其他 ${num(en.vorR, 50)}%），压到 ${num(en.vorAt, 25)}% 以下才能被消灭，之前受到致命伤害会回满",
              "最后一管血从 ${fmt(en.ehc / en.ehx * 100, 1)}% 开始；欢愉伤害 ×4（3 份变灰血）、其他 ×2（1 份变灰血），灰血（含欢愉负债）到 ${100 - num(en.vorAt, 23)}% 才能被消灭，之前受到致命伤害会回满")
s = s.replace('title="生命上限压到百分之几以下才能消灭（血条上的标记；归寂 25%）">压到 <input type="number" id="vat-${u.id}" min="0" max="100" step="1" value="${u.vorAt ?? ""}" placeholder="25"',
              'title="生命上限压到百分之几以下才能消灭（血条上的标记 = 100% − 灰血最低要求；侵蚀 4 级灰血 77%，即 23%）">压到 <input type="number" id="vat-${u.id}" min="0" max="100" step="1" value="${u.vorAt ?? ""}" placeholder="23"')
s = s.replace('title="最后一管血从百分之几开始（录像：归寂 70%）；0 = 不限制">开始 <input type="number" id="vst-${u.id}" min="0" max="100" step="1" value="${u.vorSt ?? ""}" placeholder="70"',
              'title="手动指定最后一管血从百分之几开始；空 = 按机制算">开始 <input type="number" id="vst-${u.id}" min="0" max="100" step="1" value="${u.vorSt ?? ""}" placeholder="自动"')
s = s.replace('每次伤害额外压制生命上限（欢愉伤害 75%，其他 50%，玩家 wiki），压到标记以下才能消灭；回满不清除欢愉负债"',
              '欢愉伤害按 ×4 打（3 份变灰血 = 压掉的生命上限），其他 ×2（1 份变灰血）；灰血（含欢愉负债）到 77% 才能消灭；回满不清除欢愉负债（B 站逻忆央的远方的整理）"')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/vor47b.py）</b>：核对上一条【贪饕侵蚀】，按用户给的 B 站《崩铁贪饕污染4机制解析》（逻忆央的远方）改：“灰血转化率”75% / 50% 不是“额外压掉伤害的 75%”，而是<b>欢愉伤害按 ×4 打、其中 3 份变灰血</b>（多出的不显示数字），<b>非欢愉 ×2、1 份变灰血</b>；侵蚀 4 级灰血最低 77%（欢愉负债也算，所以有阿哈时欢愉伤害只要打 100%），没到就回满。去掉了上一版“从 70% 开始”的假设（开始 % 留空 = 按机制算，也可以手填）。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
