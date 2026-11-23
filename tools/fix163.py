"""tv 163（2026-11-23）：差异清单第 39 批
1. 飞霄 1220 天赋（122004）“发动此攻击时使自身造成的伤害提高60%，持续2回合”只指天赋的追加攻击：
   以前 t fua 在终结技“视为追加攻击”时也触发。新条件 rfu（DB 同名，字段 realFua）= 只在真正的追加攻击时生效（fuaHooks 记 fuaAs）。
2. 托帕 1112 E6（111206）“【涨幅惊人！】的攻击次数额外增加1次，账账火属性抗性穿透提高10%”：以前开大后 d 2（2 回合），
   改成跟着【涨幅惊人！】：持续到次数用完（d 0 + 次数用完时清掉），只对火属性（tel 火）。

用法：python3 tools/fix163.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 163
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('122004', '发动此攻击时使自身造成的伤害提高#，持续#回合')
e = F.eff(1220, '天赋：发动追加攻击时伤害 +60%'); oldn = e['n']
e['rfu'] = 1; e['n'] = '天赋：发动天赋的追加攻击时伤害 +60%（5 魂 66%），持续 2 回合（终结技“视为追加攻击”不算）'
fx = F.FIX.setdefault('1220', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
fx['drop'].append(oldn); fx['trig'][oldn] = 'fua'; fx['map'][oldn] = e['n']; fx['add'].append(e['n']); fx['keep'] = 1
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.rfu) e.realFua = 1;')
F.rep('    const fuaHooks = (u, as) => {\n      const prev = evTarget; evTarget = u;\n      try {\n',
      '    let fuaAs = false;   // 正在结算的是“视为追加攻击”（realFua 条件用）\n    const fuaHooks = (u, as) => {\n      const prev = evTarget, pAs = fuaAs; evTarget = u; fuaAs = !!as;\n      try {\n')
F.rep('      } finally { evTarget = prev; }\n      const la = u.lastAct; u.lastAct = "fua";',
      '      } finally { evTarget = prev; fuaAs = pAs; }\n      const la = u.lastAct; u.lastAct = "fua";')
F.rep('      if (eff.evSt) {', '      if (eff.realFua && fuaAs) return;   // 只算真正的追加攻击（飞霄天赋，tv 163）\n      if (eff.evSt) {')

F.has('r:111206', '且攻击时火属性抗性穿透提高#')
e6 = F.eid(1112, 6)['eff']
z = [x for x in e6 if x.get('bk') == 'e6']; assert len(z) == 1 and z[0]['d'] == 2
z[0].update({'d': 0, 'tel': '火', 'n': 'E6：【涨幅惊人！】期间账账火属性抗性穿透 +10%（到次数用完为止）'})
e6.append({'y': 'dbuf', 't': 'atk', 'aw': 'sm', 'tg': 'sm:numby', 'm': 'resPen', 'v': 0, 'd': 0, 'bk': 'e6', 'ltc': 1, 'n': 'E6：【涨幅惊人！】次数用完时抗性穿透结束'})

log = """<li><b>2026-11-23（差异清单第 39 批）：tv 163（tools/fix163.py）</b>。① 飞霄天赋“发动此攻击时伤害 +60%”只在真正的天赋追加攻击时触发（以前终结技“视为追加攻击”也会触发）。② 托帕 E6 火属性抗性穿透 +10% 跟着【涨幅惊人！】走（次数用完才结束，以前是开大后 2 回合），只对火属性。<b>对已有配置</b>：只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 39 批）：tv 163（tools/fix163.py）。飞霄天赋 rfu（fuaAs）；托帕 E6 d 0 + tel 火 + 次数用完清掉。"""
F.finish('差异清单第 39 批（飞霄天赋增伤、托帕 E6）', log, record)
print('done tv', TV)
