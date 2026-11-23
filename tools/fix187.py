"""tv 187（2026-11-23）：差异清单第 63 批
貊泽 E2（122302）“我方全体目标对成为【猎物】的敌方目标造成伤害时，暴击伤害提高40%”：以前对所有敌人生效。
新伤害条件 ec.ebk："施放者id:键" 这组增益在目标敌人身上（v > 0）才生效；E2 用 ebk "bz:dvuln"（【猎物】的追加攻击易伤标记，只在最新的猎物身上）。
没放敌人卡时按虚拟的“敌人”（EV0），猎物标记也挂在它身上。

用法：python3 tools/fix187.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 187
F = Fix(sys.argv[1], TV, sys.argv[2])
R = json.load(open(os.path.join(sys.argv[2], 'character_ranks.json'), encoding='utf-8'))
assert R['122302']['desc'] == '我方全体目标对成为【猎物】的敌方目标造成伤害时，暴击伤害提高40%。'
c = F.C[1223]; e2 = [x for x in c['eid'] if x['r'] == 2][0]['eff']
a = [x for x in e2 if x['t'] == 'skill'][0]; assert a['m'] == 'cd' and 'ec' not in a
a['ec'] = {'ebk': 'bz:dvuln'}
a['n'] = 'E2：我方全体对【猎物】造成伤害时暴击伤害 +40%（只对猎物生效）'
assert any(x.get('bk') == 'bz' and x.get('m') == 'vuln' and x.get('tg') == 'ehit' for x in c['eff'])
F.touch(1223)
F.rep('c.dfr == null && c.dbf == null && c.dbn == null && c.nwk == null && c.dkSt == null) return f0;',
      'c.dfr == null && c.dbf == null && c.dbn == null && c.nwk == null && c.dkSt == null && c.ebk == null) return f0;')
F.rep('      if (c.est && !hasSt(en, c.est)) return 0;',
      '      if (c.ebk && !(en.buffs || []).some(z => z.kind === "d" && z.key === b.src + ":" + c.ebk && num(z.v) > 0)) return 0;   // 目标身上有施放者的这组增益（貊泽 E2：【猎物】，tv 187）\n'
      '      if (c.est && !hasSt(en, c.est)) return 0;')
log = """<li><b>2026-11-23（差异清单第 63 批）：tv 187（tools/fix187.py）</b>。貊泽 2 魂“对成为【猎物】的敌人造成伤害时暴击伤害 +40%”只对猎物生效了，以前对所有敌人都加。<b>对已有配置</b>：只影响伤害显示（打非猎物的敌人时少了这 40%）。</li>"""
record = """2026-11-23（差异清单第 63 批）：tv 187（tools/fix187.py）。伤害条件 ec.ebk；貊泽 E2 ebk bz:dvuln。"""
F.finish('差异清单第 63 批（貊泽 2 魂只对猎物）', log, record)
print('done tv', TV)
