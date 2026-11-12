"""tv 96：标记类按实际挂在谁身上——托帕【负债证明】、貊泽【猎物】只在最新的目标身上，阿格莱雅 1 魂【间隙织线】挂在被她和衣匠打过的敌人身上；景元破阵按神君实际段数。
新：伤害增益条件 ec.bn = [增益组, N]：持有者身上（主人给的）这组加速叠层 ≥N 层。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 96, sys.argv[2])
C, has, hast = F.C, F.has, F.hast
F.rep('''      if (c.pcd != null && num(u.cd, 50) < num(c.pcd) - 1e-9) return 0;''', '''      if (c.pcd != null && num(u.cd, 50) < num(c.pcd) - 1e-9) return 0;
      if (Array.isArray(c.bn)) { const o = ownerOf(u) || u, z = (u.buffs || []).find(x => x.key === o.id + ":" + c.bn[0]); if (!z || (z.n || 1) < num(c.bn[1])) return 0; }   // 这组加速叠层 ≥N 层（景元破阵）''')
F.rep('''    if (c.pcd != null) L.push(`暴击伤害 ≥${c.pcd}% 时`);''', '''    if (c.pcd != null) L.push(`暴击伤害 ≥${c.pcd}% 时`);
    if (Array.isArray(c.bn)) L.push(`叠层 ≥${c.bn[1]} 层时`);''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
# 托帕
has('111202', '【负债证明】仅对最新被施加的目标生效')
c = C[1112]; E = c['eff']; x = find(E, '战技：【负债证明】受到的追加攻击伤害'); o = x['n']; n = '战技：【负债证明】的敌人受到的追加攻击伤害 +50%（3 魂 55%；只在最新的目标身上）'; x['n'] = n
E.insert(E.index(x), dict(y='dbuf', t='skill', tg='enemies', m='vuln', v=0, sc='f', d=0, bk='fz', n='战技：【负债证明】只对最新的目标生效（先从别的敌人身上去掉）'))
F.rebuild(1112, E, rename={o: n})
# 貊泽
has('122302', '使指定敌方单体目标成为【猎物】')
c = C[1223]; E = c['eff']; x = find(E, '行迹不折镆干：【猎物】'); o = x['n']; n = '行迹不折镆干：【猎物】受到的追加攻击伤害 +25%（战技的目标；只在最新的猎物身上）'
x.update(n=n, t='skill', tg='ehit'); i = E.index(x)
E.insert(i, dict(y='dbuf', t='skill', tg='enemies', m='vuln', v=0, sc='f', d=0, bk='bz', n='战技：换【猎物】时先从别的敌人身上去掉'))
F.rebuild(1223, E, rename={o: n})
# 阿格莱雅 1 魂
has('r:140201', '【间隙织线】')
e1 = F.eid(1402, 1); x = find(e1['eff'], 'E1：【间隙织线】的敌人受到的伤害'); i = e1['eff'].index(x)
x.update(t='atk', aw='self', tg='ehit', n='E1：【间隙织线】的敌人受到的伤害 +15%（阿格莱雅攻击过的敌人）')
e1['eff'].insert(i + 1, dict(x, aw='sm', n='E1：同上（衣匠攻击过的敌人）'))
# 景元破阵
hast(1204, '破阵', '若【神君】下回合的攻击段数大于等于#1[i]段，则其下回合的暴击伤害提高#2[i]%')
c = C[1204]; x = find(c['eff'], '行迹破阵'); x.update(n='行迹破阵：神君攻击段数 ≥6 时暴击伤害 +25%（按神君当时的实际段数）', ec={'bn': ['lord', 3]}); F.touch(1204)
# 星期日过时说明
C[1313]['notes'] = [y.replace('；E6“暴击率超过 100% 的部分每 1% 换 2% 暴击伤害”没做', '') for y in C[1313].get('notes', [])]; F.touch(1313)
F.finish('标记按实际目标、景元破阵', '''<li><b>2026-11-13（标记类）</b>：tv 96（tools/fix96.py）。托帕【负债证明】、貊泽【猎物】的追加攻击易伤只挂在战技最新的目标身上（原来貊泽是敌方全体一直有）；阿格莱雅 1 魂【间隙织线】的易伤只在她和衣匠打过的敌人身上；景元行迹破阵按神君当时的实际段数（≥6 段才有暴伤 +25%）。星期日 6 魂“暴击率溢出换暴伤”其实早已做好，去掉过时的“没做”说明。</li>''',
'''2026-11-13：标记类 —— tv 96（tools/fix96.py）。新：ec.bn。
  未改 / 存疑：【负债证明】/【猎物】目标死亡后自动换人、貊泽充能为 0 时解除猎物没做；不死途【饲饵】仍按一直有''')
