# 4.7 归寂「清除存在的球戏」的【强烈震荡】推后默认改成 0：用户说明约 129 归寂单点（讥讽的目光）打的是真珠，
# 把这一下的【滋扰】算进去以后，录像里真珠的回合不用再额外推后（以前的 8% 是在补这一下）。敌人卡 qxDl 仍可填。（可重复运行）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    if b in s: return
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
rep('if (zt) { apply({ id: actor.id + "-qx", type: "delay", target: zt.id, value: num(actor.qxDl ?? 8) }',
    'if (zt && num(actor.qxDl ?? 0) > 0) { apply({ id: actor.id + "-qx", type: "delay", target: zt.id, value: num(actor.qxDl ?? 0) }')
rep('（行动延后 ${num(actor.qxDl ?? 8)}%，按录像推算）', '（行动延后 ${num(actor.qxDl ?? 0)}%）')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\r\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\r\n'
    '<li><b>2026-11-18（没改 tv；tools/qx0.py）</b>。4.7 归寂「清除存在的球戏」的【强烈震荡】行动延后默认改成 0（敌人卡字段 qxDl 仍可填）：用户说明第 2 管归寂的单点（讥讽的目光）打的是真珠，把这一下的【滋扰】算上以后，录像里真珠的回合不用再额外推后。复刻方案里归寂的攻击目标要设成真珠。</li>\r\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
