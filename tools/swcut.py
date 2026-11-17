# 银狼LV.999 强化普攻【狼尊时刻】（可重复运行，没改 tv）
# ① 修正：强普的伤害按施放时的【隐藏分】算。以前行动记录的隐藏分是“扣掉这次强普次数之后”记的，
#    最后一次强普退出无敌玩家、隐藏分已经清空（1 魂留 20%），伤害按清空后的隐藏分算，明显偏低。
# ② 官方原文：“若对场上所有敌方造成了致命伤害则结束本次技能，当存在可攻击的敌方目标后获得1个额外回合并基于剩余弹射段数和
#    【头号补给盲盒】次数再次施放。每回合首次触发该效果时，使自身所有增益效果延长1回合。”
#    用户说明：强普期间 BOSS 转阶段也会触发（所以有分阶段的敌人转阶段就算，场上还有别的敌人也一样）。
#    开了“我方伤害扣敌人生命值”才有：结算这次强普时按均分顺序打，打到转阶段 / 全部打倒就停，剩下的比例记在 rec.cut，
#    马上给银狼 1 个额外回合再次施放（新记录 rec.re = 剩下的比例，不再扣强普次数），自身增益（含全队增益）延长 1 回合。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

# ① 施放时的隐藏分
rep('''        rec.spShort = onAction(swU, rec.act); reSnap(rec, swU);
        if (rec.ult) spendCharge();''',
'''        rec.spShort = onAction(swU, rec.act); reSnap(rec, swU);
        if (rec.ult) { rec.scU = sw.score; spendCharge(); }   // scU：施放时的隐藏分（伤害按它算；最后一次强普扣完次数后隐藏分会被清空）''')
rep('''        if (u === swU && !rec.ult && rec.act === "skill" && num(W.skillPunch) > 0) addPunch(num(W.skillPunch), "银狼战技");
        if (rec.ult) spendCharge();''',
'''        if (u === swU && !rec.ult && rec.act === "skill" && num(W.skillPunch) > 0) addPunch(num(W.skillPunch), "银狼战技");
        if (rec.ult) { rec.scU = sw.score; spendCharge(); }''')
rep('      if (actor === swU && rec.ult) spendCharge();',
    '      if (actor === swU && rec.ult) { rec.scU = sw.score; spendCharge(); }')
rep('''    if (tidOf(u) === "1506" && rec && rec.score != null) {
      const sc = num(rec.score), k1''',
'''    if (tidOf(u) === "1506" && rec && (rec.scU ?? rec.score) != null) {
      const sc = num(rec.scU ?? rec.score), k1''')

# ② 被打断 / 再次施放
rep('''    const setScore = (v, why) => { sw.score = Math.max(0, Math.min(scap(), v)); scoreH.push({ t, v: sw.score, why }); };''',
'''    const setScore = (v, why) => { sw.score = Math.max(0, Math.min(scap(), v)); scoreH.push({ t, v: sw.score, why }); };
    // 强化普攻被打断（打到转阶段 / 全部打倒）后等着再次施放的：{ re: 剩下的比例, sc: 施放时的隐藏分 }
    const swRe = [];
    // 自身所有增益延长 1 回合；全队增益在她身上留一份（原来那份还在时不算，到期后她多算 1 回合）
    const extSelf = u => {
      let n = 0;
      for (const b of u.buffs) { const k = b.own ? "left" : "expire"; if (Number.isFinite(b[k])) { b[k] += 1; n++; } }
      for (const b of TEAM0.buffs) if (b.who === "all" && Number.isFinite(b.expire) && !u.buffs.some(x => x.shK === b.key)) { u.buffs.push(Object.assign({}, b, { key: b.key + "#延长", shK: b.key, expire: b.expire + 1 })); n++; }
      return n;
    };''')
# 全队增益留在她身上的那份：原来那份还在时不算
rep('''    const dbSnap = (u, en) => !u || !u.buffs ? [] : u.buffs.filter(b => b.kind === "d" && !(b.ul === 0 && b.ulAt !== actSeq))''',
    '''    const dbSnap = (u, en) => !u || !u.buffs ? [] : u.buffs.filter(b => b.kind === "d" && !(b.ul === 0 && b.ulAt !== actSeq) && !(b.shK && TEAM0.buffs.some(x => x.key === b.shK)))''')
rep('''        if (k === "el") for (const b of [...(o.buffs || []), ...TEAM0.buffs.filter(z => z.who === "all")]) if (b.kind === "d" && b.st === "el" && !b.ec''',
    '''        if (k === "el") for (const b of [...(o.buffs || []), ...TEAM0.buffs.filter(z => z.who === "all")]) if (b.kind === "d" && b.st === "el" && !(b.shK && TEAM0.buffs.some(x => x.key === b.shK)) && !b.ec''')
