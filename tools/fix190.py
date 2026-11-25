"""tv 190（2026-11-25）：差异清单第 65 批
1. 知更鸟•晴歌 1512：
   终结技（151203）“固定恢复等同于#?%能量上限的能量”：10 级 20%，5 魂终结技 +2 级 → 12 级 21.6%（以前没有 lv）。
   忆灵天赋扑翅雀跃的和声（1151203）“伤害提高（60%+气氛值*2%）”：6 级 60% / 2%，3 魂忆灵天赋 +1 级 → 7 级 66% / 2.2%；
   以前 3 魂只换了底数（每点仍 2%），这次每点也跟着换（lx vc）。
   原文公式没有封顶（气氛值本身上限 50，2 魂 70）：晴歌 / 乐手增伤和 Fever 结界无视防御的 vc 第二项（最多计入）从 50 改成 0（不限），
   2 魂气氛值超过 50 时以前少算。
2. 吉尔伽美什 1509：秘技天之锁“进入战斗后……吉尔伽美什立即获得 3 点【兴致】”那条（默认关）只给了速度，
   行迹英雄的孤傲“每获得 1 点【兴致】暴击伤害 +25%（最多 6 层）”没叠；补一条同组（bk ga）sa 3 的叠层，同样默认关。
3. 银狼LV.999 1506 E6【禁限弱点】“全属性基础抗性降低至 0（若基础抗性为 0 则改为对应属性抗性降低 20%）”：
   以前 6 魂一律按抗性 0。现在按敌人模板（或关卡）本来的弱点：本来就是弱点的属性（基础抗性 0）抗性 −20%，其余 0。
   edbAll 多存 w0（每个敌人模板本来的弱点，不含植入的）；dmgCalc 主目标、多目标加权、别的属性附加伤害三处都按它。
   没有敌人资料时：勾了「命中弱点」按本来是弱点（−20%），没勾按 0（同以前）。
   顺带改普攻【狼尊时刻】说明：6 级是 100 段共 240% + 最后一击 100%（合计 340%），以前写成“共 340%、最后 50%”。

用法：python3 tools/fix190.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 190
F = Fix(sys.argv[1], TV, sys.argv[2])

# ---------- 1. 知更鸟•晴歌 ----------
ult = F.SK['151203']; assert '能量上限的能量' in ult['desc']
pu = [p for p in F.prm('151203', 10)]; pu12 = F.prm('151203', 12)
assert 0.2 in pu and 0.216 in [round(x, 4) for x in pu12], (pu, pu12)
assert any(x['id'] == '151203' and x['num'] == 2 for x in F.RK['151205']['level_up_skills'])
mt = F.SK['1151203']; assert '（#' in mt['desc'] or '60' in str(F.prm('1151203', 6))
p6, p7 = F.prm('1151203', 6), F.prm('1151203', 7)
assert 0.6 in p6 and 0.02 in p6 and 0.66 in [round(x, 4) for x in p7] and 0.022 in [round(x, 4) for x in p7], (p6, p7)
assert any(x['id'] == '1151203' and x['num'] == 1 for x in F.RK['151203']['level_up_skills'])
c = F.C[1512]
fx = F.FIX.setdefault('1512', {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
def chg(e, newn):
    old = F.OLD[1512]; on = e['n']; t = [t for n, t in old if n == on]; assert len(t) == 1, on
    fx['drop'].append(on); fx['trig'][on] = t[0]; fx['map'][on] = newn; e['n'] = newn
en = F.eff(1512, '终结技：目标固定恢复等同于其能量上限 20% 的能量')
assert en['y'] == 'energy' and en['m'] == 'maxp' and en['v'] == 20 and 'lv' not in en
en['lv'] = [5, 21.6]
chg(en, '终结技：目标固定恢复等同于其能量上限 20% 的能量（5 魂 21.6%）')
n_dmg = 0
for e in c['eff']:
    if e.get('y') == 'dbuf' and e.get('m') == 'dmg' and e.get('bk') in ('fvd', 'fvb') and e.get('v'):
        assert e['vc'] == [2, 50] and e['lv'] == [3, 66], e
        e['vc'] = [2, 0]; e['lx'] = {'vc': [[2, 0], [2.2, 0]]}; n_dmg += 1
        chg(e, e['n'].replace('（3 魂只按底数 66% 算）', '（3 魂 66% + 气氛值 × 2.2%）'))
    elif e.get('y') == 'dbuf' and e.get('m') == 'defIg' and e.get('bk') == 'fvig' and e.get('v'):
        assert e['vc'] == [0.5, 50], e
        e['vc'] = [0.5, 0]
        chg(e, e['n'])   # 说明不变，只换字段
assert n_dmg == 6, n_dmg
fx['add'] += [e['n'] for e in c['eff'] if e['n'] in fx['map'].values()]
fx['keep'] = 1
assert len(fx['drop']) == 10, fx['drop']

# ---------- 2. 吉尔伽美什 ----------
F.hast(1509, '英雄的孤傲', '本场战斗中，吉尔伽美什每获得#点【兴致】，使自身暴击伤害提高#，该效果最多叠加#层')
F.has('150907', '进入战斗后对敌方全体造成等同于吉尔伽美什#1[i]%攻击力的雷属性伤害，且吉尔伽美什立即获得#3[i]点【兴致】')
g = F.C[1509]
t3 = F.eff(1509, '秘技天之锁：进入战斗后立即获得 3 点【兴致】')
assert t3['y'] == 'spd' and t3['t'] == 'start' and t3['sa'] == 3 and t3.get('off') == 1
NG = '行迹英雄的孤傲：暴击伤害 +25% / 层（秘技天之锁的 3 点；用了秘技再启用）'
g['eff'].insert(g['eff'].index(t3) + 1, {'y': 'dbuf', 'tg': 'self', 'm': 'cd', 'v': 25, 'st': 6, 'd': 0, 'bk': 'ga', 't': 'start', 'sa': 3, 'off': 1, 'n': NG})
F.FIX['1509'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [NG], 'sm': {}}

# ---------- 3. 银狼LV.999 E6 ----------
F.has('r:150606', '全属性基础抗性降低至0（若基础抗性为0则改为对应属性抗性降低20%）')
w = F.C[1506]
inf = [x for e in w['eid'] if e['r'] == 6 for x in e['eff'] if x.get('y') == 'info']; assert len(inf) == 1
assert '已按伤害里的抗性 0 算' in inf[0]['n']
inf[0]['n'] = 'E6：【禁限弱点】——敌方目标拥有全属性弱点，全属性基础抗性降为 0、本来就是弱点的属性（基础抗性 0）抗性 −20%（伤害里按敌人模板 / 关卡的弱点算，没有敌人资料时看「命中弱点」）；强化普攻期间欢愉伤害增笑 50%（见上）'
F.touch(1506)
p = F.prm('150608', 6); assert p[0] == 2.4 and p[2] == 100 and p[3] == 1 and p[4] == 3, p
oi = F.eff(1506, '普攻【狼尊时刻】：100 段弹射共 340%')
on = oi['n']
oi['n'] = on.replace('100 段弹射共 340%、期间 3 次【头号补给盲盒】、最后 50% 均分', '100 段弹射共 240%、期间 3 次【头号补给盲盒】、最后一击 100% 由敌方全体均分（合计 340%）')
assert oi['n'] != on
F.FIX['1506'] = {'drop': [on], 'trig': {on: oi['t']}, 'map': {on: oi['n']}, 'add': [oi['n']], 'sm': {}}

F.rep('w: Object.fromEntries(ens.map(z => [z.id, wkOf(z)])),',
      'w: Object.fromEntries(ens.map(z => [z.id, wkOf(z)])), w0: Object.fromEntries(ens.map(z => [z.id, (m => m && m.w ? String(m.w) : null)(monOf(z))])),')   # 模板本来的弱点（不含植入的，银狼LV.999 E6 用，tv 190）
F.rep('    const res = cfg.weak || swE >= 6 || (w0 != null && !!ELo && w0.includes(ELo)) ? 0 : num(cfg.res);',
      '    const res6 = b => b > 0 ? 0 : b - 20;   // 银狼LV.999 E6【禁限弱点】：基础抗性降至 0，本来就是 0 的（本来的弱点）改为抗性 −20%（tv 190）\n'
      '    const wT0 = EAm && EAm.w0 && EAm.ord && EAm.ord.length ? EAm.w0[EAm.ord[0]] : null;   // 主目标模板本来的弱点\n'
      '    const res = swE >= 6 ? res6(cfg.weak || (wT0 != null && !!ELo && wT0.includes(ELo)) ? 0 : num(cfg.res))\n'
      '      : cfg.weak || (w0 != null && !!ELo && w0.includes(ELo)) ? 0 : num(cfg.res);')
F.rep('        const rM = Math.min(2, Math.max(0.1, 1 - (res - num(cfg.pen) - D("resPen") - spkPen - E2("resRed")) / 100));',
      '        const rI = swE >= 6 && EA.w0 ? res6(EA.w0[id] != null ? (ELo && EA.w0[id].includes(ELo) ? 0 : num(cfg.res)) : (cfg.weak ? 0 : num(cfg.res))) : res;   // 银狼LV.999 E6：每个敌人按自己本来的弱点\n'
      '        const rM = Math.min(2, Math.max(0.1, 1 - (rI - num(cfg.pen) - D("resPen") - spkPen - E2("resRed")) / 100));')
F.rep('        const w = id != null ? W[id] : null, weak = swE >= 6 || (w == null ? !!cfg.weak : w.includes(el));\n',
      '        const w = id != null ? W[id] : null, wT = swE >= 6 ? (id != null && EA0.w0 ? EA0.w0[id] : w) : w, weak = wT == null ? !!cfg.weak : wT.includes(el);\n')
F.rep('        s += Math.min(2, Math.max(0.1, 1 - ((weak ? 0 : num(cfg.res)) - pen - rr) / 100));',
      '        const r0 = weak ? 0 : num(cfg.res);\n'
      '        s += Math.min(2, Math.max(0.1, 1 - ((swE >= 6 ? res6(r0) : r0) - pen - rr) / 100));')

log = """<li><b>2026-11-25（差异清单第 65 批）：tv 190（tools/fix190.py）</b>。按官方原文（Mar-7th StarRailRes character_skills / character_ranks / character_skill_trees）：① <b>知更鸟•晴歌</b>终结技“固定恢复等同于 20% 能量上限的能量”5 魂终结技 +2 级后是 21.6%（以前一直 20%）；忆灵天赋扑翅雀跃的和声“伤害提高（60% + 气氛值 × 2%）”3 魂 +1 级后是（66% + 气氛值 × 2.2%）（以前 3 魂每点仍按 2%）；这两条和 Fever 结界“无视（15% + 气氛值 × 0.5%）防御力”原文都没有封顶，以前最多按 50 点气氛值算，2 魂气氛值上限 70 时少算，现在按实际气氛值。② <b>吉尔伽美什</b>秘技天之锁“进入战斗后立即获得 3 点【兴致】”那条（默认关）补上行迹英雄的孤傲“每获得 1 点【兴致】暴击伤害 +25%”的 3 层（同样默认关，用了秘技要把这两条一起打开）。③ <b>银狼LV.999 6 魂</b>【禁限弱点】“全属性基础抗性降低至 0（<b>若基础抗性为 0 则改为对应属性抗性降低 20%</b>）”：以前一律按抗性 0；现在敌人本来就弱的属性（按敌人模板 / 关卡的弱点，不算别人植入的）抗性 −20%（伤害 ×1.2），其余 0；没放有资料的敌人时，勾了「命中弱点」按本来就弱算。顺带更正普攻【狼尊时刻】说明：6 级是 100 段共 240% + 最后一击 100%（合计 340%，伤害本来就是按 340% 算的）。<b>对已有配置</b>：晴歌 5 魂起被她开大的队友多回 1.6% 能量上限的能量（可能更早开大）；其余只影响伤害显示（开着“我方伤害扣敌人生命值”时可能改变击杀时机）。吉尔伽美什老存档的新条目默认关，用了秘技的请手动打开。</li>"""
record = """2026-11-25（差异清单第 65 批）：tv 190（tools/fix190.py）。知更鸟•晴歌终结技回能 lv [5, 21.6]、增伤 lx vc（3 魂每点 2.2%）、气氛值 vc 不封顶；吉尔伽美什秘技 3 兴致补英雄的孤傲叠层；银狼LV.999 E6 本来的弱点抗性 −20%（edbAll w0）。"""
F.finish('差异清单第 65 批（晴歌 5 魂回能 / 3 魂增伤、吉尔伽美什秘技暴伤、银狼LV.999 6 魂抗性）', log, record)
print('done tv', TV)
