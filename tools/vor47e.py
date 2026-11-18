# 用户：【贪饕】是直接回满血，不转阶段。→ 进入贪饕血条时不做转阶段的事：秘技不再触发、形态不换、减益不清、韧性不回、
# 不【转面】拉条、不掷骰子（收束命运的博弈）、欢愉负债按比例原样保留（不再截到 10%）。按 R 和喜剧学家退场照旧。没改 tv；可重复运行。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('''      if (vorOn(en) && en.ph > 0) { const vh''', '''      const vr = vorOn(en);   // 进入【贪饕】血条：直接回满，不转阶段（用户说明）
      if (vr && en.ph > 0) { const vh''')
rep('''      techAgain(en);\n      { const pm = String(en.phm''', '''      if (!vr) techAgain(en);\n      if (!vr) { const pm = String(en.phm''')
rep('''      en.buffs = []; en.dots = []; en.wk = []; en.st = {}; en.frozen = false; en.cmz = null; en.cmzUsed = false; en.yh = 0;   // 敌人身上的减益''', '''      if (!vr) { en.buffs = []; en.dots = []; en.wk = []; en.st = {}; en.frozen = false; en.cmz = null; en.cmzUsed = false; en.yh = 0;   // 敌人身上的减益''')
rep('''      en.broken = false; en.tcur = toughMax(en);   // 韧性回满''', '''      en.broken = false; en.tcur = toughMax(en); }   // 韧性回满（贪饕回满不转阶段：减益、韧性不变）''')
rep('''      marks.push({ t, uid: en.id, label: "转阶段", color: "var(--enemy)", from: killer ? killer.name : "" });\n      if (en.tf ?? en.dice) {''',
    '''      marks.push({ t, uid: en.id, label: vr ? "贪饕回满" : "转阶段", color: "var(--enemy)", from: killer ? killer.name : "" });\n      if (!vr && (en.tf ?? en.dice)) {''')
rep('''      if (en.dice && byId.aha) { pendingAha.push''', '''      if (!vr && en.dice && byId.aha) { pendingAha.push''')
rep('''if (ahaU && num(en.debtP) > 0) { en.debtP = Math.min(0.1, en.debtP);''', '''if (ahaU && num(en.debtP) > 0) { if (!vr) en.debtP = Math.min(0.1, en.debtP);''')
rep('''      addLog(`${en.name} 第 ${old} 阶段生命值打空，转入第''', '''      if (!vr) addLog(`${en.name} 第 ${old} 阶段生命值打空，转入第''')
s = s.replace('''addLog(`${en.name} 激活【贪饕】的力量：贪饕血条 ${Math.round(en.ehx)}，从''', '''addLog(`${en.name} 第 ${old} 条血打空，激活【贪饕】的力量：不转阶段，直接回满（减益、韧性、形态都不变${ahaU && num(en.debtP) > 0 ? `，欢愉负债按比例保留 ${fmt(en.debtP * 100, 1)}%` : ""}）；贪饕血条 ${Math.round(en.ehx)}，从''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/vor47e.py）</b>：用户说明：【贪饕】是<b>直接回满血、不转阶段</b>。所以进入贪饕血条时不再触发秘技、不换形态、不清减益、不回韧性、不【转面】拉条、不掷骰子给阿哈时刻；欢愉负债按比例原样带过去（不截到 10%）。按 R 和喜剧学家退场照旧。归寂这一场：第三条血打完时负债约 30%，贪饕血条从约 70% 开始，和录像一致。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
