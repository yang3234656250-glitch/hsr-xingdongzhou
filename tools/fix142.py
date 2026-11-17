# tv 142：【欢愉负债】按官方原文改成“占据生命上限”（从上面占），不再“剩余生命值不高于负债时被消灭”（可重复运行）
# 依据：TextMap「欢愉负债会占据生命上限，占据部分若包含当前生命值，则该部分当前生命值立即流失」；实战录像：归寂每条血都打到 1%～6% 才转阶段，新阶段从 90% 开始
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
OLD = '天赋【阿哈正传】：阿哈和队友造成伤害时，敌人额外获得损失生命值 25% 的【欢愉负债】（最多生命上限 10%）；敌人剩余生命值不高于【欢愉负债】时被消灭（要在敌人卡上填了生命值才算）'
NEW = '天赋【阿哈正传】：阿哈和队友造成伤害时，敌人额外获得损失生命值 25% 的【欢愉负债】（最多生命上限 10%，转阶段时按比例保留）；【欢愉负债】占据生命上限，当前生命值高出“生命上限 − 负债”的部分立即流失（新阶段一开始就少这么多；要在敌人卡上填了生命值才算）'
def rep(a, b, n=1):
    global s
    a = a.replace('\n', '\r\n'); b = b.replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# DB 说明
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
for c in db['chars']:
    for e in c['eff']:
        if e.get('n') == OLD: e['n'] = NEW
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]
# 计算
rep('    if (eHpOn) for (const z of U) if (z.kind === "enemy") { let mx = eHpMaxOf(z); const ph = phOf(z); if (ph.length) { z.phs = ph; z.ph = 0; mx = ph[0]; } if (mx > 0) { z.ehx = mx; z.ehc = mx; } }',
    '    const aha6 = U.some(z => z.kind === "ally" && !z.sm && tidOf(z) === "1511" && num(z.eid) >= 6);   // 阿哈 6 魂：敌人始终至少有生命上限 20% 的【欢愉负债】（开局就占掉）\n'
    '    if (eHpOn) for (const z of U) if (z.kind === "enemy") { let mx = eHpMaxOf(z); const ph = phOf(z); if (ph.length) { z.phs = ph; z.ph = 0; mx = ph[0]; } if (mx > 0) { z.ehx = mx; z.ehc = aha6 ? mx * 0.8 : mx; } }')
rep('    const endBar = (en, killer) => {   // 这一条血打空（或达到欢愉负债）：还有下一阶段 → 转阶段；否则消灭',
    '    const endBar = (en, killer) => {   // 这一条血打空：还有下一阶段 → 转阶段；否则消灭')
rep('      if (ahaU && num(en.debtP) > 0) en.debt = en.debtP * en.ehx;   // 【欢愉负债】按比例保留到下一阶段（占据生命上限，所以新阶段一开始就少这个比例）',
    '      if (ahaU && num(en.debtP) > 0) en.debt = en.debtP * en.ehx;   // 【欢愉负债】按比例保留到下一阶段（占据生命上限，所以新阶段一开始就少这个比例）\n'
    '      if (ahaU) en.ehc = Math.min(en.ehc, en.ehx - debtOf(en));')
rep('    const hurtEnemy = (en, a, killer) => {',
    '    const debtOf = en => !ahaU ? 0 : num(ahaU.eid) >= 6 ? Math.max(en.ehx * 0.2, num(en.debt)) : num(en.debt);   // 【欢愉负债】占据的生命上限（6 魂始终至少 20%）\n'
    '    const hurtEnemy = (en, a, killer) => {')
rep('''      if (ahaU) {   // 我方造成伤害时累积损失生命值 25% 的【欢愉负债】（上限 = 生命上限 10%；6 魂始终至少 20%），剩余生命值不高于它时被消灭
        en.debtP = Math.min(0.1, num(en.debtP) + lost * 0.25 / en.ehx); en.debt = en.debtP * en.ehx; const d = num(ahaU.eid) >= 6 ? Math.max(en.ehx * 0.2, en.debt) : en.debt;   // 官方：【欢愉负债】占据生命上限（按生命上限的比例记，最多 10%），占据部分包含的当前生命值立即流失
        if (en.ehc <= d) { addLog(`${en.name} 剩余生命值（${Math.round(en.ehc)}）不高于【欢愉负债】（${Math.round(d)}）`, false, ahaU.color, ahaU.id); endBar(en, killer); }
      } };''',
'''      if (ahaU) {   // 我方造成伤害时累积损失生命值 25% 的【欢愉负债】（上限 = 生命上限 10%；6 魂始终至少 20%）
        en.debtP = Math.min(0.1, num(en.debtP) + lost * 0.25 / en.ehx); en.debt = en.debtP * en.ehx;   // 官方：【欢愉负债】占据生命上限（按生命上限的比例记，最多 10%），占据部分包含的当前生命值立即流失（tv 142 起：从上面占，生命值打到 0 才消灭）
        const cap = en.ehx - debtOf(en); if (en.ehc > cap) en.ehc = cap;
      } };''')
# 迁移：卡片上的说明换成新的
rep('  function fixTpl141(s) { const keep = S; S = s; try { fixTpl(s, TPLFIX141); } finally { S = keep; } }',
    '  function fixTpl141(s) { const keep = S; S = s; try { fixTpl(s, TPLFIX141); } finally { S = keep; } }\n'
    '  // tv 142：阿哈【欢愉负债】说明换成“占据生命上限”的写法（只换说明文字，tools/fix142.py）\n'
    '  function fixTpl142(s) { const O = ' + json.dumps(OLD, ensure_ascii=False) + ', N = ' + json.dumps(NEW, ensure_ascii=False) + '; for (const u of s.units) for (const e of u.effects || []) if (e.note === O) e.note = N; }')
rep('    fixTpl141(s);\n    s.tv = 141;', '    fixTpl141(s);\n    fixTpl142(s);\n    s.tv = 142;')
rep('    if (s.tv >= 141) return;', '    if (s.tv >= 142) return;')
rep('  if (!(S.tv >= 141)) { migrateTpl(S);', '  if (!(S.tv >= 142)) { migrateTpl(S);')
open(p, 'w', encoding='utf8', newline='').write(s)
