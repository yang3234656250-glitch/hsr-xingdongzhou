# tv 146（可重复运行）：星神★阿哈在队里时，【阿哈时刻】的基础速度 = 星神★阿哈的基础速度（官方：“【阿哈时刻】的基础速度从 80 提高至星神★阿哈的基础速度”）。
# 阿哈专武【当第一声「阿哈」响起】基础速度 +12/14/16/18/20（官方 light_cone_ranks BaseSpeed），以前 DB 没写。
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
for l in db['lcs']:
    if l['id'] == 23065: l['bs'] = [12, 14, 16, 18, 20]
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]
rep('  const ahaSpeed = elationSpeeds => {\n    const top = [...elationSpeeds].sort((a, b) => b - a);\n    return num(S.aha.base) +',
    '  // 星神★阿哈在队里时，阿哈时刻的基础速度 = 星神★阿哈卡片的基础速度（含专武 +12 等），否则用阿哈时刻设置里的“基础”\n'
    '  const ahaAH = () => S.units.find(u => u.kind === "ally" && !u.sm && tidOf(u) === "1511");\n'
    '  const ahaBase = () => { const A = ahaAH(); return A ? num(A.base, 94) : num(S.aha.base); };\n'
    '  const ahaSpeed = elationSpeeds => {\n    const top = [...elationSpeeds].sort((a, b) => b - a);\n    return ahaBase() +')
rep('<label for="a-base">基础 <input type="number" id="a-base" step="1" value="${S.aha.base}" data-a="base"></label>',
    '${ahaAH() ? `<label title="星神★阿哈在队里：阿哈时刻的基础速度 = 星神★阿哈的基础速度（官方），跟着她的卡片（专武 +12 等）自动变">基础 <b>${fmt(ahaBase())}</b>（= 星神★阿哈基础速度）</label>` : `<label for="a-base">基础 <input type="number" id="a-base" step="1" value="${S.aha.base}" data-a="base"></label>`}')
rep('  function fixTpl143(s) {',
    '  // tv 146：阿哈专武基础速度 +12（DB 补 bs），装了的卡片 applyEquip（tools/fix146.py）\n  function fixTpl146(s) { const keep = S; S = s; try { for (const u of s.units) if (u.kind === "ally" && !u.sm) { const ah = tidOf(u) === "1511";\n      if (num(u.lc) === 23065) { const bs = [12, 14, 16, 18, 20][Math.max(1, Math.min(5, num(u.lcR, 1))) - 1]; if (!u.bsX && ah && num(u.base) - 94 >= bs - 1e-9) u.bsX = bs; applyEquip(u); }   // 以前手填进基础速度的专武 +12 不重复加\n      else if (ah && !u.bsX && num(u.base) === 106) u.base = 94; }   // 星神★阿哈没装专武，却还留着手填的 94 + 12\n    } finally { S = keep; } }\n  function fixTpl143(s) {')
rep('    fixTpl145(s);\n    s.tv = 145;', '    fixTpl145(s);\n    fixTpl146(s);\n    s.tv = 146;')
rep('    if (s.tv >= 145) return;', '    if (s.tv >= 146) return;')
rep('  if (!(S.tv >= 145)) { migrateTpl(S);', '  if (!(S.tv >= 146)) { migrateTpl(S);')
rep('if (!(s.tv >= 145)) fixTpl145(s); } finally { S = keep; } s.tv = 145; return; }', 'if (!(s.tv >= 145)) fixTpl145(s); if (!(s.tv >= 146)) fixTpl146(s); } finally { S = keep; } s.tv = 146; return; }')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17：tv 146（tools/fix146.py）</b>。星神★阿哈在队里时，<b>阿哈时刻的基础速度自动等于星神★阿哈卡片的基础速度</b>（官方：基础速度从 80 提高至星神★阿哈的基础速度），阿哈时刻设置里的“基础”不用再手填（没有星神★阿哈时照旧用它）。阿哈专武【当第一声「阿哈」响起】补上基础速度 +12（叠影 14 / 16 / 18 / 20，官方数据），换光锥时卡片基础速度自动加减。对已有配置：有星神★阿哈的方案，阿哈时刻速度按她的卡片算（以前手填的值不再用）；装了专武的卡片基础速度按光锥重算。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
