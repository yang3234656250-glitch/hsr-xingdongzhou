"""tv 44：「泉刃缇霍」队伍（黄泉、千冶•刃、缇宝、藿藿）按官方原文补齐 + 新手任务开始前 / 等价交换 / 出云显世 2 件。
用法：python3 tools/fix44.py index.html
- 千冶•刃：结界 / 【无量忿怒】做成状态 + 70 速倒计时；平时普攻、无量忿怒期间战技；天赋充能按结界自动生效；千锻魂受击充能、受到治疗 +50%；
  百炼骨（溢出 80、开局 / 结界解除补到 75%）；万淬心按队里有没有其他虚无自动选；2 魂充能上限 7；1 魂倒计时延后 15%；6 魂消耗生命值 +1 充能；
  第二种终结技【千冶铸一，万劫烬灭】的伤害（U2ST）、天赋额外战技按战技倍率算伤害（F2K）。
- 黄泉：奈落 / 2 魂按其他虚无人数自动判断；天赋 +1 残梦在千冶•刃结界期间按攻击自动生效（煞火缠身是负面效果）。
- 缇宝：天赋追加攻击每个队友 1 次、缇宝开大时重置；补秘技神启（默认关）。
- 藿藿：终结技给其他队友恢复 20% 能量上限的能量（漏了）；天赋治疗按生命值百分比最低的目标 + 生命值 ≤50% 的目标；贞凶之命只给能量上限 ≥160 的目标。
"""
import re, json, sys
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
TV = 44
assert f'if (s.tv >= {TV - 1}) return;' in s
m = re.search(r'const DB = (\{.*?\});\n', s); DB = json.loads(m.group(1))
C = {c['id']: c for c in DB['chars']}; LC = {l['id']: l for l in DB['lcs']}; RL = {r['id']: r for r in DB['relics']}
FIX = {}

def rebuild(cid, new, keep_off_on=()):
    """整组按模板顺序重建：旧说明全部 drop（trig 记原触发），同名或对应的新说明 map，add 放全部新说明"""
    c = C[cid]; old = c['eff']
    drop = [e['n'] for e in old if e.get('y') != 'info']
    trig = {e['n']: e['t'] for e in old if e.get('y') != 'info'}
    info = [e for e in old if e.get('y') == 'info']
    names = {e['n'] for e in new}
    return drop, trig, info

