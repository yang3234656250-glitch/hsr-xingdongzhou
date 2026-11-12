"""tv 98：昔涟「纷争」之诗给万敌那一下的暴伤 +200%；白厄【永续的燃烧】每个额外回合消耗 15% 当前生命值。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 98, sys.argv[2])
C, has = F.C, F.has
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
c = C[1415]; E = c['eff']; x = find(E, '献予「纷争」之诗：万敌处于【血仇】时自动施放'); o = x['n']
n = '献予「纷争」之诗：万敌处于【血仇】时自动施放 1 次不消耗充能的【弑神登神】（按给万敌 1 个额外回合）'; x['n'] = n
E.insert(E.index(x), dict(y='dbuf', t='ult', tg='ultpick', ptp=1404, ns='血仇', so='pick', m='cd', v=200, d=0, bk='fz200', nx='a', n='献予「纷争」之诗：这一下【弑神登神】的暴击伤害 +200%（万敌下一次攻击后移除）'))
c['notes'] = [y.replace('没做：纷争那一下暴伤 +200%、负世', '没做：负世') for y in c.get('notes', [])]
F.rebuild(1415, E, rename={o: n})
c = C[1408]; E = c['eff']; x = find(E, '昔涟献予「负世」之诗：变身时获得【永续的燃烧】'); o = x['n']
n = '昔涟献予「负世」之诗：变身时获得【永续的燃烧】，卡厄斯兰那的额外回合耗尽后不结束变身、刷新全部额外回合（按多 8 次行动；4 点毁伤没算）'; x['n'] = n
E.insert(E.index(x) + 1, dict(y='hpcost', t='ally', aw='sm', tg='self', v=15, m='cur', ns='献予「负世」之诗', n='昔涟献予「负世」之诗：【永续的燃烧】期间卡厄斯兰那每个额外回合消耗 15% 当前生命值（记在这次行动后）'))
F.rebuild(1408, E, rename={o: n})
F.finish('昔涟纷争暴伤、白厄永续的燃烧扣血', '''<li><b>2026-11-13</b>：tv 98（tools/fix98.py）。昔涟「纷争」之诗：万敌处于【血仇】时那一下【弑神登神】暴击伤害 +200%（用完就移除）。白厄持有昔涟给的【永续的燃烧】时，卡厄斯兰那每个额外回合消耗 15% 当前生命值（会触发“生命值降低时”的效果）。</li>''',
'''2026-11-13：昔涟纷争暴伤、白厄永续的燃烧 —— tv 98（tools/fix98.py）。
  未改 / 存疑：【永续的燃烧】的扣血记在卡厄斯兰那行动之后（原文是额外回合开始时）；4 点毁伤、火种超过 12 的暴伤没做''')
