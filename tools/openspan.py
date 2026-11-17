# 模拟中结算伤害（我方伤害扣敌人生命值）时，银狼当前这段还没结束的【无敌玩家】不在 spans 里（spans 只在退出时记），
# 所以结算期间：阿哈时刻里银狼的【崩坏级伤害演示】被当成结界外（没伤害）、1 魂“结界中的敌人受到伤害 +20%”等按结界判断的都不算。
# 阿哈时刻的伤害还缓存在 rec.__el 上，结算后没清，行动轴 / 表格也一直显示漏掉银狼的那份。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('      const keep = R_REF; R_REF = { actions, marks, ultMarks, punch, scoreH, log, spans, dots: dotRecs, heal: healTot, END };',
    '      // 当前还没结束的无敌玩家也算进 spans（结界内的判断：银狼欢愉技、1 魂易伤等）\n'
    '      const keep = R_REF; R_REF = { actions, marks, ultMarks, punch, scoreH, log, spans: spansNow(), dots: dotRecs, heal: healTot, END };')
rep('        R_REF = { actions, marks, ultMarks, punch, scoreH, log, spans, dots: dotRecs, heal: healTot, END, bgUse };',
    '        R_REF = { actions, marks, ultMarks, punch, scoreH, log, spans: spansNow(), dots: dotRecs, heal: healTot, END, bgUse };')
rep('      const one = (rec, f) => { try { return f(); } catch (e) { return null; } finally { delete rec.__dmg; } };',
    '      const one = (rec, f) => { try { return f(); } catch (e) { return null; } finally { delete rec.__dmg; delete rec.__el; } };')
# spansNow 定义：放在 sw 定义之后（swRe 那段前面）
rep('    // 强化普攻被打断（打到转阶段 / 全部打倒）后等着再次施放的：{ re: 剩下的比例, sc: 施放时的隐藏分 }',
    '    const spansNow = () => sw.inUlt ? [...spans, { a: sw.from, b: END, open: true }] : spans;   // 模拟中途：当前这段无敌玩家还没记进 spans\n'
    '    // 强化普攻被打断（打到转阶段 / 全部打倒）后等着再次施放的：{ re: 剩下的比例, sc: 施放时的隐藏分 }')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（修正，没改 tv；tools/openspan.py）</b>。开了“我方伤害扣敌人生命值”时，模拟中途结算伤害看不到银狼<b>还没结束的那段无敌玩家</b>（以前只在退出时才记下来），所以无敌玩家期间：阿哈时刻里银狼的【崩坏级伤害演示】没算伤害、1 魂“结界中的敌人受到伤害 +20%”这类按结界判断的都没算，敌人掉血偏少；阿哈时刻的伤害还被缓存住，行动轴和表格里也一直少了银狼那份。拿 4.7 王棋录像对出来的（录像里 58 行动值那次阿哈时刻约 305 万，页面以前只有 138 万）。对已有配置：有银狼的队伍在无敌玩家期间的阿哈时刻伤害变高；开了敌人生命值时敌人掉血变快。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