# ---------- 千冶•刃 1507 ----------
c = C[1507]
OLD = {e['n']: e for e in c['eff']}
O = lambda k: next(n for n in OLD if n.startswith(k))
N_ULTHP = '终结技骸骨当炉：消耗自身 20% 生命上限的生命值，展开结界（【千冶铸一，万劫烬灭】不消耗）'
new1507 = [
    OLD[O('战技刃下，归葬')],
    OLD[O('天赋：充能满时额外施放的战技')],
    dict(y='hpcost', t='ult', tg='self', v=20, m='max', ns='!无量忿怒', n=N_ULTHP),
    dict(y='summon', t='ult', tg='sm:wl', v=0, ns='!无量忿怒', n='终结技：展开结界，【无量忿怒】倒计时上场（速度 70，倒计时回合开始时结界解除）'),
    dict(y='force', t='ult', tg='self', v=99, m='skill', ns='!无量忿怒', n='终结技：【无量忿怒】期间解放战技（默认每次行动施放战技，不耗战技点；想用强化普攻在“每次行动”或行动轴上改）'),
    dict(y='state', t='ult', tg='self', sn='无量忿怒', d=0, v=1, ns='!无量忿怒', n='终结技：展开结界、进入【无量忿怒】，同时获得新终结技【千冶铸一，万劫烬灭】（结界中再开大就是它）'),
    dict(y='count', t='atk', tg='self', v=1, aw='all', ns='无量忿怒', n='天赋因果尽偿：结界持续期间我方目标每次攻击后 +1 充能（敌人陷入【煞火缠身】）'),
    dict(y='count', t='hit', tg='self', v=1, ns='无量忿怒', n='行迹千锻魂：结界持续期间受到攻击后 +1 充能'),
    OLD[O('天赋：充能满 9 时回 25 能量')] | {'n': '天赋：充能满 9 点（2 魂 7 点）时回 25 能量（3 魂 27）'},
    OLD[O('天赋：充能满 9 点时额外施放')] | {'n': '天赋：充能满时额外施放 1 次战技（视为追加攻击，伤害按战技倍率）'},
    OLD[O('终结技：【无量忿怒】中受到致命攻击')],
    dict(y='hbup', m='in', t='ult', tg='self', v=50, d=0, bk='st:无量忿怒', n='行迹千锻魂：结界持续期间受到的治疗量提高 50%'),
    dict(y='energy', t='start', tg='self', m='atl', v=75, n='行迹百炼骨：战斗开始时能量不足 75% 则恢复至 75%'),
    dict(y='energy', t='smEnd', sk='wl', tg='self', m='atl', v=75, n='行迹百炼骨：结界解除时能量不足 75% 则恢复至 75%'),
    dict(y='state', t='smEnd', sk='wl', tg='self', sn='无量忿怒', d=0, v=0, n='倒计时回合开始：结界解除，退出【无量忿怒】'),
    dict(y='force', t='smEnd', sk='wl', tg='self', v=0, m='skill', n='结界解除，恢复平时的行动（普攻；未处于【无量忿怒】时无法施放战技）'),
    OLD[O('终结技：【煞火缠身】敌方防御力')],
    OLD[O('终结技：【煞火缠身】敌方受到的伤害')],
    dict(y='dbuf', t='ult', tg='self', m='cr', v=20, d=0, bk='st:无量忿怒#wlr', n='终结技：【无量忿怒】暴击率 +20%（结界解除时消失）'),
    dict(y='dbuf', t='ult', tg='self', m='cd', v=60, lv=[3, 66], d=0, bk='st:无量忿怒#wlc', n='终结技：【无量忿怒】暴击伤害 +60%（3 魂 66%，结界解除时消失）'),
    dict(y='dbuf', t='ult', tg='team', m='dmg', v=50, d=0, bk='st:无量忿怒#wc', n='行迹万淬心：结界持续期间我方造成的伤害 +50%'),
    dict(y='dbuf', t='ult', tg='self', m='dmg', v=75, d=0, bk='st:无量忿怒#wc2', px=['虚无', 0], n='行迹万淬心：队伍里没有其他虚无角色时，千冶•刃造成的伤害额外 +75%（自动判断）'),
    dict(y='dbuf', t='ult', tg='team', m='dmg', v=75, sc='u', d=0, bk='st:无量忿怒#wc3', pm=['虚无', 1], n='行迹万淬心：有其他虚无角色时，我方造成的终结技伤害 +75%（自动判断）'),
]
for e in c['eff']:
    if e.get('y') == 'info': new1507.append(e)
oldnames = [e['n'] for e in c['eff'] if e.get('y') != 'info']
map1507 = {
    O('终结技：消耗自身 20%'): N_ULTHP,
    O('天赋：结界期间我方每次攻击'): '天赋因果尽偿：结界持续期间我方目标每次攻击后 +1 充能（敌人陷入【煞火缠身】）',
    O('天赋：充能满 9 时回 25 能量'): '天赋：充能满 9 点（2 魂 7 点）时回 25 能量（3 魂 27）',
    O('天赋：充能满 9 点时额外施放'): '天赋：充能满时额外施放 1 次战技（视为追加攻击，伤害按战技倍率）',
    O('行迹千锻魂'): '行迹千锻魂：结界持续期间受到的治疗量提高 50%',
    O('终结技：【无量忿怒】暴击率'): '终结技：【无量忿怒】暴击率 +20%（结界解除时消失）',
    O('终结技：【无量忿怒】暴击伤害'): '终结技：【无量忿怒】暴击伤害 +60%（3 魂 66%，结界解除时消失）',
    O('行迹万淬心：结界持续期间'): '行迹万淬心：结界持续期间我方造成的伤害 +50%',
    O('行迹万淬心：队伍里没有'): '行迹万淬心：队伍里没有其他虚无角色时，千冶•刃造成的伤害额外 +75%（自动判断）',
    O('行迹万淬心：有其他虚无'): '行迹万淬心：有其他虚无角色时，我方造成的终结技伤害 +75%（自动判断）',
}
for k in list(OLD):
    if k in [e['n'] for e in new1507]: map1507.setdefault(k, k)
