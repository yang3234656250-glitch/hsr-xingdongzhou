"""tv 89：不死途【婪酣】额外伤害和 2 魂返还、云璃嘲讽和【格挡】减伤、罗刹 2 魂、清理已经做完的“没做 / 没算”说明。
用法：python3 tools/fix89.py index.html <官方 json 目录>
引擎：
- 伤害增益字段 smd 消耗层数时记下消耗了几组（每组 m 层）到持有者最新的那次追加攻击记录（rec.lhG）；字段 smr = [星魂, %]：到这个星魂时返还消耗层数的 %（向下取整）。
- 额外伤害 cnt "lhG"：按 rec.lhG。
- 状态计时 ts "any"：任意单位的回合结束时 −1（同一个回合里挂上的不算），云璃【格挡】和嘲讽“持续至下一个我方或敌方回合结束时”。
- 效果字段 pri：同一个触发里先结算（罗刹 2 魂在治疗之前判断目标生命值）；条件 tgh = [op, X]：只对当前生命值百分比满足的目标生效（治疗 / 护盾 / 其他按目标的效果）。"""
import sys, json, re
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 89, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('''      if (x.nx) e.nxt = x.nx;''', '''      if (x.smr) e.stModR = x.smr; if (x.pri) e.pri = x.pri; if (x.tgh) e.tgHp = x.tgh;   // 消耗层数后返还；先结算；目标生命值条件
      if (x.nx) e.nxt = x.nx;''')
F.rep('''if (x.ts) e.stTick = x.ts === "chg" ? "chg" : x.ts === "src" ? "src" : "start";''', '''if (x.ts) e.stTick = x.ts === "chg" ? "chg" : x.ts === "src" ? "src" : x.ts === "any" ? "any" : "start";''')
F.rep('''      tg.st[k] = { left: d > 0 ? d : Infinity, tick: eff.stTick === "start" ? "start" : eff.stTick === "src" && src ? "src" : "end", by: src ? src.id : null };''',
      '''      tg.st[k] = { left: d > 0 ? d : Infinity, tick: eff.stTick === "start" ? "start" : eff.stTick === "src" && src ? "src" : eff.stTick === "any" ? "any" : "end", by: src ? src.id : null, bornT: turnSeq };''')
F.rep('''      if (actor.kind === "ally") for (const e of fx(actor, "tend")) apply(e, actor, actor.color);   // 自己回合结束时''', '''      if (actor.kind === "ally") for (const e of fx(actor, "tend")) apply(e, actor, actor.color);   // 自己回合结束时
      for (const z of U) if (z.st) for (const k of Object.keys(z.st)) { const s0 = z.st[k]; if (s0 && s0.tick === "any" && s0.bornT !== turnSeq && --s0.left <= 0) endSt(z, k); }   // 持续到下一个任意回合结束（这个回合里挂上的不算）''')
F.rep('''    const mkTk = u => { const m = new Map(); for (const e of u.effects || []) { if (e.off) continue; const ks = e.or && e.or !== e.trigger && (e.trigger !== "turn" || e.or === "xturn") ? [e.trigger, e.or] : [e.trigger]; for (const k of ks) { let a = m.get(k); if (!a) m.set(k, a = []); a.push(e); } }''',
      '''    const mkTk = u => { const m = new Map(); for (const e of u.effects || []) { if (e.off) continue; const ks = e.or && e.or !== e.trigger && (e.trigger !== "turn" || e.or === "xturn") ? [e.trigger, e.or] : [e.trigger]; for (const k of ks) { let a = m.get(k); if (!a) m.set(k, a = []); a.push(e); } } for (const a of m.values()) if (a.some(e => num(e.pri))) a.sort((x, y) => num(y.pri) - num(x.pri));''')
