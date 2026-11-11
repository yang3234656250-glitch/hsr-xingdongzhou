"""tv 79：姬子•启行 1510【助战技】—— 每个队友每次行动可以选择“用助战技”（角色卡上每次行动旁的“助”，或“有次数时都用”）。
用法：python3 tools/fix79.py index.html <官方 json 目录>；之后重跑 python3 tools/build_tgh.py index.html <官方目录> <敌人数据目录>（给助战技的削韧值）。
引擎：模板 x.sup = {st, hE, uE}（姬子•启行）：开局所有角色 1 次（上限 1，姬子•启行 E2 起 2）；效果类型 supR（恢复所有角色的次数到上限）；
持有 st（【领航旗语】）时，每个我方角色回合开始恢复 1 次（E2 再 1 次）；姬子•启行回合开始时次数 = 上限 → +hE 能量；
用助战技：在这个角色的回合开始、行动前；姬子•启行自己用不消耗次数，其他人消耗 1 次并恢复 uE 能量；记一条助战技伤害（R.dots，sup = DMG 的键 z / z2，按姬子•启行的面板和当时增益，会暴击）、
削韧（TGH 的 z / z2）、触发 aSup（队友触发：我方使用助战技时）。卡片字段 u.supAll（有次数时都用）、u.supOv[回合]（单独指定）。只做正常回合。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 79, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
SK = json.load(open(sys.argv[2] + '/character_skills.json', encoding='utf-8'))

# ================= 引擎 =================
F.rep('''    let brkBy = null, wkDepth = 0, wkEn = null;''', '''    let brkBy = null, wkDepth = 0, wkEn = null;
    // 姬子•启行【助战技】：每个角色的使用次数
    const SUP = (() => { const H = U.find(z => z.kind === "ally" && !z.sm && tx(z).sup); if (!H) return null;
      const S0 = { H, X: tx(H).sup, cap: num(H.eid) >= 2 ? 2 : 1, n: {} }; for (const z of U) if (z.kind === "ally" && !z.sm) S0.n[z.id] = 1; return S0; })();''')
F.rep('''        if (eff.type === "weak") {''', '''        if (eff.type === "supR") { if (SUP) for (const z of U) if (z.kind === "ally" && !z.sm) SUP.n[z.id] = SUP.cap; if (SUP && tg === src) addLog(`${src.name} 恢复所有助战技使用次数`, false, srcColor); continue; }   // 恢复所有角色的助战技次数
        if (eff.type === "weak") {''')
F.rep('''      if (actor.kind === "ally" && !actor.sm) { rec.act = actOf(actor, actor.turns, rec.ult); rec.nat = actOf.nat; }''',
'''      if (actor.kind === "ally" && !actor.sm) { rec.act = actOf(actor, actor.turns, rec.ult); rec.nat = actOf.nat; }
      if (SUP && actor.kind === "ally" && !actor.sm && !isCd(actor) && !actor.gone) {   // 姬子•启行【助战技】：回合开始、行动前
        const H = SUP.H, isH = actor === H, k = String(actor.turns);
        if (hasSt(H, String(SUP.X.st || "领航旗语"))) SUP.n[actor.id] = Math.min(SUP.cap, num(SUP.n[actor.id]) + 1 + (num(H.eid) >= 2 ? 1 : 0));   // 【领航旗语】：每个回合开始时恢复 1 次（E2 再 1 次）
        if (isH && num(SUP.X.hE) > 0 && num(SUP.n[H.id]) >= SUP.cap && hasEnergy(H)) { curWhy = "人类该向何处去（助战技次数满）"; addEnergy(H, num(SUP.X.hE), true); }
        const want = actor.supOv && actor.supOv[k] != null ? !!actor.supOv[k] : !!actor.supAll;
        if (want && !isH && !(num(SUP.n[actor.id]) > 0)) { rec.supNo = true; addLog(`${actor.name} 这回合想用助战技，但没有使用次数`, false, actor.color, actor.id); }
        else if (want) {
          if (!isH) SUP.n[actor.id]--;
          rec.sup = true;
          const zk = isH ? "z2" : "z", e0 = U.find(z => z.kind === "enemy" && !z.gone);
          const r = { t, uid: H.id, en: e0 ? e0.id : null, k: "助战技", sup: zk, db: dbSnap(H), edb: edbSnap(), seq: seq++, ebk: ebkNow() }; dotRecs.push(r);
          marks.push({ t, uid: actor.id, label: "助战技", color: H.color, from: actor.name });
          addLog(`${actor.name} 使用助战技（「拓星者」攻击）${isH ? "" : `，剩 ${SUP.n[actor.id]} 次`}`, false, H.color, actor.id); log[log.length - 1].dd = [r];
          if (!isH && hasEnergy(actor) && num(SUP.X.uE) > 0) { curWhy = "使用助战技"; addEnergy(actor, num(SUP.X.uE), true); }
          toughHit(H, zk);
          teamFire("aSup", actor);
        }
      }''')
F.rep('''    if (!r || !u || u.kind !== "ally") return null;
    if (r.__dmg !== undefined) return r.__dmg;''', '''    if (!r || !u || u.kind !== "ally") return null;
    if (r.__dmg !== undefined) return r.__dmg;
    if (r.sup) { const e = dmgEntry(u, r.sup); return (r.__dmg = e ? dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk }) : null); }   // 助战技：按姬子•启行当时的增益，会暴击''')
F.rep('''  const LVK = { b: "b", b2: "b", s: "s", s2: "s", u: "u", u2: "u", e: "u", e2: "u", f: "t" };''', '''  const LVK = { b: "b", b2: "b", s: "s", s2: "s", u: "u", u2: "u", e: "u", e2: "u", f: "t", z: "t", z2: "t" };''')
F.rep('''f: "f", m: "m", e: "e", e2: "e", d: "d", k: "k", sb: "k" };''', '''f: "f", m: "m", e: "e", e2: "e", d: "d", k: "k", sb: "k", z: "z", z2: "z" };''')
F.rep('''["k", "击破伤害"], ["sb", "只算超击破"]];''', '''["k", "击破伤害"], ["sb", "只算超击破"], ["z", "助战技"]];''')
F.rep('''  const TEAMT = ["ally", "atk", "aSk", "aUlt", "aFua", "aTurn", "hgive", "aHeal", "aGive", "eMax", "stEnd", "spUse", "spChg", "dotHit"];''',
      '''  const TEAMT = ["ally", "atk", "aSk", "aUlt", "aFua", "aTurn", "hgive", "aHeal", "aGive", "eMax", "stEnd", "spUse", "spChg", "dotHit", "wkAdd", "aSup"];''')
n0 = F.s.count('["wkAdd", "我方为敌人添加弱点时"]'); assert n0 == 3
F.s = F.s.replace('["wkAdd", "我方为敌人添加弱点时"]', '["wkAdd", "我方为敌人添加弱点时"], ["aSup", "我方使用助战技时"]')
F.rep('''    if (e.eBr) h.push("主目标处于弱点击破状态时");''', '''    if (e.eBr) h.push("主目标处于弱点击破状态时");
    if (e.type === "supR") h.push("恢复所有角色的助战技使用次数");''')
F.s = F.s.replace('["brkd", "造成一次击破伤害"], ["tfix", "直接削韧（点数）"], ', '["brkd", "造成一次击破伤害"], ["tfix", "直接削韧（点数）"], ["supR", "恢复助战技次数（姬子•启行）"], ', 1)
# 角色卡：有姬子•启行时的“助战技”选项
F.rep('''          ${u.elation ? `<label for="ed2-${u.id}">欢愉技 <select''', '''          ${hasSupT() ? `<label for="sa-${u.id}" title="姬子•启行的助战技：在这个角色的回合开始、行动前使用（姬子•启行自己用不消耗次数）。也可以在下面每次行动旁边单独勾“助”"><input type="checkbox" id="sa-${u.id}" ${u.supAll ? "checked" : ""} data-u="${i}" data-f="supAll">有次数时都用助战技</label>` : ""}
          ${u.elation ? `<label for="ed2-${u.id}">欢愉技 <select''')
F.rep('''  const actRowHtml = (u, i) => {''', '''  const hasSupT = () => S.units.some(z => z.kind === "ally" && !z.sm && (tplOf(z) || {}).x && tplOf(z).x.sup);   // 队伍里有姬子•启行（助战技）
  const actRowHtml = (u, i) => {''')
F.rep('''        return `<label class="ta${ov ? " ov" : ""}" title="${when}${ov ? "（单独指定过）" : ""}${a.nat === "fskill" ? "；战技* = 不耗战技点的战技" : ""}">${lab}<select data-tact="${i}" data-k="${k}" data-nat="${a.nat || ""}" aria-label="${when}的行动">${opt(opts, a.act)}</select></label>`;''',
'''        const sw = sup && !a.extra ? `<label class="ta-sup${a.sup ? " on" : a.supNo ? " no" : ""}" title="${when}：${a.sup ? "用了助战技" : a.supNo ? "想用助战技但没有次数" : "不用助战技"}（勾上 = 这回合行动前用助战技）"><input type="checkbox" data-tsup="${i}" data-k="${k}" ${a.sup || a.supNo ? "checked" : ""}>助</label>` : "";
        return `<span class="ta-wrap"><label class="ta${ov ? " ov" : ""}" title="${when}${ov ? "（单独指定过）" : ""}${a.nat === "fskill" ? "；战技* = 不耗战技点的战技" : ""}">${lab}<select data-tact="${i}" data-k="${k}" data-nat="${a.nat || ""}" aria-label="${when}的行动">${opt(opts, a.act)}</select></label>${sw}</span>`;''')
F.rep('''      box.innerHTML = `<span class="hint">每次行动：</span>` + acts.map(a => {''', '''      const sup = hasSupT();
      box.innerHTML = `<span class="hint">每次行动：</span>` + acts.map(a => {''')
F.rep('''    if (t.dataset.tact !== undefined) {''', '''    if (t.dataset.tsup !== undefined) {   // 这回合用不用助战技：和“有次数时都用”一样就删掉单独指定
      const u = S.units[+t.dataset.tsup], k = t.dataset.k;
      u.supOv = Object.assign({}, u.supOv);
      if (t.checked === !!u.supAll) delete u.supOv[k]; else u.supOv[k] = t.checked;
      if (!Object.keys(u.supOv).length) delete u.supOv;
      update(); return;
    }
    if (t.dataset.tact !== undefined) {''')
F.rep('''.unit.fold .sec-t{ display:none; }
''', '''.unit.fold .sec-t{ display:none; }
.ta-wrap{ display:inline-flex; align-items:center; gap:2px; }
.ta-sup{ display:inline-flex; align-items:center; gap:2px; font-size:10.5px; color:var(--muted); cursor:pointer; padding:0 2px; }
.ta-sup input{ margin:0; width:12px; height:12px; accent-color:var(--gold); }
.ta-sup.on{ color:var(--gold); }
.ta-sup.no{ color:var(--enemy); }
''')

# ================= 倍率表：助战技 =================
p = SK['151022']['params']; assert len(p) == 15 and r4(p[9][0]) == 1.6 and p[9][1] == 3 and r4(p[9][2]) == 0.24 and r4(p[9][3]) == 2 and p[9][4] == 4 and r4(p[9][5]) == 0.32
has('151022', '对敌方全体造成等同于姬子•启行#1[i]%攻击力的火属性伤害，额外造成#2[i]次伤害，每次伤害对敌方随机单体造成等同于姬子•启行#3[i]%攻击力的火属性伤害。姬子•启行使用时，对敌方全体造成等同于姬子•启行#4[i]%攻击力的火属性伤害，额外造成#5[i]次伤害')
F.DMG['1510']['z'] = {'v': [r4(x[0]) for x in p], 'adj': [], 'rnd': [r4(x[1] * x[2]) for x in p], 'tg': 3, 'el': 0, 'stat': 'atk', 'n': '开拓，与你同行', 'max': 15}
F.DMG['1510']['z2'] = {'v': [r4(x[3]) for x in p], 'adj': [], 'rnd': [r4(x[4] * x[5]) for x in p], 'tg': 3, 'el': 0, 'stat': 'atk', 'n': '开拓，与你同行（姬子•启行使用）', 'max': 15}

# ================= 姬子•启行模板 =================
c = C[1510]
has('151002', '施放战技后立即恢复所有助战技使用次数'); has('151004', '除姬子•启行外的我方角色使用助战技时，会使其恢复#3[i]点能量')
hast(1510, '人类该向何处去', '姬子•启行使用助战技不消耗助战技使用次数。回合开始时，若当前助战技使用次数等于当前使用次数上限，姬子•启行额外恢复#1[i]点能量')
assert prm('151004', 10)[2] == 4 and F.TR['1510101']['params'][0] == [5]
eff = [e for e in c['eff'] if not (e.get('n') or '').startswith('行迹人类该向何处去')]
old_tr = [n for n, t in F.OLD[1510] if n and n.startswith('行迹人类该向何处去')]
eff.insert(2, dict(y='supR', t='skill', tg='self', v=0, n='战技：施放后立即恢复所有角色的助战技使用次数'))
c['notes'] = [n for n in c.get('notes', []) if not n.startswith('天赋：除姬子•启行外的我方角色使用助战技时')] + [
    '助战技：每个角色卡上“每次行动”旁边勾“助”（或勾“有次数时都用助战技”），在那个角色的回合开始、行动前使用。开局每人 1 次（E2 起上限 2），姬子•启行自己用不消耗；其他人用了恢复 4 点能量；持有【领航旗语】时每个我方回合开始恢复 1 次（E2 2 次）；姬子•启行回合开始时次数满就恢复 5 点能量（行迹人类该向何处去）',
    '助战技伤害按姬子•启行的面板和当时的增益算（其他人用 160% 全体 + 3×24% 弹射，姬子•启行自己用 200% + 4×32%）；同行协议的额外助战技、行迹列车的脉搏在轰鸣的额外回合、E1 多 1 次弹射还没做']
F.rebuild(1510, eff, x={'sup': {'st': '领航旗语', 'hE': 5, 'uE': 4}})
e2 = F.eid(1510, 2); e2['eff'] = e2.get('eff', []) + [dict(y='dbuf', t='start', tg='self', m='xtra', v=30, sc='z', d=0, bk='e2z', n='E2：助战技造成的伤害为原伤害的 130%')]
for e in e2['eff']:
    if e.get('bk') == 'e2' and e.get('m') == 'xtra': e['n'] = 'E2：终结技伤害为原伤害的 130%'
e6 = F.eid(1510, 6); e6['eff'] = e6.get('eff', []) + [dict(y='dbuf', t='start', tg='self', m='dmg', v=75, sc='z', d=0, bk='e6z', n='E6：助战技造成的伤害提高 75%')]

# ================= 当一颗星照亮夜空 =================
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8'))
F.has(LR['23060']['desc'], '当装备者施放助战技时，恢复#2[i]点能量并获得【启航】，持续2回合，最多叠加#3[i]层。每层【启航】使助战技伤害提高#4[i]%')
P = LR['23060']['params']; assert [x[1] for x in P] == [6] * 5 and [x[2] for x in P] == [3] * 5
L = {x['id']: x for x in F.DB['lcs']}
L[23060]['eff'][0]['n'] = '光锥：造成伤害时无视目标防御力'
L[23060]['eff'] += [dict(y='energy', t='aSup', aw='all', tg='self', m='er', v=6, n='光锥初愿：施放助战技时恢复 6 点能量（任何角色用助战技都算姬子•启行施放）'),
                    dict(y='dbuf', t='aSup', aw='all', tg='self', m='dmg', sc='z', v=[r4(x[3] * 100) for x in P], st=3, d=2, bk='qh', n='光锥【启航】：每层助战技伤害提高，持续 2 回合，最多 3 层')]
L[23060]['notes'] = ['【启航】达到 3 层时每层终结技伤害提高还没做']

F.finish('姬子•启行【助战技】', '''<li><b>2026-11-11（姬子•启行【助战技】）</b>：tv 79（tools/fix79.py）。队伍里有姬子•启行时，每张角色卡的“每次行动”旁边多了一个“助”，勾上 = 那个回合行动前用一次助战技；也可以勾“有次数时都用助战技”。按原文：开局每人 1 次（E2 起上限 2），姬子•启行施放战技恢复所有人的次数，持有【领航旗语】时每个我方回合开始恢复 1 次（E2 2 次），姬子•启行自己用不消耗次数；其他人用了恢复 4 点能量；姬子•启行回合开始时次数满就恢复 5 点能量（行迹人类该向何处去，以前要手动开）。助战技的伤害（按姬子•启行的面板）、削韧都算；“我方使用助战技时”可以做效果的触发，当一颗星照亮夜空的回能和【启航】已接上；E2、E6 的助战技伤害加成也加了。没勾“助”的方案不变。还没做：同行协议的额外助战技、开拓同行角色的额外回合、E1 多 1 次弹射。</li>''',
'''2026-11-11：姬子•启行（1510）【助战技】—— tv 79（tools/fix79.py）。新：x.sup、效果类型 supR、触发 aSup、卡片 supAll / supOv、DMG 的 z / z2。
  未改 / 存疑：只在正常回合使用（额外回合不行）；行迹人类该向何处去的“次数满”按姬子•启行自己的次数；当一颗星照亮夜空按任何人用助战技都算装备者施放；AvatarSkillConfig 里助战技 SPBase 18（使用者回能？原文没写）没加；【领航旗语】“每个回合开始时”只算我方角色的回合。''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX79); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX79); for (const u of s.units) if (u.kind === "ally" && !u.sm && u.lc === 23060) applyEquip(u); } finally { S = keep; } }   // 当一颗星照亮夜空改了')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
