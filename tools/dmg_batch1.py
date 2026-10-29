"""伤害增益第 1 批：记忆队（昔涟、长夜月、遐蝶、风堇）+ 她们的光锥 / 遗器。
往 index.html 的 DB 里追加效果，并生成 TPLFIX21 / EQFIX21（已有配置补上新效果）。只跑一次。"""
import re, json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = open(P, encoding='utf-8').read()
m = re.search(r'const DB = (\{.*?\});\n', s); DB = json.loads(m.group(1))
C = {c['id']: c for c in DB['chars']}; LC = {l['id']: l for l in DB['lcs']}; RL = {r['id']: r for r in DB['relics']}
D = lambda **k: dict(y='dbuf', **k)
BASE = {
 1415: [
  dict(y='state', t='skill', tg='self', sn='结界', d=2, v=1, ts=1, n='战技：展开结界，持续 2 回合（昔涟每回合开始时 −1）'),
  D(t='skill', tg='team', m='xtra', v=24, lv=[5, 26.4], d=0, bk='st:结界', n='战技：结界持续期间，我方全体每造成 1 次伤害再额外造成原伤害 24% 的真实伤害（伤害估算 ×1.24）'),
  dict(y='state', t='ult', tg='self', sn='结界', d=0, v=1, first=1, n='终结技：展开战技的结界，且结界没有持续时间'),
  D(t='ult', tg='team', m='xtra', v=24, lv=[5, 26.4], d=0, bk='st:结界', first=1, n='终结技：展开的结界同样使我方全体额外造成原伤害 24% 的真实伤害'),
  D(t='ult', tg='self', m='cr', v=50, lv=[3, 55], d=0, first=1, bk='rcr', n='终结技：【往昔的涟漪】中昔涟暴击率 +50%'),
  D(t='ult', tg='sm:demiurge', m='cr', v=50, lv=[3, 55], d=0, first=1, bk='rcr', n='终结技：【往昔的涟漪】中德谬歌暴击率 +50%'),
  D(t='start', tg='team', m='dmg', v=20, lv=[3, 22], d=0, bk='tal', n='天赋：昔涟在场时我方全体造成的伤害 +20%'),
  D(t='start', tg='team', m='dmg', v=20, d=0, ms=180, bk='tr180', n='行迹三相的因果：昔涟速度 ≥180 时我方全体造成的伤害 +20%（按战斗开始时的速度）'),
  D(t='start', tg='self', m='resPen', v=200, ss='spd', hf=-360, cap=120, d=0, ms=180, bk='trpen', n='行迹三相的因果：速度超过 180 的部分每 1 点昔涟冰属性抗性穿透 +2%（最多计入 60 点，按战斗开始时的速度）'),
  D(t='smOn', sk='demiurge', tg='sm:demiurge', m='resPen', v=200, ss='spd', hf=-360, cap=120, d=0, ms=180, bk='trpen', n='行迹三相的因果：德谬歌同样获得冰属性抗性穿透（按昔涟的速度）'),
  dict(y='state', t='start', tg='self', sn='结界', d=2, v=1, ts=1, off=1, n='秘技：进入战斗后展开战技的结界（用了秘技再启用）'),
  D(t='start', tg='team', m='xtra', v=24, lv=[5, 26.4], d=0, bk='st:结界', off=1, n='秘技：秘技展开的结界同样额外造成原伤害 24% 的真实伤害（用了秘技再启用）'),
 ],
 1413: [
  D(t='skill', tg='teamMem', m='cd', ss='cd', v=24, lv=[3, 26.4], d=2, bk='skcd', n='战技：我方全体忆灵暴击伤害提高长夜月暴击伤害的 24%，持续 2 回合（长夜月每回合开始时 −1；按卡片上的暴击伤害）'),
  D(t='skill', tg='teamMem', m='cd', ss='cd', v=12, d=2, bk='skcd2', ns='献予「岁月」之诗', n='忆灵技献予「岁月」之诗：长夜月战技的忆灵暴伤提高效果额外提高长夜月暴击伤害的 12%'),
  D(t='skill', tg='teamMem', m='cd', v=5, d=2, bk='skcd3', n='行迹天亮了，雨落了：战技持续期间我方全体忆灵暴击伤害额外 +5%（队伍里有 1 名「记忆」角色）'),
  D(t='skill', tg='teamMem', m='cd', v=15, d=2, bk='skcd3', mgt=1, n='行迹天亮了，雨落了：有 2 名「记忆」角色时改为 +15%（按队伍里除长夜月外的黄金裔或「记忆」角色数，近似）'),
  D(t='skill', tg='teamMem', m='cd', v=50, d=2, bk='skcd3', mgt=2, n='行迹天亮了，雨落了：有 3 名「记忆」角色时改为 +50%'),
  D(t='skill', tg='teamMem', m='cd', v=65, d=2, bk='skcd3', mgt=3, n='行迹天亮了，雨落了：有 4 名或以上「记忆」角色时改为 +65%'),
  D(t='ult', tg='enemies', m='vuln', v=30, lv=[5, 33], d=0, bk='st:至暗之谜', n='终结技：【至暗之谜】期间敌方全体受到的伤害 +30%'),
  D(t='ult', tg='self', m='dmg', v=60, lv=[5, 66], d=0, bk='st:至暗之谜', n='终结技：【至暗之谜】期间长夜月造成的伤害 +60%'),
  D(t='ult', tg='sm:evernight', m='dmg', v=60, lv=[5, 66], d=0, bk='st:至暗之谜', n='终结技：【至暗之谜】期间「长夜」造成的伤害 +60%'),
  D(t='smOn', sk='evernight', tg='sm:evernight', m='dmg', v=60, lv=[5, 66], d=0, bk='st:至暗之谜', ns='至暗之谜', n='终结技：【至暗之谜】期间重新召唤的「长夜」同样伤害 +60%'),
  D(t='hpLoss', ew='selfsm', tg='self', m='cd', v=60, lv=[5, 66], d=2, bk='talcd', n='天赋：长夜月或「长夜」生命值降低时，长夜月暴击伤害 +60%，持续 2 回合'),
  D(t='hpLoss', ew='selfsm', tg='sm:evernight', m='cd', v=60, lv=[5, 66], d=2, bk='talcd', n='天赋：同时「长夜」暴击伤害 +60%，持续 2 回合'),
  D(t='smOn', sk='evernight', tg='self', m='dmg', v=50, lv=[3, 55], d=0, bk='lone', n='忆灵天赋孤独，浮游，漆黑：「长夜」在场时长夜月造成的伤害 +50%'),
  D(t='smOn', sk='evernight', tg='sm:evernight', m='dmg', v=50, lv=[3, 55], d=0, bk='lone', n='忆灵天赋孤独，浮游，漆黑：「长夜」在场时「长夜」造成的伤害 +50%'),
  D(t='smEnd', sk='evernight', tg='self', m='dmg', v=0, d=0, bk='lone', n='忆灵天赋孤独，浮游，漆黑：「长夜」消失时上面的增伤结束'),
  D(t='smOn', sk='evernight', tg='sm:evernight', m='dmg', v=18, sc='m', d=0, bk='yue', ns='献予「岁月」之诗', n='忆灵技献予「岁月」之诗：「长夜」施放【迷梦，流失，如露】时造成的伤害 +18%（这里按「长夜」所有攻击算，近似）'),
  D(t='start', tg='self', m='cr', v=35, d=0, bk='tcr', n='行迹天黑黑，月寂寂：长夜月暴击率 +35%'),
  D(t='start', tg='sm:evernight', m='cr', v=35, d=0, bk='tcr', n='行迹天黑黑，月寂寂：「长夜」暴击率 +35%'),
  D(t='skill', o='basic', tg='self', m='cd', v=15, d=2, bk='tcd', n='行迹天黑黑，月寂寂：施放普攻 / 战技时长夜月暴击伤害 +15%，持续 2 回合'),
  D(t='skill', o='basic', tg='sm:evernight', m='cd', v=15, d=2, bk='tcd', n='行迹天黑黑，月寂寂：施放普攻 / 战技时「长夜」暴击伤害 +15%，持续 2 回合'),
  D(t='ult', tg='self', m='cd', v=15, d=2, bk='tcd', n='行迹天黑黑，月寂寂：施放终结技时长夜月暴击伤害 +15%，持续 2 回合'),
  D(t='ult', tg='sm:evernight', m='cd', v=15, d=2, bk='tcd', n='行迹天黑黑，月寂寂：施放终结技时「长夜」暴击伤害 +15%，持续 2 回合'),
  D(t='ally', aw='sm', tg='self', m='cd', v=15, d=2, bk='tcd', n='行迹天黑黑，月寂寂：「长夜」施放技能时长夜月暴击伤害 +15%，持续 2 回合'),
  D(t='ally', aw='sm', tg='sm:evernight', m='cd', v=15, d=2, bk='tcd', n='行迹天黑黑，月寂寂：「长夜」施放技能时「长夜」暴击伤害 +15%，持续 2 回合'),
  D(t='start', tg='teamMem', m='cd', ss='cd', v=24, d=2, bk='skcd', off=1, n='秘技愿有冷雨落下：下一次战斗开始时获得与战技相同的忆灵暴伤提高（用了秘技再启用）'),
 ],
 1407: [
  D(t='smOn', sk='dragon', tg='enemies', m='resRed', v=20, lv=[3, 22], d=0, bk='realm', n='终结技：境界【遗世冥域】（死龙在场期间）敌方全体全属性抗性 −20%'),
  D(t='smEnd', sk='dragon', tg='enemies', m='resRed', v=0, d=0, bk='realm', n='终结技：死龙消失时解除【遗世冥域】'),
  D(t='hpLoss', ew='any', tg='self', m='dmg', v=20, lv=[5, 22], st=3, d=3, bk='tal', n='天赋：我方损失生命值时，遐蝶造成的伤害 +20%，最多 3 层，持续 3 回合'),
  D(t='hpLoss', ew='any', tg='sm:dragon', m='dmg', v=20, lv=[5, 22], st=3, d=3, bk='tal', n='天赋：同时死龙造成的伤害 +20%（终结技使它扩散至死龙），最多 3 层，持续 3 回合'),
  D(t='smOn', sk='dragon', tg='team', m='dmg', v=10, d=3, bk='roar', n='忆灵天赋震彻寂壤的怒啸：死龙被召唤时我方全体造成的伤害 +10%，持续 3 回合'),
 ],
 1409: [
  D(t='hgive', aw='self', tg='sm:ika', m='dmg', v=80, lv=[5, 88], st=3, d=2, bk='tal', n='天赋：风堇或小伊卡提供治疗时，小伊卡造成的伤害 +80%，持续 2 回合，最多 3 层（按“为队友提供治疗后”算）'),
  D(t='start', tg='self', m='cr', v=100, d=0, bk='tcr', n='行迹阴云莞尔：风堇暴击率 +100%'),
  D(t='start', tg='sm:ika', m='cr', v=100, d=0, bk='tcr', n='行迹阴云莞尔：小伊卡暴击率 +100%'),
 ],
}
EID = {
 1415: {2: [D(t='ult', tg='team', m='xtra', v=6, st=4, d=0, bk='e2xtra', n='E2 十三种光彩，倒映明天：每有 1 名不同的角色获得德谬歌忆灵技的增益，结界的真实伤害倍率 +6%，最多 +24%（这里按每次开大 +6% 叠层，近似）')],
        6: [D(t='smOn', sk='demiurge', tg='enemies', m='defRed', v=20, d=0, bk='e6def', n='E6：德谬歌在场时敌方全体防御力 −20%（献予「真我」之诗触发过后；这里按德谬歌在场就生效）'),
            D(t='smEnd', sk='demiurge', tg='enemies', m='defRed', v=0, d=0, bk='e6def', n='E6：德谬歌消失时防御降低结束')]},
 1413: {1: [D(t='start', tg='teamMem', m='xtra', v=50, d=0, bk='e1', n='E1 睡吧，长夜有所梦：长夜月在场时我方忆灵造成的伤害为原伤害的 150%（敌人 1 名；2 名 130%、3 名 125%、4 名以上 120%，按你的关卡改数值）')],
        2: [D(t='start', tg='self', m='cd', v=40, d=0, bk='e2', n='E2：长夜月暴击伤害 +40%'), D(t='start', tg='sm:evernight', m='cd', v=40, d=0, bk='e2', n='E2：「长夜」暴击伤害 +40%')],
        6: [D(t='start', tg='team', m='resPen', v=20, d=0, bk='e6', n='E6 就这样，一直：长夜月在场时我方全体全属性抗性穿透 +20%')]},
 1407: {1: [D(t='start', tg='sm:dragon', m='xtra', v=20, d=0, bk='e1', off=1, n='E1：敌方当前生命值 ≤80% / ≤50% 时，死龙的爪痕、焰息、晦翼对其伤害为原伤害的 120% / 140%（不知道敌人血量，默认关闭；开了按 120%）'),
             D(t='start', tg='self', m='xtra', v=20, sc='s', d=0, bk='e1', off=1, n='E1：同上，【骸爪，冥龙之环拥】（按遐蝶的战技算，近似；默认关闭）')],
        6: [D(t='start', tg='self', m='resPen', v=20, d=0, bk='e6', n='E6：遐蝶造成伤害时量子属性抗性穿透 +20%'), D(t='start', tg='sm:dragon', m='resPen', v=20, d=0, bk='e6', n='E6：死龙造成伤害时量子属性抗性穿透 +20%')]},
 1409: {4: [D(t='start', tg='self', m='cd', ss='spd', v=200, hf=-400, cap=400, ms=200.1, d=0, bk='e4', n='E4：行迹暴风停歇强化，速度超过 200 的部分每 1 点风堇暴击伤害 +2%（按战斗开始时的速度）'),
            D(t='start', tg='sm:ika', m='cd', ss='spd', v=200, hf=-400, cap=400, ms=200.1, d=0, bk='e4', n='E4：同上，小伊卡暴击伤害（按风堇的速度）')],
        6: [D(t='smOn', sk='ika', tg='team', m='resPen', v=20, d=0, bk='e6', n='E6：小伊卡在场时我方全体全属性抗性穿透 +20%'),
            D(t='smEnd', sk='ika', tg='team', m='resPen', v=0, d=0, bk='e6', n='E6：小伊卡消失时抗性穿透结束')]},
}
LCADD = {
 23052: [D(t='smTurn', tg='enemies', m='vuln', v=[10, 12, 14, 16, 18], d=0, bk='lw1', n='约定：装备者的忆灵对我方施放忆灵技时获得【空白】，敌方全体受到的伤害提高（这里按忆灵第一次行动就获得）'),
         D(t='smTurn', tg='team', m='cd', v=[16, 19, 22, 25, 28], d=0, bk='lw2', n='约定：装备者的忆灵对敌方施放忆灵技时获得【诗行】，我方全体暴击伤害提高（同上）'),
         D(t='smTurn', tg='enemies', m='vuln', v=[16, 19.8, 23.8, 28, 32.4], d=0, bk='lw1', s1=1, n='约定：同时持有【空白】和【诗行】时效果提高 60%～80%（这里按忆灵第二次行动起算）'),
         D(t='smTurn', tg='team', m='cd', v=[25.6, 31.35, 37.4, 43.75, 50.4], d=0, bk='lw2', s1=1, n='约定：同上，暴击伤害')],
 23049: [D(t='smTurn', tg='teamMem', m='defIg', v=[20, 22.5, 25, 27.5, 30], d=0, bk='night1', n='未眠：持有【夜色】时我方全体忆灵造成的伤害无视目标的部分防御力'),
         D(t='smTurn', tg='self', m='dmg', v=[30, 37.5, 45, 52.5, 60], d=0, bk='night2', n='未眠：持有【夜色】时装备者造成的伤害提高'),
         D(t='smTurn', tg='sm', m='dmg', v=[30, 37.5, 45, 52.5, 60], d=0, bk='night2', n='未眠：持有【夜色】时装备者的忆灵造成的伤害提高')],
 23040: [D(t='hpLoss', ew='selfsm', tg='self', m='defIg', v=[30, 35, 40, 45, 50], d=2, bk='ming', n='铭刻：装备者或其忆灵损失生命值时获得【冥花】，装备者无视目标的部分防御力，持续 2 回合（原文“在自身回合内”，这里不区分）'),
         D(t='hpLoss', ew='selfsm', tg='sm', m='defIg', v=[30, 35, 40, 45, 50], d=2, bk='ming', n='铭刻：同上，装备者的忆灵')],
 23042: [D(t='smTurn', tg='enemies', m='vuln', v=[18, 22.5, 27, 31.5, 36], d=2, bk='rain', n='包容：装备者的忆灵施放忆灵技时，敌方全体受到的伤害提高，持续 2 回合（忆灵下一次攻击的附加伤害没算）')],
}
RELADD = {  # (套装, 'p2' / 'p4')
 (127, 'p4'): [D(t='skill', o='basic', tg='team', m='dmg', v=0, d=0, bk='r127d', n='4件：施放普攻 / 战技后，上一次的增伤结束'),
               D(t='skill', o='basic', tg='team', m='dmg', v=15, d=0, bk='r127d', si='in', n='4件：施放普攻 / 战技后若忆灵在场，我方全体造成的伤害 +15%，持续到下次施放普攻 / 战技')],
 (125, 'p4'): [D(t='hgive', aw='self', ac=1, tg='team', m='cd', v=15, d=2, bk='valkd', n='4件：持有【甘霖】时我方全体暴击伤害 +15%（2 回合，每回合最多触发 1 次）')],
 (124, 'p4'): [D(t='start', tg='self', m='cr', v=20, d=0, bk='poet', off=1, n='4件：进入战斗前速度小于 110 时暴击率 +20%（小于 95 时 +32%，改数值），默认关闭'),
               D(t='start', tg='sm', m='cr', v=20, d=0, bk='poet', off=1, n='4件：同上，对装备者的忆灵也生效（召唤后才有忆灵，开局在场的才吃得到）')],
 (319, 'p2'): [D(t='start', tg='self', m='cd', v=28, d=0, bk='bone', n='2件：生命上限 ≥5000 时装备者暴击伤害 +28%（按满足算）'),
               D(t='smOn', tg='sm', m='cd', v=28, d=0, bk='bone', n='2件：同上，装备者的忆灵')],
}
FIX = {}
for cid, L in BASE.items():
    C[cid]['eff'].extend(L)
    FIX[str(cid)] = {'drop': [], 'map': {}, 'trig': {}, 'add': [x['n'] for x in L], 'sm': {}}
