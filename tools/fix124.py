"""tv 124（2026-11-15）：差异清单第 9 批
① 黑塔 1013 E1：普攻时「指定敌方单体生命值百分比 ≤50%」才有额外 40% 攻击力附加伤害
   原来 XR 表里手动勾、勾了对所有普攻都算
② 阿兰 1008 E6：「当前生命值百分比 ≤50%」时终结技对相邻目标的倍率提高到与主目标相同
   原来同样是手动勾
引擎：模拟结果 edbAll 里带上每个敌人的当前生命值百分比（hp）和我方每个角色的生命值百分比（uh），
      XR 额外伤害行支持 hpLe（持有者生命值 ≤X%）/ eHpLe（主目标生命值 ≤X%）

用法：python _src/fix124.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 124
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
# ① edbAll 带上生命值百分比
old_ret = 'return { ord: ens.map(z => z.id), m: Object.fromEntries(ens.map(z => [z.id, dbSnap(z)])), bk: Object.fromEntries(ens.map(z => [z.id, toughMax(z) > 0 ? !!z.broken : null])), w: Object.fromEntries(ens.map(z => [z.id, wkOf(z)])) };'
assert F.s.count(old_ret) == 1
new_ret = ('return { ord: ens.map(z => z.id), m: Object.fromEntries(ens.map(z => [z.id, dbSnap(z)])), bk: Object.fromEntries(ens.map(z => [z.id, toughMax(z) > 0 ? !!z.broken : null])), w: Object.fromEntries(ens.map(z => [z.id, wkOf(z)])), '
           'hp: Object.fromEntries(ens.map(z => [z.id, z.ehx > 0 ? Math.max(0, num(z.ehc)) / z.ehx * 100 : null])), uh: Object.fromEntries(U.filter(z => z.kind === "ally" && !z.sm).map(z => [z.id, hpPct(z)])) };   // hp：敌人当前生命值 %（没模拟敌人掉血时 null）；uh：我方角色当前生命值 %')
F.rep(old_ret, new_ret)

# ② XR 行支持生命值条件
anchor = 'if (r.on && !r.on.includes(e.key)) continue;'
assert F.s.count(anchor) == 1
gates = ('\n        if (r.hpLe != null) { const A0 = rec && rec.eAll, h = A0 && A0.uh ? A0.uh[o.id] : null; if (!(h != null && h <= num(r.hpLe) + 1e-9)) continue; }   // 持有者当前生命值 ≤X%（阿兰 E6）'
         '\n        if (r.eHpLe != null) { const A0 = rec && rec.eAll, mid = A0 && A0.ord ? A0.ord[0] : null, h = A0 && A0.hp && mid != null ? A0.hp[mid] : null; if (!(h != null && h <= num(r.eHpLe) + 1e-9)) continue; }   // 主目标当前生命值 ≤X%（黑塔 E1）')
F.rep(anchor, anchor + gates)


# ---------------- XR 数据 ----------------
def edit_xr(cid, key, **chg):
    L = F.XR.get(str(cid)) or []
    row = next((x for x in L if x['k'] == key), None)
    assert row is not None, (cid, key)
    row.update(chg)
    return row


# 黑塔 E1：改成按指定目标生命值判断、默认开
edit_xr(1013, 'e1', eHpLe=50, n='E1：施放普攻时，若指定敌方单体生命值 ≤50%，额外造成 40% 攻击力的冰属性附加伤害（按目标实际生命值判断，默认开启）')
F.XR['1013'][0].pop('off', None)

# 阿兰 E6：改成按自身生命值判断、默认开
edit_xr(1008, 'e6adj', hpLe=50, n='E6：当前生命值 ≤50% 时，终结技对相邻目标的倍率提高到与主目标相同（每个相邻目标 + 主目标倍率 50%；按自身当前生命值判断，默认开启）')
F.XR['1008'][0].pop('off', None)

F.has('r:101301', '若指定敌方单体生命值百分比小于等于#，则额外造成等同于黑塔#攻击力的冰属性附加伤害')
F.has('r:100806', '当前生命值百分比小于等于#时，终结技造成的伤害提高#，且对相邻目标的伤害倍率提高到与主目标相同的伤害倍率')

log = """<li><b>2026-11-15（差异清单第 9 批）：tv 124（tools/fix124.py）</b>。这一批先把「生命值百分比」打通到伤害显示：模拟结果里现在带着每个敌人的当前生命值 % 和我方每个角色的当前生命值 %，「额外伤害」表也能按它判断。① <b>黑塔 E1</b>「施放普攻时，若指定敌方单体生命值 ≤50%，额外造成 40% 攻击力的冰属性附加伤害」原来手动勾、勾了对所有普攻都算，现在按目标实际生命值判断并默认开启。② <b>阿兰 E6</b>「当前生命值 ≤50% 时，终结技对相邻目标的倍率提高到与主目标相同」同样原来手动勾，现在按阿兰自己的当前生命值判断并默认开启。<b>对已有配置</b>：这两条只在开了「我方伤害扣敌人生命值」（敌人血量会掉）或者我方生命值真的掉到 50% 以下时才会算；没开的话黑塔那条不算（目标血量未知按满血），阿兰那条也不触发，和以前手动关着时一致。</li>"""

record = """2026-11-15（差异清单第 9 批）：tv 124（tools/fix124.py）。引擎：edbAll 带 hp（敌人当前生命值 %）/ uh（我方角色当前生命值 %）；XR 行支持 hpLe / eHpLe。改：黑塔 E1 加 eHpLe 50、默认开；阿兰 E6 加 hpLe 50、默认开。
  未改 / 存疑：黑塔那条没开「我方伤害扣敌人生命值」时敌人血量未知（按满血 → 不触发）；阿兰那条要我方生命值真的掉下来（敌人伤害 / 烧血）才会触发。"""

F.finish('差异清单第 9 批（黑塔 E1 / 阿兰 E6 按生命值判断）', log, record)
print('done tv', TV)
