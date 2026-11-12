"""tv 93：零散条件——寒鸦【承负】增伤按敌人真的有承负、克拉拉 4 魂受击后减伤、佩拉追歼只算下一次攻击。
新：伤害增益条件 ec.est = 目标（敌人）有这个状态。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 93, sys.argv[2])
C, has, hast = F.C, F.has, F.hast
F.rep('''      if (c.brk && !(toughMax(en) > 0 && en.broken)) return 0;   // 目标处于弱点击破状态''', '''      if (c.brk && !(toughMax(en) > 0 && en.broken)) return 0;   // 目标处于弱点击破状态
      if (c.est && !hasSt(en, c.est)) return 0;   // 目标有这个状态（寒鸦【承负】）''')
F.rep('''c.hpv == null && c.brk == null && c.dfr == null''', '''c.hpv == null && c.brk == null && c.est == null && c.dfr == null''')
F.rep('''    if (c.brk) L.push("目标处于弱点击破状态时");''', '''    if (c.brk) L.push("目标处于弱点击破状态时");
    if (c.est) L.push(`目标有【${c.est}】时`);''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
# 寒鸦
c = C[1215]; e = find(c['eff'], '天赋：我方对【承负】的敌人'); o = e['n']; n = '天赋：我方对【承负】的敌人施放普攻、战技、终结技时伤害 +30%'
ec = dict(e.get('ec') or {}); ec['est'] = '承负'; e.update(n=n, ec=ec); F.rebuild(1215, c['eff'], rename={o: n})
# 克拉拉 4 魂
has('r:110704', '受到攻击后，克拉拉受到的伤害降低30%，效果持续到自己的下个回合开始')
e4 = F.eid(1107, 4); e4['eff'] = [x for x in e4['eff'] if x.get('m') != 'dr' and x.get('sn') != '无惧伤痛'] + [
    dict(y='state', t='hit2', tg='self', sn='无惧伤痛', v=1, d=1, ts='start', n='E4 家人般的爱护：受到攻击后获得减伤，持续到克拉拉的下一个回合开始'),
    dict(y='dbuf', t='hit2', tg='self', m='dr', v=30, d=0, bk='st:无惧伤痛#e4', n='E4：受到攻击后受到的伤害降低 30%')]
C[1107]['notes'] = [x for x in C[1107].get('notes', []) if 'E4 受到攻击后' not in x]; F.touch(1107)
# 佩拉追歼
hast(1106, '追歼', '施放战技解除增益效果时，下一次攻击造成的伤害提高#1[i]%')
c = C[1106]; c['notes'] = [x for x in c.get('notes', []) if '追歼' not in x]
c['eff'].append(dict(y='dbuf', t='skill', tg='self', m='dmg', v=20, d=0, bk='zj', nx='a', off=1, n='行迹追歼：施放战技解除了敌人的增益效果时，下一次攻击造成的伤害 +20%（敌人有增益可解除时启用）'))
F.rebuild(1106, c['eff'])
F.finish('零散条件：承负、克拉拉 4 魂、佩拉追歼', '''<li><b>2026-11-12（零散条件）</b>：tv 93（tools/fix93.py）。寒鸦天赋的 +30% 伤害现在只在敌人真的挂着【承负】时生效（原来按一直有）；克拉拉 4 魂受到攻击后受到的伤害降低 30%，到她下个回合开始；佩拉行迹追歼做成“下一次攻击 +20%”（敌人的增益不模拟，默认关，敌人有增益可解除时自己开）。</li>''',
'''2026-11-12：零散条件 —— tv 93（tools/fix93.py）。新：ec.est（目标有状态）。
  未改 / 存疑：托帕【负债证明】、貊泽【猎物】、阿格莱雅【间隙织线】、不死途【饲饵】仍按一直有；波提欧蛇之上行、景元破阵没做''')
