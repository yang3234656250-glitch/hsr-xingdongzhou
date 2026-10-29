"""伤害增益第 4 批：开拓者（毁灭 / 存护 / 同谐 / 记忆）。同谐主是超击破 / 击破特攻，伤害估算不算击破伤害，没加。"""
import sys; sys.path.insert(0, 'tools')
from dmgbatch import run, D
DES = lambda: [
  D(t='break', tg='self', m='atkP', v=20, lv=[3, 22], st=2, d=0, bk='qz', n='天赋牵制盗垒：每次击破弱点攻击力 +20%，最多 2 层'),
  D(t='start', tg='self', m='dmg', v=25, sc='s', d=0, bk='dz', n='行迹斗志：战技对指定敌方目标的伤害 +25%'),
  D(t='start', tg='self', m='dmg', v=25, sc='u', d=0, bk='dzu', n='行迹斗志：终结技全胜•安息全垒打对指定敌方目标的伤害 +25%（另一种终结技没有这个加成）'),
]
PRE = lambda: [D(t='turn', tg='self', m='atkP', v=15, d=1, bk='xss', off=1, n='行迹行胜思：回合开始时持有护盾则攻击力 +15%，持续到行动结束（有护盾时启用）')]
MEM = lambda: [
  D(t='smOn', sk='mimi', tg='team', m='cd', ss='cd', v=12, lv=[3, 13.2], hf=24, d=0, bk='mimi', n='忆灵天赋：迷迷在场时我方全体暴击伤害 +迷迷暴击伤害的 12% + 24%（按开拓者面板暴伤算；3 魂只按 13.2% 算，固定部分没升）'),
  D(t='smEnd', sk='mimi', tg='team', m='cd', v=0, d=0, bk='mimi', n='忆灵天赋：迷迷离场，暴伤加成取消'),
]
BASE = {8002: DES(), 8001: DES(), 8004: PRE(), 8003: PRE(), 8008: MEM(), 8007: MEM()}
DE = lambda: {4: [D(t='start', tg='self', m='cr', v=25, d=0, bk='e4', off=1, n='E4：击中弱点击破状态的敌人时暴击率 +25%（打破韧性的敌人时启用）')]}
PE = lambda: {6: [D(t='ebasic', o='ult', tg='self', m='defP', v=10, st=3, d=0, bk='e6', n='E6：施放强化普攻或终结技后防御力 +10%，最多 3 层')]}
ME = lambda: {1: [D(t='start', tg='ultpick', m='cr', v=10, d=0, bk='e1', off=1, n='E1：持有【迷迷的声援】的目标暴击率 +10%（目标在“每次大招目标”里选；需要时启用）')],
              6: [D(t='start', tg='self', m='cr', v=100, sc='u', d=0, bk='e6', n='E6：终结技暴击率固定为 100%')]}
EID = {8002: DE(), 8001: DE(), 8004: PE(), 8003: PE(), 8008: ME(), 8007: ME()}
run(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 24, BASE, EID, {}, {}, '伤害增益第 4 批（开拓者）')
