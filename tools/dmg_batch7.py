"""伤害增益第 7 批：花火（强化版）、真理医生、砂金、阮•梅、银枝、忘归人、三月七（虚数）、貊泽、灵砂；黑天鹅补强化版烛影朕兆。"""
import sys, re, json; sys.path.insert(0, 'tools')
from dmgbatch import run, D
P = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
BASE = {
 1306: [
  D(t='skill', tg='$ally', m='cd', ss='cd', v=24, hf=45, lv=[3, 26.4], d=2, bk='mys', n='【强化版】战技：目标暴击伤害 +花火暴击伤害的 24% + 45%，持续 2 回合（按卡片面板暴伤；3 魂固定部分 48.6% 没升）'),
  D(t='aSk', aw='all', tg='enemies', m='vuln', v=4, lv=[5, 4.4], st=3, d=2, bk='hx', n='【强化版】天赋：我方每消耗战技点花火获得 1 层【幻相】，敌方全体受到的伤害 +4%，最多 3 层，持续 2 回合（按“施放战技”算 1 点）'),
  D(t='ult', tg='enemies', m='vuln', v=18, lv=[5, 19.44], d=3, bk='mg', n='【强化版】终结技：【谜诡】期间幻相每层额外 +6%（按 3 层算 +18%），持续 3 回合'),
  D(t='start', tg='team', m='atkP', v=45, d=0, bk='yxq', n='【强化版】行迹夜想曲：我方全体攻击力 +45%'),
  D(t='skill', tg='$ally', m='resPen', v=10, d=2, bk='yxp', n='【强化版】行迹夜想曲：持有战技暴伤增益的角色全属性抗性穿透 +10%'),
 ],
 1305: [
  D(t='skill', tg='self', m='cr', v=7.5, d=0, bk='gn', n='行迹归纳：战技时目标每有 1 个负面效果暴击率 +2.5%、暴伤 +5%，最多 6 层（按 3 个负面算）'),
  D(t='skill', tg='self', m='cd', v=15, d=0, bk='gnc', n='行迹归纳：暴击伤害部分（按 3 个负面算）'),
  D(t='start', tg='self', m='dmg', v=30, d=0, bk='tl', n='行迹推理：目标负面效果 ≥3 个时每个伤害 +10%，最多 50%（按 3 个算）'),
 ],
 1304: [
  D(t='ult', tg='team', m='cd', v=15, lv=[3, 16.2], d=3, bk='jh', n='终结技：我方击中【惊惶】的敌人时暴击伤害 +15%，持续 3 回合'),
  D(t='start', tg='self', m='cr', ss='def', v=0.02, hf=-32, cap=48, d=0, bk='gg', n='行迹杠杆：防御力超过 1600 时每 100 点暴击率 +2%，最多 +48%（按卡片面板防御力，线性近似）'),
 ],
 1303: [
  D(t='skill', tg='team', m='dmg', v=32, lv=[5, 35.2], d=3, bk='xwy', n='战技：【弦外音】期间我方全体伤害 +32%，持续 3 回合'),
  D(t='skill', tg='team', m='dmg', v=36, d=3, bk='lz', off=1, n='行迹落烛照水燃：击破特攻超过 120% 时弦外音增伤额外提高，最多 +36%（没有击破特攻数值，按满额写；击破特攻 ≥180% 时启用）'),
  D(t='ult', tg='team', m='resPen', v=25, lv=[3, 27], d=2, bk='jj', n='终结技：结界期间我方全体全属性抗性穿透 +25%，持续 2 回合'),
 ],
 1302: [
  D(t='atk', aw='self', tg='self', m='cr', v=2.5, lv=[3, 2.8], st=10, d=0, bk='sg', n='天赋：每击中 1 个敌人获得 1 层【升格】，暴击率 +2.5%，最多 10 层（按每次攻击 1 层）'),
  D(t='start', tg='self', m='dmg', v=15, d=0, bk='yq', off=1, n='行迹勇气：对生命值 ≤50% 的敌人伤害 +15%（需要时启用）'),
 ],
 1225: [D(t='skill', tg='enemies', m='defRed', v=18, lv=[3, 20], d=3, bk='zz', n='战技：【炽灼】期间【狐祈】目标攻击时敌人防御力 −18%（按战技后 3 回合近似）')],
 1224: [
  D(t='start', tg='self', m='dmg', v=80, lv=[5, 88], sc='eb', d=0, bk='tf', n='天赋：充能满 7 点立即行动时伤害 +80%（只算强化普攻）'),
  D(t='ebasic', tg='$ally', m='cd', v=60, d=2, bk='wb', n='行迹斡波：施放强化普攻后【师父】暴击伤害 +60%，持续 2 回合（师父 = 模板里的第一个队友）'),
 ],
 1223: [
  D(t='start', tg='enemies', m='vuln', v=25, sc='f', d=0, bk='bz', n='行迹不折镆干：【猎物】受到的追加攻击伤害 +25%（按一直有猎物算）'),
  D(t='start', tg='self', m='dmg', v=30, d=2, bk='tech', off=1, n='秘技：隐身状态下攻击进入战斗时伤害 +30%，持续 2 回合（用了秘技再启用）'),
 ],
 1222: [D(t='start', tg='self', m='atkP', v=50, d=0, bk='zl', off=1, n='行迹朱燎：攻击力 +击破特攻的 25%，最多 50%（没有击破特攻数值，按满额写；击破特攻 ≥200% 时启用）')],
 1307: [D(t='start', tg='team', m='dmg', v=72, d=0, bk='zyt', off=1, n='【强化版】行迹烛影朕兆：我方全体伤害 +黑天鹅效果命中的 60%，最多 72%（效果命中 ≥120% 时启用，并关掉原版那条）')],
}
EID = {
 1306: {1: [D(t='ult', tg='team', m='atkP', v=40, d=4, bk='e1', n='E1：持有【谜诡】的目标攻击力 +40%（谜诡持续时间 +1 回合）')],
        2: [D(t='aSk', aw='all', tg='team', m='defIg', v=8, st=3, d=2, bk='e2', n='E2：天赋每层额外使我方无视目标 8% 防御力')],
        6: [D(t='skill', tg='$ally', m='cd', ss='cd', v=30, d=2, bk='e6', n='E6：战技暴伤增益额外 +花火暴击伤害的 30%（扩散给谜诡队友没算）')]},
 1305: {6: [D(t='start', tg='self', m='dmg', v=50, sc='f', d=0, bk='e6', n='E6：天赋追加攻击伤害 +50%')]},
 1304: {1: [D(t='start', tg='team', m='cd', v=20, d=0, bk='e1', n='E1：持有【坚垣筹码】的目标暴击伤害 +20%（按一直有护盾算）')],
        2: [D(t='basic', tg='enemies', m='resRed', v=12, d=3, bk='e2', n='E2：施放普攻时目标全属性抗性 −12%，持续 3 回合')],
        6: [D(t='start', tg='self', m='dmg', v=150, d=0, bk='e6', n='E6：每有 1 个队友持有护盾伤害 +50%，最多 150%（按 3 个队友都有护盾算）')]},
 1303: {1: [D(t='ult', tg='team', m='defIg', v=20, d=2, bk='e1', n='E1：结界期间我方全体无视目标 20% 防御力')],
        2: [D(t='start', tg='team', m='atkP', v=40, d=0, bk='e2', off=1, n='E2：对弱点击破状态的敌人攻击力 +40%（打击破敌人时启用）')]},
 1302: {1: [D(t='atk', aw='self', tg='self', m='cd', v=4, st=10, d=0, bk='e1', n='E1：每层【升格】暴击伤害 +4%')],
        2: [D(t='ult', tg='self', m='atkP', v=40, d=1, bk='e2', off=1, n='E2：敌人 ≥3 个时施放终结技攻击力 +40%（敌人多时启用）')],
        6: [D(t='start', tg='self', m='defIg', v=30, sc='u', d=0, bk='e6', n='E6：终结技无视敌方 30% 防御力')]},
 1224: {6: [D(t='ult', tg='self', m='cd', v=50, sc='eb', d=3, bk='e6', n='E6：施放终结技后下一次强化普攻暴击伤害 +50%（按 3 回合近似）')]},
 1223: {2: [D(t='start', tg='team', m='cd', v=40, d=0, bk='e2', n='E2：我方对【猎物】造成伤害时暴击伤害 +40%')],
        4: [D(t='ult', tg='self', m='dmg', v=30, d=2, bk='e4', n='E4：施放终结技时伤害 +30%，持续 2 回合')]},
 1222: {1: [D(t='break', tg='enemies', m='defRed', v=20, d=1, bk='e1', off=1, n='E1：敌人被击破时防御力 −20%（持续到恢复韧性，需要时启用）')],
        6: [D(t='smOn', sk='fuyuan', tg='enemies', m='resRed', v=20, d=0, bk='e6', n='E6：浮元在场时敌方全体全属性抗性 −20%'),
            D(t='smEnd', sk='fuyuan', tg='enemies', m='resRed', v=0, d=0, bk='e6', n='E6：浮元离场，减抗取消')]},
}
run(P, 27, BASE, EID, {}, {}, '伤害增益第 7 批')
# 流萤 1 魂只算强化战技（新模板用；旧配置里那条保持“战技”）
s = open(P, encoding='utf-8').read(); m = re.search(r'const DB = (\{.*?\});\n', s); DB = json.loads(m.group(1))
for c in DB['chars']:
    if c['id'] == 1310:
        for r in c['eid']:
            for x in r['eff']:
                if x.get('bk') == 'e1' and x.get('y') == 'dbuf': x['sc'] = 'es'; x['n'] = 'E1：施放强化战技时无视目标 15% 防御'
s = s[:m.start(1)] + json.dumps(DB, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]; open(P, 'w', encoding='utf-8').write(s)
