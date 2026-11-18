# 开怪秘技（进战触发的秘技）在敌人转阶段时再次触发（用户说明：基本所有开怪秘技都是这样）；银狼LV.999 秘技【怪怪怪味豆】建模。
# ① 银狼秘技：每个波次开始时触发 1 次【头号补给盲盒】，本次固定计入 99 点【好活当赏】：90% 欢愉伤害（12 级起 99%）由敌方全体均分，
#    1/3 概率再多 20% 真实伤害（按期望），笑点 / 回复战技点那些随机结果不算。开局一次（S.sw.swq 没设 = 开，银狼设置里可关）。
# ② 转阶段（endBar 换到下一条血，敌人卡 tq 没设 = 跟 dice）时：开怪角色（攻击敌人进战的那位，银狼设置旁的「开怪」下拉 = S.opener）
#    说明以「秘技」开头的进战效果再生效一次；银狼秘技盲盒（原文“每个波次开始时”）也再触发一次。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
# 伤害层：固定好活当赏
rep('    let bg = inAha ? num(rec.consumed, 0) : bangerAt(u, rec);',
    '    let bg = inAha ? num(rec.consumed, 0) : rec && rec.bgFix != null ? num(rec.bgFix) : bangerAt(u, rec);   // bgFix：固定计入的好活当赏（银狼秘技 99）')
rep('  function dotDmgOf(r, u) {\n    if (!r || !u || u.kind !== "ally") return null;\n    if (r.__dmg !== undefined) return r.__dmg;\n',
    '  function dotDmgOf(r, u) {\n    if (!r || !u || u.kind !== "ally") return null;\n    if (r.__dmg !== undefined) return r.__dmg;\n'
    '    if (r.swq) {   // 银狼秘技【怪怪怪味豆】：头号补给盲盒，固定计入 99 点好活当赏；90% 欢愉伤害敌方全体均分，1/3 概率再多 20% 真实伤害（期望）\n'
    '      const ent = { v: num(dmgLv(u, "u")) >= 12 ? 0.99 : 0.9, adj: 0, rnd: 0, tg: 0, stat: "lv", el: true, key: "box", n: "秘技·头号补给盲盒", lv: dmgLv(u, "u") };\n'
    '      const d = dmgCalc(u, ent, { t: r.t, seq: r.seq, uid: u.id, db: r.db, edb: r.edb, eAll: r.eAll, ebk: r.ebk, __box: true, bgFix: 99 });\n'
    '      if (d) d.total *= 1 + 0.2 / 3;\n'
    '      return (r.__dmg = d);\n'
    '    }\n')
# 模拟：触发函数
rep('    if (swU && pool > 0) setScore(sw.score + pool, "开局笑点");\n',
    '    if (swU && pool > 0) setScore(sw.score + pool, "开局笑点");\n'
    '    const swqFire = why => {   // 银狼秘技【怪怪怪味豆】：每个波次开始时 1 次头号补给盲盒（固定 99 点好活当赏）\n'
    '      if (!swU || swU.gone || W.swq === false) return;\n'
    '      const e0 = U.find(z => z.kind === "enemy" && !z.gone);\n'
    '      const r = { t, uid: swU.id, en: e0 ? e0.id : null, k: "秘技·头号补给盲盒", swq: 1, db: dbSnap(swU), edb: edbSnap(e0), eAll: edbAll(), seq: seq++, ebk: ebkNow() }; dotRecs.push(r);\n'
    '      addLog(`${swU.name} 秘技【怪怪怪味豆】：触发【头号补给盲盒】（${why}；固定计入 99 点好活当赏）`, false, swU.color, swU.id); log[log.length - 1].dd = [r];\n'
    '    };\n'
    '    const techAgain = en => {   // 转阶段：开怪秘技再次触发（用户说明）\n'
    '      if (!(en.tq ?? en.dice)) return;\n'
    '      const L = U.filter(u => u.kind === "ally" && !u.gone && !u.sm && u.id === S.opener).map(u => [u, fx(u, "start").filter(e => /^秘技/.test(e.note || ""))]);   // 只有开怪的那位（S.opener）\n'
    '      let n = 0; for (const [u, F] of L) for (const e of F) { apply(e, u, u.color); n++; }\n'
    '      if (n) addLog(`转阶段：开怪秘技再次触发（${L.filter(x => x[1].length).map(x => x[0].name).join("、")}）`, false, "var(--muted)");\n'
    '      swqFire("转阶段");\n'
    '    };\n')
rep('      for (const [u, L] of S0) for (const e of L) if (e.type === "cast") apply(e, u, u.color);\n    }\n    checkPunchE();\n',
    '      for (const [u, L] of S0) for (const e of L) if (e.type === "cast") apply(e, u, u.color);\n      swqFire("进战");\n    }\n    checkPunchE();\n')
rep('      en.ehx = en.ehc = en.phs[en.ph];   // 欢愉负债不清除（写在阿哈的效果里）\n',
    '      en.ehx = en.ehc = en.phs[en.ph];   // 欢愉负债不清除（写在阿哈的效果里）\n      techAgain(en);\n')
# 设置
rep('''        ${sn("charges", "强普次数", 'min="1" step="1"')}\n''',
    '''        ${sn("charges", "强普次数", 'min="1" step="1"')}\n        <label title="秘技【怪怪怪味豆】：每个波次开始时（进战、敌人转阶段）触发 1 次【头号补给盲盒】，固定计入 99 点好活当赏；只算伤害"><input type="checkbox" data-s="swq" ${W.swq === false ? "" : "checked"}> 秘技盲盒</label>\n''')
rep('S.sw[k] = el.type === "checkbox" ? el.checked : k === "uid" || k === "e2when" || k === "beanL" ? el.value : num(el.value);',
    'if (k === "opener") { if (el.value) S.opener = el.value; else delete S.opener; update(); return; }\n      S.sw[k] = el.type === "checkbox" ? el.checked : k === "uid" || k === "e2when" || k === "beanL" ? el.value : num(el.value);')
rep('''<input type="checkbox" data-s="swq" ${W.swq === false ? "" : "checked"}> 秘技盲盒</label>\n''',
    '''<input type="checkbox" data-s="swq" ${W.swq === false ? "" : "checked"}> 秘技盲盒</label>\n        <label title="用秘技攻击敌人进战的那位：敌人转阶段时，她 / 他的开怪秘技再触发一次">开怪 <select data-s="opener">${opt([["", "（不算）"], ...S.units.filter(x => x.kind === "ally" && !x.sm).map(x => [x.id, x.name])], S.opener || "")}</select></label>\n''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/tech47.py）</b>。① 银狼LV.999 秘技<b>【怪怪怪味豆】</b>建模：每个波次开始时触发 1 次【头号补给盲盒】，固定计入 99 点好活当赏，90% 欢愉伤害由敌方全体均分（1/3 概率多 20% 真实伤害按期望）；笑点 / 回复战技点这些随机结果不算。银狼设置里「秘技盲盒」可关。② <b>开怪秘技在敌人转阶段时再次触发</b>（用户说明）：银狼设置里选「开怪」角色（用秘技攻击敌人进战的那位），4.7 王棋归寂每次转阶段时，她 / 他说明以「秘技」开头的进战效果再生效一次；银狼秘技盲盒（原文“每个波次开始时”）也再触发一次（敌人卡字段 tq 可关，没设跟骰子开关）。对已有配置：有银狼LV.999 的方案开局多一段伤害；没选开怪角色时其他不变。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
