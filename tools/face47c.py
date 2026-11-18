# 4.7 归寂：录像 5:28～5:31（第 2 管开头，AV 105，我方额外回合之后）归寂「成」连出「讥讽的目光 → 埋梗时刻」（用户：两次转阶段都有拉条）；
# 第 1 管 54 是「讥讽的目光 → 存在的闹剧」。所以「成」主形态每回合第一招固定讥讽的目光，第二招按 闹剧 → 埋梗 → … 轮。
# phm 主形态段新增第 7 项 = 每回合第一招固定的技能下标、第 8 项 = 自己的出招表（逗号分隔的技能下标）；开局（第 1 管）也按 phm 第 1 段设置。
# 固定的那一招不推进出招表。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
C = '万色返空主，归寂•「成」'
OLD = f'{C}@@@2|{C}@@@2|'
NEW = f'{C}@@@2@@@37@36;40;41;38;39;42;43;44;45|{C}@@@2@@@37@36;40;41;38;39;42;43;44;45|'
s = s.replace(OLD, NEW)
# 默认字符串提出来，开局也用
if 'en.phm ??= phmDef(en)' in s:
    i = s.index('const phmDef = en => en.dice && /^万色返空主，归寂/.test(String(en.mon || "")) ? "'); j = s.index('" : ""', i); DEF = s[i + len('const phmDef = en => en.dice && /^万色返空主，归寂/.test(String(en.mon || "")) ? "'):j]
else:
    i = s.index('en.phm ??= (en.dice && en.mon === "万色返空主，归寂" ? "'); j = s.index('" : "")', i)
    DEF = s[i + len('en.phm ??= (en.dice && en.mon === "万色返空主，归寂" ? "'):j]
    rep(f'en.phm ??= (en.dice && en.mon === "万色返空主，归寂" ? "{DEF}" : "")', 'en.phm ??= phmDef(en)')
rep('    const FACE = [];',
    f'    const phmDef = en => en.dice && /^万色返空主，归寂/.test(String(en.mon || "")) ? "{DEF}" : "";   // 4.7 归寂默认的每管形态（录像）\n'
    '    const phTok = (en, a) => { if (!a) return; en.dblN = Math.max(1, num(a[3]) || 1); en.dblI = 0; en.dblF = a[6] != null && a[6] !== "" ? num(a[6]) : null;   // 主形态：每回合几招、第一招固定哪个\n'
    '      if (a[7]) { const q = String(a[7]).split(/[;；]/).map(x => num(x)).filter(x => MON.sk[x]); if (q.length) en.seq = q; } };   // 自己的出招表\n'
    '    for (const z of U) if (z.kind === "enemy" && z.phs) { const a = String(z.phm ?? phmDef(z)).split("|")[0]; if (a) { z.phm ??= phmDef(z); phTok(z, a.split("+")[0].trim().split("@")); } }   // 第 1 管也按 phm\n'
    '    const FACE = [];')
rep('        en.dblN = Math.max(1, num(fl[0][3]) || 1); en.dblI = 0; en.moX =',
    '        en.moX =')
rep('addLog(`${en.name} 变成「${m2.n.split("「")[1] || m2.n}：出招表换成这个形态的`, false, "var(--enemy)"); }\n',
    'addLog(`${en.name} 变成「${m2.n.split("「")[1] || m2.n}：出招表换成这个形态的`, false, "var(--enemy)"); }\n'
    '        phTok(en, fl[0]);\n')
# 选招：每回合第一招固定的不推进出招表
rep('const sqI = ((actor.turns - 1 + (FG ? 0 : num(actor.sqo))) % seq.length + seq.length) % seq.length, sk = MON.sk[seq[sqI]];',
    'const fxA = !FG && actor.dblF != null && !(num(actor.dblI) > 0) && MON.sk[actor.dblF] ? actor.dblF : null; if (fxA != null) actor.sqo = num(actor.sqo) - 1;   // 每回合第一招固定（phm 第 7 项），不推进出招表\n'
    '          const sqI = ((actor.turns - 1 + (FG ? 0 : num(actor.sqo))) % seq.length + seq.length) % seq.length, skI = fxA ?? seq[sqI], sk = MON.sk[skI];')
rep('((monOf(actor) || {}).x || {})[seq[sqI]]', '((monOf(actor) || {}).x || {})[skI]')
rep('          const skIdx = seq[sqI];', '          const skIdx = skI;')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/face47c.py）</b>。4.7 归寂「成」每回合<b>第一招固定讥讽的目光</b>，第二招按 存在的闹剧 → 埋梗时刻 → … 轮：录像第 1 管 54「讥讽的目光 → 存在的闹剧」、第 2 管开头 105（转面拉条，我方额外回合之后）「讥讽的目光 → 埋梗时刻」。以前第 2 管开头连出两下群攻，我方被多推了一次条。phm 主形态段多了第 7 项（每回合第一招固定的技能）和第 8 项（自己的出招表，用分号分隔）。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
