# 4.7 王棋：喜剧学家被消灭后按【粉墨登场】周期重新登场（rev）；关卡效果【滋扰】敌人攻击后被打的角色行动延后（zr）。可重复运行
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\n', '\r\n'); b = b.replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# 1) 敌人卡：重新登场周期（开伤害扣血时）、滋扰
rep('data-f="dice">转阶段骰子选阿哈时刻</label>',
    'data-f="dice">转阶段骰子选阿哈时刻</label><label for="rv-${u.id}" title="被消灭后在下一个“周期的整数倍”行动值重新登场（满血、减益清空、从头跑条）。4.7 王棋的喜剧学家：【粉墨登场】速度 115 × 1.32 = 151.8，每 65.9 行动值召唤一次（第一次在 0）。不填 = 不会重新登场。召唤出来的敌人在主要敌人都被消灭后一起消失">被消灭后每 <input type="number" id="rv-${u.id}" min="0" step="0.1" value="${u.rev ?? ""}" data-u="${i}" data-f="rev" style="width:64px"> 行动值重新登场</label>', 2)
rep('u.atkWho || "")}</select></label>',
    'u.atkWho || "")}</select></label>${u.atkWho ? `<label for="zr-${u.id}" title="关卡效果【滋扰】：敌方目标施放攻击后，对攻击目标随机造成 5% 或 10% 的行动延后（绝境 5% / 20%）。模拟按固定值算，默认填期望 7.5；想算最坏情况填 10。不填 = 没有">攻击后被打的角色行动延后 <input type="number" id="zr-${u.id}" min="0" step="0.5" value="${u.zr ?? ""}" data-u="${i}" data-f="zr" style="width:56px"> %（滋扰）</label>` : ""}')
rep('      if (f === "phs") { u.phs = String(el.value || "").replace(/[^0-9.,，\\s\\/]/g, "").trim(); if (!u.phs) delete u.phs; }   // 分阶段生命值',
    '      if (f === "phs") { u.phs = String(el.value || "").replace(/[^0-9.,，\\s\\/]/g, "").trim(); if (!u.phs) delete u.phs; }   // 分阶段生命值\n'
    '      if ((f === "rev" || f === "zr") && !(num(el.value) > 0)) delete u[f];   // 重新登场周期 / 滋扰：清空 = 没有')
# 2) 模拟：重新登场
rep('    const killEnemy = (en, killer) => {\n      en.ehc = 0; en.gone = true;',
    '    const revQ = [];   // 等着重新登场的敌人（【粉墨登场】）\n'
    '    const killEnemy = (en, killer) => {\n      en.ehc = 0; en.gone = true; if (num(en.rev) > 0) { const P = num(en.rev); revQ.push({ at: Math.ceil((t + 1e-6) / P) * P, en }); }')
rep('    const ahaU = U.find(z => z.kind === "ally" && !z.sm && tidOf(z) === "1511");   // 星神★阿哈在队：【欢愉负债】',
    '    const ahaU = U.find(z => z.kind === "ally" && !z.sm && tidOf(z) === "1511");   // 星神★阿哈在队：【欢愉负债】\n'
    '    const reviveEnemy = en => {   // 被消灭的敌人重新登场：满血、减益清空、从头跑条\n'
    '      if (!en.gone) return;\n'
    '      en.gone = false; en.dist = 10000; en.ehc = aha6 ? en.ehx * 0.8 : en.ehx; en.debt = 0; en.debtP = 0;\n'
    '      en.buffs = []; en.dots = []; en.wk = []; en.st = {}; en.frozen = false; en.cmz = null; en.cmzUsed = false; en.yh = 0; en.broken = false; en.tcur = toughMax(en);\n'
    '      marks.push({ t, uid: en.id, label: "重新登场", color: "var(--enemy)", from: "" });\n'
    '      addLog(`${en.name} 重新登场（每 ${fmt(num(en.rev), 1)} 行动值一次；生命值 ${Math.round(en.ehc)}）`, false, "var(--enemy)");\n'
    '    };')
rep('      if (eHpOn && U.some(z => z.kind === "enemy") && !U.some(z => z.kind === "enemy" && !z.gone)) { addLog(`行动值 ${fmt(t)}：敌人全部被消灭，战斗结束`, false); break; }',
    '      if (eHpOn && U.some(z => z.kind === "enemy") && !U.some(z => z.kind === "enemy" && !z.gone && !(num(z.rev) > 0 && U.some(y => y.kind === "enemy" && !(num(y.rev) > 0))))) {   // 会重新登场的（召唤出来的）在主要敌人都被消灭后一起消失\n'
    '        const left = U.filter(z => z.kind === "enemy" && !z.gone); for (const z of left) z.gone = true;\n'
    '        addLog(`行动值 ${fmt(t)}：敌人全部被消灭，战斗结束${left.length ? `（召唤出来的${[...new Set(left.map(z => z.name))].join("、")}随之消失）` : ""}`, false); break; }')
rep('      const next = t + best;\n      if (ei < evs.length',
    '      const next = t + best;\n'
    '      if (revQ.length) { revQ.sort((a, b) => a.at - b.at); if (revQ[0].at <= next + 1e-9 && revQ[0].at <= END) { const rq = revQ.shift(), at = Math.max(t, rq.at); move(at - t); t = at; reviveEnemy(rq.en); checkUlts(); continue; } }\n'
    '      if (ei < evs.length')
# 3) 模拟：滋扰
rep('          enemyDebuff(actor, tgs, (actor.skx || {})[skIdx], "sk" + skIdx);',
    '          enemyDebuff(actor, tgs, (actor.skx || {})[skIdx], "sk" + skIdx);\n'
    '          if (num(actor.zr) > 0 && ZRT.includes(sk.t)) for (const tg of tgs) apply({ id: actor.id + "-zr", type: "delay", target: tg.id, value: num(actor.zr) }, actor, actor.color);   // 关卡效果【滋扰】：攻击后被打的角色行动延后（妨害 / 强化不算攻击）')
rep('          enemyDebuff(actor, tgs, { dl: actor.hitDl, sl: actor.hitSl, sd: actor.hitSd }, "hit");',
    '          enemyDebuff(actor, tgs, { dl: actor.hitDl, sl: actor.hitSl, sd: actor.hitSd }, "hit");\n'
    '          if (num(actor.zr) > 0) for (const tg of tgs) apply({ id: actor.id + "-zr", type: "delay", target: tg.id, value: num(actor.zr) }, actor, actor.color);   // 【滋扰】')
rep('  const HIT1 = ["单攻", "妨害"], HIT3 = ["扩散", "弹射"], HITALL = ["群攻", "横扫", "分摊"];',
    '  const HIT1 = ["单攻", "妨害"], HIT3 = ["扩散", "弹射"], HITALL = ["群攻", "横扫", "分摊"], ZRT = ["单攻", "扩散", "弹射", "群攻", "横扫", "分摊"];   // ZRT：算“施放攻击”的技能标签（滋扰用）')
# 4) 关卡：换上这一波敌人时带上 rev / zr
old = "if (m.phs) u.phs = m.phs; if (m.ehp) u.ehp = m.ehp; if (m.dice) u.dice = true;"
rep(old, old + " if (m.rev) u.rev = m.rev; if (m.zr) u.zr = m.zr;")
open(p, 'w', encoding='utf8', newline='').write(s)