# 结算：银狼强普按均分顺序打，打到转阶段 / 全部打倒就停
rep('''      const go = (d, uid, en1) => {
        if (!d || !(d.total > 0)) return;
        const w = SU[uid], ow = w && w.sm ? SU[w.sm.owner] || w : w, killer = ow ? byId[ow.id] : null;
        const ens = U.filter(z => z.kind === "enemy" && !z.gone && z.ehx > 0); if (!ens.length) return;
        const main = en1 && !en1.gone && en1.ehx > 0 ? en1 : ens[0], others = ens.filter(z => z !== main);''',
'''      let goRec = null;
      // 银狼强化普攻【狼尊时刻】：对场上所有敌方造成致命伤害（或有分阶段的敌人被打到转阶段）就结束本次技能，
      // 剩下的弹射 / 盲盒 / 最后一击在 1 个额外回合里再次施放；每回合首次触发时自身所有增益延长 1 回合
      const swCut = (d, rec, main, killer) => {
        let left = d.total, why = "";
        let L = (Array.isArray(d.tw) && d.tw.length ? d.tw.map(([id, sh]) => [byId[id], sh]) : [[main, 1]]).filter(([z, sh]) => z && !z.gone && z.ehx > 0 && sh > 0);
        for (let k = 0; k < 40 && left > 1e-6 && L.length; k++) {
          const S2 = L.reduce((p, x) => p + x[1], 0);
          let xm = Infinity; for (const [z, sh] of L) xm = Math.min(xm, Math.max(0, z.ehc) * S2 / sh);   // 下一个被打到致命的目标（均分着打）
          const step = Math.min(left, xm), ph0 = L.map(([z]) => z.ph);
          for (const [z, sh] of L) { const a = step * sh / S2, cap = Math.max(0, z.ehc); hurtEnemy(z, a >= cap - 1e-6 ? cap + 1e-6 : a, killer); }
          left -= step;
          const ended = L.find(([z], i) => z.phs && z.ph !== ph0[i]);
          L = L.filter(([z]) => !z.gone);
          if (left > 1e-6 && (ended || !L.length)) { why = ended ? `${ended[0].name}转阶段` : "敌人全部倒下"; break; }
        }
        if (!why || !U.some(z => z.kind === "enemy" && !z.gone)) return;   // 没打断，或者已经没有可攻击的敌人（战斗结束）
        const f = left / d.total; rec.cut = f;
        swRe.push({ re: num(rec.re ?? 1, 1) * f, sc: rec.scU ?? rec.score });
        const n = rec.swExt ? 0 : extSelf(swU); rec.swExt = true;
        addLog(`${swU.name} 强化普攻打到${why}，本次技能结束（剩 ${Math.round(f * 100)}% 没打），获得 1 个额外回合再次施放剩下的部分${n ? `；自身 ${n} 个增益延长 1 回合` : ""}`, false, swU.color, swU.id);
      };
      const go = (d, uid, en1) => {
        if (!d || !(d.total > 0)) return;
        const w = SU[uid], ow = w && w.sm ? SU[w.sm.owner] || w : w, killer = ow ? byId[ow.id] : null;
        const ens = U.filter(z => z.kind === "enemy" && !z.gone && z.ehx > 0); if (!ens.length) return;
        const main = en1 && !en1.gone && en1.ehx > 0 ? en1 : ens[0], others = ens.filter(z => z !== main);
        if (goRec && swU && goRec.uid === swU.id && goRec.act === "ebasic" && goRec.ult) { swCut(d, goRec, main, killer); return; }''')
rep('''const w = SU[x.uid]; if (!w || w.kind !== "ally") continue; go(one(x, () => dmgOf(x, w)), x.uid); }''',
    '''const w = SU[x.uid]; if (!w || w.kind !== "ally") continue; goRec = x; try { go(one(x, () => dmgOf(x, w)), x.uid); } finally { goRec = null; } }''')
