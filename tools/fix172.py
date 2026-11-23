"""tv 172（2026-11-23）：差异清单第 48 批
新触发 tgd（成为我方技能的施放目标时）：别人施放战技（目标 skpick）或终结技（目标 ultpick）选中这个角色时，在被选中的角色身上触发（自己选自己不算）。
1. 丹恒 1002 天赋（100204）“当丹恒成为我方技能的施放目标时，下一次攻击的风属性抗性穿透提高36%。该效果在2回合后可再次触发”、E2（100202）冷却 −1：
   以前开局一直有（默认关）；改成 tgd 触发、下一次攻击后移除（nx a）、冷却 2 回合（E2 起 1 回合，cdt），默认开，只对风属性（tel 风）。
2. 白厄 1408 天赋（140804）“当白厄成为其他任意目标的技能目标时，获得1点【火种】。若施放者为白厄的队友，还会使白厄的暴击伤害提高30%”：
   以前按“队友施放战技后”近似（+1 火种默认关）；改成 tgd（队友的战技 / 终结技真的选中白厄时），+1 火种默认开。敌人技能选中白厄的情况没做。

用法：python3 tools/fix172.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 172
F = Fix(sys.argv[1], TV, sys.argv[2])
F.has('100204', '当丹恒成为我方技能的施放目标时，下一次攻击的风属性抗性穿透提高#。该效果在#回合后可再次触发')
F.has('r:100202', '天赋的冷却时间减少#回合')
F.has('140804', '当白厄成为其他任意目标的技能目标时，获得#点【火种】。若施放者为白厄的队友，还会使白厄的暴击伤害提高#，持续#回合')


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


e = F.eff(1002, '天赋：成为我方技能目标时下一次攻击风属性抗性穿透 +36%'); oldn = e['n']
assert e.get('off') == 1 and e['t'] == 'start'
del e['off']; e.update({'t': 'tgd', 'nx': 'a', 'cdt': 2, 'xe': 2, 'tel': '风', 'n': '天赋寸长寸强：成为我方技能的施放目标时下一次攻击风属性抗性穿透 +36%（5 魂 39.6%），2 回合后可再次触发'})
fx = fix_of(1002); fx['drop'].append(oldn); fx['trig'][oldn] = 'start'; fx['map'][oldn] = e['n']; fx['add'].append(e['n']); fx['keep'] = 1
fx.setdefault('off0', []).append(oldn)
e2 = F.eid(1002, 2)
e2['eff'] = [dict({k: v for k, v in e.items() if k != 'xe'}, cdt=1, n='E2 气吞山河：天赋冷却 −1 回合（成为技能目标时下一次攻击风抗穿透，1 回合后可再次触发）')]

for frag, newn in [('天赋：成为其他目标的技能目标时 +1 火种', '天赋：成为队友战技 / 终结技的施放目标时 +1 火种（被敌人技能选中没算）'),
                   ('天赋：成为队友技能目标时暴击伤害 +30%', '天赋：成为队友技能的施放目标时暴击伤害 +30%（5 魂 33%），持续 3 回合')]:
    e = F.eff(1408, frag); oldn = e['n']
    was_off = e.get('off') == 1
    e.pop('off', None); e.pop('aw', None); e['t'] = 'tgd'; e['n'] = newn
    fx = fix_of(1408); fx['drop'].append(oldn); fx['trig'][oldn] = 'aSk'; fx['map'][oldn] = newn; fx['add'].append(newn); fx['keep'] = 1
    if was_off: fx.setdefault('off0', []).append(oldn)

F.rep('      if (k === "skill") { u.skN = num(u.skN) + 1; skMarks.push({ t, uid: u.id, n: u.skN }); }   // 第几次施放战技（skpick 目标用）',
      '      if (k === "skill") { u.skN = num(u.skN) + 1; skMarks.push({ t, uid: u.id, n: u.skN }); if (u.effects.some(e => !e.off && trig(e, "skill") && (e.target === "skpick" || e.target === "skpickm"))) { const pk = byId[skPickTarget(u, u.skN, U)]; if (pk && pk !== u && !pk.gone) { const ev0 = evTarget; evTarget = u; try { healFor(pk, "tgd"); } finally { evTarget = ev0; } } } }   // 第几次施放战技（skpick 目标用）；被选中的触发“成为技能目标时”（tv 172）')
F.rep('      if (usesPick) parts.push(`第${u.ultN}次大招目标：${nameOf(pickFor(u))}`);',
      '      if (usesPick) parts.push(`第${u.ultN}次大招目标：${nameOf(pickFor(u))}`);\n      if (usesPick) { const pk = byId[pickFor(u)]; if (pk && pk !== u && !pk.gone) { const ev0 = evTarget; evTarget = u; try { healFor(pk, "tgd"); } finally { evTarget = ev0; } } }   // 被选中的触发“成为技能目标时”（tv 172）')
F.rep('["eGet", "受到队友提供的能量恢复时"]', '["eGet", "受到队友提供的能量恢复时"], ["tgd", "成为我方技能的施放目标时"]', 2)
F.rep('eGet: "受到队友提供的能量恢复时",', 'eGet: "受到队友提供的能量恢复时", tgd: "成为我方技能的施放目标时",')

log = """<li><b>2026-11-23（差异清单第 48 批）：tv 172（tools/fix172.py）</b>。新触发“成为我方技能的施放目标时”：队友的战技 / 终结技真的选中这个角色时触发（按卡片上“每次战技目标 / 每次大招目标”的选择）。① 丹恒天赋寸长寸强：成为技能目标时下一次攻击风抗穿透 +36%，2 回合冷却（E2 1 回合），默认开（以前开局一直有、默认关）。② 白厄天赋：成为队友技能目标时 +1 火种、暴伤 +30%，按真的选中他算（以前按队友施放任何战技近似，+1 火种默认关）。<b>对已有配置</b>：有白厄、且队友的战技 / 大招目标选了白厄的方案，火种会多、开大可能更早；没选中他的不再给暴伤。丹恒只影响伤害。</li>"""
record = """2026-11-23（差异清单第 48 批）：tv 172（tools/fix172.py）。新触发 tgd（skpick / ultpick 选中时，在被选中者身上 healFor）；丹恒天赋 tgd + nx + cdt（E2 1）；白厄天赋两条 tgd。"""
F.finish('差异清单第 48 批（成为技能目标时：丹恒、白厄）', log, record)
print('done tv', TV)
