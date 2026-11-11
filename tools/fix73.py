"""tv 73：击破第 6 批 —— 遐蝶 1407 E6（死龙无视弱点削韧）、银狼LV.999 1506 E6（禁限弱点）、姬子•启行 1510 天赋（无视弱点削韧）、
白厄 1408 终结技（境界内敌方全体始终拥有物理弱点）、长夜月 1413 E4（忆灵击破效率）。用法：python3 tools/fix73.py index.html <官方 json 目录>
引擎：weak 的 ws = 状态名（施放者有这个状态时弱点才算数）；hasWk(en, 属性) 统一判断添加的弱点。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 73, sys.argv[2])
C, has = F.C, F.has
D = lambda **k: dict(dict(y='dbuf', d=0, t='start', tg='self'), **k)
# 引擎
F.rep('''weak = !el || !m || !m.w || m.w.includes(el) || (en.wk || []).some(z => z.el === "all" || z.el.includes(el));''', '''weak = !el || !m || !m.w || m.w.includes(el) || hasWk(en, el);''')
F.rep('''if (!eff.ig && m && m.w && !m.w.includes(wl) && !(tg.wk || []).some(z => z.el === "all" || z.el.includes(wl))) continue;''', '''if (!eff.ig && m && m.w && !m.w.includes(wl) && !hasWk(tg, wl)) continue;''')
F.rep('''    const toughHit = (who, key) => {''', '''    const hasWk = (en, el) => (en.wk || []).some(z => (z.el === "all" || z.el.includes(el)) && (!z.st || (byId[z.own] && hasSt(byId[z.own], z.st))));   // 添加的弱点（ws：施放者有这个状态时才算数）
    const toughHit = (who, key) => {''')
F.rep('''tg.wk.push({ key, el: wl, left: dur > 0 ? dur : Infinity });''', '''tg.wk.push({ key, el: wl, left: dur > 0 ? dur : Infinity, st: eff.wst || "", own: own.id });''')
F.rep('''      if (x.wel) e.wel = x.wel;''', '''      if (x.wel) e.wel = x.wel; if (x.ws) e.wst = x.ws;''')
# 遐蝶 E6
has('r:140706', '死龙攻击期间可以无视弱点属性削减敌方韧性')
e6 = F.eid(1407, 6); e6['eff'] = e6.get('eff', []) + [D(m='tig', v=100, sc='m', bk='e6t', n='E6：死龙攻击期间可以无视弱点属性削减敌方韧性')]
# 银狼LV.999 E6
has('r:150606', '拥有全属性弱点并且全属性基础抗性降低至0')
e6 = F.eid(1506, 6); e6['eff'] = e6.get('eff', []) + [dict(y='weak', t='start', tg='enemies', wel='all', d=0, bk='jx', n='E6：敌方目标进入战斗时被植入【禁限弱点】，拥有全属性弱点')]
# 姬子•启行
has('151004', '攻击时可无视弱点属性削减敌方韧性')
F.rebuild(1510, list(C[1510]['eff']) + [D(m='tig', v=100, bk='zzt', n='天赋：使用助战技后姬子•启行攻击时可无视弱点属性削减敌方韧性（按已用过助战技算）')])
# 白厄
has('140803', '敌方全体始终拥有物理属性弱点'); assert any(e.get('sn') == '变身' and e.get('t') == 'smOn' for e in C[1408]['eff'])
F.rebuild(1408, list(C[1408]['eff']) + [dict(y='weak', t='smOn', sk='khaslana', tg='enemies', wel='物', d=0, ws='变身', bk='jj', n='终结技：境界内敌方全体始终拥有物理属性弱点（变身结束后消失）')])
# 长夜月 E4
has('r:141304', '我方忆灵的弱点击破效率提高25%，忆灵「长夜」的弱点击破效率额外提高25%')
e4 = F.eid(1413, 4); e4['eff'] = e4.get('eff', []) + [
    D(tg='team', m='bef', v=25, sc='m', bk='e4t', n='E4：长夜月在场时我方忆灵的弱点击破效率 +25%'), D(m='bef', v=25, sc='m', bk='e4s', n='E4：忆灵「长夜」的弱点击破效率额外 +25%')]
F.finish('击破第 6 批（遐蝶 E6、银狼LV.999 E6、姬子•启行、白厄、长夜月 E4）', '''<li><b>2026-11-11（击破第 6 批）</b>：tv 73（tools/fix73.py）。遐蝶 E6 死龙无视弱点属性削韧；银狼LV.999 E6【禁限弱点】敌方全体拥有全属性弱点；姬子•启行天赋无视弱点属性削韧（按已用过助战技）；白厄变身期间敌方全体拥有物理弱点；长夜月 E4 忆灵击破效率 +25%（长夜再 +25%）。只在放了带韧性的敌人时有变化。</li>''',
'''2026-11-11（击破第 6 批）：遐蝶（1407）E6、银狼LV.999（1506）E6、姬子•启行（1510）天赋、白厄（1408）终结技、长夜月（1413）E4 的击破相关效果 —— tv 73（tools/fix73.py）。新：weak 的 ws。
  未改 / 存疑：姬子•启行按战斗一开始就用过助战技；银狼LV.999 E6 只对开局在场的敌人；开拓者•毁灭天赋（击破后攻击力 +25%）仍是原来的写法。''')
