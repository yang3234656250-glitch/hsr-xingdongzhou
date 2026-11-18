# 用户说明：开怪秘技 = 攻击型秘技（像银狼这种打敌人进战的）；真珠、爻光那种给自己加状态的、阿哈的领域都不算。
# 改成：转阶段时，进战效果里有秘技伤害（hitd）的角色 = 攻击型秘技，她 / 他说明以「秘技」开头的进战效果再生效一次；
# 银狼秘技盲盒照旧每次转阶段触发。去掉上一版的「开怪」下拉（S.opener 不再使用）。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
rep('      const L = U.filter(u => u.kind === "ally" && !u.gone && !u.sm && u.id === S.opener).map(u => [u, fx(u, "start").filter(e => /^秘技/.test(e.note || ""))]);   // 只有开怪的那位（S.opener）',
    '      const L = U.filter(u => u.kind === "ally" && !u.gone && !u.sm).map(u => [u, fx(u, "start").filter(e => /^秘技/.test(e.note || ""))]).filter(([u, F]) => F.some(e => e.type === "hitd"));   // 攻击型秘技（有秘技伤害的）才算开怪秘技；加状态的、领域类的不算')
s = s.replace('if (k === "opener") { if (el.value) S.opener = el.value; else delete S.opener; update(); return; }\r\n      ', '')
s = s.replace('''        <label title="用秘技攻击敌人进战的那位：敌人转阶段时，她 / 他的开怪秘技再触发一次">开怪 <select data-s="opener">${opt([["", "（不算）"], ...S.units.filter(x => x.kind === "ally" && !x.sm).map(x => [x.id, x.name])], S.opener || "")}</select></label>\r\n''', '')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/tech47b.py）</b>。更正上一条：<b>开怪秘技只算攻击型秘技</b>（用户说明：像银狼这种打敌人的；真珠、爻光那种给自己加状态的、阿哈的领域都不算）。转阶段时，进战效果里有秘技伤害的角色，她 / 他的秘技效果再生效一次；银狼秘技盲盒照旧每次转阶段触发。去掉了「开怪」下拉。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
