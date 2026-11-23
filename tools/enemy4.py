"""敌人第 4 批（2026-11-22 晚，每日敌人任务，没改 tv：新字段都是“没有就是旧行为”）。
用法：python3 -I tools/enemy4.py index.html <官方 ExcelOutput 目录（含 TextMapCHS.json）> [更新日志 li 文件]
官方数据：https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/*.json 和 TextMap/TextMapCHS.json
（目录里要有 MonsterConfig MonsterTemplateConfig MonsterSkillConfig EliteGroup HardLevelGroup StageConfig TextMapCHS）
（当时推不上仓库，2026-11-23 从 claude.ai 页面原样合回 index.html，这个脚本从项目文档补丁里补进仓库。）

A. 新敌人：可可利亚，虚妄之母（历战余响）（MonsterID 1005012，模板 1005012，历战余响关卡 1052020～1052026 用）：
   比主线版本（1005010，MON 里的「可可利亚，虚妄之母」）多一个天赋【灭世者的决意】，裂魂寒流倍率 6.5（主线 9.5），速度 / 弱点 / 韧性 / 攻击 / 生命相同。
   以前按名字比已经“有了”，其实是不同形态（同名不同形态要分开）。
B. 怪物效果（MON.sk 新字段，模拟里用）：
   - bp：敌人施放这招时我方战技点 ±N（锁元“使我方战技点减少1个”、大破大立“并使我方战技点减少1个”）。
     “减少我方战技点”没写个数的（坏猴来了记大过、狼的讥讽、极乐螺旋）不做（官方参数是 1，但原文没写，存疑）。
   - kbp：敌人被消灭时（“我方伤害扣敌人生命值”开着才会被消灭）我方战技点 +N（归元“受到致命攻击后使我方战技点恢复3个”）。
   - ctr / ctn：施放这招后进入【反击状态】，到它下一个回合开始时结束；状态中受到我方角色攻击后，立即对攻击者施放 MON.sk[ctr]
     （被打的角色回该招能量、触发“受到攻击时”、开了敌人伤害时按倍率扣血），每次我方攻击最多反击一次；ctn = 最多触发几次（原文“该效果最多触发1次”）。
     以牙还牙 3 个：杰帕德（末日幻影）（没有次数限制）、杰帕德（完整）（最多 1 次）、杰帕德（幻象）（没有次数限制）。
     页面的取舍（原文没写，写进总结请用户确认）：反击引起的我方攻击（比如克拉拉被反击后的反击）不再触发反击；攻击者是召唤物 / 忆灵时不反击（只写日志）；
     “持续1回合”按到它下一个回合开始时结束。
"""
import sys, json, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import Mon, page, grab, num

P, D = sys.argv[1], sys.argv[2]
M = Mon(D)
s, crlf = page(P)
assert 'if (s.tv >= 152) return;' in s and 'if (s.tv >= 153) return;' not in s, '页面 tv 不是 152'
assert 'ctrHit' not in s and 'k.kbp' not in s and 'num(sk.bp)' not in s, '已经跑过'
mM = grab(s, 'MON', r'\{'); MON = json.loads(mM.group(2))
idx = {m['n']: i for i, m in enumerate(MON['m'])}
nm0 = len(MON['m']); sk0 = len(MON['sk'])
SN = lambda o: [MON['sk'][i]['n'] for i in o]

