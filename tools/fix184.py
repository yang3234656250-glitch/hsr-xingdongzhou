"""tv 184（2026-11-23）：差异清单第 60 批
景元 E6（120406）“【神君】每段攻击后会使指定敌方目标额外陷入易伤状态……受到的伤害提高12%，持续至【神君】本次攻击结束，最多叠加3层”：
以前是一条默认关的敌方全体常驻 +36% 易伤（会算进别人的伤害）。去掉它，改在神君伤害里按段数自动算：
第 i 段（从 0 数）主目标多 min(i, 3) × 12% 易伤，主目标那部分伤害 × (1 + Σ / 段数 / 原易伤区)。

用法：python3 tools/fix184.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 184
F = Fix(sys.argv[1], TV, sys.argv[2])
R = json.load(open(os.path.join(sys.argv[2], 'character_ranks.json'), encoding='utf-8'))
assert '受到的伤害提高12%，持续至【神君】本次攻击结束，该效果最多叠加3层' in R['120406']['desc']
c = F.C[1204]; e6 = [x for x in c['eid'] if x['r'] == 6][0]
assert len(e6['eff']) == 1 and e6['eff'][0]['bk'] == 'e6'
e6['eff'] = []
e6['notes'] = ['E6：神君每段攻击后主目标易伤 +12%（最多 3 层，到本次攻击结束）已自动算进神君的伤害（第 2 段起 12%、第 3 段 24%、第 4 段起 36%）']
F.touch(1204)
F.rep('      if (String(T.id) === "1204") e = Object.assign({}, e, { v: num(e.v) * (3 + num(a.oc)) / 3 });   // 神君段数 = 3 + 【神君段数】计数\n      return dmgCalc(o, e, a);\n',
      '      if (String(T.id) === "1204") e = Object.assign({}, e, { v: num(e.v) * (3 + num(a.oc)) / 3 });   // 神君段数 = 3 + 【神君段数】计数\n'
      '      const r = dmgCalc(o, e, a);\n'
      '      if (String(T.id) === "1204" && num(o.eid) >= 6 && r && r.total > 0) {   // E6：每段攻击后主目标易伤 +12%，最多 3 层，到本次攻击结束（tv 184）\n'
      '        const n = 3 + num(a.oc); let s6 = 0; for (let i = 0; i < n; i++) s6 += Math.min(i, 3) * 0.12;\n'
      '        const rm = dmgCalc(o, Object.assign({}, e, { adj: 0, rnd: 0 }), a), mainD = rm ? rm.total - (rm.xr ? num(rm.xr.sum) : 0) : 0;\n'
      '        const add = mainD * s6 / n / Math.max(0.01, num(r.vulnM, 1));\n'
      '        if (add > 0) { r.total += add; r.xr = r.xr || { sum: 0, parts: [] }; r.xr.parts.push({ n: `6 魂：神君每段攻击后主目标易伤 +12%（${n} 段，最多 3 层）`, amt: add }); r.xr.sum += add; }\n'
      '      }\n'
      '      return r;\n')
log = """<li><b>2026-11-23（差异清单第 60 批）：tv 184（tools/fix184.py）</b>。景元 6 魂“神君每段攻击后主目标易伤 +12%，最多 3 层，到本次攻击结束”改成在神君的伤害里按实际段数自动算（第 2 段起 12%、第 3 段 24%、第 4 段起 36%）；以前是一条默认关的敌方全体常驻 +36%（开了会算进别人的伤害），这条去掉了。<b>对已有配置</b>：6 魂景元的神君伤害变高；别人的伤害不再吃到这 36%。</li>"""
record = """2026-11-23（差异清单第 60 批）：tv 184（tools/fix184.py）。景元 E6 去掉 dbuf e6，memDmgOf 按段数给主目标易伤（xr 一项）。"""
F.finish('差异清单第 60 批（景元 6 魂易伤）', log, record)
print('done tv', TV)
