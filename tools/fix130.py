"""tv 130（2026-11-15）：修正 tv 129 + 小修一批
警告：tv 129 加的两条 E4 是重复的——虎克 E4、希露瓦 E4 模板里本来就有（希露瓦用的 m:"new" 只给没触电的）。这批：
  1. 删掉 tv 129 加的那两条重复效果；
  2. 虎克 E4 原有的那条补上「攻击灼烧目标才算」（ns 灼烧 / so enemy），持续回合按战技的 2 回合（原来写 3）；
  3. 希露瓦 E2「攻击触电目标触发天赋时 +4 能量」按主目标有触电判断（edk）、默认开；
  4. 虎克 天赋「攻击灼烧目标 +5 能量」、行迹童真「触发天赋时回复 5% 生命上限」按主目标有灼烧判断（edk）、默认开。

用法：python _src/fix130.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 130
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 1. 删掉 tv 129 的重复行 ----------------
DUP = {
    1109: 'E4：触发天赋时（攻击灼烧状态的目标后），相邻目标也陷入等同于战技的灼烧（65% 攻击力，3 魂 71.5%，持续 2 回合）',
    1103: 'E4：施放终结技时，非触电状态的敌方目标也陷入与战技相同的触电（104% 攻击力，3 魂 114.4%，持续 2 回合；已触电的算刷新）',
}
for cid, note in DUP.items():
    for x in F.C[cid]['eid']:
        n0 = len(x['eff'])
        x['eff'] = [e for e in x['eff'] if e.get('n') != note]
        if len(x['eff']) != n0:
            F.touch(cid)

# ---------------- 2. 虎克 E4 原有那条补条件 ----------------
for e in F.C[1109]['eid']:
    for z in e['eff']:
        if (z.get('n') or '').startswith('E4：触发天赋时使指定敌方目标的相邻目标也陷入等同于战技的灼烧状态'):
            z['ns'] = '灼烧'
            z['so'] = 'enemy'
            z['d'] = 2
            z['n'] = 'E4：触发天赋时（攻击灼烧状态的目标后），指定敌方目标的相邻目标也陷入等同于战技的灼烧状态（持续 2 回合）'
            F.touch(1109)

# ---------------- 3. 希露瓦 E2 ----------------
for e in F.C[1103]['eid']:
    for z in e['eff']:
        if (z.get('n') or '').startswith('E2 安可！'):
            z['edk'] = '触电'
            z.pop('off', None)
            z['n'] = 'E2 安可！：攻击触电状态的目标（触发天赋附加伤害）时，希露瓦恢复 4 点能量（按主目标是否有触电判断，默认开启）'
            F.touch(1103)


# ---------------- 4. 虎克 天赋 / 童真 ----------------
def rename_eff(cid, frag, r=None, off0=None, drop_off=False, **chg):
    e = F.eff(cid, frag, r=r)
    oldn = e['n']
    trig = e.get('t')
    e.update(chg)
    if drop_off:
        e.pop('off', None)
    new = e['n']
    fx = F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
    fx['drop'].append(oldn)
    fx['add'].append(new)
    fx['trig'][oldn] = trig
    if new != oldn:
        fx['map'][oldn] = new
    if off0:
        fx.setdefault('off0', []).append(new)
    return oldn, new


def rename_exact(cid, note, off0=None, drop_off=False, **chg):
    """按完整说明精确匹配（避免片段命中多条）"""
    L = [x for x in F.C[cid]['eff'] if x.get('n') == note]
    assert len(L) == 1, (cid, note, len(L))
    e = L[0]
    oldn = e['n']
    trig = e.get('t')
    e.update(chg)
    if drop_off:
        e.pop('off', None)
    new = e['n']
    fx = F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
    fx['drop'].append(oldn)
    fx['add'].append(new)
    fx['trig'][oldn] = trig
    if new != oldn:
        fx['map'][oldn] = new
    if off0:
        fx.setdefault('off0', []).append(new)
    return oldn, new


F.has('r:110904', '触发天赋时，有#基础概率使指定敌方目标的相邻目标也陷入等同于战技的灼烧状态')
rename_exact(
    1109, '天赋（攻击灼烧目标）',
    edk='灼烧',
    n='天赋：攻击处于灼烧状态的敌方目标时（触发天赋），恢复 5 点能量（按主目标有没有灼烧判断，默认开启）',
    drop_off=True, off0=1,
)
rename_exact(
    1109, '行迹童真：触发天赋（攻击灼烧目标）时回复自身 5% 生命上限',
    edk='灼烧',
    n='行迹童真：触发天赋（攻击灼烧状态的敌方目标）时，回复自身 5% 生命上限（按主目标有没有灼烧判断，默认开启）',
    drop_off=True, off0=1,
)

log = """<li><b>2026-11-15（修正 tv 129 + 第 15 批）：tv 130（tools/fix130.py）</b>。先纠正上一批的错误：<b>虎克 E4 和希露瓦 E4 模板里本来就有</b>，tv 129 又各加了一条一模一样的，会重复计算——这批把重复的两条删掉了（希露瓦原来那条用的是「只给没触电的」，才是对的）。顺手把这几条和原文对齐：① <b>虎克 E4</b> 补上「要攻击灼烧状态的敌人（触发天赋）才生效」，持续回合按战技的 2 回合（原来写 3）；② <b>希露瓦 E2</b>「攻击触电目标触发天赋时 +4 能量」按主目标有没有触电判断、默认开启；③ <b>虎克</b>天赋「攻击灼烧目标 +5 能量」和行迹童真「回复 5% 生命上限」也按主目标有没有灼烧判断、默认开启。<b>对已有配置</b>：带虎克 / 希露瓦的方案，这几条从「默认关」变成按实际状态自动生效（目标带电 / 灼烧时才回能、才治疗），行动轴可能变。</li>"""

record = """2026-11-15（修正 tv 129 + 第 15 批）：tv 130（tools/fix130.py）。删：tv 129 重复加的虎克 E4 / 希露瓦 E4 两条。改：虎克 E4 加 ns 灼烧 / so enemy、d 改 2；希露瓦 E2 加 edk 触电、默认开；虎克天赋 +5 能量 / 行迹童真加 edk 灼烧、默认开。
  教训：加星魂效果前先 dump 一遍 eid（tv 129 就是没看 eid r4，重复加了两条）；F.eid() 会把整组效果按模板重建。"""

F.finish('修正 tv 129 重复的 E4 + 虎克/希露瓦按持续伤害状态判断', log, record)
print('done tv', TV)
