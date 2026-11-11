"""tv 71：击破第 4 批 —— 大丽花 1321（结界、共舞者超击破、败谢添加弱点、E1 / E6）、阮•梅 1303【残梅绽】。
用法：python3 tools/fix71.py index.html <官方 json 目录>
引擎：weak 的 wel 可写 "st:状态名"（所有持有该状态的我方角色的属性）；模板 x.cmz = {st, be, fl, v, lv:[几魂, v]}：
持有者有状态 st 时，我方攻击过的敌人被挂上【残梅绽】，这个敌人要从弱点击破恢复的那个回合改成：不恢复、不行动，行动延后 be% × 击破特攻 + fl%，受一次 v% 击破伤害；下次轮到才恢复。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 71, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
def lvE(cid, base):
    for r in range(1, 7):
        for z in (F.RK[str(cid * 100 + r)].get('level_up_skills') or []):
            if str(z.get('id')) == str(base): return r
    raise KeyError(base)
D = lambda **k: dict(dict(y='dbuf', d=0), **k)

# ---------- 引擎 ----------
F.rep('''(en.wk || []).some(z => z.el === el || z.el === "all");''', '''(en.wk || []).some(z => z.el === "all" || z.el.includes(el));''')
F.rep('''const wl = eff.wel === "self" ? ELW[(tplOf(own) || {}).elem] : eff.wel === "first" ? ELW[(tplOf(f1) || {}).elem] : eff.wel; if (!wl) continue;''',
      '''const wl = eff.wel === "self" ? ELW[(tplOf(own) || {}).elem] : eff.wel === "first" ? ELW[(tplOf(f1) || {}).elem]
            : String(eff.wel).startsWith("st:") ? [...new Set(U.filter(z => z.kind === "ally" && !z.sm && !z.gone && hasSt(z, String(eff.wel).slice(3))).map(z => ELW[(tplOf(z) || {}).elem] || ""))].join("") : eff.wel; if (!wl) continue;   // st:状态名 = 持有该状态的我方角色的属性（大丽花【共舞者】）''')
F.rep('''        const base = num(v[1]) + (i === 0 ? num(v[0]) : i <= 2 ? num(v[2]) : 0); if (!(base > 0)) return;
        const was = !!en.broken;''', '''        const base = num(v[1]) + (i === 0 ? num(v[0]) : i <= 2 ? num(v[2]) : 0); if (!(base > 0)) return;
        if (!en.cmzUsed && !en.cmz) { const cz = U.find(z => z.kind === "ally" && !z.sm && !z.gone && tx(z).cmz && hasSt(z, String(tx(z).cmz.st))); if (cz) en.cmz = cz.id; }   // 结界中我方攻击后：施加【残梅绽】
        const was = !!en.broken;''')
F.rep('''      move(best); t = next; actor.dist = 0;
      const spd = spdOf(actor);''', '''      move(best); t = next; actor.dist = 0;
      if (actor.kind === "enemy" && actor.broken && actor.cmz && !actor.cmzUsed && byId[actor.cmz]) {   // 【残梅绽】：尝试从弱点击破恢复时，延长击破状态、行动延后、受一次击破伤害（这个回合不算过）
        const rm = byId[actor.cmz], cz = tx(rm).cmz || {}, be = num(rm.be) + dsum(dbSnap(rm), "be", "k"), dl = num(cz.be) * be / 100 + num(cz.fl);
        const vv = Array.isArray(cz.lv) && num(rm.eid) >= num(cz.lv[0]) ? num(cz.lv[1]) : num(cz.v), mx = toughMax(actor), wl = ELW[(tplOf(rm) || {}).elem] || "冰";
        actor.cmzUsed = true; actor.cmz = null; actor.dist = dl * 100;
        const r = { t, uid: rm.id, en: actor.id, k: "残梅绽", mult: BRKM[wl] * (0.5 + mx / 120) * vv / 100, stat: "brk", why: "brkd", db: dbSnap(rm), edb: edbSnap(), defIg: 0, seq: seq++, ebk: true }; dotRecs.push(r);
        marks.push({ t, uid: actor.id, label: "残梅绽", color: rm.color, from: rm.name });
        addLog(`${actor.name} 尝试从弱点击破恢复：【残梅绽】延长击破状态，行动延后 ${fmt(dl, 1)}%，并受到 ${fmt(vv, 1)}% ${wl}属性击破伤害的击破伤害`, false, rm.color); log[log.length - 1].dd = [r];
        checkUlts(); continue;
      }
      const spd = spdOf(actor);''')
F.rep('''if (actor.broken) { actor.broken = false; actor.yh = 0;''', '''if (actor.broken) { actor.broken = false; actor.yh = 0; actor.cmzUsed = false; actor.cmz = null;''')

# ---------- 阮•梅 ----------
has('130303', '延后数值等同于阮•梅#3[i]%的击破特攻+#4[i]%，并对其造成等同于阮•梅#5[i]%冰属性击破伤害的击破伤害')
eu = lvE(1303, 130303); u10, u12 = prm('130303', 10), prm('130303', 12); assert [r4(v) for v in u10[2:]] == [0.2, 0.1, 0.5] and r4(u12[4]) == 0.54
assert any(e.get('sn') == '阮•梅结界' for e in C[1303]['eff'])
c = C[1303]; c['notes'] = [n for n in c.get('notes', []) if '残梅绽' not in n]
F.rebuild(1303, list(c['eff']), x={'cmz': {'st': '阮•梅结界', 'be': 20, 'fl': 10, 'v': 50, 'lv': [eu, 54]}},
          notes=['终结技【残梅绽】：结界中我方攻击过的敌人，尝试从弱点击破状态恢复时改为延长击破状态、行动延后（阮•梅击破特攻的 20%% + 10%%）、受到 50%% 冰属性击破伤害的击破伤害（%d 魂 54%%）；恢复前不会再次附加（已自动处理，要放带韧性的敌人）' % eu])

# ---------- 大丽花 ----------
c = C[1321]
has('132102', '我方全体的弱点击破效率提高#3[i]%，敌方目标未处于弱点击破状态时承受的削韧值也能够转化为超击破伤害'); has('132102', '开启结界，持续#2[i]回合，大丽花回合开始时持续回合数减1')
has('132103', '并且会被添加所有【共舞者】属性的弱点'); has('132104', '会将本次攻击的削韧值转化为1次#5[i]%的超击破伤害'); has('132104', '会将本次伤害的削韧值转化为1次#3[i]%的超击破伤害')
has('r:132101', '天赋为【共舞者】提供的超击破伤害倍率对我方全体角色生效，其中【共舞者】的倍率额外提高40%'); has('r:132106', '【共舞者】的击破特攻提高150%')
es, et = lvE(1321, 132102), lvE(1321, 132104); assert es == et
s10, t10, t12, u10 = prm('132102', 10), prm('132104', 10), prm('132104', 12), prm('132103', 10)
assert s10[1:] == [3, 0.5] and prm('132102', 12)[2] == 0.5 and [r4(t10[2]), r4(t10[4]), r4(t12[2]), r4(t12[4])] == [2, 0.6, 2.2, 0.66] and u10[1] == 4
c['notes'] = [n for n in c.get('notes', []) if '战技结界' not in n]
new = list(c['eff']) + [
    dict(y='state', t='skill', tg='self', sn='大丽花结界', v=1, d=3, ts=1, n='战技：开启结界，持续 3 回合（大丽花回合开始时 −1）'),
    D(t='skill', tg='team', m='bef', v=50, bk='st:大丽花结界', n='战技：结界持续期间我方全体弱点击破效率 +50%'),
    D(t='skill', tg='team', m='sbkA', v=1, bk='st:大丽花结界#a', n='战技：结界持续期间，敌方目标没处于弱点击破状态时承受的削韧值也能转化为超击破伤害'),
    D(t='start', tg='self', m='sbk', v=60, lv=[et, 66], bk='gw', xe=1, n='天赋：【共舞者】（大丽花）攻击弱点击破状态的敌人后，把削韧值转化为 1 次 60%%（%d 魂 66%%）的超击破伤害' % et),
    D(t='start', tg='$ally', m='sbk', v=60, lv=[et, 66], bk='gw', xe=1, n='天赋：【共舞者】（另一位，目标和上面【共舞者】那条选同一个队友）攻击弱点击破状态的敌人后，把削韧值转化为 1 次 60%%（%d 魂 66%%）的超击破伤害' % et),
    D(t='start', tg='self', m='sbk', v=200, lv=[et, 220], sc='f', bk='gwf', n='天赋：追加攻击每次对弱点击破状态的敌人造成伤害后，把削韧值转化为 1 次 200%%（%d 魂 220%%）的超击破伤害（和【共舞者】的那一次相加）' % et),
    dict(y='weak', t='ult', tg='enemies', wel='st:共舞者', d=4, bk='bx', n='终结技：【败谢】状态下敌方全体被添加所有【共舞者】属性的弱点，持续 4 回合'),
    D(t='start', tg='others', m='be', v=50, d=1, bk='zl', n='行迹又一场葬礼：进入战斗时其他角色击破特攻 +（大丽花击破特攻的 24% + 50%），持续 1 回合（这里只算 +50%，要算上 24% 那部分请自己改数值；受到治疗 / 护盾后再次触发没做）'),
]
F.rebuild(1321, new, notes=['天赋追加攻击的削韧只按 1 次伤害打主目标算（实际是 5 次随机目标），超击破会偏低', '行迹弃旧，恋新的 20 点固定削韧和回能、E1 的固定削韧、秘技还没做'])
e1 = F.eid(1321, 1); e1['eff'] = e1.get('eff', []) + [
    D(t='start', tg='team', m='sbk', v=60, lv=[et, 66], bk='e1t', n='E1：天赋的超击破伤害倍率对我方全体角色生效（60%%，%d 魂 66%%）' % et),
    D(t='start', tg='self', m='sbk', v=40, bk='e1g', n='E1：【共舞者】（大丽花）的超击破倍率额外 +40%'),
    D(t='start', tg='$ally', m='sbk', v=40, bk='e1g', n='E1：【共舞者】（另一位）的超击破倍率额外 +40%')]
e2 = F.eid(1321, 2); e2['eff'] = e2.get('eff', []) + [dict(y='weak', t='start', tg='enemies', wel='st:共舞者', d=3, bk='bx', n='E2：敌方目标入场时立即陷入【败谢】，被添加所有【共舞者】属性的弱点，持续 3 回合')]
e6 = F.eid(1321, 6); e6['eff'] = e6.get('eff', []) + [
    D(t='start', tg='self', m='be', v=150, bk='e6', n='E6：【共舞者】（大丽花）击破特攻 +150%'), D(t='start', tg='$ally', m='be', v=150, bk='e6', n='E6：【共舞者】（另一位）击破特攻 +150%')]

F.finish('击破第 4 批（大丽花、阮•梅【残梅绽】）', '''<li><b>2026-11-11（击破第 4 批：大丽花、阮•梅【残梅绽】）</b>：tv 71（tools/fix71.py）。<b>阮•梅【残梅绽】</b>：结界中我方攻击过的敌人，轮到它从弱点击破恢复时改成不恢复、不行动，行动延后（阮•梅击破特攻的 20% + 10%）并受到 50% 冰属性击破伤害，下一次轮到才恢复。<b>大丽花</b>：战技结界 3 回合（全队击破效率 +50%，没破韧时削韧值也转超击破）、【共舞者】60% 超击破、追加攻击 200% 超击破、终结技【败谢】添加所有【共舞者】属性的弱点、行迹又一场葬礼（只算 +50%）、E1（全队超击破、共舞者 +40%）、E2 入场【败谢】、E6 共舞者击破特攻 +150%。只在放了带韧性的敌人时有变化；阮•梅在场时破韧的敌人会多延后一次，行动顺序会跟着变。</li>''',
'''2026-11-11（击破第 4 批）：大丽花（1321）击破相关、阮•梅（1303）【残梅绽】—— tv 71（tools/fix71.py）。新：weak 的 wel "st:状态名"、模板 x.cmz。
  未改 / 存疑：【残梅绽】按“结界中我方有削韧的攻击打到的敌人”附加（忆灵 / 召唤物的攻击不算），触发的那个回合不计入敌人的回合数（持续伤害、减益回合都不动）；大丽花追加攻击只按 1 次伤害削韧，追加攻击的 200% 和【共舞者】的 60% 相加；又一场葬礼只算固定的 50%；弃旧恋新的固定削韧、E1 固定削韧、秘技没做；【共舞者】换人（另一位不在场时改成击破特攻最高的队友）没做。''')
