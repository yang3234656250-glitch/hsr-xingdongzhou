# 2026-11-19 全页自检（tools/selfchk2.py，没改 tv；可重复运行）：【贪饕】用户给的整理图里的注：
# “贪饕血条回复至满血时，单次攻击的攻击段数再多也无法伤害满血后的贪饕血条；单次攻击的伤害再高，最多把可回复的生命值上限降低至 50%”。
# 页面一次攻击对一个敌人结算一次 hurtEnemy：攻击开始时贪饕血条是满的（生命值 = 可回复上限 − 欢愉负债），这次最多把可回复上限压到 50%。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('let gr = 0; if (en.vmx != null) {', 'let gr = 0; const vFull = en.vmx != null && en.ehc >= en.vmx - debtOf(en) - 1; if (en.vmx != null) {')
rep('const was = en.vmx - debtOf(en); en.vmx = Math.max(0, en.vmx - gr);',
    'const was = en.vmx - debtOf(en); en.vmx = Math.max(vFull ? Math.min(en.vmx, en.ehx * 0.5) : 0, en.vmx - gr);   /* 满血时单次攻击最多压到 50% */')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-19（全页自检，没改 tv；tools/selfchk1.py、selfchk2.py）</b>：所有 99 个角色模板分 25 队，星魂 0 / 6，各放一组按关卡的敌人、开敌我掉血，逐个跑了一遍，再用归寂复刻方案把 14 种手动事件各加一次（电脑 / 手机宽度）。改了：① 归寂「连续行动」的行动轴提示显示成“undefined → 连续行动”；② 伤害提示“× N 个目标”按敌人卡数量写，和实际算伤害用的在场敌人数（比如归寂最后一段只剩它自己）对不上；③ 【贪饕】补上整理图里的注：贪饕血条满血时，一次攻击最多把可回复生命上限压到 50%。tv 149（敌人第 1 批）的工具和日志这次一起补进了 GitHub（之前推送失败，页面已经是 tv 149）。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
