"""伤害增益第 10 批（1.x 物理 / 冰 / 量子……）：卢卡、玲可、虎克、克拉拉、佩拉、希露瓦、希儿（强化版）、布洛妮娅。桑博（持续伤害易伤）、娜塔莎、杰帕德没有能算进来的伤害增益。"""
import sys; sys.path.insert(0, 'tools')
from dmgbatch import run, D
BASE = {
 1111: [D(t='ult', tg='enemies', m='vuln', v=20, lv=[5, 21.6], d=3, bk='ult', n='终结技：目标受到的伤害 +20%，持续 3 回合')],
 1109: [],
 1106: [
  D(t='ult', tg='enemies', m='defRed', v=40, lv=[5, 42], d=2, bk='tj', n='终结技：【通解】敌方防御力 −40%，持续 2 回合'),
  D(t='start', tg='self', m='dmg', v=20, d=0, bk='tj2', n='行迹痛击：对处于负面效果的敌人伤害 +20%（按一直有负面算）'),
  D(t='start', tg='enemies', m='defRed', v=20, d=2, bk='tech', off=1, n='秘技：进入战斗后敌方防御力 −20%，持续 2 回合（用了秘技再启用）'),
 ],
 1103: [D(t='kill', tg='self', m='atkP', v=20, d=2, bk='kr', n='行迹狂热：消灭敌人后攻击力 +20%，持续 2 回合')],
 1102: [
  D(t='kill', tg='self', m='dmg', v=80, lv=[3, 88], d=3, bk='zf', n='【强化版】天赋：消灭敌人进入增幅状态，伤害 +80%，持续 3 回合'),
  D(t='kill', tg='self', m='resPen', v=25, d=3, bk='gl', n='【强化版】行迹割裂：增幅状态下量子属性抗性穿透 +25%'),
  D(t='kill', tg='self', m='dmg', v=50, st=3, d=3, bk='yx', n='行迹夜行：消灭敌人时伤害 +50%，最多 3 层，持续 3 回合'),
  D(t='start', tg='self', m='dmg', v=80, lv=[3, 88], d=3, bk='zf', off=1, n='【强化版】秘技：用了秘技进入战斗时立即进入增幅状态（用了秘技再启用）'),
  D(t='start', tg='self', m='resPen', v=25, d=3, bk='gl', off=1, n='【强化版】秘技：同上，割裂穿透'),
 ],
 1101: [
  D(t='skill', tg='$ally', m='dmg', v=66, lv=[5, 72.6], d=1, bk='sk', n='战技：目标造成的伤害 +66%，持续 1 回合'),
  D(t='ult', tg='team', m='atkP', v=55, lv=[3, 59.4], d=2, bk='ulta', n='终结技：我方全体攻击力 +55%，持续 2 回合'),
  D(t='ult', tg='team', m='cd', ss='cd', v=16, hf=20, lv=[3, 16.8], d=2, bk='ultc', n='终结技：我方全体暴击伤害 +布洛妮娅暴伤的 16% + 20%（按卡片面板暴伤；3 魂固定部分 21.6% 没升）'),
  D(t='start', tg='team', m='dmg', v=10, d=0, bk='js', n='行迹军势：我方全体伤害 +10%'),
  D(t='start', tg='team', m='atkP', v=15, d=2, bk='tech', off=1, n='秘技：下一次战斗开始时我方全体攻击力 +15%，持续 2 回合（用了秘技再启用）'),
 ],
}
del BASE[1109]
EID = {
 1111: {1: [D(t='start', tg='self', m='dmg', v=15, d=0, bk='e1', n='E1：目标处于裂伤时伤害 +15%（按一直裂伤算）')],
        4: [D(t='skill', tg='self', m='atkP', v=5, st=4, d=0, bk='e4', n='E4：每获得 1 层【斗志】攻击力 +5%，最多 4 层'),
            D(t='ult', tg='self', m='atkP', v=5, st=4, d=0, bk='e4', n='E4：终结技获得 2 层斗志（第 1 层）'),
            D(t='ult', tg='self', m='atkP', v=5, st=4, d=0, bk='e4', n='E4：终结技获得 2 层斗志（第 2 层）')]},
 1110: {4: [D(t='skill', tg='$ally', m='atkF', ss='hp', v=3, d=1, bk='e4', n='E4：获得【求生反应】时攻击力 +玲可生命上限的 3%，持续 1 回合')]},
 1109: {1: [D(t='start', tg='self', m='dmg', v=20, sc='s', d=0, bk='e1', n='E1：强化战技伤害 +20%（按战技算）')],
        6: [D(t='start', tg='self', m='dmg', v=20, d=0, bk='e6', n='E6：对灼烧的敌人伤害 +20%（按一直灼烧算）')]},
 1107: {2: [D(t='ult', tg='self', m='atkP', v=30, d=2, bk='e2', n='E2：施放终结技后攻击力 +30%，持续 2 回合（强化反击的倍率提高没算）')]},
 1106: {4: [D(t='skill', tg='enemies', m='resRed', v=12, d=2, bk='e4', n='E4：施放战技时敌人冰属性抗性 −12%，持续 2 回合（只该算冰属性角色）')]},
 1103: {6: [D(t='start', tg='self', m='dmg', v=30, d=0, bk='e6', n='E6：对触电的敌人伤害 +30%（按一直触电算）')]},
 1102: {1: [D(t='start', tg='self', m='cr', v=15, d=0, bk='e1', off=1, n='E1：对生命值 ≤80% 的敌人暴击率 +15%（需要时启用）')]},
}
run(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 30, BASE, EID, {}, {}, '伤害增益第 10 批')
