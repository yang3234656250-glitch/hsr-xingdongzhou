"""tv 80：大黑塔 1401【解读】/【谜底】自动算；光锥时节不居 23013 的附加伤害；修正：击破伤害 / 固定数值伤害的基础值不再吃攻击力%加成。
用法：python3 tools/fix80.py index.html <官方 json 目录>
引擎：模板 x.jd = {max, wave, md}：敌人 en.jd（【解读】层数），大黑塔 HT.md（【谜底】）。进入战斗每个敌人 1 层、第一个敌人再 25 层（“随机、优先精英”按主目标）；
我方每次攻击按削韧表判断击中哪些敌人，每个 +1；队伍「智识」≥2 名时再给击中目标里层数最高的 +1（智识攻击者再 +2）；大黑塔战技主目标再 +1；
强化战技：记下主目标层数（E1 加相邻最高的 50%）到行动记录 jd / jd0 / jd2，然后重置为 1（E1 15）；终结技：层数从高到低重排到第一个敌人起，记录 md。
伤害层：强化战技主目标每层 +8%（3 魂 8.8%，智识 ≥2 名翻倍），其他目标每层一半；主目标 42 层时伤害 +50%；终结技每层【谜底】倍率 +1%（每个目标）。
效果类型 twn（时节不居）：我方攻击后（每回合 1 次）按装备者自上次结算以来的治疗量 × v% 打一次附加伤害（不暴击、不吃增伤），记在 R.dots（fixed）。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 80, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎：模拟 =================
F.rep('''    let brkBy = null, wkDepth = 0, wkEn = null;''', '''    let brkBy = null, wkDepth = 0, wkEn = null;
    // 大黑塔【解读】（敌人身上 en.jd）/【谜底】（HT.md）
    const HT = U.find(z => z.kind === "ally" && !z.sm && tx(z).jd) || null, JDX = HT ? tx(HT).jd : null;
    const JD2 = !!HT && U.filter(z => z.kind === "ally" && !z.sm && (tplOf(z) || {}).path === "智识").length >= 2;
    const jdAdd = (en, n) => { if (!HT || !en || !(n > 0)) return; en.jd = Math.min(num(JDX.max) || 42, num(en.jd) + n); HT.md = Math.min(num(JDX.md) || 99, num(HT.md) + n); };
    if (HT) { HT.md = 0; const ens = U.filter(z => z.kind === "enemy"); for (const z of ens) { z.jd = 0; jdAdd(z, 1); } if (ens[0]) jdAdd(ens[0], num(JDX.wave)); }   // 进入战斗各 1 层；波次开始给一个敌人 25 层（按主目标）
    const jdSort = () => { const ens = U.filter(z => z.kind === "enemy" && !z.gone), v = ens.map(z => num(z.jd)).sort((a, b) => b - a); ens.forEach((z, i) => { z.jd = v[i]; }); };   // 终结技：层数高的排到前面（主目标）
    const jdHit = (who, key) => {   // 我方攻击：被击中的敌人 +1 层【解读】
      if (!HT || !who) return;
      const o = ownerOf(who) || who, T0 = o.kind === "ally" ? tplOf(o) : null, ens = U.filter(z => z.kind === "enemy" && !z.gone); if (!ens.length) return;
      if (!key && who.sm) key = "m";
      if ((key === "s" || key === "u") && T0) { try { const f = (key === "s" ? S2ST : U2ST)[String(T0.id)]; if (f && f({ sts: o.st ? Object.keys(o.st).filter(k => o.st[k]) : [], mIn: U.some(x => x.sm && x.sm.owner === o.id && x.sm.mem && !x.gone) })) key += "2"; } catch (e) { /* 按普通 */ } }
      if (o === HT && key === "s2" && curRec && curRec.uid === HT.id) {   // 强化战技：先记下主目标层数（伤害用），再重置
        const e1 = ens[0], am = Math.max(0, ...ens.slice(1, 3).map(z => num(z.jd)));
        curRec.jd0 = num(e1.jd); curRec.jd = num(e1.jd) + (num(HT.eid) >= 1 ? am * 0.5 : 0); curRec.jd2 = JD2; e1.jd = num(HT.eid) >= 1 ? 15 : 1;
      }
      const tb = T0 ? (TGH[T0.id] || {})[key] : null;
      const hit = !tb ? [ens[0]] : ens.filter((z, i) => i === 0 ? num(tb[0]) > 0 || num(tb[1]) > 0 : num(tb[1]) > 0 || (i <= 2 && num(tb[2]) > 0));
      if (o === HT && (key === "s" || key === "s2")) jdAdd(ens[0], 1);   // 战技本身施加 1 层
      for (const z of hit) jdAdd(z, 1);   // 行迹冷漠的诚实
      if (JD2 && hit.length) { const top = hit.reduce((a, b) => num(b.jd) > num(a.jd) ? b : a); jdAdd(top, 1 + ((T0 || {}).path === "智识" ? 2 : 0)); }   // 行迹视界外来信
    };''')
# 强化战技 / 终结技的判断用行动开始时的状态快照（大黑塔【灵感】这类在施放时就被移除的状态），削韧也一样
n0 = F.s.count('f({ sts: o.st ? Object.keys(o.st).filter(k => o.st[k]) : [], mIn:'); assert n0 == 2, n0
F.s = F.s.replace('f({ sts: o.st ? Object.keys(o.st).filter(k => o.st[k]) : [], mIn:', 'f({ sts: curRec && curRec.uid === o.id && Array.isArray(curRec.sts) ? curRec.sts : o.st ? Object.keys(o.st).filter(k => o.st[k]) : [], mIn:')
F.rep('''    const atkAct = (who, fromFua, act) => { toughHit(who, fromFua ? "f" : ACT2K[act]); teamFire("atk", who, fromFua ? e => !e.nf : null); };''',
      '''    const atkAct = (who, fromFua, act) => { toughHit(who, fromFua ? "f" : ACT2K[act]); jdHit(who, fromFua ? "f" : ACT2K[act]); teamFire("atk", who, fromFua ? e => !e.nf : null); };''')
F.rep('''      ultMarks.push({ t, uid: u.id, n: u.ultN, ''', '''      if (HT && u === HT) jdSort(); ultMarks.push({ md: HT && u === HT ? num(HT.md) : undefined, t, uid: u.id, n: u.ultN, ''')
# 时节不居
F.rep('''        if (eff.type === "supR") {''', '''        if (eff.type === "twn") {   // 时节不居：按装备者自上次结算以来的治疗量打一次附加伤害（不暴击、不吃增伤）
          const own = src ? (ownerOf(src) || src) : null; if (!own || tg.kind !== "enemy") continue;
          const tot = num(healTot[own.id]), a = (tot - num(own.twnB)) * v / 100; if (!(a > 0)) continue;
          own.twnB = tot;
          const r = { t, uid: own.id, en: tg.id, k: "时节不居", fixed: a, db: dbSnap(own, tg), edb: edbSnap(), seq: seq++, ebk: !!tg.broken }; dotRecs.push(r);
          addLog(`${own.name}「时节不居」：按记录的治疗量造成附加伤害（基础 ${Math.round(a)}）`, false, srcColor); log[log.length - 1].dd = [r];
          continue;
        }
        if (eff.type === "supR") {''')
# ================= 引擎：伤害层 =================
F.rep('''    if (r.sup) { const e = dmgEntry(u, r.sup); return (r.__dmg = e ? dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk }) : null); }''',
      '''    if (r.sup) { const e = dmgEntry(u, r.sup); return (r.__dmg = e ? dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk }) : null); }
    if (r.fixed != null) { const d = dmgCalc(u, { v: 1, adj: 0, rnd: 0, tg: 1, el: 0, stat: "atk", key: "x", n: r.k, lv: 0, dot: true, brk: true, defIg: 0 }, { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk }, r.fixed); if (d) { d.noPanel = false; d.stat = "记录的治疗量"; } return (r.__dmg = d); }   // 固定数值的附加伤害（时节不居）''')
F.rep('''    if (!isLv && e.stat === "atk") base +=''', '''    if (baseOv == null && !isLv && e.stat === "atk") base +=''')
F.rep('''    if (!isLv && e.stat === "def") base +=''', '''    if (baseOv == null && !isLv && e.stat === "def") base +=''')
a = '''    if (tidOf(u) === "1505" && e.key === "u" && e.rnd > 0) {'''
i = F.s.index(a); j = F.s.index('\n', i)
F.s = F.s[:j + 1] + '''    if (tidOf(u) === "1401" && rec) {   // 大黑塔：强化战技按【解读】层数、终结技按【谜底】提高倍率
      if (e.key === "s2" && num(rec.jd) > 0) { const p = (num(u.eid) >= 3 ? 0.088 : 0.08) * (rec.jd2 ? 2 : 1); mult += p * num(rec.jd) + p / 2 * num(rec.jd) * nAdj; if (num(rec.jd0) >= 42) bonus += 50; }   // 行迹冷漠的诚实：主目标 42 层时伤害 +50%
      if (e.key === "u" && num(rec.md) > 0) mult += 0.01 * num(rec.md) * nAll;
    }
''' + F.s[j + 1:]
assert F.s.index('if (tidOf(u) === "1401" && rec)') < F.s.index('const dmgM = ')
assert 'let mult = e.v * nAll' in F.s and 'let cr = num(u.cr, 5) + D("cr"), cd = num(u.cd, 50) + D("cd"), bonus' in F.s
F.rep('''["supR", "恢复助战技次数（姬子•启行）"], ''', '''["supR", "恢复助战技次数（姬子•启行）"], ["twn", "按记录的治疗量造成附加伤害（时节不居）"], ''')

# ================= 大黑塔 =================
c = C[1401]
has('140104', '敌方目标进入战斗时，大黑塔对其施加1层【解读】。每个波次开始时，对一个随机敌方目标施加#6[i]层【解读】'); has('140104', '每层对主目标/其他目标提高#1[f1]%/#2[f1]%，若队伍中的「智识」命途角色大于等于2名，每层额外对主目标/其他目标提高#1[f1]%/#2[f1]%')
hast(1401, '冷漠的诚实', '施放强化战技时，若主目标的【解读】层数达到42，使大黑塔造成的伤害提高#2[i]%'); hast(1401, '饥饿的地景', '敌方目标每被施加1层【解读】，大黑塔获得1层【谜底】，最多叠加#2[i]层。施放终结技时，每持有1层【谜底】，使本次终结技的伤害倍率提高#1[f1]%')
has('r:140101', '额外计算主目标及相邻目标中层数最高的1个目标当前【解读】层数的50%。施放强化战技重置【解读】时，改为将层数重置为15层')
t10, t12 = prm('140104', 10), prm('140104', 12); assert r4(t10[0]) == 0.08 and r4(t12[0]) == 0.088 and t10[2] == 42 and t10[5] == 25
eff = [e for e in c['eff'] if e.get('bk') != 'md']
for e in eff:
    if e.get('bk') == 'ult' and e.get('m') == 'atkP': e['n'] = '终结技：攻击力 +80%（5 魂 88%），持续 3 回合'
old_md = [n for n, t in F.OLD[1401] if n and n.startswith('行迹饥饿的地景')]
old_u = [n for n, t in F.OLD[1401] if n and n.startswith('终结技：攻击力 +80%')]
c['notes'] = ['【解读】/【谜底】自动算（要放敌人卡）：进入战斗各 1 层、第一个敌人再 25 层（“随机、优先精英”按主目标）；我方每次攻击击中的敌人 +1；「智识」≥2 名时再给层数最高的 +1（智识攻击者再 +2）；战技主目标再 +1；强化战技按主目标层数提高倍率（每层主目标 8% / 其他 4%，智识 ≥2 名翻倍；42 层时伤害 +50%），用后重置为 1 层（E1 15 层）；终结技把层数从高到低重排到第一个敌人起，每层【谜底】倍率 +1%',
              '“击中哪些敌人”按削韧表（有全体削韧 = 打全部、有相邻削韧 = 打第 2、3 个）；强化战技每层倍率按主目标 / 其他目标各加一次（不是每段都加）']
F.rebuild(1401, eff, rename={old_u[0]: '终结技：攻击力 +80%（5 魂 88%），持续 3 回合'} if old_u else None, x={'jd': {'max': 42, 'wave': 25, 'md': 99}})

# ================= 时节不居 =================
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8'))
F.has(LR['23013']['desc'], '当任意我方目标施放攻击后，根据记录治疗量的#3[i]%，对随机1个受到攻击的敌方目标造成基于装备者属性的附加伤害。该伤害不受加成影响，每回合最多结算1次')
L = {x['id']: x for x in F.DB['lcs']}
L[23013]['eff'] = L[23013].get('eff', []) + [dict(y='twn', t='atk', aw='all', tg='efirst', ptn=1, v=[r4(p[2] * 100) for p in LR['23013']['params']], n='光锥：任意我方目标攻击后（每回合 1 次），按装备者记录的治疗量（自上次结算后的）造成附加伤害（打主目标；不暴击、不吃增伤）')]
L[23013]['notes'] = ['时节不居：记录的治疗量结算后清零、不暴击，原文没写，这里这样算']

F.finish('大黑塔【解读】、时节不居、击破伤害基础值修正', '''<li><b>2026-11-11（大黑塔【解读】、时节不居）</b>：tv 80（tools/fix80.py）。<b>大黑塔</b>：【解读】和【谜底】现在按模拟里的攻击自动叠（要放敌人卡）：进入战斗各 1 层、第一个敌人再 25 层，我方每次攻击击中的敌人 +1，「智识」≥2 名时再给层数最高的 +1（智识角色攻击再 +2），战技主目标再 +1；强化战技按主目标层数提高倍率（每层 8% / 其他目标 4%，智识 ≥2 名翻倍，42 层时伤害再 +50%），用后重置为 1 层（E1 15 层）；终结技每层【谜底】倍率 +1%（以前按叠满 99 层估）。<b>时节不居</b>：任意我方攻击后（每回合 1 次），按装备者记录的治疗量 36% 打一次附加伤害。<b>修正</b>：击破伤害的基础值以前会误吃攻击力%加成（偏高），现在不吃了；施放时就移除状态的强化战技（比如大黑塔用掉最后一层【灵感】）以前按普通战技削韧，现在按强化战技。只影响伤害数字，行动轴不变。</li>''',
'''2026-11-11：大黑塔（1401）【解读】/【谜底】、光锥时节不居 —— tv 80（tools/fix80.py）。新：x.jd、效果类型 twn、R.dots 的 fixed；修正击破伤害基础值吃攻击力%；强化战技的削韧按行动开始时的状态判断（以前大黑塔最后一层【灵感】的强化战技按普通战技削韧）。
  未改 / 存疑：【解读】“随机、优先精英”和终结技重排都按第一个敌人是精英；击中目标按削韧表推断；强化战技的层数加成按每个目标加一次；敌人离场 / 被消灭的转移没做（页面不模拟消灭）；时节不居的记录治疗量结算后清零、不暴击、打主目标（原文没写清零和暴击）。''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX80); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX80); for (const u of s.units) if (u.kind === "ally" && !u.sm && u.lc === 23013) applyEquip(u); } finally { S = keep; } }   // 时节不居改了')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