for cid, R in EID.items():
    for r, L in R.items():
        ent = next((e for e in C[cid]['eid'] if e['r'] == r), None)
        if not ent: ent = {'r': r, 'eff': [], 'notes': []}; C[cid]['eid'].append(ent); C[cid]['eid'].sort(key=lambda e: e['r'])
        ent['eff'].extend(L)
    FIX.setdefault(str(cid), {'drop': [], 'map': {}, 'trig': {}, 'add': [], 'sm': {}})
for lid, L in LCADD.items(): LC[lid]['eff'].extend(L)
for (rid, part), L in RELADD.items(): RL[rid].setdefault(part, {'eff': [], 'notes': []})['eff'].extend(L)
EQ = {'lc': list(LCADD), 'rel': sorted({r for r, _ in RELADD})}
newdb = json.dumps(DB, ensure_ascii=False, separators=(',', ':'))
s = s[:m.start(1)] + newdb + s[m.end(1):]
# 迁移表
anchor = '  const fixTpl20 = s => fixTpl(s, TPLFIX20);'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + '\n  // tv 21：伤害增益第 1 批（记忆队 + 光锥 / 遗器）\n  const TPLFIX21 = ' + json.dumps(FIX, ensure_ascii=False) + ';\n  const EQFIX21 = ' + json.dumps(EQ) + ';\n  const fixTpl21 = s => { fixTpl(s, TPLFIX21); for (const u of s.units) if (u.kind === "ally" && !u.sm && !TPLFIX21[String((tplOf(u) || {}).id)] && (EQFIX21.lc.includes(u.lc) || [u.rA, u.rB, u.rP].some(r => EQFIX21.rel.includes(r)))) applyEquip(u); };')
open(P, 'w', encoding='utf-8').write(s)
print('ok', {k: len(v['add']) for k, v in FIX.items()}, EQ)
