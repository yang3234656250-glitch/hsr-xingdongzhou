"""tv 74：击破收尾 —— 同谐主 8005 / 8006 随波逐流、乱破 1317 E2 和秘技、大丽花 1321 行迹弃旧恋新（固定削韧 + 回能）、卡片上的“削韧段数”。
用法：python3 tools/fix74.py index.html <官方 json 目录>
引擎：模板 x.tghAdd = [[键, 主目标另加的削韧值（30 = 10 点）, 几魂起], …]；角色卡 u.thit = {键: 打到主目标的段数}（主目标的削韧值 × 段数，弹射 / 多段技能自己填）；
tfix 的 nw = 只对被施放者添加了“原本没有的弱点”的敌人；能量方式 maxp 的 ecx = 最多恢复到能量上限的 X%、nwk = 施放者给至少一个敌人添加了原本没有的弱点时才生效。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 74, sys.argv[2])
C, has, hast, prm = F.C, F.has, F.hast, F.prm
# ---------- 引擎 ----------
F.rep('''        const base = num(v[1]) + (i === 0 ? num(v[0]) : i <= 2 ? num(v[2]) : 0); if (!(base > 0)) return;''',
      '''        const base = num(v[1]) + (i === 0 ? num(v[0]) * hitN + addM : i <= 2 ? num(v[2]) : 0); if (!(base > 0)) return;''')
F.rep('''      U.filter(x => x.kind === "enemy" && !x.gone).forEach((en, i) => {
        const mx = toughMax(en); if (!(mx > 0)) return;
        const m = monOf(en), weak =''', '''      const hitN = Math.max(1, Math.round(num((o.thit || {})[key], 1)));   // 卡片上填的“打到主目标的段数”
      let addM = 0; for (const z of Array.isArray(X.tghAdd) ? X.tghAdd : []) if (z[0] === key && num(o.eid) >= num(z[2])) addM += num(z[1]);   // 主目标另加的削韧值（同谐主随波逐流、乱破 E2）
      U.filter(x => x.kind === "enemy" && !x.gone).forEach((en, i) => {
        const mx = toughMax(en); if (!(mx > 0)) return;
        const m = monOf(en), weak =''')
F.rep('''    const toughHit = (who, key) => {''', '''    const newWk = (en, own) => { const m = monOf(en); return !!(m && m.w) && (en.wk || []).some(z => z.own === own.id && (z.el === "all" || [...z.el].some(ch => !m.w.includes(ch)))); };   // 这个人给它添加了原本没有的弱点
    const toughHit = (who, key) => {''')
F.rep('''          if (eff.opt) { if ((tg.tf1 || {})[key]) continue;''', '''          if (eff.nw && !newWk(tg, own)) continue;
          if (eff.opt) { if ((tg.tf1 || {})[key]) continue;''')
F.rep('''          if (eff.mode === "maxp") { if (hasEnergy(tg) && !(noStdE(tg) && tg !== src)) addEnergy(tg, Math.max(num(eff.eMin), eCfg(tg).maxE * v / 100), false); continue; }''',
      '''          if (eff.mode === "maxp") {
            if (eff.nwk && !(brkOn && src && U.some(z => z.kind === "enemy" && !z.gone && newWk(z, ownerOf(src) || src)))) continue;   // 施放者添加过原本没有的弱点才生效（大丽花弃旧恋新）
            let a = Math.max(num(eff.eMin), eCfg(tg).maxE * v / 100); if (num(eff.ecx) > 0) a = Math.min(a, eCfg(tg).maxE * num(eff.ecx) / 100 - num(tg.e));   // ecx：最多恢复到能量上限的 X%
            if (a > 1e-9 && hasEnergy(tg) && !(noStdE(tg) && tg !== src)) addEnergy(tg, a, false); continue; }''')
F.rep('''      if (x.vpc) e.vpc = x.vpc;''', '''      if (x.nw) e.nw = 1; if (x.nwk) e.nwk = 1; if (x.ecx) e.ecx = x.ecx;
      if (x.vpc) e.vpc = x.vpc;''')
# 卡片：削韧段数
F.rep('''placeholder="0" data-u="${i}" data-f="be" style="width:58px"></label>
''', '''placeholder="0" data-u="${i}" data-f="be" style="width:58px"></label>
          ${(tb => { const ks = [["b", "普攻"], ["b2", "强普"], ["s", "战技"], ["s2", "强化战技"], ["u", "终结技"], ["f", "追击"], ["e", "欢愉技"], ["m", "忆灵技"]].filter(([k]) => tb && tb[k] && num(tb[k][0]) > 0); return !ks.length ? "" : `<details class="dmg-mult thit"${u.thit ? " open" : ""}><summary title="弹射、多段的技能，官方数据只有一段的削韧值。知道一次技能有几段打在主目标上，就填在这里：主目标的削韧值 × 段数">削韧段数${u.thit ? "（已填）" : ""}</summary><div class="row">${ks.map(([k, l]) => `<label for="th-${u.id}-${k}" title="${l}：主目标每段削韧 ${fmt(num(tb[k][0]) / 3, 1)} 点">${l} × <input type="number" id="th-${u.id}-${k}" min="1" step="1" value="${(u.thit || {})[k] ?? ""}" placeholder="1" data-u="${i}" data-thit="${k}" style="width:46px"></label>`).join("")}</div></details>`; })(TGH[String(u.tpl || tidOf(u) || "")])}
''')
F.rep('''    if (!t.dataset.f && !t.dataset.a && !t.dataset.s) return;
    onField(t, t.tagName === "SELECT"''', '''    if (t.dataset.thit) {   // 削韧段数：1 或清空 = 不填
      const u = S.units[+t.dataset.u], n = Math.round(num(t.value)); u.thit = u.thit || {};
      if (n > 1) u.thit[t.dataset.thit] = n; else delete u.thit[t.dataset.thit];
      if (!Object.keys(u.thit).length) delete u.thit;
      update(); return;
    }
    if (!t.dataset.f && !t.dataset.a && !t.dataset.s) return;
    onField(t, t.tagName === "SELECT"''')
# ---------- 同谐主 ----------
for cid in (8005, 8006):
    hast(cid, '随波逐流', '施放战技时，第一次伤害的削韧值额外提高#1[i]%'); assert ('"%d":{"b":[30,0,0],"s":[30,0,30]' % cid) in F.s
    c = C[cid]; c['notes'] = [n for n in c.get('notes', []) if '随波逐流' not in n]
    F.rebuild(cid, list(c['eff']), x={'tghAdd': [['s', 30, 0]]}, notes=['行迹随波逐流：战技第一次伤害的削韧值 +100%（主目标多削 10 点，已自动处理）；战技后 4 次随机伤害的削韧没算，知道打到主目标几段可以在卡片“削韧段数”里填', '秘技、E4 还没做'])
# ---------- 乱破 ----------
has('r:131702', '强化普攻的前2段攻击对指定敌方单体的削韧值提高50%'); has('131707', '对每个敌方目标造成#5[i]点无视弱点属性的削韧，以及等同于乱破#2[i]%虚数属性击破伤害的击破伤害，并对其相邻目标造成等同于乱破#3[i]%虚数属性击破伤害的击破伤害')
assert prm('131707', 1) == [20, 2, 1.8, 10, 30] and '"1317":{"b":[30,0,0],"s":[0,30,0],"b2":[75,0,45]}' in F.s
c = C[1317]; c['notes'] = [n for n in c.get('notes', []) if 'E2（前 2 段' not in n]
new = list(c['eff']) + [
    dict(y='tfix', t='start', tg='enemies', v=30, ig=1, bk='mj', off=1, n='秘技忍步•血义理：主动攻击敌人进入战斗后，对每个敌方目标造成 30 点无视弱点属性的削韧（用了秘技再启用）'),
    dict(y='brkd', t='start', tg='enemies', nb=1, v=200, off=1, n='秘技忍步•血义理：对每个敌方目标造成 200% 虚数属性击破伤害的击破伤害（用了秘技再启用）'),
    dict(y='brkd', t='start', tg='eadj', nb=1, v=180, off=1, n='秘技忍步•血义理：对相邻目标造成 180% 虚数属性击破伤害的击破伤害（按主目标的相邻目标各 1 次；用了秘技再启用）'),
]
F.rebuild(1317, new, x={'tghAdd': [['b2', 30, 2]]}, notes=['天赋的击破伤害和削韧排在强化普攻本身的削韧之前结算（游戏里是第 3 段时）', 'E2：强化普攻前 2 段对指定敌方单体的削韧值 +50%（主目标多削 10 点，2 魂起自动处理）'])
# ---------- 大丽花 ----------
hast(1321, '弃旧，恋新', '攻击后对每个添加弱点的目标额外造成#5[i]点火属性固定削韧，并恢复#2[i]%能量上限的能量，最多通过此效果恢复至能量上限的#1[i]%')
assert F.TR['1321103']['params'][0] == [0.5, 0.1, 0.3, 2, 20]
c = C[1321]; c['notes'] = [n for n in c.get('notes', []) if '弃旧，恋新的 20 点' not in n]
new = list(c['eff']) + [
    dict(y='state', t='start', tg='self', sn='共舞者', v=1, d=0, n='天赋：大丽花自身也是【共舞者】（【败谢】添加的弱点包含她的火属性）'),
    dict(y='tfix', t='ult', tg='enemies', v=20, nw=1, bk='qj', n='行迹弃旧，恋新：大丽花施放终结技添加过弱点时，攻击后对每个被添加弱点的目标额外造成 20 点火属性固定削韧（敌人原本就有这些弱点时不算）'),
    dict(y='energy', t='ult', tg='self', m='maxp', v=10, ecx=50, nwk=1, n='行迹弃旧，恋新：添加过弱点时恢复 10% 能量上限的能量，最多恢复到能量上限的 50%（要放带韧性、有弱点资料的敌人才会触发）'),
]
F.rebuild(1321, new, notes=['天赋追加攻击的削韧只按 1 次伤害打主目标算（实际是 5 次随机目标），知道打到主目标几段可以在卡片“削韧段数”里填', '行迹弃旧，恋新：其他火属性队友（比如流萤）添加弱点时的固定削韧和回能、秘技还没做'])

F.finish('击破收尾（随波逐流、乱破 E2 / 秘技、大丽花弃旧恋新、削韧段数）', '''<li><b>2026-11-11（击破收尾：削韧段数、随波逐流、乱破 E2 / 秘技、大丽花弃旧恋新）</b>：tv 74（tools/fix74.py）。① 角色卡「击破特攻」下面多了<b>削韧段数</b>：弹射、多段的技能官方数据只有一段的削韧值，知道一次技能有几段打在主目标上就填进去（主目标削韧 × 段数），不填 = 1 段，和以前一样。② <b>同谐主</b>随波逐流：战技第一次伤害削韧 +100%（主目标多 10 点）。③ <b>乱破</b> E2：强化普攻前 2 段对单体削韧 +50%（主目标多 10 点）；秘技的 30 点无视弱点削韧和击破伤害（默认关）。④ <b>大丽花</b>弃旧恋新：终结技给敌人添加了原本没有的弱点时，每个目标 20 点固定削韧，并恢复 10% 能量上限（最多到 50%）。只在放了带韧性的敌人时有变化；大丽花的回能会让她开大稍快。</li>''',
'''2026-11-11（击破收尾）：同谐主（8005 / 8006）随波逐流、乱破（1317）E2 / 秘技、大丽花（1321）弃旧恋新 —— tv 74（tools/fix74.py）。新：x.tghAdd、卡片 thit（削韧段数）、tfix 的 nw、能量 maxp 的 ecx / nwk。
  未改 / 存疑：弹射 / 多段技能的削韧官方数据只有一个“单体”值，是每段还是合计各技能不一致，所以做成卡片上自己填段数；随波逐流和乱破 E2 按“单体值 = 第一段 / 前两段每段 10 点”算；上一批大丽花自己没有记成【共舞者】，【败谢】少了火属性弱点，这次补上；大丽花弃旧恋新只做了她自己终结技的情况，手动敌人（没有弱点资料）不触发。''')
