"""tv 87：敌人身上的减益按实际被打的敌人挂；多目标伤害按每个敌人自己的减益 / 击破状态算。
用法：python3 tools/fix87.py index.html <官方 json 目录>
引擎：
- 新目标 ehit = 这次攻击击中的敌人（按削韧表 TGH[角色][动作] = [主目标, 全体, 相邻] 推断；没有数据时按敌方全体）。
  当前出手的单位和动作记在 atkCtx（回合开始 / 行动 / 开大 / 追加攻击 / 欢愉技 / 秘技施放 / 攻击结算时设置）。
- 伤害增益（dbuf）挂在敌人身上时按目标解析（efirst / eadj / ehit / evt 只挂在这些敌人身上；enemies 仍是全体）。
- 敌方减益快照 edbSnap(en)：按主目标（第一个还在的敌人）或记录里的那个敌人；行动 / 开大 / 追击 / 欢愉技另存 eAll（每个敌人的减益和击破状态）。
- dmgCalc：扩散 / 群攻 / 弹射按 eAll 把每个敌人的防御区 × 抗性区 × 易伤区 × 击破区加权（主目标 = v + rnd，相邻 = adj，群攻其他 = v），
  总伤害 × (加权平均 / 主目标)；返回 tw（每个敌人分到的比例），“我方伤害扣敌人生命值”按它分。
- 模板：触发是攻击类（普攻 / 强化普攻 / 战技 / 终结技 / 追加攻击 / 攻击后）、目标写“敌方全体”的减益里，说明没写“全体 / 结界 / 每个 / 其他敌人”的改成 ehit。"""
import sys, json, re
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 87, sys.argv[2])
C = F.C

# ================= 引擎：目标 =================
F.rep('''      if (target === "lowsh") {''', '''      if (target === "ehit") return hitEns();   // 这次攻击击中的敌人（按削韧表推断；没有数据时按敌方全体）
      if (target === "lowsh") {''')
F.rep('''    let actSeq = 0;''', '''    let actSeq = 0, atkCtx = null;   // atkCtx：当前出手的我方单位和动作键（ehit 目标用）
    const hitEns = () => {
      const ens = U.filter(z => z.kind === "enemy" && !z.gone); if (!ens.length || !atkCtx || !atkCtx.u) return ens;
      const who = atkCtx.u, o = ownerOf(who) || who, T0 = o.kind === "ally" ? tplOf(o) : null; let key = who.sm ? "m" : atkCtx.k;
      if ((key === "s" || key === "u") && T0 && !who.sm) { try { const f = (key === "s" ? S2ST : U2ST)[String(T0.id)]; if (f && f({ sts: curRec && curRec.uid === o.id && Array.isArray(curRec.sts) ? curRec.sts : o.st ? Object.keys(o.st).filter(k => o.st[k]) : [], mIn: U.some(x => x.sm && x.sm.owner === o.id && x.sm.mem && !x.gone) })) key += "2"; } catch (e) {} }
      const tb = T0 && key ? (TGH[T0.id] || {})[key] : null; if (!tb) return ens;
      return ens.filter((z, i) => i === 0 ? num(tb[0]) > 0 || num(tb[1]) > 0 : num(tb[1]) > 0 || (i <= 2 && num(tb[2]) > 0));   // [主目标, 全体, 相邻]；相邻 = 第 2、3 个敌人
    };''')
F.rep('''    const atkAct = (who, fromFua, act) => { nxUse(who, fromFua ? "f" : ACT2K[act] || "m");''', '''    const atkAct = (who, fromFua, act) => { atkCtx = { u: who, k: fromFua ? "f" : ACT2K[act] || "m" }; nxUse(who, fromFua ? "f" : ACT2K[act] || "m");''')
F.rep('''      actor.turns++; turnSeq++; ntSeq++; actSeq++;''', '''      actor.turns++; turnSeq++; ntSeq++; actSeq++; atkCtx = actor.kind === "ally" && actor.sm ? { u: actor, k: "m" } : null;''')
F.rep('''    const onAction = (u, type) => {''', '''    const onAction = (u, type) => {
      atkCtx = { u, k: ACT2K[type] || "b" };''')
F.rep('''    const castOther = (u, why) => {
      actSeq++;''', '''    const castOther = (u, why) => {
      actSeq++; atkCtx = { u, k: "u" };''')
