# 银狼普攻说明：“对全体造成致命伤害时给额外回合没建模”已经做了（tools/swcut.py / swcut2.py），说明改掉；并入 tv 144（可重复运行）
import json
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
O = '普攻【狼尊时刻】：100 段弹射共 340%、期间 3 次【头号补给盲盒】、最后 50% 均分；每 60 点【隐藏分】强化普攻伤害 +15%（最多 2 层）（已算；对全体造成致命伤害时给额外回合没建模）'
N = '普攻【狼尊时刻】：100 段弹射共 340%、期间 3 次【头号补给盲盒】、最后 50% 均分；每 60 点【隐藏分】强化普攻伤害 +15%（最多 2 层）（已算；对场上全体造成致命伤害时结束本次技能、额外回合再次施放剩下的部分并延长自身增益也已算，要开“我方伤害扣敌人生命值”）'
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
hit = 0
for c in db['chars']:
    for e in c['eff']:
        if e.get('n') == O: e['n'] = N; hit += 1
assert hit or N in line, 'not found'
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]
rep('    for (const u of s.units) { if (u.kind !== "ally" || u.sm) continue;\n',
    '    for (const u of s.units) { if (u.kind !== "ally" || u.sm) continue;\n'
    '      for (const e of u.effects || []) if (e.note === ' + json.dumps(O, ensure_ascii=False) + ') e.note = ' + json.dumps(N, ensure_ascii=False) + ';   // 银狼普攻说明\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok', hit)
