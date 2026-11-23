"""tv 157（2026-11-23）：差异清单第 33 批：几条“默认关、要手动开”的改成按实际情况自动判断
1. 丹恒 1002 终结技（100203）“若敌方目标处于减速状态，则终结技造成的伤害倍率提高”：XR slow 加 slowAny（主目标减速才算），默认开。
2. 彦卿 1209 行迹颁冰（1209102）“对携带冰属性弱点的敌方目标造成 30% 攻击力的冰属性附加伤害”：新 XR 条件 ewk（主目标有这个属性弱点，eAll.w），默认开。
3. 真理医生 1305 天赋（130504）“目标每有 1 个负面效果概率提高 20%”，负面效果 ≥3 时 40% + 60% = 100% 必定发动：
   新加一条 negMin 3 的追加攻击（默认开；概率那条照旧默认关）。
4. 艾丝妲 1009 行迹点燃（1009101）“我方全体火属性伤害提高 18%”：加 tel 火，默认开（以前对所有属性、默认关）。
5. 素裳 1206 行迹破敌（1206102）“施放普攻或战技后，若场上有处于弱点击破状态的敌方目标，则行动提前 15%”：
   改成普攻 / 战技行动后（ally aw self aa）+ 新条件 ebra（场上任意敌人破韧），默认开；
   E1（120601）“对处于弱点击破状态的敌方目标施放战技后恢复 1 个战技点”：战技行动后 + ebr（主目标破韧），默认开。

用法：python3 tools/fix157.py index.html <官方 json 目录>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 157
F = Fix(sys.argv[1], TV, sys.argv[2])


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


def swap(cid, oldn, oldt, newn, was_off=False):
    fx = fix_of(cid)
    fx['drop'].append(oldn); fx['trig'][oldn] = oldt; fx['map'][oldn] = newn; fx['add'].append(newn); fx['keep'] = 1
    if was_off: fx.setdefault('off0', []).append(oldn)


def xrow(cid, k):
    R = [r for r in F.XR[str(cid)] if r['k'] == k]; assert len(R) == 1; return R[0]


# 1. 丹恒
F.has('100203', '当受到攻击的敌方目标处于减速状态时，终结技造成的伤害倍率提高')
r = xrow(1002, 'slow'); assert r.get('off') == 1
del r['off']; r['slowAny'] = True; r['n'] = '终结技：目标处于减速状态时伤害倍率 +120%（12 级 129.6%；按主目标是否减速自动判断）'
# 2. 彦卿
F.hast(1209, '颁冰', '对携带冰属性弱点的敌方目标造成')
r = xrow(1209, 'bb'); assert r.get('off') == 1
del r['off']; r['ewk'] = '冰'; r['n'] = '行迹颁冰：攻击后对有冰属性弱点的敌人 30% 攻击力附加伤害（按主目标有没有冰弱点自动判断；没放敌人卡不算）'
F.rep('        if (r.slowAny) {',
      '        if (r.ewk) { const A5 = rec && rec.eAll, mid5 = A5 && A5.ord ? A5.ord[0] : null, w5 = A5 && A5.w && mid5 != null ? A5.w[mid5] : null; if (!(w5 && String(w5).includes(r.ewk))) continue; }   // 主目标有这个属性弱点（彦卿颁冰，tv 157）\n'
      '        if (r.slowAny) {')
# 3. 真理医生
F.has('130504', '目标每有#个负面效果')
c = F.C[1305]
i = [k for k, e in enumerate(c['eff']) if e['n'].startswith('天赋：施放战技时有 40% 的固定概率')][0]
NN = '天赋：施放战技时目标有 3 个及以上负面效果时必定对该目标发动追加攻击（40% + 3 × 20% = 100%；按主目标的实际负面效果数）'
c['eff'].insert(i + 1, {'y': 'fua', 't': 'skill', 'tg': 'self', 'v': 0, 'nmin': 3, 'n': NN})
c['eff'][i]['n'] = '天赋：施放战技时有 40% 的固定概率对该目标发动追加攻击，目标每有 1 个负面效果概率 +20%（概率触发，默认不算；负面效果 ≥3 个必定触发的情况由下一条自动算）'
swap(1305, '天赋：施放战技时有 40% 的固定概率对该目标发动追加攻击，目标每有 1 个负面效果概率 +20%（概率触发，默认不算；目标有 3 个负面效果时必定触发，届时启用）', 'skill', c['eff'][i]['n'])
fix_of(1305)['add'].append(NN)
# 4. 艾丝妲
F.hast(1009, '点燃', '我方全体的火属性伤害提高')
e = F.eff(1009, '行迹点燃：我方全体火属性伤害 +18%'); oldn = e['n']
del e['off']; e['tel'] = '火'; e['n'] = '行迹点燃：我方全体火属性伤害 +18%（只对火属性的攻击）'
swap(1009, oldn, 'start', e['n'], True)
# 5. 素裳
F.hast(1206, '破敌', '若场上有敌方目标处于弱点击破状态，则素裳的行动提前')
F.has('r:120601', '对陷入弱点击破状态的敌方目标施放战技后')
c = F.C[1206]
L = [e for e in c['eff'] if e['n'] == '行迹破敌（场上有击破状态的敌人）']; assert len(L) == 2
for e in L: c['eff'].remove(e)
new = {'y': 'advance', 't': 'ally', 'aw': 'self', 'aa': ['basic', 'skill'], 'ebra': 1, 'tg': 'self', 'v': 15, 'n': '行迹破敌：施放普攻或战技后，场上有处于弱点击破状态的敌人时行动提前 15%'}
c['eff'].append(new)
fx = fix_of(1206); fx['drop'].append('行迹破敌（场上有击破状态的敌人）'); fx['trig']['行迹破敌（场上有击破状态的敌人）'] = 'skill'; fx['add'].append(new['n'])
e1 = F.eid(1206, 1)['eff']; assert len(e1) == 1 and e1[0].get('off') == 1
e1[0] = {'y': 'sp', 't': 'ally', 'aw': 'self', 'aa': 'skill', 'ebr': 1, 'tg': 'self', 'v': 1, 'n': 'E1：对处于弱点击破状态的敌方目标施放战技后恢复 1 个战技点（按主目标）'}
F.rep('      if (x.edk) e.eDk = x.edk; if (x.ebr) e.eBr = 1;', '      if (x.edk) e.eDk = x.edk; if (x.ebr) e.eBr = 1; if (x.ebra) e.eBrA = 1;')
F.rep('      if (!eff.eWl && !eff.eDk && !eff.eBr && !eff.negMin && !eff.slowMin) return true;',
      '      if (eff.eBrA && !U.some(x => x.kind === "enemy" && !x.gone && toughMax(x) > 0 && x.broken)) return false;   // 场上有处于弱点击破状态的敌人（素裳破敌，tv 157）\n'
      '      if (!eff.eWl && !eff.eDk && !eff.eBr && !eff.negMin && !eff.slowMin) return true;')
F.rep('eff.eWl || eff.eDk || eff.eBr || eff.uPk || eff.negMin || eff.slowMin) {', 'eff.eWl || eff.eDk || eff.eBr || eff.eBrA || eff.uPk || eff.negMin || eff.slowMin) {')

log = """<li><b>2026-11-23（差异清单第 33 批）：tv 157（tools/fix157.py）</b>。几条以前默认关、要手动勾的改成按实际情况自动判断：① 丹恒终结技“目标减速时倍率 +120%”按主目标是否减速；② 彦卿行迹颁冰按主目标有没有冰弱点；③ 真理医生天赋：目标负面效果 ≥3 个时追加攻击必定发动（新加一条，按主目标实际负面效果数；概率那条仍默认关）；④ 艾丝妲行迹点燃只给火属性攻击 +18%、默认开；⑤ 素裳行迹破敌（普攻 / 战技后场上有破韧敌人 → 行动提前 15%）和 E1（对破韧目标施放战技后 +1 战技点）默认开、按实际击破判断。<b>对已有配置</b>：只有放了敌人卡且有击破 / 减速 / 负面效果时才会变；素裳、真理医生在这种方案里行动顺序可能变，其余只影响伤害。</li>"""
record = """2026-11-23（差异清单第 33 批）：tv 157（tools/fix157.py）。丹恒 XR slow + slowAny；彦卿 XR bb + 新 XR 条件 ewk；真理医生 nmin 3 必定追击；艾丝妲点燃 tel 火；素裳破敌 ally aa + 新条件 ebra、E1 ebr。"""
F.finish('差异清单第 33 批（丹恒、彦卿、真理医生、艾丝妲、素裳：默认关改成按实际判断）', log, record)
print('done tv', TV)
