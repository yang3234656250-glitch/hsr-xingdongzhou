"""tv 174（2026-11-23）：差异清单第 50 批
星期日 1313 E1（131301）“使目标角色造成伤害时无视目标16%的防御力，召唤物造成伤害时无视目标40%的防御力”：
以前召唤物也按 16%。召唤物 / 忆灵的伤害按主人身上的增益算，所以给目标角色另加一条只算忆灵伤害（sc m）的 +24%（合计 40%）。
账账、神君这类走主人追加攻击倍率的召唤物没区分（仍按 16%）。

用法：python3 tools/fix174.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 174
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('r:131301', '召唤物造成伤害时无视目标#的防御力')
e1 = F.eid(1313, 1)['eff']; assert len(e1) == 1
e1[0]['n'] = 'E1 千纪沉寂之末：施放战技时目标角色造成伤害无视敌方 16% 防御力，持续 2 回合'
e1.append(dict(e1[0], v=24, sc='m', bk='e1m', n='E1：目标的召唤物 / 忆灵造成伤害时无视防御额外 +24%（合计 40%），持续 2 回合'))
F.touch(1313)
log = """<li><b>2026-11-23（差异清单第 50 批）：tv 174（tools/fix174.py）</b>。星期日 E1：目标的忆灵 / 召唤物造成伤害时无视 40% 防御（以前也按 16%）。<b>对已有配置</b>：只影响伤害显示。</li>"""
record = """2026-11-23（差异清单第 50 批）：tv 174（tools/fix174.py）。星期日 E1 忆灵 sc m +24。"""
F.finish('差异清单第 50 批（星期日 E1 召唤物无视防御）', log, record)
print('done tv', TV)
