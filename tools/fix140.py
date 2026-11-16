# tv 140：魔法少女 4 件“每累计 5 笑点额外无视 1% 防御”也是欢愉伤害范围（fix139 漏了）；可重复运行
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
for r in db['relics']:
    if r['id'] == 129:
        for e in r['p4']['eff']:
            if e.get('sc') == 'e': e['sc'] = 'el'
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]
def rep(a, b):
    global s
    if a not in s and b in s: return
    assert s.count(a) == 1, a; s = s.replace(a, b)
rep('    fixTpl139(s);\r\n    s.tv = 139;', '    fixTpl139(s);   // tv 140：再跑一遍 fixTpl139（魔法少女 4 件第二条也改成欢愉伤害范围，tools/fix140.py）\r\n    s.tv = 140;')
rep('    if (s.tv >= 139) return;', '    if (s.tv >= 140) return;')
rep('  if (!(S.tv >= 139)) { migrateTpl(S);', '  if (!(S.tv >= 140)) { migrateTpl(S);')
open(p, 'w', encoding='utf8', newline='').write(s)
