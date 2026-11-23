"""tv 155（2026-11-23）：差异清单第 31 批
1. 黑天鹅【强化版】星魂按强化版（用户规则：有强化版的一律按强化版）+ 行迹脏中躁动：
   - 行迹脏中躁动（11307101）“敌方目标受到黑天鹅攻击后，有65%的基础概率陷入5层【奥迹】”：新加（atk aw self、tg ehit、5 层；基础概率按命中）。
   - E2（1130702）“敌方目标进入战斗时，有100%的基础概率陷入30层【奥迹】”：换掉原版“被消灭时相邻 6 层”（eIn + evt）。
   - E4（1130704）“【揭露】状态下，敌方目标受到的伤害额外提高20%，且每回合开始时或被消灭时使黑天鹅恢复8点能量”：
     易伤 20%（敌人进场时挂、ec.est 揭露）；回能：敌方回合开始 / 被消灭（ekill）时目标有【揭露】，去掉原版“每次【揭露】最多 1 次”。
   - E6（1130706）“【奥迹】可以叠加的层数提高30层。当敌方目标受到黑天鹅的队友的攻击时……1层【奥迹】。每当黑天鹅使敌方目标陷入1层【奥迹】时，使本次叠加层数额外提高1层”：
     所有【奥迹】效果 stE [6, 80]、saE [6, 原层数 + 1]（必定，不是原版的 50% 固定概率）；队友攻击那条目标 efirst → ehit。
2. 波提欧【优势口袋】“【绝命对峙】的目标被消灭或弱点被击破”：新条件 evSt（DB evs）= 事件对象身上有这个状态（有施放者的要是自己施放的）；
   用【嘲讽】（波提欧战技给对峙目标的）判断；消灭改用 ekill（事件对象 = 被消灭的敌人）。
3. 白露行迹岐黄精义（1211102）“为我方目标提供治疗造成过量治疗会使目标生命上限提高10%”：doHeal 记下这次治疗溢出的目标（u.ovh），
   生命上限效果的新条件 ovh = 只给同一时刻被这个施放者过量治疗的目标；两条改成默认开启。
4. 藿藿 E4（1121704）“目标的当前生命值越低治疗量越高，最多使藿藿提供的治疗量提高80%”：治疗加成新方式 lin
   = 按目标治疗前已损失生命值比例（80% × (1 − 当前生命值 / 生命上限)，线性；官方没给公式），默认开启。

用法：python3 tools/fix155.py index.html <官方 json 目录>
"""
import sys, os, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 155
F = Fix(sys.argv[1], TV, sys.argv[2])


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


def swap(cid, oldn, oldt, newn, keep=1):
    fx = fix_of(cid)
    fx['drop'].append(oldn); fx['trig'][oldn] = oldt; fx['map'][oldn] = newn; fx['add'].append(newn)
    if keep: fx['keep'] = 1


# ---------------- 1. 黑天鹅 ----------------
F.has('r:1130702', '敌方目标进入战斗时，有#的基础概率陷入#层【奥迹】')
F.has('r:1130704', '【揭露】状态下，敌方目标受到的伤害额外提高#，且每回合开始时或被消灭时使黑天鹅恢复#点能量')
F.has('r:1130706', '【奥迹】可以叠加的层数提高#层')
F.has('r:1130706', '每当黑天鹅使敌方目标陷入#层【奥迹】时，使本次叠加层数额外提高#层')
F.hast(1307, '脏中躁动', '敌方目标受到黑天鹅攻击后，有#的基础概率陷入#层【奥迹】')
bs = F.C[1307]
aj0 = [e for e in bs['eff'] if e.get('bk') == 'aj' and e['t'] == 'dotHit']; assert len(aj0) == 1
proto = {k: v for k, v in aj0[0].items() if k not in ('t', 'tg', 'n', 'off', 'sa', 'o', 'aw')}
new = copy.deepcopy(bs['eff'])
i = [k for k, e in enumerate(new) if e.get('bk') == 'aj' and e['t'] == 'dotHit'][0]
NZ = '【强化版】行迹脏中躁动：敌方目标受到黑天鹅攻击后陷入 5 层【奥迹】（基础概率按命中算）'
assert not any(e.get('n') == NZ for e in new)
new.insert(i + 1, dict(proto, t='atk', aw='self', tg='ehit', sa=5, n=NZ))
for e in new:
    if e.get('bk') == 'aj' and e['y'] == 'dot':
        e['ste'] = [6, 80]; e['sae'] = [6, int(e.get('sa', 1)) + 1]
