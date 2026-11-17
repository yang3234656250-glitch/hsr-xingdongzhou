# 4.7 王棋归寂：每一管血换成对应形态的出招表（录像：第 1、2 管「成」，第 3、4 管「坏」），
# 「清除存在的球戏」= 再次行动（放完马上再出一招）+ 随机单体陷入【强烈震荡】（按录像反推：行动延后 8%，敌人卡 qxDl 可改；先打 qxWho 指定的，没有就轮到的那个角色）。
# 关卡数据加 phm（每管血的敌人模板名，用 | 分隔——名字里有全角逗号）；旧配置里按关卡放的归寂（有 dice、模板是本体）在模拟时用同样的默认。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
PHM = '万色返空主，归寂•「成」|万色返空主，归寂•「成」|万色返空主，归寂•「坏」|万色返空主，归寂•「坏」'
rep('"phs": "16768365,16768365,31859894,6707346", "dice": 1,'.replace('": ', '":').replace(', "', ',"'),
    ('"phs": "16768365,16768365,31859894,6707346", "phm": "%s", "dice": 1,' % PHM).replace('": ', '":').replace(', "', ',"'))
rep('if (m.dice) u.dice = true;', 'if (m.dice) u.dice = true; if (m.phm) u.phm = m.phm;')
rep('      en.ehx = en.ehc = en.phs[en.ph];   // 欢愉负债不清除（写在阿哈的效果里）\n',
    '      en.ehx = en.ehc = en.phs[en.ph];   // 欢愉负债不清除（写在阿哈的效果里）\n'
    '      { const pm = String(en.phm ??= (en.dice && en.mon === "万色返空主，归寂" ? "%s" : "")).split("|").map(x => x.trim()), mn = pm[en.ph], m2 = mn && MON.m.find(x => x.n === mn);   // 每管血换形态（4.7 归寂：成 / 成 / 坏 / 坏，录像里的名字）：出招表换成这个形态的，接着按回合数轮\n'
    '        if (m2 && m2.n !== en.mon) { en.mon = m2.n; en.__mon = undefined; en.seq = (m2.q || []).slice(); addLog(`${en.name} 变成「${m2.n.split("「")[1] || m2.n}：出招表换成这个形态的`, false, "var(--enemy)"); } }\n' % PHM)
rep('          enemyDebuff(actor, tgs, (actor.skx || {})[skIdx], "sk" + skIdx);\n',
    '          enemyDebuff(actor, tgs, (actor.skx || {})[skIdx], "sk" + skIdx);\n'
    '          if (sk.n === "清除存在的球戏") {   // 4.7 归寂：再次行动（放完马上再出一招）；随机单体陷入【强烈震荡】——按录像反推是行动延后 8%（另外两下攻击各有【滋扰】7.5%），敌人卡 qxDl 可改，先打轮到的那个角色\n'
    '            actor.again = true; const zt = pool.find(x => x.id === actor.qxWho) || main || pool[0];   // 敌人卡 qxWho = 指定被震荡的角色（对录像用）\n'
    '            if (zt) { apply({ id: actor.id + "-qx", type: "delay", target: zt.id, value: num(actor.qxDl ?? 8) }, actor, actor.color); addLog(`${actor.name}【清除存在的球戏】：${zt.name} 陷入【强烈震荡】（行动延后 ${num(actor.qxDl ?? 8)}%，按录像推算），归寂再次行动`, false, "var(--enemy)"); }\n'
    '          }\n')
rep('      actor.zseq = 0; actor.zpre = null;\n',
    '      actor.zseq = 0; actor.zpre = null;\n'
    '      if (actor.again) { actor.again = false; if (!actor.gone) { actor.dist = 0; actor.zpre = -Infinity; marks.push({ t, uid: actor.id, label: "再次行动", color: "var(--enemy)" }); } }   // 「清除存在的球戏」：马上再出一招\n')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/phm47.py）</b>。4.7 王棋归寂：<b>每管血换形态</b>，按录像里血条上的名字：第 1、2 管「成」，第 3、4 管「坏」，转阶段时出招表换成那个形态的（游戏数据），接着按回合数轮。<b>「清除存在的球戏」</b>：归寂<b>再次行动</b>（录像里有「再次行动」字样，放完马上再出一招）；随机一名角色陷入【强烈震荡】，按录像推算是<b>行动延后 8%</b>（录像里真珠被推后约 14 行动值，其中两下攻击的【滋扰】各 7.5%；敌人卡字段 qxDl 可改），先打轮到的那个角色（字段 qxWho 可指定）。录像里第 3 管血的实际出招是 虚无的愉悦 → 球戏 → 收束命运的博弈 → 三重的蔑视 → 球戏 → 令欢愉终归死寂 → 埋梗时刻，和游戏数据的出招表顺序不一样，还没对上。旧配置里的归寂也按这个算。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
