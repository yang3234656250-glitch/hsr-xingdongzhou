"""tv 76：击破 / 持续伤害相关的光锥（23 个）和遗器（8 套）—— 以前页面不算击破，这些只做了一部分或默认关闭。
用法：python3 tools/fix76.py index.html <官方 json 目录>
引擎：
- 触发条件（触发时判断，DB 字段 → 效果字段）：bby → brkSelf（弱点击破时：只算装备者自己击破的；手动事件照旧都算）、mbe → mBe（击破特攻 ≥N）、
  mat → mAtk（卡片面板攻击力 ≥N）、ewl / ewn → eWl / eWn（主目标 / 至少 N 个敌人有某属性弱点，self = 装备者属性）、edk → eDk（主目标有某种持续伤害，"own" = 装备者挂的）、
  ebr → eBr（主目标处于弱点击破状态）、upk → uPk（装备者的终结技对我方施放）。
- 伤害增益的出手时条件 ec（{dk, dn, wb, wc, wl, be}，在行动快照时按主目标算）：dk 有某种持续伤害、dn 每个持续伤害一层（上限）、wb 有装备者添加的弱点、
  wc 每种弱点一层（上限；没有弱点资料时按 1）、wl 有某属性弱点、be 持有者击破特攻 ≥N。持续伤害 / 击破伤害的记录按受到伤害的那个敌人算。
- 伤害增益类型 bkd（造成的击破伤害提高，单独一个乘区，超击破也吃）；范围 sb = 只算超击破；新触发 wkAdd（装备者为敌人添加弱点时）。
"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 76, sys.argv[2])
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8')); RS = json.load(open(sys.argv[2] + '/relic_sets.json', encoding='utf-8'))
L = {c['id']: c for c in F.DB['lcs']}; R = {c['id']: c for c in F.DB['relics']}
def col(lid, k, pct=True): return [r4(p[k] * (100 if pct else 1)) for p in LR[str(lid)]['params']]
def hasl(lid, frag): F.has(LR[str(lid)]['desc'], frag)
def hasr(rid, j, frag): F.has(RS[str(rid)]['desc'][j], frag)
def LE(lid, frag):
    X = [e for e in L[lid]['eff'] if frag in (e.get('n') or '')]; assert len(X) == 1, (lid, frag, len(X)); return X[0]
def RE(rid, p, frag):
    X = [e for e in R[rid][p]['eff'] if frag in (e.get('n') or '')]; assert len(X) == 1, (rid, frag, len(X)); return X[0]
D = lambda **k: dict(dict(y='dbuf', d=0, t='start', tg='self'), **k)

# ================= 引擎 =================
F.rep('''    const dbSnap = u => !u || !u.buffs ? [] : u.buffs.filter(b => b.kind === "d").map(b => [b.st, b.sc, dbV(b)])''',
'''    const beTeam = () => TEAM0.buffs.reduce((p, z) => p + (z.kind === "d" && z.st === "be" && z.who === "all" ? num(z.v) : 0), 0);
    const dkIs = (name, k) => { const n = String(name); return n.includes(k) || (k === "触电" && n.includes("游丝")) || (k === "灼烧" && n.includes("烬煨")) || (n.includes("奥迹") && ["风化", "裂伤", "灼烧", "触电"].includes(k)); };   // 【游丝】视为触电、【烬煨】视为灼烧、【强化版】【奥迹】视为风化 / 裂伤 / 灼烧 / 触电
    const ecF = (b, u, en) => {   // 伤害增益的出手时条件（光锥 / 遗器）：主目标（第一个敌人；持续伤害 / 击破伤害按受到伤害的那个敌人）的持续伤害、弱点，或持有者的击破特攻
      const c = b.ec;
      if (c.be != null && beOf(u) + beTeam() < num(c.be) - 1e-9) return 0;
      if (c.dk == null && c.dn == null && c.wb == null && c.wc == null && c.wl == null) return 1;
      en = en || U.find(x => x.kind === "enemy" && !x.gone); if (!en) return 0;
      const ds = (en.dots || []).filter(d => !d.gone), m = monOf(en);
      if (c.dk && !ds.some(d => [].concat(c.dk).some(k => k === "own" ? d.src === b.src : dkIs(d.k, k)))) return 0;
      if (c.wb && !(en.wk || []).some(z => z.own === b.src)) return 0;
      if (c.wl && !((m && m.w && m.w.includes(c.wl)) || hasWk(en, c.wl))) return 0;
      let f = 1;
      if (c.dn != null) f *= Math.min(num(c.dn), ds.length);
      if (c.wc != null) { const st = new Set(String(m && m.w || "").split("").filter(Boolean)); for (const z of en.wk || []) for (const ch of z.el === "all" ? "物火冰雷风量虚" : z.el) st.add(ch); f *= st.size ? Math.min(num(c.wc), st.size) : 1; }   // 没有弱点资料：按 1 种
      return f;
    };
    const dbSnap = (u, en) => !u || !u.buffs ? [] : u.buffs.filter(b => b.kind === "d").map(b => { const f = b.ec ? ecF(b, u, en) : 1; return f > 0 ? [b.st, b.sc, dbV(b) * f] : null; }).filter(Boolean)''')
F.rep('''        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: (amt0 + ovx) * n, n };
''', '''        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: (amt0 + ovx) * n, n };
        if (eff.ec) b.ec = eff.ec;   // 出手时条件（按主目标 / 持有者击破特攻）
''')
F.rep('''k: "击破", mult: BRKM[el] * tm, stat: "brk", why: "break", db: dbSnap(o)''', '''k: "击破", mult: BRKM[el] * tm, stat: "brk", why: "break", db: dbSnap(o, en)''')
F.rep('''stat: d.stat, why, db: dbSnap(o)''', '''stat: d.stat, why, db: dbSnap(o, en)''')
F.rep('''k: "击破", mult: BRKM[el || "物"] * (0.5 + mx / 120), stat: "brk", why: "break", db: dbSnap(o)''', '''k: "击破", mult: BRKM[el || "物"] * (0.5 + mx / 120), stat: "brk", why: "break", db: dbSnap(o, en)''')
F.rep('''why: "brkd", db: dbSnap(own)''', '''why: "brkd", db: dbSnap(own, tg)''')
F.rep('''why: "brkd", db: dbSnap(rm)''', '''why: "brkd", db: dbSnap(rm, actor)''')
# 只算自己击破的
F.rep('''      fireEv("break", en);''', '''      { const pb = brkBy; brkBy = o.id; try { fireEv("break", en); } finally { brkBy = pb; } }''')
F.rep('''    const doBreak = (en, o, el, mx) => {''', '''    let brkBy = null, wkDepth = 0;   // 正在结算谁打出的弱点击破（手动事件 = null，都算）；添加弱点时触发的嵌套层数
    const doBreak = (en, o, el, mx) => {''')
F.rep('''          if (kind !== "break" && !evOk(e, u, tg)) continue;''', '''          if (kind !== "break" && !evOk(e, u, tg)) continue;
          if (kind === "break" && e.brkSelf && brkBy != null && brkBy !== u.id) continue;   // 只算自己击破的（开疆、流星追迹的怪盗……）''')
# 触发时条件
F.rep('''      if (eff.ms && !eff.dyn && src && spdOf(src) < num(eff.ms)) return; // 装备效果的速度门槛（dyn 的伤害增益出手时再看）''',
'''      if (eff.ms && !eff.dyn && src && spdOf(src) < num(eff.ms)) return; // 装备效果的速度门槛（dyn 的伤害增益出手时再看）
      if (eff.mBe != null || eff.mAtk != null || eff.eWl || eff.eDk || eff.eBr || eff.uPk) { const H = src ? (ownerOf(src) || src) : null; if (!H || !condX(eff, H)) return; }   // 光锥 / 遗器的触发条件''')
F.rep('''    const applyIn = (eff, src, srcColor) => {''', '''    const condX = (eff, H) => {   // 击破特攻 / 攻击力门槛，主目标的弱点 / 持续伤害 / 破韧，终结技是否对我方施放
      if (eff.mBe != null && beOf(H) + beTeam() < num(eff.mBe) - 1e-9) return false;
      if (eff.mAtk != null && num(H.atk != null && H.atk !== "" ? H.atk : H.atkB) < num(eff.mAtk)) return false;
      if (eff.uPk && !H.effects.some(e => !e.off && e.trigger === "ult" && !["self", "enemies", "efirst", "eadj", "evt"].includes(String(e.target)))) return false;
      if (!eff.eWl && !eff.eDk && !eff.eBr) return true;
      const ens = U.filter(x => x.kind === "enemy" && !x.gone), en = ens[0]; if (!en) return false;
      if (eff.eBr && !(toughMax(en) > 0 && en.broken)) return false;
      if (eff.eWl) { const el = eff.eWl === "self" ? ELW[(tplOf(H) || {}).elem] : eff.eWl, ok = z => { const m = monOf(z); return !!el && ((m && m.w && m.w.includes(el)) || hasWk(z, el)); };
        if (num(eff.eWn) > 1 ? ens.filter(ok).length < num(eff.eWn) : !ok(en)) return false; }
      if (eff.eDk && !(en.dots || []).some(d => !d.gone && [].concat(eff.eDk).some(k => k === "own" ? d.src === H.id : dkIs(d.k, k)))) return false;
      return true;
    };
    const applyIn = (eff, src, srcColor) => {''')
# 添加弱点时
F.rep('''          if (brkOn && toughMax(tg) > 0) addLog(`${src.name} 给 ${tg.name} 添加${wl === "all" ? "全属性" : wl + "属性"}弱点${dur > 0 ? `（${dur} 回合）` : ""}`, false, srcColor);
''', '''          if (brkOn && toughMax(tg) > 0) addLog(`${src.name} 给 ${tg.name} 添加${wl === "all" ? "全属性" : wl + "属性"}弱点${dur > 0 ? `（${dur} 回合）` : ""}`, false, srcColor);
          if (!wkDepth) { wkDepth++; try { for (const e2 of fx(own, "wkAdd")) apply(e2, own, own.color); } finally { wkDepth--; } }   // 装备者为敌人添加弱点时（勿忘她的火焰）
''')
F.rep('''      if (x.wel) e.wel = x.wel;''', '''      if (x.bby) e.brkSelf = 1; if (x.mbe != null) e.mBe = x.mbe; if (x.mat != null) e.mAtk = x.mat; if (x.ewl) e.eWl = x.ewl; if (x.ewn) e.eWn = x.ewn;
      if (x.edk) e.eDk = x.edk; if (x.ebr) e.eBr = 1; if (x.upk) e.uPk = 1; if (x.ec) e.ec = x.ec;   // 光锥 / 遗器的条件
      if (x.wel) e.wel = x.wel;''')
# 造成的击破伤害提高 / 超击破范围
F.rep('''    const vulnM = (1 + (num(cfg.vuln) + ED("vuln") + (inWx ? 20 : 0)) / 100) * (1 + D("xtra") / 100);''',
      '''    const vulnM = (1 + (num(cfg.vuln) + ED("vuln") + (inWx ? 20 : 0)) / 100) * (1 + D("xtra") / 100) * (e.brk ? 1 + D("bkd") / 100 : 1);   // bkd：造成的击破伤害提高（超击破也吃）''')
F.rep('''(x[1] === "es" && key === "s2")) ? num(x[2]) : 0), 0);   // eb / es = 只对强化普攻 / 强化战技''', '''(x[1] === "es" && key === "s2") || (x[1] === "sb" && key === "sb")) ? num(x[2]) : 0), 0);   // eb / es = 只对强化普攻 / 强化战技；sb = 只算超击破''')
F.rep('''key: brk ? "k" : "d", n: r.k''', '''key: brk ? (r.why === "sbk" ? "sb" : "k") : "d", n: r.k''')
F.rep('''f: "f", m: "m", e: "e", e2: "e", d: "d", k: "k" };''', '''f: "f", m: "m", e: "e", e2: "e", d: "d", k: "k", sb: "k" };''')
F.rep('''["d", "持续伤害"], ["k", "击破伤害"]];''', '''["d", "持续伤害"], ["k", "击破伤害"], ["sb", "只算超击破"]];''')
F.rep('''const DBM = [["be", "击破特攻 %"], ''', '''const DBM = [["be", "击破特攻 %"], ["bkd", "造成的击破伤害提高 %"], ''')
F.rep('''be: "击破特攻", bef: "击破效率",''', '''be: "击破特攻", bkd: "击破伤害提高", bef: "击破效率",''')
s0 = F.s.count('["break", "弱点击破时"]')
F.s = F.s.replace('["break", "弱点击破时"]', '["break", "弱点击破时"], ["wkAdd", "为敌人添加弱点时"]').replace('["break", "弱点击破"]', '["break", "弱点击破"], ["wkAdd", "为敌人添加弱点时"]', 1)
assert s0 == 2
F.rep('''    if (e.tgE) h.push(`只给能量上限 ≥${e.tgE} 的目标`);''', '''    if (e.tgE) h.push(`只给能量上限 ≥${e.tgE} 的目标`);
    if (e.brkSelf) h.push("只算自己击破的");
    if (e.mBe != null) h.push(`击破特攻 ≥${e.mBe}% 时`);
    if (e.mAtk != null) h.push(`攻击力 ≥${e.mAtk} 时`);
    if (e.eWl) h.push(`${num(e.eWn) > 1 ? `至少 ${e.eWn} 个敌人` : "主目标"}有${e.eWl === "self" ? "对应属性" : e.eWl + "属性"}弱点时`);
    if (e.eDk) h.push(`主目标有${[].concat(e.eDk).map(k => k === "own" ? "自己挂的持续伤害" : k).join(" / ")}时`);
    if (e.eBr) h.push("主目标处于弱点击破状态时");
    if (e.uPk) h.push("终结技对我方施放时");
    if (e.ec) h.push("出手时按主目标的状态算");''')

# ================= 光锥 =================
def upd(e, n=None, **k):
    e.pop('off', None); e.update(k)
    if n: e['n'] = n
    return e
# 20017 开疆
hasl(20017, '当装备者击破敌方目标的弱点时，回复等同于自身生命上限#1[i]%的生命值')
upd(LE(20017, '公司'), '公司：装备者击破敌方目标的弱点时，回复自身生命上限 12% 的生命值', bby=1)
# 21008 猎物的视线
hasl(21008, '同时造成的持续伤害提高#2[i]%')
L[21008]['eff'].append(D(m='dmg', sc='d', v=col(21008, 1), bk='lc', n='光锥：造成的持续伤害提高'))
# 21016 宇宙市场趋势
hasl(21016, '当装备者受到攻击后，有#2[i]%的基础概率使敌方目标陷入灼烧状态，每回合造成等同于装备者#3[i]%防御力的持续伤害，持续#4[i]回合')
L[21016]['eff'].append(dict(y='dot', t='hit', tg='efirst', dk='灼烧', v=col(21016, 2), ss='def', d=2, bk='lc', n='光锥：受到攻击后使敌方目标陷入灼烧，每回合造成装备者防御力 40% 的持续伤害，持续 2 回合（按第一个敌人；基础概率按命中）'))
# 21022 延长记号 / 21026 汪！散步时间！
hasl(21022, '对处于触电或风化状态的敌方目标造成的伤害提高#2[i]%，该效果对持续伤害也会生效')
upd(LE(21022, '触电或风化'), '光锥：对处于触电或风化状态的敌方目标造成的伤害提高（含持续伤害；按主目标当时的状态）', ec={'dk': ['触电', '风化']})
hasl(21026, '对处于灼烧或裂伤状态的敌方目标造成的伤害提高#2[i]%，该效果对持续伤害也会生效')
upd(LE(21026, '灼烧或裂伤'), '光锥：对处于灼烧或裂伤状态的敌方目标造成的伤害提高（含持续伤害；按主目标当时的状态）', ec={'dk': ['灼烧', '裂伤']})
# 21040 银河沦陷日
hasl(21040, '若有不少于#3[i]个被攻击的敌方目标具有对应属性弱点，装备者的暴击伤害提高#2[i]%')
upd(LE(21040, '对应弱点'), '光锥：施放攻击后，若有至少 2 个敌方目标具有装备者属性的弱点，暴击伤害提高，持续 2 回合（按场上敌人算，不看这次打到了几个）', ewl='self', ewn=2)
# 21047 黑夜如影随行
hasl(21047, '进入战斗时或造成击破伤害后，速度提高#2[i]%，持续#3[i]回合，该效果每回合只可触发1次')
LE(21047, '隐匿').update(bk='lc')
L[21047]['eff'].append(dict(y='spd', m='pct', d=2, tg='self', t='break', bby=1, ptn=1, bk='lc', v=col(21047, 1), n='隐匿：装备者击破敌方弱点（造成击破伤害）后速度提高，持续 2 回合，每回合只可触发 1 次'))
# 21048 梦的蒙太奇
hasl(21048, '攻击处于弱点击破状态下的敌方目标后，恢复#2[i]点能量，该效果每回合最多触发#3[i]次')
e = LE(21048, '学院式剪接'); e.clear(); e.update(y='energy', m='er', t='atk', aw='self', tg='self', ebr=1, ac=2, v=col(21048, 1, False), n='学院式剪接：攻击处于弱点击破状态下的敌方目标后恢复能量，每回合最多 2 次（按主目标；要放带韧性的敌人）')
L[21048]['notes'] = [n for n in L[21048].get('notes', []) if '学院式剪接' not in n]
# 21056 追逐风的时候
hasl(21056, '进入战斗后，使我方全体造成的击破伤害提高#1[i]%')
L[21056]['eff'].append(D(tg='team', m='bkd', v=col(21056, 0), bk='lc', n='光锥：进入战斗后我方全体造成的击破伤害提高（同类技能无法重复生效）'))
# 22004 宇宙大生意
hasl(22004, '敌方目标每拥有1个不同属性的弱点，装备者对其造成的伤害提高#2[i]%，最多计入7个')
upd(LE(22004, '每有 1 种弱点'), '光锥：敌方目标每有 1 种不同属性的弱点，装备者对其造成的伤害提高，最多 7 种（按主目标当时的弱点；没有弱点资料时按 1 种）', ec={'wc': 7})
# 23006 只需等待
hasl(23006, '【游丝】状态下，敌方目标每回合开始时受到等同于装备者#1[i]%攻击力的雷属性持续伤害，持续#5[i]回合')
L[23006]['eff'].append(dict(y='dot', t='atk', aw='self', tg='efirst', m='new', dk='游丝', v=col(23006, 0), d=1, bk='ys', n='光锥【游丝】：击中不处于【游丝】的敌方目标时使其陷入【游丝】（视为触电），回合开始时受到装备者攻击力 60% 的雷属性持续伤害，持续 1 回合（按主目标）'))
# 23019 镜中故我
hasl(23019, '并且若装备者击破特攻大于等于#4[i]%，则恢复1个战技点')
upd(LE(23019, '恢复 1 个战技点'), '彻骨梅香：施放终结技后，若击破特攻 ≥150% 恢复 1 个战技点（按卡片击破特攻 + 战斗中的加成）', mbe=150)
# 23022 重塑时光之忆
hasl(23022, '每层【先知】使装备者的攻击力提高#2[i]%，造成的持续伤害无视目标#3[i]%的防御力')
for k in ('风化', '灼烧', '触电', '裂伤'):
    L[23022]['eff'] += [dict(y='dbuf', t='atk', aw='self', tg='self', m='atkP', v=col(23022, 1), st=4, d=0, bk='xz', edk=[k], first=1, n='光锥【先知】：对陷入%s的敌方目标造成伤害时获得 1 层（每种状态每场 1 次），每层攻击力提高（按主目标）' % k),
                        dict(y='dbuf', t='atk', aw='self', tg='self', m='defIg', sc='d', v=col(23022, 2), st=4, d=0, bk='xz2', edk=[k], first=1, n='光锥【先知】（%s）：每层造成的持续伤害无视目标防御力' % k)]
# 23025 梦应归于何处
hasl(23025, '【溃败】状态下目标受到装备者造成的击破伤害提高#2[i]%，速度降低#3[i]%')
upd(LE(23025, '溃败'), '光锥【溃败】：装备者造成击破伤害（击破弱点）时目标速度降低 20%，持续 2 回合', bby=1)
L[23025]['eff'].append(dict(y='dbuf', t='break', bby=1, tg='self', m='bkd', v=col(23025, 1), d=2, bk='kb2', n='光锥【溃败】：目标受到装备者造成的击破伤害提高（这里按装备者造成的击破伤害提高算，对所有敌人生效；2 回合按装备者的回合）'))
# 23027 驶向第二次生命
hasl(23027, '造成的击破伤害无视目标#3[i]%的防御力。当装备者在战斗中击破特攻大于等于#2[i]%时，速度提高#4[i]%')
L[23027]['eff'].append(D(m='defIg', sc='k', v=col(23027, 2), bk='lc', n='光锥：造成的击破伤害无视目标防御力'))
upd(LE(23027, '苦航'), '苦航：战斗中击破特攻 ≥150% 时速度提高（按战斗开始时的击破特攻）', mbe=150)
# 23029 那无数个春天
hasl(23029, '若目标处于装备者施加的持续伤害状态，则有#5[i]%的基础概率将装备者施加的【卸甲】状态升级成【穷寇】状态')
upd(LE(23029, '穷寇'), '光锥【穷寇】：目标处于装备者施加的持续伤害状态时，受到的伤害额外提高（按主目标；基础概率按命中）', edk=['own'])
# 23032 唯有香如故
hasl(23032, '若装备者当前击破特攻大于等于#3[i]%，受到的伤害提高效果额外提高#4[i]%')
LE(23032, '忘忧').update(n='光锥【忘忧】：终结技攻击后敌人受到的伤害提高，持续 2 回合')
L[23032]['eff'].append(dict(y='dbuf', t='ult', tg='enemies', m='vuln', v=col(23032, 3), d=2, bk='lc2', mbe=150, n='光锥【忘忧】：装备者击破特攻 ≥150% 时受到的伤害额外提高'))
# 23035 长路终有归途
hasl(23035, '当有敌方目标的弱点被击破时，有#2[i]%的基础概率使其陷入【焚灼】状态，受到的击破伤害提高#3[i]%，持续#4[i]回合，此效果可叠加#5[i]层')
L[23035]['eff'].append(dict(y='dbuf', t='break', tg='evt', m='vuln', sc='k', v=col(23035, 2), st=2, d=2, bk='lc', n='光锥【焚灼】：敌方目标的弱点被击破时，受到的击破伤害提高，持续 2 回合，可叠加 2 层'))
# 23041 生命当付之一炬
hasl(23041, '若敌方目标拥有装备者添加的弱点，装备者对其造成的伤害提高#3[i]%')
upd(LE(23041, '对有装备者添加弱点'), '光锥：敌方目标拥有装备者添加的弱点时，装备者对其造成的伤害提高（按主目标当时的状态）', ec={'wb': 1})
# 23047 海洋为何而歌
hasl(23047, '受到我方目标攻击时，使攻击者速度提高#6[i]%，持续#7[i]回合')
upd(LE(23047, '独奏'), '光锥【魂迷】：处于【魂迷】的敌人受到我方攻击时攻击者速度提高，持续 3 回合（按主目标身上有装备者挂的持续伤害时算【魂迷】）', edk=['own'])
L[23047]['notes'] = L[23047].get('notes', []) + ['【魂迷】“每有 1 个装备者施加的负面效果受到的持续伤害提高 5%”没做']
# 23050 勿忘她的火焰
hasl(23050, '进入战斗时，使装备者和另一位开战的队友造成的击破伤害提高#2[i]%')
L[23050]['eff'] += [D(m='bkd', v=col(23050, 1), bk='lc', n='光锥：进入战斗时装备者造成的击破伤害提高'),
                    D(tg='$ally', m='bkd', v=col(23050, 1), bk='lc', n='光锥：进入战斗时另一位开战的队友造成的击破伤害提高（默认第一个队友，可改目标）')]
upd(LE(23050, '恢复 1 个战技点'), '光锥：装备者为敌方目标添加弱点时恢复 1 个战技点（最多 1 次，施放终结技时重置）', t='wkAdd')
# 24000 记一位星神的陨落
hasl(24000, '当装备者击破敌方目标弱点后，造成的伤害提高#3[i]%')
upd(LE(24000, '击破弱点后'), '光锥：装备者击破敌方目标弱点后伤害提高，持续 2 回合', bby=1)
# 24003 孤独的疗愈
hasl(24003, '当装备者施放终结技时，使装备者造成的持续伤害提高#2[i]%，持续#3[i]回合')
L[24003]['eff'].append(dict(y='dbuf', t='ult', tg='self', m='dmg', sc='d', v=col(24003, 1), d=2, bk='lc', n='光锥：施放终结技时造成的持续伤害提高，持续 2 回合'))

# ================= 遗器 =================
hasr(108, 1, '若目标拥有量子属性弱点，额外无视其10%的防御力')
upd(RE(108, 'p4', '量子弱点'), '4件：目标有量子属性弱点时额外无视 10% 防御力（按主目标）', ec={'wl': '量'})
hasr(111, 1, '当装备者击破敌方目标弱点后，恢复3点能量')
upd(RE(111, 'p4', '恢复 3 点能量'), '4件：装备者击破敌方目标弱点后恢复 3 点能量', bby=1)
hasr(116, 1, '敌方目标每承受1个持续伤害效果，装备者对其造成伤害时就无视其6%的防御力，最多计入3个持续伤害效果')
upd(RE(116, 'p4', '持续伤害'), '4件：敌方目标每承受 1 个持续伤害效果，无视其 6% 防御力，最多 3 个（按主目标当时的状态）', v=6, ec={'dn': 3})
hasr(118, 1, '当装备者对我方目标施放终结技时，我方全体击破特攻提高30%，持续2回合，该效果无法叠加')
R[118]['p4']['eff'].append(dict(y='dbuf', t='ult', upk=1, tg='team', m='be', v=30, d=2, bk='wm', n='4件：装备者对我方目标施放终结技时，我方全体击破特攻提高 30%，持续 2 回合（终结技有我方目标的效果才算）'))
hasr(119, 1, '当装备者的击破特攻大于等于150%时，对敌方目标造成的击破伤害无视其10%的防御力。当装备者的击破特攻大于等于250%时，对敌方目标造成的超击破伤害额外无视其15%的防御力')
R[119]['p4']['eff'] += [D(m='defIg', sc='k', v=10, ec={'be': 150}, bk='r', n='4件：击破特攻 ≥150% 时造成的击破伤害无视目标 10% 防御力（出手时按击破特攻判断）'),
                        D(m='defIg', sc='sb', v=15, ec={'be': 250}, bk='r2', n='4件：击破特攻 ≥250% 时造成的超击破伤害额外无视目标 15% 防御力')]
hasr(307, 0, '当装备者的速度大于等于145时，击破特攻额外提高20%')
R[307]['p2']['eff'].append(D(m='be', v=20, ms=145, bk='r', n='2件：速度 ≥145 时击破特攻额外提高 20%（按战斗开始时的速度；面板击破特攻里已经算进去就关掉）'))
hasr(316, 0, '当装备者击中拥有火属性弱点的敌方目标时，击破特攻提高40%，持续1回合')
R[316]['p2']['eff'].append(dict(y='dbuf', t='atk', aw='self', tg='self', m='be', v=40, d=1, ewl='火', bk='r', n='2件：击中拥有火属性弱点的敌方目标时击破特攻提高 40%，持续 1 回合（按主目标）'))
hasr(322, 0, '当装备者的攻击力大于等于2400/3600时，使造成的持续伤害额外提高12%/24%')
R[322]['p2']['eff'] += [D(m='dmg', sc='d', v=12, mat=2400, bk='r', n='2件：攻击力 ≥2400 时造成的持续伤害额外提高 12%（按卡片面板攻击力）'),
                        D(m='dmg', sc='d', v=12, mat=3600, bk='r2', n='2件：攻击力 ≥3600 时再提高 12%（共 24%）')]

F.finish('击破 / 持续伤害相关的光锥和遗器', '''<li><b>2026-11-11（击破 / 持续伤害相关的光锥和遗器）</b>：tv 76（tools/fix76.py）。以前页面不算击破，这些光锥 / 遗器的条件只能手动开，现在按模拟里的状态自动判断（条件按主目标 = 第一个敌人）。<b>光锥</b>：开疆、流星追迹的怪盗、记一位星神的陨落、黑夜如影随行、梦应归于何处只算自己击破的；梦的蒙太奇（打破韧的敌人回能）、镜中故我 / 驶向第二次生命 / 唯有香如故（击破特攻 ≥150%）、银河沦陷日（≥2 个敌人有对应弱点）、延长记号 / 汪！散步时间！（目标有触电 / 风化、灼烧 / 裂伤）、宇宙大生意（按弱点种数）、生命当付之一炬（目标有自己加的弱点）、那无数个春天【穷寇】、海洋为何而歌（攻击者加速）自动判断；新加：猎物的视线 / 孤独的疗愈的持续伤害提高、宇宙市场趋势被攻击后灼烧、只需等待【游丝】、重塑时光之忆【先知】、追逐风的时候 / 勿忘她的火焰的击破伤害提高（勿忘她的火焰添加弱点回战技点也自动了）、驶向第二次生命无视防御、长路终有归途【焚灼】。<b>遗器</b>：繁星璀璨的天才（量子弱点）、幽锁深牢的系囚（按持续伤害个数）自动判断；新加：机心戏梦的钟表匠 4 件、荡除蠹灾的铁骑 4 件、盗贼公国塔利亚（速度 ≥145）、劫火莲灯铸炼宫、沉欢醉饮的海隅。<b>对已有配置</b>：装备了这些光锥 / 遗器的卡片会换成新效果；没放敌人卡时，看敌人状态的条件都不成立（以前手动打开的这类效果会变成不生效），梦的蒙太奇改成打破韧敌人才回能，行动顺序可能变。</li>''',
'''2026-11-11：击破 / 持续伤害相关的光锥 23 个、遗器 8 套 —— tv 76（tools/fix76.py）。新：触发条件 bby / mbe / mat / ewl / ewn / edk / ebr / upk，伤害增益 ec、类型 bkd、范围 sb、触发 wkAdd。
  未改 / 存疑：条件都按主目标（第一个敌人）判断，群攻里其他目标不单独算；“造成的击破伤害提高”单独一个乘区（和受到的击破伤害提高分开相乘，是否和其他增伤同区原文没写）；梦应归于何处【溃败】的易伤按装备者造成的击破伤害提高算、对所有敌人生效；只需等待【游丝】、宇宙市场趋势的灼烧按第一个敌人；海洋为何而歌【魂迷】的持续伤害易伤、晚安与睡颜按负面效果个数没做；钟表匠 / 追逐风“无法叠加”没判断（两件同时装会叠）；驶向第二次生命的速度、塔利亚按战斗开始时判断。''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX76); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX76); for (const u of s.units) if (u.kind === "ally" && !u.sm && (u.lc || u.rA || u.rB || u.rP)) applyEquip(u); } finally { S = keep; } }   // 光锥 / 遗器改了：带装备的卡片都重建装备效果')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
