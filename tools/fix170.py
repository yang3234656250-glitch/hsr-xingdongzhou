"""tv 170（2026-11-23）：差异清单第 46 批
貊泽 1223 天赋（122304）“我方目标攻击【猎物】后，貊泽会额外造成1次……附加伤害，并消耗1点充能……天赋的追加攻击不会消耗充能”：
1. 以前只算队友（aw others），貊泽自己的终结技攻击【猎物】也该消耗充能：补 aw self + aa ult 两条（天赋追加攻击照旧不算）。
2. 以前队友任何攻击都算打到【猎物】；新条件 hbk（DB 同名，字段 hitBk）= 这次攻击击中的敌人里有带持有者这组增益（bk bz，【猎物】的追加攻击易伤）的；
   没放敌人卡时不检查（和以前一样）。

用法：python3 tools/fix170.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 170
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('122304', '我方目标攻击【猎物】后，貊泽会额外造成#次等同于自身#攻击力的雷属性附加伤害，并消耗#点充能')
F.has('122304', '天赋的追加攻击不会消耗充能')
c = F.C[1223]
a = F.eff(1223, '天赋：队友攻击【猎物】后消耗 1 点充能'); b = F.eff(1223, '天赋：同上，【猎物】的充能 −1')
olda, oldb = a['n'], b['n']
a['hbk'] = 'bz'; b['hbk'] = 'bz'
a['n'] = '天赋：队友攻击【猎物】后消耗 1 点充能（计入发动追加攻击所需的 3 点；按这次攻击有没有击中【猎物】）'
b['n'] = '天赋：同上，【猎物】的充能 −1，到 0 时解除【猎物】、貊泽回场'
i = c['eff'].index(b)
a2 = dict(a, aw='self', aa='ult', n='天赋：貊泽自己的终结技攻击【猎物】后也消耗 1 点充能（天赋的追加攻击不算）')
b2 = dict(b, aw='self', aa='ult', n='天赋：同上（貊泽终结技），【猎物】的充能 −1')
c['eff'][i + 1:i + 1] = [a2, b2]
fx = F.FIX.setdefault('1223', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
for o, n in ((olda, a['n']), (oldb, b['n'])):
    fx['drop'].append(o); fx['trig'][o] = 'atk'; fx['map'][o] = n; fx['add'].append(n)
fx['add'] += [a2['n'], b2['n']]; fx['keep'] = 1
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.hbk) e.hitBk = x.hbk;')
F.rep('      if (eff.evSt) {',
      '      if (eff.hitBk && src && U.some(z => z.kind === "enemy")) { const H = ownerOf(src) || src, k0 = H.id + ":" + eff.hitBk + ":"; if (!hitEns().some(z => (z.buffs || []).some(b => String(b.key).startsWith(k0)))) return; }   // 这次攻击击中了带这组增益的敌人（貊泽【猎物】，tv 170）\n'
      '      if (eff.evSt) {')

log = """<li><b>2026-11-23（差异清单第 46 批）：tv 170（tools/fix170.py）</b>。貊泽天赋“我方目标攻击【猎物】后消耗 1 点充能”：① 貊泽自己的终结技攻击【猎物】也算（以前只算队友；天赋的追加攻击仍不算）；② 放了敌人卡时只有击中【猎物】的攻击才算（以前队友打哪个敌人都算）。<b>对已有配置</b>：有貊泽的方案【猎物】会更早解除（终结技也扣充能），多敌人时打别的敌人不再扣，貊泽回场时机会变。</li>"""
record = """2026-11-23（差异清单第 46 批）：tv 170（tools/fix170.py）。貊泽天赋 aw self + aa ult；新条件 hbk（hitBk）。"""
F.finish('差异清单第 46 批（貊泽【猎物】充能）', log, record)
print('done tv', TV)
