# 用户：场地技能 R 也有伤害。录像 5:39 按 R（“点兵，开幕！”）总伤害 228315。敌人卡“R 伤害”可改（空 = 归寂 228315，0 = 不算）；
# 先按欢愉伤害算（打贪饕血条 ×4），卡上可改成非欢愉。没改 tv；可重复运行。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('''      if ((en.lastR ?? en.dice) && en.ph === en.phs.length - 1) {   // 4.7 王棋：最后一管血出现时按 R''',
    '''      let rNow = false;
      if ((en.lastR ?? en.dice) && en.ph === en.phs.length - 1) { rNow = true;   // 4.7 王棋：最后一管血出现时按 R''')
i = s.index('阶段生命值打空，转入第'); j = s.index('\n', i)
blk = '''      if (rNow && eHpOn) { const rd = en.rDmg != null && en.rDmg !== "" ? num(en.rDmg) : (en.dice ? 228315 : 0);   // 场地技能 R 的伤害（用户说明；录像 228315）
        if (rd > 0) { const pe = curEl; curEl = en.rEl ?? true; addLog(`场地技能 R 对${en.name}造成 ${fmt(rd / 1e4, 1)} 万${curEl ? "欢愉" : ""}伤害`, false, "var(--accent)"); hurtEnemy(en, rd, null); curEl = pe; } }\r\n'''
if 'const rd = en.rDmg' not in s: s = s[:j+1] + blk + s[j+1:]
s = s.replace('''data-f="lastR">最后一管血按 R</label>''', '''data-f="lastR">最后一管血按 R</label>${(u.lastR ?? !!u.dice) ? `<label for="rdm-${u.id}" title="场地技能 R 的伤害（录像：归寂 228315；空 = 用这个，0 = 不算）">R 伤害 <input type="number" id="rdm-${u.id}" min="0" step="1000" value="${u.rDmg ?? ""}" placeholder="${u.dice ? 228315 : 0}" data-u="${i}" data-f="rDmg" style="width:76px"></label><label for="rel-${u.id}" title="R 的伤害算不算欢愉伤害（打贪饕血条时欢愉 ×4，其他 ×2）"><input type="checkbox" id="rel-${u.id}" ${(u.rEl ?? true) ? "checked" : ""} data-u="${i}" data-f="rEl">欢愉</label>` : ""}''') if 'data-f="rDmg"' not in s else s
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/rdmg47.py）</b>：用户说明：场地技能 R 也有伤害。按 R 时对归寂造成伤害，默认 228315（录像 5:39“点兵，开幕！”的总伤害），先按欢愉伤害算；敌人卡“R 伤害”和“欢愉”勾选框可改。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
