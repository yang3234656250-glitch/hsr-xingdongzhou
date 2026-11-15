"""tv 135（2026-11-15）：差异清单第 20 批
瓦尔特 1004 两条「按敌人一直减速」的近似：
  ① 天赋附加伤害 XR tf：击中减速的敌人时额外附加伤害 —— 原来按「一直减速」算
  ② E2「攻击减速目标触发天赋时 +3 能量」：原来手动勾
引擎：edbAll 带 slow（每个敌人是否处于减速：身上有没有「无类型的负数值增益」，和 negOf 的判法一致）；
      XR 行支持 slowAny；效果条件支持 slowMin（主目标处于减速）。

用法：python _src/fix135.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 135
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 1：edbAll 带 slow ----------------
old = 'dot: Object.fromEntries(ens.map(z => [z.id, (z.dots || []).filter(d => !d.gone).map(d => d.k)])) };'
assert F.s.count(old) == 1, F.s.count(old)
F.rep(old, 'dot: Object.fromEntries(ens.map(z => [z.id, (z.dots || []).filter(d => !d.gone).map(d => d.k)])), slow: Object.fromEntries(ens.map(z => [z.id, (z.buffs || []).some(b => !b.kind && num(b.v) < 0)])) };   // slow：这个敌人是否处于减速')

# ---------------- 引擎 2：XR 行 slowAny ----------------
anchor = 'if (r.dotAny)'
assert F.s.count(anchor) == 1, F.s.count(anchor)
F.rep(anchor, 'if (r.slowAny) { const A3 = rec && rec.eAll, mid3 = A3 && A3.ord ? A3.ord[0] : null; if (!(A3 && A3.slow && mid3 != null && A3.slow[mid3])) continue; }   // 主目标处于减速（瓦尔特天赋附加伤害）\n        ' + anchor)

# ---------------- 引擎 3：条件 slowMin ----------------
old2 = 'if (!eff.eWl && !eff.eDk && !eff.eBr && !eff.negMin) return true;'
assert F.s.count(old2) == 1, F.s.count(old2)
F.rep(old2, 'if (!eff.eWl && !eff.eDk && !eff.eBr && !eff.negMin && !eff.slowMin) return true;')
old3 = 'if (!H || !condX(eff, H)) return; }'
assert F.s.count(old3) == 1, F.s.count(old3)
F.rep(old3, 'if (!H || !condX(eff, H)) return; }')
old4 = 'if (eff.negMin && !(negOf(en) >= num(eff.negMin))) return false;'
assert F.s.count(old4) == 1, F.s.count(old4)
F.rep(old4, old4 + ' if (eff.slowMin && !(en.buffs || []).some(b => !b.kind && num(b.v) < 0)) return false;   // 主目标处于减速（瓦尔特 E2）')
old5 = '|| eff.uPk || eff.negMin) {'
assert F.s.count(old5) == 1, F.s.count(old5)
F.rep(old5, '|| eff.uPk || eff.negMin || eff.slowMin) {')
F.rep('if (x.nmin != null) e.negMin = x.nmin;',
      'if (x.nmin != null) e.negMin = x.nmin; if (x.slowMin) e.slowMin = 1;   // 主目标处于减速（瓦尔特 E2）')

# ---------------- 数据 ----------------
F.has('1100404', '击中处于减速状态的敌方目标时，额外造成#次等同于瓦尔特#攻击力的虚数属性附加伤害')
F.has('r:100402', '触发天赋时，瓦尔特恢复#点能量')

row = next(x for x in F.XR['1004'] if x['k'] == 'tf')
row['slowAny'] = True
row['n'] = '天赋：击中处于减速状态的敌人时，额外造成 1 次瓦尔特攻击力 100% 的附加伤害（5 魂 110%；战技 5 段、终结技按敌人数；按主目标是否减速判断）'

for e in F.C[1004]['eid']:
    for z in e['eff']:
        if (z.get('n') or '').startswith('E2 星的凝聚'):
            z['slowMin'] = 1
            z.pop('off', None)
            z['n'] = 'E2 星的凝聚：施放战技攻击处于减速状态的敌人后（触发天赋），额外恢复 3 点能量（按主目标是否减速判断，默认开启）'
            F.touch(1004)

log = """<li><b>2026-11-15（差异清单第 20 批）：tv 135（tools/fix135.py）</b>。<b>瓦尔特</b>两条「按敌人一直减速算」的近似改成按实际状态判断（伤害显示现在带着每个敌人是否处于减速）：① <b>天赋附加伤害</b>（击中减速敌人时额外 100% 攻击力附加伤害）原来一直算；② <b>E2</b>「攻击减速目标触发天赋时 +3 能量」原来手动勾着、默认关，现在按主目标是否减速判断并默认开启。<b>对已有配置</b>：带瓦尔特的方案，这两条只在敌人真的处于减速（战技减速 / 终结技禁锢 / 秘技）时才算；敌人没被减速时伤害和回能会比以前少。</li>"""

record = """2026-11-15（差异清单第 20 批）：tv 135（tools/fix135.py）。引擎：edbAll 带 slow；XR slowAny；条件 slowMin。改：瓦尔特 XR tf 加 slowAny；E2 加 slowMin、默认开。
  未改 / 存疑：减速的判法跟 negOf 一致（身上有无类型的负数值增益）；「每个目标每回合最多 8 次」那类上限没再细分。"""

F.finish('差异清单第 20 批（瓦尔特天赋附加伤害 / E2 按减速判断）', log, record)
print('done tv', TV)
