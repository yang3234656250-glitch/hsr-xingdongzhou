"""tv 180（2026-11-23）：差异清单第 56 批
米沙 1312 终结技段数（131203 初始 3 段、最多 10 段；131202 战技 +1 段；131204 我方每消耗 1 个战技点 +1 段；秘技 131207 +2 段；E1 131201 场上每有 1 个敌人额外 +1 段，最多 5）：
以前伤害固定按 4.5 段（DMG u 2.7 = 60% × 4.5）。米沙新加计数【终结技段数】（只累计，最多 7 = 10 − 3）：战技 +1、天赋每消耗 1 个战技点 +1、秘技 +2（用了秘技再启用）、施放终结技后清零；
开大记录多存 oc（开大时的计数），ultDmgOf 按 (3 + 计数，最多 10) + E1 敌人数（最多 5）段 × 每段倍率算。削韧没按段数（终结技效果先于攻击结算，计数已清零），还是 1 段。

用法：python3 tools/fix180.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 180
F = Fix(sys.argv[1], TV, sys.argv[2])
S = json.load(open(os.path.join(sys.argv[2], 'character_skills.json'), encoding='utf-8'))
assert S['131204']['params'][0][1] == 1 and S['131203']['params'][9][0] == 3 and S['131203']['params'][9][4] == 10 and S['131207']['params'][0][1] == 2 and S['131202']['params'][0][2] == 1
c = F.C[1312]; assert c.get('cnt') is None
c['cnt'] = {'n': '终结技段数', 'at': 0, 'max': 7}
L = c['eff']
i = [k for k, e in enumerate(L) if e['n'].startswith('天赋：我方全体每消耗 1 个战技点，米沙恢复')][0]
NA = '天赋：我方全体每消耗 1 个战技点，下一次终结技攻击段数 +1（计数【终结技段数】，最多 +7，即最多 10 段）'
NS = '战技：下一次终结技攻击段数 +1（计数【终结技段数】）'
NT = '秘技停一停吧，你真美丽！：与【梦境监牢】中的敌人进入战斗后，下一次终结技段数 +2（用了秘技再启用）'
NR = '终结技：施放后攻击段数恢复至初始 3 段（计数清零）'
L.insert(i + 1, {'y': 'count', 't': 'skill', 'tg': 'self', 'v': 1, 'n': NS})
L.insert(i + 2, {'y': 'count', 't': 'spUse', 'aw': 'all', 'tg': 'self', 'v': 1, 'n': NA})
L += [{'y': 'count', 't': 'start', 'tg': 'self', 'v': 2, 'off': 1, 'n': NT}, {'y': 'count', 't': 'ult', 'tg': 'self', 'm': 'set', 'v': 0, 'n': NR}]
F.touch(1312, set={'cntName': '终结技段数', 'cntAt': 0, 'cntMax': 7})
F.FIX['1312']['add'] += [NS, NA, NT, NR]
F.rep('ultMarks.push({ md: HT && u === HT ?', 'ultMarks.push({ oc: u.cnt != null ? num(u.cnt) : undefined, md: HT && u === HT ?')
F.rep('    return dmgCalc(u, e, Object.assign({}, m));\n  }\n  // 一次追加攻击',
      '    if (tidOf(u) === "1312" && m.oc != null) {   // 米沙：按这次的攻击段数（3 + 【终结技段数】，最多 10；E1 每个敌人 +1，最多 5），DMG u 是 4.5 段（tv 180）\n'
      '      const nE = m.eAll && m.eAll.ord ? m.eAll.ord.length : enemyCount(), n = Math.min(10, 3 + num(m.oc)) + (num(u.eid) >= 1 ? Math.min(5, nE) : 0);\n'
      '      e = Object.assign({}, e, { v: num(e.v) / 4.5 * n });\n'
      '    }\n'
      '    return dmgCalc(u, e, Object.assign({}, m));\n  }\n  // 一次追加攻击')
log = """<li><b>2026-11-23（差异清单第 56 批）：tv 180（tools/fix180.py）</b>。米沙终结技按实际攻击段数算伤害：初始 3 段，战技 +1 段，我方每消耗 1 个战技点 +1 段（最多 10 段），秘技 +2，1 魂每个敌人再 +1（最多 5）；以前固定按 4.5 段。米沙卡上多了计数【终结技段数】。<b>对已有配置</b>：只影响伤害显示（段数多时伤害明显更高）；削韧仍按 1 段。</li>"""
record = """2026-11-23（差异清单第 56 批）：tv 180（tools/fix180.py）。米沙计数【终结技段数】，ultMarks.oc，ultDmgOf 按段数。"""
F.finish('差异清单第 56 批（米沙终结技段数）', log, record)
print('done tv', TV)