F.rep('''        if (Array.isArray(eff.stMod)) { const o = old ? old.n || 1 : 0, k = num(eff.stMod[1]), m = Math.max(1, num(eff.stMod[0])); n = o <= k ? o : ((o - k) % m) + k; }''',
      '''        if (Array.isArray(eff.stMod)) {   // 每 m 层消耗掉，最后加的 k 层不算（不死途强化追击）；消耗的组数记到最近一次追加攻击上，2 魂返还
          const o = old ? old.n || 1 : 0, k = num(eff.stMod[1]), m = Math.max(1, num(eff.stMod[0])); n = o <= k ? o : ((o - k) % m) + k;
          const g = Math.max(0, Math.round((o - n) / m)); const fm = src ? [...marks].reverse().find(z => z.uid === src.id && z.label === "追击") : null; if (fm) fm.lhG = g;
          if (Array.isArray(eff.stModR) && src && num(ownerOf(src).eid) >= num(eff.stModR[0])) n = Math.min(lim, n + Math.floor((o - n) * num(eff.stModR[1]) / 100 + 1e-9));
        }''')
F.rep('''r.cnt === "modN" ? Math.max(0, num(rec.modN) - 1) :''', '''r.cnt === "modN" ? Math.max(0, num(rec.modN) - 1) : r.cnt === "lhG" ? num(rec.lhG) :''')
# 目标生命值条件
F.rep('''      const tgs = resolve(eff.target, src).filter(u => u && !u.gone && !isCd(u) && !(u.kind === "ally" && u.sm && !u.sm.mem) && (u.kind !== "aha") && !(group && u.kind !== "ally") && !(eff.target === "evt" && isOut(u)));   // 界外的（德谬歌）选不中''',
      '''      const tgs = resolve(eff.target, src).filter(u => u && !u.gone && !isCd(u) && !(u.kind === "ally" && u.sm && !u.sm.mem) && (u.kind !== "aha") && !(group && u.kind !== "ally") && !(eff.target === "evt" && isOut(u)) && !(eff.tgHp && !cmpP(hpPct(u), eff.tgHp)));   // 界外的（德谬歌）选不中；tgHp：目标当前生命值条件''')
F.rep('''      const tgs = all.filter(u => u.kind === "ally" && !u.gone && !isCd(u) && !(u.sm && !u.sm.mem) && !(eff.target === "evt" && isOut(u)));''',
      '''      const tgs = all.filter(u => u.kind === "ally" && !u.gone && !isCd(u) && !(u.sm && !u.sm.mem) && !(eff.target === "evt" && isOut(u)) && !(eff.tgHp && !cmpP(hpPct(u), eff.tgHp)));''')
F.rep('''    if (e.alv) h.push("施加者倒下时消失");''', '''    if (e.alv) h.push("施加者倒下时消失");
    if (e.tgHp) h.push(`只对当前生命值 ${({ le: "≤", lt: "<", ge: "≥", gt: ">" })[e.tgHp[0]] || "≥"}${e.tgHp[1]}% 的目标`);
    if (num(e.pri)) h.push("同一时机里先结算");''')
assert 'const hpPct = ' in F.s and F.s.index('const hpPct = ') < F.s.index('    const doHeal = ')

def setx(e, **kw):
    for k, v in kw.items():
        if v is None: e.pop(k, None)
        else: e[k] = v
    return e
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]

# ---- 不死途 ----
has('150403', '拥有【婪酣】时，每消耗#3[i]层【婪酣】可额外造成1次等同于不死途#4[i]%攻击力的雷属性伤害')
p10, p12 = prm('150403', 10), prm('150403', 12); assert p10[2] == 4 and p10[3] == 2 and p12[3] == 2.2
has('r:150402', '每当不死途发动强化天赋追加攻击后，返还所移除【婪酣】层数的35%')
c = C[1504]; E = c['eff']; x = find(E, '终结技：强化天赋追加攻击每消耗 4 层【婪酣】'); o = x['n']
n = '终结技：强化天赋追加攻击每消耗 4 层【婪酣】额外造成 1 次 200% 攻击力的伤害（伤害算在那次追加攻击上；2 魂返还消耗层数的 35%）'
setx(x, n=n, smr=[2, 35])
c['notes'] = ['【饲饵】按场上一直有（不存在时会自动选生命值最低的敌人）；消耗【婪酣】的额外伤害每次都打主目标（“打死后继续打新的饲饵”按同一个敌人算）']
F.rebuild(1504, E, rename={o: n})
F.XR.setdefault('1504', []).append({"k": "lh", "n": "终结技：强化天赋追加攻击每消耗 4 层【婪酣】额外 1 次 200% 攻击力伤害（12 级 220%；按这次实际消耗的组数）", "on": ["f"], "st": "atk", "v": [2.0, 2.2], "lk": "u", "cnt": "lhG"})