F.rebuild(1307, new)
e2 = F.eid(1307, 2)
assert len(e2['eff']) == 1 and e2['eff'][0]['t'] == 'kill'
e2['eff'] = [dict(proto, t='eIn', tg='evt', sa=30, ste=[6, 80], sae=[6, 31], n='【强化版】E2 羔羊，请勿为我恸哭：敌方目标进入战斗时陷入 30 层【奥迹】（每个敌人进场时各一次）')]
e2['notes'] = []
e4 = F.eid(1307, 4)
assert len(e4['eff']) == 1 and e4['eff'][0].get('perUlt')
e4['eff'] = [
    {'y': 'dbuf', 't': 'eIn', 'tg': 'evt', 'm': 'vuln', 'v': 20, 'd': 0, 'bk': 'e4', 'ec': {'est': '揭露'}, 'n': '【强化版】E4 泪水，亦是礼物：【揭露】状态下的敌方目标受到的伤害额外 +20%'},
    {'y': 'energy', 't': 'eturn', 'o': 'ekill', 'tg': 'self', 'v': 8, 'm': 'er', 'ns': '揭露', 'so': 'evt', 'n': '【强化版】E4：【揭露】状态下的敌方目标每回合开始时或被消灭时黑天鹅恢复 8 点能量（每个敌人各算）'},
]
e6 = F.eid(1307, 6)
z = [x for x in e6['eff'] if x.get('bk') == 'aj']; assert len(z) == 1 and z[0]['tg'] == 'efirst'
z[0].update({'tg': 'ehit', 'ste': [6, 80], 'sae': [6, 2], 'n': '【强化版】E6 万神皆善，苦役者未知：敌方目标受到黑天鹅的队友的攻击时陷入 1 层【奥迹】（每个击中的敌人；基础概率按命中算）；6 魂起黑天鹅每次施加【奥迹】额外 +1 层、【奥迹】层数上限 +30（写在各条【奥迹】效果上）'})
e6['notes'] = [n for n in e6.get('notes', []) if '50%' not in n]
# dot 的 ste / sae 缩写引擎早已支持（tv 148）

# ---------------- 2. 波提欧 evSt ----------------
F.has('131502', '该目标被消灭或弱点被击破后，波提欧均可获得#层【优势口袋】')
n = 0
for e in F.C[1315]['eff']:
    if e.get('t') == 'break' and e.get('o') == 'kill' and e.get('ns') == '绝命对峙':
        e['o'] = 'ekill'; e['evs'] = '嘲讽'; n += 1
        e['n'] = e['n'].replace('；没判断被消灭的是不是【绝命对峙】的目标', '；按被消灭 / 被击破的敌人身上有没有波提欧给的【嘲讽】判断')
assert n == 6, n
F.rebuild(1315, F.C[1315]['eff'])
F.rep('      if (x.edk) e.eDk = x.edk;', '      if (x.evs) e.evSt = x.evs;   // 事件对象身上有这个状态（有施放者的要是自己施放的；波提欧【绝命对峙】的目标，tv 155）\n      if (x.edk) e.eDk = x.edk;')
F.rep('      if (eff.xSt && src && hasSt(src, String(eff.xSt))) return;',
      '      if (eff.evSt) { const s0 = evTarget && evTarget.st && evTarget.st[eff.evSt]; if (!s0 || (s0.by && src && s0.by !== (ownerOf(src) || src).id)) return; }   // 事件对象有这个状态（波提欧：被消灭 / 被击破的是【绝命对峙】的目标）\n'
      '      if (eff.xSt && src && hasSt(src, String(eff.xSt))) return;')

# ---------------- 3. 白露岐黄精义 ----------------
F.hast(1211, '岐黄精义', '白露对我方目标造成过量治疗时会提高目标#的生命上限')
for frag, t in [('行迹岐黄精义：战技造成过量治疗', 'skill'), ('行迹岐黄精义：终结技造成过量治疗', 'ult')]:
    e = F.eff(1211, frag); oldn = e['n']; assert e.get('off') == 1 and e['t'] == t
    del e['off']; e['ovh'] = 1
    e['n'] = f'行迹岐黄精义：{"战技" if t == "skill" else "终结技"}治疗造成过量治疗时（治疗前已经满血或治疗量超过已损失生命值），被过量治疗的目标生命上限 +10%，持续 2 回合'
    swap(1211, oldn, t, e['n'], keep=0)
    fix_of(1211).setdefault('off0', []).append(oldn)
F.rep('      if (x.edk) e.eDk = x.edk;', '      if (x.ovh) e.ovh = 1;   // 生命上限：只给同一时刻被施放者过量治疗的目标（白露岐黄精义，tv 155）\n      if (x.edk) e.eDk = x.edk;')
F.rep('      for (const [tg, a] of parts) if (a != null) { const c = hpCur(tg); if (c != null) { setHc(tg, c + a); syncMirror(tg, false); } }   // 当前生命值（不超过上限）\n',
      '      for (const [tg, a] of parts) if (a != null) { const c = hpCur(tg); if (c != null) { if (c + a > hpNow(tg) + 1e-6) tg.ovh = { at: t, by: src ? src.id : null }; setHc(tg, c + a); syncMirror(tg, false); } }   // 当前生命值（不超过上限）；溢出的记下（过量治疗）\n')
F.rep('      const tgs = resolve(eff.target, src).filter(u => u && u.kind === "ally" && !isCd(u) && !(u.sm && !u.sm.mem) && !(group && u.gone) && !(u.sm && (smDef(u) || {}).he));   // 死龙的生命上限固定\n',
      '      const tgs = resolve(eff.target, src).filter(u => u && u.kind === "ally" && !isCd(u) && !(u.sm && !u.sm.mem) && !(group && u.gone) && !(u.sm && (smDef(u) || {}).he) && !(eff.ovh && !(u.ovh && u.ovh.at === t && u.ovh.by === (src ? src.id : null))));   // 死龙的生命上限固定；ovh：只给刚被这个施放者过量治疗的\n')

