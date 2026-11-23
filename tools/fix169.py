"""tv 169（2026-11-23）：差异清单第 45 批
1. 雪衣 1214 天赋（121404）“当雪衣的队友施放攻击削减敌方韧性后，雪衣叠加1层【恶报】”：以前队友任何攻击都 +1。
   新条件 tcut（DB 同名，字段 tCut）= 这次攻击真的削减了韧性（toughHit 记 lastCut；没放敌人卡时不检查，和以前一样）。
2. 桂乃芬 1210 E2（121002）“当敌方目标处于灼烧状态时，桂乃芬的普攻与战技对其施加的灼烧伤害倍率提高40%”：
   以前 E2 起一律 +40%；新加持续伤害方式 has / hasn（目标已有 / 没有这种持续伤害时才挂），E2 改成已灼烧的目标按 +40%、没灼烧的按原倍率。

用法：python3 tools/fix169.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 169
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('121404', '当雪衣的队友施放攻击削减敌方韧性后')
e = F.eff(1214, '天赋：队友攻击削减韧性后 +1 恶报'); oldn = e['n']
e['tcut'] = 1; e['n'] = '天赋：队友施放攻击削减敌方韧性后 +1 恶报（没削到韧性不算；没放敌人卡时每次攻击都算）'
fx = F.FIX.setdefault('1214', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
fx['drop'].append(oldn); fx['trig'][oldn] = 'atk'; fx['map'][oldn] = e['n']; fx['add'].append(e['n']); fx['keep'] = 1
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.tcut) e.tCut = 1;')
F.rep('    const toughHit = (who, key) => {', '    let lastCut = 0;   // 这次攻击削掉的韧性（tcut 条件，雪衣天赋，tv 169）\n    const toughHit = (who, key) => {')
F.rep('          en.tcur -= amt;\n', '          en.tcur -= amt; lastCut += amt;\n')
F.rep('nxUse(who, fromFua ? "f" : ACT2K[act] || "m"); toughHit(who, fromFua ? "f" : ACT2K[act]);',
      'nxUse(who, fromFua ? "f" : ACT2K[act] || "m"); lastCut = 0; toughHit(who, fromFua ? "f" : ACT2K[act]);')
F.rep('      if (eff.evSt) {', '      if (eff.tCut && U.some(z => z.kind === "enemy") && !(lastCut > 0)) return;   // 这次攻击削减了韧性（雪衣天赋）\n      if (eff.evSt) {')

F.has('r:121002', '当敌方目标处于灼烧状态时，桂乃芬的普攻与战技对其施加的灼烧状态的伤害倍率提升#')
e2 = F.eid(1210, 2)['eff']; assert len(e2) == 3
base = {(x['t'], x['tg']): x for x in F.C[1210]['eff'] if x['y'] == 'dot'}
new = []
for x in e2:
    b = base[(x['t'], x['tg'])]
    new.append(dict(x, m='has', n=x['n'].replace('（按目标已经处于灼烧算）', '（目标已处于灼烧时）')))
    nb = {k: v for k, v in b.items() if k != 'xe'}; nb['m'] = 'hasn'; nb['n'] = 'E2：' + ('战技' if x['t'] == 'skill' else '行迹缘竿') + '对还没灼烧的目标按原倍率'
    new.append(nb)
F.eid(1210, 2)['eff'] = new
F.touch(1210)
F.rep('          if (eff.mode === "new" && tg.dots.some(z => z.key === key0)) continue;',
      '          if (eff.mode === "new" && tg.dots.some(z => z.key === key0)) continue;\n'
      '          if ((eff.mode === "has" || eff.mode === "hasn") && tg.dots.some(z => num(z.n) > 0 && dkIs(z.k, eff.dk)) !== (eff.mode === "has")) continue;   // 目标已有 / 没有这种持续伤害时才挂（桂乃芬 E2，tv 169）')

log = """<li><b>2026-11-23（差异清单第 45 批）：tv 169（tools/fix169.py）</b>。① 雪衣天赋：队友攻击<b>真的削减了韧性</b>才叠【恶报】（打非弱点 / 已破韧的敌人不算；没放敌人卡时照旧每次攻击都算）。② 桂乃芬 E2：只有对已经处于灼烧的敌人，灼烧倍率才 +40%（以前一律 +40%）。<b>对已有配置</b>：放了敌人卡的雪衣方案【恶报】变少、追加攻击变少；桂乃芬只影响伤害。</li>"""
record = """2026-11-23（差异清单第 45 批）：tv 169（tools/fix169.py）。雪衣 tcut（lastCut）；桂乃芬 E2 dot 方式 has / hasn。"""
F.finish('差异清单第 45 批（雪衣恶报按削韧、桂乃芬 E2）', log, record)
print('done tv', TV)