# ---- 云璃：嘲讽、【格挡】减伤 ----
has('122103', '云璃获得【格挡】并使敌方全体陷入嘲讽状态，持续至下一个我方或敌方回合结束时'); hast(1221, '却邪', '【格挡】状态下抵抗受到的控制类负面效果，并使受到的伤害降低#1[i]%')
c = C[1221]; E = c['eff']
E += [dict(y='state', t='ult', tg='self', sn='格挡', v=1, d=1, ts='any', n='终结技：获得【格挡】，持续至下一个我方或敌方回合结束时'),
      dict(y='state', t='ult', tg='enemies', sn='嘲讽', v=1, d=1, ts='any', n='终结技：敌方全体陷入嘲讽，持续至下一个我方或敌方回合结束时（被嘲讽的敌人单体攻击打云璃）'),
      dict(y='state', t='hit2', tg='self', sn='格挡', v=0, n='终结技：【格挡】期间被攻击触发【勘破•灭】时移除【格挡】'),
      dict(y='dbuf', t='start', tg='self', m='dr', v=20, d=0, bk='qx', ec={'st': '格挡'}, n='行迹却邪：【格挡】状态下受到的伤害降低 20%')]
F.rebuild(1221, E)

# ---- 罗刹 2 魂 ----
has('r:120302', '触发战技效果时，若指定我方目标当前生命值百分比小于50%，则罗刹提供的治疗量提高30%；若指定我方目标当前生命值百分比大于等于50%，则为其提供能够抵消等同于罗刹18%攻击力+240伤害的护盾，持续2回合')
e2 = F.eid(1203, 2)
base = find(C[1203]['eff'], '战技：为指定我方单体回复生命值'); auto = find(C[1203]['eff'], '战技：我方任意单体当前生命值 ≤50% 时')
H = lambda b, **kw: dict(y='heal', m='atk', v=r4(b['v'] * 0.3), hf=r4(b['hf'] * 0.3), lv=[b['lv'][0], r4(b['lv'][1] * 0.3)], lx={'flat': [r4(b['lx']['flat'][0] * 0.3), r4(b['lx']['flat'][1] * 0.3)]}, pri=1, tgh=['lt', 50], **kw)
e2['eff'] = [H(base, t='skill', tg='$ally', n='E2 净庭赐礼：战技目标当前生命值 <50% 时治疗量提高 30%（多回复战技治疗量的 30%）'),
             H(auto, t='hpLoss', ew='any', hlv=50, ns='!白花的祈望冷却', tg='evt', n='E2：自动触发的战技效果同样治疗量提高 30%'),
             dict(y='shield', t='skill', tg='$ally', m='atk', v=18, hf=240, d=2, pri=1, tgh=['ge', 50], n='E2：战技目标当前生命值 ≥50% 时为其提供护盾（罗刹 18% 攻击力 +240），持续 2 回合')]

# ---- 清理已经做完的说明 ----
def ren(cid, r, pre, new):
    L = C[cid]['eff'] if r is None else F.eid(cid, r)['eff']; e = find(L, pre); o = e['n']; e['n'] = new; return o, new
ren(1107, 2, 'E2：施放终结技后攻击力 +30%', 'E2：施放终结技后攻击力 +30%，持续 2 回合（强化反击的倍率提高在额外伤害里算）')
ren(1220, 6, 'E6：天赋追加攻击同时视为终结技伤害', 'E6：天赋追加攻击同时视为终结技伤害，同样 +20%（倍率 +140% 在额外伤害里算）')
ren(1412, 6, 'E6：刻律德菈全属性抗性穿透', 'E6：刻律德菈全属性抗性穿透 +20%（军功附加伤害倍率提高在额外伤害里算）')
C[1108]['notes'] = [x for x in C[1108].get('notes', []) if 'E1 多出的 1 段战技伤害没算' not in x]; F.touch(1108)
C[1412]['notes'] = [x.replace('；附加伤害最多 20 次（终结技重置）没限制', '') for x in C[1412].get('notes', [])]
F.touch(1412)

