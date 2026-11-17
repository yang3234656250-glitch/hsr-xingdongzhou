# tv 145（可重复运行）：银狼开大时隐藏分的净变化按录像核对。
# 录像（4.7 王棋上 1:21～1:24）：开大前隐藏分 122（+阿哈时刻结束的 4 笑点 = 126），开大后 136，期间笑点 52→106（+50，专武 20 + 开大 30）。
# 所以开大本身净 −40（126 − 40 + 50 = 136）。用户给的规则“开大消耗 40”就是这个净值；tv 143 又加了【隐藏关卡全成就】+20，等于算了两遍
# （页面开大后 156，比录像多 20，第一次无敌玩家里 2 魂多给 1 个额外回合 + 1 次强普）。
# 现在【隐藏关卡全成就】默认不另加（设置里勾上 = 另加，那时应把开大消耗改成 60）；老存档开大消耗还是 40 的关掉它。
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
OLD = '行迹【隐藏关卡全成就】：进入【无敌玩家】后获得 20 点【隐藏分】（已算，银狼设置里可关）'
NEW = '行迹【隐藏关卡全成就】：进入【无敌玩家】后获得 20 点【隐藏分】（银狼设置里“开大消耗 40”是录像里的净值，已经含这 20；勾上“隐藏关卡全成就”另加时把开大消耗改成 60）'
# DB 模板说明
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
hit = 0
for c in db['chars']:
    for e in c.get('eff', []):
        if e.get('n') == OLD: e['n'] = NEW; hit += 1
assert hit or NEW in line
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]
rep('      cdUp: 40, cdUp2: 40, ach: true, achV: 20 };', '      cdUp: 40, cdUp2: 40, ach: false, achV: 20 };   // ach：开大消耗 40 已经是含它的净值（录像核对），默认不另加')
rep('      if (W.ach !== false && num(W.achV, 20) > 0) {', '      if (W.ach === true && num(W.achV, 20) > 0) {')
rep('<input type="checkbox" id="s-ach" ${W.ach !== false ? "checked" : ""} data-s="ach">行迹隐藏关卡全成就：进入无敌玩家后隐藏分 +</label>',
    '<input type="checkbox" id="s-ach" ${W.ach === true ? "checked" : ""} data-s="ach" title="默认不勾：上面的“开大消耗 40”是录像里开大的净变化，已经含这 20。勾上另加时把开大消耗改成 60">行迹隐藏关卡全成就：另加，进入无敌玩家后隐藏分 +</label>')
rep('  function fixTpl143(s) {',
    '  // tv 145：银狼【隐藏关卡全成就】默认不另加（开大消耗 40 是录像里的净值，已经含这 20）；开大消耗还是 40 的存档关掉，说明换掉（tools/fix145.py）\n'
    '  function fixTpl145(s) { const O = ' + json.dumps(OLD, ensure_ascii=False) + ', N = ' + json.dumps(NEW, ensure_ascii=False) + ';\n'
    '    if (s.sw && num(s.sw.cost, 40) === 40) s.sw.ach = false;\n'
    '    for (const u of s.units) for (const e of u.effects || []) if (e.note === O) e.note = N; }\n'
    '  function fixTpl143(s) {')
rep('    fixTpl144(s);\n    s.tv = 144;', '    fixTpl144(s);\n    fixTpl145(s);\n    s.tv = 145;')
rep('    if (s.tv >= 144) return;', '    if (s.tv >= 145) return;')
rep('  if (!(S.tv >= 144)) { migrateTpl(S);', '  if (!(S.tv >= 145)) { migrateTpl(S);')
rep('if (!(s.tv >= 144)) fixTpl144(s); } finally { S = keep; } s.tv = 144; return; }', 'if (!(s.tv >= 144)) fixTpl144(s); if (!(s.tv >= 145)) fixTpl145(s); } finally { S = keep; } s.tv = 145; return; }')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17：tv 145（tools/fix145.py）</b>。银狼开大时隐藏分按录像核对：录像里开大前 122（阿哈时刻结束 +4 笑点后 126），开大后 136，期间笑点 +50（专武 20 + 开大 30），所以开大本身净 −40，就是设置里的“开大消耗 40”。tv 143 又加了【隐藏关卡全成就】+20，算了两遍：页面开大后 156，第一次无敌玩家里 2 魂多给了 1 个额外回合和 1 次强普。现在这条行迹默认不另加（设置里可勾，勾上时把开大消耗改成 60）。对已有配置：开大消耗还是 40 的存档自动关掉这条，有银狼的队伍开大后隐藏分少 20，2 魂额外回合可能变少。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok', hit)
