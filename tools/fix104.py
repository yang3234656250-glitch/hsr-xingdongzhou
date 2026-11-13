"""tv 104：貊泽的离场状态和【猎物】充能。
- 状态新字段 ps = 持有期间本体暂停（不跑条、不行动）；充能型状态的消耗效果 ce = 减到 0 立刻结束。
- 敌方增益新字段 lst = 目标被消灭时结束施放者身上的这个状态（猎物被消灭 → 貊泽回场）。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 104, sys.argv[2])
C, has = F.C, F.has
F.rep('''      if (x.ux) e.ux = x.ux;''', '''      if (x.ps) e.stPause = 1; if (x.ce) e.stNow = 1; if (x.lst) e.lSt = x.lst;   // 状态：持有期间本体暂停 / 充能减到 0 立刻结束；敌方增益：目标被消灭时结束施放者的这个状态
      if (x.ux) e.ux = x.ux;''')
F.rep('''        if (v < 0) { if (old) old.left = Math.max(0, old.left + v); return; }
        tg.st[k] = { left: (old ? old.left : 0) + v, tick: "chg" };''', '''        if (v < 0) { if (old) { old.left = Math.max(0, old.left + v); if (eff.stNow && old.left <= 0) endSt(tg, k); } return; }
        tg.st[k] = { left: (old ? old.left : 0) + v, tick: "chg" };
        if (eff.stPause) { tg.paused = true; tg.stP = k; }   // 持有期间本体暂停（貊泽离场）''')
F.rep('''      if (!u.st[k]) return;
      delete u.st[k];''', '''      if (!u.st[k]) return;
      delete u.st[k];
      if (u.stP === k) { u.paused = false; delete u.stP; }''')
F.rep('''        if (eff.mvD) b.mvd = 1;''', '''        if (eff.mvD) b.mvd = 1;
        if (eff.lSt && src) b.lst = [src.id, String(eff.lSt)];''')
F.rep('''      { const nx = U.find(z => z.kind === "enemy" && !z.gone), mv = (en.buffs || []).filter(b => b.mvd);''', '''      for (const b of (en.buffs || []).filter(b => b.lst)) { const o = byId[b.lst[0]]; if (o && o.st && o.st[b.lst[1]]) endSt(o, b.lst[1]); }   // 这个敌人身上挂着的状态联动（貊泽【猎物】被消灭）
      { const nx = U.find(z => z.kind === "enemy" && !z.gone), mv = (en.buffs || []).filter(b => b.mvd);''')
F.rep('''        if ((eff.type === "advance" || eff.type === "delay") && tg.gone) continue;''', '''        if ((eff.type === "advance" || eff.type === "delay") && (tg.gone || tg.paused)) continue;   // 离场 / 被暂停的单位不吃拉条推条''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('122302', '使指定敌方单体目标成为【猎物】，并对其造成等同于貊泽#1[i]%攻击力的雷属性伤害，并获得#2[i]点充能'); assert F.prm('122302', 10)[1] == 9
has('122304', '场上存在【猎物】时，貊泽会进入离场状态')
has('122304', '当充能为0时，解除目标【猎物】状态，并重置计入发动追加攻击所需的充能点数。天赋的追加攻击不会消耗充能')
F.hast(1223, '手奋匕尺', '貊泽解除离场状态时，行动提前#1[i]%。每个波次开始时，貊泽行动提前#2[i]%')
has('r:122301', '每触发1次天赋的附加伤害，貊泽恢复2点能量'); has('r:122302', '我方全体目标对成为【猎物】的敌方目标造成伤害时，暴击伤害提高40%')
c = C[1223]; E = c['eff']
adv = find(E, '行迹手奋匕尺'); o_adv = adv['n']; adv['n'] = '行迹手奋匕尺：每个波次开始时行动提前 30%'
cn = find(E, '天赋：我方攻击猎物后消耗 1 点充能'); o_cn = cn['n']
cn.pop('nf', None); cn.pop('off', None); cn['aw'] = 'others'; cn['ns'] = '猎物'; cn['n'] = '天赋：队友攻击【猎物】后消耗 1 点充能（计入发动追加攻击所需的 3 点；貊泽自己的攻击不算）'
vu = find(E, '行迹不折镆干：【猎物】受到的追加攻击伤害'); o_vu = vu['n']; vu['lst'] = '猎物'; vu['n'] = '行迹不折镆干：【猎物】受到的追加攻击伤害 +25%（战技的目标；只在最新的猎物身上，猎物被消灭时貊泽回场）'
i = E.index(cn)
E.insert(i, dict(y='state', t='skill', tg='self', sn='猎物', ts='chg', v=9, ps=1, n='战技：使目标成为【猎物】并获得 9 点充能，【猎物】存在期间貊泽离场（不跑条、不行动，可以开大）'))
i = E.index(cn) + 1
E.insert(i, dict(y='state', t='atk', aw='others', tg='self', sn='猎物', ts='chg', v=-1, ce=1, ns='猎物', n='天赋：同上，【猎物】的充能 −1，到 0 时解除【猎物】、貊泽回场'))
E += [dict(y='dbuf', t='stEnd', se='猎物', aw='self', tg='enemies', m='vuln', v=0, sc='f', d=0, bk='bz', n='天赋：【猎物】解除时，追加攻击易伤一起消失'),
      dict(y='count', t='stEnd', se='猎物', aw='self', tg='self', m='set', v=0, n='天赋：【猎物】解除时重置计入追加攻击所需的充能点数'),
      dict(y='advance', t='stEnd', se='猎物', aw='self', tg='self', v=20, n='行迹手奋匕尺：解除离场状态时行动提前 20%'),
      dict(y='dbuf', t='skill', tg='team', m='rx', sc='mz', v=1, d=0, bk='mzx', n='额外伤害标记：【猎物】存在时队友攻击后貊泽额外造成 30% 攻击力的附加伤害'),
      dict(y='dbuf', t='stEnd', se='猎物', aw='self', tg='team', m='rx', sc='mz', v=0, d=0, bk='mzx', n='额外伤害标记：【猎物】解除')]
c['notes'] = [n for n in (c.get('notes') or []) if '解除离场状态时' not in n]
F.rebuild(1223, E, rename={o_adv: adv['n'], o_cn: cn['n'], o_vu: vu['n']}, notes=c['notes'])
e1 = F.eid(1223, 1); y = find(e1['eff'], 'E1 矢志（猎物被攻击触发天赋附加伤害）'); y.pop('off', None); y.update(aw='others', ns='猎物', n='E1 矢志：每触发 1 次天赋的附加伤害（队友攻击【猎物】后）恢复 2 点能量')
e2 = F.eid(1223, 2); y = find(e2['eff'], 'E2：我方对【猎物】造成伤害时暴击伤害'); y['t'] = 'skill'; y['n'] = 'E2：【猎物】存在时我方全体暴击伤害 +40%（按对所有敌人算）'
e2['eff'].append(dict(y='dbuf', t='stEnd', se='猎物', aw='self', tg='team', m='cd', v=0, d=0, bk='e2', n='E2：【猎物】解除时暴击伤害加成消失'))
r = F.XR['1223'][0]; assert r['k'] == 'tf'; r['flag2'] = 'mz'; r['n'] = '天赋：队友攻击【猎物】后貊泽额外 30% 攻击力附加伤害（【猎物】存在时）'
F.finish('貊泽离场和猎物充能', '''<li><b>2026-11-13</b>：tv 104（tools/fix104.py）。貊泽按原文重做：战技后获得 9 点充能并离场（不跑条、不行动，仍可开大）；队友每攻击 1 次【猎物】消耗 1 点充能，每 3 点追加攻击 1 次，充能用完或【猎物】被消灭时回场并行动提前 20%；附加伤害、追加攻击易伤、1 魂回能、2 魂暴伤都只在【猎物】存在时生效。</li>''',
'''2026-11-13：貊泽离场和猎物充能 —— tv 104（tools/fix104.py）。新：状态字段 ps（持有期间暂停）、ce（充能到 0 立刻结束）、敌方增益字段 lst。
  未改 / 存疑：离场期间按“行动条停住、回场后接着跑再提前 20%”算，没有实测；离场 / 暂停中的单位不再吃别人的拉条推条（白厄变身期间的队友也一样）；貊泽自己的终结技不算消耗充能；队友的攻击都按打到【猎物】算''')
