# 拿 4.7 王棋录像对出来的两处“我方伤害扣敌人生命值”问题（没改 tv）：
# 1. 阿哈时刻的伤害（几个人的欢愉技合在一起）结算时整个扣在第一个敌人身上：群攻的部分本来按每个敌人分（tw），
#    合在一起后没有 tw，全部算给了 BOSS（5 个敌人时 BOSS 多扣 4 倍）。现在每个人的欢愉技各按自己的分配结算，
#    星神★阿哈【满月】的真实伤害按原文由敌方全体均分。
# 2. 群攻的目标数按敌人卡数量算，打死 / 还没重新登场的敌人也算进去，结算时总伤害分给剩下的几个，每个都多扣。
#    现在行动记录里有当时在场的敌人（eAll）时，按在场的个数算。没开敌人掉血时敌人都在场，和以前一样。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('if (x.uid === "aha") { go(one(x, () => elationDmgOf(x)), null); continue; }',
    'if (x.uid === "aha") { const d = one(x, () => elationDmgOf(x)); if (d) for (const p of d.parts) { const tA = num(p.r.trueAmt); go(tA > 0 ? Object.assign({}, p.r, { total: p.r.total - tA }) : p.r, null); if (tA > 0) { const L = U.filter(z => z.kind === "enemy" && !z.gone && z.ehx > 0); for (const z of L) hurtEnemy(z, tA / L.length, null); } } continue; }')
rep('      killK = "a";\n      try {\n        for (; iA < actions.length; iA++)',
    '      killK = "a";\n      // 阿哈时刻：每个人的欢愉技按自己的目标分；满月的真实伤害由敌方全体均分\n      try {\n        for (; iA < actions.length; iA++)')
rep('    const N = enemyCount();\n    const nAll = e.tg === 3 ? N : 1;',
    '    const N = rec && rec.eAll && rec.eAll.ord && rec.eAll.ord.length ? rec.eAll.ord.length : enemyCount();   // 当时在场的敌人（开了敌人掉血时会有打死 / 还没登场的）\n    const nAll = e.tg === 3 ? N : 1;')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（修正，没改 tv；tools/ahasplit.py）</b>。“我方伤害扣敌人生命值”两处：① <b>阿哈时刻</b>的伤害以前整个扣在第一个敌人（BOSS）身上，群攻部分没按敌人分，5 个敌人时 BOSS 多扣 4 倍；现在每个人的欢愉技按自己的目标分，星神★阿哈【满月】的真实伤害由敌方全体均分。② 群攻的目标数以前按敌人卡数量，打死 / 还没重新登场的敌人也算，剩下的敌人每个都多扣；现在按当时在场的敌人数。对已有配置：没开敌人掉血时伤害不变；开了的，有群攻 / 阿哈时刻、并且有敌人倒下时伤害变少。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
