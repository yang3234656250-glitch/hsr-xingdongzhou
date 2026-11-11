"""界面第 2 轮：角色卡下半部分（行动 / 能量 / 终结技 / 效果）分段标题 + 能量改成两列列表 + 折叠条样式。只改 HTML / CSS，不改任何数据和计算。
用法：python3 tools/ui2.py index.html"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)
rep('''        ${u.kind === "ally" && !u.sm ? actRowHtml(u, i) : ""}''', '''        ${u.kind === "ally" && !u.sm ? `<div class="sec-t">行动 <em>普攻 / 战技</em></div>` + actRowHtml(u, i) : ""}''')
rep('''    return `<div class="row">
          <label for="ac-${u.id}">平时 ''', '''    return `<div class="row act-row">
          <label for="ac-${u.id}">平时 ''')
rep('''          : (c => `<div class="row">
          <label for="em-${u.id}">''', '''          : (c => `<div class="sec-t">${eName(u)} <em>上限 / 回复</em></div><div class="row en-row">
          <label for="em-${u.id}">''')
rep('''        <div class="ult-list"><span class="hint">开大时机：</span>${ultChips(ultKeysOf(u),''', '''        <div class="sec-t">终结技 <em>开大时机</em></div>
        <div class="ult-list ult-when"><span class="hint">开大时机：</span>${ultChips(ultKeysOf(u),''')
rep('''        <div class="effects">
          ${effHead(u, i)}''', '''        <div class="sec-t">效果 <em>${u.kind === "ally" && !u.sm ? "卡片上的 / 行迹面板" : "这张卡上的"}</em></div>
        <div class="effects">
          ${effHead(u, i)}''')
rep('''        ${u.kind === "enemy" ? `<div class="row">
          <div class="pickwrap">敌人模板 ''', '''        ${u.kind === "enemy" ? `<div class="sec-t">敌人 <em>模板 / 出招</em></div><div class="row eq-row en-mon">
          <div class="pickwrap">敌人模板 ''')
css = '''
/* ===== 界面第 2 轮：角色卡下半部分（行动 / 能量 / 终结技 / 效果） ===== */
.unit .en-row{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:0 16px; align-items:stretch; }
.unit .en-row > label{ display:flex; justify-content:space-between; align-items:center; gap:6px; padding:4px 2px; font-size:12.5px; color:#d5e2ea; border-bottom:1px solid rgba(190,225,240,.10); min-width:0; }
.unit .en-row > label input[type=number]{ width:72px !important; text-align:right; border:none; background:none; padding:1px 2px; font-size:14px; font-weight:600; color:#fff; border-radius:4px; }
.unit .en-row > label input[type=number]:focus{ background:rgba(111,227,236,.10); box-shadow:none; }
.unit .en-row > label input::placeholder{ color:rgba(160,180,200,.55); font-weight:500; }
.unit .en-row > label:has(input[type=checkbox]){ justify-content:flex-start; color:#b9cad6; }
.unit .act-row{ gap:6px 14px; }
.unit .act-row > label{ font-size:12.5px; color:#d5e2ea; }
.unit .act-row select{ border-radius:999px; padding:3px 10px; border-color:var(--line-2); background:rgba(18,30,52,.72); }
.unit .turn-acts{ padding:6px 8px; border:1px solid rgba(122,206,224,.14); border-radius:8px; background:rgba(6,11,22,.45); }
.unit .turn-acts:empty{ display:none; }
.unit > details:not(.dmg-mult){ border:1px solid rgba(122,206,224,.16); border-radius:8px; background:rgba(8,13,26,.45); padding:0 10px; }
.unit > details:not(.dmg-mult) > summary{ list-style:none; padding:6px 0; font-size:12px; letter-spacing:.04em; color:#a8dce8; display:flex; align-items:center; gap:6px; }
.unit > details:not(.dmg-mult) > summary::-webkit-details-marker{ display:none; }
.unit > details:not(.dmg-mult) > summary::before{ content:"▸"; color:var(--accent); font-size:10px; }
.unit > details[open]:not(.dmg-mult) > summary::before{ content:"▾"; }
.unit > details[open]:not(.dmg-mult){ padding-bottom:8px; }
.unit .ult-when{ padding:6px 8px; border:1px solid rgba(183,156,255,.20); border-radius:8px; background:linear-gradient(90deg, rgba(183,156,255,.08), rgba(8,13,26,.4)); }
.unit .ult-targets{ padding:4px 2px; }
.unit .eff-head{ padding:2px 0 0; }
.unit .eff-head button{ border-radius:999px; }
.unit .add-effect{ border-style:dashed; color:#a8dce8; }
.unit .en-mon > label{ align-self:end; padding-bottom:4px; }
.unit.fold .sec-t{ display:none; }
@media (max-width:420px){ .unit .en-row{ gap:0 12px; } .unit .en-row > label{ font-size:12px; white-space:nowrap; } .unit .en-row > label input[type=number]{ width:50px !important; font-size:13px; } .unit .stat-row > label, .unit .dmg-row > label{ white-space:nowrap; font-size:12.5px; } .unit .stat-row > label input[type=number], .unit .dmg-row > label input[type=number]{ width:64px !important; } }
'''
anchor = '@media (max-width:420px){ .unit-head .portrait{ width:84px; height:108px; } .unit-head .swatch{ left:80px; top:102px; } }\n'
rep(anchor, anchor + css.lstrip('\n'))
li = '<li><b>2026-11-11（界面第 2 轮：角色卡下半部分）</b>：卡片下半部分分成「行动」「能量」「终结技」「效果」几段，能量那一排改成和属性一样的两列列表，折叠的几条（没识别的描述、计数器 · 召唤物）改成细条，敌人卡加「敌人」分段。只改样式和排版，数据和计算都没动。</li>'
i = s.index('<li>', s.index('id="changelog"')); s = s[:i] + li + '\n' + ' ' * 14 + s[i:]
open(p, 'w', encoding='utf8').write(s); print('ok')
