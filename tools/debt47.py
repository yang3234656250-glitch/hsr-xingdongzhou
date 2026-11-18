# 【欢愉负债】官方（星神权能·阿哈正传）：造成伤害时额外获得损失生命值 25% 的欢愉负债；阶段转换时保留，最高不超过生命上限 10%。
# 以前把 10% 当成了负债本身的上限。用户截图（第三阶段负债明显超过 10%）。改成：阶段内不封顶，转阶段时保留 min(负债, 10%)。
# vorDebt：贪饕血条上负债要不要继续累积（整理图按开局 10% 固定算），默认不累积。没改 tv；可重复运行。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('''        en.debtP = Math.min(0.1, num(en.debtP) + lost * 0.25 / en.ehx); en.debt = en.debtP * en.ehx;''',
    '''        if (!(en.vmx != null && !en.vorDebt)) { en.debtP = Math.min(1, num(en.debtP) + lost * 0.25 / en.ehx); en.debt = en.debtP * en.ehx; }   // 阶段内不封顶（官方只说转阶段保留最多 10%）；贪饕血条上默认不再累积''')
rep('''      if (ahaU && num(en.debtP) > 0) en.debt = en.debtP * en.ehx;''',
    '''      if (ahaU && num(en.debtP) > 0) { en.debtP = Math.min(0.1, en.debtP); en.debt = en.debtP * en.ehx; }   // 转阶段保留，最高 10%''')
s = s.replace('（最多生命上限 10%，转阶段时按比例保留）', '（阶段内不封顶；转阶段时保留，最多生命上限 10%）')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/debt47.py）</b>：修正<b>【欢愉负债】</b>上限。官方（星神权能·阿哈正传）：造成伤害时额外获得损失生命值 25% 的欢愉负债，<b>阶段转换时</b>保留、最高不超过生命上限 10%。以前把 10% 当成负债本身的上限；用户截图第三阶段负债明显超过 10%。现在阶段内不封顶，转阶段只带 10% 过去；贪饕血条上不再累积（整理图按开局 10% 算）。<b>对已有配置</b>：负债从上面占生命上限，正常打的时候生命值本来就在它下面，所以模拟结果基本不变（4 组模板队伍、归寂这一场都没变）；日志里的负债数会变大。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
