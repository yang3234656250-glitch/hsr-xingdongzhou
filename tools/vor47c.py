# 【贪饕污染】按用户给的整理图（贪饕污染说明 + 数值速查表）补：污染 4 级多阶段怪物的贪饕血条 = 原血量（最后一条正常血）的 216%，
# 可回复生命上限降到 23% 后才能消灭；欢愉伤害 1:3、非欢愉 1:1（已在 vor47b）；击杀贪饕血条时灰血不够 → 截断攻击、回复到当前灰血处。
# 录像核对：214 那一波显示掉 38%，按 216% × 31859894 和 ×4 正好约 650 万欢愉伤害，和页面算的一致（按 nanoka 的 ×2.48 = 6707346 会差 10 倍）。没改 tv；可重复运行。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('''      en.ehx = en.ehc = en.phs[en.ph];   // 欢愉负债不清除（写在阿哈的效果里）\n''',
    '''      en.ehx = en.ehc = en.phs[en.ph];   // 欢愉负债不清除（写在阿哈的效果里）
      if (vorOn(en) && en.ph > 0) { const vh = num(en.vorHp, 216); if (vh > 0) en.ehx = en.ehc = en.phs[en.ph - 1] * vh / 100; }   // 【贪饕】污染 4 级多阶段怪物：贪饕血条 = 上一条（最后一条正常血）的 216%（用户给的整理图）；填 0 = 用分阶段里写的\n''')
s = s.replace('''addLog(`${en.name} 激活【贪饕】的力量：最后一管血从''', '''addLog(`${en.name} 激活【贪饕】的力量：贪饕血条 ${Math.round(en.ehx)}，从''')
s = s.replace('''title="手动指定最后一管血从百分之几开始；空 = 按机制算">开始''', '''title="贪饕血条是上一条血的百分之几（污染 4 级多阶段 216%、非多阶段 120%；3 级 144% / 80%；填 0 = 用分阶段里写的最后一条）">血条 <input type="number" id="vhp-${u.id}" min="0" step="1" value="${u.vorHp ?? ""}" placeholder="216" data-u="${i}" data-f="vorHp" style="width:52px">%</label><label for="vst-${u.id}" title="手动指定最后一管血从百分之几开始；空 = 按机制算">开始''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/vor47c.py）</b>：【贪饕】血量按用户给的《贪饕污染说明》整理图：污染 4 级多阶段怪物的贪饕血条 = 最后一条正常血的 <b>216%</b>（非多阶段 120%；3 级 144% / 80%），可回复生命上限降到 23% 才能消灭。归寂最后一条从 6707346 变成 31859894 × 216% ≈ 6882 万（敌人卡“血条 %”可改，填 0 = 用分阶段里写的）。核对录像：214 那一波血条掉 38%，按 6882 万 × 4 倍约 650 万欢愉伤害，和页面算的一致。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
