"""tv 160（2026-11-23）：差异清单第 36 批
1. 万敌 1404【血仇】额外回合的【弑神登神】（140411）：以前按【弑王成王】算（110% / 相邻 66%、回能 30、削韧 [60, 0, 30]），
   改成弑神登神 280% / 相邻 168%（DMG 1404 新键 s4，按技能等级）、回能 10（官方 AvatarSkillConfig 140411 SPBase 10）、削韧 [90, 0, 60]（ShowStanceList）。
   引擎：额外回合效果新字段 xk（这个额外回合用哪个伤害表键）、xke（这个额外回合回多少能量，代替按动作回能）；
   行动记录 rec.xk，dmgKey / toughHit / hitEns 优先用它；SCK / LVK 认 s4（算战技）。
   没做：“此技能期间无法积攒充能”、E1“主目标 +30% 且对敌方全体造成主目标倍率”。
2. 三月七（巡猎）1224 行迹斡波（1224103）“施放强化普攻后，使【师父】的暴击伤害提高60%，击破特攻提高36%，持续2回合”：补击破特攻 +36%。
3. 灵砂 1222 E6（122206）“【浮元】攻击时额外造成4次伤害……和5点削韧值”：补削韧（4 × 5 = 20 点，按主目标；原文随机、优先有火弱点且韧性 >0 的目标）。

用法：python3 tools/fix160.py index.html <官方 json 目录>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 160
F = Fix(sys.argv[1], TV, sys.argv[2])


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


# 1. 万敌
F.has('140411', '消耗#点充能，对敌方单体造成等同于万敌#生命上限的虚数属性伤害，同时对其相邻目标造成等同于万敌#生命上限的虚数属性伤害')
P = F.prm('140411'); assert len(P) == 15 and P[9][:2] == [2.8, 1.68]
D = F.DMG['1404']; assert 's4' not in D
D['s4'] = {'v': [round(p[0], 4) for p in P], 'adj': [round(p[1], 4) for p in P], 'rnd': [], 'tg': 2, 'el': 0, 'stat': 'hp', 'n': '弑神登神', 'max': 15}
m = re.search(r'const TGH = (\{.*?\});', F.s); T = json.loads(m.group(1))
assert 's4' not in T['1404']; T['1404']['s4'] = [90, 0, 60]
F.s = F.s[:m.start(1)] + json.dumps(T, ensure_ascii=False, separators=(',', ':')) + F.s[m.end(1):]
e = F.eff(1404, '天赋：【血仇】期间充能达到 150 时消耗 150 点，立即获得 1 个额外回合'); oldn = e['n']
e['xk'] = 's4'; e['xke'] = 10
e['n'] = '天赋：【血仇】期间充能达到 150 时消耗 150 点，立即获得 1 个额外回合并自动施放【弑神登神】（280% / 相邻 168% 生命上限，回能 10；6 魂 100 点）'
fx = fix_of(1404); fx['drop'].append(oldn); fx['trig'][oldn] = 'cntUp'; fx['map'][oldn] = e['n']; fx['add'].append(e['n']); fx['keep'] = 1
F.rep('      if (x.evs) e.evSt = x.evs;', '      if (x.evs) e.evSt = x.evs; if (x.xk) e.xKey = x.xk; if (x.xke != null) e.xkE = x.xke;')
F.rep('keep: 0, jh: 0, why: eff.trigger }); marks.push({ t, uid: tg.id, label: "额外回合"',
      'keep: 0, jh: 0, why: eff.trigger, xk: eff.xKey, xkE: eff.xkE }); marks.push({ t, uid: tg.id, label: "额外回合"')
F.rep('extra: true, ult: u === swU && sw.inUlt, seq: seq++, why: q.why };',
      'extra: true, ult: u === swU && sw.inUlt, seq: seq++, why: q.why }; if (q.xk) rec.xk = q.xk;   // 额外回合指定的技能（万敌【弑神登神】）')
F.rep('        if (hasEnergy(u)) { curWhy = `额外回合${actName[rec.act] || ""}回能`; addEnergy(u, actE(u, rec.act), true); }',
      '        if (hasEnergy(u)) { curWhy = `额外回合${actName[rec.act] || ""}回能`; addEnergy(u, q.xkE != null ? num(q.xkE) : actE(u, rec.act), true); }')
F.rep('    if (a.act === "basic") return "b";\n    if (a.act === "ebasic") return "b2";\n    const T = u && tplOf(u), f = T && S2ST[String(T.id)], D = dmgTpl(u);',
      '    if (a.act === "basic") return "b";\n    if (a.act === "ebasic") return "b2";\n    const T = u && tplOf(u), f = T && S2ST[String(T.id)], D = dmgTpl(u);\n    if (a.xk && D && D[a.xk]) return a.xk;   // 额外回合指定的技能（tv 160）')
F.rep('      const tb = T0 && key ? (TGH[T0.id] || {})[key] : null; if (!tb) return ens;',
      '      if (curRec && curRec.xk && curRec.uid === o.id && !who.sm && (TGH[T0.id] || {})[curRec.xk]) key = curRec.xk;\n      const tb = T0 && key ? (TGH[T0.id] || {})[key] : null; if (!tb) return ens;')
F.rep('      const v = tb[key]; if (!v) return;\n',
      '      if (curRec && curRec.xk && curRec.uid === o.id && !who.sm && tb[curRec.xk]) key = curRec.xk;   // 额外回合指定的技能（万敌【弑神登神】）\n      const v = tb[key]; if (!v) return;\n')
F.rep('const SCK = { b: "b", b2: "b", s: "s", s2: "s", s3: "s",', 'const SCK = { b: "b", b2: "b", s: "s", s2: "s", s3: "s", s4: "s",')
F.rep('const LVK = { b: "b", b2: "b", s: "s", s2: "s", s3: "s",', 'const LVK = { b: "b", b2: "b", s: "s", s2: "s", s3: "s", s4: "s",')

# 2. 三月七（巡猎）斡波
F.hast(1224, '斡波', '施放强化普攻后，使【师父】的暴击伤害提高#，击破特攻提高#，持续#回合')
e = F.eff(1224, '行迹斡波：施放强化普攻后【师父】暴击伤害 +60%'); oldn = e['n']
e['n'] = '行迹斡波：施放强化普攻后【师父】暴击伤害 +60%，持续 2 回合（师父 = 战技最新的目标）'
c = F.C[1224]; i = c['eff'].index(e)
NB = '行迹斡波：施放强化普攻后【师父】击破特攻 +36%，持续 2 回合'
c['eff'].insert(i + 1, {'y': 'dbuf', 't': 'ebasic', 'tg': 'skpick', 'm': 'be', 'v': 36, 'd': 2, 'bk': 'wbb', 'n': NB})
fx = fix_of(1224); fx['drop'].append(oldn); fx['trig'][oldn] = 'ebasic'; fx['map'][oldn] = e['n']; fx['add'] += [e['n'], NB]; fx['keep'] = 1

# 3. 灵砂 E6 削韧
F.has('r:122206', '额外造成#次伤害，每次伤害对随机敌方单体造成等同于灵砂#攻击力的火属性伤害和#点削韧值')
e6 = F.eid(1222, 6)
e6['eff'].append({'y': 'tfix', 't': 'fua', 'tg': 'efirst', 'v': 20, 'n': 'E6：【浮元】攻击时额外 4 次伤害各 5 点削韧（共 20 点，按主目标；原文随机、优先有火弱点且韧性 >0 的目标）'})

log = """<li><b>2026-11-23（差异清单第 36 批）：tv 160（tools/fix160.py）</b>。① <b>万敌【弑神登神】</b>：【血仇】期间充能满 150 给的额外回合以前按【弑王成王】算（110%、回能 30），改成官方弑神登神 280% / 相邻 168% 生命上限、回能 10、削韧 30 / 相邻 20（新字段：额外回合指定技能 / 回能）。② 三月七（巡猎）行迹斡波补【师父】击破特攻 +36%。③ 灵砂 E6【浮元】额外 4 次伤害的削韧（共 20 点，按主目标）。<b>对已有配置</b>：万敌血仇额外回合少回 20 能量（开大可能晚一点），伤害变高；其余只影响击破 / 伤害。</li>"""
record = """2026-11-23（差异清单第 36 批）：tv 160（tools/fix160.py）。万敌弑神登神 DMG s4 / TGH s4 / 额外回合 xk + xke；三月七（巡猎）斡波 be 36；灵砂 E6 tfix 20。"""
F.finish('差异清单第 36 批（万敌弑神登神、三月七巡猎斡波、灵砂 E6 削韧）', log, record)
print('done tv', TV)