# ---------------- 4. 藿藿 E4 ----------------
F.has('r:1121704', '目标的当前生命值越低治疗量越高，最多使藿藿提供的治疗量提高#')
h4 = F.eid(1217, 4)
assert len(h4['eff']) == 1 and h4['eff'][0].get('off') == 1
h4['eff'] = [{'y': 'hbup', 'm': 'lin', 't': 'start', 'tg': 'self', 'v': 80, 'd': 0, 'n': '【强化版】E4 坐卧不离，争拗难宁：施放战技或触发天赋治疗时，目标当前生命值越低治疗量越高，最多 +80%（按治疗前已损失生命值比例线性算：80% × 已损失 / 生命上限）'}]
F.rep('const c = hpCur(tg), m = hpNow(tg); if (c == null || !(m > 0)) return 0;\n      let b = 0; for (const x of H.buffs) if (x.kind === "hbl" && c <= m * num(x.thr, 50) / 100 + 1e-6) b += x.v;',
      'const c = hpCur(tg), m = hpNow(tg); if (c == null || !(m > 0)) return 0;\n      let b = 0; for (const x of H.buffs) if (x.kind === "hbl" && x.lin) b += x.v * Math.max(0, 1 - c / m); else if (x.kind === "hbl" && c <= m * num(x.thr, 50) / 100 + 1e-6) b += x.v;   // lin：按已损失生命值比例（藿藿 E4，tv 155）')
F.rep('low = eff.mode === "low", kind = low ? "hbl"', 'low = eff.mode === "low" || eff.mode === "lin", kind = low ? "hbl"')
F.rep(': low ? { thr: num(eff.ovT, 50) } : {};', ': eff.mode === "lin" ? { lin: 1 } : low ? { thr: num(eff.ovT, 50) } : {};')
F.rep('["low", "为生命值低的目标治疗时提高"]];', '["low", "为生命值低的目标治疗时提高"], ["lin", "目标生命值越低越高（按已损失比例）"]];')
F.rep('const hbSum = e => e.mode === "low" ?', 'const hbSum = e => e.mode === "lin" ? `目标当前生命值越低治疗量越高，最多 +${num(e.value)}%（按已损失生命值比例）` : e.mode === "low" ?')

log = """<li><b>2026-11-23（差异清单第 31 批）：tv 155（tools/fix155.py）</b>。依据官方原文。① <b>黑天鹅【强化版】星魂按强化版</b>：E2 改成“敌方目标进入战斗时陷入 30 层【奥迹】”（原版是被消灭时相邻 6 层）；E4 改成【揭露】状态下敌人受到的伤害额外 +20%、每回合开始时或被消灭时回 8 能量（去掉原版“每次揭露最多 1 次”）；E6 改成【奥迹】层数上限 +30、每次施加额外 +1 层（必定，不是原版的 50% 概率），队友攻击给的 1 层改成每个被击中的敌人；补上强化版行迹脏中躁动“受到黑天鹅攻击后陷入 5 层【奥迹】”。② <b>波提欧【优势口袋】</b>：只有【绝命对峙】的那个敌人被消灭 / 被击破才算（以前任何敌人都算），按敌人身上波提欧给的【嘲讽】判断。③ <b>白露岐黄精义</b>：按当前生命值判断过量治疗（治疗量超过已损失生命值），被过量治疗的目标生命上限 +10% 2 回合，默认开启（以前默认关、说明写“没有生命值”）。④ <b>藿藿 E4</b>：目标当前生命值越低治疗量越高，按已损失生命值比例线性算，最多 +80%，默认开启（以前固定 +80%、默认关）。<b>对已有配置</b>：有黑天鹅的方案【奥迹】层数、伤害和 E4 回能会变；有波提欧且对峙目标以外的敌人被消灭 / 击破时少拿【优势口袋】；白露的治疗会触发生命上限 +10%（老存档里关着的岐黄精义打开）；6 魂藿藿治疗量会变。其他方案行动顺序不变。</li>"""

record = """2026-11-23（差异清单第 31 批）：tv 155（tools/fix155.py）。改：黑天鹅强化版 E2 / E4 / E6 + 脏中躁动（dot ste / sae 缩写）；波提欧优势口袋 6 条 o ekill + evs 嘲讽（新条件 evSt）；白露岐黄精义 ovh（doHeal 记 u.ovh）默认开；藿藿 E4 hbup lin。
  没改：黑天鹅终结技【揭露】“每陷入 1 层【奥迹】50% 固定概率额外 1 层、不减半”的 50% 概率（随机）；藿藿 E4 的线性公式是推断（官方只写“越低越高，最多 80%”）。"""

F.finish('差异清单第 31 批（黑天鹅强化版星魂、波提欧优势口袋、白露岐黄精义、藿藿 E4）', log, record)
print('done tv', TV)
