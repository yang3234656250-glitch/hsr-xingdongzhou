# 手动事件「引爆【爆梗】」（4.7 王棋归寂，官方：我方角色施放【爆梗】时，归寂对我方全体造成大量伤害，移除 1 层【爆梗】）：
# 我方全体当作受到一次攻击（受击回能，默认 10 点 × 各自充能效率，触发“受到攻击时”）。目标选引爆的人（只写进日志）。用户要手动引爆。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('["hit", "受到攻击"], ["fua", "追加攻击"]], v.type)}</select>', '["hit", "受到攻击"], ["fua", "追加攻击"], ["bg", "引爆【爆梗】（4.7 王棋归寂）"]], v.type)}</select>')
rep('          : v.type === "fua" ? "（目标选发动追加攻击的我方角色）"',
    '          : v.type === "bg" ? `（目标选引爆的人；归寂对我方全体造成伤害：全体当作受到攻击）受击回能 <input type="number" id="vv-${v.id}" step="1" min="0" value="${v.value ?? 10}" data-v="${i}" data-f="value" aria-label="受击回能" style="width:52px">`\n'
    '          : v.type === "fua" ? "（目标选发动追加攻击的我方角色）"')
rep('        apply({ id: ev.id, type: ev.type, target: ev.target, value: ev.value }, null, "var(--accent)");\n',
    '        if (ev.type === "bg") {   // 引爆【爆梗】：归寂对我方全体造成伤害（全体受到一次攻击）\n'
    '          const who = byId[ev.target]; addLog(`${who ? who.name : "我方"} 引爆【爆梗】：归寂对我方全体造成伤害（全体受到攻击，受击回能 ${num(ev.value, 10)}）`, false, "var(--enemy)");\n'
    '          marks.push({ t, uid: who ? who.id : (U.find(z => z.kind === "ally") || {}).id, label: "爆梗", color: "var(--enemy)", from: "引爆【爆梗】" });\n'
    '          apply({ id: ev.id, type: "hit", target: "allies", value: num(ev.value, 10) }, null, "var(--enemy)");\n'
    '        } else apply({ id: ev.id, type: ev.type, target: ev.target, value: ev.value }, null, "var(--accent)");\n')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（没改 tv；tools/bg47.py）</b>。手动事件新类型<b>「引爆【爆梗】」</b>（4.7 王棋归寂）：官方说明是我方角色施放【爆梗】时，归寂对我方全体造成大量伤害，所以全体当作受到一次攻击（受击回能默认 10 点，乘各自充能效率；触发“受到攻击时”）。目标选引爆的人，只写进日志。录像里 128 行动值归寂放【埋梗时刻】后，银狼、真珠、爻光先后引爆，爻光开大前挨了 3 次（约 37 能量），这就是页面上她少的能量。归寂放【埋梗时刻】和出招顺序还没做，暂时手动放。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