F.rep('''    const castUlt = where => {
      actSeq++;''', '''    const castUlt = where => {
      actSeq++; atkCtx = { u: swU, k: "u" };''')
F.rep('''    const castAct = (u, k, src) => {
      actSeq++;''', '''    const castAct = (u, k, src) => {
      actSeq++; atkCtx = u ? { u, k: ACT2K[k] || "s" } : atkCtx;''')
F.rep('''        actSeq++;
        if (se > 0 && !u.punchAt)''', '''        actSeq++; atkCtx = { u, k: "e" };
        if (se > 0 && !u.punchAt)''')
F.rep('''    const doFua = (u, color, why, as) => {
      if (!u || u.kind !== "ally" || u.gone || isCd(u) || fuaDepth >= 4) return;
      actSeq++;''', '''    const doFua = (...a) => { const p = atkCtx; try { return doFua0(...a); } finally { atkCtx = p; } };   // 追加攻击结束后恢复外面那次行动的 atkCtx
    const doFua0 = (u, color, why, as) => {
      if (!u || u.kind !== "ally" || u.gone || isCd(u) || fuaDepth >= 4) return;
      actSeq++; atkCtx = { u, k: "f" };''')
# 敌人身上的伤害增益按目标解析
F.rep('''      let tgs = teamT ? [TEAM0] : onEnemy ? (U.filter(u => u.kind === "enemy")) :''', '''      let tgs = teamT ? [TEAM0] : onEnemy ? (eff.target === "enemies" || !["efirst", "eadj", "ehit", "evt"].includes(eff.target) ? U.filter(u => u.kind === "enemy") : resolve(eff.target, src).filter(u => u && u.kind === "enemy")) :''')
F.rep('''const onEnemy = ["vuln", "defRed", "resRed", "wkn"].includes(eff.mode) || eff.target === "enemies";''', '''const onEnemy = ["vuln", "defRed", "resRed", "wkn"].includes(eff.mode) || ["enemies", "ehit", "efirst", "eadj"].includes(eff.target);''')
# ================= 引擎：敌方减益快照 =================
F.rep('''    const edbSnap = () => {
      const all = [...U.filter(u => u.kind === "enemy"), EV0].map(u => dbSnap(u)).filter(x => x.length);
      if (all.length <= 1) return all[0] || [];
      const sum = l => l.reduce((p, x) => p + x[2], 0);
      return all.sort((a, b) => sum(b) - sum(a))[0];
    };''', '''    const edbSnap = en => {   // 敌方减益：按指定的敌人，没指定按主目标（第一个还在的敌人）；没放敌人卡按虚拟的“敌人”
      const z = en && en.kind === "enemy" ? en : U.find(u => u.kind === "enemy" && !u.gone);
      return z ? dbSnap(z) : dbSnap(EV0);
    };
    const edbAll = () => {   // 每个敌人的减益和击破状态（多目标伤害按每个敌人算）
      const ens = U.filter(u => u.kind === "enemy" && !u.gone); if (ens.length < 2) return undefined;
      return { ord: ens.map(z => z.id), m: Object.fromEntries(ens.map(z => [z.id, dbSnap(z)])), bk: Object.fromEntries(ens.map(z => [z.id, toughMax(z) > 0 ? !!z.broken : null])) };
    };''')
lines = F.s.split('\n'); n1 = n2 = 0
for i, L in enumerate(lines):
    if 'edb: edbSnap()' not in L: continue
    m = re.search(r'\ben: (\w+)(?:\.id| \? \1\.id : null)', L)
    if m: lines[i] = L.replace('edb: edbSnap()', 'edb: edbSnap(%s)' % m.group(1)); n1 += 1
    else: lines[i] = L.replace('edb: edbSnap()', 'edb: edbSnap(), eAll: edbAll()'); n2 += 1
