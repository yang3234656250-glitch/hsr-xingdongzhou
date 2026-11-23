"""tv 173（2026-11-23）：差异清单第 49 批
流萤 1310 天赋（131004 / 强化版 1131004）“生命值越低受到的伤害越低，生命值小于等于20%时减伤效果达到最大值，最多降低40%。「完全燃烧」状态下减伤效果维持最大值”：
模板里没有（开了“敌人打我方掉血”时影响）。伤害增益条件新字段 ec.hpl = [下限 %, 上限 %, 状态名]：
按持有者当前生命值线性换算（≥上限 0、≤下限满额；原文只写“越低越低”，线性是推断），持有该状态时按满额。
流萤加一条 dbuf dr 40（ec.hpl [20, 100, 完全燃烧]）。只影响“敌人打我方掉血”。

用法：python3 tools/fix173.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 173
F = Fix(sys.argv[1], TV, sys.argv[2])
S = json.load(open(os.path.join(sys.argv[2], 'character_skills.json'), encoding='utf-8'))
k = '1131004' if '1131004' in S else '131004'
assert '生命值越低受到的伤害越低' in S[k]['desc'] and '「完全燃烧」状态下减伤效果维持最大值' in S[k]['desc'], S[k]['desc']
P = S[k]['params'][9]
dr = round(P[0] * 100, 4); print('流萤天赋减伤', dr, P)
c = F.C[1310]
NN = f'【强化版】天赋：生命值越低受到的伤害越低，≤20% 时最多降低 {dr:g}%（按当前生命值线性换算，线性是推断）；「完全燃烧」状态下维持最大值（只影响敌人打我方掉血）'
assert not any(e.get('n') == NN for e in c['eff'])
c['eff'].append({'y': 'dbuf', 't': 'start', 'tg': 'self', 'm': 'dr', 'v': dr, 'd': 0, 'bk': 'tdr', 'ec': {'hpl': [20, 100, '完全燃烧']}, 'n': NN})
F.touch(1310); F.FIX['1310']['add'].append(NN)
F.rep('      if (c.lost) { f0 *= Math.max(0, 1 - hpPct(u) / 100); if (!(f0 > 1e-9)) return 0; }',
      '      if (c.lost) { f0 *= Math.max(0, 1 - hpPct(u) / 100); if (!(f0 > 1e-9)) return 0; }\n'
      '      if (Array.isArray(c.hpl) && !(c.hpl[2] && hasSt(u, c.hpl[2]))) { const lo = num(c.hpl[0]), hi = num(c.hpl[1], 100), p = hpPct(u); f0 *= p == null ? 0 : Math.max(0, Math.min(1, (hi - p) / Math.max(1e-9, hi - lo))); if (!(f0 > 1e-9)) return 0; }   // 生命值越低越高（流萤天赋减伤，tv 173）')

log = """<li><b>2026-11-23（差异清单第 49 批）：tv 173（tools/fix173.py）</b>。流萤天赋“生命值越低受到的伤害越低，≤20% 时最多降低 40%，「完全燃烧」状态下维持最大值”补上（按当前生命值线性换算，线性是推断；伤害增益条件新字段“按生命值线性”）。<b>对已有配置</b>：只在开了“敌人打我方掉血”时影响流萤受到的伤害。</li>"""
record = """2026-11-23（差异清单第 49 批）：tv 173（tools/fix173.py）。流萤天赋 dr + ec.hpl。"""
F.finish('差异清单第 49 批（流萤天赋减伤）', log, record)
print('done tv', TV)