off0_1507 = [O('天赋：结界期间我方每次攻击'), O('行迹千锻魂'), O('行迹万淬心：有其他虚无')]
c['eff'] = new1507
c['x'] = dict(c['x'], act='basic', capE=240)
c['sm'] = [dict(k='wl', n='无量忿怒倒计时', spd=70, life=1, cd=True)]
c['cnt'] = dict(c['cnt'], le=[2, 7])
c['notes'] = [n for n in c.get('notes', []) if '无量忿怒' not in n and '结界' not in n] + [
    '结界和【无量忿怒】做成同一个状态【无量忿怒】（缇宝的结界是另一个），倒计时（速度 70）回合开始时解除；“当前生命值大于 1 才能施放战技 / 额外战技”没做（生命值降到 1 时请手动改普攻）',
    '【千冶铸一，万劫烬灭】和第一个终结技一样要 160 能量；百炼骨：能量最多存 240，开大扣 160、多出的保留']
E = {r['r']: r for r in c['eid']}
E[1]['eff'] = [
    dict(y='dbuf', t='ult', tg='enemies', m='resRed', v=20, d=0, bk='st:无量忿怒#e1', n='E1：结界持续期间敌方全体全属性抗性 −20%（结界解除时消失）'),
    dict(y='delay', t='cnt', tg='sm:wl', v=15, n='E1：施放天赋的额外战技后【无量忿怒】倒计时行动延后 15%'),
]
E[1]['notes'] = []
E[4]['eff'] = [dict(y='dbuf', t='ult', tg='team', m='dmg', v=50, d=0, bk='st:无量忿怒#e4', n='E4：万淬心的增伤额外 +50%（结界期间）')]
E[6]['eff'] = [
    dict(y='count', t='hpLoss', ew='self', tg='self', v=1, ns='无量忿怒', ptn=1, n='E6：结界持续期间受到伤害或消耗生命值时 +1 充能（任意目标回合结束后可再次触发，按每个回合 1 次）'),
] + [e for e in E[6]['eff'] if e.get('y') == 'dbuf']
FIX['1507'] = {'drop': oldnames, 'trig': {e: OLD[e]['t'] for e in oldnames}, 'map': map1507,
               'add': [e['n'] for e in new1507 if e.get('y') != 'info'], 'off0': off0_1507,
               'set': {'act': 'basic', 'capE': 240}, 'sm': {}}

