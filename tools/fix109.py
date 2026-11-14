"""tv 109：卡厄斯兰那的速度含义改成用户说的：基础速度 × 60% 是整个变身的速度（变身总长 = 10000 ÷ 56.4 ≈ 177.3 行动值），
8 个额外回合均分在里面（间隔 ≈ 22.2），开大后立刻第 1 个，第 8 个（最后一击）之后再过一个间隔变身结束。
召唤物模板 spb 改成“均分成几份”，新字段 tail = 最后一次行动后再等一个间隔才离场。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 109, sys.argv[2])
C, has = F.C, F.has
F.rep('''u.spbF = !!(d0 && d0.spb); }
      if (o && o !== u && !o.sm && u.spbF) return Math.max(1, num(o.base, 100) * num(u.sm.ratio) / 100);   // 速度固定为本体基础速度的 X%，不吃加速（卡厄斯兰那）''',
'''u.spbF = d0 && num(d0.spb) > 0 ? num(d0.spb) : 0; }
      if (o && o !== u && !o.sm && u.spbF) return Math.max(1, num(o.base, 100) * num(u.sm.ratio) / 100 * u.spbF);   // 本体基础速度的 X% 是整段变身的速度，额外回合均分在里面（×份数 = 每个额外回合的间隔）；不吃加速（卡厄斯兰那）''')
F.rep('''      if (actor.sm && actor.life > 0 && --actor.life <= 0) summonOff(actor);   // 持续回合用完离场''',
'''      if (actor.sm && actor.life > 0 && --actor.life <= 0) {   // 持续回合用完离场
        if ((smDef(actor) || {}).tail && !actor.tailOn) { actor.tailOn = true; actor.life = 1; }   // 最后一次行动后再等一个间隔才离场（卡厄斯兰那：变身到整段时间走完才结束）
        else { actor.tailOn = false; summonOff(actor); } }''')
F.rep('''        if (num(actor.life) === 1) { rec.smk = "-"; lab("最后一击"); }''', '''        if (actor.tailOn) { rec.smk = "-"; lab("变身结束"); }
        else if (num(actor.life) === 1) { rec.smk = "-"; lab("最后一击"); }''')
F.rep('''        if (!was && sd.rot) u.rot = num(sd.rot[0]); }''', '''        if (!was && sd.rot) u.rot = num(sd.rot[0]); if (!was) u.tailOn = false; }''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
c = C[1408]; m = c['sm'][0]; assert m['k'] == 'khaslana' and m['life'] == 8; m.update(spb=8, tail=1)
E = c['eff']; x = find(E, '终结技：变身，卡厄斯兰那 8 个额外回合'); o1 = x['n']
x['n'] = '终结技：变身，整段变身的速度 = 白厄基础速度 × 60%（1 魂 66%；基础速度含专武加的），8 个额外回合均分在里面，开大后立刻第 1 个；其他队友离场'
c['notes'] = (c.get('notes') or []) + ['卡厄斯兰那卡片上显示的速度 = 基础速度 × 60% × 8（每个额外回合的间隔用），不是游戏里的面板速度；第 8 个额外回合（最后一击）之后还有一行“变身结束”，队友从那时起回场']
F.rebuild(1408, E, rename={o1: x['n']}, notes=c['notes'])
F.finish('卡厄斯兰那额外回合均分', '''<li><b>2026-11-14</b>：tv 109（tools/fix109.py）。卡厄斯兰那改成：白厄基础速度 × 60% 是整段变身的速度（基础速度含专武加的，1 魂比例 66%，都会跟着变），8 个额外回合均分在里面，开大后立刻第 1 个；最后一击之后再过一个间隔变身结束、队友回场。</li>''',
'''2026-11-14：卡厄斯兰那额外回合均分 —— tv 109（tools/fix109.py）。用户说明：60% 基础速度是整个大招的速度，8 个额外回合插在大招里面，均分、开大后立刻第 1 个。
  未改 / 存疑：2 魂的额外回合、昔涟刷新的额外回合会让变身变长（每多 1 个回合多一个间隔）''')
