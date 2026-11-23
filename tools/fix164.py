"""tv 164（2026-11-23）：差异清单第 40 批
白厄 1408 E1（140801）“卡厄斯兰那的额外回合的基础速度继承比例提高至66%。单场战斗中每有1个敌方目标被消灭，使其额外提高1.5%，最多提高至84%”：
后半没做（说明让用户自己改）。召唤物模板新字段 lrk = [几魂起, 每消灭 1 个敌人 +%, 上限 %]：spdOf 里卡厄斯兰那的继承比例 = 卡片比例 + 本场被消灭敌人数 × 1.5（最多 84）；
simulate 里 killN 在 killEnemy 时 +1（重新登场的敌人再被消灭也算）。只有开了“我方伤害扣敌人生命值”（会消灭敌人）时有变化。

用法：python3 tools/fix164.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 164
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('r:140801', '单场战斗中每有#个敌方目标被消灭，使其额外提高#，最多提高至#')
c = F.C[1408]
sm = [m for m in c['sm'] if m['k'] == 'khaslana']; assert len(sm) == 1 and 'lrk' not in sm[0]
sm[0]['lrk'] = [1, 1.5, 84]
for r in c['eid']:
    if r['r'] == 1: r['notes'] = [n for n in r.get('notes', []) if '1.5%' not in n]
F.touch(1408)
F.rep('    const spdOf = u => {', '    let killN = 0;   // 本场被消灭的敌人数（白厄 1 魂：卡厄斯兰那继承比例，tv 164）\n    const spdOf = u => {')
F.rep('num(o.base, 100) * num(u.sm.ratio) / 100 * u.spbF',
      'num(o.base, 100) * ((L => num(u.sm.ratio) + (L && num(o.eid) >= num(L[0]) ? Math.max(0, Math.min(num(L[2]) - num(u.sm.ratio), killN * num(L[1]))) : 0))((smDef(u) || {}).lrk)) / 100 * u.spbF')
F.rep('      en.ehc = 0; en.gone = true; if (num(en.rev) > 0)', '      killN++; en.ehc = 0; en.gone = true; if (num(en.rev) > 0)')
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs;')   # 占位：确认没有被别的批次改掉

log = """<li><b>2026-11-23（差异清单第 40 批）：tv 164（tools/fix164.py）</b>。白厄 1 魂后半“单场战斗中每有 1 个敌方目标被消灭，卡厄斯兰那的继承比例额外 +1.5%，最多 84%”：以前要自己改卡片比例，现在开了“我方伤害扣敌人生命值”时按实际消灭数自动加（召唤物模板新字段 lrk）。<b>对已有配置</b>：没开敌人掉血的方案不变；开了的 1 魂以上白厄变身后额外回合更密。</li>"""
record = """2026-11-23（差异清单第 40 批）：tv 164（tools/fix164.py）。白厄卡厄斯兰那 sm.lrk [1, 1.5, 84]，simulate killN。"""
F.finish('差异清单第 40 批（白厄 1 魂按消灭数提高继承比例）', log, record)
print('done tv', TV)
