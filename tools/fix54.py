"""tv 54：每日校对 2026-11-08（彦卿 1209、桂乃芬 1210、白露 1211），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix54.py index.html（需要 /tmp/sr/character_skills.json、character_ranks.json）
- 彦卿：【智剑连心】按原文做成状态（战技获得，持续 1 回合；施放战技的这个回合结束不算，所以写 d 2、回合结束时 −1）：
  天赋暴击率 / 暴击伤害跟着状态（原来按开局一直有）；终结技“若处于【智剑连心】暴击伤害额外 +50%”加状态条件；
  E2“处于【智剑连心】效果时充能效率 +10%”原来是默认关闭的“开大后 1 回合”近似，改成跟着状态、默认开启
  （充能效率增益支持 bk "st:状态名"，状态结束时一起移除）；天赋追击概率说明 65% → 60%（5 魂 62%；65% 是冻结概率）。
- 桂乃芬：战技使目标与相邻目标陷入【灼烧】（敌人身上的状态，2 回合，按敌方全体）；行迹缘竿（普攻 80% 概率灼烧，默认关）；
  E4“灼烧每触发一次伤害 +2 能量”改成敌人回合开始时该敌人有【灼烧】才回（仍默认关，基础概率），补终结技引爆那一下（默认关）；
  E6“【吞火】可叠加层数 +1”补进伤害增益。
- 白露：终结技“已拥有【生息】的延长 1 回合”（新字段 stExt / DB sx）；秘技进战全体【生息】2 回合（默认关）；
  E1“【生息】结束时若目标当前生命值等于生命上限额外恢复 8 点能量”原来只在 notes，用新触发 stEnd（我方目标的状态结束时，
  事件对象 = 失去状态的目标，DB se = 只算哪个状态）+ 新条件 hpFEv（DB hfe，事件对象当前生命值 ≥ X%）做出来，默认开启。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 54
assert f'if (s.tv >= {TV - 1}) return;' in s
SK = json.load(open('/tmp/sr/character_skills.json'))
RK = json.load(open('/tmp/sr/character_ranks.json'))
prm = lambda sid: SK[sid]['params']
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:90], s.count(x)); s = s.replace(x, y)
def find(L, pred):
    R = [x for x in L if pred(x)]; assert len(R) == 1, R; return R[0]

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}

# ---------- 彦卿 1209 ----------
c = C[1209]; ST = '智剑连心'; BK = 'st:' + ST
p2 = prm('120902'); assert p2[9] == [2.2] and abs(p2[11][0] - 2.42) < 1e-9
pu = prm('120903'); assert pu[9] == [0.6, 0.5, 3.5] and pu[11][1] == 0.54
pt = prm('120904'); assert pt[9][:3] == [0.2, 0.3, 0.6] and pt[11][:3] == [0.21, 0.33, 0.62], pt[9]
assert '能量恢复效率' in RK['120902']['desc']
fua = find(c['eff'], lambda x: x['y'] == 'fua'); o_fua = fua['n']; assert '65%' in o_fua
fua['n'] = '天赋：对敌方目标施放攻击后 60% 固定概率追加攻击（5 魂 62%；概率触发，需要时启用）'
cr = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'cr' and x['t'] == 'start'); o_cr = cr['n']
cd = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'cd' and x['t'] == 'start'); o_cd = cd['n']
assert cr['lv'] == [5, 21] and cd['lv'] == [5, 33]
cr.update(t='skill', bk=BK, d=0, n='天赋：处于【智剑连心】时暴击率 +20%（跟着【智剑连心】）')
cd.update(t='skill', bk=BK, d=0, n='天赋：处于【智剑连心】时暴击伤害 +30%（跟着【智剑连心】）')
uc = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'cd' and x['t'] == 'ult'); o_uc = uc['n']
assert uc['v'] == 50 and uc['lv'] == [5, 54]
uc.update(ns=ST, n='终结技：若处于【智剑连心】，暴击伤害额外 +50%，持续 1 回合')
Z = dict(y='state', t='skill', tg='self', sn=ST, v=1, d=2,
         n='战技：为彦卿附加【智剑连心】，持续 1 回合（施放战技的这个回合结束时不算，所以这里写 2；受到伤害后消失没做）')
k = c['eff'].index(cr); c['eff'].insert(k, Z)
e2 = next(e for e in c['eid'] if e['r'] == 2)['eff'][0]
assert e2['y'] == 'erbuff' and e2['v'] == 10 and e2['t'] == 'ult'
for f in ('off',): e2.pop(f, None)
e2.update(t='skill', bk=BK, d=0, n='E2 空明：处于【智剑连心】效果时充能效率额外 +10%（跟着【智剑连心】）')
c['notes'] = (c.get('notes') or []) + ['【智剑连心】“受到伤害后消失”没做（敌人伤害不做）；E6 消灭敌人时延长增益没做（击杀不自动判断）']
FIX['1209'] = {'drop': [o_fua, o_cr, o_cd, o_uc], 'trig': {o_fua: 'atk', o_cr: 'start', o_cd: 'start', o_uc: 'ult'},
               'map': {o_fua: fua['n'], o_cr: cr['n'], o_cd: cd['n'], o_uc: uc['n']},
               'add': [Z['n'], cr['n'], cd['n'], uc['n'], fua['n']], 'sm': {}}

# ---------- 桂乃芬 1210 ----------
c = C[1210]; BU = '灼烧'
p2 = prm('121002'); assert p2[9][2:] == [1, 2.1821, 2] or (p2[9][2] == 1 and p2[9][4] == 2), p2[9]
pt = prm('121004'); assert pt[9][3:] == [0.07, 3, 3] and abs(pt[11][3] - 0.076) < 1e-9, pt[9]
assert all(x.get('y') != 'state' for x in c['eff'])
B1 = dict(y='state', t='skill', tg='enemies', sn=BU, v=1, d=2,
          n='战技：100% 基础概率使目标与相邻目标陷入【灼烧】，持续 2 回合（这里按敌方全体，每个敌人自己的回合结束 −1）')
B2 = dict(y='state', t='basic', tg='efirst', sn=BU, v=1, d=2, off=1,
          n='行迹缘竿：普攻 80% 基础概率使目标陷入与战技相同的【灼烧】（概率触发，需要时启用）')
c['eff'] = c['eff'][:1] + [B1, B2] + c['eff'][1:]
e4 = next(e for e in c['eid'] if e['r'] == 4); o_e4 = e4['eff'][0]['n']
assert e4['eff'][0]['t'] == 'eturn' and e4['eff'][0]['v'] == 2
e4['eff'][0].update(ns=BU, so='evt', n='E4 金枪锁咽喉：灼烧每触发一次伤害桂乃芬恢复 2 点能量（敌人回合开始时它有【灼烧】就 +2；灼烧要命中，需要时启用）')
e4['eff'].append(dict(y='energy', t='ult', tg='self', v=2, m='er', ns=BU, so='enemy', off=1,
                      n='E4：终结技使【灼烧】立即产生伤害时也 +2（按 1 个灼烧的敌人；几个敌人灼烧就把数值改成 2 × 个数）'))
assert not any(e['r'] == 6 for e in c['eid'])
th = find(c['eff'], lambda x: x['y'] == 'dbuf' and x['m'] == 'vuln'); assert th['v'] == 21 and th['lv'] == [5, 22.8]
c['eid'].append({'r': 6, 'eff': [dict(y='dbuf', t='skill', tg='enemies', m='vuln', v=7.6, d=3, bk='th6',
                                       n='E6 徒手接子弹：【吞火】可叠加层数 +1（按叠满 4 层，再 +7.6%）')], 'notes': []})
c['eid'].sort(key=lambda e: e['r'])
FIX['1210'] = {'drop': [], 'trig': {}, 'map': {}, 'add': [B1['n'], B2['n']], 'sm': {}}

# ---------- 白露 1211 ----------
c = C[1211]; SX = '生息'
pu = prm('121103'); assert pu[9] == [0.135, 360, 2] and pu[11][:2] == [0.144, 400.5], pu[9]
assert prm('121107')[0] == [2]
us = find(c['eff'], lambda x: x['y'] == 'state' and x['t'] == 'ult'); o_us = us['n']
us.update(sx=1, n='终结技：没有【生息】的我方目标获得【生息】，持续 2 回合；已有的延长 1 回合')
T = dict(y='state', t='start', tg='allies', sn=SX, v=1, d=2, off=1,
         n='秘技徜徉灵泽病恙短：进入战斗时为我方全体附上【生息】，持续 2 回合（用了秘技再启用）')
c['eff'].append(T)
e1 = next(e for e in c['eid'] if e['r'] == 1); assert not e1['eff'] and e1['notes']
e1['eff'] = [dict(y='energy', t='stEnd', se=SX, aw='all', hfe=100, tg='evt', v=8, m='er',
                  n='E1 百脉甘津宁神久：【生息】结束时若我方目标当前生命值等于其生命上限，额外恢复目标 8 点能量')]
e1['notes'] = []
c['notes'] = (c.get('notes') or []) + ['天赋【生息】受击回复“可以触发 2 次（行迹 +1）”的次数限制没做（现在每次受击都回复）']
FIX['1211'] = {'drop': [o_us], 'trig': {o_us: 'ult'}, 'map': {o_us: us['n']}, 'add': [us['n'], T['n']], 'sm': {}}
put(m, DB)

# ---------- 新字段 / 新触发 ----------
rep("      if (x.hlv) e.hpLEv = x.hlv;",
    "      if (x.hlv) e.hpLEv = x.hlv;\n"
    "      if (x.hfe) e.hpFEv = x.hfe;                 // 事件对象当前生命值 ≥ X% 才生效（白露 E1：等于生命上限写 100）\n"
    "      if (x.se) e.seKey = x.se;                   // 触发“我方目标的状态结束时”只算这个状态（白露【生息】）\n"
    "      if (x.sx) e.stExt = x.sx;                   // 状态：目标已经有这个状态时持续回合 +N（白露终结技：已有【生息】的延长 1 回合）")
rep("      if (num(eff.anyLE) > 0 && !U.some(",
    "      if (num(eff.hpFEv) > 0) { const T = evTarget, c = T ? hpCur(T) : null, mx = T ? hpNow(T) : null; if (c == null || !(mx > 0) || c < mx * num(eff.hpFEv) / 100 - 1e-6 * Math.max(1, mx)) return; }   // 事件对象当前生命值 ≥ X%（白露 E1）\n"
    "      if (num(eff.anyLE) > 0 && !U.some(")
rep("      const d = Math.max(0, Math.round(num(eff.duration)));\n      tg.st[k] = { left: d > 0 ? d : Infinity,",
    "      const d = Math.max(0, Math.round(num(eff.duration)));\n"
    "      if (num(eff.stExt) > 0 && tg.st[k] && tg.st[k].tick !== \"chg\") { tg.st[k].left += Math.round(num(eff.stExt)); return; }   // 已有这个状态：持续回合 +N（白露终结技延长【生息】）\n"
    "      tg.st[k] = { left: d > 0 ? d : Infinity,")
rep("      marks.push({ t, uid: u.id, label: k + \"结束\", color: u.color, from: u.name });\n    };",
    "      marks.push({ t, uid: u.id, label: k + \"结束\", color: u.color, from: u.name });\n"
    "      if (u.kind === \"ally\" && stEndDepth < 3) { stEndDepth++; try { teamFire(\"stEnd\", u, e => !e.seKey || String(e.seKey).trim() === k); } finally { stEndDepth--; } }   // 我方目标的状态结束时（白露 E1：【生息】结束）\n"
    "    };")
rep("    const endSt = (u, k) => {", "    let stEndDepth = 0;\n    const endSt = (u, k) => {")
rep('const key = (src ? src.id : "ev") + ":er:" + (eff.bk || (num(eff.stack) > 0 ? eff.id : v)),',
    'const key = (src ? src.id : "ev") + (eff.bk && String(eff.bk).startsWith("st:") ? ":" + eff.bk + "#er" : ":er:" + (eff.bk || (num(eff.stack) > 0 ? eff.id : v))),')
rep('const TEAMT = ["ally", "atk", "aSk", "aUlt", "aFua", "aTurn", "hgive", "aHeal", "aGive", "eMax"];',
    'const TEAMT = ["ally", "atk", "aSk", "aUlt", "aFua", "aTurn", "hgive", "aHeal", "aGive", "eMax", "stEnd"];')
rep('"hpLoss", "aHeal", "aGive", "eMax"];', '"hpLoss", "aHeal", "aGive", "eMax", "stEnd"];')
rep('["eMax", "我方角色能量达到上限时"]', '["eMax", "我方角色能量达到上限时"], ["stEnd", "我方目标的状态结束时"]', 2)
rep('cntUp: "计数增加后", eMax: "我方角色能量达到上限时"', 'cntUp: "计数增加后", eMax: "我方角色能量达到上限时", stEnd: "我方目标的状态结束时"')
rep("+ (num(e.hpLEv) > 0 ? `（事件对象生命 ≤${num(e.hpLEv)}%）` : \"\")",
    "+ (num(e.hpLEv) > 0 ? `（事件对象生命 ≤${num(e.hpLEv)}%）` : \"\") + (num(e.hpFEv) > 0 ? `（事件对象生命 ≥${num(e.hpFEv)}%）` : \"\") + (e.seKey ? `（【${e.seKey}】结束时）` : \"\") + (num(e.stExt) > 0 ? `（已有的 +${num(e.stExt)} 回合）` : \"\")")

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-08（彦卿、桂乃芬、白露，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