# ---------- 黄泉 1308 ----------
c = C[1308]
pat1308 = {}
e = next(x for x in c['eff'] if x['n'].startswith('行迹奈落：队里有 1 名'))
pat1308[e['n']] = '行迹奈落：队里有其他虚无角色时伤害为原伤害的 115%（普攻、战技、终结技；自动判断）'; e['n'] = pat1308[e['n']]; e['pm'] = ['虚无', 1]
e = next(x for x in c['eff'] if x['n'].startswith('行迹奈落：有 2 名'))
pat1308[e['n']] = '行迹奈落：有 2 名其他虚无角色时为 160%（和上一条合起来 ×1.6；自动判断）'; e['n'] = pat1308[e['n']]; e['pm'] = ['虚无', 2]; e.pop('off', None)
e2 = next(r for r in c['eid'] if r['r'] == 2)
x = next(x for x in e2['eff'] if x['n'].startswith('E2：奈落只需'))
x['n'] = 'E2：奈落只需 1 名其他虚无角色即为 160%（和奈落第一条合起来 ×1.6；只有 1 名时生效，自动判断）'; x['pm'] = ['虚无', 1]; x['px'] = ['虚无', 1]
gen = next(x for x in c['eff'] if x['n'].startswith('天赋：任意单位施放技能期间'))
gen['n'] = '天赋：任意单位施放技能期间使敌人陷入负面效果时 +1 残梦（通用近似：按“队友行动 / 开大后”；队里有千冶•刃时用下面三条，别开这条）'
pat1308_gen_old = '天赋：任意单位施放技能期间使敌人陷入负面效果时 +1 残梦（每次施放技能最多 1 次；按“队友行动 / 开大后”近似，确认这次会上负面效果再启用；黄泉自己的战技已单独算）'
i = c['eff'].index(gen) + 1
new_t = [
    dict(y='energy', t='atk', aw='all', tg='self', v=1, m='fixed', ns='无量忿怒', so='team', n='天赋：千冶•刃结界期间我方任意角色攻击后（敌人陷入【煞火缠身】）+1 残梦（自动判断）'),
    dict(y='energy', t='aUlt', aw='others', at=1507, tg='self', v=1, m='fixed', n='天赋：千冶•刃施放终结技（敌方全体陷入【煞火缠身】）+1 残梦'),
    dict(y='energy', t='atk', aw='others', at=1507, tg='self', v=1, m='fixed', ns='!无量忿怒', so='team', n='天赋：千冶•刃结界外的普攻（目标陷入嘲讽）+1 残梦'),
]
c['eff'][i:i] = new_t
FIX['1308'] = {'drop': list(pat1308) + [pat1308_gen_old], 'trig': {k: 'start' for k in pat1308} | {pat1308_gen_old: 'ally'},
               'map': dict(pat1308) | {pat1308_gen_old: gen['n']}, 'add': list(pat1308.values()) + [gen['n']] + [x['n'] for x in new_t],
               'off0': [k for k in pat1308 if '2 名' in k], 'sm': {}}

# ---------- 缇宝 1403 ----------
c = C[1403]
e = next(x for x in c['eff'] if x['n'].startswith('天赋：其他队友施放终结技后追加攻击'))
o = e['n']; e['n'] = '天赋：其他队友施放终结技后追加攻击（每个队友 1 次，缇宝施放终结技时重置）'; e['pw'] = 1; e['acR'] = 'ult'
tech = dict(y='dbuf', t='start', tg='team', m='resPen', v=24, lv=[5, 26.4], d=3, bk='sq', off=1, n='秘技开心你就拍拍手：进入战斗时获得【神启】3 回合，我方全体全属性抗性穿透 +24%（用了秘技再启用）')
c['eff'].append(tech)
FIX['1403'] = {'drop': [o], 'trig': {o: 'aUlt'}, 'map': {o: e['n']}, 'add': [e['n'], tech['n']], 'sm': {}}

# ---------- 藿藿 1217 ----------
c = C[1217]
e = next(x for x in c['eff'] if x['n'].startswith('【强化版】天赋：同时回复生命值百分比最低'))
o1 = e['n']; e['n'] = '【强化版】天赋：同时回复生命值百分比最低的我方目标（按当前生命值自动选）'; e['tg'] = 'lowhp'; e.pop('off', None)
hp50 = dict(e, n='【强化版】天赋：随后为每个当前生命值 ≤50% 的我方目标再回复一次（按当前生命值）', tg='hp50')
c['eff'].insert(c['eff'].index(e) + 1, hp50)
z = next(x for x in c['eff'] if x['n'].startswith('行迹贞凶之命'))
o2 = z['n']; z['n'] = '行迹贞凶之命：施放终结技时能量上限 ≥160 的目标攻击力额外 +24%（自动判断）'; z['tge'] = 160; z.pop('off', None)
ue = dict(y='energy', t='ult', tg='others', m='maxp', v=20, lv=[3, 21], n='【强化版】终结技：为除自身以外的队友恢复各自 20% 能量上限的能量（3 魂 21%；残梦这类不是能量的不算）')
c['eff'].insert(c['eff'].index(next(x for x in c['eff'] if x['n'].startswith('终结技：除自身外的队友攻击力'))), ue)
FIX['1217'] = {'drop': [o1, o2], 'trig': {o1: 'aTurn', o2: 'ult'}, 'map': {o1: e['n'], o2: z['n']},
               'add': [e['n'], hp50['n'], z['n'], ue['n']], 'off0': [o1, o2], 'sm': {}}