F.s = "\n".join(lines); print("edb 按敌人", n1, "多目标", n2); assert n1 + n2 == 11 and n2 == 3, (n1, n2)
F.rep('''    const reSnap = (rec, a) => { if (!a) return; rec.db = dbSnap(a); rec.edb = edbSnap();''', '''    const reSnap = (rec, a) => { if (!a) return; rec.db = dbSnap(a); rec.edb = edbSnap(); rec.eAll = edbAll();''')
F.rep('''      rec.db = dbSnap(a); rec.edb = edbSnap(); rec.pAt = pool;''', '''      rec.db = dbSnap(a); rec.edb = edbSnap(); rec.eAll = edbAll(); rec.pAt = pool;''')
F.rep('''um.edb = edbSnap();''', '''um.edb = edbSnap(); um.eAll = edbAll();''')
# ================= 伤害层：多目标按每个敌人 =================
F.rep('''    const mainDmg = base * mult * elM * dmgM * critM * defM * resM * vulnM * toughM * ev1M;''', '''    // 多目标：按每个敌人自己的减益 / 击破状态加权（主目标 v + rnd，相邻 adj，群攻其他 v），总伤害乘“加权平均 / 主目标”
    let adjF = 1, tw = null;
    const EA = rec && rec.eAll;
    if (EA && EA.ord && EA.ord.length > 1 && (nAll > 1 || nAdj > 0) && !e.dot && !e.brk) {
      const gOf = (id, i) => {
        const L = EA.m[id] || [], L1 = L.some(x => x[3]) ? L.filter(x => !x[3] || x[3].includes(EL1)) : L, E2 = st => dsum(L1, st, e.key);
        const dM = 100 / (100 + (enemyLevel() + 20) * Math.max(0, 1 - (num(cfg.defR) + E2("defRed")) / 100 - defI / 100));
        const rM = Math.min(2, Math.max(0.1, 1 - (res - num(cfg.pen) - D("resPen") - spkPen - E2("resRed")) / 100));
        const vM = 1 + (num(cfg.vuln) + E2("vuln") + (inWx ? 20 : 0)) / 100;
        const bk = i === 0 ? (rec.ebk != null ? rec.ebk : cfg.broken) : (EA.bk[id] != null ? EA.bk[id] : cfg.broken);
        return dM * rM * vM * (bk ? 1 : 0.9);
      };
      const W = [];
      EA.ord.forEach((id, i) => { const w = i === 0 ? e.v + e.rnd : e.tg === 3 ? e.v : e.tg === 2 ? (i <= nAdj ? e.adj : 0) : e.tg === 4 ? e.adj : 0; if (w > 0) W.push([id, w, gOf(id, i)]); });
      const sw = W.reduce((p, x) => p + x[1], 0), sg = W.reduce((p, x) => p + x[1] * x[2], 0), g0 = W.length ? gOf(EA.ord[0], 0) : 0;
      if (sw > 0 && sg > 0 && g0 > 0) { adjF = sg / (sw * g0); tw = W.map(x => [x[0], x[1] * x[2] / sg]); }
    }
    const mainDmg = base * mult * elM * dmgM * critM * defM * resM * vulnM * toughM * ev1M * adjF;''')
F.rep('''      mult, multOne: e.v + e.rnd, v: e.v, adj: e.adj, rnd: e.rnd, adjN: nAdj, tg: e.tg, targets: nAll + nAdj, name: e.n, lv: e.lv, key: e.key };''',
      '''      mult, multOne: e.v + e.rnd, v: e.v, adj: e.adj, rnd: e.rnd, adjN: nAdj, tg: e.tg, targets: nAll + nAdj, name: e.n, lv: e.lv, key: e.key, adjF, tw };''')
F.rep('''        if (!(num(d.mult) > 0) || d.dot || d.brk) { hurtEnemy(main, d.total, killer); return; }''', '''        if (!(num(d.mult) > 0) || d.dot || d.brk) { hurtEnemy(main, d.total, killer); return; }
        if (Array.isArray(d.tw) && d.tw.length) { for (const [id, sh] of d.tw) { const z = byId[id] && !byId[id].gone ? byId[id] : main; hurtEnemy(z, d.total * sh, killer); } return; }   // 按每个敌人分到的比例''')

# ================= 模板：攻击类的减益改成挂在被打的敌人身上 =================
ATK = {'basic', 'ebasic', 'skill', 'ult', 'fua', 'atk'}
KEEP = re.compile(r'全体|结界|每个|其他敌人|领域|境界')
changed = []
def fix(where, e):
    if e.get('tg') != 'enemies' or e.get('y') not in ('dbuf', 'dot') or e.get('t') not in ATK: return False
    if e.get('y') == 'dbuf' and e.get('m') not in ('vuln', 'defRed', 'resRed', 'wkn'): return False
    if e.get('y') == 'dot' and e.get('m') in ('ext', 'new'): return False
    if KEEP.search(e.get('n', '')): return False
    if any(where.startswith(w) and e.get('n', '').startswith(n) for w, n in EXCL): return False   # 原文是敌方全体 / 每个单体，或不是攻击挂上的
    e['tg'] = 'ehit'; e['n'] = re.sub(r'（按敌方全体；?', '（', e['n']).replace('（）', '').replace('；页面按敌方全体', '').replace('（按敌方全体）', '')
    changed.append((where, e['n'][:60])); return True
