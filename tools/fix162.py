"""tv 162（2026-11-23）：差异清单第 38 批
景元 1204 E4（120404）“【神君】每段攻击后景元恢复2点能量”：以前每次神君行动固定 +6（按 3 段），没按实际段数。
神君段数 = 3 + 战技 / 终结技 / 秘技给的段数（最多 +7，共 10 段）：景元新加计数【神君段数】（只累计，最多 7），
和每条“神君 +1 段”同时 +1；神君行动后先按 E4 回能 2 × (3 + 计数)（4 魂起，写在基础效果里 me 4），再把计数清零。

用法：python3 tools/fix162.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 162
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('r:120404', '【神君】每段攻击后，景元恢复#点能量')
c = F.C[1204]
assert c.get('cnt') is None
c['cnt'] = {'n': '神君段数', 'at': 0, 'max': 7}
adds = []
L = c['eff']
i_skill = max(k for k, e in enumerate(L) if e['n'] == '战技：神君 +1 段（+10 速度）')
i_ult = max(k for k, e in enumerate(L) if e['n'] == '终结技：神君 +1 段（+10 速度）')
i_tech = max(k for k, e in enumerate(L) if e['n'].startswith('秘技摄召威灵：神君第 1 回合 +1 段'))
NS, NU, NT = '战技：神君段数计数 +2（E4 回能按段数）', '终结技：神君段数计数 +3（E4 回能按段数）', '秘技摄召威灵：神君段数计数 +3（用了秘技再启用）'
ins = [(i_tech, {'y': 'count', 't': 'start', 'tg': 'self', 'v': 3, 'off': 1, 'n': NT}),
       (i_ult, {'y': 'count', 't': 'ult', 'tg': 'self', 'v': 3, 'n': NU}),
       (i_skill, {'y': 'count', 't': 'skill', 'tg': 'self', 'v': 2, 'n': NS})]
for i, e in sorted(ins, key=lambda x: -x[0]): L.insert(i + 1, e)
NE = 'E4 惊电烁云：神君每段攻击后景元恢复 2 点能量（按这次的实际段数：3 + 神君段数计数）'
NR = '天赋：神君行动后神君段数计数清零'
L += [{'y': 'energy', 't': 'ally', 'aw': 'sm', 'tg': 'self', 'v': 6, 'vc': [2, 7], 'me': 4, 'm': 'er', 'n': NE},
      {'y': 'count', 't': 'ally', 'aw': 'sm', 'tg': 'self', 'm': 'set', 'v': 0, 'n': NR}]
e4 = F.eid(1204, 4); assert len(e4['eff']) == 1 and e4['eff'][0]['v'] == 6
e4['eff'] = []
F.touch(1204, set={'cntName': '神君段数', 'cntAt': 0, 'cntMax': 7})
F.FIX['1204']['add'] += [NT, NU, NS, NE, NR]

log = """<li><b>2026-11-23（差异清单第 38 批）：tv 162（tools/fix162.py）</b>。景元 E4“【神君】每段攻击后景元恢复 2 点能量”：以前每次神君行动固定 +6（按 3 段），现在按实际段数（3 + 战技 / 终结技 / 秘技给的段数，最多 10 段）。景元卡上多了计数【神君段数】。<b>对已有配置</b>：4 魂以上景元能量更多，开大可能更早。</li>"""
record = """2026-11-23（差异清单第 38 批）：tv 162（tools/fix162.py）。景元计数【神君段数】（max 7），E4 回能 6 + vc [2, 7]（me 4，基础效果里），神君行动后清零。"""
F.finish('差异清单第 38 批（景元 E4 按神君段数回能）', log, record)
print('done tv', TV)
