"""tv 63：全面校对第 7 批（光锥 172 个、遗器 64 套对照 light_cone_ranks / relic_sets 原文）。
用法：python3 tools/fix63.py index.html <官方 json 目录>
新功能：光锥字段 bs（基础速度 +N，5 档叠影；写进卡片的基础速度，u.bsX 记下已加的）；条件 minMaxE（DB mxe：装备者能量上限 ≥N）；
nthU（DB nu：“每第 N 次”的计数在自己施放终结技时清零）；战技点上限方式 el（每有 1 名欢愉角色 +v，cap 封顶）；
ovE 的各项可以写 5 档叠影数组、第 4 项 = 每几点算一档，充能效率增益也支持 ovE；ovE 效果数值写 0 不再当成“清掉这组增益”。
迁移：所有带光锥 / 遗器的卡片重建装备效果（开关按 来源 + 触发 + 类型 + 目标 + 说明 保留）。
"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 63, sys.argv[2])
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8')); RS = json.load(open(sys.argv[2] + '/relic_sets.json', encoding='utf-8'))
L = {c['id']: c for c in F.DB['lcs']}; R = {c['id']: c for c in F.DB['relics']}
def col(lid, k, pct=True): return [r4(p[k] * (100 if pct else 1)) for p in LR[str(lid)]['params']]
def hasl(lid, frag): F.has(LR[str(lid)]['desc'], frag)
def hasr(rid, j, frag): F.has(RS[str(rid)]['desc'][j], frag)
def LE(lid, frag):
    X = [e for e in L[lid]['eff'] if frag in (e.get('n') or '')]; assert len(X) == 1, (lid, frag, len(X)); return X[0]

# ================= 引擎 =================
F.rep('      if (x.ove) e.ovE = x.ove;      // 伤害增益：[门槛, 每点 %, 上限 %] 目标能量上限每超过门槛 1 点另加',
      '      if (x.ove) e.ovE = x.ove.map(z => pickR(z, rank || 1));      // 伤害增益 / 充能效率：[门槛, 每点 %, 上限 %, 每几点算一档] 目标能量上限每超过门槛 1 点另加（各项可写 5 档叠影）\n      if (x.mxe) e.minMaxE = x.mxe;   // 装备者能量上限 ≥N 才生效\n      if (x.nu) e.nthU = true;        // “每第 N 次”的计数在自己施放终结技时清零')
F.rep('      if (eff.maxSP != null && eff.maxSP !== "" && sp > num(eff.maxSP)) return;   // 战技点不超过 N 才生效（远坂凛自在远坂流）',
      '      if (eff.maxSP != null && eff.maxSP !== "" && sp > num(eff.maxSP)) return;   // 战技点不超过 N 才生效（远坂凛自在远坂流）\n      if (num(eff.minMaxE) > 0) { const H = src ? (ownerOf(src) || src) : null; if (!H || H.kind !== "ally" || noStdE(H) || eCfg(H).maxE < num(eff.minMaxE) - 1e-9) return; }   // 能量上限 ≥N（没有回报的加冕、向着不可追问处）')
F.rep('      u.ultN = (u.ultN || 0) + 1;\n      for (const q of Object.keys(teamCnt))', '      u.ultN = (u.ultN || 0) + 1;\n      for (const e of u.effects) if (e.nthU) delete firedMap[u.id + ":nth:" + e.id];   // 施放终结技时重置“每第 N 次”的计数（忍法帖的雷遁）\n      for (const q of Object.keys(teamCnt))')
F.rep('        if (eff.type === "spmax") { spMax = Math.max(1, spMax + v); continue; }',
      '        if (eff.type === "spmax") { const k = eff.mode === "el" ? Math.min(num(eff.dcap) > 0 ? num(eff.dcap) : 99, U.filter(z => z.kind === "ally" && !z.sm && z.elation).length) : 1; spMax = Math.max(1, spMax + v * k); continue; }   // 方式 el：队伍里每有 1 名欢愉角色 +v（花花世界迷人眼）')
OVX = 'Math.min(num(eff.ovE[2]), (num(eff.ovE[3]) > 0 ? Math.floor(Math.max(0, eCfg(tg).maxE - num(eff.ovE[0])) / num(eff.ovE[3]) + 1e-9) * num(eff.ovE[3]) : Math.max(0, eCfg(tg).maxE - num(eff.ovE[0]))) * num(eff.ovE[1]))'
F.rep('? Math.min(num(eff.ovE[2]), Math.max(0, eCfg(tg).maxE - num(eff.ovE[0])) * num(eff.ovE[1])) : 0;   // 目标能量上限超过门槛的部分另加（吉尔伽美什王霸的竞逐）',
      '? ' + OVX + ' : 0;   // 目标能量上限超过门槛的部分另加（吉尔伽美什王霸的竞逐；第 4 项 = 每几点算一档）')
F.rep('        if ((v === 0 && bk) || n <= 0) continue;   // stAdd 负数：减层，减到 0 移除', '        if ((v === 0 && bk && !Array.isArray(eff.ovE)) || n <= 0) continue;   // stAdd 负数：减层，减到 0 移除')
F.rep('          tg.buffs.push({ key, kind: "er", src: src ? src.id : null, v: v * n, n, expire: expireAt(src, dur) });',
      '          const ovx = Array.isArray(eff.ovE) && tg.kind === "ally" && !tg.sm && !noStdE(tg) ? ' + OVX + ' : 0;   // 按能量上限超出部分另加（邂逅于下一个花季）\n          if (Array.isArray(eff.ovE) && !(v + ovx > 0)) continue;\n          tg.buffs.push({ key, kind: "er", src: src ? src.id : null, v: (v + ovx) * n, n, expire: expireAt(src, dur) });')
F.rep('    for (const [k] of STATS) u[k + "B"] = Math.floor(T[k] + (lc && lc[k] != null ? lc[k] : 0) + 1e-9);\n  }',
      '''    for (const [k] of STATS) u[k + "B"] = Math.floor(T[k] + (lc && lc[k] != null ? lc[k] : 0) + 1e-9);
    // 光锥“基础速度提高 N”（黎明恰如此燃烧、将光阴织成黄金）：加进卡片的基础速度（百分比加速按它算），u.bsX = 已经加上的
    const bs = lc && lc.bs ? num([].concat(lc.bs)[Math.min([].concat(lc.bs).length - 1, Math.max(0, (u.lcR || 1) - 1))]) : 0;
    if (bs !== num(u.bsX)) { u.base = Math.round((num(u.base, T.spd) - num(u.bsX) + bs) * 100) / 100; if (bs) u.bsX = bs; else delete u.bsX; }
  }''')

# ================= 光锥 =================
SP = lambda **k: dict(dict(y='sp', tg='self', v=1), **k)
# 23064 向浪花掷下盛夏
hasl(23064, '每个波次开始时或装备者每施放#4[i]次欢愉技后，恢复1个战技点'); hasl(23064, '获得【风口】，【风口】使装备者的速度提高')
e = LE(23064, '浪行'); e.update(d=0, bk='fk', n='浪行：施放欢愉技时获得【风口】，速度提高（原文没写持续时间，按获得后一直有）'); e.pop('off', None)
L[23064]['eff'] += [SP(t='start', n='浪行：每个波次开始时恢复 1 个战技点（这里按第一波）'), SP(t='aha', nth=3, n='浪行：每施放 3 次欢愉技后恢复 1 个战技点')]
# 23063 你将起身歌唱
hasl(23063, '装备者施放终结技后，为我方恢复1点战技点')
L[23063]['eff'].append(SP(t='ult', n='即兴：施放终结技后为我方恢复 1 个战技点'))
# 23058 邂逅于下一个花季
hasl(23058, '每超出10点能量上限额外使能量恢复效率提高#6[f1]%，最多计入#7[i]点超出的能量上限')
p = LR['23058']['params'][0]; assert p[4] == 120 and p[5] == 0.003 and p[6] == 360
L[23058]['eff'].append(dict(y='erbuff', t='start', tg='self', v=0, d=0, ove=[120, 0.03, 10.8, 10], n='遐想：能量上限大于 120 时，每超出 10 点能量恢复效率 +0.3%，最多计入 360 点（+10.8%；面板上看不到这部分）'))
L[23058]['notes'] = [n for n in L[23058].get('notes', []) if '每超出10点' not in n]
# 23053 花花世界迷人眼
hasl(23053, '队伍中每有1名「欢愉」命途的角色，战技点上限提高#2[i]点，最多提高#3[i]点')
L[23053]['eff'].insert(0, dict(y='spmax', t='start', tg='self', m='el', v=1, cap=3, n='光锥：队伍中每有 1 名「欢愉」命途的角色，战技点上限 +1，最多 +3（同类光锥效果不叠加）'))
# 23050 勿忘她的火焰
hasl(23050, '装备者为敌方目标添加弱点时，恢复1个战技点，该效果最多触发1次，施放终结技时重置可触发次数')
L[23050]['eff'].append(SP(t='skill', perUlt=1, off=1, n='光锥：为敌方目标添加弱点时恢复 1 个战技点（最多 1 次，施放终结技时重置；装备者的战技会添加弱点时启用）'))
# 23048 金血铭刻的时代
hasl(23048, '施放终结技攻击后恢复#3[i]个战技点')
L[23048]['eff'].insert(0, SP(t='ult', n='光锥：施放终结技攻击后恢复 1 个战技点'))
# 23045 没有回报的加冕
hasl(23045, '若装备者的能量上限大于等于#3[i]点，为装备者固定恢复等同于装备者能量上限#5[i]%的能量，并再次使装备者的攻击力提高#2[i]%，持续#4[i]回合')
e = LE(23045, '施放终结技时攻击力提高'); e['n'] = '光锥：施放终结技时攻击力提高，持续 2 回合'
L[23045]['eff'] += [dict(y='energy', t='ult', tg='self', m='maxp', v=10, mxe=300, n='光锥：能量上限 ≥300 点时，施放终结技固定恢复能量上限 10% 的能量'),
                    dict(y='dbuf', t='ult', tg='self', m='atkP', v=col(23045, 1), d=2, bk='lc2', mxe=300, n='光锥：能量上限 ≥300 点时，施放终结技再次使攻击力提高，持续 2 回合')]
# 23037 向着不可追问处
hasl(23037, '若本次终结技消耗的能量大于等于#3[i]点，恢复1个战技点')
L[23037]['eff'].append(SP(t='ult', mxe=140, n='光锥：施放终结技后，若本次终结技消耗的能量 ≥140 点，恢复 1 个战技点（按能量上限判断）'))
# 23034 回到大地的飞行
hasl(23034, '装备者每对我方单体角色施放#5[i]次战技或终结技后，恢复1个战技点')
L[23034]['eff'].append(SP(t='skill', o='ult', nth=2, n='再启程：每对我方单体角色施放 2 次战技或终结技后，恢复 1 个战技点'))
# 23033 忍法帖•缭乱破魔
hasl(23033, '装备者施放终结技后获得【雷遁】，施放2次普攻后，装备者行动提前#3[i]%，并移除【雷遁】。装备者施放终结技后会重置【雷遁】')
L[23033]['eff'] += [dict(y='state', t='ult', tg='self', sn='雷遁', v=1, d=0, n='除邪：施放终结技后获得【雷遁】'),
                    dict(y='advance', t='basic', tg='self', v=col(23033, 2), ns='雷遁', nth=2, nu=1, n='除邪：持有【雷遁】时施放 2 次普攻后行动提前（施放终结技会重置次数）'),
                    dict(y='state', t='basic', tg='self', sn='雷遁', v=0, ns='雷遁', nth=2, nu=1, n='除邪：行动提前后移除【雷遁】')]
L[23033]['notes'] = [n for n in L[23033].get('notes', []) if '雷遁' not in n]
# 23027 驶向第二次生命
hasl(23027, '当装备者在战斗中击破特攻大于等于#2[i]%时，速度提高')
L[23027]['eff'].append(dict(y='spd', t='start', tg='self', m='pct', v=col(23027, 3), d=0, off=1, n='苦航：战斗中击破特攻 ≥150% 时速度提高（满足时启用；面板速度里已经算进去就别开）'))
L[23027]['notes'] = [n for n in L[23027].get('notes', []) if '速度提高' not in n]
# 23025 梦应归于何处
hasl(23025, '【溃败】状态下目标受到装备者造成的击破伤害提高#2[f1]%，速度降低#3[i]%')
L[23025]['eff'].append(dict(y='spd', t='break', tg='evt', m='pct', v=[-x for x in col(23025, 2)], d=2, cnt='own', bk='kb', n='光锥【溃败】：装备者造成击破伤害时目标速度降低 20%，持续 2 回合（用手动事件“弱点击破”触发）'))
# 23019 镜中故我
hasl(23019, '若装备者击破特攻大于等于#4[i]%，则恢复1个战技点')
L[23019]['eff'].append(SP(t='ult', off=1, n='彻骨梅香：施放终结技后，若击破特攻 ≥150%，恢复 1 个战技点（满足时启用）'))
# 23018 片刻，留在眼底 / 21034 今日亦是和平的一日：按实际能量上限
hasl(23018, '每点能量提高#2[f2]%，最多计入#3[i]点'); assert LR['23018']['params'][0][2] == 180
e = LE(23018, '终结技伤害按能量上限提高'); per = col(23018, 1)
e.update(v=0, ove=[0, per, [r4(x * 180) for x in per]], n='光锥：终结技伤害按装备者能量上限提高，每点 0.36%～0.6%，最多计入 180 点'); e.pop('off', None)
hasl(21034, '每点能量提高#1[f2]%，最多计入#2[i]点'); assert LR['21034']['params'][0][1] == 160
e = LE(21034, '按能量上限伤害提高'); per = col(21034, 0)
e.update(v=0, ove=[0, per, [r4(x * 160) for x in per]], n='光锥：按装备者能量上限伤害提高，每点 0.2%～0.4%，最多计入 160 点')
# 基础速度
for lid in (23044, 23036):
    hasl(lid, '使装备者的基础速度提高#1[i]'); L[lid]['bs'] = [int(p[0]) for p in LR[str(lid)]['params']]
    L[lid]['notes'] = [n for n in L[lid].get('notes', []) if '基础速度' not in n] + ['基础速度 +12～20 已加进卡片的“基础速度”（百分比加速按它算）；面板速度照游戏里填']

# ================= 遗器 =================
hasr(106, 1, '回合开始时，如果装备者当前生命值百分比小于等于50%，则回复等同于自身生命上限8%的生命值，并恢复5点能量')
for e in R[106]['p4']['eff']: e.pop('off', None); e['hle'] = 50
R[106]['p4']['eff'][0]['n'] = '4件：回合开始时当前生命值 ≤50% 则恢复 5 点能量'; R[106]['p4']['eff'][1]['n'] = '4件：回合开始时当前生命值 ≤50% 则回复 8% 生命上限'
hasr(111, 1, '当装备者击破敌方目标弱点后，恢复3点能量')
e = R[111]['p4']['eff'][0]; e.pop('off', None); e['n'] = '4件：装备者击破敌方目标弱点后恢复 3 点能量（用手动事件“弱点击破”触发）'
hasr(123, 1, '装备者的忆灵在场时，装备者的速度提高6%')
P = R[123]['p4']['eff']; assert P[0]['y'] == 'spd'
R[123]['p4']['eff'] = [dict(y='spd', t='start', o='smOn', tg='self', v=6, m='pct', d=0, bk='r123', si='in', n='4件：装备者的忆灵在场时速度 +6%'),
                       dict(y='spd', t='smEnd', tg='self', v=0, m='pct', d=0, bk='r123', si='out', n='4件：装备者的忆灵都不在场时这个加速结束')] + P[1:]
hasr(301, 0, '当装备者的速度大于等于120时，攻击力额外提高12%')
R[301]['p2']['eff'] = R[301]['p2'].get('eff', []) + [dict(y='dbuf', t='start', ms=120, tg='self', m='atkP', v=12, d=0, bk='r', n='2件：速度 ≥120 时攻击力额外提高 12%（战斗中才有，面板攻击力里没有）')]
hasr(328, 0, '若装备者能量上限大于等于200点，每超过1点使装备者造成的伤害提高0.2%，最多提高32%')
e = R[328]['p2']['eff'][0]; e.pop('off', None); e.update(v=0, ove=[200, 0.2, 32], mxe=200, n='2件：能量上限 ≥200 点时，每超过 1 点伤害提高 0.2%，最多 32%（按装备者的能量上限自动算）')

F.finish('全面校对第 7 批（光锥 / 遗器）', '''<li><b>2026-11-10（全面校对第 7 批：光锥 172 个、遗器 64 套）</b>：全部对照官方原文和 5 档叠影数值跑了一遍（数值都对得上），补上漏掉的效果，tv 63（tools/fix63.py）。<b>光锥</b>：① 漏掉的战技点：金血铭刻的时代（终结技攻击后 +1）、你将起身歌唱（终结技后 +1）、回到大地的飞行（每 2 次战技 / 终结技 +1）、向着不可追问处（终结技消耗 ≥140 能量 +1）、向浪花掷下盛夏（波次开始 +1、每 3 次欢愉技 +1）、花花世界迷人眼（每名欢愉角色战技点上限 +1，最多 +3）；勿忘她的火焰、镜中故我要条件，默认关闭。② 忍法帖•缭乱破魔【雷遁】：终结技后 2 次普攻行动提前 50%～70%（原来只写在备注里）。③ 没有回报的加冕：能量上限 ≥300 时终结技回 10% 能量、攻击力再提高一次。④ 邂逅于下一个花季：能量上限超过 120 的部分给的能量恢复效率。⑤ 片刻，留在眼底 / 今日亦是和平的一日：按装备者实际能量上限算（原来按 120 写死）。⑥ 黎明恰如此燃烧 / 将光阴织成黄金：基础速度 +12～20 加进卡片的基础速度（百分比加速会略高）。⑦ 向浪花掷下盛夏【风口】默认开；梦应归于何处【溃败】减速、驶向第二次生命的速度（默认关）。<b>遗器</b>：凯歌祝捷的英豪 4 件“忆灵在场时速度 +6%”按忆灵在不在场自动算（原来默认关）；戍卫风雪的铁卫 4 件按当前生命值 ≤50% 自动判断；流星追迹的怪盗 4 件默认开；太空封印站补“速度 ≥120 攻击力 +12%”；寰宇生研院按实际能量上限算。<b>对已有配置</b>：装备了上面这些光锥 / 遗器的卡片会自动换成新效果（原来关着的仍关着），战技点和个别行动提前会变；其他不变。</li>''',
'''2026-11-10（全面校对第 7 批）：光锥 172 个、遗器 64 套 —— 用审计脚本对照 light_cone_ranks / relic_sets：每个数值必须是官方某一档参数，5 档数组必须等于官方某一列；原文里有行动提前 / 速度 / 能量 / 战技点 / 额外回合 / 回复 / 消耗生命的句子必须有对应效果，逐条人工看剩下的差异。tv 63（tools/fix63.py）。
  改：见更新日志同日条目。新字段：光锥 bs、条件 mxe、nu、战技点上限方式 el、ovE 数组 / 档位、充能效率 ovE。
  核对无误：其余光锥 / 遗器的数值和触发（数值全部对上官方参数）。
  未改 / 存疑：星火悄然闪耀、天国@直播间、花花世界迷人眼【推流】（同一回合消耗 ≥3 / 4 个战技点）仍要手动开；游戏尘寰【彩焰】（每恢复 1 个战技点 1 层，4 层再得【假面】）没做；理想燃烧的地狱（战技点上限 ≥6）手动开；当一颗星照亮夜空的助战技回能没做；时节不居的附加伤害、镂月裁云之意的随机效果没做；按面板属性换算的常驻加成（此时恰好、泛银河商业公司、筑城者的贝洛伯格）算面板；击破 / 持续伤害类（机心戏梦的钟表匠、荡除蠹灾的铁骑、盗贼公国塔利亚、劫火莲灯铸炼宫、沉欢醉饮的海隅）页面不算。当第一声「阿哈」响起、在世界尽头相会吧！、神的瞬息欢愉、亚空异容所官方 dump 里没有，没法核对。''')
s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX63); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX63); for (const u of s.units) if (u.kind === "ally" && !u.sm && (u.lc || u.rA || u.rB || u.rP)) applyEquip(u); } finally { S = keep; } }   // 光锥 / 遗器改了：带装备的卡片都重建装备效果')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
