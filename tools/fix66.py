"""tv 66：持续伤害第 2 批（海瑟音 1410、桑博 1108、桂乃芬 1210、椒丘 1218）。
用法：python3 tools/fix66.py index.html <官方 json 目录>
引擎：dot 的 cyc（几种状态轮流挂：先挂目标身上还没有的，都有了就刷新剩余回合最少的；stAdd = 一次挂几种）；
效果类型 dotd（直接造成一次持续伤害类的伤害：数值 = 倍率 %，cap = 同一时刻最多几次；自己造成的这次不会再触发自己）；
dotx 的 dk = 只引爆这种状态；dotHit 触发的 dki = 只在这种状态造成伤害时；条件 xe（星魂 ≥N 时这条不生效，用来让高星魂的版本替换它）。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 66, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
def lvE(cid, base):
    for r in range(1, 7):
        for z in (F.RK[str(cid * 100 + r)].get('level_up_skills') or []):
            if str(z.get('id')) == str(base): return r
    raise KeyError(base)

# ================= 引擎 =================
F.rep('      if (x.dk) e.dk = x.dk; if (x.vps != null) e.vps = x.vps;', '      if (x.cyc) e.dcyc = x.cyc; if (x.dki) e.dkIf = x.dki; if (x.xe) e.maxEid = x.xe;   // 轮流挂的几种状态；只在这种状态造成伤害时；星魂 ≥N 时不生效\n      if (x.dk) e.dk = x.dk; if (x.vps != null) e.vps = x.vps;')
F.rep('      if (num(eff.minMaxE) > 0) {', '      if (eff.maxEid != null && src && num((ownerOf(src) || src).eid) >= num(eff.maxEid)) return;   // 星魂 ≥N 时不生效（由星魂里的版本替换）\n      if (num(eff.minMaxE) > 0) {')
F.rep('for (const e of fx(u, "dotHit")) { if (e.dotOwn && (ownerOf(u) || u).id !== d.src) continue; apply(e, u, u.color); } }',
      'for (const e of fx(u, "dotHit")) { if ((e.dotOwn && (ownerOf(u) || u).id !== d.src) || (e.dkIf && e.dkIf !== d.k) || e.__busy) continue; apply(e, u, u.color); } }')
F.rep('''          const key = own.id + ":" + (eff.bk || eff.id), lim = Math.max(1, Math.round(num(eff.stack, 1))), add = Math.max(1, Math.round(num(eff.stAdd, 1)));
          tg.dots = tg.dots || []; let d = tg.dots.find(z => z.key === key);
          if (!d) tg.dots.push(d = { key, src: own.id, n: 0 });
          Object.assign(d, { k: eff.dk || "持续伤害", v, vps: num(eff.vps), stm: !!eff.stm, stat: eff.srcS || "atk", half: !!eff.half, keepSt: eff.keepSt || "", defIg: num(eff.defIg), adjV: num(eff.adjV), cap: lim, left: Math.max(0, Math.round(num(eff.duration))) });
          d.n = eff.over ? d.n + add : Math.min(lim, d.n + add);
          continue;''', '''          const key0 = own.id + ":" + (eff.bk || eff.id), lim = Math.max(1, Math.round(num(eff.stack, 1))), add = Math.max(1, Math.round(num(eff.stAdd, 1)));
          tg.dots = tg.dots || [];
          const put = (key, name, k) => { let d = tg.dots.find(z => z.key === key); if (!d) tg.dots.push(d = { key, src: own.id, n: 0 });
            Object.assign(d, { k: name, v, vps: num(eff.vps), stm: !!eff.stm, stat: eff.srcS || "atk", half: !!eff.half, keepSt: eff.keepSt || "", defIg: num(eff.defIg), adjV: num(eff.adjV), cap: lim, left: Math.max(0, Math.round(num(eff.duration))) });
            d.n = eff.over ? d.n + k : Math.min(lim, d.n + k); };
          if (Array.isArray(eff.dcyc) && eff.dcyc.length) {   // 几种状态轮流挂（海瑟音天赋）：先挂还没有的，都有了就刷新剩余回合最少的
            for (let q = 0; q < add; q++) { const have = eff.dcyc.map(nm => tg.dots.find(z => z.key === key0 + ":" + nm)); let j = have.findIndex(z => !z); if (j < 0) j = have.reduce((b, z, i2) => z.left < have[b].left ? i2 : b, 0); put(key0 + ":" + eff.dcyc[j], eff.dcyc[j], 1); }
          } else put(key0, eff.dk || "持续伤害", add);
          continue;
        }
        if (eff.type === "dotd") {   // 直接造成一次持续伤害类的伤害（海瑟音结界）：cap = 同一时刻最多几次；这次伤害不会再触发这条效果自己
          const own = src ? (ownerOf(src) || src) : null; if (!own || tg.kind !== "enemy") continue;
          const ck = own.id + ":dotd:" + (eff.bk || eff.id), c0 = dotdCnt[ck];
          if (!c0 || Math.abs(c0.t - t) > 1e-9) dotdCnt[ck] = { t, n: 0 };
          if (num(eff.dcap) > 0 && dotdCnt[ck].n >= num(eff.dcap)) continue;
          dotdCnt[ck].n++;
          const mine = dotBag === null, bag = mine ? [] : dotBag; if (mine) dotBag = bag;
          eff.__busy = true;
          try { dotHit(tg, { src: own.id, k: eff.dk || "持续伤害", v, vps: 0, n: 1, stat: eff.srcS || "atk", defIg: num(eff.defIg) }, 1, "direct"); } finally { eff.__busy = false; if (mine) { dotBag = null; dotBagLog(bag, (src ? src.name : "") + " 对 " + tg.name + " 造成持续伤害：", srcColor); } }
          continue;''')
F.rep('    const dotRecs = []; let dotDepth = 0, dotBag = null;', '    const dotRecs = [], dotdCnt = {}; let dotDepth = 0, dotBag = null;')
F.rep('''          try { for (const d of tg.dots.slice()) if (eff.mode !== "own" || (own && d.src === own.id)) dotHit(tg, d, v / 100, "det"); } finally { dotBag = keep; }''',
      '''          try { for (const d of tg.dots.slice()) if ((eff.mode !== "own" || (own && d.src === own.id)) && (!eff.dk || d.k === eff.dk)) dotHit(tg, d, v / 100, "det"); } finally { dotBag = keep; }''')
F.rep('state: "状态", dot: "持续伤害", dotx: "引爆持续伤害",', 'state: "状态", dot: "持续伤害", dotx: "引爆持续伤害", dotd: "造成一次持续伤害",')
F.rep('["dotx", "引爆持续伤害"], ["hpup", "生命上限"],', '["dotx", "引爆持续伤害"], ["dotd", "造成一次持续伤害"], ["hpup", "生命上限"],')

# ================= 海瑟音 1410 =================
c = C[1410]
has('141004', '我方目标攻击时，海瑟音有#1[i]%的基础概率使被击中的敌方目标陷入风化/裂伤/灼烧/触电其中1种状态，且会优先陷入不同的状态')
has('141004', '每回合开始时受到等同于海瑟音#2[f1]%攻击力的风/火/雷属性的持续伤害，持续#5[i]回合'); has('141004', '最多不超过海瑟音攻击力的#4[f1]%')
has('141003', '处于结界中的敌方目标每受到1次持续伤害，海瑟音对其造成等同于自身#4[f1]%攻击力的物理属性持续伤害，该伤害在每回合开始时或我方目标单次攻击后触发，且最多触发#5[i]次。该伤害不会重复触发此效果')
has('141003', '结界持续#2[i]回合，自身每回合开始时结界持续回合数减1'); hast(1410, '盛会的泡沫', '使其当前承受的所有持续伤害立即产生相当于原伤害#1[i]%的伤害')
has('r:141001', '我方目标造成的持续伤害为原伤害的116%'); has('r:141001', '额外使其陷入一次与原天赋效果相同，且可同时存在的风化/裂伤/灼烧/触电状态')
has('r:141006', '次数上限提高至12次，且造成的伤害倍率提高20%')
et, eu = lvE(1410, 141004), lvE(1410, 141003); t10, t12, u10, u12 = prm('141004', 10), prm('141004', 12), prm('141003', 10), prm('141003', 12)
assert r4(t10[1]) == 0.25 and r4(t10[3]) == 0.25 and t10[4] == 2 and r4(u10[3]) == 0.8 and u10[4] == 8 and u10[1] == 3
KINDS = ['风化', '裂伤', '灼烧', '触电']
HX = lambda **k: dict(dict(y='dot', cyc=KINDS, v=r4(t10[1] * 100), lv=[et, r4(t12[1] * 100)], d=2, bk='hx'), **k)
JJ = '结界'
new = list(c['eff']) + [
    HX(t='atk', aw='all', tg='efirst', n='天赋：我方目标攻击时，使被击中的敌方目标陷入风化 / 裂伤 / 灼烧 / 触电其中 1 种（优先不同的），每回合开始受到 25%% 攻击力的持续伤害（%d 魂 27.5%%），持续 2 回合（按主目标；基础概率按命中算；裂伤按上限 25%% 攻击力）' % et),
    dict(y='state', t='ult', o='start', tg='self', sn=JJ, v=1, d=3, ts='start', n='终结技 / 行迹征服的剑旗：展开结界，持续 3 回合（海瑟音每回合开始时 −1）'),
    dict(y='dotd', t='dotHit', tg='evt', dk='结界（物理）', v=r4(u10[3] * 100), lv=[eu, r4(u12[3] * 100)], cap=8, ns=JJ, xe=6, bk='jjd', n='终结技：结界中的敌方目标每受到 1 次持续伤害，海瑟音对其造成 80%% 攻击力的物理属性持续伤害（%d 魂 88%%），同一时刻最多 8 次' % eu),
    dict(y='dotx', t='ult', tg='enemies', v=150, n='行迹盛会的泡沫：施放终结技时，敌方目标当前承受的所有持续伤害立即产生 150% 的伤害'),
    HX(t='start', tg='enemies', sa=2, off=1, n='秘技于海的栖息地：进入战斗后敌方每个单体目标陷入天赋的风化 / 裂伤 / 灼烧 / 触电其中 2 种（用了秘技再启用）'),
]
F.rebuild(1410, new, notes=[n for n in c.get('notes', []) if '持续伤害' not in n] + ['结界的攻击力降低不影响我方；结界的物理持续伤害“每回合开始时或我方单次攻击后最多 8 次”按同一时刻最多 8 次'])
e1 = F.eid(1410, 1)
e1['eff'] = e1.get('eff', []) + [dict(y='dbuf', t='start', tg='team', m='xtra', sc='d', v=16, d=0, bk='e1x', n='E1：海瑟音在场时我方目标造成的持续伤害为原伤害的 116%'),
                                HX(t='atk', aw='all', tg='efirst', bk='hx2', n='E1：通过天赋使敌人陷入状态时，额外再陷入一次相同且可同时存在的风化 / 裂伤 / 灼烧 / 触电状态')]
e1['notes'] = [n for n in e1.get('notes', []) if '持续伤害' not in n]
e6 = F.eid(1410, 6)
e6['eff'] = e6.get('eff', []) + [dict(y='dotd', t='dotHit', tg='evt', dk='结界（物理）', v=r4(u12[3] * 100 + 20), cap=12, ns=JJ, bk='jjd', n='E6：结界的物理持续伤害次数上限提高至 12 次，伤害倍率 +20%%（共 %s%%）' % r4(u12[3] * 100 + 20))]
e6['notes'] = [n for n in e6.get('notes', []) if '持续伤害' not in n]

# ================= 桑博 1108 =================
c = C[1108]
has('110804', '桑博击中敌方目标后有#1[i]%的基础概率使目标陷入风化状态，持续#3[i]回合'); has('110804', '每回合开始时受到等同于桑博#2[i]%攻击力的风属性持续伤害。风化状态最多叠加#4[i]层')
has('110803', '使被攻击的敌方目标受到的持续伤害提高#2[i]%，持续#3[i]回合'); hast(1108, '圈套', '天赋使敌方陷入风化状态的持续时间延长#1[i]回合'); has('r:110806', '天赋施加的风化状态的伤害倍率提高15%')
et, eu = lvE(1108, 110804), lvE(1108, 110803); t10, t12, u10, u12 = prm('110804', 10), prm('110804', 12), prm('110803', 10), prm('110803', 12)
assert r4(t10[1]) == 0.52 and t10[2] == 3 and t10[3] == 5 and r4(u10[1]) == 0.3 and u10[2] == 2
FH = lambda **k: dict(dict(y='dot', dk='风化', v=r4(t10[1] * 100), lv=[et, r4(t12[1] * 100)], stm=1, st=5, d=4, bk='fh', xe=6), **k)
FH6 = lambda **k: dict(dict(y='dot', dk='风化', v=r4(t12[1] * 100 + 15), stm=1, st=5, d=4, bk='fh'), **k)
T = [('basic', 'efirst', 1, '普攻击中'), ('skill', 'efirst', 5, '战技 5 段（都按打在主目标上；多个敌人时游戏里随机分散）'), ('ult', 'enemies', 1, '终结技击中敌方全体')]
new = list(c['eff']) + [FH(t=t, tg=tg, **({'sa': sa} if sa > 1 else {}), n='天赋：%s后使目标陷入风化，每层每回合开始受到 52%% 攻击力的风属性持续伤害（%d 魂 57.2%%），最多 5 层，持续 3 + 1 回合（行迹圈套；基础概率按命中算）' % (w, et)) for t, tg, sa, w in T] + [
    dict(y='dbuf', t='ult', tg='enemies', m='vuln', sc='d', v=r4(u10[1] * 100), lv=[eu, r4(u12[1] * 100)], d=2, bk='dv', n='终结技：被攻击的敌方目标受到的持续伤害 +30%%（%d 魂 32%%），持续 2 回合' % eu)]
F.rebuild(1108, new, notes=[n for n in c.get('notes', []) if '持续伤害' not in n] + ['E1 多出的 1 段战技、E2、E4（引爆 8%）没做'])
e6 = F.eid(1108, 6)
e6['eff'] = e6.get('eff', []) + [FH6(t=t, tg=tg, **({'sa': sa} if sa > 1 else {}), n='E6：%s的风化伤害倍率 +15%%（每层 %s%%）' % (w.split('（')[0], r4(t12[1] * 100 + 15))) for t, tg, sa, w in T]
e6['notes'] = [n for n in e6.get('notes', []) if '风化' not in n]

# ================= 桂乃芬 1210 =================
c = C[1210]
has('121002', '每回合开始时受到等同于桂乃芬#4[i]%攻击力的火属性持续伤害，持续#5[i]回合'); has('121003', '使其当前承受的灼烧状态立即产生相当于原伤害#2[i]%的伤害')
hast(1210, '缘竿', '普攻有#1[i]%的基础概率使敌方目标陷入与战技相同的灼烧状态'); has('r:121002', '灼烧状态的伤害倍率提升40%'); has('r:121004', '桂乃芬施加的灼烧状态每触发一次伤害，使自身恢复2点能量')
es, eu = lvE(1210, 121002), lvE(1210, 121003); s10, s12, u10, u12 = prm('121002', 10), prm('121002', 12), prm('121003', 10), prm('121003', 12)
assert r4(s10[3]) == 2.1821 and s10[4] == 2 and r4(u10[1]) == 0.92
ZS = lambda **k: dict(dict(y='dot', dk='灼烧', v=r4(s10[3] * 100), lv=[es, r4(s12[3] * 100)], d=2, bk='zs', xe=2), **k)
v2 = lambda: [r4(s10[3] * 100 + 40), [es, r4(s12[3] * 100 + 40)]]
ZS2 = lambda **k: dict(dict(y='dot', dk='灼烧', v=v2()[0], lv=v2()[1], d=2, bk='zs'), **k)
P = [('skill', 'efirst', '战技：指定敌方单体'), ('skill', 'eadj', '战技：相邻目标'), ('basic', 'efirst', '行迹缘竿：普攻使目标')]
new = list(c['eff']) + [ZS(t=t, tg=tg, n='%s陷入灼烧，每回合开始受到 218.21%% 攻击力的火属性持续伤害（%d 魂 240.03%%），持续 2 回合（基础概率按命中算）' % (w, es)) for t, tg, w in P] + [
    dict(y='dotx', t='ult', tg='enemies', dk='灼烧', v=r4(u10[1] * 100), lv=[eu, r4(u12[1] * 100)], n='终结技：处于灼烧状态的目标，其当前承受的灼烧状态立即产生 92%% 的伤害（%d 魂 96%%）' % eu)]
F.rebuild(1210, new, notes=[n for n in c.get('notes', []) if '持续伤害' not in n])
e2 = F.eid(1210, 2)
e2['eff'] = e2.get('eff', []) + [ZS2(t=t, tg=tg, n='E2：%s的灼烧伤害倍率 +40%%（按目标已经处于灼烧算）' % w.split('：')[0]) for t, tg, w in P]
e2['notes'] = [n for n in e2.get('notes', []) if '灼烧' not in n]
F.eid(1210, 4)['eff'] = [dict(y='energy', t='dotHit', down=1, dki='灼烧', tg='self', v=2, m='er', n='E4 金枪锁咽喉：桂乃芬施加的灼烧状态每触发一次伤害，恢复 2 点能量')]

# ================= 椒丘 1218 =================
c = C[1218]
has('121804', '也会被视为同时陷入了灼烧状态，每回合开始时受到等同于椒丘#6[i]%攻击力的火属性持续伤害'); has('121804', '【烬煨】最多叠加#4[i]层，持续#5[i]回合')
has('r:121802', '【烬煨】对其造成的火属性持续伤害倍率提高300%')
et = lvE(1218, 121804); t10, t12 = prm('121804', 10), prm('121804', 12)
assert r4(t10[5]) == 1.8 and t10[4] == 2
JW = lambda **k: dict(dict(y='dot', dk='烬煨', v=r4(t10[5] * 100), lv=[et, r4(t12[5] * 100)], d=2, bk='jwd', xe=2), **k)
JW2 = lambda **k: dict(dict(y='dot', dk='烬煨', v=r4(t10[5] * 100 + 300), lv=[et, r4(t12[5] * 100 + 300)], d=2, bk='jwd'), **k)
P = [('basic', 'efirst', '普攻'), ('skill', 'efirst', '战技（主目标）'), ('skill', 'eadj', '战技（相邻目标）'), ('ult', 'enemies', '终结技')]
new = list(c['eff']) + [JW(t=t, tg=tg, n='天赋：%s击中敌人时施加【烬煨】，处于【烬煨】的目标每回合开始受到 180%% 攻击力的火属性持续伤害（%d 魂 198%%），持续 2 回合（基础概率按命中算）' % (w, et)) for t, tg, w in P]
F.rebuild(1218, new, notes=[n for n in c.get('notes', []) if '持续伤害' not in n] + ['终结技结界里“敌人回合开始时再叠 1 层【烬煨】”只影响层数（易伤按叠满），没另做'])
e2 = F.eid(1218, 2)
e2['eff'] = e2.get('eff', []) + [JW2(t=t, tg=tg, n='E2：%s施加的【烬煨】火属性持续伤害倍率 +300%%' % w) for t, tg, w in P]
e2['notes'] = [n for n in e2.get('notes', []) if '持续伤害' not in n]

F.finish('持续伤害第 2 批（海瑟音、桑博、桂乃芬、椒丘）', '''<li><b>2026-11-11（持续伤害第 2 批：海瑟音、桑博、桂乃芬、椒丘）</b>：tv 66（tools/fix66.py）。① <b>海瑟音</b>：天赋——我方每次攻击给主目标挂风化 / 裂伤 / 灼烧 / 触电其中一种（先挂没有的，各 25% 攻击力、2 回合）；终结技结界（3 回合）里敌人每受到 1 次持续伤害，海瑟音再打一次 80% 攻击力的物理持续伤害（同一时刻最多 8 次，E6 12 次、倍率 +20%）；行迹盛会的泡沫终结技引爆 150%；E1 持续伤害 ×116% 并多挂一套。② <b>桑博</b>：风化按层数算（每层 52% 攻击力，最多 5 层，4 回合），普攻 1 层、战技 5 段、终结技全体 1 层；终结技的持续伤害易伤 30%；E6 倍率 +15%。③ <b>桂乃芬</b>：战技 / 普攻的灼烧（218.21% 攻击力，2 回合），终结技引爆灼烧 92%，E2 倍率 +40%，E4 灼烧每次伤害 +2 能量（现在自动算）。④ <b>椒丘</b>：【烬煨】的火属性持续伤害 180% 攻击力，E2 +300%。还是要<b>放了敌人卡</b>才有；基础概率按命中算。<b>对已有配置</b>：有敌人卡并且用到这四人的方案伤害合计变大，桂乃芬 4 魂的能量会变；其他不变。</li>''',
'''2026-11-11（持续伤害第 2 批）：海瑟音（1410）、桑博（1108）、桂乃芬（1210）、椒丘（1218）—— tv 66（tools/fix66.py）。
  改：见更新日志同日条目。新：dot 的 cyc、效果类型 dotd、dotx 的 dk、dotHit 的 dki、条件 xe。
  未改 / 存疑：海瑟音天赋按主目标（群攻实际会打到全部被击中的敌人）、裂伤按上限（25% 攻击力）；结界物理持续伤害“每回合开始时或我方单次攻击后最多 8 次”按同一时刻最多 8 次；桑博战技 5 段都算在主目标上、E1 / E2 / E4 没做；桂乃芬 E2 按目标已经灼烧、【吞火】仍按叠满；椒丘结界里敌人回合开始再叠层没另做。还没做持续伤害的：希露瓦、卢卡、虎克、姬子、艾丝妲。''')