EXCL = [('光锥 一场谎言的终幕', '光锥【影噬】'), ('光锥 谎言在风中飘扬', '光锥【失窃】'), ('大丽花', '终结技：【败谢】'), ('花火', '【强化版】终结技：【谜诡】'), ('花火 E1', 'E1 悬置怀疑'),
        ('千冶•刃', '终结技：【煞火缠身】'), ('流萤', '终结技：「完全燃烧」')]
touched = set()
for c in F.DB['chars']:
    for e in c['eff']:
        if fix(c['name'], e): touched.add(('b', c['id']))
    for r in c.get('eid', []):
        for e in r['eff']:
            if fix('%s E%d' % (c['name'], r['r']), e): touched.add(('e', c['id'], r['r']))
LCS = set()
for l in F.DB['lcs']:
    for e in l.get('eff', []):
        if fix('光锥 ' + l['name'], e): LCS.add(l['id'])
for r in F.DB['relics']:
    for p in ('p2', 'p4'):
        for e in r[p]['eff']: assert not fix('遗器 ' + r['name'], e)
F.has('140602', '有#6[i]%的基础概率使指定敌方单体及其相邻目标陷入虚弱状态')
z = [e for e in C[1406]['eff'] if e.get('m') == 'wkn']; assert len(z) == 1
z[0]['tg'] = 'ehit'; z[0]['n'] = '战技：指定敌方单体及其相邻目标陷入虚弱，造成的伤害降低 10%，持续 2 回合（按命中算）'; touched.add(('b', 1406)); changed.append(('赛飞儿', z[0]['n']))
for w, n in changed: print('  ehit', w, '|', n)
for t in sorted(touched, key=str):
    if t[0] == 'b': F.rebuild(t[1], C[t[1]]['eff'])
    else: F.eid(t[1], t[2])
# 姬子星火说明里的“按敌方全体”已去掉；赛飞儿
F.finish('减益挂在被打的敌人身上、多目标伤害按每个敌人算', '''<li><b>2026-11-11（减益按被打的敌人）</b>：tv 87（tools/fix87.py）。攻击附带的减益（易伤、减防、减抗、虚弱）和持续伤害，原来一律挂在敌方全体，现在只挂在这次攻击真正击中的敌人身上（按各技能的目标类型：单体只挂主目标，扩散挂主目标和相邻，群攻挂全体）：银狼战技、卡芙卡 1 魂、卢卡终结技、托帕【负债证明】、砂金 2 魂、佩拉 4 魂、黑天鹅战技 / 普攻、赛飞儿战技 / 2 魂、那刻夏 1 魂、波提欧【绝命对峙】、姬子星火、忘归人【狐祈】、椒丘【烬煨】，以及生命当付之一炬、唯有香如故、那无数个春天、命运从未公平、雨一直下、假日浴场大冒险、决心如汗珠般闪耀等光锥。写着“敌方全体”的照旧。<b>伤害</b>：扩散 / 群攻 / 弹射现在按每个敌人自己的减益和是否被击破分别算（主目标以外的敌人没有那个减益就少算），“我方伤害扣敌人生命值”也按每个敌人分到的伤害扣。对已有配置：多个敌人时，单体减益不再加到其他敌人身上，群攻 / 扩散的伤害可能比原来低。</li>''',
'''2026-11-11：减益按被打的敌人 —— tv 87（tools/fix87.py）。新：目标 ehit、atkCtx、edbSnap(en) / edbAll / rec.eAll、dmgCalc adjF / tw，onEnemy 增益按目标解析。
  未改 / 存疑：“相邻”按第 2、3 个敌人卡；弹射的随机段都算在主目标上；击中哪些敌人按削韧表推断（没有削韧数据的动作按敌方全体）；伤害显示里防御 / 抗性 / 易伤三个乘区写的是主目标的''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX87); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX87); for (const u of s.units) if (u.kind === "ally" && !u.sm && (' + ' || '.join('u.lc === %d' % i for i in sorted(LCS)) + ')) applyEquip(u); } finally { S = keep; } }   // 攻击类减益改挂被打的敌人的光锥')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok', sorted(LCS))
