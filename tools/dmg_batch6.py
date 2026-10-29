"""伤害增益第 6 批（2.x 后半）：大丽花、乱破、波提欧、翡翠、星期日、米沙、流萤、知更鸟、黄泉、黑天鹅。按原版技能文字（游戏里的【强化版】技能没另做）。"""
import sys; sys.path.insert(0, 'tools')
from dmgbatch import run, D
BASE = {
 1321: [D(t='ult', tg='enemies', m='defRed', v=18, lv=[3, 20], d=4, bk='bx', n='终结技：【败谢】敌方防御力 −18%，持续 4 回合')],
 1315: [
  D(t='skill', tg='enemies', m='vuln', v=30, lv=[5, 33], d=2, bk='jm', n='战技：【绝命对峙】的敌人受到波提欧攻击时伤害 +30%，持续 2 回合'),
  D(t='start', tg='self', m='cr', v=30, d=0, bk='yl1', off=1, n='行迹幽灵装填：暴击率 +击破特攻的 10%，最多 30%（没有击破特攻数值，按满额写；击破特攻 ≥300% 时启用）'),
  D(t='start', tg='self', m='cd', v=150, d=0, bk='yl2', off=1, n='行迹幽灵装填：暴击伤害 +击破特攻的 50%，最多 150%（同上）'),
 ],
 1314: [
  D(t='fua', tg='self', m='cd', v=12, lv=[3, 13.2], st=10, d=0, bk='dp', n='天赋：追加攻击时获得 5 层【当品】，每层暴击伤害 +2.4%，最多 50 层（这里每次追加攻击算 1 叠 = 5 层）'),
  D(t='fua', tg='self', m='atkP', v=2.5, st=10, d=0, bk='dpa', n='行迹绝当品：每层【当品】攻击力 +0.5%（同上）'),
 ],
 1313: [
  D(t='skill', tg='ultpick', m='dmg', v=30, lv=[5, 33], d=2, bk='sk', n='战技：目标造成的伤害 +30%，持续 2 回合（目标在“每次大招目标”里选）'),
  D(t='skill', tg='ultpick', m='dmg', v=50, lv=[5, 55], d=2, bk='sk2', off=1, n='战技：目标有召唤物时增伤额外 +50%（目标有召唤物 / 忆灵时启用）'),
  D(t='skill', tg='ultpick', m='cr', v=20, lv=[5, 22], d=3, bk='tf', n='天赋：施放战技时目标暴击率 +20%，持续 3 回合'),
  D(t='ult', tg='ultpick', m='cd', ss='cd', v=30, hf=12, lv=[3, 33.6], d=3, bk='mf', n='终结技：【蒙福者】暴击伤害 +星期日暴击伤害的 30% + 12%，持续 3 回合（按卡片面板暴伤；3 魂固定部分 12.8% 没升）'),
  D(t='start', tg='ultpick', m='dmg', v=50, d=2, bk='tech', off=1, n='秘技：首次对我方目标施放技能时目标伤害 +50%，持续 2 回合（用了秘技再启用）'),
 ],
 1312: [D(t='start', tg='self', m='cd', v=30, d=0, bk='cc', off=1, n='行迹传冲：对冻结的敌人暴击伤害 +30%（打冻结敌人时启用）')],
 1309: [
  D(t='skill', tg='team', m='dmg', v=50, lv=[3, 55], d=3, bk='sk', n='战技：我方全体造成的伤害 +50%，持续 3 回合'),
  D(t='smOn', sk='concert', tg='team', m='atkF', ss='atk', v=22.8, hf=200, lv=[3, 24.32], d=0, bk='xz', n='终结技：【协奏】期间我方全体攻击力 +知更鸟攻击力的 22.8% + 200（3 魂固定部分 230 没升）'),
  D(t='smEnd', sk='concert', tg='team', m='atkF', v=0, d=0, bk='xz', n='终结技：退出【协奏】，攻击力加成取消'),
  D(t='start', tg='team', m='cd', v=20, lv=[5, 23], d=0, bk='tf', n='天赋：我方全体暴击伤害 +20%'),
  D(t='smOn', sk='concert', tg='team', m='cd', v=25, sc='f', d=0, bk='jx', n='行迹即兴装饰：【协奏】期间我方全体追加攻击的暴击伤害 +25%'),
  D(t='smEnd', sk='concert', tg='team', m='cd', v=0, sc='f', d=0, bk='jx', n='行迹即兴装饰：退出【协奏】，取消'),
 ],
 1308: [
  D(t='ult', tg='enemies', m='resRed', v=20, lv=[5, 22], sc='u', d=1, bk='ult', n='天赋：终结技期间敌方全体全属性抗性 −20%（只算进终结技伤害）'),
  D(t='start', tg='self', m='xtra', v=15, d=0, bk='nl1', n='行迹奈落：队里有 1 名其他虚无角色时伤害为原伤害的 115%（普攻、战技、终结技）'),
  D(t='start', tg='self', m='xtra', v=45, d=0, bk='nl2', off=1, n='行迹奈落：有 2 名时改为 160%（启用这条，和上一条合起来 ×1.6）'),
  D(t='ult', tg='self', m='dmg', v=90, d=3, bk='lx', n='行迹雷心：啼泽雨斩击中有集真赤的敌人时伤害 +30%，最多 3 层，持续 3 回合（按开大直接叠满）'),
 ],
 1307: [
  D(t='skill', tg='enemies', m='defRed', v=20.8, lv=[3, 22], d=3, bk='fd', n='战技：敌人防御力 −20.8%，持续 3 回合（行迹杯底端倪：普攻、终结技也会挂上，这里只按战技）'),
  D(t='ult', tg='enemies', m='vuln', v=25, lv=[5, 27], d=2, bk='jl', n='终结技：【揭露】敌方受到的伤害 +25%，持续 2 回合（原版只在敌方自己回合内生效）'),
  D(t='start', tg='self', m='dmg', v=72, d=0, bk='zy', off=1, n='行迹烛影朕兆：伤害 +效果命中的 60%，最多 72%（没有效果命中数值，按满额写；效果命中 ≥120% 时启用）'),
 ],
}
EID = {
 1321: {2: [D(t='start', tg='enemies', m='resRed', v=20, d=0, bk='e2', n='E2：敌方全体全属性抗性 −20%')],
        4: [D(t='fua', tg='enemies', m='vuln', v=12, d=2, bk='e4', n='E4：天赋追加攻击时敌方全体受到的伤害 +12%，持续 2 回合')]},
 1317: {1: [D(t='ult', tg='self', m='defIg', v=15, d=2, bk='e1', n='E1：【结印】期间无视目标 15% 防御（按 2 回合近似）')]},
 1315: {1: [D(t='start', tg='self', m='defIg', v=16, d=0, bk='e1', n='E1：波提欧造成伤害时无视敌方 16% 防御力')],
        4: [D(t='skill', tg='enemies', m='vuln', v=12, d=2, bk='e4', n='E4：【绝命对峙】的敌人受到波提欧攻击时伤害额外 +12%')]},
 1314: {1: [D(t='start', tg='self', m='dmg', v=32, sc='f', d=0, bk='e1', n='E1：天赋追加攻击伤害 +32%')],
        2: [D(t='fua', tg='self', m='cr', v=18, d=0, bk='e2', n='E2：【当品】叠到 15 层时暴击率 +18%（这里第 1 次追加攻击就算）')],
        4: [D(t='ult', tg='self', m='defIg', v=12, d=3, bk='e4', n='E4：施放终结技时无视敌方 12% 防御力，持续 3 回合')],
        6: [D(t='start', tg='self', m='resPen', v=20, d=0, bk='e6', n='E6：有【收债人】时量子属性抗性穿透 +20%')]},
 1313: {1: [D(t='skill', tg='ultpick', m='defIg', v=16, d=2, bk='e1', n='E1：战技目标无视敌方 16% 防御力，持续 2 回合（召唤物 40% 没算）')],
        2: [D(t='ult', tg='ultpick', m='dmg', v=30, d=3, bk='e2', n='E2：【蒙福者】造成的伤害 +30%')]},
 1312: {2: [D(t='ult', tg='enemies', m='defRed', v=16, d=3, bk='e2', off=1, n='E2：终结技每段攻击前 24% 基础概率使目标防御力 −16%，持续 3 回合（概率效果，需要时启用）')],
        6: [D(t='ult', tg='self', m='dmg', v=30, d=1, bk='e6', n='E6：施放终结技时伤害 +30%，持续到自身回合结束')]},
 1310: {1: [D(t='start', tg='self', m='defIg', v=15, sc='s', d=0, bk='e1', n='E1：强化战技无视目标 15% 防御')],
        6: [D(t='smOn', sk='burn', tg='self', m='resPen', v=20, d=0, bk='e6', n='E6：「完全燃烧」期间火属性抗性穿透 +20%'),
            D(t='smEnd', sk='burn', tg='self', m='resPen', v=0, d=0, bk='e6', n='E6：「完全燃烧」结束，穿透取消')]},
 1309: {1: [D(t='smOn', sk='concert', tg='team', m='resPen', v=24, d=0, bk='e1', n='E1：【协奏】期间我方全体全属性抗性穿透 +24%'),
            D(t='smEnd', sk='concert', tg='team', m='resPen', v=0, d=0, bk='e1', n='E1：退出【协奏】，穿透取消')]},
 1308: {1: [D(t='start', tg='self', m='cr', v=18, d=0, bk='e1', n='E1：对处于负面效果的敌人暴击率 +18%（按一直有负面算）')],
        4: [D(t='start', tg='enemies', m='vuln', v=8, sc='u', d=0, bk='e4', n='E4：敌人受到的终结技伤害 +8%')],
        6: [D(t='start', tg='self', m='resPen', v=20, sc='u', d=0, bk='e6', n='E6：终结技伤害全属性抗性穿透 +20%（普攻、战技视为终结技伤害没算）')]},
 1307: {1: [D(t='start', tg='enemies', m='resRed', v=25, d=0, bk='e1', n='E1：风化 / 裂伤 / 灼烧 / 触电的敌人对应属性抗性 −25%（按一直有对应持续伤害算）')]},
}
run(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 26, BASE, EID, {}, {}, '伤害增益第 6 批（2.x 后半）')