# 额外回合：再次施放剩下的部分（不再扣强普次数）
rep('''    const drainOne = () => {
      if (swU && sw.pending > 0) {''',
'''    const drainOne = () => {
      if (swU && swRe.length) {   // 银狼强化普攻被打断后：1 个额外回合，再次施放剩下的部分（伤害按剩下的比例；不再扣强普次数）
        const q = swRe.shift(); stats.extras++;
        const xn = swU.extraN = (swU.extraN || 0) + 1;
        settle();
        ultChecks(swU.id, "x" + xn, "in");
        const rec = { uid: swU.id, t, turn: swU.turns, xn, spd: spdOf(swU), cycle: cycleOf(t), extra: true, ult: true, seq: seq++, re: q.re, why: "再次施放" };
        rec.act = "ebasic"; rec.nat = "ebasic";
        rec.wx = wxActive(); annRec(rec); actions.push(rec);
        swU.acting = true;
        for (const e of fx(swU, "xturn")) apply(e, swU, swU.color);
        swU.acting = false;
        rec.spShort = onAction(swU, rec.act); reSnap(rec, swU);
        rec.scU = q.sc; rec.pool = pool; rec.score = sw.score; rec.sp = sp;
        if (isAtk(swU, rec.act)) atkAct(swU, false, rec.act);
        allyAct(swU, false);
        settle();
        clearConv();
        rec.poolD = pool; rec.scoreD = sw.score;
        ultChecks(swU.id, "x" + xn, "after");
        checkUlts();
        return true;
      }
      if (swU && sw.pending > 0) {''')
# 伤害：被打断的只算打出去的部分，再次施放的只算剩下的部分
rep('''    const total = (mainDmg + rider + yaoDmg + (xr ? xr.sum : 0)) * swScoreM + swBox;
    return { total, xr, swBox, swScoreM,''',
'''    const reF = tidOf(u) === "1506" && e.key === "b2" && rec && !rec.__box ? num(rec.re ?? 1, 1) * (1 - num(rec.cut, 0)) : 1;   // 强化普攻被打断（只打出一部分）/ 再次施放剩下的部分
    const reTxt = reF < 1 ? (rec.re != null ? `再次施放剩下的 ${fmt(num(rec.re) * 100, 1)}%` : "") + (num(rec.cut) > 0 ? `${rec.re != null ? "，" : ""}打到转阶段 / 全部倒下时结束，打出 ${fmt((1 - num(rec.cut)) * 100, 1)}%` : "") : "";
    const total = ((mainDmg + rider + yaoDmg + (xr ? xr.sum : 0)) * swScoreM + swBox) * reF;
    return { total, reF, reTxt, xr, swBox, swScoreM,''')
rep('''      + (r.yaoDmg ? ` ＋ 爻光【大吉大利】${r.yaoN} 次 × ${fmt(r.yaoV * 100, 1)}%（欢愉度 ${fmt(r.yaoEl, 1)}%） = ${Math.round(r.yaoDmg).toLocaleString()}` : "")
      + ` = ${Math.round(r.total).toLocaleString()}`;''',
'''      + (r.yaoDmg ? ` ＋ 爻光【大吉大利】${r.yaoN} 次 × ${fmt(r.yaoV * 100, 1)}%（欢愉度 ${fmt(r.yaoEl, 1)}%） = ${Math.round(r.yaoDmg).toLocaleString()}` : "")
      + (r.reF != null && r.reF < 1 ? `；以上合计 × ${fmt(r.reF * 100, 1)}%（${r.reTxt}）` : "")
      + ` = ${Math.round(r.total).toLocaleString()}`;''')
# 更新日志
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17（银狼强化普攻：施放时的隐藏分、转阶段打断后再次施放，没改 tv；tools/swcut.py）</b>。① <b>修正</b>：强普伤害改按<b>施放时</b>的【隐藏分】算。以前行动记录的隐藏分是扣完这次强普次数后记的，每次无敌玩家的最后一次强普退出时隐藏分已清空（1 魂留 20%），伤害按清空后的算，只有正常的一半左右。② 官方原文「若对场上所有敌方造成了致命伤害则结束本次技能，当存在可攻击的敌方目标后获得 1 个额外回合并基于剩余弹射段数和【头号补给盲盒】次数再次施放。每回合首次触发该效果时，使自身所有增益效果延长 1 回合」，用户说明 BOSS 转阶段也算：开了“我方伤害扣敌人生命值”时，银狼的强普按均分着打，打到有分阶段的敌人转阶段（场上还有别的敌人也算）或敌人全部倒下就结束，剩下的比例在 1 个额外回合里再次施放（不再扣强普次数，伤害按剩下的比例、新阶段的减益重新算），被打断的那次只算打出去的部分；自身所有增益（含全队增益，原来的到期后她多算 1 回合）延长 1 回合。日志和伤害提示里写了比例。对已有配置：有银狼无敌玩家的方案伤害变高；行动顺序只在开了敌人生命值、强普打到转阶段时多出“再次施放”的额外回合。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
