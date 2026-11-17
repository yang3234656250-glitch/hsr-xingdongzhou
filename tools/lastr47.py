# 4.7 王棋归寂：最后一管血出现时的机制（用户说明：按 R 键，击破归寂韧性条、我方全体行动提前 100%）。
# 敌人卡开关 lastR（没设过 = 跟着「转阶段骰子」走，所以 4.7 王棋的归寂默认开）；STG 里归寂带 lr。可重复运行，没改 tv。
import re, json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# 界面：骰子开关后面
if 'data-f="lastR"' not in s:
    a = 'data-f="dice">转阶段骰子选阿哈时刻</label>'
    assert s.count(a) == 2, s.count(a)
    s = s.replace(a, a + '<label for="lr-${u.id}" title="4.7 王棋归寂：最后一管血出现时按 R 键，击破归寂的韧性条（弱点击破：行动延后 25%，没有击破伤害），我方全体行动提前 100%（用户说明）。只在开了敌人掉血、有分阶段生命值时有用"><input type="checkbox" id="lr-${u.id}" ${(u.lastR ?? !!u.dice) ? "checked" : ""} data-u="${i}" data-f="lastR">最后一管血按 R</label>')
# 模拟：转阶段进到最后一条血
rep('      if (en.dice && byId.aha) { pendingAha.push(',
    '      if ((en.lastR ?? en.dice) && en.ph === en.phs.length - 1) {   // 4.7 王棋：最后一管血出现时按 R：击破韧性条、我方全体行动提前 100%（用户说明）\n'
    '        en.tcur = 0; en.broken = true; en.dist += 2500;\n'
    '        marks.push({ t, uid: en.id, label: "击破（R）", color: "var(--enemy)", from: "最后一管血" });\n'
    '        const who = U.filter(z => z.kind === "ally" && !z.gone && !z.paused && !(z.sm && z.sm.cd));\n'
    '        for (const z of who) { pull(z, 10000); marks.push({ t, uid: z.id, label: "+100%", color: "var(--enemy)", from: "最后一管血（R）" }); }\n'
    '        addLog(`${en.name} 最后一管血出现，按 R：击破韧性条（行动延后 25%），我方全体行动提前 100%（${who.map(z => z.name).join("、")}）`, false, "var(--enemy)");\n'
    '        { const pb = brkBy; brkBy = null; try { fireEv("break", en); } finally { brkBy = pb; } }\n'
    '      }\n'
    '      if (en.dice && byId.aha) { pendingAha.push(')
# 按关卡放敌人时带上
old = "if (m.dice) u.dice = true;"
if old + " if (m.lr) u.lastR = true;" not in s:
    assert s.count(old) == 1; s = s.replace(old, old + " if (m.lr) u.lastR = true;")
# STG 数据：归寂带 lr
L = s.split('\r\n')
k = [i for i, l in enumerate(L) if l.lstrip().startswith('const STG = ')]
assert len(k) == 1
line = L[k[0]]; pre = line[:line.index('const STG = ') + len('const STG = ')]; body = line[len(pre):]
semi = body.endswith(';'); body = body[:-1] if semi else body
st = json.loads(body); n = 0
for g in st:
    if not str(g.get('g', '')).startswith('异相仲裁·4.7 王棋'): continue
    for f in g['f']:
        for h in f['h']:
            for wave in h:
                for m in wave:
                    if m.get('dice'): m['lr'] = 1; n += 1
assert n >= 1, n
L[k[0]] = pre + json.dumps(st, ensure_ascii=False, separators=(',', ':')) + (';' if semi else '')
s = '\r\n'.join(L)
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（没改 tv；tools/lastr47.py）</b>。4.7 王棋归寂<b>最后一管血</b>出现时的机制（用户说明，录像下半 5:24 那段）：按 R 键击破归寂的韧性条（按弱点击破：行动延后 25%、之后不吃“未击破 ×0.9”，没有击破伤害），我方全体行动提前 100%。敌人卡「转阶段骰子」旁边新开关「最后一管血按 R」，没设过就跟着骰子开关（4.7 王棋的归寂默认开）。对已有配置：只影响开了敌人掉血、放了 4.7 王棋归寂的方案，最后一条血开始后行动顺序会变。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok', n)
