# 4.7 王棋归寂【收束命运的博弈】：转阶段时选「阿哈时刻」= 一次固定计入 20 笑点的额外阿哈时刻（敌人卡开关 dice，可重复运行）
import re
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
if 'data-f="dice"' not in s:
    pat = re.compile(r'(data-f="phs"[^<]*</label>)')
    assert len(pat.findall(s)) == 2
    s = pat.sub(lambda m: m.group(1) + '<label for="dc-${u.id}" title="归寂【收束命运的博弈】：每次转阶段掷骰子，三选一给我方，其余归敌人。勾上 = 每次都选「阿哈时刻」：阿哈立即获得 1 个固定计入 20 笑点的额外回合（另两项【屏障】/ 对我方伤害没做）"><input type="checkbox" id="dc-${u.id}" ${u.dice ? "checked" : ""} data-u="${i}" data-f="dice">转阶段骰子选阿哈时刻</label>', s)
a = '      marks.push({ t, uid: en.id, label: "转阶段", color: "var(--enemy)", from: killer ? killer.name : "" });'
b = a + '\r\n      if (en.dice && byId.aha) { pendingAha.push({ n: 20, from: en.name + "的骰子" }); addLog(`${en.name}【收束命运的博弈】：选「阿哈时刻」，阿哈获得 1 个固定计入 20 笑点的额外回合`, false, "var(--enemy)"); }'
if b not in s:
    assert s.count(a) == 1; s = s.replace(a, b)
old = "if (m.phs) u.phs = m.phs; if (m.ehp) u.ehp = m.ehp;"
if old + " if (m.dice) u.dice = true;" not in s:
    assert s.count(old) == 1; s = s.replace(old, old + " if (m.dice) u.dice = true;")
open(p, 'w', encoding='utf8', newline='').write(s)
