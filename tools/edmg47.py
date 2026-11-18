# 手动事件新类型「额外伤害（随机盲盒等）」：数值 = 伤害（单位万），目标 = 造成伤害的我方角色；扣在第一个在场敌人身上（BOSS）。
# 只在开了“我方伤害扣敌人生命值”时扣血；用来补录像里随机的【头号补给盲盒】这类页面按期望算不准的伤害。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
rep('''        } else apply({ id: ev.id, type: ev.type, target: ev.target, value: ev.value }, null, "var(--accent)");\n        checkUlts();\n''',
    '''        } else if (ev.type === "edmg") {   // 额外伤害（随机盲盒等）：数值单位万，扣第一个在场敌人
          const who = byId[ev.target], en = U.find(z => z.kind === "enemy" && !z.gone), a = num(ev.value) * 1e4;
          addLog(`${who ? who.name : "我方"} 额外伤害 ${num(ev.value)} 万（手动补的，比如随机盲盒）${en ? " → " + en.name : ""}`, false, who ? who.color : "var(--accent)", who ? who.id : undefined);
          if (eHpOn && en && a > 0) hurtEnemy(en, a, who || null);
        } else apply({ id: ev.id, type: ev.type, target: ev.target, value: ev.value }, null, "var(--accent)");\n        checkUlts();\n''')
rep('["bg", "引爆【爆梗】（4.7 王棋归寂）"]], v.type)}', '["bg", "引爆【爆梗】（4.7 王棋归寂）"], ["edmg", "额外伤害（万，随机盲盒等）"]], v.type)}')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/edmg47.py）</b>。手动事件新类型<b>「额外伤害（万）」</b>：目标选造成伤害的角色，数值填多少万，扣在当时第一个在场敌人身上（要开“我方伤害扣敌人生命值”）。用来补录像里随机出的伤害（比如【头号补给盲盒】出得多），页面按期望算的部分不变。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
# 重新登场排在更早的手动事件之后（以前 revQ 先处理，会把时间推到登场时刻，手动事件跟着被推后）
s = open(p, encoding='utf8', newline='').read()
rep('if (revQ[0].at <= next + 1e-9 && revQ[0].at <= END) {', 'if (revQ[0].at <= next + 1e-9 && revQ[0].at <= END && !(ei < evs.length && num(evs[ei].av) < revQ[0].at - 1e-9)) {')
open(p, 'w', encoding='utf8', newline='').write(s)
