"""tv 161（2026-11-23）：差异清单第 37 批
1. 寒鸦 1215 E1（121501）“持有终结技效果的我方目标消灭敌方目标时，寒鸦行动提前15%，该效果每回合只能触发1次”：
   以前默认关、任何人消灭都算；新条件 evb（DB 同名）= 事件对象身上有效果持有者给的这组增益（键 = 持有者 id:bk），
   寒鸦 E1 用 evb hyu（终结技的速度增益），默认开。
2. 乱破 1317 行迹忍法帖•魔天（1317102）“精英级别及以上的敌方目标的弱点被击破时”：新条件 elt = 事件对象（被击破的敌人）
   按敌人模板等级是首领 / 强敌 / 精英（MON r = B / L / E；没选模板的敌人卡按精英算，和以前一样）。

用法：python3 tools/fix161.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 161
F = Fix(sys.argv[1], TV, sys.argv[2])


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


F.has('r:121501', '持有终结技效果的我方目标消灭敌方目标时，寒鸦行动提前#')
for r in F.C[1215]['eid']:
    if r['r'] == 1:
        assert len(r['eff']) == 1 and r['eff'][0].get('off') == 1
        r['eff'][0] = {'y': 'advance', 't': 'kill', 'tg': 'self', 'v': 15, 'ew': 'any', 'ac': 1, 'evb': 'hyu',
                       'n': 'E1 一心：持有寒鸦终结技效果的我方目标消灭敌方目标时寒鸦行动提前 15%（每回合 1 次；按消灭者身上有没有终结技的速度增益）'}
F.touch(1215)
F.hast(1317, '忍法帖•魔天', '精英级别及以上的敌方目标')
for frag, t in [('行迹忍法帖•魔天：精英级别及以上的敌方目标的弱点被击破时恢复 10 点能量', 'break'), ('行迹忍法帖•魔天：精英级别及以上的敌方目标的弱点被击破时额外获得 1 点充能', 'break')]:
    e = F.eff(1317, frag); oldn = e['n']
    e['elt'] = 1; e['n'] = oldn.replace('（按敌人都是精英及以上算，打小怪时关掉）', '（按敌人模板的等级自动判断；没选模板的敌人卡按精英算）')
    fx = fix_of(1317); fx['drop'].append(oldn); fx['trig'][oldn] = t; fx['map'][oldn] = e['n']; fx['add'].append(e['n']); fx['keep'] = 1
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.evb) e.evBk = x.evb; if (x.elt) e.eltOnly = 1;')
F.rep('      if (eff.evSt) {',
      '      if (eff.evBk) { const H = src ? (ownerOf(src) || src) : null, k0 = H ? H.id + ":" + eff.evBk : null; if (!k0 || !evTarget || !(evTarget.buffs || []).some(b => b.key === k0 || String(b.key).startsWith(k0 + ":"))) return; }   // 事件对象身上有自己给的这组增益（寒鸦 E1，tv 161）\n'
      '      if (eff.eltOnly) { const m0 = evTarget && evTarget.kind === "enemy" ? monOf(evTarget) : null; if (m0 && m0.r && !["B", "L", "E"].includes(m0.r)) return; }   // 事件对象是精英级别及以上的敌人（乱破忍法帖•魔天）\n'
      '      if (eff.evSt) {')

log = """<li><b>2026-11-23（差异清单第 37 批）：tv 161（tools/fix161.py）</b>。① 寒鸦 E1“持有终结技效果的我方目标消灭敌方目标时行动提前 15%（每回合 1 次）”：以前默认关、谁消灭都算；现在默认开，按消灭者身上有没有寒鸦终结技的增益判断。② 乱破行迹忍法帖•魔天“精英级别及以上的敌人被击破时 +1 充能、回 10 能量”：按敌人模板的等级（首领 / 强敌 / 精英）自动判断，打普通怪不再触发。<b>对已有配置</b>：只在开了“我方伤害扣敌人生命值”（消灭）或有击破时有影响。</li>"""
record = """2026-11-23（差异清单第 37 批）：tv 161（tools/fix161.py）。寒鸦 E1 evb hyu 默认开；乱破魔天 elt。新条件 evBk / eltOnly。"""
F.finish('差异清单第 37 批（寒鸦 E1、乱破忍法帖•魔天）', log, record)
print('done tv', TV)
