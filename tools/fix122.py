"""tv 122（2026-11-15）：差异清单第 7 批
卡芙卡 1005 行迹掠夺：触电状态下的敌方目标被消灭时额外恢复 5 点能量
  原来挂在「消灭敌人」上默认关、也不判断被消灭的敌人有没有触电；现在按敌人身上有没有触电判断，默认开
  引擎：消灭事件支持 killDot（只算身上有这种持续伤害的敌人被消灭）

用法：python _src/fix122.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 122
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
anchor = 'if (kind === "kill" && e.killU && killK != null && killK !== "u") continue;'
assert F.s.count(anchor) == 1
F.rep(anchor, anchor + '\n          if (kind === "kill" && e.killDot && !(tg && (tg.dots || []).some(d => !d.gone && dkIs(d.k, e.killDot)))) continue;   // 只算身上有这种持续伤害的敌人被消灭（卡芙卡行迹掠夺）')
F.rep('if (x.ku) e.killU = 1;',
      'if (x.ku) e.killU = 1; if (x.kd) e.killDot = x.kd;   // 只算有这种持续伤害的敌人被消灭（卡芙卡行迹掠夺）')


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


# ---------------- 卡芙卡 ----------------
F.hast(1005, '掠夺', '触电状态下的敌方目标被消灭时，卡芙卡额外恢复#点能量')
rename_eff(
    1005, '行迹掠夺',
    kd='触电',
    n='行迹掠夺：触电状态下的敌方目标被消灭时，卡芙卡额外恢复 5 点能量（只算身上有触电的敌人，需要开「我方伤害扣敌人生命值」）',
    drop_off=True, off0=True,
)

log = """<li><b>2026-11-15（差异清单第 7 批）：tv 122（tools/fix122.py）</b>。<b>卡芙卡</b>行迹掠夺「触电状态下的敌方目标被消灭时，卡芙卡额外恢复 5 点能量」：原来挂在「消灭敌人」上、默认关着，也不管被消灭的敌人身上有没有触电。消灭事件新增「只算身上有这种持续伤害的敌人」，这条按触电判断并默认开启。<b>对已有配置</b>：只有开了「我方伤害扣敌人生命值」、并且敌人真的被触电状态期间消灭时才会多回能量；没开敌人掉血的方案完全不变。</li>"""

record = """2026-11-15（差异清单第 7 批）：tv 122（tools/fix122.py）。引擎：消灭事件 killDot（模板字段 kd）+ 透传。改：卡芙卡行迹掠夺加 kd 触电、默认开（off0）。
  未改 / 存疑：这只判断「被消灭时身上有触电」，不区分触电是谁挂的（原文没写只能自己挂）；消灭事件本身要开「我方伤害扣敌人生命值」才有。"""

F.finish('差异清单第 7 批（卡芙卡行迹掠夺按触电判断）', log, record)
print('done tv', TV)
