# 用户截图（133.06）：银狼最后一次强普被打断时，页面先写“无敌玩家结束，隐藏分清空”，再结算伤害、转阶段，最后才写“获得额外回合再次施放剩下的部分”，
# 而且再次施放时已经不在无敌玩家里了。改成：
# 1) 最后一次强普扣完次数后先不结束，等这次伤害结算完（主循环 settleDmg 之后）；被打断就等再次施放打完再结束。
# 2) 打断的日志 / 额外回合排在转阶段之前（技能结束 → 获得额外回合 → 转阶段 → 再次施放）。没改 tv；可重复运行。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('''      sw.left--;
      if (sw.left > 0) return;
      sw.inUlt = false;''', '''      sw.left--;
      if (sw.left > 0) return;
      sw.endP = true;   // 等这次强普的伤害结算完（被打断就等再次施放打完）再结束无敌玩家
    };
    const swEnd = () => {
      if (!sw.endP) return; sw.endP = false;
      if (sw.left > 0) return;   // 期间 2 魂又加了强普次数：继续
      sw.inUlt = false;''')
rep('''      if (sw.inUlt) { stats.fails++; addLog(`${where}，${swU.name} 开大失败：还在无敌玩家状态''',
    '''      if (sw.inUlt && sw.endP && !swRe.length) swEnd();   // 最后一次强普已经打完
      if (sw.inUlt) { stats.fails++; addLog(`${where}，${swU.name} 开大失败：还在无敌玩家状态''')
rep('''    while (guard++ < 3000 && U.length) {
      settleDmg();\n''', '''    while (guard++ < 3000 && U.length) {
      settleDmg();
      if (sw.endP && !swRe.length) { swEnd(); checkUlts(); }   // 银狼最后一次强普（含被打断后再次施放的）结算完：无敌玩家结束\n''')
# 打断：先记额外回合，再转阶段
rep('''        for (const z of pend) if (!z.gone) hurtEnemy(z, Math.max(0, z.ehc) + 1e-6, killer);   // 技能结束：转阶段
        if (!why || !U.some(z => z.kind === "enemy" && !z.gone)) return;   // 没打断，或者已经没有可攻击的敌人（战斗结束）
        const f = left / d.total; rec.cut = f;''', '''        if (why && U.some(z => z.kind === "enemy" && !z.gone)) {   // 打断（转阶段的还在场）：技能结束 → 获得额外回合 → 转阶段 → 再次施放
        const f = left / d.total; rec.cut = f;''')
rep('''获得 1 个额外回合再次施放剩下的部分${n ? `；自身 ${n} 个增益延长 1 回合` : ""}`, false, swU.c''', '''获得 1 个额外回合再次施放剩下的部分${n ? `；自身 ${n} 个增益延长 1 回合` : ""}`, false, swU.c''')
i = s.index('获得 1 个额外回合再次施放剩下的部分${n ?'); j = s.index('\n', i)
if 'for (const z of pend) if (!z.gone) hurtEnemy(z, Math.max(0, z.ehc) + 1e-6, killer);   // 技能结束后转阶段' not in s:
    s = s[:j+1] + '''        }
        for (const z of pend) if (!z.gone) hurtEnemy(z, Math.max(0, z.ehc) + 1e-6, killer);   // 技能结束后转阶段\r\n''' + s[j+1:]
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/swend47.py）</b>：用户截图（133.06）指出顺序不对：银狼最后一次强普被打断时，以前先“无敌玩家结束、隐藏分清空”，再转阶段，再次施放剩下的部分时已经不在无敌玩家里。现在：最后一次强普的伤害结算完才结束无敌玩家；被打断就按“技能结束 → 获得额外回合 → 转阶段 → 再次施放剩下的部分 → 无敌玩家结束”。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
