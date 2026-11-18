# 4.7 王棋归寂：【贪饕侵蚀】（Voracity Corrosion）最后一管血。没改 tv；可重复运行。
# 官方：受到致命伤害不会被消灭，立即回复一定比例生命值；造成伤害持续压制生命上限，压到一定比例后才能彻底消灭。
# 玩家 wiki：每次伤害额外压制 50% 的生命上限，侵蚀 3/4 级受到欢愉伤害时 75%；回血不清除欢愉负债；压到血条标记以下就不再复活。
# 用户：这关标记在 25%；录像里最后一管血从 70% 开始。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# 1) 伤害是不是欢愉伤害
rep('''    const hurtEnemy = (en, a, killer) => { if (!en || en.gone || !(en.ehx > 0) || !(a > 0)) return;''',
    '''    let curEl = false;   // 当前这笔伤害是不是欢愉伤害（【贪饕】欢愉伤害压制更多）
    const vorOn = en => (en.vor ?? !!en.dice) && en.phs && en.ph === en.phs.length - 1;
    const vorRevive = en => {   // 【贪饕】：生命上限还没压到标记以下，受到致命伤害不会被消灭，回满（不清除欢愉负债）
      en.ehc = Math.max(1, en.vmx - debtOf(en)); en.vorN = num(en.vorN) + 1;
      marks.push({ t, uid: en.id, label: "贪饕回满", color: "var(--enemy)", from: "" });
      addLog(`${en.name}【贪饕】受到致命伤害没有被消灭，回满生命值（生命上限已被压制到 ${fmt(en.vmx / en.ehx * 100, 1)}%，压到 ${num(en.vorAt, 25)}% 以下才能消灭）`, false, "var(--enemy)");
    };
    const hurtEnemy = (en, a, killer) => { if (!en || en.gone || !(en.ehx > 0) || !(a > 0)) return;''')
rep('''      if (en.ehc <= 1e-6) { endBar(en, killer); return; }
      if (ahaU) {''',
    '''      if (en.vmx != null) { const r = curEl ? num(en.vorRe, 75) : num(en.vorR, 50), was = en.vmx; en.vmx = Math.max(0, en.vmx - a * r / 100); const th = num(en.vorAt, 25) / 100 * en.ehx;   // 【贪饕】每次伤害压制生命上限
        if (was > th && en.vmx <= th) { marks.push({ t, uid: en.id, label: "贪饕压制", color: "var(--enemy)", from: killer ? killer.name : "" }); addLog(`${en.name}【贪饕】生命上限被压制到 ${num(en.vorAt, 25)}% 以下：之后生命值打空就会被消灭`, false, "var(--enemy)"); } }
      if (en.ehc <= 1e-6) { if (en.vmx != null && en.vmx > num(en.vorAt, 25) / 100 * en.ehx + 1e-6) { vorRevive(en); return; } endBar(en, killer); return; }
      if (en.vmx != null && en.ehc > en.vmx - (ahaU ? debtOf(en) : 0)) en.ehc = Math.max(0, en.vmx - (ahaU ? debtOf(en) : 0));
      if (ahaU) {''')
rep('''        const cap = en.ehx - debtOf(en); if (en.ehc > cap) en.ehc = cap;''',
    '''        const cap = (en.vmx ?? en.ehx) - debtOf(en); if (en.ehc > cap) en.ehc = cap;''')
# 2) 转进最后一管血时开启
rep('''      if (ahaU) en.ehc = Math.min(en.ehc, en.ehx - debtOf(en));\n''',
    '''      if (ahaU) en.ehc = Math.min(en.ehc, en.ehx - debtOf(en));
      if (vorOn(en)) { const st = num(en.vorSt, 70); en.vmx = st > 0 ? st / 100 * en.ehx : en.ehx; en.ehc = Math.min(en.ehc, en.vmx);   // 【贪饕侵蚀】最后一管血：生命上限降到 vorSt%（录像 70%），之后按伤害压制
        addLog(`${en.name} 激活【贪饕】的力量：最后一管血从 ${fmt(en.ehc / en.ehx * 100, 1)}% 开始；之后每次伤害额外压制生命上限（欢愉伤害 ${num(en.vorRe, 75)}%，其他 ${num(en.vorR, 50)}%），压到 ${num(en.vorAt, 25)}% 以下才能被消灭，之前受到致命伤害会回满`, false, "var(--enemy)"); }\n''')
# 3) 标记欢愉伤害
rep('''        if (!d || !(d.total > 0)) return;
        const w = SU[uid]''', '''        if (!d || !(d.total > 0)) return;
        curEl = !!(d.el || d.b2el || num(d.bg) > 0 || num(d.punch) > 0);
        const w = SU[uid]''')
rep('''if (tA > 0) { const L = U.filter(z => z.kind === "enemy" && !z.gone && z.ehx > 0); for (const z of L)''',
    '''if (tA > 0) { curEl = false; const L = U.filter(z => z.kind === "enemy" && !z.gone && z.ehx > 0); for (const z of L)''')
rep('''          if (eHpOn && en && a > 0) hurtEnemy(en, a, who || null);''',
    '''          if (eHpOn && en && a > 0) { curEl = true; hurtEnemy(en, a, who || null); }''')
# 4) 敌人卡
rep('''data-f="lastR">最后一管血按 R</label>''',
    '''data-f="lastR">最后一管血按 R</label><label for="vor-${u.id}" title="【贪饕侵蚀】（4.5 起，4.7 王棋隐藏关卡侵蚀 4 级）：最后一管血受到致命伤害不会被消灭而是回满；每次伤害额外压制生命上限（欢愉伤害 75%，其他 50%，玩家 wiki），压到标记以下才能消灭；回满不清除欢愉负债"><input type="checkbox" id="vor-${u.id}" ${(u.vor ?? !!u.dice) ? "checked" : ""} data-u="${i}" data-f="vor">贪饕</label>${(u.vor ?? !!u.dice) ? `<label for="vat-${u.id}" title="生命上限压到百分之几以下才能消灭（血条上的标记；归寂 25%）">压到 <input type="number" id="vat-${u.id}" min="0" max="100" step="1" value="${u.vorAt ?? ""}" placeholder="25" data-u="${i}" data-f="vorAt" style="width:48px">%</label><label for="vst-${u.id}" title="最后一管血从百分之几开始（录像：归寂 70%）；0 = 不限制">开始 <input type="number" id="vst-${u.id}" min="0" max="100" step="1" value="${u.vorSt ?? ""}" placeholder="70" data-u="${i}" data-f="vorSt" style="width:48px">%</label>` : ""}''', 2)
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/vor47.py）</b>：4.7 王棋归寂最后一管血加<b>【贪饕侵蚀】</b>。依据：官方 4.5 更新说明（受到致命伤害不会被消灭而是回复一定比例生命值，伤害持续压制生命上限，压到一定比例后才能彻底消灭）；玩家 wiki（每次伤害额外压制 50% 生命上限，侵蚀 3/4 级受到欢愉伤害 75%；回满不清除欢愉负债）；这关侵蚀 4 级；用户：标记在 25%，录像里最后一管血从 70% 开始。页面做法：转进最后一管血时生命上限降到 70%，之后每次伤害按上面的比例压制，压到 25% 以下前生命值打空会回满。敌人卡上“贪饕”勾选框（归寂默认开）和“压到 / 开始”两个数。<b>对已有配置</b>：只影响勾了“掷骰子”的归寂的最后一管血，其他敌人不变。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
