"""tv 59：全面校对第 3 批（米沙 1312、星期日 1313、翡翠 1314、波提欧 1315、乱破 1317）。
用法：python3 tools/fix59.py index.html <官方 json 目录>
新功能：触发 spUse（我方消耗战技点时，每点 1 次）；目标 skpickm（战技目标和它的召唤物）；条件 xPath（DB xp：目标是这个命途就跳过）、
stOn "sk"（看战技目标身上的状态）、hitEq（DB hn：这次攻击正好击中 N 个敌人）、needBk（DB nbk：[bk, 属性, N] 自己这组增益至少 N 层）、
minEid（DB me：几魂起才生效，写在基础效果里）；能量 eMin（DB emn：按能量上限 % 回能时至少回多少）；
伤害增益 tHasSm（DB ths：目标有召唤物才给）、durE（DB de：[几魂, 回合]）、stAdd 可以是负数（减层，减到 0 移除）。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 59, sys.argv[2])
C, prm, has = F.C, F.prm, F.has
TRS = lambda cid: {F.TR[t]['name']: F.TR[t]['desc'] for t in F.CH[str(cid)]['skill_trees'] if F.TR[t].get('desc')}

# ================= 引擎 =================
F.rep('        sp = Math.max(0, sp - need);\n        return short;',
      '        sp = Math.max(0, sp - need);\n        for (let i = 0; i < need; i++) teamFire("spUse", u);   // 我方消耗战技点时（每点 1 次；米沙天赋）\n        return short;')
F.rep('["eMax", "我方角色能量达到上限时"]', '["eMax", "我方角色能量达到上限时"], ["spUse", "我方消耗战技点时"]', 2)
F.rep('eMax: "我方角色能量达到上限时"', 'eMax: "我方角色能量达到上限时", spUse: "我方消耗战技点时"')
F.rep('"aGive", "eMax", "stEnd"];', '"aGive", "eMax", "stEnd", "spUse"];', 2)
F.rep('      if (target === "ultpickm") {', '''      if (target === "skpickm") { const k = src ? byId[skPickTarget(src, Math.max(1, num(src.skN)), U)] : null; return k ? [k, ...U.filter(u => u.sm && !u.sm.cd && u.sm.owner === k.id && !u.gone)] : []; }   // 战技目标和它的召唤物（星期日）
      if (target === "ultpickm") {''')
F.rep('        if ((eff.type === "advance" || eff.type === "delay") && tg.gone) continue;',
      '        if (eff.xPath && (tplOf(ownerOf(tg) || tg) || {}).path === eff.xPath) continue;   // 目标是这个命途就不生效（星期日战技对「同谐」角色无法立即行动）\n        if ((eff.type === "advance" || eff.type === "delay") && tg.gone) continue;')
F.rep('hasSt(eff.stOn === "evt" ? evTarget : eff.stOn === "pick" && src ? byId[pickFor(src)] : src, k);',
      'hasSt(eff.stOn === "evt" ? evTarget : eff.stOn === "pick" && src ? byId[pickFor(src)] : eff.stOn === "sk" && src ? resolve("skpick", src)[0] : src, k);')
F.rep('addEnergy(tg, eCfg(tg).maxE * v / 100, false); continue; }   // 残梦', 'addEnergy(tg, Math.max(num(eff.eMin), eCfg(tg).maxE * v / 100), false); continue; }   // eMin：至少回这么多（星期日主日渴慕）；残梦')
F.rep('      if (num(eff.tgE) > 0) tgs = tgs.filter(u => !u.sm && !noStdE(u) && eCfg(u).maxE >= num(eff.tgE));',
      '      if (num(eff.tgE) > 0) tgs = tgs.filter(u => !u.sm && !noStdE(u) && eCfg(u).maxE >= num(eff.tgE));\n      if (eff.tHasSm) tgs = tgs.filter(u => U.some(z => z.sm && !z.sm.cd && z.sm.owner === (ownerOf(u) || u).id));   // 目标拥有召唤物才给（星期日战技）')
F.rep('      const dur = Math.max(0, Math.round(num(eff.duration))), lim = Array.isArray(eff.stE) && src && num(src.eid) >= num(eff.stE[0])',
      '      const dur = Math.max(0, Math.round(num(Array.isArray(eff.durE) && src && num(src.eid) >= num(eff.durE[0]) ? eff.durE[1] : eff.duration))), lim = Array.isArray(eff.stE) && src && num(src.eid) >= num(eff.stE[0])')
F.rep('n = lim > 0 ? Math.min(lim, (old ? old.n || 1 : 0) + Math.max(1, Math.round(num(eff.stAdd, 1)))) : 1;',
      'n = lim > 0 ? Math.min(lim, (old ? old.n || 1 : 0) + (Math.round(num(eff.stAdd, 1)) || 1)) : 1;')
F.rep('        if (v === 0 && bk) continue;\n        const b = { key, kind: "d",', '        if ((v === 0 && bk) || n <= 0) continue;   // stAdd 负数：减层，减到 0 移除\n        const b = { key, kind: "d",')
F.rep('      if (eff.perHit && !phIn) {', '''      if (num(eff.minEid) > 0 && src && num((ownerOf(src) || src).eid) < num(eff.minEid)) return;   // 几魂起才生效（写在基础效果里的星魂效果）
      if (num(eff.hitEq) > 0 && hitN(evTarget && evTarget.kind === "ally" ? evTarget : src) !== Math.round(num(eff.hitEq))) return;   // 这次攻击正好击中 N 个敌人（翡翠 E1）
      if (Array.isArray(eff.needBk) && src) { const b = src.buffs.find(z => z.key === src.id + ":" + eff.needBk[0] + ":d" + eff.needBk[1]); if (!b || (b.n || 1) < num(eff.needBk[2])) return; }   // 自己这组增益至少 N 层（翡翠 E2）
      if (eff.perHit && !phIn) {''')
F.rep('      if (x.sa) e.stAdd = x.sa;', '''      if (x.sa) e.stAdd = x.sa;
      if (x.xp) e.xPath = x.xp;      // 目标是这个命途就跳过
      if (x.emn) e.eMin = x.emn;     // 按能量上限 % 回能时至少回多少
      if (x.ths) e.tHasSm = true;    // 伤害增益：目标拥有召唤物才给
      if (x.de) e.durE = x.de;       // 伤害增益：[几魂起, 持续回合]
      if (x.hn) e.hitEq = x.hn;      // 这次攻击正好击中 N 个敌人
      if (x.nbk) e.needBk = x.nbk;   // [bk, 属性, N]：自己这组增益至少 N 层
      if (x.me) e.minEid = x.me;     // 几魂起才生效''')

# ================= 米沙 1312 =================
c = C[1312]; E = lambda f, r=None: F.eff(1312, f, r)
has('131204', '我方全体每消耗1个战技点，增加#2[i]段米沙下一次终结技的攻击段数，同时米沙恢复#1[f1]点能量')
tf = E('天赋：我方每消耗 1 个战技点'); o_tf = tf['n']
tf.update(t='spUse', n='天赋：我方全体每消耗 1 个战技点，米沙恢复 2 点能量（5 魂 2.2；不耗战技点的战技不算，耗 2 点的算 2 次）')
F.rebuild(1312, [tf if e is tf else e for e in c['eff']], rename={o_tf: tf['n']},
          notes=['终结技攻击段数（初始 3 段，战技和我方每消耗 1 个战技点各 +1 段，最多 10 段；秘技 +2、E1 每个敌人 +1）只影响伤害，伤害按初始 3 段显示'])
has('r:131206', '下一次施放战技后为我方恢复1个战技点')
e6 = F.eid(1312, 6); old6 = E('E6：开大后下一次施放战技恢复 1 个战技点', 6)
e6['eff'] = [x for x in e6['eff'] if x is not old6] + [
    dict(y='state', t='ult', tg='self', sn='E6 战技点', v=1, d=0, n='E6 久已生疏的憧憬：施放终结技时，记下“下一次施放战技后恢复 1 个战技点”'),
    dict(y='sp', t='skill', tg='self', v=1, ns='E6 战技点', n='E6：施放终结技后的下一次战技恢复 1 个战技点'),
    dict(y='state', t='skill', tg='self', sn='E6 战技点', v=0, n='E6：战技点恢复后清掉记号')]

# ================= 星期日 1313 =================
c = C[1313]; E = lambda f, r=None: F.eff(1313, f, r)
p2, p3, p4 = prm('131302', 10), prm('131303', 10), prm('131304', 10)
assert p2 == [1, 0.3, 2, 0.5] and p3 == [0.2, 0.3, 3, 0.12] and p4 == [0.2, 3]
has('131302', '当星期日对「同谐」命途的角色施放该技能时，无法触发立即行动效果'); has('131302', '对【蒙福者】施放战技后恢复1个战技点')
has('131303', '为指定我方单体角色恢复等同于#1[i]%能量上限的能量'); has('131303', '星期日自身每回合开始时【蒙福者】状态持续回合减1')
assert '若为目标恢复的能量不足40点，恢复的能量提高至40点' in TRS(1313)['主日渴慕'].replace('#1[i]', '40')
MF = '蒙福者'
st0, cd = E('行迹崇高拂尘'), E('终结技：【蒙福者】暴击伤害')
o_cd = cd['n']; st0['n'] = '行迹崇高拂尘：战斗开始时恢复 25 点能量'
cd.update(mv=1, n='终结技：【蒙福者】暴击伤害 +星期日暴击伤害的 30% + 12%，持续 3 回合（星期日每回合开始时 −1；按卡片面板暴伤；3 魂固定部分 12.8% 没升）')
new = [
    st0,
    dict(y='advance', t='skill', tg='skpickm', v=100, xp='同谐', n='战技：使指定我方单体及其召唤物立即行动（对「同谐」命途的角色无效；目标在卡片“每次战技目标”里选）'),
    dict(y='sp', t='skill', tg='self', v=1, ns=MF, so='sk', n='战技：对【蒙福者】施放战技后恢复 1 个战技点（自动判断战技目标是不是蒙福者）'),
    dict(y='dbuf', t='skill', tg='skpick', m='dmg', v=30, lv=[5, 33], d=2, cnt='own', bk='sk', n='战技：目标造成的伤害 +30%（5 魂 33%），持续 2 回合（按目标自己的回合）'),
    dict(y='dbuf', t='skill', tg='skpick', m='dmg', v=50, lv=[5, 55], d=2, cnt='own', bk='sk2', ths=1, n='战技：目标拥有召唤物时增伤额外 +50%（5 魂 55%；自动判断）'),
    dict(y='dbuf', t='skill', tg='skpick', m='cr', v=20, lv=[5, 22], d=3, cnt='own', bk='tf', ste=[6, 3], de=[6, 4], n='天赋：施放战技时目标暴击率 +20%（5 魂 22%），持续 3 回合（6 魂可叠 3 层、持续 4 回合）'),
    dict(y='state', t='ult', tg='others', sn=MF, v=0, n='终结技：【蒙福者】仅对终结技最新的施放目标生效（先取消原来的）'),
    dict(y='state', t='ult', tg='ultpick', sn=MF, v=1, d=3, ts='src', n='终结技：使目标成为【蒙福者】，持续 3 回合（星期日每回合开始时 −1；目标在“每次大招目标”里选）'),
    dict(y='energy', t='ult', tg='ultpick', m='maxp', v=20, emn=40, n='终结技：为目标恢复 20% 能量上限的能量（行迹主日渴慕：不足 40 点时提高至 40 点）'),
    cd,
    dict(y='dbuf', t='skill', tg='skpick', m='dmg', v=50, d=2, cnt='own', bk='tech', first=1, off=1, n='秘技荣光之秘：下一次战斗首次对我方目标施放技能时目标伤害 +50%，持续 2 回合（用了秘技再启用）'),
]
on = {n for n, t in F.OLD[1313]}
ren = {'行迹崇高拂尘': st0['n'], '战技：目标（及其召唤物）立即行动；对同谐角色无效': new[1]['n'], '战技：对蒙福者施放战技后恢复 1 个战技点': new[2]['n'], o_cd: cd['n']}
for k, i in (('战技：目标造成的伤害 +30%', 3), ('战技：目标有召唤物时增伤额外 +50%', 4), ('天赋：施放战技时目标暴击率 +20%', 5), ('秘技：首次对我方目标施放技能时', 10)):
    k0 = [n for n in on if n.startswith(k)]; assert len(k0) == 1, k; ren[k0[0]] = new[i]['n']
F.rebuild(1313, new, rename=ren, off0=['战技：对蒙福者施放战技后恢复 1 个战技点', [n for n in on if n.startswith('战技：目标有召唤物时增伤额外 +50%')][0]],
          notes=['行迹掌中安港（解除负面效果）页面不算；E6“暴击率超过 100% 的部分每 1% 换 2% 暴击伤害”没做'])
e1 = E('E1', 1); e1.update(tg='skpick', cnt='own', n='E1 千纪沉寂之末：施放战技时目标造成伤害无视敌方 16% 防御力，持续 2 回合（召唤物是 40%，没单独算）')
e2 = E('E2：【蒙福者】造成的伤害', 2); e2.update(mv=1, n='E2 笃信补完微缺：【蒙福者】造成的伤害 +30%')
has('r:131306', '星期日施放终结技时，也可以为目标添加天赋的暴击率提高效果')
F.eid(1313, 6)['eff'] = [dict(new[5], t='ult', tg='ultpick', n='E6 群星喧哗之始：施放终结技时也为目标添加天赋的暴击率提高效果（可叠 3 层、持续 4 回合）')]

# ================= 翡翠 1314 =================
c = C[1314]; E = lambda f, r=None: F.eff(1314, f, r)
p2, p4 = prm('131402', 10), prm('131404', 10)
assert p2 == [30, 0.02, 0.25, 3] and p4 == [0.024, 50, 8, 5, 1.2] and r4(prm('131404', 12)[0]) == 0.0264
has('131402', '当场上存在【收债人】时，翡翠无法施放战技，翡翠每回合开始时【收债人】状态持续回合数减1')
has('131404', '每击中1名敌方目标均可获得')
has('131403', '强化效果可生效#2[i]次'); assert prm('131403', 10)[:2] == [0.8, 2]
assert '处于【收债人】状态的角色回合开始时，额外获得' in TRS(1314)['逆回购']
SZ = '收债人'
adv, hp = E('行迹折牙票'), E('战技：【收债人】施放攻击后消耗自身')
o_hp = hp['n']; adv['n'] = '行迹折牙票：战斗开始时翡翠的行动提前 50%'
hp['n'] = '战技：【收债人】施放攻击后消耗自身 2% 生命上限的生命值（不足时降到 1 点；翡翠自己是收债人时不消耗）'
DP = lambda **k: dict(dict(y='dbuf', tg='self', m='cd', v=2.4, lv=[3, 2.64], st=50, d=0, bk='dp'), **k)
DA = lambda **k: dict(dict(y='dbuf', tg='self', m='atkP', v=0.5, st=50, d=0, bk='dpa'), **k)
new = [
    dict(y='spd', t='skill', tg='others', v=0, m='flat', d=0, bk='szr', n='战技：换【收债人】时，原来的【收债人】失去速度加成'),
    dict(y='state', t='skill', tg='others', sn=SZ, v=0, n='战技：【收债人】只有一个（先取消原来的）'),
    dict(y='spd', t='skill', tg='skpick', v=30, m='flat', d=3, bk='szr', n='战技：【收债人】速度 +30 点，持续 3 回合（翡翠每回合开始时 −1；目标在卡片“每次战技目标”里选）'),
    dict(y='state', t='skill', tg='skpick', sn=SZ, v=1, d=3, ts='src', n='战技：指定我方单体成为【收债人】，持续 3 回合（翡翠每回合开始时 −1）'),
    dict(y='force', t='skill', tg='self', v=2, m='basic', n='战技：场上存在【收债人】时翡翠无法施放战技（施放战技后的 2 次行动用普攻）'),
    dict(y='dbuf', t='skill', tg='skpick', m='rx', v=1, sc='jade', d=3, bk='rx', mv=1, n='额外伤害标记：【收债人】攻击后对每个击中的敌方目标造成翡翠 25% 攻击力的附加伤害（3 回合）'),
    hp, adv,
    dict(y='count', t='atk', aw='self', nf=1, ph=1, tg='self', v=1, n='天赋：翡翠施放攻击后每击中 1 名敌方目标获得 1 点充能（按敌人卡数量；天赋的追加攻击不获得）'),
    dict(y='count', t='atk', aw='others', **{'as': SZ}, ph=1, tg='self', v=1, n='天赋：【收债人】施放攻击后每击中 1 名敌方目标，翡翠获得 1 点充能（按敌人卡数量）'),
    DP(t='cnt', sa=5, n='天赋：发动天赋的追加攻击时立即获得 5 层【当品】，每层暴击伤害 +2.4%（3 魂 2.64%），最多 50 层'),
    DA(t='cnt', sa=5, n='行迹绝当品：每层【当品】额外使攻击力 +0.5%（追加攻击的 5 层）'),
    dict(y='fua', t='cnt', tg='self', v=0, n='天赋：充能达到 8 点后消耗 8 点，发动 1 次追加攻击（本次追加攻击不获得充能）'),
    dict(y='dbuf', t='ult', tg='self', m='rx', v=1, sc='jadeu', st=2, sa=2, d=0, bk='ju', n='终结技：天赋的追加攻击获得强化，伤害倍率 +80%，可生效 2 次'),
    dict(y='dbuf', t='fua', tg='self', m='rx', v=1, sc='jadeu', st=2, sa=-1, d=0, bk='ju', n='终结技：每次追加攻击用掉 1 次强化'),
    DP(t='start', n='行迹逆回购：敌方目标进入战斗时获得 1 层【当品】（按 1 个敌人进战）'),
    DA(t='start', n='行迹绝当品：开局那 1 层【当品】的攻击力'),
    DP(t='aTurn', aw='others', **{'as': SZ}, sa=3, n='行迹逆回购：处于【收债人】状态的角色回合开始时，额外获得 3 层【当品】'),
    DA(t='aTurn', aw='others', **{'as': SZ}, sa=3, n='行迹绝当品：【收债人】回合开始那 3 层【当品】的攻击力'),
    DP(t='start', sa=15, off=1, n='秘技猎手的视界：进入战斗后立即获得 15 层【当品】（用了秘技再启用）'),
    DA(t='start', sa=15, off=1, n='秘技猎手的视界：15 层【当品】的攻击力（和上一条一起开）'),
]
on = [n for n, t in F.OLD[1314]]
ren = {'战技': new[2]['n'], o_hp: hp['n'], '行迹折牙票': adv['n'],
       '战技：指定队友成为【收债人】（翡翠每回合开始时 −1，持续 3 回合；对谁在效果目标里选）': new[3]['n'],
       '天赋：翡翠攻击后每击中 1 个目标 +1 充能（按 1 个；收债人的攻击请自己加）': new[8]['n'],
       '天赋：【收债人】施放攻击后翡翠 +1 充能（按击中 1 个敌人算）': new[9]['n'],
       '天赋：充能满 8 点时追加攻击（本次追加攻击不获得充能）': new[12]['n'],
       '天赋：追加攻击时获得 5 层【当品】，每层暴击伤害 +2.4%，最多 50 层（这里每次追加攻击算 1 叠 = 5 层）': new[10]['n'],
       '行迹绝当品：每层【当品】攻击力 +0.5%（同上）': new[11]['n'],
       '额外伤害标记：【收债人】（3 回合，收债人 = 模板里的第一个队友）': new[5]['n']}
F.rebuild(1314, new, rename=ren, notes=['战技：若翡翠成为【收债人】时，无法获得速度提高效果且攻击后不消耗生命值'])
F.xr(1314, [dict(k='ult', n='终结技：强化天赋的追加攻击，伤害倍率 +80%（3 魂 88%，可生效 2 次）', who='flag', flag='jadeu', self=1, on=['f'], st='atk', v=[0.8, 0.88], lk='u', cnt='hit')])
has('r:131401', '击中敌方目标数量等于2/1名时，翡翠额外获得1/2点充能'); has('r:131402', '【当品】叠加至15层时，翡翠暴击率提高')
has('r:131406', '同时翡翠获得【收债人】状态')
F.eid(1314, 1)['eff'] += [
    dict(y='count', t='atk', aw='others', **{'as': SZ}, hn=2, tg='self', v=1, n='E1 无私？亦可交割：【收债人】施放攻击后击中的敌方目标正好 2 名时，额外获得 1 点充能'),
    dict(y='count', t='atk', aw='others', **{'as': SZ}, hn=1, tg='self', v=2, n='E1：【收债人】施放攻击后击中的敌方目标正好 1 名时，额外获得 2 点充能')]
e2 = E('E2', 2); e2.update(t='cnt', nbk=['dp', 'cd', 15], n='E2 道德？谨此核押：【当品】叠加至 15 层时暴击率 +18%（发动追加攻击时检查）')
F.eid(1314, 2)['eff'].append(dict(e2, t='turn', n='E2：【当品】叠加至 15 层时暴击率 +18%（翡翠回合开始时检查）'))
F.eid(1314, 6)['eff'] += [DP(t='turn', ns=SZ, so='team', sa=3, n='E6 公平？仍须保荐：场上有【收债人】时翡翠也获得【收债人】状态，自己回合开始时额外获得 3 层【当品】'),
                          DA(t='turn', ns=SZ, so='team', sa=3, n='E6：自己回合开始那 3 层【当品】的攻击力')]

# ================= 波提欧 1315 =================
c = C[1315]; E = lambda f, r=None: F.eff(1315, f, r)
has('131502', '持续#3[i]回合，波提欧每回合开始时持续回合数减1'); has('131502', '该目标被消灭或弱点被击破后，波提欧均可获得1层【优势口袋】，随后解除【绝命对峙】')
has('131504', '最多叠加#5[i]层'); assert prm('131504', 10)[4] == 3 and prm('131502', 10)[2] == 2
assert '处于【绝命对峙】并获得【优势口袋】时，恢复' in TRS(1315)['抵近射击']
JM, KD = '绝命对峙', '优势口袋'
dl, ex, fo, vu = E('终结技'), E('战技：施放后本回合不结束'), E('战技：进入绝命对峙 2 回合'), E('战技：【绝命对峙】的敌人受到波提欧攻击时伤害 +30%')
o = {k: e['n'] for k, e in dict(dl=dl, ex=ex, fo=fo).items()}
dl.update(tg='efirst', n='终结技：使指定敌方单体行动延后 40%（3 魂 42%）')
ex['n'] = '战技：施放该战技后本回合不会结束（同一回合内再行动一次）'
fo['n'] = '战技：【绝命对峙】期间普攻获得强化且无法施放战技（之后 2 次行动用强化普攻【击锤连弩】，不回战技点）'
new = [
    dl,
    dict(y='state', t='skill', tg='self', sn=JM, v=1, d=2, ts=1, n='战技：使指定敌方单体及自身进入【绝命对峙】，持续 2 回合（波提欧每回合开始时 −1）'),
    ex, fo, vu,
    dict(y='count', t='break', o='kill', ew='any', ns=JM, tg='self', v=1, n='战技：【绝命对峙】的目标被消灭或弱点被击破后获得 1 层【优势口袋】（最多 3 层；击破 / 消灭用手动事件触发）'),
    dict(y='energy', t='break', o='kill', ew='any', ns=JM, tg='self', v=10, m='er', n='行迹抵近射击：处于【绝命对峙】并获得【优势口袋】时恢复 10 点能量（溢出时也触发）'),
    dict(y='sp', t='break', o='kill', ew='any', ns=JM, tg='self', v=1, me=2, ptn=1, n='E2 里程碑贩子：处于【绝命对峙】并获得【优势口袋】时恢复 1 个战技点（2 魂起；单个回合内不重复触发）'),
    dict(y='force', t='break', o='kill', ew='any', ns=JM, tg='self', v=0, m='ebasic', n='战技：获得【优势口袋】后解除【绝命对峙】（普攻不再强化）'),
    dict(y='state', t='break', o='kill', ew='any', ns=JM, tg='self', sn=JM, v=0, n='战技：获得【优势口袋】后解除【绝命对峙】'),
] + [e for e in c['eff'] if '行迹幽灵装填' in e['n']]
F.rebuild(1315, new, rename={o['dl']: dl['n'], o['ex']: ex['n'], o['fo']: fo['n']}, cnt={'n': KD, 'at': 0, 'max': 3}, set={'cntName': KD, 'cntAt': 0, 'cntMax': 3},
          notes=['天赋的击破伤害、【优势口袋】的削韧、行迹蛇之上行（减伤）、E2 击破特攻、E6 页面不算击破，没做；秘技只添加弱点'])
has('r:131501', '战斗开始时，获得1层【优势口袋】')
F.eid(1315, 1)['eff'].append(dict(y='count', t='start', tg='self', v=1, n='E1 扬尘孤星：战斗开始时获得 1 层【优势口袋】'))

# ================= 乱破 1317 =================
c = C[1317]; E = lambda f, r=None: F.eff(1317, f, r)
A = {}
import json
for r in json.load(open(sys.argv[2] + '/AvatarSkillConfig.json', encoding='utf-8')):
    if str(r['SkillID']) in ('131708', '131710', '131712') and r.get('Level', 1) == 1: A[str(r['SkillID'])] = (r.get('SPBase') or {}).get('Value') if isinstance(r.get('SPBase'), dict) else r.get('SPBase')
assert A == {'131708': 5, '131710': 5, '131712': 10}, A   # 强化普攻三段：5 + 5 + 10 = 20 点能量
has('131703', '进入【结印】状态，立即获得1个额外回合并获得#3[i]点【彩墨】'); assert prm('131703', 10)[2] == 3
has('131703', '施放强化普攻后会消耗1点【彩墨】，耗尽时退出【结印】状态'); has('131707', '同时使自身获得#4[i]点能量')
JY = '结印'
ex, mt, fo = E('终结技：进入结印并立即获得额外回合'), E('行迹忍法帖•魔天'), E('终结技：结印期间普攻强化')
o = {k: e['n'] for k, e in dict(ex=ex, mt=mt, fo=fo).items()}
ex['n'] = '终结技：进入【结印】状态，立即获得 1 个额外回合'
fo['n'] = '终结技：获得 3 点【彩墨】，【结印】状态下普攻获得强化且无法施放战技和终结技（之后 3 次行动用强化普攻，每次消耗 1 点彩墨）'
mt['n'] = '行迹忍法帖•魔天：精英级别及以上的敌方目标的弱点被击破时恢复 10 点能量（并额外获得 1 点充能；击破用手动事件触发，需要时启用）'
new = [
    dict(y='state', t='ult', tg='self', sn=JY, v=1, d=0, n='终结技：进入【结印】状态（【彩墨】耗尽时退出）'),
    ex, fo,
    dict(y='state', t='ally', aw='self', aa=['ebasic'], nth=3, tg='self', sn=JY, v=0, n='终结技：施放第 3 次强化普攻后【彩墨】耗尽，退出【结印】状态'),
    mt,
    dict(y='energy', t='start', tg='self', v=10, m='er', off=1, n='秘技忍步•血义理：主动攻击敌人进入战斗后获得 10 点能量（用了秘技再启用）'),
]
F.rebuild(1317, new, rename={o['ex']: ex['n'], o['fo']: fo['n'], o['mt']: mt['n']}, x={'ebasicE': 20}, set={'ebasicE': 20},
          notes=['强化普攻【忍具•降魔花弁】三段分别恢复 5 / 5 / 10 点能量，共 20 点', '天赋的充能（敌方弱点被击破 +1，最多 10 点）、超击破、击破伤害页面不算击破，没做'])
has('r:131701', '退出【结印】状态后恢复20点能量'); has('r:131704', '【结印】状态期间，我方全体速度提高12%')
e1 = E('E1', 1); e1.update(d=0, bk='st:结印', n='E1 常世道返三途无六钱：【结印】状态期间造成的伤害无视目标 15% 的防御（退出结印时消失）')
F.eid(1317, 1)['eff'].append(dict(y='energy', t='ally', aw='self', aa=['ebasic'], nth=3, tg='self', v=20, m='er', n='E1：退出【结印】状态后恢复 20 点能量'))
F.eid(1317, 1)['notes'] = []
e4 = E('E4', 4); e4.update(d=0, bk='st:结印', n='E4 经年劣化任侠无忍义：【结印】状态期间我方全体速度 +12%（退出结印时消失）'); e4.pop('off', None)

F.finish('全面校对第 3 批（米沙、星期日、翡翠、波提欧、乱破）', '''<li><b>2026-11-10（全面校对第 3 批：米沙、星期日、翡翠、波提欧、乱破）</b>：逐条对照原文，tv 59（tools/fix59.py）。① <b>星期日</b>：<b>终结技为目标恢复 20% 能量上限的能量（不足 40 点按 40 点）原来漏了</b>，现在补上；战技目标和终结技目标分开选（战技看“每次战技目标”，终结技看“每次大招目标”）；立即行动带上目标的召唤物、对「同谐」角色无效；【蒙福者】做成状态（3 回合，星期日每回合开始 −1），“对蒙福者施放战技后恢复 1 个战技点”自动判断并默认开启；目标有召唤物时的 +50% 增伤自动判断；E6 暴击率叠 3 层、4 回合，终结技也给。② <b>翡翠</b>：【收债人】= “每次战技目标”；充能按<b>每击中 1 名敌方目标</b>算（按敌人卡数量）；有收债人时翡翠不能放战技（之后 2 次行动普攻）；【当品】按层数算（追加攻击 +5 层并且这次追击就吃到、开局 +1、收债人回合开始 +3，最多 50 层）；补终结技“追加攻击倍率 +80%，2 次”、E1 的额外充能、E2 按 15 层判断、E6、秘技 15 层（默认关）。③ <b>米沙</b>：天赋改成“我方每消耗 1 个战技点”触发（原来按“队友施放战技后”，不耗点的战技也算、耗 2 点的只算 1 次）；E6 的战技点恢复自动判断。④ <b>波提欧</b>：【绝命对峙】做成状态；补【优势口袋】（目标被击破 / 消灭时 +1 层、解除对峙）、行迹抵近射击 +10 能量、E1 开局 1 层、E2 回战技点（击破 / 消灭用手动事件）；终结技延后只对指定敌方单体。⑤ <b>乱破</b>：<b>强化普攻三段共恢复 20 点能量</b>（5 + 5 + 10，原来只算 5 点）；【结印】做成状态，第 3 次强化普攻后退出；E1 无视防御 / E4 全队加速跟着结印走（原来按 2 回合近似），补 E1 退出时 +20 能量和秘技 +10 能量（默认关）。新功能：触发“我方消耗战技点时”等（见 tools/fix59.py 开头）。<b>对已有配置</b>：用到这五个角色的方案会变（星期日的队友能量多了、乱破开大更快、翡翠追击更多）。</li>''',
'''2026-11-10（全面校对第 3 批）：米沙（1312）、星期日（1313）、翡翠（1314）、波提欧（1315）、乱破（1317）—— tv 59（tools/fix59.py）。AvatarSkillConfig：乱破强化普攻三段 131708 / 131710 / 131712 SPBase 5 / 5 / 10；波提欧战技 SPBase 没有（0）、强化普攻 30 不回战技点；翡翠天赋追击 10。
  改：见更新日志同日条目。新触发 spUse，新字段 xPath / eMin / tHasSm / durE / hitEq / needBk / minEid，目标 skpickm，stOn "sk"，stAdd 可为负。
  未改 / 存疑：米沙终结技段数没做（伤害按 3 段）；星期日 E6 溢出暴击率换暴伤没做、E1 召唤物 40% 没单独算；翡翠 E6 自己攻击的附加伤害没算；波提欧 / 乱破的击破伤害、充能（乱破天赋）没做。''')
