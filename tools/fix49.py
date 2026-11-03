"""tv 49：每日校对 2026-11-03（黑塔 1013、Saber 1014、Archer 1015、希儿【强化版】1102），对照 StarRailRes 原文与 AvatarSkillConfig。
用法：python3 tools/fix49.py index.html
- 黑塔：全部核对无误，不改。
- Saber：
  · 战技风王铁槌“若不能消耗【炉心共鸣】恢复满能量……否则立即获得 3 点【炉心共鸣】”：原来漏了“否则 +3”，
    cntE 新字段 els（没消耗时计数 +N，没有 = 旧行为），DB 缩写 els；
  · 行迹龙之骑士“进入战斗和施放强化普攻时获得【魔力放出】，该效果下……消耗【魔力放出】恢复 1 个战技点并立即行动”：
    原来每次充满都给，改成状态【魔力放出】（开局 / 强普获得，充满时有它才 +1 战技点、立即行动，然后移除）；
  · 秘技“并获得 2 点【炉心共鸣】”补上（和秘技攻击力一起默认关）；
  · E6“湖之祝福可积攒的溢出能量提高到 200 点”做成 ecap（能量最多存 360+200=560），
    “进入战斗首次施放终结技后恢复 300 点能量，该效果每再施放 3 次终结技可触发 1 次”：新字段 ultEv（DB 缩写 oe）= 第 1、4、7… 次开大；
  · 伤害：强化普攻解放的金色王权原来把“敌方 1 个时额外 220%”并进了主倍率（v 370%），改成主倍率 150%（7 级 165%），
    额外部分走 XR，新字段 eqN（敌人卡数量正好 N 个时才算，没放敌人按 1 个）：2 个 +150%/165%、1 个 +220%/242%。
- Archer：战技增伤 +100% 补 3 魂 108%（lv）；E6“战技增伤可叠加层数 +1”用 ste [6, 3]（伤害增益也支持 stE 了）；
  秘技千里眼“并获得 1 点充能”补上（默认关）。
- 希儿【强化版】：终结技“立即进入增幅状态”原来漏了（增伤 80%/88% 和割裂穿透 25%，持续 3 回合）；
  E2“战技的加速效果可以叠加，最多叠加 2 层”原来漏了（加速共用 bk gr，ste [2, 2]；自动施放战技那条近似也共用）；
  DMG 战技 / 终结技换成强化版倍率（1110202：360%，12 级 396%；1110203：720%，12 级 792%；原来是旧版 220% / 425%）。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 49
assert f'if (s.tv >= {TV - 1}) return;' in s
SR = '/tmp/sr/'
SK = json.load(open(SR + 'character_skills.json'))
prm = lambda sid: SK[sid]['params']
def grab(name):
    m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
def put(m, obj):
    global s
    s = s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:90], s.count(x)); s = s.replace(x, y)

m, DB = grab('DB')
C = {c['id']: c for c in DB['chars']}
FIX = {}
def find(c, pred):
    L = [x for x in c['eff'] if pred(x)]; assert len(L) == 1, L; return L[0]

# ---------- Saber 1014 ----------
c = C[1014]
ce = find(c, lambda x: x['y'] == 'cntE')
o_ce = ce['n']; assert ce['t'] == 'skill' and ce['m'] == 'fill'
ce['els'] = 3
ce['n'] = '战技风王铁槌：消耗全部炉心共鸣能恢复满能量时消耗，每点固定 +8 能量；否则立即获得 3 点炉心共鸣'
spx = find(c, lambda x: x['y'] == 'sp' and x['t'] == 'cnt0')
adv = find(c, lambda x: x['y'] == 'advance' and x['t'] == 'cnt0')
o_sp, o_adv = spx['n'], adv['n']
spx['ns'] = '魔力放出'; spx['n'] = '行迹龙之骑士：【魔力放出】下消耗炉心共鸣充满能量时，消耗【魔力放出】为我方恢复 1 个战技点'
adv['ns'] = '魔力放出'; adv['n'] = '行迹龙之骑士：【魔力放出】下消耗炉心共鸣充满能量时，Saber 立即行动'
i = c['eff'].index(adv) + 1
mf0 = dict(y='state', t='cnt0', tg='self', v=0, sn='魔力放出', d=0, ns='魔力放出', n='行迹龙之骑士：上面两条生效后移除【魔力放出】')
c['eff'].insert(i, mf0)
mf1 = dict(y='state', t='start', tg='self', v=1, sn='魔力放出', d=0, pre=1, n='行迹龙之骑士：进入战斗时获得【魔力放出】')
mf2 = dict(y='state', t='ebasic', tg='self', v=1, sn='魔力放出', d=0, n='行迹龙之骑士：施放强化普攻时获得【魔力放出】')
j = c['eff'].index(spx)
c['eff'][j:j] = [mf1, mf2]
tech = find(c, lambda x: x.get('bk') == 'tech')
tc = dict(y='count', t='start', tg='self', v=2, off=1, n='秘技骑士王的登场：下一次战斗开始时获得 2 点炉心共鸣（用了秘技再启用）')
c['eff'].insert(c['eff'].index(tech) + 1, tc)
e6 = next(e for e in c['eid'] if e['r'] == 6)
en = next(x for x in e6['eff'] if x['y'] == 'energy'); assert en.get('once') and en['v'] == 300
en['oe'] = 3
en['n'] = 'E6：进入战斗首次施放终结技后固定恢复 300 能量，之后每再施放 3 次终结技触发 1 次（第 1、4、7… 次）'
e6['eff'].insert(0, dict(y='ecap', t='start', tg='self', v=round(560 / 360 * 100, 8),
                         n='E6：湖之祝福可积攒的溢出能量提高到 200 点（能量最多存 360 + 200 = 560）'))
e6['notes'] = [x for x in e6.get('notes', []) if '溢出能量提高到 200' not in x]
FIX['1014'] = {'drop': [o_ce, o_sp, o_adv], 'trig': {o_ce: 'skill', o_sp: 'cnt0', o_adv: 'cnt0'},
               'map': {o_ce: ce['n'], o_sp: spx['n'], o_adv: adv['n']},
               'add': [ce['n'], mf1['n'], mf2['n'], spx['n'], adv['n'], mf0['n'], tc['n']], 'sm': {}}

# ---------- Archer 1015 ----------
c = C[1015]
hl = find(c, lambda x: x.get('bk') == 'hl')
o_hl = hl['n']; assert hl['v'] == 100 and 'lv' not in hl
sk = prm('1015' + '02')  # 101502 第 2 个参数 = 战技增伤
assert abs(sk[9][1] - 1) < 1e-9 and abs(sk[11][1] - 1.08) < 1e-9
hl['lv'] = [3, 108]; hl['ste'] = [6, 3]
hl['n'] = '战技：【回路连接】中施放战技后战技伤害 +100%（3 魂 108%），最多 2 层（6 魂 3 层；行动记录在战技之后才记，所以这次战技就会吃到新的一层，偏高）'
e6 = next(e for e in c['eid'] if e['r'] == 6)
for x in e6['eff']:
    if x.get('bk') == 'e6': x['n'] = 'E6：战技无视 20% 防御力（战技增伤可叠加层数 +1 已写在战技那条）'
tc = dict(y='count', t='start', tg='self', v=1, off=1, n='秘技千里眼：进入战斗后获得 1 点充能（用了秘技再启用；伤害没算）')
c['eff'].insert(1, tc)
FIX['1015'] = {'drop': [o_hl], 'trig': {o_hl: 'skill'}, 'map': {o_hl: hl['n']}, 'add': [hl['n'], tc['n']], 'sm': {}}

# ---------- 希儿 1102（强化版） ----------
c = C[1102]
sp1 = find(c, lambda x: x['y'] == 'spd' and x['t'] == 'skill')
sp2 = find(c, lambda x: x['y'] == 'spd' and x['t'] == 'atk')
o1, o2 = sp1['n'], sp2['n']
for x in (sp1, sp2): x['bk'] = 'gr'; x['ste'] = [2, 2]
sp1['n'] = '【强化版】战技：速度 +25%，持续 3 回合（E2 可叠加 2 层）'
sp2['n'] = '【强化版】战技：队友攻击后目标生命值 ≤50% 时自动施放战技（不耗战技点、不回能量，每回合 1 次；这里只算加速，和战技共用层数）'
zf = find(c, lambda x: x.get('bk') == 'zf' and x['t'] == 'kill')
gl = find(c, lambda x: x.get('bk') == 'gl' and x['t'] == 'kill')
assert zf['d'] == 3 and gl['d'] == 3
u1 = dict(zf, t='ult', n='【强化版】终结技：立即进入增幅状态，伤害 +80%（3 魂 88%），持续 3 回合')
u2 = dict(gl, t='ult', n='【强化版】行迹割裂：终结技进入增幅状态时量子属性抗性穿透 +25%')
i = c['eff'].index(gl) + 1
c['eff'][i:i] = [u1, u2]
FIX['1102'] = {'drop': [o1, o2], 'trig': {o1: 'skill', o2: 'atk'}, 'map': {o1: sp1['n'], o2: sp2['n']},
               'add': [sp1['n'], sp2['n'], u1['n'], u2['n']], 'off0': [], 'sm': {}}
put(m, DB)

# ---------- 伤害表 ----------
m, DMG = grab('DMG')
r4 = lambda v: round(v, 4)
d = DMG['1102']
d['s'] = dict(d['s'], v=[r4(x[0]) for x in prm('1110202')], n='归刃（强化版）')
d['u'] = dict(d['u'], v=[r4(x[0]) for x in prm('1110203')], n='乱蝶（强化版）')
assert d['s']['v'][9] == 3.6 and d['u']['v'][9] == 7.2
d = DMG['1014']
assert d['b2']['v'][5] == 3.7
d['b2'] = dict(d['b2'], v=[r4(x[0]) for x in prm('101408')])
assert d['b2']['v'][5] == 1.5
put(m, DMG)

m, XR = grab('XR')
assert '1014' not in XR
b2 = prm('101408')
XR['1014'] = [
    dict(k='n2', n='强化普攻解放的金色王权：施放时敌方目标数量为 2，额外对敌方全体 150%（7 级 165%）', on=['b2'], st='atk', v=[r4(b2[5][2]), r4(b2[6][2])], lk='b', cnt='N', eqN=2),
    dict(k='n1', n='强化普攻解放的金色王权：施放时敌方目标数量为 1，额外 220%（7 级 242%；没放敌人卡按 1 个）', on=['b2'], st='atk', v=[r4(b2[5][3]), r4(b2[6][3])], lk='b', cnt='N', eqN=1),
]
put(m, XR)

# ---------- 代码：新字段 ----------
rep('      if (x.once) e.once = true;\n', '      if (x.once) e.once = true;\n      if (x.oe) e.ultEv = x.oe;   // 只第一次开大 + 之后每再开 N 次大触发 1 次（Saber 6 魂：第 1、4、7… 次）\n      if (x.els) e.els = x.els;   // 计数换能量：没消耗时计数 +N（Saber 战技“否则立即获得 3 点炉心共鸣”）\n')
rep('      if (eff.once && src && (src.ultN || 1) > 1) return;   // 只在第一次开大时生效\n',
    '      if (eff.once && src && (src.ultN || 1) > 1 && !(num(eff.ultEv) > 0 && ((src.ultN || 1) - 1) % Math.round(num(eff.ultEv)) === 0)) return;   // 只在第一次开大时生效（ultEv：之后每再开 N 次大再生效 1 次）\n')
rep('{ curWhy = `消耗 ${n} 点${tg.cntName || "计数"}`; addEnergy(tg, n * v, false); subCnt(tg, n); }\n          continue;',
    '{ curWhy = `消耗 ${n} 点${tg.cntName || "计数"}`; addEnergy(tg, n * v, false); subCnt(tg, n); }\n          else if (num(eff.els) > 0) addCnt(tg, num(eff.els));   // 没消耗：计数 +N（Saber 风王铁槌）\n          continue;')
rep('        if (r.minN && enemyCount() < r.minN) continue;\n',
    '        if (r.minN && enemyCount() < r.minN) continue;\n        if (r.eqN && enemyCount() !== r.eqN) continue;   // 敌人正好 N 个（Saber 解放的金色王权）\n')
rep('const dur = Math.max(0, Math.round(num(eff.duration))), lim = Math.round(num(eff.stack));\n      const bk = eff.bk ? String(eff.bk) : "", key = (src ? src.id : "ev") + ":" + (bk ? bk + (bk.startsWith("st:")',
    'const dur = Math.max(0, Math.round(num(eff.duration))), lim = Array.isArray(eff.stE) && src && num(src.eid) >= num(eff.stE[0]) ? Math.round(num(eff.stE[1])) : Math.round(num(eff.stack));   // stE：几魂起叠层上限变（Archer 6 魂战技增伤 3 层）\n      const bk = eff.bk ? String(eff.bk) : "", key = (src ? src.id : "ev") + ":" + (bk ? bk + (bk.startsWith("st:")')
rep('${e.once ? `<span class="hint">只第一次开大</span>` : ""}', '${e.once ? `<span class="hint">${num(e.ultEv) > 0 ? `第 1 次开大，之后每 ${e.ultEv} 次再 1 次` : "只第一次开大"}</span>` : ""}')

# ---------- 迁移 ----------
a = re.search(rf'  // tv {TV - 1}：', s)
s = s[:a.start()] + (f'  // tv {TV}：每日校对 11-03（黑塔、Saber、Archer、希儿，tools/fix{TV}.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()})
