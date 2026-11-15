"""tv 120（2026-11-15）：差异清单第 5 批
① 银狼 1006 E1：终结技攻击后「目标每有 1 个负面效果回 7 点能量，每次最多 5 次」
   原来是固定按 3 个（21 点）、默认关；现在按目标实际负面效果数算（上限 5），并默认开
   引擎：能量效果新增方式 neg（按事件目标身上的负面效果数 × 数值，stCap = 上限次数）
② 卡芙卡 1005 E6：秘技进的触电也要 6 魂加成（+156% → 474.27%、持续 3 回合）
   引擎：持续伤害支持 6 魂专用数值 v6 / d6

用法：python _src/fix120.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 120
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
# ① 能量方式 neg：目标每有 1 个负面效果回 N 点，最多 stCap 次
anchor = 'if (eff.mode === "evp") {'
assert F.s.count(anchor) == 1
add = ('if (eff.mode === "neg") { const E = evTarget && evTarget.kind === "enemy" ? evTarget : U.find(z => z.kind === "enemy" && !z.gone); '
       'const n = E ? Math.min(Math.round(num(eff.stCap, 5)), negOf(E)) : 0; '
       'if (n > 0 && hasEnergy(tg)) { curWhy = `${src && src !== tg ? src.name + "：" : ""}${eff.note || "回能效果"}`; addEnergy(tg, v * n, false); } continue; }   // 按目标身上的负面效果数回能（银狼 E1）\n          ')
F.rep(anchor, add + anchor)

# ② 持续伤害的 6 魂数值：v6 / d6
F.rep('{ k: name, v, vps: num(eff.vps)',
      '{ k: name, v: (num(own.eid) >= 6 && eff.v6 != null ? num(eff.v6) : v), vps: num(eff.vps)')
F.rep('cap: lim, left: Math.max(0, Math.round(num(eff.duration))) }',
      'cap: lim, left: Math.max(0, Math.round(num(num(own.eid) >= 6 && eff.d6 != null ? eff.d6 : eff.duration))) }')
F.rep('if (x.ku) e.killU = 1;',
      'if (x.ku) e.killU = 1; if (x.v6 != null) e.v6 = x.v6; if (x.d6 != null) e.d6 = x.d6;   // 6 魂起换一组数值（卡芙卡秘技的触电）')


def rename_eff(cid, frag, r=None, off0=None, drop_off=False, **chg):
    e = F.eff(cid, frag, r=r)
    old = e['n']
    trig = e.get('t')
    e.update(chg)
    if drop_off:
        e.pop('off', None)
    new = e['n']
    fx = F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
    fx['drop'].append(old)
    fx['add'].append(new)
    fx['trig'][old] = trig
    if new != old:
        fx['map'][old] = new
    if off0:
        fx.setdefault('off0', []).append(new)
    return old, new


# ---------------- ① 银狼 E1 ----------------
F.has('r:100601', '目标每有#个负面效果，银狼恢复#点能量。该效果在每次终结技攻击中最多生效#次')
e1 = F.eid(1006, 1)['eff'][0]
e1.update({'y': 'energy', 't': 'ult', 'tg': 'self', 'm': 'er', 'mode': 'neg', 'v': 7, 'stCap': 5,
           'n': 'E1 社会工程：终结技攻击敌方目标后，目标每有 1 个负面效果，银狼恢复 7 点能量（每次终结技最多 5 次）'})
e1.pop('off', None)

# ---------------- ② 卡芙卡 E6 秘技 ----------------
F.has('r:100506', '终结技、秘技与天赋触发的追加攻击使敌方目标陷入的触电状态的伤害倍率提高#，并使触电状态的持续时间增加#回合')
rename_eff(
    1005, '进入战斗后敌方每个单体目标陷入与终结技相同的触电状态',
    v6=474.27, d6=3,
    n='秘技宽恕无关慈悲：进入战斗后敌方每个单体目标陷入与终结技相同的触电状态，持续 2 回合（用了秘技再启用；6 魂起按 +156% 算，即 474.27%、持续 3 回合）',
)

log = """<li><b>2026-11-15（差异清单第 5 批）：tv 120（tools/fix120.py）</b>。两条都要动引擎：① <b>银狼 E1</b> 原文「施放终结技攻击敌方目标后，目标每有 1 个负面效果，银狼恢复 7 点能量，每次终结技最多 5 次」，页面原来固定按 3 个负面效果算 21 点、还默认关着；能量效果新增「按目标负面效果数回能」，这条改成按目标实际负面效果数 × 7（上限 5 次）并默认开启。② <b>卡芙卡 E6</b> 原文「终结技、<b>秘技</b>与天赋触发的追加攻击使触电倍率 +156%、持续 +1 回合」，页面只改了终结技和追加攻击，秘技进的触电仍是 290% / 2 回合；持续伤害新增「6 魂专用数值」，这条 6 魂时按 474.27% / 3 回合算。<b>对已有配置</b>：银狼这条只在放终结技、敌人身上有负面效果时让他多回能量（可能让开大提前）；卡芙卡那条只影响带 6 魂卡芙卡并用秘技进战的方案。其他不变。</li>"""

record = """2026-11-15（差异清单第 5 批）：tv 120（tools/fix120.py）。引擎：能量方式 neg（stCap）、持续伤害 v6 / d6 + 模板字段透传。改：银狼 E1 改 neg（7 点 / 每个负面，上限 5）默认开；卡芙卡秘技触电 6 魂 474.27% / 3 回合。
  未改 / 存疑：银狼 E4「每 1 个负面效果额外 20% 攻击力附加伤害，最多 5 次」仍在额外伤害表里按固定 5 次算（XR 表没有按状态动态取次数的机制）；银狼 E6「每 1 个负面 +20% 最多 100%」之前已按负面数做过。"""

F.finish('差异清单第 5 批（银狼 E1 负面数回能 / 卡芙卡 E6 秘技触电）', log, record)
print('done tv', TV)
