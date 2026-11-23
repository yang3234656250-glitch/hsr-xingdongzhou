"""tv 178（2026-11-23）：差异清单第 54 批
景元 1204【神君】削韧：以前 TGH f = [15, 0, 0] 每次行动只削一次（= 1 段）；原文每段攻击都削韧，段数 = 3 + 计数【神君段数】（tv 162）。
TGH f 主目标改成 3 段（45），模板 x.tghCnt ["f", 33.333]：每多 1 段 +1/3（神君行动时景元的【神君段数】计数还没清零）。相邻目标的削韧（随机单体 + 相邻）没做。

用法：python3 tools/fix178.py index.html <官方 json 目录>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 178
F = Fix(sys.argv[1], TV, sys.argv[2])
m = re.search(r'const TGH = (\{.*?\});', F.s); T = json.loads(m.group(1))
assert T['1204']['f'] == [15, 0, 0]
T['1204']['f'] = [45, 0, 0]
F.s = F.s[:m.start(1)] + json.dumps(T, ensure_ascii=False, separators=(',', ':')) + F.s[m.end(1):]
c = F.C[1204]; x = c.setdefault('x', {}); assert 'tghCnt' not in x
x['tghCnt'] = ['f', 33.3333]
log = """<li><b>2026-11-23（差异清单第 54 批）：tv 178（tools/fix178.py）</b>。景元【神君】削韧按实际段数（3 + 【神君段数】，每段 5 点）算，以前每次行动只算 1 段。<b>对已有配置</b>：放了敌人卡时景元方案击破更早，敌人行动顺序可能变；相邻目标的削韧没做。</li>"""
record = """2026-11-23（差异清单第 54 批）：tv 178（tools/fix178.py）。景元 TGH f 45 + x.tghCnt f 33.33（按神君段数计数）。"""
F.finish('差异清单第 54 批（景元神君削韧按段数）', log, record)
print('done tv', TV)
