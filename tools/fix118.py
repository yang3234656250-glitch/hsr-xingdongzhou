"""tv 118（2026-11-15）：差异清单第 3 批（要动引擎字段）
① 银狼 1006【强化版】战技：添加的弱点对应抗性 −20% 只在「添加的弱点不是敌方原有属性」时生效
   引擎：伤害增益条件加 nwk（newWk 判断；敌人没有弱点资料时保持原来的行为）
② 姬子 1003 E4：施放战技造成弱点击破时额外 +1 充能（原来模板里没有）
   引擎：击破事件支持 brkAct（只算某种动作造成的击破）

用法：python _src/fix118.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 118
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
# ① 条件 nwk：加进“需要敌人信息”的早退判断 + 具体判断（有弱点资料才判断）
F.rep('c.est == null && c.dfr == null && c.dbf == null && c.dbn == null) return f0;',
      'c.est == null && c.dfr == null && c.dbf == null && c.dbn == null && c.nwk == null) return f0;')
F.rep('if (c.brk && !(toughMax(en) > 0 && en.broken)) return 0;',
      'if (c.nwk) { const mw = monOf(en); if (mw && mw.w && !newWk(en, byId[b.src] || u)) return 0; }   // 只算“添加了原本没有的弱点”（银狼战技抗性；敌人没有弱点资料就不判断）\n      if (c.brk && !(toughMax(en) > 0 && en.broken)) return 0;')

# ② 击破事件支持 brkAct：模板字段 → 运行时字段；触发时按当前动作过滤
F.rep('if (x.ku) e.killU = 1;',
      'if (x.ku) e.killU = 1; if (x.brkAct) e.brkAct = x.brkAct;   // 只算这种动作造成的击破（姬子 E4）')
F.rep('if (kind === "break" && e.brkSelf && brkBy != null && brkBy !== u.id) continue;',
      'if (kind === "break" && e.brkSelf && brkBy != null && brkBy !== u.id) continue;\n          if (kind === "break" && e.brkAct && !(atkCtx && e.brkAct.includes(atkCtx.k))) continue;   // 只算某种动作造成的击破')


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


# ---------------- ① 银狼 ----------------
F.has('100602', '若添加的是敌方目标原有属性的弱点，则不会触发对应属性的抗性降低效果')
rename_eff(
    1006, '添加的弱点对应属性抗性 −20%',
    ec={'nwk': 1},
    n='【强化版】战技：添加的弱点对应属性抗性 −20%，持续 3 回合（优先编队第一位角色的属性；只在添加的弱点不是敌方原有属性时才算）',
)

# ---------------- ② 姬子 E4 ----------------
F.has('r:100304', '施放战技对敌方目标造成弱点击破时，姬子额外获得#点充能')
R = F.eid(1003, 4)
R['eff'].append({
    'y': 'count', 't': 'break', 'tg': 'self', 'v': 1,
    'bby': 1, 'brkAct': ['s'],
    'n': 'E4：施放战技造成弱点击破时，额外获得 1 点充能（只算姬子自己用战技打破的）',
})

log = """<li><b>2026-11-15（差异清单第 3 批）：tv 118（tools/fix118.py）</b>。这两条要动引擎：① <b>银狼【强化版】</b>战技：原文「若添加的是敌方目标<b>原有属性</b>的弱点，则不会触发对应属性的抗性降低」，页面原来「添加的弱点对应抗性 −20%」一直生效；伤害增益的条件里新增「这次添加的是不是原本没有的弱点」，这条现在按它判断（敌人卡没有弱点资料时仍按原来一直生效，不硬扣）。② <b>姬子 E4</b>「施放战技对敌方目标造成弱点击破时，姬子额外获得 1 点充能」原来模板里没有：击破事件新增「只算某种动作造成的击破」字段，这条做成计数效果（只算姬子自己用战技打破的，普攻 / 终结技打破不算）。<b>对已有配置</b>：银狼这条只在敌人有弱点资料、且加的是原本就有的弱点时不再给 −20%（伤害略高）；姬子这条只在有韧性敌人、且她用战技打破时多 1 点充能，可能影响后续行动轴。没有韧性敌人的方案、队伍里没有银狼 / 姬子的方案完全不变。</li>"""

record = """2026-11-15（差异清单第 3 批）：tv 118（tools/fix118.py）。引擎：伤害增益条件 nwk（newWk；敌人无弱点资料不判断）、击破事件 brkAct + 模板字段透传。改：银狼战技抗性 −20% 加 ec nwk；姬子补 E4 充能（count / break / bby / brkAct s）。
  未改 / 存疑：银狼 E1「按固定 3 个负面效果 +21 能量」、E4「按固定 5 个」还没改成按实际负面数；姬子 E4 只看“动作是战技 + 是自己击破”，原文就是这两条限定。"""

F.finish('差异清单第 3 批（银狼战技抗性 / 姬子 E4 充能）', log, record)
print('done tv', TV)
