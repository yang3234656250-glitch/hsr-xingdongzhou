# 银狼强普打断：用户补充“就算归寂血量归 0，但如果还有怪没死，那就不会在强普期间转阶段”（可重复运行，没改 tv）
# = 官方原文“对场上所有敌方造成了致命伤害则结束本次技能”：有下一阶段的敌人在强普里被打到 0 先不转阶段、不再挨弹射，
#   剩下的弹射打其他敌人；场上敌人全部受到致命伤害才结束技能（剩下的在额外回合再次施放），技能结束后才转阶段。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

rep('''      // 银狼强化普攻【狼尊时刻】：对场上所有敌方造成致命伤害（或有分阶段的敌人被打到转阶段）就结束本次技能，
      // 剩下的弹射 / 盲盒 / 最后一击在 1 个额外回合里再次施放；每回合首次触发时自身所有增益延长 1 回合
      const swCut = (d, rec, main, killer) => {
        let left = d.total, why = "";
        let L = (Array.isArray(d.tw) && d.tw.length ? d.tw.map(([id, sh]) => [byId[id], sh]) : [[main, 1]]).filter(([z, sh]) => z && !z.gone && z.ehx > 0 && sh > 0);
        for (let k = 0; k < 40 && left > 1e-6 && L.length; k++) {
          const S2 = L.reduce((p, x) => p + x[1], 0);
          let xm = Infinity; for (const [z, sh] of L) xm = Math.min(xm, Math.max(0, z.ehc) * S2 / sh);   // 下一个被打到致命的目标（均分着打）
          const step = Math.min(left, xm), ph0 = L.map(([z]) => z.ph);
          for (const [z, sh] of L) { const a = step * sh / S2, cap = Math.max(0, z.ehc); hurtEnemy(z, a >= cap - 1e-6 ? cap + 1e-6 : a, killer); }
          left -= step;
          const ended = L.find(([z], i) => z.phs && z.ph !== ph0[i]);
          L = L.filter(([z]) => !z.gone);
          if (left > 1e-6 && (ended || !L.length)) { why = ended ? `${ended[0].name}转阶段` : "敌人全部倒下"; break; }
        }
        if (!why || !U.some(z => z.kind === "enemy" && !z.gone)) return;   // 没打断，或者已经没有可攻击的敌人（战斗结束）''',
'''      // 银狼强化普攻【狼尊时刻】：对场上所有敌方造成致命伤害就结束本次技能，剩下的弹射 / 盲盒 / 最后一击在 1 个额外回合里再次施放；
      // 每回合首次触发时自身所有增益延长 1 回合。有下一阶段的敌人（归寂）被打到 0 时先不转阶段、不再挨弹射，
      // 场上还有别的敌人没倒下就继续打它们；技能结束（打完或被打断）后才转阶段（用户说明）
      const swCut = (d, rec, main, killer) => {
        let left = d.total, why = "";
        const pend = [];   // 这次强普里被打到 0、等技能结束再转阶段的
        let L = (Array.isArray(d.tw) && d.tw.length ? d.tw.map(([id, sh]) => [byId[id], sh]) : [[main, 1]]).filter(([z, sh]) => z && !z.gone && z.ehx > 0 && sh > 0);
        for (let k = 0; k < 40 && left > 1e-6 && L.length; k++) {
          const S2 = L.reduce((p, x) => p + x[1], 0);
          let xm = Infinity; for (const [z, sh] of L) xm = Math.min(xm, Math.max(0, z.ehc) * S2 / sh);   // 下一个被打到致命的目标（均分着打）
          const step = Math.min(left, xm);
          for (const [z, sh] of L) {
            const a = step * sh / S2, cap = Math.max(0, z.ehc);
            if (a < cap - 1e-6) hurtEnemy(z, a, killer);
            else if (z.phs && z.ph < z.phs.length - 1) pend.push(z);   // 致命伤害，转阶段等技能结束
            else hurtEnemy(z, cap + 1e-6, killer);
          }
          left -= step;
          L = L.filter(([z]) => !z.gone && !pend.includes(z));
          if (left > 1e-6 && !L.length) { why = "场上敌人全部受到致命伤害"; break; }
        }
        for (const z of pend) if (!z.gone) hurtEnemy(z, Math.max(0, z.ehc) + 1e-6, killer);   // 技能结束：转阶段
        if (!why || !U.some(z => z.kind === "enemy" && !z.gone)) return;   // 没打断，或者已经没有可攻击的敌人（战斗结束）''')
rep('''        addLog(`${swU.name} 强化普攻打到${why}，本次技能结束（剩 ${Math.round(f * 100)}% 没打）''',
    '''        addLog(`${swU.name} 强化普攻打到${why}${pend.length ? `（${[...new Set(pend.map(z => z.name))].join("、")}随后转阶段）` : ""}，本次技能结束（剩 ${Math.round(f * 100)}% 没打）''')
rep('''`${rec.re != null ? "，" : ""}打到转阶段 / 全部倒下时结束，打出''', '''`${rec.re != null ? "，" : ""}场上敌人全部受到致命伤害时结束，打出''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（银狼强普打断：按“场上所有敌人受到致命伤害”，没改 tv；tools/swcut2.py）</b>。用户说明：归寂生命值打到 0，但场上还有别的敌人没死时，强普期间不会转阶段。现在有下一阶段的敌人在强普里被打到 0 后先不转阶段、不再挨弹射，剩下的弹射打其他敌人；场上敌人全部受到致命伤害才结束技能、在额外回合再次施放剩下的部分；这次强普结束（打完或被打断）后它才转阶段。上一条“BOSS 转阶段就打断”的写法作废。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