# ---- 追加攻击伤害倍率（原来伤害表里没有，追加攻击不显示伤害）----
import copy
lv = lambda sid, k: [r4(p[k]) for p in F.SK[sid]['params']]
has('150404', '消耗#3[i]点充能对【饲饵】发动追加攻击，造成等同于不死途#4[i]%攻击力的雷属性伤害')
F.DMG['1504']['f'] = {"v": lv('150404', 3), "adj": [], "rnd": [], "tg": 1, "el": 0, "stat": "atk", "n": "宿怨，切齿奉还（追加攻击）", "max": 15}
has('140604', '赛飞儿立即对【老主顾】发动追加攻击，造成等同于赛飞儿#1[i]%攻击力的量子属性伤害')
F.DMG['1406']['f'] = {"v": lv('140604', 0), "adj": [], "rnd": [], "tg": 1, "el": 0, "stat": "atk", "n": "热情好客的多洛斯人（追加攻击）", "max": 15}
has('r:110104', '布洛妮娅立即进行1次追加攻击，对该目标造成等同于普攻伤害80%的风属性伤害')
b = F.DMG['1101']['b']['v']; F.DMG['1101']['f'] = {"v": [r4(b[5] * 0.8)] * 10 + [r4(b[6] * 0.8)] * 5, "adj": [], "rnd": [], "tg": 1, "el": 0, "stat": "atk", "n": "E4 追加攻击（普攻伤害的 80%，按普攻 6 / 7 级）", "max": 15}
has('r:120104', '对该目标造成等同于普攻或强化普攻伤害100%的量子属性伤害')
f = copy.deepcopy(F.DMG['1201']['b2']); f['n'] = 'E4 追加攻击（按强化普攻伤害的 100%）'; F.DMG['1201']['f'] = f
f = copy.deepcopy(F.DMG['1507']['s']); f['n'] = '天赋：额外施放的战技（视为追加攻击）'; F.DMG['1507']['f'] = f

F.finish('不死途婪酣、云璃格挡、罗刹 2 魂', '''<li><b>2026-11-11（不死途、云璃、罗刹）</b>：tv 89（tools/fix89.py）。不死途终结技的强化追加攻击，每消耗 4 层【婪酣】额外 1 次 200% 攻击力伤害（按实际消耗的组数，算在那次追加攻击上），2 魂返还消耗层数的 35%。云璃终结技获得【格挡】并嘲讽敌方全体，持续到下一个我方或敌方回合结束（被嘲讽的敌人单体攻击打云璃），【格挡】期间受到的伤害降低 20%，被攻击后【格挡】移除。不死途、赛飞儿、千冶•刃（额外战技）、布洛妮娅 4 魂、青雀 4 魂的追加攻击原来伤害表里没有倍率、不显示伤害，现在补上。罗刹 2 魂：战技目标生命值 <50% 时治疗量 +30%，≥50% 时给护盾（18% 攻击力 +240，2 回合），自动触发的战技也算。克拉拉 2 魂、飞霄 6 魂、刻律德菈 6 魂、桑博 1 魂的“没算”说明去掉（这些早已在额外伤害里算了）。对已有配置：带云璃时敌人会改打云璃；不死途伤害变高。</li>''',
'''2026-11-11：不死途、云璃、罗刹 —— tv 89（tools/fix89.py）。新：smd 记 rec.lhG、smr 返还、XR cnt lhG、状态 ts "any"（bornT）、效果 pri、条件 tgh。
  未改 / 存疑：消耗【婪酣】的额外伤害按打主目标；云璃【格挡】按受到攻击后移除（勘破•斩 / 灭仍按原来的显示在开大上）；刻律德菈附加伤害每轮最多 20 次没限制''')
