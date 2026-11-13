"""tv 102：
- 伤害增益新字段 ux = 最多生效几次攻击（持有者每施放 1 次攻击 −1，用完不再生效；重新施加 / 换持有者时次数接着算），uxr = 重新施加时把次数重置。
  刻律德菈【军功】附加伤害最多触发 20 次、每次开大重置。
- 敌方身上的伤害增益新字段 mvd = 目标被消灭时转到下一个敌人（托帕【负债证明】）。
- 新目标 a1（队伍里的第一位角色）、st:状态名（持有这个状态的我方目标）。刻律德菈终结技：场上没有【军功】时给第一位角色。
- 刻律德菈 E1：【爵位】战技额外无视 20% 防御力。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 102, sys.argv[2])
C, has = F.C, F.has
F.rep('''      if (x.mv) e.mv = true;''', '''      if (x.ux) e.ux = x.ux; if (x.uxr) e.uxr = 1; if (x.mvd) e.mvD = 1;   // 最多生效几次攻击 / 重新施加时重置次数 / 目标被消灭时转到下一个敌人
      if (x.mv) e.mv = true;''')
F.rep('''      if (target === "evt") return evTarget ? [evTarget] : [];''', '''      if (target === "evt") return evTarget ? [evTarget] : [];
      if (target === "a1") { const a = U.find(u => u.kind === "ally" && !u.sm && !u.gone); return a ? [a] : []; }   // 队伍里的第一位角色
      if (typeof target === "string" && target.startsWith("st:")) return U.filter(u => u.kind === "ally" && !u.gone && hasSt(u, target.slice(3)));   // 持有这个状态的我方目标''')
F.rep('''      if (eff.mv && bk && !teamT && !onEnemy) for (const z of U)''', '''      let ul0 = null; if (eff.ux) for (const z of U) { const o0 = (z.buffs || []).find(b => b.key === key && b.ul != null); if (o0) ul0 = o0.ul; }   // 剩余次数跟着这组增益走（换持有者也不重置）
      if (eff.mv && bk && !teamT && !onEnemy) for (const z of U)''')
F.rep('''        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: (amt0 + ovx) * n, n };''', '''        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: (amt0 + ovx) * n, n };
        if (eff.ux) { b.ul = ul0 != null && !eff.uxr ? ul0 : Math.round(num(eff.ux)); b.at = actSeq; }
        if (eff.mvD) b.mvd = 1;''')
F.rep('''const dbSnap = (u, en) => !u || !u.buffs ? [] : u.buffs.filter(b => b.kind === "d")''', '''const dbSnap = (u, en) => !u || !u.buffs ? [] : u.buffs.filter(b => b.kind === "d" && !(b.ul === 0 && b.ulAt !== actSeq))''')
F.rep('''    const nxUse = (who, k) => { if (who && who.buffs && who.buffs.some(b => b.nx))''', '''    const nxUse = (who, k) => { if (who && who.buffs) for (const b of who.buffs) if (b.ul > 0 && b.at < actSeq && --b.ul === 0) b.ulAt = actSeq;   // 有次数的增益：每施放 1 次攻击 −1
      if (who && who.buffs && who.buffs.some(b => b.nx))''')
F.rep('''      if (killer && killer.kind === "ally") fireEv("kill", killer);
      fireAll("ekill", en);''', '''      if (killer && killer.kind === "ally") fireEv("kill", killer);
      { const nx = U.find(z => z.kind === "enemy" && !z.gone), mv = (en.buffs || []).filter(b => b.mvd);   // 只对一个目标生效的效果：目标被消灭时转到下一个敌人（托帕【负债证明】；游戏里是随机敌人）
        if (nx && mv.length) { for (const b of mv) if (!nx.buffs.some(x => x.key === b.key)) nx.buffs.push(b); en.buffs = en.buffs.filter(b => !b.mvd); } }
      fireAll("ekill", en);''')
F.rep('''      .concat(withPend || sel === "pend" ? [["pend", "记下的目标"]] : [])''', '''      .concat(withPend || sel === "pend" ? [["pend", "记下的目标"]] : [])
      .concat(sel === "a1" ? [["a1", "队伍里的第一位角色"]] : []).concat(String(sel || "").startsWith("st:") ? [[sel, `持有【${String(sel).slice(3)}】的我方目标`]] : [])''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
# ---- 托帕 ----
has('111202', '我方目标回合开始或行动时，若场上不存在陷入【负债证明】状态的敌方目标，托帕使随机敌方目标陷入【负债证明】状态')
E = C[1112]['eff']; x = find(E, '战技：【负债证明】的敌人受到的追加攻击伤害'); o = x['n']
x['mvd'] = 1; x['n'] = '战技：【负债证明】的敌人受到的追加攻击伤害 +50%（3 魂 55%；只在最新的目标身上，目标被消灭时转到下一个敌人）'
F.rebuild(1112, E, rename={o: x['n']})
# ---- 刻律德菈 ----
has('141204', '该效果最多触发#4[i]次，刻律德菈每次施放终结技时重置可触发次数'); assert F.prm('141204', 10)[3] == 20
has('141203', '若场上不存在持有【军功】的角色，优先使当前队伍中的第一位角色获得【军功】')
has('r:141201', '若当前【军功】已升级为【爵位】，则该角色造成战技伤害时额外无视目标20%的防御力')
c = C[1412]; E = c['eff']
x = find(E, '额外伤害标记：【军功】持有者施放攻击后'); o = x['n']; x['ux'] = 20
x['n'] = '额外伤害标记：【军功】持有者施放攻击后刻律德菈额外造成 60% 攻击力的附加伤害（最多触发 20 次，每次开大重置）'
jg = find(E, '天赋：持有【军功】的角色攻击力')
i = E.index(find(E, '终结技：获得 2 点充能')) + 1
new = [dict(y='state', t='ult', tg='a1', sn='军功', v=1, d=0, mv=1, ns='!军功', so='team', n='终结技：场上没有持有【军功】的角色时，使队伍中的第一位角色获得【军功】'),
       dict(y='dbuf', t='ult', tg='st:军功', m='atkF', ss='atk', v=24, lv=[5, 25.2], d=0, bk='jg', mv=1, n='终结技：给出【军功】时同样提高持有者的攻击力（已有【军功】时只是刷新）'),
       dict(y='dbuf', t='ult', tg='st:军功', m='rx', v=1, sc='cer', d=0, bk='rx', mv=1, ux=20, uxr=1, n='终结技：重置【军功】附加伤害的可触发次数（20 次）')]
assert jg['ss'] == 'atk' and jg['v'] == 24 and jg['lv'] == [5, 25.2] and jg['bk'] == 'jg'
E[i:i] = new
c['notes'] = [n for n in (c.get('notes') or []) if '场上没有军功时给第一位角色' not in n]
F.rebuild(1412, E, rename={o: x['n']}, notes=c['notes'])
e1 = F.eid(1412, 1); y = find(e1['eff'], 'E1：持有【军功】的角色无视目标 16% 防御力'); y['n'] = 'E1：持有【军功】的角色无视目标 16% 防御力'
e1['eff'] += [dict(y='dbuf', t='ult', tg='st:军功', m='defIg', v=16, d=0, bk='e1', mv=1, n='E1：终结技给出【军功】时同样生效'),
              dict(y='dbuf', t='cntUp', nc=6, tg='skpick', m='defIg', v=20, sc='s', d=0, bk='e1j', n='E1：【军功】升级为【爵位】时，该角色造成战技伤害额外无视目标 20% 防御力'),
              dict(y='dbuf', t='aSk', aw='others', **{'as': '军功'}, tg='evt', m='defIg', v=0, sc='s', d=0, bk='e1j', n='E1：奇袭结束后【爵位】的额外无视防御取消')]
e2 = F.eid(1412, 2); e2['eff'].append(dict(y='dbuf', t='ult', tg='st:军功', m='dmg', v=40, d=0, bk='e2', mv=1, n='E2：终结技给出【军功】时同样生效'))
e6 = F.eid(1412, 6); e6['eff'].append(dict(y='dbuf', t='ult', tg='st:军功', m='resPen', v=20, d=0, bk='e6', mv=1, n='E6：终结技给出【军功】时同样生效'))
F.finish('军功附加伤害 20 次上限、负债证明换目标', '''<li><b>2026-11-13</b>：tv 102（tools/fix102.py）。刻律德菈：【军功】的附加伤害按原文最多触发 20 次、每次开大重置；终结技在场上没有【军功】时给队伍里的第一位角色；1 魂【爵位】战技额外无视 20% 防御力。托帕：【负债证明】的敌人被消灭时自动转到下一个敌人（游戏里是随机敌人）。</li>''',
'''2026-11-13：军功附加伤害 20 次上限、负债证明换目标 —— tv 102（tools/fix102.py）。新：伤害增益字段 ux / uxr / mvd，目标 a1、st:状态名。
  未改 / 存疑：负债证明转移按第一个还在的敌人（游戏里随机）；貊泽【猎物】被消灭后没有自动换目标（原文也没有），貊泽的离场状态仍然没做''')
