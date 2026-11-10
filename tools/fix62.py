"""tv 62：全面校对第 6 批（远坂凛 1508、吉尔伽美什 1509、姬子•启行 1510、开拓者 毁灭 8001/8002、存护 8003/8004、同谐 8005/8006；卢卡 1111 补普攻自动强化）。
用法：python3 tools/fix62.py index.html <官方 json 目录>
新功能：触发 spChg（我方消耗或恢复战技点时，每点 1 次）；“sp”效果方式 to（把战技点消耗到 N 点，cntPer = 每消耗 1 点自己的计数 +N）；
计数方式 mod（每 N 点消耗一轮，直到不足 N 点，dcap = 最多几轮；轮数记在行动记录 modN 上给伤害显示用）；条件 maxSP（DB xsp：战技点 ≤N）；
needBk 的属性写 "spd" = 看加速叠层；加速也支持 stAdd；能量方式 evp（事件对象开大消耗能量的 X%）；伤害增益 ovE（DB ove：[门槛, 每点, 上限]，按目标能量上限超出的部分另加）、
伤害增益也认 tgTpl；模板 x.actSt（[状态, 有状态时的动作, 没有时的动作]）、x.ebCnt / x.ebSt（计数 ≥N 或拥有状态时普攻自动变强化普攻）；XR cnt "modN"。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 62, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
X = lambda cid, n: [e for e in C[cid]['eff'] if e.get('n') == n][0]

# ================= 引擎 =================
# 触发 spChg
F.rep('["spUse", "我方消耗战技点时"]', '["spUse", "我方消耗战技点时"], ["spChg", "我方消耗或恢复战技点时"]', 2)
F.rep('spUse: "我方消耗战技点时"', 'spUse: "我方消耗战技点时", spChg: "我方消耗或恢复战技点时"')
F.rep('"aGive", "eMax", "stEnd", "spUse"];', '"aGive", "eMax", "stEnd", "spUse", "spChg"];', 2)
F.rep('      if (type === "basic" || (type === "ebasic" && u.ebSP)) sp = Math.min(spMax, sp + 1);   // ebSP = 这个角色的强普也回战技点（真珠）',
      '      if (type === "basic" || (type === "ebasic" && u.ebSP)) { const s0 = sp; sp = Math.min(spMax, sp + 1); if (sp > s0) teamFire("spChg", u); }   // ebSP = 这个角色的强普也回战技点（真珠）；spChg = 我方消耗或恢复战技点时（远坂凛，按实际变化）')
F.rep('        for (let i = 0; i < need; i++) teamFire("spUse", u);   // 我方消耗战技点时（每点 1 次；米沙天赋）',
      '        for (let i = 0; i < need; i++) { teamFire("spUse", u); teamFire("spChg", u); }   // 我方消耗战技点时（每点 1 次；米沙天赋）')
F.rep('        if (eff.type === "sp") { sp = Math.min(spMax, Math.max(0, sp + v)); continue; }',
      '''        if (eff.type === "sp") {   // 战技点 ±；方式 to = 把战技点消耗到 N 点（远坂凛强化战技）。效果造成的消耗 / 恢复也触发 spUse / spChg（每点 1 次，按实际变化）
          const s0 = sp; sp = eff.mode === "to" ? Math.min(sp, Math.max(0, Math.round(v))) : Math.min(spMax, Math.max(0, sp + v));
          const d = Math.round(sp - s0), who = src ? (ownerOf(src) || src) : null;
          if (d < 0 && eff.mode === "to" && num(eff.cntPer) > 0 && src) addCnt(src, -d * num(eff.cntPer));
          if (d && who && who.kind === "ally" && spDepth < 2) { spDepth++; try { for (let i = 0; i < Math.abs(d); i++) { if (d < 0) teamFire("spUse", who); teamFire("spChg", who); } } finally { spDepth--; } }
          continue;
        }''')
F.rep('    let sp = Math.min(spMax, Math.max(0, num(S.spStart, 3)));\n    const useSP', '    let sp = Math.min(spMax, Math.max(0, num(S.spStart, 3))), spDepth = 0;\n    const useSP')
# 条件 maxSP
F.rep('      if (num(eff.needSP) > 0 && sp < num(eff.needSP)) return;',
      '      if (num(eff.needSP) > 0 && sp < num(eff.needSP)) return;\n      if (eff.maxSP != null && eff.maxSP !== "" && sp > num(eff.maxSP)) return;   // 战技点不超过 N 才生效（远坂凛自在远坂流）')
F.rep('      if (x.nsp) e.needSP = x.nsp;  // 战技点至少这么多才生效',
      '      if (x.nsp) e.needSP = x.nsp;  // 战技点至少这么多才生效\n      if (x.xsp != null) e.maxSP = x.xsp;   // 战技点不超过这么多才生效\n      if (x.cpp) e.cntPer = x.cpp;   // sp 方式 to：每消耗 1 点战技点自己的计数 +N\n      if (x.ove) e.ovE = x.ove;      // 伤害增益：[门槛, 每点 %, 上限 %] 目标能量上限每超过门槛 1 点另加')
# 计数方式 mod
F.rep('          if (eff.mode === "half") subCnt(tg, Math.max((tg.cnt || 0) * 0.5, Math.abs(v)));   // 扣当前的一半，至少扣 |v|',
      '''          if (eff.mode === "mod") {   // 每 |v| 点消耗一轮，直到不足 |v| 点（dcap = 最多几轮）；轮数记在这次行动上给伤害显示用（远坂凛第二魔法实验）
            const k = Math.max(1, Math.abs(Math.round(v))); let n = Math.floor(((tg.cnt || 0) + 1e-9) / k); if (num(eff.dcap) > 0) n = Math.min(n, Math.round(num(eff.dcap)));
            tg.lastCnt = tg.cnt || 0; if (n > 0) subCnt(tg, n * k); if (curRec && curRec.uid === tg.id) curRec.modN = n; continue;
          }
          if (eff.mode === "half") subCnt(tg, Math.max((tg.cnt || 0) * 0.5, Math.abs(v)));   // 扣当前的一半，至少扣 |v|''')
F.rep('${opt([["pct", "加（负数是减）"], ["half", "扣当前的一半，至少扣这么多"], ["set", "设为"]], e.mode === "half" || e.mode === "set" ? e.mode : "pct")}',
      '${opt([["pct", "加（负数是减）"], ["half", "扣当前的一半，至少扣这么多"], ["set", "设为"], ["mod", "每这么多点消耗一轮，直到不足"]], e.mode === "half" || e.mode === "set" || e.mode === "mod" ? e.mode : "pct")}')
# needBk 看加速叠层
F.rep('const b = src.buffs.find(z => z.key === src.id + ":" + eff.needBk[0] + ":d" + eff.needBk[1]);',
      'const b = src.buffs.find(z => z.key === src.id + ":" + eff.needBk[0] + (eff.needBk[1] === "spd" ? "" : ":d" + eff.needBk[1]));')
# 加速 stAdd
F.rep('          let n = lim > 0 ? (oldN >= lim ? oldN : oldN + 1) : 1;   // 已经超过这条的上限（别的效果叠上去的）就不往下压',
      '          let n = lim > 0 ? (oldN >= lim ? oldN : Math.min(lim, oldN + (Math.round(num(eff.stAdd, 1)) || 1))) : 1;   // 已经超过这条的上限（别的效果叠上去的）就不往下压；stAdd = 每次叠几层（吉尔伽美什的兴致）')
# 能量方式 evp
F.rep('          if (eff.mode === "maxp") { if (hasEnergy(tg)',
      '          if (eff.mode === "evp") { const E = evTarget && evTarget.kind === "ally" ? (ownerOf(evTarget) || evTarget) : null; if (E && hasEnergy(E) && !noStdE(E) && hasEnergy(tg)) addEnergy(tg, num(eCfg(E).ultCost, eCfg(E).maxE) * v / 100, false); continue; }   // 固定恢复事件对象这次开大消耗能量的 X%（吉尔伽美什史诗的源头）\n          if (eff.mode === "maxp") { if (hasEnergy(tg)')
# 伤害增益：tgTpl、ovE
F.rep('      if (num(eff.tgE) > 0) tgs = tgs.filter(u => !u.sm && !noStdE(u) && eCfg(u).maxE >= num(eff.tgE));',
      '      if (num(eff.tgE) > 0) tgs = tgs.filter(u => !u.sm && !noStdE(u) && eCfg(u).maxE >= num(eff.tgE));\n      if (eff.tgTpl && !teamT && !onEnemy) tgs = tgs.filter(u => [].concat(eff.tgTpl).map(Number).includes((tplOf(u) || {}).id));   // 只给某个角色（远坂凛秉持优雅：Archer）')
F.rep('        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: amt0 * n, n };',
      '        const ovx = Array.isArray(eff.ovE) && tg.kind === "ally" && !tg.sm && !noStdE(tg) ? Math.min(num(eff.ovE[2]), Math.max(0, eCfg(tg).maxE - num(eff.ovE[0])) * num(eff.ovE[1])) : 0;   // 目标能量上限超过门槛的部分另加（吉尔伽美什王霸的竞逐）\n        if (Array.isArray(eff.ovE) && !(ovx > 0) && !(amt0 > 0)) continue;\n        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: (amt0 + ovx) * n, n };')
# 行动选择：模板 actSt / ebCnt / ebSt
F.rep('      actOf.nat = (f && f.act) || (u.act === "basic" || u.act === "ebasic" ? u.act : "skill");   // 不单独指定时会用的动作（角色卡“每次行动”用）\n      const a = (u.actOv && u.actOv[key]) || actOf.nat;',
      '''      const X = tx(u), aS = Array.isArray(X.actSt) ? (hasSt(u, String(X.actSt[0])) ? X.actSt[1] : X.actSt[2]) : null;   // 模板 actSt：有 / 没有某个状态时固定用哪种行动（吉尔伽美什【来兴致了！】前只能普攻、之后只能战技）
      actOf.nat = (f && f.act) || aS || (u.act === "basic" || u.act === "ebasic" ? u.act : "skill");   // 不单独指定时会用的动作（角色卡“每次行动”用）
      let a = (u.actOv && u.actOv[key]) || actOf.nat;
      if (a === "basic" && ((num(X.ebCnt) > 0 && num(u.cnt) >= num(X.ebCnt) - 1e-9) || (X.ebSt && hasSt(u, String(X.ebSt))))) a = "ebasic";   // 普攻自动强化：计数 ≥N 或拥有某个状态（开拓者•存护【灼热意志】、卢卡【斗志】）''')
# 伤害层
F.rep('const S2ST = { "1109": a => (a.sts || []).includes("强化战技"),', 'const S2ST = { "1508": a => (a.sts || []).includes("第二魔法实验"), "1109": a => (a.sts || []).includes("强化战技"),')
F.rep('r.cnt === "bnc" ? bnc() : num(r.cnt, 1)) * xrN(o, r);', 'r.cnt === "bnc" ? bnc() : r.cnt === "modN" ? Math.max(0, num(rec.modN) - 1) : num(r.cnt, 1)) * xrN(o, r);')

# ================= 卢卡 1111：【斗志】≥2 时普攻自动强化 =================
has('111104', '【斗志】'); C[1111].setdefault('x', {})['ebCnt'] = 2

# ================= 远坂凛 1508 =================
c = C[1508]
has('150804', '进入战斗时，获得#1[i]点【宝石能量】。我方目标消耗或恢复战技点时，使其暴击伤害提高#3[i]%，持续#2[i]回合，且每消耗或恢复1点战技点就使远坂凛获得1点【宝石能量】')
has('150804', '若远坂凛持有的【宝石能量】大于等于#5[i]点或当前战技点大于等于#4[i]点，战技强化为【第二魔法实验】')
has('150809', '之后，消耗#2[i]点【宝石能量】对敌方随机单体目标额外造成'); has('150809', '施放时，若当前战技点大于#5[i]点，将战技点消耗至#5[i]点，每消耗1点立即获得#4[i]点【宝石能量】')
has('150805', '若战技点小于等于#3[i]点或本次【回路连接】状态已主动施放5次【伪•螺旋剑】'); has('150805', '并为我方恢复#2[i]个战技点')
hast(1508, '财源广进', '远坂凛施放终结技时，获得12点【宝石能量】'); hast(1508, '淑女风范', '进入战斗时和施放强化战技后，远坂凛的速度提高20%，持续3回合')
hast(1508, '秉持优雅', '若Archer在队伍中，Archer也会获得该效果'); has('150807', '下一次战斗开始时获得#1[i]点【宝石能量】')
p4 = prm('150804', 10); assert p4[0] == 20 and p4[4] == 15 and p4[3] == 7
ST = '第二魔法实验'
s0, s1 = X(1508, '行迹淑女风范'), X(1508, '行迹淑女风范：施放强化战技后速度 +20%（请在强化战技时启用）')
fu, spf, spu, smx, vul = X(1508, '天赋：Archer 施放伪•螺旋剑后（战技点 ≤3 或已施放 5 次）和 Archer 连携追加攻击，恢复 4 个战技点（远坂凛回合内 1 次）'), X(1508, '天赋：连携追加攻击恢复 4 个战技点'), X(1508, '终结技：恢复 1 个战技点'), X(1508, '远坂凛在场时战技点上限 +2'), X(1508, '终结技：敌方全体受到的伤害 +20%，持续 3 回合')
cdo, cds = X(1508, '天赋宝石魔术：我方目标消耗战技点（施放战技）时暴击伤害 +70%，持续 2 回合'), X(1508, '天赋宝石魔术：终结技恢复战技点时远坂凛暴击伤害 +70%，持续 2 回合')
ak, rp = X(1508, '行迹秉持优雅：进入战斗时攻击力 +150%（Archer 也有，请在 Archer 卡上自己加）'), X(1508, '行迹秉持优雅：量子属性抗性穿透 +15%')
o = {k: e['n'] for k, e in dict(s0=s0, s1=s1, fu=fu, spf=spf, cdo=cdo, cds=cds, ak=ak).items()}
s0.update(bk='sn', n='行迹淑女风范：进入战斗时速度 +20%，持续 3 回合')
s1.update(bk='sn', ns=ST, n='行迹淑女风范：施放强化战技后速度 +20%，持续 3 回合'); s1.pop('off', None)
fu.update(at=1015, xsp=3, n='天赋自在远坂流：Archer 施放【伪•螺旋剑】攻击后，若战技点 ≤3，远坂凛和 Archer 发动连携追加攻击（每回合 1 次，远坂凛回合开始时重置；“本次回路连接已主动施放 5 次”没判断）'); fu.pop('off', None)
spf['n'] = '天赋自在远坂流：连携追加攻击为我方恢复 4 个战技点'; spf.pop('off', None)
cdo.update(t='spChg', aw='others', tg='evt', cnt='own', n='天赋宝石魔术：我方目标消耗或恢复战技点时，使其暴击伤害 +70%（5 魂 77%），持续 2 回合')
cds.update(t='spChg', aw='self', tg='self', st=1, ste=[4, 2], n='天赋宝石魔术：远坂凛自己消耗或恢复战技点时暴击伤害 +70%（5 魂 77%），持续 2 回合（4 魂起可叠 2 层）'); cds.pop('o', None)
ak['n'] = '行迹秉持优雅：进入战斗时远坂凛攻击力 +150%'
new = [
    dict(y='count', t='start', tg='self', v=20, n='天赋宝石魔术：进入战斗时获得 20 点【宝石能量】'),
    dict(y='count', t='start', tg='self', v=10, off=1, n='秘技转换充能：下一次战斗开始时获得 10 点【宝石能量】（用了秘技再启用）'),
    s0,
    dict(y='state', t='skill', tg='self', sn=ST, v=1, d=0, nc=15, n='天赋宝石魔术：【宝石能量】≥15 点时战技强化为【第二魔法实验】（不消耗战技点）'),
    dict(y='state', t='skill', tg='self', sn=ST, v=1, d=0, nsp=7, n='天赋宝石魔术：当前战技点 ≥7 点时战技强化为【第二魔法实验】'),
    dict(y='sp', t='skill', tg='self', m='to', v=2, cpp=2, ns=ST, n='强化战技第二魔法实验：施放时若战技点大于 2 点，将战技点消耗至 2 点，每消耗 1 点立即获得 2 点【宝石能量】'),
    dict(y='count', t='skill', tg='self', m='mod', v=3, cap=33, ns=ST, n='强化战技第二魔法实验：每消耗 3 点【宝石能量】额外造成 1 次伤害，重复直至不足 3 点（最多 33 轮）'),
    s1,
    dict(y='state', t='ally', aw='self', aa=['skill'], tg='self', sn=ST, v=0, n='强化战技结束后变回普通战技（下次施放战技时重新判断）'),
    dict(y='count', t='spChg', aw='all', tg='self', v=1, n='天赋宝石魔术：我方目标每消耗或恢复 1 点战技点，远坂凛获得 1 点【宝石能量】'),
    cdo, cds, spu,
    dict(y='count', t='ult', tg='self', v=12, n='行迹财源广进：施放终结技时获得 12 点【宝石能量】'),
    vul, fu, spf, smx, ak, rp,
    dict(y='dbuf', t='start', tg='others', tt=1015, m='atkP', v=150, d=0, bk='yy', n='行迹秉持优雅：Archer 在队伍中时，Archer 的攻击力也 +150%'),
    dict(y='dbuf', t='start', tg='others', tt=1015, m='resPen', v=15, d=0, bk='yyp', n='行迹秉持优雅：Archer 的量子属性抗性穿透也 +15%'),
]
F.rebuild(1508, new, rename={o['s0']: s0['n'], o['s1']: s1['n'], o['fu']: fu['n'], o['spf']: spf['n'], o['cdo']: cdo['n'], o['cds']: cds['n'], o['ak']: ak['n']},
          off0=[o['s1'], o['fu'], o['spf']], x={'freeSkSt': [ST, 0]}, cnt={'n': '宝石能量', 'at': 0}, set={'cntName': '宝石能量', 'cntAt': 0},
          notes=['战技点已满时恢复的战技点不算“恢复”（按实际变化算）；连携追加攻击里 Archer 的 300% 攻击力伤害没算；E1【影子宝石】没做'])
e4 = F.eid(1508, 4); e4['eff'] = []; e4['notes'] = ['E4 红色•恶魔•三倍速：【宝石魔术】的暴击伤害对远坂凛可叠 2 层（已并进天赋那条效果，4 魂起自动生效）']
has('r:150806', '施放终结技时，获得24点【宝石能量】和1个额外回合')
F.eid(1508, 6)['eff'].insert(0, dict(y='count', t='ult', tg='self', v=24, n='E6 这次没掉链子！：施放终结技时获得 24 点【宝石能量】'))
F.xr(1508, [dict(k='gem', n='强化战技第二魔法实验：每消耗 3 点【宝石能量】额外 1 次 90% 攻击力伤害（3 魂 99%；按这次实际消耗的轮数，第 1 次已算在倍率里）', on=['s2'], st='atk', v=[0.9, 0.99], lk='s', cnt='modN')])

# ================= 吉尔伽美什 1509 =================
c = C[1509]
F.OLD[1509] = list(dict.fromkeys(F.OLD[1509]))
has('150904', '初始自身回合开始时自动施放普攻。我方其他目标行动时，吉尔伽美什获得1点【兴致】，每拥有1点【兴致】使自身速度提高')
has('150904', '当【兴致】首次达到#2[i]点时，进入【来兴致了！】状态，该状态下仅能施放战技，且持续整场战斗。施放战技后，清空自身【兴致】')
has('150905', '吉尔伽美什或Saber攻击时累计1点攻击计数'); has('150905', 'Saber固定恢复#4[i]点能量并使自身下一次施放终结技时，造成的伤害为原伤害的#6[i]%')
hast(1509, '史诗的源头', '吉尔伽美什额外获得2点【兴致】，并固定恢复等同于本次消耗能量值30%的能量')
hast(1509, '英雄的孤傲', '吉尔伽美什每获得1点【兴致】，使自身暴击伤害提高25%，该效果最多叠加6层')
hast(1509, '王霸的竞逐', '若目标能量上限大于140，每超过1点能量上限使攻击力和暴击伤害额外提高1%，最多额外提高100%')
has('150907', '且吉尔伽美什立即获得3点【兴致】')
p5 = prm('150905', 10); assert p5[3] == 120 and p5[4] == 8 and p5[5] == 2 and prm('150905', 12)[5] == 2.16
LX = '来兴致了！'
XZ = lambda **k: dict(dict(y='spd', tg='self', v=10, d=0, m='pct', st=99, bk='xz'), **k)
GA = lambda **k: dict(dict(y='dbuf', tg='self', m='cd', v=25, st=6, d=0, bk='ga'), **k)
ST_ = lambda t, o_, n: dict(dict(y='state', t=t, tg='self', sn=LX, v=1, d=0, nbk=['xz', 'spd', 10], ns='!' + LX, n=n), **({'o': o_} if o_ else {}))
ct, fu, clr = X(1509, '天赋：吉尔伽美什攻击时 +1 攻击计数（Saber 的攻击请自己加）'), X(1509, '天赋：攻击计数满 8 时和 Saber 发动连携追加攻击'), X(1509, '天赋：来兴致了！状态下施放战技后清空兴致（速度加成归零）')
en, wl, wb, wa, wc = X(1509, '行迹史诗的源头：其他角色施放终结技时固定恢复其消耗能量的 30%（按能量上限 120 算 36，请按队友改）'), X(1509, '战技：【王来承认】自身造成伤害时无视目标 30% 防御力，持续 3 回合'), X(1509, '天赋：队友施放终结技时自身终结技伤害 +40%，持续 3 回合'), X(1509, '行迹王霸的竞逐：我方全体攻击力 +20%（能量上限超过 140 的额外部分没算）'), X(1509, '行迹王霸的竞逐：我方全体暴击伤害 +20%')
o = {k: e['n'] for k, e in dict(ct=ct, en=en, wa=wa).items()}
ct['n'] = '天赋：吉尔伽美什攻击时累计 1 点攻击计数'
en.update(m='evp', v=30, n='行迹史诗的源头：我方其他角色施放终结技时，固定恢复等同于本次消耗能量值 30% 的能量')
wa['n'] = '行迹王霸的竞逐：吉尔伽美什在场时我方全体攻击力 +20%'
N_ALLY, N_GA = '天赋：我方其他目标行动时 +1 兴致（每点速度 +10%）', '行迹英雄的孤傲：每获得 1 点兴致暴击伤害 +25%，最多 6 层（按其他目标行动算，连携和开大的兴致没另算）'
new = [
    ct,
    dict(y='count', t='atk', aw='others', at=1014, nf=1, tg='self', v=1, n='天赋：Saber 攻击时累计 1 点攻击计数'),
    fu,
    XZ(t='ally', aw='others', n=N_ALLY),
    GA(t='ally', aw='others', n='行迹英雄的孤傲：每获得 1 点【兴致】暴击伤害 +25%，最多 6 层（其他目标行动的 1 点）'),
    XZ(t='fua', sa=3, n='天赋：连携追加攻击后 +3 兴致'),
    GA(t='fua', sa=3, n='行迹英雄的孤傲：暴击伤害 +25% / 层（连携追加攻击的 3 点）'),
    dict(y='energy', t='fua', tg='others', tt=1014, m='fixed', v=120, n='天赋：连携追加攻击后 Saber 固定恢复 120 点能量'),
    dict(y='dbuf', t='fua', tg='others', tt=1014, m='xtra', sc='u', v=100, lv=[5, 116], d=0, bk='sab', n='天赋：连携追加攻击后 Saber 下一次施放终结技造成的伤害为原伤害的 200%（5 魂 216%）'),
    dict(y='dbuf', t='aUlt', aw='others', at=1014, tg='evt', m='xtra', sc='u', v=0, d=0, bk='sab', n='天赋：Saber 施放终结技后，上面的 200% 用掉'),
    XZ(t='ult', sa=2, n='行迹史诗的源头：施放终结技时 +2 兴致'),
    GA(t='ult', sa=2, n='行迹英雄的孤傲：暴击伤害 +25% / 层（自己终结技的 2 点）'),
    XZ(t='aUlt', aw='others', sa=2, n='行迹史诗的源头：其他角色施放终结技时 +2 兴致'),
    GA(t='aUlt', aw='others', sa=2, n='行迹英雄的孤傲：暴击伤害 +25% / 层（其他角色终结技的 2 点）'),
    en,
    XZ(t='start', sa=3, off=1, n='秘技天之锁：进入战斗后立即获得 3 点【兴致】（用了秘技再启用；200% 攻击力的伤害没算）'),
    ST_('ally', 'fua', '天赋：【兴致】首次达到 10 点时进入【来兴致了！】状态，此后只能施放战技（其他目标行动 / 连携追加攻击后判断）'),
    ST_('ult', 'aUlt', '天赋：【兴致】首次达到 10 点时进入【来兴致了！】（施放终结技 / 队友施放终结技后判断）'),
    ST_('start', None, '天赋：【兴致】首次达到 10 点时进入【来兴致了！】（进入战斗时判断）'),
    clr, wl, wb, wa, wc,
    dict(y='dbuf', t='start', tg='allies', m='atkP', v=0, ove=[140, 1, 100], d=0, n='行迹王霸的竞逐：目标能量上限每超过 140 点 1 点，攻击力额外 +1%，最多 +100%'),
    dict(y='dbuf', t='start', tg='allies', m='cd', v=0, ove=[140, 1, 100], d=0, n='行迹王霸的竞逐：目标能量上限每超过 140 点 1 点，暴击伤害额外 +1%，最多 +100%'),
]
new[18]['aw'] = 'others'; new[16]['aw'] = 'others'; new[17]['aw'] = 'others'
F.rebuild(1509, new, rename={o['ct']: ct['n'], o['en']: en['n'], o['wa']: wa['n'], N_GA: new[4]['n']},
          x={'actSt': [LX, 'skill', 'basic']},
          notes=['【来兴致了！】之前每回合自动普攻、之后只能战技（卡片“每次行动”里单独指定的仍然优先）；连携追加攻击里 Saber 的 600% 攻击力伤害没算'])
e2 = F.eid(1509, 2)
e2['eff'] = [XZ(t='start', sa=5, n='E2 通晓万物之智：进入战斗时获得 5 点【兴致】'), GA(t='start', sa=5, n='E2：行迹英雄的孤傲的暴击伤害（进入战斗的 5 点）'),
             XZ(t='ult', sa=5, n='E2：施放终结技时额外获得 5 点【兴致】'), GA(t='ult', sa=5, n='E2：行迹英雄的孤傲的暴击伤害（终结技额外的 5 点）')]
has('r:150906', '队友施放终结技时，吉尔伽美什获得1点【黄金律】，最多累计3点。自身施放终结技时消耗全部【黄金律】，每消耗1点【黄金律】使造成的终结技伤害的暴击伤害提高100%')
e6 = F.eid(1509, 6)
for x in e6['eff']: x['n'] = x['n'].replace('（黄金律的终结技暴伤没算）', '')
e6['eff'] += [dict(y='dbuf', t='aUlt', aw='others', tg='self', m='cd', sc='u', v=100, st=3, d=0, bk='hjl', n='E6：队友施放终结技时获得 1 点【黄金律】（最多 3 点），每点使终结技伤害的暴击伤害 +100%'),
              dict(y='dbuf', t='aUlt', aw='self', tg='self', m='cd', sc='u', v=0, d=0, bk='hjl', n='E6：自身施放终结技时消耗全部【黄金律】')]
has('r:150902', '对主目标造成的伤害倍率提高100%，对相邻目标造成的伤害倍率提高50%'); has('r:150906', '弹射伤害倍率提高80%')
F.xr(1509, [dict(k='e2', n='E2：战技【王之财宝】对主目标的伤害倍率 +100%', on=['s'], st='atk', v=[1.0], e=2),
            dict(k='e2a', n='E2：战技对相邻目标的伤害倍率 +50%', on=['s'], st='atk', v=[0.5], e=2, cnt='adj'),
            dict(k='e6', n='E6：终结技 10 次弹射的伤害倍率各 +80%', on=['u'], st='atk', v=[8.0], e=6)])

# ================= 姬子•启行 1510 =================
c = C[1510]
has('151002', '姬子•启行获得【领航旗语】，持续#2[i]回合，姬子•启行每回合开始时持续回合数减1。当姬子•启行拥有【领航旗语】时，我方全体造成的伤害提高')
has('151003', '对指定敌方单体最多造成等同于姬子•启行#9[i]%攻击力的火属性伤害，对其他目标最多造成等同于姬子•启行#10[i]%攻击力的火属性伤害')
hast(1510, '人类该向何处去', '回合开始时，若当前助战技使用次数等于当前使用次数上限，姬子•启行额外恢复5点能量')
LH = '领航旗语'
qy = X(1510, '战技：【领航旗语】期间我方全体造成的伤害 +20%，持续 3 回合'); oq = qy['n']
qy.update(d=0, bk='st:' + LH, n='战技：拥有【领航旗语】时我方全体造成的伤害 +20%（5 魂 22%）')
new = []
for e in c['eff']:
    if e is qy:
        new.append(dict(y='state', t='skill', tg='self', sn=LH, v=1, d=3, ts='start', n='战技：姬子•启行获得【领航旗语】，持续 3 回合（每回合开始时持续回合数 −1）'))
    new.append(e)
new.append(dict(y='energy', t='turn', tg='self', v=5, m='er', off=1, n='行迹人类该向何处去：回合开始时，若助战技使用次数等于使用次数上限，额外恢复 5 点能量（这回合之前没人用助战技时启用）'))
F.rebuild(1510, new, rename={oq: qy['n']},
          notes=[n for n in c.get('notes', []) if '人类该向何处去' not in n] + ['助战技（谁在什么时候用）页面没法自动判断：其他角色使用助战技恢复 4 点能量、额外回合、【同行协议】发动的额外助战技、【源能】都要自己用手动事件 / 效果加'])
D = F.DMG['1510']['u']; pu = F.SK['151003']['params']
assert r4(pu[9][8]) == 7.62 and r4(pu[9][9]) == 2.52 and D['v'][9] == 7.62
D.update(tg=4, adj=[r4(p[9]) for p in pu])   # 主目标最多 762%、其他目标最多 252%（原来按全体 762%）

# ================= 开拓者•毁灭 8001 / 8002 =================
for cid in (8001, 8002):
    c = C[cid]; sid = str(cid)
    has('800104', '每次击破敌方目标的弱点后，攻击力提高'); has('r:800106', '开拓者消灭敌方目标时，也会触发天赋')
    hast(cid, '坚韧', '天赋的效果每层同时使开拓者的防御力提高10%')
    tf = F.eff(cid, '天赋牵制盗垒')
    new = []
    for e in c['eff']:
        new.append(e)
        if e is tf: new.append(dict(y='dbuf', t='break', tg='self', m='defP', v=10, st=2, d=0, bk='jr', n='行迹坚韧：天赋的效果每层同时使防御力 +10%'))
    F.rebuild(cid, new, set={'atkUlt': True})
    c['x'].pop('atkUlt')   # 终结技是攻击（官方类型写“强化”，实际两种模式都造成伤害）：去掉“不算攻击”
    e6 = F.eid(cid, 6)
    e6['eff'] = [dict(y='dbuf', t='kill', tg='self', m='atkP', v=20, lv=[3, 22], st=2, d=0, bk='qz', n='E6 拓宇行天的意志：消灭敌方目标时也会触发天赋（攻击力 +20%，最多 2 层）'),
                 dict(y='dbuf', t='kill', tg='self', m='defP', v=10, st=2, d=0, bk='jr', n='E6：消灭敌方目标触发天赋时，行迹坚韧的防御力 +10% 也叠 1 层')]
    e6['notes'] = []
    ps = F.SK['800102']['params']; assert r4(ps[9][0]) == 1.25
    F.DMG[sid]['s'] = dict(v=[r4(p[0]) for p in ps], adj=[r4(p[0]) for p in ps], rnd=[], tg=2, el=0, stat='atk', n='安息全垒打', max=15)

# ================= 开拓者•存护 8003 / 8004 =================
ZY, FREE = '灼热意志', '炎枪强化'
for cid in (8003, 8004):
    c = C[cid]; sid = str(cid)
    has('800304', '每受到1次攻击，叠加1层【灼热意志】，最多可叠加#3[i]层'); has('800304', '【灼热意志】层数不低于4时，普攻将获得强化')
    has('800304', '开拓者施放普攻、战技、终结技后，为我方全体提供能够抵消'); has('800308', '消耗4层【灼热意志】，强化普攻')
    has('800301', '并叠加1层【灼热意志】'); has('800302', '并叠加1层【灼热意志】'); has('800303', '下一次施放普攻时，自动获得强化且不消耗【灼热意志】')
    has('r:800304', '战斗开始时，立即获得4层【灼热意志】'); has('800307', '下一次战斗开始时给自身提供能够抵消')
    new = [
        dict(y='count', t='ally', aw='self', aa=['basic'], tg='self', v=1, n='普攻：叠加 1 层【灼热意志】（最多 8 层；≥4 层时普攻自动强化）'),
        dict(y='count', t='skill', tg='self', v=1, n='战技：叠加 1 层【灼热意志】'),
        dict(y='count', t='hit', tg='self', v=1, n='天赋筑城者遗宝：每受到 1 次攻击，叠加 1 层【灼热意志】'),
        dict(y='count', t='ebasic', tg='self', v=-4, ns='!' + FREE, n='强化普攻：消耗 4 层【灼热意志】'),
        dict(y='state', t='ebasic', tg='self', sn=FREE, v=0, n='终结技给的强化用掉（这次强化普攻不消耗【灼热意志】）'),
        dict(y='state', t='ult', tg='self', sn=FREE, v=1, d=0, n='终结技：下一次施放普攻时自动获得强化且不消耗【灼热意志】'),
        dict(y='shield', t='basic', o='skill', tg='allies', v=0, n='天赋筑城者遗宝：施放普攻、战技后为我方全体提供护盾（6% 防御力 +80，3 魂 6.4% +89），持续 2 回合'),
        dict(y='shield', t='ult', tg='allies', v=0, n='天赋筑城者遗宝：施放终结技后为我方全体提供护盾，持续 2 回合'),
        dict(y='shield', t='start', tg='self', v=0, off=1, n='秘技守护者召令：下一次战斗开始时给自身提供护盾（30% 防御力 +384），持续 1 回合（用了秘技再启用）'),
    ] + list(c['eff'])
    F.rebuild(cid, new, x={'ebCnt': 4, 'ebSt': FREE}, cnt={'n': ZY, 'at': 0, 'max': 8}, set={'cntName': ZY, 'cntAt': 0, 'cntMax': 8},
              notes=['战技的嘲讽和受到的伤害降低、行迹强援弱（我方全体受到的伤害降低 15%）不影响行动轴，没做；护盾数值不算（只触发“受到护盾时”）'])
    e4 = F.eid(cid, 4); e4['eff'] = [dict(y='count', t='start', tg='self', v=4, n='E4 驻留文明的誓言：战斗开始时立即获得 4 层【灼热意志】')]; e4['notes'] = []
    pb = F.SK['800308']['params']; assert r4(pb[5][0]) == 1.35 and r4(pb[5][1]) == 0.54
    F.DMG[sid]['b2'] = dict(v=[r4(p[0]) for p in pb], adj=[r4(p[1]) for p in pb], rnd=[], tg=2, el=0, stat='atk', n='穿彻坚冰的烈芒（强化）', max=10)
    pu = F.SK['800303']['params']; assert r4(pu[9][0]) == 1.0 and r4(pu[9][1]) == 1.5 and F.DMG[sid]['u']['stat'] == 'def'
    F.xr(cid, [dict(k='ua', n='终结技：另有 100% 攻击力的部分（5 魂 110%；倍率表里只有 150% 防御力）', on=['u'], st='atk', v=[1.0, 1.1], lk='u', cnt='N')])

# ================= 开拓者•同谐 8005 / 8006 =================
for cid in (8005, 8006):
    has('r:800506', '战技的额外伤害次数增加2次')
    e6 = F.eid(cid, 6)
    e6['eff'] = [dict(y='energy', t='skill', tg='self', v=12, m='er', n='E6 明天，栖息聚光之下：战技的额外伤害次数 +2（每次伤害回 6 点能量，共多回 12 点）')]; e6['notes'] = []
    F.xr(cid, [dict(k='e6', n='E6：战技额外 2 次伤害（各 50% 攻击力，3 魂 55%）', on=['s'], st='atk', v=[1.0, 1.1], lk='s', e=6)])
    C[cid]['notes'] = [n for n in C[cid].get('notes', [])] + ['终结技【伴舞】（击破特攻 +30%、超击破）、行迹卫我起舞 / 随波逐流、秘技、E4 都只影响击破，页面不算击破伤害，没做']

F.finish('全面校对第 6 批（远坂凛、吉尔伽美什、姬子•启行、开拓者毁灭 / 存护 / 同谐）', '''<li><b>2026-11-10（全面校对第 6 批：远坂凛、吉尔伽美什、姬子•启行、开拓者毁灭 / 存护 / 同谐）</b>：逐条对照原文，tv 62（tools/fix62.py）。① <b>远坂凛</b>：【宝石能量】做成计数（进入战斗 20 点、我方每消耗或恢复 1 点战技点 +1、终结技 +12、6 魂 +24、秘技 +10 默认关）；<b>≥15 点或战技点 ≥7 时战技自动强化为【第二魔法实验】</b>：不耗战技点，把战技点消耗到 2 点（每点 +2 宝石能量），每 3 点宝石能量多 1 次伤害直到不足 3 点，之后速度 +20% 3 回合；暴击伤害改成“我方目标消耗或恢复战技点时”给那个目标（原来只在施放战技 / 终结技时）；连携追加攻击按原文默认开（只认 Archer 的战技、战技点 ≤3）；行迹秉持优雅 Archer 也获得。② <b>吉尔伽美什</b>：<b>【来兴致了！】之前自动普攻、兴致首次到 10 点后只能战技</b>（不用再手动点）；兴致合并成一条（连携 +3、终结技 +2、E2 +5），行迹英雄的孤傲的暴击伤害按每次实际获得的兴致叠；Saber 的攻击也计数，连携后 Saber 回 120 能量、下一次终结技 200%；行迹史诗的源头按队友实际能量上限的 30%（原来固定 36）；行迹王霸的竞逐补“能量上限每超过 140 点 1 点 +1%，最多 +100%”；E2 战技倍率、E6 弹射倍率和【黄金律】进伤害。③ <b>姬子•启行</b>：【领航旗语】做成状态（3 回合，回合开始时 −1），增伤跟着状态；终结技伤害改成主目标 762% + 其他目标 252%（原来按全体 762%）。④ <b>开拓者•存护</b>：【灼热意志】做成计数（普攻 / 战技 / 受到攻击 +1，最多 8 层，E4 开局 4 层），<b>≥4 层时普攻自动变强化普攻</b>并消耗 4 层，终结技后下一次普攻免费强化；天赋护盾、强化普攻倍率 135% + 相邻 54%、终结技的 100% 攻击力部分补上。⑤ <b>开拓者•毁灭</b>：终结技算攻击、补战技倍率（125% 扩散）、行迹坚韧、E6。⑥ <b>开拓者•同谐</b>：E6 多 2 次伤害（多回 12 能量）。⑦ <b>卢卡</b>：【斗志】≥2 层时普攻自动变直冲碎天拳。新触发“我方消耗或恢复战技点时”。<b>对已有配置</b>：用到这些角色的方案行动顺序会变（远坂凛的战技点 / 速度、吉尔伽美什开局普攻、存护主强化普攻）；其他角色不变。</li>''',
'''2026-11-10（全面校对第 6 批）：远坂凛（1508）、吉尔伽美什（1509）、姬子•启行（1510）、开拓者•毁灭（8001 / 8002）、存护（8003 / 8004）、同谐（8005 / 8006）—— tv 62（tools/fix62.py）。AvatarSkillConfigLD：远坂凛第二魔法实验 BPNeed −1、SPBase 30；吉尔伽美什战技 BPNeed −1。
  改：见更新日志同日条目。新触发 spChg；sp 方式 to + cntPer（cpp）；计数方式 mod；条件 maxSP（xsp）；needBk 属性 "spd"；加速 stAdd；能量方式 evp；伤害增益 ovE（ove）、tgTpl；模板 x.actSt / x.ebCnt / x.ebSt；XR cnt "modN"。
  核对无误：远坂凛终结技 +1 战技点、易伤 20%/22% 3 回合、战技点上限 +2、E2 / E6；吉尔伽美什王来承认 30%/33% 3 回合、王来背负 40%/44%、攻击计数 8、E1 / E4；姬子•启行秘技进战施放战技、天赋穿透 20%/22%、暴伤 80%/88%、同行协议（默认关）、E2 / E4 / E6；开拓者•毁灭行迹蓄势 +15、斗志 25%、秘技、E1 / E2 / E4；存护行迹生先死 5%、行胜思（默认关）、E1 / E6；同谐战技 5×6 能量、天赋 +10/11、剧院之帽 30%、E1 / E2。
  未改 / 存疑：远坂凛战技点已满时“恢复”算不算原文没写（按实际变化）、E1【影子宝石】没做、连携“已主动施放 5 次”没判断；吉尔伽美什和 Saber 连携里 Saber 的伤害没算；姬子•启行的助战技整套（使用次数、其他角色使用回 4 能量和额外回合、同行协议额外助战技、源能）要手动加；开拓者•毁灭终结技只按【全胜•再见安打】算伤害；存护的行胜思要知道有没有护盾，仍默认关；同谐 E6 多出的 2 次伤害按每次 6 点回能（原文没单独写）。''')
