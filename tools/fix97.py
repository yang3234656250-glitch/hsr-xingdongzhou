"""tv 97：波提欧行迹蛇之上行；奇缘星魂的追加攻击“视为终结技 / 普攻伤害”套上对应类型的增益。
模板 x.drNot = [自己的状态, %]：自己有这个状态时，受到“没被自己嘲讽的敌人”的伤害降低 %（波提欧【绝命对峙】）。
模板 exe.fAs = "u" / "b"：勾了奇缘星魂时，追加攻击同时吃只对终结技 / 普攻生效的增益（黄泉、丹恒•饮月）。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 97, sys.argv[2])
C, has, hast = F.C, F.has, F.hast
F.rep('''      d *= drOf(tg) * (src && src.kind === "enemy" ?''', '''      { const dn = tg.kind === "ally" && !tg.sm ? tx(tg).drNot : null; if (dn && src && src.kind === "enemy" && hasSt(tg, dn[0]) && !(src.st && src.st["嘲讽"] && src.st["嘲讽"].by === tg.id)) d *= Math.max(0, 1 - num(dn[1]) / 100); }   // 波提欧蛇之上行：受到未处于【绝命对峙】的目标的伤害降低
      d *= drOf(tg) * (src && src.kind === "enemy" ?''')
F.rep('''    const D = st => dsum(DB0, st, e.key), ED = st => dsum(EDB1, st, e.key);''', '''    const asK = e.key === "f" && u.ex && tplOf(u) && tplOf(u).exe ? tplOf(u).exe.fAs : null, asS = (L, st) => asK ? (L || []).reduce((p, x) => p + (x[0] === st && x[1] === asK ? num(x[2]) : 0), 0) : 0;   // 奇缘星魂的追加攻击同时视为终结技 / 普攻伤害：加上只对那一类生效的增益
    const D = st => dsum(DB0, st, e.key) + asS(DB0, st), ED = st => dsum(EDB1, st, e.key) + asS(EDB1, st);''')
hast(1315, '蛇之上行', '波提欧处于【绝命对峙】时，受到未处于【绝命对峙】目标的伤害降低#1[i]%')
c = C[1315]; c['notes'] = [x for x in c.get('notes', []) if '蛇之上行' not in x] + ['行迹蛇之上行：波提欧处于【绝命对峙】时，受到没被他嘲讽的敌人的伤害降低 30%（“敌人打我方掉血”开着时生效）']
F.rebuild(1315, c['eff'], x={'drNot': ['绝命对峙', 30]})
D = lambda cid: next(z for z in F.DB['chars'] if z['id'] == cid)
for cid, k, a, b in ((1308, 'u', '视为终结技伤害；', '视为终结技伤害，吃终结技的增益；'), (1213, 'b', '（视为普攻伤害）', '（视为普攻伤害，吃普攻的增益）')):
    x = D(cid)['exe']; x['fAs'] = k
    for e in x['eff']: e['n'] = e['n'].replace(a, b)
    F.touch(cid)
F.finish('波提欧蛇之上行、奇缘星魂追加攻击的伤害类型', '''<li><b>2026-11-13</b>：tv 97（tools/fix97.py）。波提欧行迹蛇之上行：处于【绝命对峙】时受到没被他嘲讽的敌人的伤害降低 30%。奇缘星魂：黄泉的追加攻击同时吃终结技的增益（天赋的终结技抗性降低、6 魂抗性穿透等），丹恒•饮月的追加攻击同时吃普攻的增益。</li>''',
'''2026-11-13：波提欧蛇之上行、奇缘星魂伤害类型 —— tv 97（tools/fix97.py）。新：x.drNot、exe.fAs。
  未改 / 存疑：fAs 只加“限定那一类”的增益（sc = u / b），限定强化普攻（eb）的不算''')
