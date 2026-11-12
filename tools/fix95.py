"""tv 95：4.7 奇缘星魂（EX 星魂）：黄泉、丹恒•饮月、景元。原文取自 BWIKI（官方 dump 里还没有）。
模板字段 exe = {n: 名称, eff: [...], cm: 计数上限}；卡片字段 ex（勾选“奇缘星魂”）；applyEquip 勾上时加 exe.eff（来源标记 "ex"）。
加速叠层字段 stx（stX）：勾了奇缘星魂时的层数上限；fadv（fAdv）：勾了奇缘星魂、叠到上限的那一刻目标立即行动（景元【神君】）。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 95, sys.argv[2])
C = F.C
F.rep('''    if (T) for (const x of T.eid) if (x.r <= (u.eid || 0)) add.push(...dbEffects(x.eff, u, "e" + x.r));''', '''    if (T) for (const x of T.eid) if (x.r <= (u.eid || 0)) add.push(...dbEffects(x.eff, u, "e" + x.r));
    if (T && T.exe && u.ex) add.push(...dbEffects(T.exe.eff, u, "ex"));   // 奇缘星魂（4.7）''')
F.rep('''    // 星魂改计数上限（砂金•戏浪 2 魂热意 30 → 50）；手动改过的不动''', '''    if (T && T.cnt && T.exe && T.exe.cm && u.cntName === T.cnt.n && (num(u.cntMax) === T.cnt.max || num(u.cntMax) === T.exe.cm)) u.cntMax = u.ex ? T.exe.cm : T.cnt.max;   // 奇缘星魂改计数上限（丹恒•饮月逆鳞 3 → 4）
    // 星魂改计数上限（砂金•戏浪 2 魂热意 30 → 50）；手动改过的不动''')
F.rep('''      u[k] = k === "r4" ? t.checked : k === "lcR"''', '''      u[k] = k === "r4" || k === "ex" ? t.checked : k === "lcR"''')
F.rep('''/^e\\d$/.test(e.eq) ? "eid"''', '''/^e(\\d|x)$/.test(e.eq) ? "eid"''')
F.rep('''u.eid || 0)}</select></label>` : ""}''', '''u.eid || 0)}</select></label>` : ""}
          ${tplOf(u) && tplOf(u).exe ? `<label for="ex-${u.id}" title="奇缘星魂「${esc(tplOf(u).exe.n)}」：和 1～6 魂分开，勾上才生效"><input type="checkbox" id="ex-${u.id}" data-u="${i}" data-eq="ex"${u.ex ? " checked" : ""}> 奇缘星魂</label>` : ""}''')
F.rep('''      if (x.nx) e.nxt = x.nx;''', '''      if (x.stx) e.stX = x.stx; if (x.fadv) e.fAdv = 1;   // 奇缘星魂：层数上限、叠满立即行动
      if (x.nx) e.nxt = x.nx;''')
F.rep('''          const lim = Array.isArray(eff.stE) && kSrc && num(kSrc.eid) >= num(eff.stE[0])''', '''          const exOn = !!(kSrc && (ownerOf(kSrc) || kSrc).ex);
          const exG = exOn && eff.bk ? (kSrc.effects || []).filter(z => z.bk === eff.bk && !z.off && num(z.stX) > 0) : [];   // 奇缘星魂里同一组的效果：上限和“叠满立即行动”对原来的效果也生效
          const lim = exG.length ? Math.round(Math.max(...exG.map(z => num(z.stX)))) : Array.isArray(eff.stE) && kSrc && num(kSrc.eid) >= num(eff.stE[0])''')
F.rep('''          const dur = Math.max(0, Math.round(num(eff.duration)));
          // srcpct''', '''          if (exG.some(z => z.fAdv) && lim > 0 && n >= lim && oldN < lim && tg !== curActor && !tg.gone) { pull(tg, 10000); marks.push({ t, uid: tg.id, label: "+100%", color: srcColor, from: "攻击段数叠满" }); }   // 叠满的那一刻立即行动
          const dur = Math.max(0, Math.round(num(eff.duration)));
          // srcpct''')
D = lambda cid: next(c for c in F.DB['chars'] if c['id'] == cid)
# 景元
c = C[1204]
D(1204)['exe'] = {'n': '万钧入盏，风静灯明', 'eff': [
    dict(y='dbuf', t='start', tg='self', m='dmg', v=240, d=0, bk='ex', n='奇缘星魂：【神君】获得强化期间景元造成的伤害 +240%（战斗开始和【神君】每次行动后获得，持续 4 回合；按一直有算）'),
    dict(y='spd', t='skill', tg='sm:lord', v=10, m='flat', d=1, st=27, stx=27, sa=6, bk='lord', cnt='own', fadv=1, n='奇缘星魂：施放战技时【神君】额外 +6 段（上限提高 20 段到 30 段，叠满立即行动）'),
    dict(y='spd', t='ult', tg='sm:lord', v=10, m='flat', d=1, st=27, stx=27, sa=12, bk='lord', cnt='own', fadv=1, n='奇缘星魂：施放终结技时【神君】额外 +12 段')]}
F.touch(1204)
# 黄泉
D(1308)['exe'] = {'n': '虚隙一顾…枯骨眠霜', 'eff': [
    dict(y='fua', t='atk', aw='others', tg='self', v=0, ac=1, n='奇缘星魂：队友攻击带有【集真赤】的敌人后黄泉发动追加攻击（全体 300% + 6 次随机 80%，视为终结技伤害；每回合 1 次，黄泉回合开始时重置；按敌人都有集真赤算）'),
    dict(y='energy', t='fua', tg='self', v=1, m='fixed', n='奇缘星魂：这次追加攻击后获得 1 点【残梦】')]}
F.DMG['1308']['f'] = {"v": [3.0] * 15, "adj": [], "rnd": [4.8] * 15, "tg": 3, "el": 0, "stat": "atk", "n": "奇缘星魂追加攻击", "max": 15}
F.touch(1308)
# 丹恒•饮月
D(1213)['exe'] = {'n': '沧溟间，月落潮平', 'cm': 4, 'eff': [
    dict(y='dbuf', t='spUse', aw='all', nth=5, tg='self', m='dmg', v=240, d=3, bk='ex', n='奇缘星魂：我方每消耗 5 个战技点，丹恒•饮月造成的伤害 +240%，持续 3 回合'),
    dict(y='fua', t='spUse', aw='all', nth=5, tg='self', v=0, n='奇缘星魂：随后发动追加攻击，6 段共对敌方全体 500% 攻击力（视为普攻伤害）'),
    dict(y='count', t='fua', tg='self', v=1, n='奇缘星魂：追加攻击后获得 1 个【逆鳞】（上限 4 个）')]}
F.DMG['1213']['f'] = {"v": [5.0] * 15, "adj": [], "rnd": [], "tg": 3, "el": 0, "stat": "atk", "n": "奇缘星魂追加攻击", "max": 15}
F.touch(1213)
F.finish('4.7 奇缘星魂：黄泉、丹恒•饮月、景元', '''<li><b>2026-11-13（奇缘星魂）</b>：tv 95（tools/fix95.py）。4.7 的奇缘星魂（EX 星魂）：黄泉、丹恒•饮月、景元的卡片上“星魂”旁边多了“奇缘星魂”勾选框，和 1～6 魂分开，默认不勾。<b>景元</b>「万钧入盏，风静灯明」：【神君】攻击段数上限 10 → 30，叠满时立即行动；景元伤害 +240%；战技 / 终结技额外 +6 / +12 段。<b>黄泉</b>「虚隙一顾…枯骨眠霜」：队友攻击后追加攻击（全体 300% + 6 次随机 80%），+1 残梦，每回合 1 次。<b>丹恒•饮月</b>「沧溟间，月落潮平」：逆鳞上限 4；我方每消耗 5 个战技点，伤害 +240%（3 回合）并追加攻击（全体 500%），+1 逆鳞。原文取自 BWIKI。</li>''',
'''2026-11-13：奇缘星魂 —— tv 95（tools/fix95.py）。新：模板 exe、卡片 ex、spd stx / fadv。原文来源 BWIKI（官方 dump 还没有奇缘星魂），抓取时是转述不是逐字。
  未改 / 存疑：黄泉追加攻击“视为终结技伤害”、饮月“视为普攻伤害”没套对应的增伤；黄泉按敌人都有【集真赤】、追加攻击给敌人叠集真赤没做；景元强化按一直有；数值待官方 dump 更新后再核对''')
