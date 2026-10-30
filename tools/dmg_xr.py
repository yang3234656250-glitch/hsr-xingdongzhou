"""额外伤害的标记（rx）+ 复查时补上的几条伤害增益。tv 37。"""
import sys; sys.path.insert(0, 'tools')
from dmgbatch import run, D
F = lambda **k: D(m='rx', v=1, **k)
BASE = {
 1202: [F(t='skill', tg='$ally', sc='ty1', d=3, bk='rx', n='额外伤害标记：【赐福】持有者（持续 3 回合，持有者 = 模板里的第一个队友）'),
        D(t='start', tg='self', m='dmg', v=40, sc='b', d=0, bk='zr', n='行迹止厄：普攻伤害 +40%')],
 1309: [F(t='smOn', sk='concert', tg='team', sc='rob', d=0, bk='rx', n='额外伤害标记：【协奏】期间我方攻击后知更鸟追加附加伤害'),
        D(t='smEnd', sk='concert', tg='team', m='rx', v=0, sc='rob', d=0, bk='rx', n='额外伤害标记：退出【协奏】')],
 1403: [F(t='ult', tg='team', sc='trb', d=2, bk='rx', n='额外伤害标记：结界期间（2 回合）我方攻击后缇宝附加伤害')],
 1412: [F(t='start', tg='$ally', sc='cer', d=0, bk='rx', n='额外伤害标记：【军功】持有者（模板里的第一个队友）')],
 1503: [F(t='aha', tg='team', sc='prl', d=1, bk='rx', n='额外伤害标记：欢愉技后我方下一次攻击的欢愉附加段（按到真珠下回合）')],
 8007: [F(t='cnt', tg='$ally', sc='mimi', d=3, bk='rx', n='额外伤害标记：【迷迷的声援】持有者（3 回合，持有者 = 模板里的第一个队友）')],
 8008: [F(t='cnt', tg='$ally', sc='mimi', d=3, bk='rx', n='额外伤害标记：【迷迷的声援】持有者（3 回合，持有者 = 模板里的第一个队友）')],
 1107: [D(t='start', tg='self', m='dmg', v=30, sc='f', d=0, bk='fc', n='行迹复仇：史瓦罗的反击伤害 +30%')],
 1214: [D(t='start', tg='self', m='dmg', v=10, sc='u', d=0, bk='cf', off=1, n='行迹摧锋轴承：敌人韧性 ≥50% 时终结技伤害 +10%（需要时启用）')],
 1401: [D(t='start', tg='self', m='xtra', v=49.5, sc='u', d=0, bk='md', n='行迹饥饿的地景：每层【谜底】终结技倍率 +1%，最多 99 层（按叠满，200% → 299%）')],
}
EID = {
 1412: {4: [D(t='start', tg='self', m='xtra', v=100, sc='u', d=0, bk='e4', n='E4：终结技倍率 +240%（240% → 480%）')]},
 1312: {4: [D(t='start', tg='self', m='xtra', v=10, sc='u', d=0, bk='e4x', n='E4：终结技每段倍率 +6%（每段 60% → 66%）')]},
 1508: {4: [D(t='skill', o='ult', tg='self', m='cd', v=70, lv=[5, 77], d=2, bk='e4b', n='E4：宝石魔术的暴伤对远坂凛可叠 2 层（第 2 层）')]},
 1507: {6: [D(t='start', tg='self', m='xtra', v=50, sc='u', d=0, bk='e6x', n='E6：【千冶铸一，万劫烬灭】伤害倍率为原倍率的 150%')]},
}
run(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 37, BASE, EID, {}, {}, '额外伤害标记 + 复查补漏')
