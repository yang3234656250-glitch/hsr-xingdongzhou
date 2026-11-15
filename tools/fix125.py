"""tv 125（2026-11-15）：差异清单第 10 批
瓦尔特 1004【强化版】三条原来都默认关着、但原文都是必定触发的（基础概率按命中算）：
  ① 终结技禁锢：行动延后 12%、速度 −10%（原文「100% 的基础概率」）
  ② 天赋【失重】受击行动延后 4%（原文没有概率，且「每个目标每回合最多 8 次」）
引擎：推条效果支持 turnCap（同一个目标每回合最多触发 N 次，敌方回合开始时清零）

用法：python _src/fix125.py
"""
import sys
sys.path.insert(0, '_src')
from fixlib import Fix

TV = 125
F = Fix('星铁行动轴.html', TV, '_src')

# ---------------- 引擎 ----------------
old = 'else if (eff.type === "delay") { if (v < 0) pull(tg, -v * 100); else tg.dist += v * 100;'
assert F.s.count(old) == 1
F.rep(old, 'else if (eff.type === "delay") { if (num(eff.turnCap) > 0) { tg.dlC = tg.dlC || {}; const k0 = String(eff.bk || eff.id), c0 = tg.dlC[k0] || 0; if (c0 >= num(eff.turnCap)) continue; tg.dlC[k0] = c0 + 1; }   // 每个目标每回合最多 N 次（瓦尔特【失重】受击推条 8 次）\n          if (v < 0) pull(tg, -v * 100); else tg.dist += v * 100;')

anchor = 'if (actor.wk && actor.wk.length) { for (const z of actor.wk) z.left--; actor.wk = actor.wk.filter(z => z.left > 0); }'
assert F.s.count(anchor) == 1
F.rep(anchor, 'actor.dlC = {};   // 每回合推条次数清零（瓦尔特【失重】受击推条最多 8 次）\n        ' + anchor)

F.rep('if (x.ku) e.killU = 1;',
      'if (x.ku) e.killU = 1; if (x.tc != null) e.turnCap = x.tc;   // 每个目标每回合最多触发 N 次（瓦尔特【失重】受击推条）')


# ---------------- 瓦尔特 ----------------
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


F.has('1100403', '有#的基础概率使受到攻击的敌方目标陷入禁锢状态')
F.has('1100403', '禁锢状态下，敌方目标行动延后#，速度降低#')

# ① 禁锢：行动延后 12%
rename_eff(
    1004, '【强化版】终结技：禁锢状态下行动延后',
    n='【强化版】终结技：禁锢状态下行动延后 12%（基础概率按命中算，默认开启）',
    drop_off=True, off0=True,
)
# ① 禁锢：速度 −10%
rename_eff(
    1004, '【强化版】终结技：禁锢状态下速度',
    n='【强化版】终结技：禁锢状态下速度 −10%，持续 1 回合（按敌人自己的回合；基础概率按命中算，默认开启）',
    drop_off=True, off0=True,
)
# ② 【失重】受击推条 4%，每目标每回合最多 8 次
rename_eff(
    1004, '【失重】的敌人受到攻击时行动延后 4%',
    tc=8,
    n='【强化版】终结技：【失重】的敌人受到攻击时行动延后 4%（只推被打到的敌人；每个目标每回合最多 8 次，默认开启）',
    drop_off=True, off0=True,
)

log = """<li><b>2026-11-15（差异清单第 10 批）：tv 125（tools/fix125.py）</b>。<b>瓦尔特【强化版】</b>三条原来都默认关着，但原文都没有随机成分（「100% 的基础概率」按本页的规矩 = 必定命中）：① 终结技禁锢期间「行动延后 12%、速度 −10%」；② 天赋【失重】的敌人受到攻击时「行动延后 4%」，且原文写明「每个目标每回合最多 8 次」——这条上限也做了（同一目标每回合推到第 8 次后不再推，敌方回合开始时清零）。三条都改成默认开启。<b>对已有配置</b>：带瓦尔特的方案，敌人会被推得更多（开大后禁锢的 12% + 每次攻击 4%），行动顺序会变；这也是原文的效果，之前只是关着没算。</li>"""

record = """2026-11-15（差异清单第 10 批）：tv 125（tools/fix125.py）。引擎：推条 turnCap（每目标每回合最多 N 次，敌方回合开始清零）+ 模板字段 tc。改：瓦尔特 禁锢延后 12% / 禁锢减速 10% / 失重受击推条 4%（turnCap 8）三条默认开。
  未改 / 存疑：失重受击推条的上限按「每个目标」分别计数（游戏里也是每个目标 8 次）；禁锢的推条 / 减速同样没有按「敌人身上是否还有禁锢」再判断（终结技必定挂、时长一致）。"""

F.finish('差异清单第 10 批（瓦尔特禁锢 / 失重受击推条默认开 + 每回合 8 次上限）', log, record)
print('done tv', TV)
