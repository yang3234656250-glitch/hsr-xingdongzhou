"""tv 92：姬子•启行——使用 / 发动助战技视为施放了战技（触发光锥、遗器的“施放战技时”）；天赋的抗性穿透、暴伤、无视弱点削韧从第一次助战技起才有；6 魂源能额外伤害。
用法：python3 tools/fix92.py index.html <官方 json 目录>"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 92, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
F.rep('''      if (freeWhy) { toughHit(H, zk); return; }''', '''      for (const e of fx(H, "skill")) if (e.eq && /^(光锥|\\d ?件)/.test(e.note || "")) apply(e, H, H.color);   // 天赋：使用助战技视为姬子•启行施放了战技（只触发光锥 / 遗器的“施放战技时”，不重复战技本身的效果）
      if (freeWhy) { toughHit(H, zk); teamFire("aSup", H, e => e.supX); return; }''')
F.rep('''      if (x.lsc) e.lsCut = x.lsc;''', '''      if (x.spx) e.supX = 1;   // 额外发动的助战技也触发
      if (x.lsc) e.lsCut = x.lsc;''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('151004', '使用助战技视为姬子•启行施放了战技，姬子•启行获得全属性抗性穿透提高#2[i]%、暴击伤害提高#1[i]%，攻击时可无视弱点属性削减敌方韧性')
has('r:151006', '发动【轨道歼灭脉冲】时，若当前【源能】大于等于6点，则额外对敌方全体造成1次等同于姬子•启行160%攻击力的火属性伤害')
c = C[1510]; E = c['eff']; ren = {}
for pre, n in [('天赋：使用助战技后姬子•启行全属性抗性穿透', '天赋：使用助战技后姬子•启行全属性抗性穿透 +20%（5 魂 22%；第一次助战技起）'),
               ('天赋：使用助战技后姬子•启行暴击伤害', '天赋：使用助战技后姬子•启行暴击伤害 +80%（5 魂 88%；第一次助战技起）'),
               ('天赋：使用助战技后姬子•启行攻击时可无视弱点属性', '天赋：使用助战技后姬子•启行攻击时可无视弱点属性削减敌方韧性（第一次助战技起）')]:
    e = find(E, pre); ren[e['n']] = n; e.update(n=n, t='aSup', aw='all', spx=1)
c['notes'] = [x.replace('；【源能】和 6 魂源能的额外伤害没做', '；终结技按官方写的最多 762% / 252%（已含【源能】），6 魂的源能额外伤害按 1 次 160% 全体算') for x in c['notes']]
c['notes'].append('使用 / 发动助战技视为姬子•启行施放了战技：会触发她的光锥、遗器里“施放战技时”的效果（不重复战技本身的【领航旗语】和恢复次数）')
F.rebuild(1510, E, rename=ren)
e4 = F.eid(1510, 4)
for e in e4['eff']: e.update(t='aSup', aw='all', spx=1); e['n'] = e['n'].replace('（按已用过助战技算）', '（第一次助战技起）')
e6 = F.eid(1510, 6); find(e6['eff'], 'E6：火属性抗性穿透')['n'] = 'E6：火属性抗性穿透 +20%'
F.XR.setdefault('1510', []).append({"k": "e6y", "n": "E6：发动【轨道歼灭脉冲】时【源能】≥6 点，额外对敌方全体造成 1 次 160% 攻击力的伤害（按每次终结技 1 次算）", "on": ["u"], "st": "atk", "v": [1.6], "cnt": "N", "e": 6})
F.finish('姬子•启行助战技视为战技、6 魂源能', '''<li><b>2026-11-12（姬子•启行补完）</b>：tv 92（tools/fix92.py）。使用或发动助战技视为姬子•启行施放了战技：会触发她光锥、遗器里“施放战技时”的效果。天赋的全属性抗性穿透 +20%、暴击伤害 +80%、无视弱点削韧，原来按“一直有”，现在从第一次助战技（含额外发动的）起才生效，4 魂给队友的抗性穿透同理。6 魂：终结技补上【源能】≥6 时的 160% 全体额外伤害（按每次终结技 1 次）。</li>''',
'''2026-11-12：姬子•启行补完 —— tv 92（tools/fix92.py）。新：效果字段 spx（supX，额外发动的助战技也触发 aSup）；supCast 里触发 H 的装备类 skill 效果。
  未改 / 存疑：“视为施放战技”只触发光锥 / 遗器的效果；终结技里光束 / 脉冲怎么放由玩家选，伤害按官方的“最多”值，6 魂 160% 按 1 次''')
