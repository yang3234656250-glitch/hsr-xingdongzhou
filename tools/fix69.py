"""tv 69：击破第 2 步（超击破、弱点击破效率、无视弱点削韧、添加弱点、击破伤害效果、【云火昭】）+ 阮•梅 1303、同谐主 8005 / 8006、忘归人 1225、
流萤 1310、乱破 1317、加拉赫 1301、波提欧 1315、银狼 1006 的击破相关效果。用法：python3 tools/fix69.py index.html <官方 json 目录>
引擎：
- 伤害增益类型（挂在我方）：bef 弱点击破效率 %、befU 只对没破韧的目标的击破效率 %、tig 无视弱点属性削韧（原削韧值的 X%，取最大不叠加）、
  sbk 超击破倍率 %（攻击已破韧的目标后把削韧值转成超击破）、sbkU 超击破伤害提高 %、sbkA 没破韧时也转超击破；范围 dsc 照常（eb / es / u …）。
- 伤害增益字段 ven = [1 个敌人, 2, 3, 4, 5 个以上] 按敌人卡数量取数值。
- 效果类型 weak（给敌人添加弱点：wel = 属性字 / self 施放者属性 / first 编队第一位的属性 / all，d = 敌人回合数）、
  brkd（造成一次击破伤害：v% 的击破伤害，vcn = 按施放者计数取值，tcap = 计入的韧性上限封顶，nb = 目标没破韧也打，mb = 主目标破韧了才打）。
- 模板 x.sbk = {st, th: [[击破特攻, 倍率], …]}（有状态且击破特攻达标时的超击破）、x.tghCnt = [键, 每层 %]（计数每层让这个动作削韧值提高）、x.exT = 敌人额外韧性 %（云火昭）。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 69, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
def lvE(cid, base):
    for r in range(1, 7):
        for z in (F.RK[str(cid * 100 + r)].get('level_up_skills') or []):
            if str(z.get('id')) == str(base): return r
    raise KeyError(base)

# ================= 引擎 =================
# 1) 削韧：击破效率、无视弱点、添加的弱点、超击破、云火昭
F.rep('''      const el = ELW[T0.elem] || "";
      U.filter(x => x.kind === "enemy" && !x.gone).forEach((en, i) => {
        const mx = toughMax(en); if (!(mx > 0) || en.broken) return;
        const m = monOf(en); if (m && m.w && el && !m.w.includes(el)) return;   // 不是弱点属性：不削韧
        const amt = num(v[1]) + (i === 0 ? num(v[0]) : i <= 2 ? num(v[2]) : 0); if (!(amt > 0)) return;
        if (en.tcur == null) en.tcur = mx;
        en.tcur -= amt;
        if (en.tcur <= 1e-9) doBreak(en, o, el || "物", mx);
      });
    };''', '''      const el = ELW[T0.elem] || "", X = T0.x || {};
      // 这次攻击吃到的增益：普通行动用“施放时”记下的快照（结印这类在行动后结束的状态也算得到），开大用开大时的
      const um = key === "u" || key === "u2" ? ultMarks[ultMarks.length - 1] : null;
      const snap = um && um.uid === o.id && um.db ? um.db : key !== "f" && curRec && curRec.uid === o.id && curRec.db ? curRec.db : dbSnap(o);
      const ok = z => !z[1] || z[1] === SCK[key] || (z[1] === "eb" && key === "b2") || (z[1] === "es" && key === "s2");
      const ds = st => snap.reduce((p, z) => p + (z[0] === st && ok(z) ? num(z[2]) : 0), 0), dm = st => snap.reduce((p, z) => z[0] === st && ok(z) ? Math.max(p, num(z[2])) : p, 0);
      const bef = ds("bef"), befU = ds("befU"), tig = Math.min(100, dm("tig")), sbA = ds("sbkA") > 0;
      let sbk = ds("sbk") * (1 + ds("sbkU") / 100);   // “超击破伤害提高”只乘增益给的超击破（同谐主卫我起舞）
      if (X.sbk && Array.isArray(X.sbk.th) && (!X.sbk.st || hasSt(o, String(X.sbk.st)))) { const be = num(o.be) + dsum(snap, "be", "k"); let q = 0; for (const z of X.sbk.th) if (be >= num(z[0]) - 1e-9) q = Math.max(q, num(z[1])); sbk += q; }   // 击破特攻达标时的超击破（流萤）
      const cUp = Array.isArray(X.tghCnt) && X.tghCnt[0] === key ? 1 + num(X.tghCnt[1]) * num(o.cnt) / 100 : 1;   // 计数每层让这个动作的削韧值提高（波提欧优势口袋）
      U.filter(x => x.kind === "enemy" && !x.gone).forEach((en, i) => {
        const mx = toughMax(en); if (!(mx > 0)) return;
        const m = monOf(en), weak = !el || !m || !m.w || m.w.includes(el) || (en.wk || []).some(z => z.el === el || z.el === "all");
        const base = num(v[1]) + (i === 0 ? num(v[0]) : i <= 2 ? num(v[2]) : 0); if (!(base > 0)) return;
        const was = !!en.broken;
        const amt = base * cUp * (1 + (bef + (was ? 0 : befU)) / 100) * (weak ? 1 : tig / 100); if (!(amt > 0)) return;   // 不是弱点属性：只有“无视弱点属性削韧”才削
        if (!was) {
          if (en.tcur == null) en.tcur = mx;
          en.tcur -= amt;
          if (en.tcur <= 1e-9) doBreak(en, o, el || "物", mx);
        } else if (num(en.yh) > 0) {   // 【云火昭】：破韧后继续削，削完再受一次弱点击破伤害
          en.yh -= amt;
          if (en.yh <= 1e-9) { en.yh = 0; const r = { t, uid: o.id, en: en.id, k: "击破", mult: BRKM[el || "物"] * (0.5 + mx / 120), stat: "brk", why: "break", db: dbSnap(o), edb: edbSnap(), defIg: 0, seq: seq++, ebk: true }; dotRecs.push(r);
            addLog(`${o.name} 削完 ${en.name} 的【云火昭】：再次造成弱点击破伤害`, false, o.color); log[log.length - 1].dd = [r]; }
        }
        if (sbk > 0 && (was || sbA)) {   // 超击破：这次攻击的削韧值（每 10 点韧性 = 这里的 30）× 倍率
          const r = { t, uid: o.id, en: en.id, k: "超击破", mult: amt / 30 * sbk / 100, stat: "brk", why: "sbk", db: snap, edb: edbSnap(), defIg: 0, seq: seq++, ebk: !!en.broken }; dotRecs.push(r);
          addLog(`${o.name} 对 ${en.name} 造成超击破伤害（削韧 ${fmt(amt / 3, 1)} 点 × ${fmt(sbk, 1)}%）`, false, o.color); log[log.length - 1].dd = [r];
        }
      });
    };''')
F.rep('''      en.tcur = 0; en.broken = true;
''', '''      en.tcur = 0; en.broken = true;
      { let q = 0; for (const z of U) if (z.kind === "ally" && !z.sm && !z.gone) q = Math.max(q, num(tx(z).exT)); en.yh = q > 0 ? mx * q / 100 : 0; }   // 忘归人在场：额外附上韧性上限 X% 的【云火昭】
''')
F.rep('''        if (actor.broken) { actor.broken = false; actor.tcur = toughMax(actor);''', '''        if (actor.wk && actor.wk.length) { for (const z of actor.wk) z.left--; actor.wk = actor.wk.filter(z => z.left > 0); }   // 添加的弱点：按敌人自己的回合数
        if (actor.broken) { actor.broken = false; actor.yh = 0; actor.tcur = toughMax(actor);''')
# 2) 新效果类型：weak / brkd
F.rep('''        if (eff.type === "dotd") {   // 直接造成一次持续伤害类的伤害''', '''        if (eff.type === "weak") {   // 给敌人添加弱点（wel：属性字 / self / first / all；同一个人的同一组 bk 只留最新的）
          const own = src ? (ownerOf(src) || src) : null; if (!own || tg.kind !== "enemy") continue;
          const f1 = U.find(z => z.kind === "ally" && !z.sm && tplOf(z));
          const wl = eff.wel === "self" ? ELW[(tplOf(own) || {}).elem] : eff.wel === "first" ? ELW[(tplOf(f1) || {}).elem] : eff.wel; if (!wl) continue;
          const key = own.id + ":" + (eff.bk || eff.id), dur = Math.max(0, Math.round(num(eff.duration)));
          tg.wk = (tg.wk || []).filter(z => z.key !== key); tg.wk.push({ key, el: wl, left: dur > 0 ? dur : Infinity });
          if (brkOn && toughMax(tg) > 0) addLog(`${src.name} 给 ${tg.name} 添加${wl === "all" ? "全属性" : wl + "属性"}弱点${dur > 0 ? `（${dur} 回合）` : ""}`, false, srcColor);
          continue;
        }
        if (eff.type === "brkd") {   // 造成一次击破伤害（v% 的击破伤害；默认只打已破韧的目标）
          const own = src ? (ownerOf(src) || src) : null; if (!own || tg.kind !== "enemy" || !brkOn) continue;
          const mx = toughMax(tg); if (!(mx > 0) || (!eff.noBk && !tg.broken)) continue;
          if (eff.mainBk) { const e0 = U.find(z => z.kind === "enemy" && !z.gone); if (!e0 || !e0.broken) continue; }   // 主目标破韧了才打（波提欧 E6 的相邻目标）
          const vv = Array.isArray(eff.vcn) ? num(eff.vcn[Math.min(eff.vcn.length, Math.round(num(own.cnt))) - 1]) : v; if (!(vv > 0)) continue;
          const wl = ELW[(tplOf(own) || {}).elem] || "物", mxe = num(eff.tcap) > 0 ? Math.min(mx, num(eff.tcap)) : mx;
          const r = { t, uid: own.id, en: tg.id, k: "击破伤害", mult: BRKM[wl] * (0.5 + mxe / 120) * vv / 100, stat: "brk", why: "brkd", db: dbSnap(own), edb: edbSnap(), defIg: 0, seq: seq++, ebk: !!tg.broken }; dotRecs.push(r);
          addLog(`${src.name} 对 ${tg.name} 造成 ${fmt(vv, 1)}% ${wl}属性击破伤害的击破伤害`, false, srcColor); log[log.length - 1].dd = [r];
          continue;
        }
        if (eff.type === "dotd") {   // 直接造成一次持续伤害类的伤害''')
F.rep('''      const amt0 = dbAmt(eff, src, v);
      if (eff.clr && v === 0 && bk) {''', '''      const amt0 = Array.isArray(eff.vEn) ? num(eff.vEn[Math.min(eff.vEn.length, Math.max(1, U.filter(z => z.kind === "enemy" && !z.gone).length)) - 1]) : dbAmt(eff, src, v);   // vEn：按敌人数量取值（同谐主卫我起舞）
      if (eff.clr && v === 0 && bk) {''')
F.rep('''      if (x.dk) e.dk = x.dk; if (x.vps != null) e.vps = x.vps;''', '''      if (x.wel) e.wel = x.wel; if (x.vcn) e.vcn = x.vcn; if (x.tcap) e.tcap = x.tcap; if (x.nb) e.noBk = 1; if (x.mb) e.mainBk = 1; if (x.ven) e.vEn = x.ven;   // 添加弱点 / 击破伤害 / 按敌人数量取值
      if (x.dk) e.dk = x.dk; if (x.vps != null) e.vps = x.vps;''')
# 3) 界面文字
F.rep('''["dotd", "造成一次持续伤害"], ''', '''["dotd", "造成一次持续伤害"], ["weak", "给敌人添加弱点"], ["brkd", "造成一次击破伤害"], ''')
F.rep('''const DBM = [["be", "击破特攻 %"], ''', '''const DBM = [["be", "击破特攻 %"], ["bef", "弱点击破效率 %"], ["befU", "弱点击破效率 %（目标没破韧时）"], ["tig", "无视弱点属性削韧（原削韧值的 X%）"], ["sbk", "超击破倍率 %"], ["sbkU", "超击破伤害提高 %"], ["sbkA", "没破韧时削韧值也转超击破"], ''')
F.rep('''be: "击破特攻", vuln: "受到伤害提高"''', '''be: "击破特攻", bef: "击破效率", befU: "击破效率（未破韧）", tig: "无视弱点削韧", sbk: "超击破倍率", sbkU: "超击破伤害提高", sbkA: "未破韧也转超击破", vuln: "受到伤害提高"''')

D = lambda **k: dict(dict(y='dbuf', d=0), **k)

# ================= 阮•梅 =================
c = C[1303]
has('130302', '弱点击破效率提高#2[i]%'); hast(1303, '物体呼吸中', '我方全体击破特攻提高#1[i]%'); has('130304', '阮•梅对其造成等同于自身#2[f1]%冰属性击破伤害的击破伤害')
has('r:130304', '阮•梅自身击破特攻提高100%，持续3回合'); has('r:130306', '天赋造成的击破伤害倍率额外提高200%')
et = lvE(1303, 130304); t10, t12 = prm('130304', 10), prm('130304', 12); assert r4(t10[1]) == 1.2 and r4(t12[1]) == 1.32 and prm('130302', 10)[1] == 0.5 and et < 6
new = list(c['eff']) + [
    D(t='skill', tg='team', m='bef', v=50, bk='st:弦外音', n='战技：阮•梅拥有【弦外音】时我方全体弱点击破效率 +50%'),
    D(t='start', tg='team', m='be', v=20, bk='wt', n='行迹物体呼吸中：我方全体击破特攻 +20%（队友面板上看不到，这里加）'),
    dict(y='brkd', t='break', tg='evt', v=120, lv=[et, 132], xe=6, n='天赋：我方击破敌方目标弱点时，阮•梅对其造成 120%% 冰属性击破伤害的击破伤害（%d 魂 132%%）' % et),
]
F.rebuild(1303, new)
e4 = F.eid(1303, 4); e4['eff'] = e4.get('eff', []) + [D(t='break', tg='self', m='be', v=100, d=3, bk='e4', n='E4：敌方目标的弱点被击破时，阮•梅自身击破特攻 +100%，持续 3 回合')]
e6 = F.eid(1303, 6); e6['eff'] = e6.get('eff', []) + [dict(y='brkd', t='break', tg='evt', v=332, n='E6：天赋的击破伤害倍率额外 +200%（共 332% 冰属性击破伤害）')]

# ================= 同谐主 =================
for cid in (8005, 8006):
    c = C[cid]; u = str(cid * 100 + 3)
    has(u, '持有【伴舞】的我方目标击破特攻提高#3[i]%'); has(u, '会将本次攻击的削韧值转化为1次超击破伤害'); has(u, '开拓者每回合开始时持续回合数减1')
    hast(cid, '卫我起舞', '【伴舞】效果触发的超击破伤害提高#1[i]%/#2[i]%/#3[i]%/#4[i]%/#5[i]%')
    eu = lvE(cid, cid * 100 + 3); u10, u12 = prm(u, 10), prm(u, 12); assert u10[0] == 3 and r4(u10[2]) == 0.3 and r4(u12[2]) == 0.33
    assert F.TR[str(cid * 1000 + 101)]['params'][0] == [0.2, 0.3, 0.4, 0.5, 0.6]
    new = list(c['eff']) + [
        dict(y='state', t='ult', tg='self', sn='伴舞', v=1, d=3, ts=1, n='终结技：为我方全体附上【伴舞】，持续 3 回合（开拓者每回合开始时 −1）'),
        D(t='ult', tg='team', m='be', v=30, lv=[eu, 33], bk='st:伴舞', n='终结技：持有【伴舞】的我方目标击破特攻 +30%%（%d 魂 33%%）' % eu),
        D(t='ult', tg='team', m='sbk', v=100, bk='st:伴舞', n='终结技：持有【伴舞】的我方目标攻击弱点击破状态的敌人后，把本次攻击的削韧值转化为 1 次超击破伤害'),
        D(t='ult', tg='team', m='sbkU', v=60, ven=[60, 50, 40, 30, 20], bk='st:伴舞', n='行迹卫我起舞：敌方目标 1 / 2 / 3 / 4 / 5 名以上时【伴舞】的超击破伤害 +60% / 50% / 40% / 30% / 20%（按敌人卡数量）'),
    ]
    F.rebuild(cid, new, notes=['行迹随波逐流（战技第一次伤害的削韧值 +100%）、秘技、E4 还没做'])

# ================= 忘归人 =================
c = C[1225]
has('122502', '击破特攻提高#2[i]%，攻击没有对应属性弱点的敌人也能削减韧性，效果等同于原削韧值的#6[i]%'); has('122503', '本次攻击无视弱点属性削减敌方全体的韧性')
has('122504', '额外附上等同于自身韧性上限#2[i]%的【云火昭】'); has('122504', '会将本次攻击的削韧值转化为1次#1[i]%的超击破伤害')
hast(1225, '涂山玄设', '使自身击破特攻提高#1[i]%'); hast(1225, '玑星太素', '使除自身以外的队友击破特攻提高#1[i]%')
has('r:122501', '持有【狐祈】的我方目标，弱点击破效率提高50%'); has('r:122506', '忘归人的弱点击破效率提高50%')
es, et = lvE(1225, 122502), lvE(1225, 122504); s10, s12, t10, t12 = prm('122502', 10), prm('122502', 12), prm('122504', 10), prm('122504', 12)
assert r4(s10[1]) == 0.3 and r4(s12[1]) == 0.33 and s10[5] == 0.5 and t10 == [1, 0.4] and r4(t12[0]) == 1.1
for e in c['eff']:
    if e.get('sn') == '狐祈': e['n'] = '战技：使指定我方单体获得【狐祈】（卡片上“每次战技目标”选的队友）'
old_hq = [n for n, t in F.OLD[1225] if n and n.startswith('战技：使指定我方单体获得【狐祈】')][0]
new = list(c['eff']) + [
    D(t='skill', tg='skpick', m='be', v=30, lv=[es, 33], mv=1, bk='hq', n='战技：持有【狐祈】的我方目标击破特攻 +30%%（%d 魂 33%%）' % es),
    D(t='skill', tg='skpick', m='tig', v=50, mv=1, bk='hq', n='战技：持有【狐祈】的我方目标攻击没有对应属性弱点的敌人也能削韧，等同于原削韧值的 50%（不和其他无视弱点削韧叠加）'),
    D(t='start', tg='self', m='tig', v=100, sc='u', bk='ult', n='终结技：本次攻击无视弱点属性削减敌方全体的韧性'),
    D(t='start', tg='team', m='sbk', v=100, lv=[et, 110], bk='tf', n='天赋：忘归人在场时，我方攻击弱点击破状态的敌人后，把本次攻击的削韧值转化为 1 次 100%% 的超击破伤害（%d 魂 110%%）' % et),
    D(t='start', tg='self', m='be', v=30, bk='ts', n='行迹涂山玄设：自身击破特攻 +30%（面板里已经算进去的话关掉）'),
    D(t='break', tg='others', m='be', v=6, st=2, d=2, bk='jx', n='行迹玑星太素：敌方目标弱点被击破时，其他队友击破特攻 +6%，持续 2 回合，最多 2 层（忘归人击破特攻 ≥220% 时每层 18%，自己改数值）'),
]
F.rebuild(1225, new, rename={old_hq: '战技：使指定我方单体获得【狐祈】（卡片上“每次战技目标”选的队友）'}, x={'exT': 40})
e1 = F.eid(1225, 1); e1['eff'] = e1.get('eff', []) + [D(t='skill', tg='skpick', m='bef', v=50, mv=1, bk='hq', n='E1：持有【狐祈】的我方目标弱点击破效率 +50%')]
e6 = F.eid(1225, 6); e6['eff'] = e6.get('eff', []) + [D(t='start', tg='self', m='bef', v=50, bk='e6', n='E6：忘归人的弱点击破效率 +50%')]

# ================= 流萤（强化版） =================
c = C[1310]
has('1131003', '施放强化普攻、强化战技时自身弱点击破效率提高#2[i]%、使敌方目标受到装甲「萨姆」造成的击破伤害提高#1[f1]%'); has('1131009', '为指定敌方单体及其相邻目标添加火属性弱点，持续2回合')
assert F.TR['11310101']['params'][0][0] == 0.25 and F.TR['11310102']['params'][0] == [1.5, 3, 1, 1.5]
has('r:131006', '施放强化普攻、强化战技时弱点击破效率提高50%')
eu = lvE(1310, 131003); u10, u12 = prm('1131003', 10), prm('1131003', 12); assert r4(u10[0]) == 0.2 and r4(u12[0]) == 0.22 and u10[1] == 0.5
new = list(c['eff']) + [
    D(t='ult', tg='self', m='bef', v=50, sc='eb', bk='st:完全燃烧#b', n='终结技：「完全燃烧」状态下施放强化普攻时自身弱点击破效率 +50%'),
    D(t='ult', tg='self', m='bef', v=50, sc='es', bk='st:完全燃烧#s', n='终结技：「完全燃烧」状态下施放强化战技时自身弱点击破效率 +50%'),
    D(t='ult', tg='enemies', m='vuln', v=20, lv=[eu, 22], sc='k', bk='st:完全燃烧#v', n='终结技：「完全燃烧」状态下敌方目标受到的击破伤害 +20%%（%d 魂 22%%；原文只算装甲「萨姆」强化普攻 / 强化战技造成的，这里对「完全燃烧」期间所有击破伤害都算）' % eu),
    D(t='ult', tg='self', m='be', v=25, bk='st:完全燃烧#be', n='【强化版】行迹α模组-偏时迸发：「完全燃烧」状态下击破特攻 +25%'),
    dict(y='weak', t='skill', tg='efirst', wel='火', d=2, bk='wk', ns='完全燃烧', n='【强化版】强化战技：为指定敌方单体添加火属性弱点，持续 2 回合'),
    dict(y='weak', t='skill', tg='eadj', wel='火', d=2, bk='wk', ns='完全燃烧', n='【强化版】强化战技：为相邻目标添加火属性弱点，持续 2 回合'),
    dict(y='weak', t='start', tg='enemies', wel='火', d=2, bk='wk', off=1, n='秘技Δ指令-焦土陨击：进入战斗后为敌方全体添加火属性弱点，持续 2 回合（用了秘技再启用）'),
]
F.rebuild(1310, new, x={'sbk': {'st': '完全燃烧', 'th': [[150, 100], [300, 150]]}},
          notes=['【强化版】行迹β模组-自限装甲：「完全燃烧」状态下击破特攻 ≥150% / 300% 时，攻击弱点击破状态的敌人后把削韧值转化为 100% / 150% 的超击破伤害（按卡片上的击破特攻 + 战斗中的加成自动判断）',
                 '行迹γ模组-过载核心（攻击力高于 1800 的部分每 10 点 +0.8% 击破特攻）不自动换算，请把换算后的击破特攻填在卡片上'])
e6 = F.eid(1310, 6); e6['eff'] = e6.get('eff', []) + [
    D(t='ult', tg='self', m='bef', v=50, sc='eb', bk='st:完全燃烧#e6b', n='E6：施放强化普攻时弱点击破效率 +50%'),
    D(t='ult', tg='self', m='bef', v=50, sc='es', bk='st:完全燃烧#e6s', n='E6：施放强化战技时弱点击破效率 +50%')]

# ================= 乱破 =================
c = C[1317]
has('131703', '同时弱点击破效率提高#1[i]%，击破特攻提高#2[i]%'); has('131718', '攻击没有虚数弱点的敌人也可以削减韧性，效果等同于原削韧值的#4[i]%')
hast(1317, '忍法帖•海鸣', '会将本次伤害的削韧值转化为1次#1[i]%的超击破伤害')
eu = lvE(1317, 131703); u10, u12 = prm('131703', 10), prm('131703', 12); assert u10[0] == 0.5 and r4(u10[1]) == 0.3 and r4(u12[1]) == 0.34 and prm('131718', 6)[3] == 0.5
new = list(c['eff']) + [
    D(t='ult', tg='self', m='bef', v=50, bk='st:结印', n='终结技：【结印】状态期间弱点击破效率 +50%'),
    D(t='ult', tg='self', m='be', v=30, lv=[eu, 34], bk='st:结印#be', n='终结技：【结印】状态期间击破特攻 +30%%（%d 魂 34%%）' % eu),
    D(t='start', tg='self', m='tig', v=50, sc='eb', bk='eb', n='强化普攻【忍具•降魔花弁】：攻击没有虚数弱点的敌人也可以削韧，等同于原削韧值的 50%'),
    D(t='ult', tg='self', m='sbk', v=60, sc='eb', bk='st:结印#sb', n='行迹忍法帖•海鸣：【结印】状态期间强化普攻对弱点击破状态的敌人造成伤害后，把削韧值转化为 1 次 60% 的超击破伤害'),
]
for e in c['eff']:
    if '击破用手动事件触发，需要时启用' in (e.get('n') or '') and e.get('t') == 'break': e['n'] = e['n'].replace('；击破用手动事件触发，需要时启用', '；按敌人都是精英及以上算，打小怪时关掉'); e.pop('off', None)
old_mt = [n for n, t in F.OLD[1317] if n and n.startswith('行迹忍法帖•魔天')][0]
F.rebuild(1317, new, rename={old_mt: [e['n'] for e in c['eff'] if (e.get('n') or '').startswith('行迹忍法帖•魔天')][0]},
          notes=['强化普攻【忍具•降魔花弁】三段分别恢复 5 / 5 / 10 点能量，共 20 点', '天赋的充能（敌方弱点被击破 +1，最多 10 点）和第 3 段的额外击破伤害、行迹忍法帖•枯叶（击破后受到的击破伤害提高）、E2、E6 还没做'])

# ================= 加拉赫 =================
c = C[1301]
has('130104', '【酩酊】使目标受到的击破伤害提高#1[f1]%'); has('r:130106', '加拉赫的击破特攻提高20%，弱点击破效率提高20%')
et = lvE(1301, 130104); assert r4(prm('130104', 10)[0]) == 0.12 and r4(prm('130104', 12)[0]) == 0.132
ZM = lambda **k: D(**dict(dict(tg='enemies', m='vuln', sc='k', v=12, lv=[et, 13.2], bk='zm'), **k))
new = list(c['eff']) + [
    ZM(t='ult', d=2, xe=4, n='天赋：【酩酊】使目标受到的击破伤害 +12%%（%d 魂 13.2%%），跟终结技的【酩酊】持续 2 回合' % et),
    ZM(t='start', d=2, off=1, n='秘技亲启佳酿：进入战斗后的【酩酊】同样使目标受到的击破伤害 +12%（用了秘技再启用）'),
]
F.rebuild(1301, new)
e4 = F.eid(1301, 4); e4['eff'] = e4.get('eff', []) + [ZM(t='ult', d=3, n='E4：【酩酊】延长 1 回合，受到的击破伤害提高也持续 3 回合')]
e6 = F.eid(1301, 6); e6['eff'] = e6.get('eff', []) + [D(t='start', tg='self', m='be', v=20, bk='e6', n='E6 血与沙：击破特攻 +20%'), D(t='start', tg='self', m='bef', v=20, bk='e6', n='E6 血与沙：弱点击破效率 +20%')]

# ================= 波提欧 =================
c = C[1315]
has('131503', '为指定敌方单体添加物理弱点，持续#3[i]回合'); has('131504', '每层【优势口袋】使强化普攻的削韧值提高#4[i]%'); has('131504', '该伤害计入的韧性上限不超过普攻【蹄铁裂颅】基础削韧值的#6[i]倍')
has('r:131502', '击破特攻提高30%，持续2回合'); has('r:131506', '对目标额外造成等同于原伤害倍率40%的击破伤害，对相邻目标额外造成等同于原伤害倍率70%的击破伤害')
et = lvE(1315, 131504); t10, t12 = prm('131504', 10), prm('131504', 12); assert [r4(v) for v in t10] == [0.7, 1.2, 1.7, 0.5, 3, 16] and [r4(v) for v in t12[:3]] == [0.77, 1.32, 1.87] and prm('131503', 10)[2] == 2
assert '"1315":{"b":[30,0,0]' in F.s
V0, V1 = [70, 120, 170], [77, 132, 187]
BK = lambda **k: dict(dict(y='brkd', t='ebasic', tg='efirst', tcap=480), **k)
eff = list(c['eff']); i = next(j for j, e in enumerate(eff) if e.get('y') == 'force' and e.get('t') == 'break')
eff[i:i] = [D(t='break', o='kill', ew='any', ns='绝命对峙', tg='self', m='be', v=30, d=2, bk='e2', me=2, n='E2：处于【绝命对峙】并获得【优势口袋】时击破特攻 +30%，持续 2 回合（2 魂起）')]
for e in eff:
    if e.get('t') == 'break' and '击破 / 消灭用手动事件触发' in (e.get('n') or ''): e['n'] = e['n'].replace('；击破 / 消灭用手动事件触发', '；消灭用手动事件触发')
new = eff + [
    dict(y='weak', t='ult', tg='efirst', wel='物', d=2, bk='wk', n='终结技：为指定敌方单体添加物理弱点，持续 2 回合'),
    dict(y='weak', t='skill', tg='efirst', wel='物', d=2, bk='wk', first=1, off=1, n='秘技三乘九的微笑：下一次战斗首次施放战技时为目标添加物理弱点，持续 2 回合（用了秘技再启用）'),
    BK(vcn=V0, xe=et, n='天赋：施放强化普攻期间目标处于弱点击破状态时，按【优势口袋】1 / 2 / 3 层造成 70%% / 120%% / 170%% 物理属性击破伤害的击破伤害（%d 魂 77%% / 132%% / 187%%；计入的韧性上限不超过 160 点）' % et),
]
old_cnt = [n for n, t in F.OLD[1315] if n and '击破 / 消灭用手动事件触发' in n]
F.rebuild(1315, new, rename={n: n.replace('；击破 / 消灭用手动事件触发', '；消灭用手动事件触发') for n in old_cnt}, x={'tghCnt': ['b2', 50]},
          notes=['天赋：每层【优势口袋】使强化普攻的削韧值 +50%（已自动处理）', '行迹蛇之上行（减伤）不影响行动轴和伤害，没做'])
ee = F.eid(1315, et); ee['eff'] = ee.get('eff', []) + [BK(vcn=V1, n='E%d：天赋等级 +2，击破伤害倍率 77%% / 132%% / 187%%' % et)]
e6 = F.eid(1315, 6); e6['eff'] = e6.get('eff', []) + [
    BK(vcn=[r4(v * 0.4) for v in V1], n='E6：触发天赋造成击破伤害时，对目标额外造成原伤害倍率 40% 的击破伤害'),
    BK(tg='eadj', nb=1, mb=1, vcn=[r4(v * 0.7) for v in V1], n='E6：触发天赋造成击破伤害时，对相邻目标额外造成原伤害倍率 70% 的击破伤害')]

# ================= 银狼（强化版） =================
c = C[1006]
has('1100602', '添加1个场上我方目标持有属性的弱点（优先添加我方编队中的第一位角色持有属性的弱点）'); assert prm('1100602', 10)[2] == 3
F.rebuild(1006, list(c['eff']) + [dict(y='weak', t='skill', tg='efirst', wel='first', d=3, bk='wk', n='【强化版】战技：为指定敌方单体添加我方编队第一位角色属性的弱点，持续 3 回合（基础概率按命中算；只保留最新添加的）')])

F.finish('击破第 2 步（超击破、击破效率、无视弱点削韧、添加弱点）+ 阮•梅、同谐主、忘归人、流萤、乱破、加拉赫、波提欧、银狼', '''<li><b>2026-11-11（击破第 2 步：超击破、击破效率、无视弱点削韧、添加弱点）</b>：tv 69（tools/fix69.py）。① <b>超击破</b>：攻击已经破韧的敌人后，把这次攻击的削韧值转成超击破伤害（80 级击破基础值 × 削韧点数 ÷ 10 × 倍率 × (1 + 击破特攻)），记在日志和伤害里。② <b>弱点击破效率</b>、<b>无视弱点属性削韧</b>（不叠加，取最大）、<b>给敌人添加弱点</b>（按敌人自己的回合数消失）、<b>直接造成击破伤害</b>的效果，都可以在效果里自己加。③ 角色：<b>阮•梅</b>【弦外音】击破效率 +50%、行迹全队击破特攻 +20%、天赋击破时 120% 冰属性击破伤害（E6 332%）、E4 击破特攻 +100%；<b>同谐主</b>【伴舞】（3 回合，击破特攻 +30%、超击破 100%，卫我起舞按敌人数量 +20%～60%）；<b>忘归人</b>【狐祈】击破特攻 +30% 和 50% 无视弱点削韧、终结技无视弱点、全队 100% 超击破、【云火昭】（破韧后还有 40% 额外韧性，削完再受一次击破伤害）、行迹和 E1 / E6；<b>流萤</b>「完全燃烧」击破效率 +50%、击破特攻 +25%、受到击破伤害 +20%、强化战技添加火弱点、击破特攻 ≥150% / 300% 时 100% / 150% 超击破、E6；<b>乱破</b>【结印】击破效率 +50%、击破特攻 +30%、强化普攻 50% 无视弱点削韧和 60% 超击破；<b>加拉赫</b>【酩酊】受到击破伤害 +12%、E6；<b>波提欧</b>终结技添加物理弱点、【优势口袋】每层强化普攻削韧 +50%、天赋击破伤害（70% / 120% / 170%）、E2 击破特攻、E6；<b>银狼</b>战技添加编队第一位属性的弱点。对已有方案：手动添加的敌人没有韧性，结果不变；用了怪物库敌人的方案，这些角色在场时破韧会更快、多出超击破伤害。还没做：阮•梅【残梅绽】、乱破天赋充能和第 3 段击破伤害、同谐主随波逐流、忘归人 E4 / E6 全队狐祈、流萤攻击力换算击破特攻，以及大丽花、那刻夏、雪衣、飞霄、黄泉、灵砂等其余角色的击破相关效果。</li>''',
'''2026-11-11（击破第 2 步）：阮•梅（1303）、同谐主（8005 / 8006）、忘归人（1225）、流萤（1310）、乱破（1317）、加拉赫（1301）、波提欧（1315）、银狼（1006）的击破相关效果 —— tv 69（tools/fix69.py）。新：伤害增益类型 bef / befU / tig / sbk / sbkU / sbkA、字段 ven；效果类型 weak / brkd；模板 x.sbk / x.tghCnt / x.exT。
  未改 / 存疑：打出破韧的那一次攻击不算超击破（游戏里按每段伤害算，破韧之后的几段会算）；超击破用整次攻击的削韧值；同谐主卫我起舞的“超击破伤害提高”对所有增益给的超击破都乘（忘归人天赋的也会乘到）；流萤“受到击破伤害提高”对完全燃烧期间所有击破伤害都算；忘归人行迹涂山玄设的击破特攻 +30% 默认开（面板里已有就关）、玑星太素按 6%；【云火昭】削完后的击破伤害按攻击者属性、不附带击破效果；银狼添加弱点的抗性降低仍是原来的写法；阮•梅【残梅绽】、乱破天赋、同谐主随波逐流、忘归人 E4 / E6、击破伤害提高类（忘归人 E4）没做；大丽花、那刻夏、雪衣、飞霄、黄泉、灵砂、Archer E2、银狼LV.999 E6、遐蝶 E6、姬子•启行的击破相关效果下一批。''')
