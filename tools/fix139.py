# tv 139：“欢愉伤害”范围的增益（光锥欢迎来到银河城 / 菇菇嘎嘎 / 一刀不鸽、魔法少女 4 件）以前标成“欢愉技”，强普 / 盲盒 / 普攻 / 终结技这些欢愉伤害吃不到
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    if b in s and a not in s: return
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
# 1) DB：sc e → el
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
hit = []
def fix(lst, tag):
    for e in lst:
        if e.get('sc') == 'e' and '欢愉伤害' in e.get('n', '') and '欢愉技期间' not in e.get('n', ''): e['sc'] = 'el'; hit.append(tag)
for l in db['lcs']: fix(l['eff'], l['id'])
for r in db['relics']:
    for k in ('p2', 'p4'): fix(r[k]['eff'], r['id'])
print('改范围：', hit)
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]
# 2) 计算：el 范围对所有欢愉伤害生效
rep('    const D = st => dsum(DB0e, st, e.key) + asS(DB0e, st), ED = st => dsum(EDB1, st, e.key) + asS(EDB1, st);',
    '    const elD = isLv || e.el || (tidOf(u) === "1506" && e.key === "b2"), dEl = (L, st) => elD ? (L || []).reduce((p, x) => p + (x[0] === st && x[1] === "el" ? num(x[2]) : 0), 0) : 0;   // 范围“欢愉伤害”：所有欢愉伤害都吃（强普 / 盲盒 / 普攻 / 终结技 / 欢愉技）\r\n'
    '    const D = st => dsum(DB0e, st, e.key) + asS(DB0e, st) + dEl(DB0e, st), ED = st => dsum(EDB1, st, e.key) + asS(EDB1, st) + dEl(EDB1, st);')
rep('["m", "忆灵造成的"], ["e", "欢愉技"], ', '["m", "忆灵造成的"], ["e", "欢愉技"], ["el", "欢愉伤害（全部）"], ')
# 3) 迁移
if 'EQFIX139' not in s: rep('  function fixTpl138(s) { const keep = S; S = s; try { fixTpl(s, TPLFIX138); } finally { S = keep; } }',
    '  function fixTpl138(s) { const keep = S; S = s; try { fixTpl(s, TPLFIX138); } finally { S = keep; } }\r\n'
    '  // tv 139：“欢愉伤害”范围的光锥 / 遗器效果从“欢愉技”改成“欢愉伤害（全部）”，装备了的卡片重建装备效果（tools/fix139.py）\r\n'
    '  const EQFIX139 = {"lc": [21064, 23053, 23057], "rel": [129]};\r\n'
    '  function fixTpl139(s) { const keep = S; S = s; try { for (const u of s.units) if (u.kind === "ally" && !u.sm && (EQFIX139.lc.includes(u.lc) || [u.rA, u.rB, u.rP].some(r => EQFIX139.rel.includes(+r)))) applyEquip(u); } finally { S = keep; } }')
rep('    fixTpl138(s);\r\n    s.tv = 138;', '    fixTpl138(s);\r\n    fixTpl139(s);\r\n    s.tv = 139;')
rep('    if (s.tv >= 138) return;', '    if (s.tv >= 139) return;')
rep('  if (!(S.tv >= 138)) { migrateTpl(S);', '  if (!(S.tv >= 139)) { migrateTpl(S);')
open(p, 'w', encoding='utf8', newline='').write(s)