# ---------- A. 可可利亚，虚妄之母（历战余响） ----------
NM = '可可利亚，虚妄之母（历战余响）'
assert NM not in idx
base = MON['m'][idx['可可利亚，虚妄之母']]
tmp = {'sk': list(MON['sk'])}; ref = M.build(tmp, 1005010)   # 验证：主线版本按同一算法重建和 MON 一致
assert {k: v for k, v in ref.items() if k not in ('k', 'p', 'q', 'x')} == {k: v for k, v in base.items() if k not in ('k', 'p', 'q', 'x')}
assert [tmp['sk'][i] for i in ref['k'] + ref['p']] == [MON['sk'][i] for i in base['k'] + base['p']]
assert {tmp['sk'][int(i)]['n']: v for i, v in ref['x'].items()} == {MON['sk'][int(i)]['n']: v for i, v in base['x'].items()}
o = M.build(MON, 1005012, NM)
assert M.name(1005012) == '可可利亚，虚妄之母' and M.MC[1005012]['MonsterTemplateID'] == 1005012
assert SN(o['q']) == SN(base['q']) and SN(o['p']) == ['灭世者的决意', '创世者的决意'], (SN(o['q']), SN(o['p']))
assert (o['s'], o['w'], o['tn'], o['a'], o['h']) == (base['s'], base['w'], base['tn'], base['a'], base['h'])
xo = {MON['sk'][int(i)]['n']: v for i, v in o['x'].items()}
assert xo['裂魂寒流'] == [6.5, 6.5, 1] and xo['碎骨寒流'] == [3.5, 3.5, 1], xo
assert MON['sk'][o['p'][0]]['d'] == '对指定我方单体施放【裂魂寒流】大概率使该目标陷入冻结状态。'
MON['m'].append(o); idx[NM] = len(MON['m']) - 1

# ---------- B1. 战技点 bp / kbp ----------
BP = {}
for i, k in enumerate(MON['sk']):
    if re.search(r'使我方战技点减少1个', k['d']): k['bp'] = -1; BP[i] = (k['n'], -1)
    if k['d'] == '受到致命攻击后使我方战技点恢复3个。': k['kbp'] = 3; BP[i] = (k['n'], 'kbp 3')
assert sorted(v[0] for v in BP.values()) == ['大破大立', '归元', '锁元'], BP
assert MON['sk'][[i for i in BP if BP[i][0] == '归元'][0]]['t'] == '天赋'

# ---------- B2. 反击状态 ctr / ctn ----------
CT = {}
for j, m in enumerate(MON['m']):
    for i in m.get('k', []) + m.get('p', []):
        k = MON['sk'][i]
        if k['n'] != '以牙还牙': continue
        assert k['d'].startswith('进入反击状态，持续1回合。在该状态下受到我方目标攻击后，立即对该目标施放【霜之惩击】。'), k['d']
        h = [x for x in m['k'] if MON['sk'][x]['n'] == '霜之惩击']; assert len(h) == 1, m['n']
        if 'ctr' in k: assert k['ctr'] == h[0]; continue
        k['ctr'] = h[0]
        if '该效果最多触发1次' in k['d']: k['ctn'] = 1
        CT[m['n']] = (i, h[0], k.get('ctn'))
assert set(CT) == {'杰帕德（完整）', '杰帕德（幻象）', '杰帕德（末日幻影）'}, CT
assert CT['杰帕德（完整）'][2] == 1 and CT['杰帕德（末日幻影）'][2] is None and CT['杰帕德（幻象）'][2] is None

s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]

def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:120], s.count(x)); s = s.replace(x, y)

# 我方攻击：记下这次打到的、处在反击状态的敌人，攻击结算完后反击
rep('    const atkAct = (who, fromFua, act) => { atkCtx = { u: who, k: fromFua ? "f" : ACT2K[act] || "m" }; ',
    '    const atkAct = (who, fromFua, act) => { atkCtx = { u: who, k: fromFua ? "f" : ACT2K[act] || "m" }; const ctE = !ctrD && U.some(z => z.kind === "enemy" && z.ctr && !z.gone) ? hitEns().filter(z => z.ctr) : null; ')
