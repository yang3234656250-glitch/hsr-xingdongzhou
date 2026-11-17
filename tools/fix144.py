# tv 144（可重复运行）：拿 4.7 王棋实战录像逐段对出来的两处
# ① 位面饰品「神的瞬息欢愉」2 件“装备者欢愉度 ≥40% 时进战行动提前 40%”：以前按卡片上的欢愉度判断，
#    阿哈卡片欢愉度 20%（行迹盒中蕴藏的世界的 +150% 在战斗里才加）→ 不提前；录像里阿哈第一次行动在 18 行动值（= 30% + 40% 提前）。
#    现在按战斗中的欢愉度（卡片 + 自身 / 全队的欢愉度增益）判断。
# ② 真珠卡片上【终结技额外回合】有两条：旧说明那条在以前的模板更新里没被换掉，新说明的又加了一条 → 美学底本每次得到 2 个额外回合、
#    2 × 60 个临时笑点。官方原文只有 1 个额外回合；录像里银狼隐藏分只涨一次 60。迁移时去掉旧说明那条。
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

OLDN = '2件：装备者欢愉度 ≥40% 时，进入战斗时行动提前 40%（按卡片上的欢愉度）'
NEWN = '2件：装备者欢愉度 ≥40% 时，进入战斗时行动提前 40%（按战斗中的欢愉度：卡片 + 行迹 / 队友的欢愉度增益）'
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
hit = 0
for r in db['relics']:
    for k in ('p2', 'p4'):
        for e in r[k]['eff']:
            if e.get('n') == OLDN: e['n'] = NEWN; hit += 1
assert hit or NEWN in line
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]

# 战斗中的欢愉度
rep('    const dbV = b =>', '''    // 战斗中的欢愉度：卡片 + 自身 / 全队的欢愉度增益（不带条件、不限伤害类型的那些；召唤物按主人）
    const elBattle = u => { const o = ownerOf(u) || u; let x = num(o.el, 0); for (const b of [...(o.buffs || []), ...TEAM0.buffs.filter(z => z.who === "all")]) if (b.kind === "d" && b.st === "el" && !b.ec && !b.sc && !(b.shK && TEAM0.buffs.some(y => y.key === b.shK))) x += num(dbV(b)); return x; };
    const dbV = b =>''')
rep('      if (eff.mel && src && num(src.el, 0) < num(eff.mel)) return;   // 装',
    '      if (eff.mel && src && elBattle(src) < num(eff.mel)) return;   // 装')

OLDX = '终结技（队伍有 4 名欢愉角色时；额外回合结束收回笑点）；阿哈升格后额外回合结束保留 10%（阿哈 2 魂 20%）笑点；目标在额外回合开始时获得 30 点绝活共赏'
NEWX = OLDX + '；2 魂起额外回合开始时的笑点和好活当赏提高 100%（60→120、30→60）'
rep('  function fixTpl143(s) {',
    '  // tv 144：神的瞬息欢愉 2 件按战斗中的欢愉度（说明换掉，装备了的卡片重建装备效果）；真珠卡上旧说明的【终结技额外回合】和新说明的重复了，去掉旧的（tools/fix144.py）\n'
    '  function fixTpl144(s) { const keep = S; S = s; try { const OX = ' + json.dumps(OLDX, ensure_ascii=False) + ', NX = ' + json.dumps(NEWX, ensure_ascii=False) + ';\n'
    '    for (const u of s.units) { if (u.kind !== "ally" || u.sm) continue;\n'
    '      if ((u.effects || []).some(e => e.note === NX && e.type === "xturn")) u.effects = u.effects.filter(e => !(e.note === OX && e.type === "xturn"));\n'
    '      if ([u.rA, u.rB, u.rP].some(r => +r === 329)) applyEquip(u); } } finally { S = keep; } }\n'
    '  function fixTpl143(s) {')
rep('    fixTpl143(s);\n    s.tv = 143;', '    fixTpl143(s);\n    fixTpl144(s);\n    s.tv = 144;')
rep('    if (s.tv >= 143) return;', '    if (s.tv >= 144) return;')
rep('  if (!(S.tv >= 143)) { migrateTpl(S);', '  if (!(S.tv >= 144)) { migrateTpl(S);')
rep('if (!(s.tv >= 143)) fixTpl143(s); } finally { S = keep; } s.tv = 143; return; }', 'if (!(s.tv >= 143)) fixTpl143(s); if (!(s.tv >= 144)) fixTpl144(s); } finally { S = keep; } s.tv = 144; return; }')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17：tv 144（tools/fix144.py）</b>。拿 4.7 王棋实战录像逐段对出来的两处。① 位面饰品<b>神的瞬息欢愉</b> 2 件“装备者欢愉度 ≥40% 时进战行动提前 40%”：以前按卡片上的欢愉度判断，阿哈卡片 20%（行迹盒中蕴藏的世界的 +150% 战斗里才加）就不提前；录像里阿哈第一次行动在 18 行动值（= 行迹 30% + 饰品 40%）。现在按战斗中的欢愉度（卡片 + 自身 / 全队的欢愉度增益）判断。② <b>真珠卡片上【终结技额外回合】重复了两条</b>（旧说明那条在以前的模板更新里没换掉），美学底本每次得到 2 个额外回合、2 × 60 临时笑点；官方只有 1 个，录像里银狼隐藏分也只涨一次 60。迁移时去掉旧说明那条。对已有配置：装了这件饰品的欢愉角色开局可能提前；有重复那条的真珠队伍，银狼第一次无敌玩家不再在开大那一刻把强普全部打完。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok', hit)
