"""tv 105：远坂凛 1 魂【影子宝石】。count 方式 mod 新字段 shd = [状态名, 门槛]：1 魂起单次消耗 ≥ 门槛时获得等量的这个（充能型）状态；
持有时这次改为消耗全部该状态、不动计数。效果新字段 xst = 自己持有这个状态时不生效。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 105, sys.argv[2])
C, has = F.C, F.has
F.rep('''      if (x.ps) e.stPause = 1;''', '''      if (x.shd) e.shd = x.shd; if (x.xst) e.xSt = x.xst;   // count mod：影子宝石；自己持有这个状态时不生效
      if (x.ps) e.stPause = 1;''')
F.rep('''      if (eff.needSt && String(eff.needSt).trim()) {   // 拥有某个状态才生效''', '''      if (eff.xSt && src && hasSt(src, String(eff.xSt))) return;   // 自己持有这个状态时不生效（远坂凛持有【影子宝石】时不转化战技点）
      if (eff.needSt && String(eff.needSt).trim()) {   // 拥有某个状态才生效''')
F.rep('''            tg.lastCnt = tg.cnt || 0; if (n > 0) subCnt(tg, n * k); if (curRec && curRec.uid === tg.id) curRec.modN = n; continue;''', '''            const sd = Array.isArray(eff.shd) ? eff.shd : null, sh = sd && tg.st && tg.st[sd[0]];
            if (sh && num(sh.left) > 0) {   // 持有【影子宝石】：这次消耗全部影子宝石，不动计数
              n = Math.floor((num(sh.left) + 1e-9) / k); if (num(eff.dcap) > 0) n = Math.min(n, Math.round(num(eff.dcap)));
              marks.push({ t, uid: tg.id, label: `消耗${sd[0]} ${Math.round(sh.left)}`, color: srcColor, from: tg.name }); endSt(tg, sd[0]);
              if (curRec && curRec.uid === tg.id) curRec.modN = n; continue;
            }
            tg.lastCnt = tg.cnt || 0; if (n > 0) subCnt(tg, n * k); if (curRec && curRec.uid === tg.id) curRec.modN = n;
            if (sd && num(tg.eid) >= 1 && n * k >= num(sd[1])) { tg.st[sd[0]] = { left: n * k, tick: "chg" }; marks.push({ t, uid: tg.id, label: `${sd[0]} ${n * k}`, color: srcColor, from: tg.name }); }   // 1 魂：单次消耗 ≥30 点，获得等量的【影子宝石】
            continue;''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('r:150801', '若单次强化战技消耗的【宝石能量】数量大于等于30点，远坂凛获得与消耗的【宝石能量】数量相同的【影子宝石】')
has('r:150801', '强化战技会消耗所有【影子宝石】，不触发将战技点转化为【宝石能量】的效果且不消耗【宝石能量】')
c = C[1508]; E = c['eff']
sp = find(E, '强化战技第二魔法实验：施放时若战技点大于 2 点'); o1 = sp['n']; sp['xst'] = '影子宝石'; sp['n'] += '（1 魂持有【影子宝石】时不触发）'
md = find(E, '强化战技第二魔法实验：每消耗 3 点【宝石能量】额外造成 1 次伤害'); o2 = md['n']; md['shd'] = ['影子宝石', 30]
md['n'] = '强化战技第二魔法实验：每消耗 3 点【宝石能量】额外造成 1 次伤害，重复直至不足 3 点（最多 33 轮；1 魂：单次消耗 ≥30 点时获得等量【影子宝石】，持有时改为消耗全部【影子宝石】）'
i = E.index(sp)
E.insert(i, dict(y='state', t='skill', tg='self', sn='第二魔法实验', v=1, d=0, ns='影子宝石', n='1 魂：持有【影子宝石】时战技强化为【第二魔法实验】'))
c['notes'] = [n.replace('；E1【影子宝石】没做', '') for n in (c.get('notes') or [])]
F.rebuild(1508, E, rename={o1: sp['n'], o2: md['n']}, notes=c['notes'])
F.finish('远坂凛 1 魂影子宝石', '''<li><b>2026-11-13</b>：tv 105（tools/fix105.py）。远坂凛 1 魂：单次强化战技消耗的【宝石能量】≥30 点时获得等量【影子宝石】；持有【影子宝石】时战技直接强化，消耗全部【影子宝石】、不把战技点转成【宝石能量】、也不消耗【宝石能量】。</li>''',
'''2026-11-13：远坂凛 1 魂影子宝石 —— tv 105（tools/fix105.py）。新：count mod 的 shd、效果字段 xst''')