# ---------- 光锥 / 遗器 ----------
LC[22000]['eff'] = [dict(y='energy', m='er', t='atk', aw='self', tg='self', v=[4, 5, 6, 7, 8], ns='无量忿怒', so='team',
                         n='新手任务开始前：攻击防御力被降低的敌人后恢复能量（按千冶•刃结界期间【煞火缠身】降防自动判断；别的降防来源请自己改条件）')]
LC[21021]['eff'] = [dict(y='energy', m='er', t='turn', tg='elow', v=[8, 10, 12, 14, 16],
                         n='等价交换：回合开始时为 1 名能量低于 50% 的其他角色恢复能量（游戏里随机，这里给能量百分比最低的）')]
r = RL[314]['p2']['eff'][0]; r['n'] = '2件：至少有 1 名和装备者同命途的队友时暴击率提高 12%（自动判断）'; r['pm'] = ['=', 1]; r.pop('off', None)
EQ = {'lc': [21021, 22000], 'rel': [314]}

s = s[:m.start(1)] + json.dumps(DB, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:80], s.count(x)); s = s.replace(x, y)
a = re.search(r'  function fixTpl43\(s\) \{', s)
s = s[:a.start()] + (f'  // tv {TV}：泉刃缇霍（黄泉、千冶•刃、缇宝、藿藿）按原文补齐，新手任务开始前 / 等价交换 / 出云 2 件（tools/fix44.py）\n'
    f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + f';\n  const EQFIX{TV} = ' + json.dumps(EQ) + ';\n'
    f'  function fixTpl{TV}(s) {{\n'
    f'    const keep = S; S = s;\n'
    f'    try {{\n'
    f'      for (const u of s.units) if (u.kind === "ally" && !u.sm && tidOf(u) === "1507" && !s.units.some(z => z.sm && z.sm.owner === u.id && z.sm.key === "wl"))\n'
    f'        s.units.push({{ id: nid(), name: "无量忿怒倒计时", color: u.color, kind: "ally", spd: 70, base: 70, opening: 0, effects: [], sm: {{ owner: u.id, key: "wl", ratio: 0, life: 1, start: false, cd: true, pause: false, fua: false, noTurn: false }} }});\n'
    f'      // 黄泉：队里有千冶•刃时，通用近似那条“天赋 +1 残梦”会和新的三条重复，关掉\n'
    f'      const hasQ = s.units.some(z => z.kind === "ally" && !z.sm && tidOf(z) === "1507");\n'
    f'      fixTpl(s, TPLFIX{TV});\n'
    f'      if (hasQ) for (const u of s.units) if (tidOf(u) === "1308") for (const e of u.effects) if (String(e.note || "").startsWith("天赋：任意单位施放技能期间")) e.off = true;\n'
    f'      for (const u of s.units) if (u.kind === "ally" && !u.sm && !TPLFIX{TV}[tidOf(u)] && (EQFIX{TV}.lc.includes(u.lc) || [u.rA, u.rB, u.rP].some(r => EQFIX{TV}.rel.includes(r)))) applyEquip(u);\n'
    f'    }} finally {{ S = keep; }}\n'
    f'  }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    if (!(s.tv >= {TV - 1})) fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    if (!(s.tv >= {TV - 1})) fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
for k, v in FIX.items():
    for d in v['drop']: assert d in v['trig'], (k, d)
print('ok', {k: (len(v['drop']), len(v['add'])) for k, v in FIX.items()})
