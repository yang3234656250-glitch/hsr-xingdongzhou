# tv 143：银狼LV.999 两条行迹（可重复运行）
# ① 固有行迹（阿哈升格后）「暴击伤害提高 #3[i]%」：欢愉万相期间暴击伤害 +40%（以前只做了隐藏分溢出和绝活共赏转隐藏分，漏了这一条）
# ② 行迹【隐藏关卡全成就】「进入【无敌玩家】状态后，获得 20 点【隐藏分】」（以前没建模）
# 依据：TextMapCHS 14702607912588532380；Mar-7th character_skill_trees 1506103 params [[20]]
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

OLD = '行迹【隐藏关卡全成就】：进入【无敌玩家】后获得 20 点【隐藏分】（没建模，需要时自己加）'
NEW = '行迹【隐藏关卡全成就】：进入【无敌玩家】后获得 20 点【隐藏分】（已算，银狼设置里可关）'
# DB 说明
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
hit = 0
for c in db['chars']:
    for e in c['eff']:
        if e.get('n') == OLD: e['n'] = NEW; hit += 1
assert hit or NEW in line, 'DB 说明没找到'
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]

# 默认设置
rep('      jh: false, jhPct: 20, jhPct2: 40, capUp: 360, capUp2: 999 };',
    '      jh: false, jhPct: 20, jhPct2: 40, capUp: 360, capUp2: 999,\n'
    '      // 同一条固有行迹：升格期间暴击伤害 +cdUp%（阿哈 2 魂时的数值没查到官方数据，先同 40）；行迹隐藏关卡全成就：进入无敌玩家后隐藏分 +achV\n'
    '      cdUp: 40, cdUp2: 40, ach: true, achV: 20 };')
# 开大：进入无敌玩家后 +20 隐藏分
rep('      const entry = log[log.length - 1], pool0 = pool, score0 = sw.score;',
    '      const entry = log[log.length - 1], pool0 = pool, score0 = sw.score;\n'
    '      // 行迹【隐藏关卡全成就】：进入【无敌玩家】状态后获得 20 点【隐藏分】（2 魂按新的一档再加强普）\n'
    '      if (W.ach !== false && num(W.achV, 20) > 0) { setScore(sw.score + num(W.achV, 20), "隐藏关卡全成就"); checkE2(); entry.text += `；行迹隐藏关卡全成就 隐藏分 +${num(W.achV, 20)}`; }')
# 伤害：升格期间暴击伤害 +40%
rep('    if (tidOf(u) === "1511" && rec && rec.wx) { cr += num(u.eid) >= 2 ? 20 : 12; defI = num(u.eid) >= 2 ? 60 : 30; }',
    '    if (tidOf(u) === "1511" && rec && rec.wx) { cr += num(u.eid) >= 2 ? 20 : 12; defI = num(u.eid) >= 2 ? 60 : 30; }\n'
    '    // 银狼LV.999 固有行迹（阿哈升格后）：「欢愉」命途升格（欢愉万相）期间暴击伤害 +40%（银狼设置里勾了这条固有行迹才算）\n'
    '    if (tidOf(u) === "1506" && rec && rec.wx && S.sw && S.sw.jh) { const AH = S.units.find(x => x.kind === "ally" && x.wxTurns); cd += num(AH && num(AH.eid) >= 2 ? S.sw.cdUp2 : S.sw.cdUp, 40); }')
# 设置界面
rep('aria-label="2魂升格上限" style="width:62px">）\n      </div>',
    'aria-label="2魂升格上限" style="width:62px">）；升格期间暴击伤害 +<input type="number" id="s-cdUp" value="${W.cdUp ?? 40}" data-s="cdUp" step="1" aria-label="升格暴击伤害" style="width:50px">%（2 魂起 <input type="number" id="s-cdUp2" value="${W.cdUp2 ?? 40}" data-s="cdUp2" step="1" aria-label="2魂升格暴击伤害" style="width:50px">%）\n      </div>\n'
    '      <div class="row">\n'
    '        <label for="s-ach"><input type="checkbox" id="s-ach" ${W.ach !== false ? "checked" : ""} data-s="ach">行迹隐藏关卡全成就：进入无敌玩家后隐藏分 +</label><input type="number" id="s-achV" value="${W.achV ?? 20}" data-s="achV" step="1" aria-label="进入无敌玩家时的隐藏分" style="width:50px">\n'
    '      </div>')
# 迁移：卡片上的说明换成新的
rep('  function fixTpl142(s) {',
    '  // tv 143：银狼【隐藏关卡全成就】说明改成“已算”（只换说明文字，tools/swup143.py）\n'
    '  function fixTpl143(s) { const O = ' + json.dumps(OLD, ensure_ascii=False) + ', N = ' + json.dumps(NEW, ensure_ascii=False) + '; for (const u of s.units) for (const e of u.effects || []) if (e.note === O) e.note = N; }\n'
    '  function fixTpl142(s) {')
rep('    fixTpl142(s);\n    s.tv = 142;', '    fixTpl142(s);\n    fixTpl143(s);\n    s.tv = 143;')
rep('    if (s.tv >= 142) return;', '    if (s.tv >= 143) return;')
rep('  if (!(S.tv >= 142)) { migrateTpl(S);', '  if (!(S.tv >= 143)) { migrateTpl(S);')
rep('if (!(s.tv >= 142)) fixTpl142(s); } finally { S = keep; } s.tv = 142; return; }', 'if (!(s.tv >= 142)) fixTpl142(s); if (!(s.tv >= 143)) fixTpl143(s); } finally { S = keep; } s.tv = 143; return; }')
# 更新日志
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17：tv 143（tools/swup143.py）</b>。银狼LV.999 两条漏算的行迹（依据官方原文）：① 固有行迹（阿哈升格后）“当「欢愉」命途升格时……<b>暴击伤害提高 40%</b>”：以前只做了隐藏分溢出到 360 和绝活共赏转隐藏分，漏了这 40% 暴伤；现在阿哈欢愉万相期间银狼的所有伤害暴伤 +40%（银狼设置里勾了这条固有行迹才算；阿哈 2 魂时的数值没查到，先按 40%，可改）。② 行迹【隐藏关卡全成就】“进入【无敌玩家】状态后，获得 20 点【隐藏分】”：以前没建模，现在每次开大进入无敌玩家后隐藏分 +20（开大日志里写；2 魂按新的一档再加强普；银狼设置里可关）。对已有配置：有银狼的队伍伤害变高，隐藏分变多可能让自动开大、2 魂的额外强普提前；卡片上这条行迹的说明从“没建模”换成“已算”。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
