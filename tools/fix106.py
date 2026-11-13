"""tv 106：阿哈【欢愉负债】。队里有星神★阿哈、且开了敌人生命值时：我方每次造成伤害，敌人累积损失生命值 25% 的【欢愉负债】（上限 = 生命上限 10%；6 魂始终至少 20%），
剩余生命值不高于【欢愉负债】时敌人被消灭（效果由用户按游戏实际说明）。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 106, sys.argv[2])
C, has = F.C, F.has
F.rep('''    const hurtEnemy = (en, a, killer) => { if (!en || en.gone || !(en.ehx > 0) || !(a > 0)) return; en.ehc -= a; if (en.ehc <= 1e-6) killEnemy(en, killer); };''',
'''    const ahaU = U.find(z => z.kind === "ally" && !z.sm && tidOf(z) === "1511");   // 星神★阿哈在队：【欢愉负债】
    const hurtEnemy = (en, a, killer) => { if (!en || en.gone || !(en.ehx > 0) || !(a > 0)) return;
      const lost = Math.min(a, Math.max(0, en.ehc)); en.ehc -= a; if (en.ehc <= 1e-6) { killEnemy(en, killer); return; }
      if (ahaU) {   // 我方造成伤害时累积损失生命值 25% 的【欢愉负债】（上限 = 生命上限 10%；6 魂始终至少 20%），剩余生命值不高于它时被消灭
        en.debt = Math.min(en.ehx * 0.1, num(en.debt) + lost * 0.25); const d = num(ahaU.eid) >= 6 ? Math.max(en.ehx * 0.2, en.debt) : en.debt;
        if (en.ehc <= d) { addLog(`${en.name} 剩余生命值（${Math.round(en.ehc)}）不高于【欢愉负债】（${Math.round(d)}）`, false, ahaU.color, ahaU.id); killEnemy(en, killer); }
      } };''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('151131', '对敌方目标额外造成等同于损失的生命值#1[i]%的【欢愉负债】效果'); has('151131', '最高不超过目标生命上限的#3[i]%'); p = F.SK['151131']['params'][0]; assert p[0] == 0.25 and p[2] == 0.1
has('r:151106', '敌方目标始终拥有至少等同于该目标生命上限20%的【欢愉负债】效果')
c = C[1511]
find(c['eff'], '天赋【阿哈正传】')['n'] = '天赋【阿哈正传】：阿哈和队友造成伤害时，敌人额外获得损失生命值 25% 的【欢愉负债】（最多生命上限 10%）；敌人剩余生命值不高于【欢愉负债】时被消灭（要在敌人卡上填了生命值才算）'
F.touch(1511)
e6 = F.eid(1511, 6); find(e6['eff'], 'E6：敌方目标始终至少有生命上限 20% 的【欢愉负债】')['n'] = 'E6：敌方目标始终至少有生命上限 20% 的【欢愉负债】（已算：剩余生命值 ≤20% 时被消灭）'
F.finish('阿哈欢愉负债', '''<li><b>2026-11-13</b>：tv 106（tools/fix106.py）。阿哈【欢愉负债】：队里有星神★阿哈、敌人填了生命值时，我方每次造成伤害敌人累积损失生命值 25% 的【欢愉负债】（最多生命上限 10%，6 魂始终至少 20%），敌人剩余生命值不高于【欢愉负债】时被消灭，日志里会写出来。</li>''',
'''2026-11-13：阿哈欢愉负债 —— tv 106（tools/fix106.py）。
  未改 / 存疑：【欢愉负债】的效果（剩余生命值低于它时怪物死亡）原文没写，是用户说的；“损失的生命值”按每次伤害实际扣掉的生命值算''')
