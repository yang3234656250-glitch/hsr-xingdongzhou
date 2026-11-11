"""tv 84：伤害增益的条件按模拟里的实际状态判断（原来“按一直满足算”或“满足时启用”的）。
用法：python3 tools/fix84.py index.html <官方 json 目录>
伤害增益条件 ec 新字段（出手 / 结算时判断，按主目标 = 第一个还在的敌人；没放敌人卡时按“敌人”虚拟目标 EV0）：
  hp = [op, X] 持有者当前生命值 %（没有生命数值按满血）；lost = 1 按持有者已损失生命值百分比倍乘（阿兰）；ef = 1 持有者能量满；
  ehp = [op, X] 目标当前生命值 %（“我方伤害扣敌人生命值”关着时按满血）；hpv = 1 目标生命值百分比 ≥ 持有者；
  dfr = ["def" / "spd"] 目标处于防御降低 / 减速；dbf = N 目标负面效果 ≥N 个；dbn = N 按目标负面效果个数倍乘（最多 N）。
  op：le ≤ / lt < / ge ≥ / gt >。负面效果个数 = 持续伤害 + 敌人身上的易伤 / 减防 / 减抗 / 虚弱 / 减速增益（每组算 1 个）+ 敌人身上的状态 + 植入的弱点。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 84, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('''    const ecF = (b, u, en) => {''', '''    const cmpP = (p, c) => { const op = c[0], v = num(c[1]); return op === "le" ? p <= v + 1e-9 : op === "lt" ? p < v - 1e-9 : op === "gt" ? p > v + 1e-9 : p >= v - 1e-9; };   // 百分比比较：le ≤ / lt < / ge ≥ / gt >
    const hpPct = u => { const c = hpCur(u), m = hpNow(u); return c == null || !(m > 0) ? 100 : c / m * 100; };   // 没有生命数值按满血
    const ePct = en => eHpOn && en && en.ehx > 0 ? Math.max(0, num(en.ehc)) / en.ehx * 100 : 100;   // 敌人当前生命值 %（不模拟敌人掉血时按满血）
    const NEGST = ["vuln", "defRed", "resRed", "wkn"];
    const negOf = en => {   // 敌人身上的负面效果个数：持续伤害、易伤 / 减防 / 减抗 / 虚弱 / 减速（每组 1 个）、状态、植入的弱点
      if (!en) return 0; const k = new Set();
      for (const d of en.dots || []) if (!d.gone) k.add("d:" + d.key);
      for (const z of en.buffs || []) if ((z.kind === "d" && NEGST.includes(z.st) && num(z.v) > 0) || (!z.kind && num(z.v) < 0)) k.add("b:" + z.key);
      for (const s of Object.keys(en.st || {})) k.add("s:" + s);
      for (const w of en.wk || []) k.add("w:" + (w.own || "") + (w.el || ""));
      return k.size;
    };
    const ecF = (b, u, en) => {''')
F.rep('''      if (c.be != null && beOf(u) + beTeam() < num(c.be) - 1e-9) return 0;
      if (c.dk == null && c.dn == null && c.wb == null && c.wc == null && c.wl == null && c.tq == null) return f0;
      en = u.kind === "enemy" ? u : en || U.find(x => x.kind === "enemy" && !x.gone); if (!en) return 0;   // 挂在敌人身上的按它自己''',
      '''      if (c.hp && !cmpP(hpPct(u), c.hp)) return 0;   // 持有者当前生命值 %
      if (c.lost) { f0 *= Math.max(0, 1 - hpPct(u) / 100); if (!(f0 > 1e-9)) return 0; }   // 按已损失的生命值百分比（阿兰）
      if (c.ef && !(hasEnergy(u) && !noStdE(u) && num(u.e) >= eCfg(u).maxE - 1e-6)) return 0;   // 能量满
      if (c.be != null && beOf(u) + beTeam() < num(c.be) - 1e-9) return 0;
      if (c.dk == null && c.dn == null && c.wb == null && c.wc == null && c.wl == null && c.tq == null && c.ehp == null && c.hpv == null && c.dfr == null && c.dbf == null && c.dbn == null) return f0;
      en = u.kind === "enemy" ? u : en || U.find(x => x.kind === "enemy" && !x.gone) || EV0;   // 挂在敌人身上的按它自己；没放敌人卡按虚拟的“敌人”''')
F.rep('''      const ds = (en.dots || []).filter(d => !d.gone), m = monOf(en);''', '''      const ds = (en.dots || []).filter(d => !d.gone), m = monOf(en);
      if (c.ehp && !cmpP(ePct(en), c.ehp)) return 0;   // 目标当前生命值 %
      if (c.hpv && ePct(en) < hpPct(u) - 1e-9) return 0;   // 目标生命值百分比不低于持有者
      if (c.dfr && ![].concat(c.dfr).some(k => k === "def" ? (en.buffs || []).some(z => z.kind === "d" && z.st === "defRed" && num(z.v) > 0) : k === "spd" && (en.buffs || []).some(z => !z.kind && num(z.v) < 0))) return 0;   // 防御降低 / 减速
      if (c.dbf != null || c.dbn != null) { const n = negOf(en); if (c.dbf != null && n < num(c.dbf)) return 0; if (c.dbn != null) { f0 *= Math.min(num(c.dbn), n); if (!(f0 > 0)) return 0; } }   // 负面效果个数''')
assert F.s.index('      if (c.dbf != null || c.dbn != null)') < F.s.index('      let f = f0;\n      if (c.dn != null)')
# 编辑器提示：条件写成中文
a = F.s.index('    if (e.ec) h.push('); b = F.s.index('\n', a)
F.s = F.s[:a] + '    if (e.ec) h.push(ecTxt(e.ec));' + F.s[b:]
F.rep('''  const effSum = e => {''', '''  const OPL = { le: "≤", lt: "<", ge: "≥", gt: ">" };
  const ecTxt = c => {   // 伤害增益的条件（ec）说明
    const L = [];
    if (c.sh) L.push(c.sh === "own" ? "持有装备者给的护盾时" : c.sh === 1 || c.sh === true ? "持有护盾时" : `持有【${c.sh}】组护盾时`);
    if (Array.isArray(c.shn)) L.push(`按持有护盾的${c.shn[1] === "o" ? "队友" : "角色"}数（最多 ${c.shn[0]} 名）`);
    if (c.st) L.push(`持有【${c.st}】时`);
    if (c.hp) L.push(`自身生命值 ${OPL[c.hp[0]] || "≥"}${c.hp[1]}% 时`);
    if (c.lost) L.push("按自身已损失的生命值百分比");
    if (c.ef) L.push("能量满时");
    if (c.ehp) L.push(`目标生命值 ${OPL[c.ehp[0]] || "≥"}${c.ehp[1]}% 时（“我方伤害扣敌人生命值”关着时敌人按满血）`);
    if (c.hpv) L.push("目标生命值百分比不低于自己时");
    if (c.dfr) L.push(`目标${[].concat(c.dfr).map(k => k === "def" ? "防御降低" : "减速").join("或")}时`);
    if (c.dbf != null) L.push(`目标负面效果 ≥${c.dbf} 个时`);
    if (c.dbn != null) L.push(`按目标负面效果个数（最多 ${c.dbn} 个）`);
    if (c.be != null) L.push(`击破特攻 ≥${c.be}% 时`);
    if (c.dk || c.dn != null || c.wb || c.wc != null || c.wl || c.tq != null) L.push("出手时按主目标的状态算");
    return L.join("，") || "出手时按主目标的状态算";
  };
  const effSum = e => {''')

def setx(e, **kw):
    for k, v in kw.items():
        if v is None: e.pop(k, None)
        else: e[k] = v
    return e
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
REN, ON = {}, {}
def base(cid, pre, n, **kw):
    e = find(C[cid]['eff'], pre); o = e['n']
    if e.get('off'): ON.setdefault(cid, []).append(o)
    setx(e, n=n, **kw); REN.setdefault(cid, {})[o] = n
def eid(cid, r, pre, n, **kw):
    E = F.eid(cid, r); e = find(E['eff'], pre); setx(e, n=n, **kw); return E

# ---- 角色：基础效果 ----
base(1002, '行迹罡风', '行迹罡风：普攻对减速的敌人伤害 +40%', ec={'dfr': ['spd']}, off=None)
base(1003, '行迹道标', '行迹道标：生命值 ≥80% 时暴击率 +15%', ec={'hp': ['ge', 80]})
base(1003, '行迹灼热', '行迹灼热：战技对灼烧的敌人伤害 +20%', ec={'dk': ['灼烧']}, off=None)
has('100804', '根据阿兰当前损失的生命值百分比获得伤害加成，最多使阿兰造成的伤害提高#1[i]%')
base(1008, '天赋：按损失的生命值百分比增伤', '天赋：按当前损失的生命值百分比增伤，最多 +72%（5 魂 79.2%）', ec={'lost': 1}, off=None)
base(1013, '战技：对生命值 ≥50% 的敌人', '战技：对生命值 ≥50% 的敌人伤害 +20%（行迹效率再 +25%）', ec={'ehp': ['ge', 50]})
base(1106, '行迹痛击', '行迹痛击：对处于负面效果的敌人伤害 +20%', ec={'dbf': 1})
base(1209, '秘技：对生命值 ≥50% 的敌人', '秘技：对生命值 ≥50% 的敌人伤害 +30%，持续 2 回合（用了秘技再启用）', ec={'ehp': ['ge', 50]})
base(1210, '行迹逾锋', '行迹逾锋：对灼烧的敌人伤害 +20%', ec={'dk': ['灼烧']})
base(1302, '行迹勇气', '行迹勇气：对生命值 ≤50% 的敌人伤害 +15%', ec={'ehp': ['le', 50]}, off=None)
hast(1305, '推理', '造成伤害时，若目标负面状态大于等于#1[i]个，目标每有1个负面效果，真理医生对其造成的伤害提高#2[i]%，最多提高#3[i]%')
base(1305, '行迹推理', '行迹推理：目标负面效果 ≥3 个时每个伤害 +10%，最多 50%', v=10, ec={'dbf': 3, 'dbn': 5})
for cid in REN: F.rebuild(cid, C[cid]['eff'], rename=REN[cid], off0=ON.get(cid))

# ---- 角色：星魂 ----
eid(1002, 1, 'E1：击中生命值 ≥50% 的敌人', 'E1：击中生命值 ≥50% 的敌人时暴击率 +12%', ec={'ehp': ['ge', 50]})
eid(1003, 2, 'E2：对生命值 ≤50% 的敌人', 'E2：对生命值 ≤50% 的敌人伤害 +15%', ec={'ehp': ['le', 50]}, off=None)
has('r:100606', '敌方目标每有1个负面效果，银狼对其造成的伤害提高20%，最多提高100%')
eid(1006, 6, 'E6：敌人每有 1 个负面效果', 'E6：敌人每有 1 个负面效果伤害 +20%，最多 100%', v=20, ec={'dbn': 5})
eid(1008, 1, 'E1：生命值 ≤50% 时战技', 'E1：生命值 ≤50% 时战技伤害 +10%', ec={'hp': ['le', 50]}, off=None)
eid(1008, 6, 'E6：生命值 ≤50% 时终结技', 'E6：生命值 ≤50% 时终结技伤害 +20%', ec={'hp': ['le', 50]}, off=None)
eid(1102, 1, 'E1：对生命值 ≤80% 的敌人', 'E1：对生命值 ≤80% 的敌人暴击率 +15%', ec={'ehp': ['le', 80]}, off=None)
eid(1103, 6, 'E6：对触电的敌人', 'E6：对触电的敌人伤害 +30%', ec={'dk': ['触电']})
eid(1109, 6, 'E6：对灼烧的敌人', 'E6：对灼烧的敌人伤害 +20%', ec={'dk': ['灼烧']})
eid(1111, 1, 'E1：目标处于裂伤时', 'E1：目标处于裂伤时伤害 +15%', ec={'dk': ['裂伤']})
eid(1209, 4, 'E4：生命值 ≥80% 时', 'E4：生命值 ≥80% 时冰属性抗性穿透 +12%', ec={'hp': ['ge', 80]})
eid(1308, 1, 'E1：对处于负面效果的敌人', 'E1：对处于负面效果的敌人暴击率 +18%', ec={'dbf': 1})
has('r:140701', '敌方目标当前生命值小于等于自身生命上限80%/50%时')
E = eid(1407, 1, 'E1：敌方当前生命值 ≤80% / ≤50% 时', 'E1：敌方当前生命值 ≤80% 时，死龙的爪痕、焰息、晦翼对其伤害为原伤害的 120%', ec={'ehp': ['le', 80]}, off=None)
eid(1407, 1, 'E1：同上，【骸爪，冥龙之环拥】', 'E1：同上，【骸爪，冥龙之环拥】（按遐蝶的战技算，近似）', ec={'ehp': ['le', 80]}, off=None)
E['eff'] += [dict(y='dbuf', t='start', tg='sm:dragon', m='xtra', v=20, d=0, bk='e1b', ec={'ehp': ['le', 50]}, n='E1：敌方当前生命值 ≤50% 时再 +20%（合计原伤害的 140%）'),
             dict(y='dbuf', t='start', tg='self', m='xtra', v=20, sc='s', d=0, bk='e1b', ec={'ehp': ['le', 50]}, n='E1：同上，【骸爪，冥龙之环拥】≤50% 时再 +20%')]
has('r:150401', '当敌方目标当前生命值百分比小于等于50%时，其受到的伤害提高至36%')
E = eid(1504, 1, 'E1：敌方全体受到的伤害 +24%', 'E1：敌方全体受到的伤害 +24%')
E['eff'].append(dict(y='dbuf', t='start', tg='enemies', m='vuln', v=12, d=0, bk='e1b', ec={'ehp': ['le', 50]}, n='E1：敌人生命值 ≤50% 时受到的伤害再 +12%（合计 36%）'))

# ---- 光锥 ----
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8'))
L = {x['id']: x for x in F.DB['lcs']}
def lc(i, pre, n, frag=None, **kw):
    if frag: F.has(LR[str(i)]['desc'], frag)
    e = find(L[i]['eff'], pre); setx(e, n=n, **kw); return e
P = lambda i, k: [r4(p[k] * 100) for p in LR[str(i)]['params']]
lc(24001, '光锥：对生命值 ≤50% 的敌人', '光锥：对生命值 ≤50% 的敌人暴击率额外提高', '装备者对生命值百分比小于等于#2[i]%的敌方目标暴击率额外提高#3[i]%', ec={'ehp': ['le', 50]}, off=None)
lc(23020, '光锥：敌人每有 1 个负面效果', '光锥：敌人每有 1 个负面效果暴伤额外提高，最多 3 层', '敌方目标每承受1个负面效果，装备者对其造成的暴击伤害额外提高#2[i]%，最多叠加#3[i]层', v=P(23020, 1), ec={'dbn': 3})
lc(23007, '光锥：对有 ≥3 个负面效果', '光锥：对有 ≥3 个负面效果的敌人暴击率提高', None, ec={'dbf': 3}, off=None)
lc(23004, '光锥：对陷入负面效果的敌人', '光锥：对陷入负面效果的敌人伤害提高', None, ec={'dbf': 1})
lc(21055, '光锥：我方目标生命值 ≥50%', '光锥：我方目标生命值 ≥50% 时伤害提高', None, ec={'hp': ['ge', 50]})
lc(21044, '光锥：对防御降低或减速', '光锥：对防御降低或减速的敌人暴击伤害提高', '装备者对处于防御降低或减速状态下的敌人造成的暴击伤害提高#2[i]%', ec={'dfr': ['def', 'spd']}, off=None)
e = lc(21017, '光锥：能量满时', '光锥：能量满时普攻伤害额外提高', '当装备者的当前能量值等于其能量上限时，该效果额外提高#2[i]%', ec={'ef': 1}, sc='b', off=None)
L[21017]['eff'].append(dict(e, sc='s', bk='lc4', n='光锥：能量满时战技伤害额外提高'))
lc(21012, '光锥：对生命值百分比不低于自己', '光锥：对生命值百分比不低于自己的敌人伤害额外提高', '同时对当前生命值百分比大于等于装备者自身当前生命值百分比的敌方目标造成的伤害额外提高#2[i]%', ec={'hpv': 1}, off=None)
lc(21006, '光锥：目标生命值 ≤50%', '光锥：目标生命值 ≤50% 时追加攻击伤害额外提高', None, ec={'ehp': ['le', 50]}, off=None)
lc(21001, '光锥：敌人每有 1 个负面效果', '光锥：敌人每有 1 个负面效果伤害提高，最多 3 层（含持续伤害）', '敌方目标每承受1个负面效果，装备者对其造成的伤害提高#1[i]%，最多叠加#2[i]层', v=P(21001, 0), ec={'dbn': 3})
lc(20016, '光锥：生命值 <80%', '光锥：生命值 <80% 时暴击率提高', None, ec={'hp': ['lt', 80]}, off=None)
lc(20011, '光锥：对减速的敌人', '光锥：对减速的敌人伤害提高', '使装备者对减速状态下的敌方目标造成的伤害提高#1[i]%', ec={'dfr': ['spd']}, off=None)
lc(20009, '光锥：对生命值 >50% 的敌人', '光锥：对生命值 >50% 的敌人伤害提高', None, ec={'ehp': ['gt', 50]})
lc(20003, '光锥：生命值 <50%', '光锥：生命值 <50% 时防御力额外提高', None, ec={'hp': ['lt', 50]}, off=None)

# ---- 遗器 ----
RS = json.load(open(sys.argv[2] + '/relic_sets.json', encoding='utf-8'))
R = {x['id']: x for x in F.DB['relics']}
assert '装备者对陷入负面效果的敌方目标造成伤害时暴击率提高10%' in RS['112']['desc'][1]
setx(find(R[112]['p4']['eff'], '4件：对陷入负面效果'), n='4件：对陷入负面效果的敌人暴击率提高 10%', ec={'dbf': 1})
assert RS['117']['desc'][0] == '对受负面状态影响的敌人造成的伤害提高12%。' and '对陷入不少于2/3个负面效果的敌方目标造成的暴击伤害提高8%/12%' in RS['117']['desc'][1]
setx(find(R[117]['p2']['eff'], '2件：对受负面状态影响'), n='2件：对受负面状态影响的敌人伤害提高 12%', ec={'dbf': 1})
e = find(R[117]['p4']['eff'], '4件：对有 ≥2 个负面效果'); setx(e, n='4件：对有 ≥2 个负面效果的敌人暴击伤害提高 8%（施加负面后翻倍没算）', ec={'dbf': 2})
R[117]['p4']['eff'].append(dict(y='dbuf', t='start', tg='self', m='cd', v=4, d=0, bk='r4b', ec={'dbf': 3}, n='4件：≥3 个负面效果时再 +4%（合计 12%）'))
assert '装备者对防御力降低状态的敌方目标造成的暴击伤害提高28%' in RS['132']['desc'][1]
setx(find(R[132]['p4']['eff'], '4件：对防御力降低的敌人'), n='4件：对防御力降低的敌人暴击伤害提高 28%', ec={'dfr': ['def']}, off=None)

LCS = [24001, 23020, 23007, 23004, 21055, 21044, 21017, 21012, 21006, 21001, 20016, 20011, 20009, 20003]
F.finish('伤害增益条件按实际状态判断', '''<li><b>2026-11-11（条件按实际状态判断）</b>：tv 84（tools/fix84.py）。原来写着“按一直满足算”或“满足时启用”的伤害增益，改成在出手时按模拟里的实际状态判断：<b>敌人负面效果</b>（个数 = 持续伤害、易伤 / 减防 / 减抗 / 虚弱 / 减速、敌人身上的状态、植入的弱点；佩拉痛击、黄泉 1 魂、银狼 6 魂、真理医生推理、以世界之名、晚安与睡颜、纯粹思维的洗礼、雨一直下、盗匪荒漠的废土客、死水深潜的先驱（补上 ≥3 个时 12%））；<b>敌人持续伤害种类</b>（姬子灼热、希露瓦 / 虎克 / 卢卡 / 桂乃芬）；<b>敌人防御降低 / 减速</b>（丹恒罡风、无边曼舞、渊环、叩问天工的名冶）；<b>敌人生命值</b>（姬子 2 魂、希儿 1 魂、银枝、丹恒 1 魂、黑塔、彦卿秘技、遐蝶 1 魂 120% / 140%、不死途 1 魂 36%、星海巡航、乐圮、「我」的诞生、秘密誓心；要开“我方伤害扣敌人生命值”，关着时敌人按满血）；<b>自己的生命值 / 能量</b>（姬子道标、彦卿 4 魂、阿兰天赋按损失生命值、阿兰 1 / 6 魂、直到明天的明天、俱殁、琥珀、点个关注吧！）。原来默认关的这些现在默认开。对已有配置：敌人没有负面效果、敌人满血、自己满血时，对应的增益不再算——伤害可能比原来低（原来是按一直满足）。</li>''',
'''2026-11-11：伤害增益条件按实际状态判断 —— tv 84（tools/fix84.py）。新：ec.hp / lost / ef / ehp / hpv / dfr / dbf / dbn；没放敌人卡时 ecF 按 EV0。
  未改 / 存疑：负面效果个数按“每组增益 / 每个持续伤害 / 每个状态 / 每个植入弱点各 1 个”数，同一个技能拆成几条增益时会多数；敌人生命值按每次行动前结算的伤害（同一次行动里的多段之间不更新）；死水深潜 4 件“施加负面后翻倍”、盗匪荒漠 4 件的禁锢、景元破阵（神君段数）、托帕 / 寒鸦 / 貊泽 / 阿格莱雅的标记类仍按一直有''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX84); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX84); for (const u of s.units) if (u.kind === "ally" && !u.sm && (' + ' || '.join('u.lc === %d' % i for i in LCS) + ' || [112, 117, 132].includes(u.rA) || [117].includes(u.rB))) applyEquip(u); } finally { S = keep; } }   // 条件按实际状态的光锥 / 遗器')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