rep('teamFire("atk", who, fromFua ? e => !e.nf : null); if (SUP && who && who.kind === "ally") supCharge(hitEns().length); };',
    'teamFire("atk", who, fromFua ? e => !e.nf : null); if (SUP && who && who.kind === "ally") supCharge(hitEns().length); if (ctE && ctE.length) ctrHit(who, ctE); };\n'
    '    let ctrD = 0;   // 敌人【反击状态】（MON.sk.ctr，敌人第 4 批 tools/enemy4.py）：反击引起的我方攻击不再触发反击\n'
    '    const ctrHit = (who, ens) => {\n'
    '      if (!who || who.kind !== "ally") return;\n'
    '      for (const en of ens) {\n'
    '        const c = en.ctr, sk = c && MON.sk[c.k]; if (!sk || en.gone) continue;\n'
    '        if (who.sm || who.gone || who.domP || who.stP) { addLog(`${en.name} 反击状态：攻击者 ${who.name} 是召唤物 / 忆灵或不在场，页面没做反击`, false, "var(--enemy)"); continue; }\n'
    '        if (c.n != null && --c.n <= 0) en.ctr = null;   // 原文“该效果最多触发N次”\n'
    '        const xr = eHitOn ? ((monOf(en) || {}).x || {})[c.k] : null, eA = xr ? eAtkOf(en) : 0;\n'
    '        marks.push({ t, uid: en.id, label: "反击", color: "var(--enemy)", from: who.name });\n'
    '        addLog(`${en.name} 反击状态：受到 ${who.name} 攻击，立即对 ${who.name} 施放【${sk.n}】`, false, "var(--enemy)");\n'
    '        ctrD++; try { batchFx(() => apply({ id: en.id + "-ctr", type: "hit", target: who.id, value: num(sk.sp), dmg: xr && eA > 0 ? eA * num(xr[0]) * allyDefM(who, en) : 0 }, en, en.color)); } finally { ctrD--; }\n'
    '      }\n'
    '    };')
# 敌方回合开始：反击状态结束（“持续1回合”）
rep('        actor.dlC = {};   // 每回合推条次数清零',
    '        if (actor.ctr) { actor.ctr = null; marks.push({ t, uid: actor.id, label: "反击状态结束", color: "var(--enemy)", from: "" }); }   // 【反击状态】持续 1 回合：到它下一个回合开始（敌人第 4 批）\n'
    '        actor.dlC = {};   // 每回合推条次数清零')
# 敌人出招：战技点、进入反击状态
rep('          if (sk.ag && !FG) actor.again = true;   // MON.sk.ag：施放后再行动 1 次（罪血眈视；敌人第 3 批）\n',
    '          if (sk.ag && !FG) actor.again = true;   // MON.sk.ag：施放后再行动 1 次（罪血眈视；敌人第 3 批）\n'
    '          if (num(sk.bp)) { const s0 = sp; sp = Math.min(spMax, Math.max(0, sp + num(sk.bp))); addLog(`${actor.name}【${sk.n}】：我方战技点 ${num(sk.bp) > 0 ? "+" : "−"}${Math.abs(num(sk.bp))}（${s0} → ${sp}）`, false, "var(--enemy)"); }   // MON.sk.bp：锁元、大破大立（敌人第 4 批）\n'
    '          if (sk.ctr != null && MON.sk[sk.ctr]) { actor.ctr = { k: sk.ctr, n: sk.ctn != null ? num(sk.ctn) : null }; marks.push({ t, uid: actor.id, label: "反击状态", color: "var(--enemy)", from: "" }); }   // MON.sk.ctr：以牙还牙（敌人第 4 批）\n')
# 敌人被消灭：归元
rep('      if (killer && killer.kind === "ally") fireEv("kill", killer);\n',
    '      if (killer && killer.kind === "ally") fireEv("kill", killer);\n'
    '      { const m = monOf(en); for (const i of (m && m.p) || []) { const k = MON.sk[i]; if (k && num(k.kbp)) { const s0 = sp; sp = Math.min(spMax, Math.max(0, sp + num(k.kbp))); addLog(`${en.name}【${k.n}】：受到致命攻击，我方战技点 +${num(k.kbp)}（${s0} → ${sp}）`, false, "var(--enemy)"); } } }   // MON.sk.kbp：归元（敌人第 4 批）\n')

log = open(sys.argv[3], encoding='utf-8').read().strip() if len(sys.argv) > 3 else None
if log:
    ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
    s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('新敌人', NM, len(MON['m']) - 1, {k: v for k, v in o.items() if k not in ('k', 'p', 'q', 'x')})
print('bp', BP); print('ctr', CT)
print('MON', nm0, '→', len(MON['m']), 'sk', sk0, '→', len(MON['sk']))
