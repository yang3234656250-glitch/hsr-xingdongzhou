"""tv 131（2026-11-15）：差异清单第 16 批
1. 布洛妮娅 1101 E4：其他队友对风弱点敌人施放普攻后追加攻击（每回合 1 次）
   原来手动勾、没判断「普攻」和「风弱点」；现在加 aa（只算普攻）+ ewl（主目标有风弱点）并默认开。
2. 黑塔 1013 天赋：我方攻击使敌人生命值降到 50% 以下时追加攻击
   原来手动勾、且只能在「攻击后」触发；引擎新增事件 ehp50（敌人生命值跌破 50% 那一刻），这条改挂到它上面并默认开。

用法：python _src/fix131.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 131
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎：敌人生命值跌破 50% 的事件 ----------------
old = 'const lost = Math.min(a, Math.max(0, en.ehc)); en.ehc -= a;'
assert F.s.count(old) == 1, F.s.count(old)
F.rep(old, 'const lost = Math.min(a, Math.max(0, en.ehc)); const wasHp = en.ehc; en.ehc -= a; if (en.ehx > 0 && wasHp > en.ehx * 0.5 && en.ehc <= en.ehx * 0.5 && en.ehc > 1e-6) fireEv("ehp50", en);   // 生命值跌破 50%（黑塔天赋）')

# 事件分发：ehp50 不按「谁攻击」过滤（和 break 一样）
old2 = 'if (kind !== "break" && !evOk(e, u, tg)) continue;'
assert F.s.count(old2) == 1, F.s.count(old2)
F.rep(old2, 'if (kind !== "break" && kind !== "ehp50" && !evOk(e, u, tg)) continue;')


# ---------------- 1. 布洛妮娅 E4 ----------------
F.has('r:110104', '我方其他角色对弱点为风属性的敌方目标施放普攻后，布洛妮娅立即进行#次追加攻击')
for e in F.C[1101]['eid']:
    for z in e['eff']:
        if (z.get('n') or '').startswith('E4：其他队友普攻风弱点敌人后追加攻击'):
            z['aa'] = ['basic', 'ebasic']
            z['ewl'] = '风'
            z.pop('off', None)
            z['n'] = 'E4：其他队友对风属性弱点的敌人施放普攻后，布洛妮娅追加攻击 1 次（每回合 1 次；按主目标有没有风弱点判断，默认开启）'
            F.touch(1101)

# ---------------- 2. 黑塔 天赋 ----------------
F.has('101301', '若指定敌方单体生命值百分比小于等于#') if False else None
F.has('r:101301', '若指定敌方单体生命值百分比小于等于#')
for e in F.C[1013]['eff']:
    if (e.get('n') or '').startswith('天赋：我方攻击使敌人生命值降到 50% 以下时追加攻击'):
        oldn = e['n']
        e['t'] = 'ehp50'
        e.pop('off', None)
        e['n'] = '天赋：我方攻击使敌人生命值降到 50% 以下时，黑塔追加攻击 1 次（敌人生命值跌破 50% 那一刻触发，默认开启；要开「我方伤害扣敌人生命值」才有血量）'
        fx = F.FIX.setdefault('1013', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
        fx['drop'].append(oldn)
        fx['add'].append(e['n'])
        fx['trig'][e['n']] = 'atk'
        fx['map'][oldn] = e['n']
        fx.setdefault('off0', []).append(e['n'])

log = """<li><b>2026-11-15（差异清单第 16 批）：tv 131（tools/fix131.py）</b>。① <b>布洛妮娅 E4</b>「其他角色对弱点为风属性的敌方目标施放普攻后，布洛妮娅立即发动 1 次追加攻击」原来手动勾、没判断普攻和风弱点，现在按「队友施放普攻 + 主目标有风属性弱点」判断并默认开启（每回合 1 次）。② <b>黑塔天赋</b>「我方攻击使敌人生命值降到 50% 以下时追加攻击」原来只能挂在「攻击后」、还得手动开；引擎新增「敌人生命值跌破 50%」这个事件，这条改成在跌破那一刻触发并默认开启。<b>对已有配置</b>：布洛妮娅这条要队友打风弱点敌人时才会多一次追击，行动轴可能变；黑塔这条要开「我方伤害扣敌人生命值」（不然敌人没有血量数值）才会触发，没开时和以前一样不触发。</li>"""

record = """2026-11-15（差异清单第 16 批）：tv 131（tools/fix131.py）。引擎：敌人生命值跌破 50% 事件 ehp50（dmgEnemy 里判断，分发时跳过 evOk）。改：布洛妮娅 E4 加 aa basic / ewl 风、默认开；黑塔天赋改 t ehp50、默认开。
  未改 / 存疑：黑塔天赋的「消灭敌人」分支（击杀后重排）没做；布洛妮娅 E4 的「每回合 1 次」沿用已有的 ac。"""

F.finish('差异清单第 16 批（布洛妮娅 E4 普攻风弱点 / 黑塔天赋跌破 50%）', log, record)
print('done tv', TV)
