"""伤害增益第 11 批（最早一批角色 + Fate 联动）：Archer、Saber、黑塔、艾丝妲、阿兰、银狼（强化版）、卡芙卡、瓦尔特（强化版）、姬子、丹恒。三月七 4 魂是按防御力加的固定伤害，没加。"""
import sys; sys.path.insert(0, 'tools')
from dmgbatch import run, D
BASE = {
 1015: [
  D(t='skill', tg='self', m='dmg', v=100, sc='s', st=2, d=1, bk='hl', n='战技：【回路连接】中施放战技后战技伤害 +100%，最多 2 层（行动记录在战技之后才记，所以这次战技就会吃到新的一层，偏高）'),
  D(t='start', tg='self', m='cd', v=120, d=0, bk='shz', off=1, n='行迹守护者：我方获得战技点后若战技点 ≥4，暴击伤害 +120%，持续 1 回合（战技点多时启用）'),
 ],
 1014: [
  D(t='aUlt', aw='all', tg='self', m='dmg', v=60, lv=[5, 66], d=2, bk='lx', n='天赋：我方任意目标施放终结技时 Saber 伤害 +60%，持续 2 回合'),
  D(t='start', tg='self', m='cr', v=20, d=0, bk='lq', n='行迹龙之骑士：暴击率 +20%'),
  D(t='skill', tg='self', m='cd', v=50, d=2, bk='xg', n='行迹星之冠冕：施放战技时暴击伤害 +50%，持续 2 回合'),
  D(t='start', tg='self', m='cd', v=32, d=0, bk='xg2', n='行迹星之冠冕：每获得 1 点炉心共鸣暴伤 +4%，最多 8 层（按已叠满算）'),
  D(t='start', tg='self', m='atkP', v=35, d=2, bk='tech', off=1, n='秘技：下一次战斗开始时攻击力 +35%，持续 2 回合（用了秘技再启用）'),
 ],
 1013: [
  D(t='start', tg='self', m='dmg', v=45, sc='s', d=0, bk='xl', n='战技：对生命值 ≥50% 的敌人伤害 +20%（行迹效率再 +25%；按敌人一直 ≥50% 算）'),
  D(t='start', tg='self', m='dmg', v=20, sc='u', d=0, bk='bj', off=1, n='行迹冰结：终结技对冻结的敌人伤害 +20%（打冻结敌人时启用）'),
  D(t='start', tg='self', m='atkP', v=40, d=3, bk='tech', off=1, n='秘技：下一次战斗开始时攻击力 +40%，持续 3 回合（用了秘技再启用）'),
 ],
 1009: [
  D(t='atk', aw='self', tg='team', m='atkP', v=14, lv=[3, 15.4], st=5, d=0, bk='xn', n='天赋：每层蓄能我方全体攻击力 +14%，最多 5 层（按每次攻击 1 层，第 2 回合起每回合 −3 层没算）'),
  D(t='start', tg='team', m='dmg', v=18, d=0, bk='dr', off=1, n='行迹点燃：我方全体火属性伤害 +18%（只对火属性角色启用）'),
 ],
 1008: [D(t='start', tg='self', m='dmg', v=72, lv=[5, 79.2], d=0, bk='zt', off=1, n='天赋：按损失的生命值百分比增伤，最多 +72%（残血时启用）')],
 1006: [
  D(t='skill', tg='enemies', m='resRed', v=13, lv=[3, 13.5], d=2, bk='sk', n='【强化版】战技：目标全属性抗性 −13%，持续 2 回合'),
  D(t='skill', tg='enemies', m='resRed', v=20, d=3, bk='skw', n='【强化版】战技：添加的弱点对应属性抗性 −20%，持续 3 回合（优先编队第一位角色的属性）'),
  D(t='ult', tg='enemies', m='defRed', v=45, lv=[5, 46.8], d=3, bk='ult', n='【强化版】终结技：敌方全体防御力 −45%，持续 3 回合'),
  D(t='atk', aw='self', tg='enemies', m='defRed', v=12, lv=[3, 13.2], d=3, bk='qx', n='【强化版】天赋：【缺陷】防御力 −12%，持续 3 回合（随机 3 种，按挂上防御缺陷算）'),
  D(t='skill', tg='enemies', m='resRed', v=3, d=2, bk='pz', n='行迹旁注：目标负面效果 ≥3 个时战技减抗额外 3%'),
 ],
 1005: [D(t='start', tg='team', m='atkP', v=100, d=0, bk='zm', off=1, n='行迹折磨：效果命中 ≥75% 的我方目标攻击力 +100%（只对满足的角色启用）')],
 1004: [
  D(t='ult', tg='enemies', m='defRed', v=40, d=2, bk='sz', n='【强化版】天赋：【失重】敌人防御力 −40%（按终结技后 2 回合近似）'),
  D(t='atk', aw='all', tg='team', m='dmg', v=10, st=10, d=2, bk='cj', n='【强化版】行迹惩戒：我方攻击【失重】目标时伤害 +10%，最多 10 层，持续 2 回合（按每次攻击 1 层，没判断失重）'),
  D(t='start', tg='self', m='atkP', v=80, d=0, bk='cp', off=1, n='【强化版】行迹裁决：效果命中超过 40% 时每 10% 攻击力 +20%，最多 80%（没有效果命中数值，效果命中 ≥80% 时启用）'),
 ],
 1003: [
  D(t='start', tg='self', m='cr', v=15, d=0, bk='db', n='行迹道标：生命值 ≥80% 时暴击率 +15%（按一直满足算）'),
  D(t='start', tg='self', m='dmg', v=20, sc='s', d=0, bk='zr', off=1, n='行迹灼热：战技对灼烧的敌人伤害 +20%（敌人灼烧时启用）'),
 ],
 1002: [
  D(t='start', tg='self', m='resPen', v=36, lv=[5, 39.6], d=0, bk='cc', off=1, n='天赋：成为我方技能目标时下一次攻击风属性抗性穿透 +36%（2 回合冷却，需要时启用）'),
  D(t='start', tg='self', m='dmg', v=40, sc='b', d=0, bk='gf', off=1, n='行迹罡风：普攻对减速的敌人伤害 +40%（需要时启用）'),
  D(t='start', tg='self', m='atkP', v=40, d=3, bk='tech', off=1, n='秘技：下一次战斗开始时攻击力 +40%，持续 3 回合（用了秘技再启用）'),
 ],
}
EID = {
 1015: {2: [D(t='ult', tg='enemies', m='resRed', v=20, d=2, bk='e2', n='E2：施放终结技时敌人量子属性抗性 −20%，持续 2 回合')],
        4: [D(t='start', tg='self', m='dmg', v=150, sc='u', d=0, bk='e4', n='E4：终结技伤害 +150%')],
        6: [D(t='start', tg='self', m='defIg', v=20, sc='s', d=0, bk='e6', n='E6：战技无视 20% 防御力（战技增伤上限 +1 层没算）')]},
 1014: {1: [D(t='start', tg='self', m='dmg', v=60, sc='u', d=0, bk='e1', n='E1：终结技伤害 +60%')],
        2: [D(t='start', tg='self', m='defIg', v=15, d=0, bk='e2', n='E2：每获得 1 点炉心共鸣无视 1% 防御力，最多 15 层（按已叠满算）')],
        4: [D(t='start', tg='self', m='resPen', v=8, d=0, bk='e4', n='E4：风属性抗性穿透 +8%'),
            D(t='ult', tg='self', m='resPen', v=4, st=3, d=0, bk='e4u', n='E4：施放终结技后风属性抗性穿透 +4%，最多 3 层')],
        6: [D(t='start', tg='self', m='resPen', v=20, sc='u', d=0, bk='e6', n='E6：终结技伤害风属性抗性穿透 +20%')]},
 1013: {2: [D(t='fua', tg='self', m='cr', v=3, st=5, d=0, bk='e2', n='E2：天赋每触发 1 次暴击率 +3%，最多 5 层')],
        4: [D(t='start', tg='self', m='dmg', v=10, sc='f', d=0, bk='e4', n='E4：天赋追加攻击伤害 +10%')],
        6: [D(t='ult', tg='self', m='atkP', v=25, d=1, bk='e6', n='E6：施放终结技后攻击力 +25%，持续 1 回合')]},
 1008: {1: [D(t='start', tg='self', m='dmg', v=10, sc='s', d=0, bk='e1', off=1, n='E1：生命值 ≤50% 时战技伤害 +10%（残血时启用）')],
        6: [D(t='start', tg='self', m='dmg', v=20, sc='u', d=0, bk='e6', off=1, n='E6：生命值 ≤50% 时终结技伤害 +20%（残血时启用）')]},
 1006: {6: [D(t='start', tg='self', m='dmg', v=100, d=0, bk='e6', n='E6：敌人每有 1 个负面效果伤害 +20%，最多 100%（按 5 个负面算）')]},
 1003: {2: [D(t='start', tg='self', m='dmg', v=15, d=0, bk='e2', off=1, n='E2：对生命值 ≤50% 的敌人伤害 +15%（需要时启用）')]},
 1002: {1: [D(t='start', tg='self', m='cr', v=12, d=0, bk='e1', n='E1：击中生命值 ≥50% 的敌人时暴击率 +12%（按敌人一直 ≥50% 算）')]},
}
run(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 31, BASE, EID, {}, {}, '伤害增益第 11 批')
