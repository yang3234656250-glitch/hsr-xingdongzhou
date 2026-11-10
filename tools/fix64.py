"""tv 64：每日校对（2026-11-10 晚）—— 布洛妮娅 1101、停云 1202、阮•梅 1303、花火【强化版】1306（四人上次校对是 10-27 / 10-28，最久）。
用法：python3 tools/fix64.py index.html <官方 json 目录>
新功能：
- “战技点”效果 ovc（DB ovc，字段 spOvc）：恢复战技点时溢出的部分记在施放者身上（u.spRec，最多 ovc 点）；
  方式 rec：把记下的溢出战技点补回去，直到战技点上限（花火【强化版】终结技）。
- 条件 tsp（字段 tspN）：这个回合里（任意单位的正常回合；额外回合算进前一个回合，对应刃 / Archer 的“回合不结束”）我方已消耗的战技点 ≥N（花火【强化版】人造花）。
"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 64, sys.argv[2])
C, has, hast = F.C, F.has, F.hast
X = lambda cid, n: [e for e in C[cid]['eff'] if e.get('n') == n][0]
cp = lambda e: dict(e)

# ================= 引擎 =================
F.rep('      if (x.xsp != null) e.maxSP = x.xsp;   // 战技点不超过这么多才生效',
      '      if (x.xsp != null) e.maxSP = x.xsp;   // 战技点不超过这么多才生效\n'
      '      if (x.ovc) e.spOvc = x.ovc;   // 战技点：恢复时溢出的部分记下来，最多这么多点（花火终结技）\n'
      '      if (x.tsp) e.tspN = x.tsp;    // 条件：这个回合里我方已消耗的战技点 ≥N（花火人造花）')
F.rep('    let turnSeq = 0;   // 任意单位每开始一个回合（含额外回合、阿哈时刻）+1',
      '    let turnSeq = 0;   // 任意单位每开始一个回合（含额外回合、阿哈时刻）+1\n    let ntSeq = 0;   // 任意单位每开始一个正常回合 +1（额外回合算进前一个回合：刃 / Archer 的“回合不结束”）')
F.rep('      actor.turns++; turnSeq++;\n', '      actor.turns++; turnSeq++; ntSeq++;\n')
F.rep('    let sp = Math.min(spMax, Math.max(0, num(S.spStart, 3))), spDepth = 0;',
      '    let sp = Math.min(spMax, Math.max(0, num(S.spStart, 3))), spDepth = 0, spSeq = -1, spTurn = 0;\n'
      '    const spSpent = n => { if (spSeq !== ntSeq) { spSeq = ntSeq; spTurn = 0; } spTurn += n; };   // 这个回合（正常回合 ntSeq，额外回合算进前一个）里我方消耗了几个战技点')
F.rep('        for (let i = 0; i < need; i++) { teamFire("spUse", u); teamFire("spChg", u); }   // 我方消耗战技点时（每点 1 次；米沙天赋）',
      '        for (let i = 0; i < need; i++) { spSpent(1); teamFire("spUse", u); teamFire("spChg", u); }   // 我方消耗战技点时（每点 1 次；米沙天赋）')
F.rep('''          const s0 = sp; sp = eff.mode === "to" ? Math.min(sp, Math.max(0, Math.round(v))) : Math.min(spMax, Math.max(0, sp + v));
          const d = Math.round(sp - s0), who = src ? (ownerOf(src) || src) : null;''',
      '''          const s0 = sp;
          if (eff.mode === "rec") {   // 把记下的溢出战技点补回去，直到上限（花火【强化版】终结技：我方角色回合结束后）
            const k = src ? Math.min(Math.round(num(src.spRec)), Math.max(0, spMax - sp)) : 0;
            if (!(k > 0)) continue;
            sp += k; src.spRec -= k; marks.push({ t, uid: src.id, label: `补 ${k} 战技点（还记着 ${src.spRec}）`, color: srcColor, from: src.name });
          } else {
            if (num(eff.spOvc) > 0 && src && eff.mode !== "to" && v > 0 && s0 + v > spMax) src.spRec = Math.min(Math.round(num(eff.spOvc)), Math.round(num(src.spRec) + s0 + v - spMax));   // 溢出的记下来
            sp = eff.mode === "to" ? Math.min(sp, Math.max(0, Math.round(v))) : Math.min(spMax, Math.max(0, sp + v));
          }
          const d = Math.round(sp - s0), who = src ? (ownerOf(src) || src) : null;''')
F.rep('for (let i = 0; i < Math.abs(d); i++) { if (d < 0) teamFire("spUse", who); teamFire("spChg", who); }',
      'for (let i = 0; i < Math.abs(d); i++) { if (d < 0) { spSpent(1); teamFire("spUse", who); } teamFire("spChg", who); }')
F.rep('      if (eff.maxSP != null && eff.maxSP !== "" && sp > num(eff.maxSP)) return;   // 战技点不超过 N 才生效（远坂凛自在远坂流）',
      '      if (eff.maxSP != null && eff.maxSP !== "" && sp > num(eff.maxSP)) return;   // 战技点不超过 N 才生效（远坂凛自在远坂流）\n'
      '      if (num(eff.tspN) > 0 && (spSeq === ntSeq ? spTurn : 0) < num(eff.tspN)) return;   // 这个回合里我方已消耗 ≥N 个战技点（花火人造花）')

F.rep('    if (e.maxEl) h.push(`队伍里欢愉角色不超过 ${e.maxEl} 名才生效`);',
      '    if (e.maxEl) h.push(`队伍里欢愉角色不超过 ${e.maxEl} 名才生效`);\n'
      '    if (num(e.tspN) > 0) h.push(`这个回合里我方已消耗 ≥${e.tspN} 个战技点才生效`);\n'
      '    if (num(e.spOvc) > 0) h.push(`恢复时溢出的战技点记下来（最多 ${e.spOvc} 点）`);\n'
      '    if (e.type === "sp" && e.mode === "rec") h.push("把记下的溢出战技点补回去，直到上限");')

# ================= 布洛妮娅 1101 =================
cid = 1101
has(110103, '使我方全体攻击力提高#，同时提高等同于布洛妮娅#暴击伤害+#的暴击伤害，持续#回合')
hast(cid, '号令', '普攻的暴击率提高至#'); hast(cid, '阵地', '战斗开始时，我方全体的防御力提高#，持续#回合'); hast(cid, '军势', '布洛妮娅在场时，我方全体造成的伤害提高#')
has('r:110102', '施放战技时，被指定的我方目标在行动后速度提高#，持续#回合')
has('r:110106', '战技对指定我方目标造成的伤害提高效果的持续时间增加#回合')
p3 = F.prm('110103')
assert abs(p3[9][2] - 0.20) < 1e-9 and abs(p3[11][2] - 0.216) < 1e-9, p3[9]
old = C[cid]['eff']
uc = X(cid, '终结技：我方全体暴击伤害 +布洛妮娅暴伤的 16% + 20%（按卡片面板暴伤；3 魂固定部分 21.6% 没升）')
nu = cp(uc); nu['lx'] = {'flat': [20, 21.6]}; nu['n'] = '终结技：我方全体暴击伤害 +布洛妮娅暴伤的 16% + 20%（按卡片面板暴伤；3 魂 16.8% + 21.6%）'
new = []
for e in old:
    new.append(nu if e is uc else e)
    if e.get('bk') == 'js':
        new.append({'y': 'dbuf', 't': 'start', 'tg': 'team', 'm': 'defP', 'v': 20, 'd': 2, 'bk': 'zd', 'n': '行迹阵地：战斗开始时我方全体防御力 +20%，持续 2 回合'})
        new.append({'y': 'dbuf', 't': 'start', 'tg': 'self', 'm': 'cr', 'v': 100, 'sc': 'b', 'd': 0, 'bk': 'hl', 'n': '行迹号令：普攻的暴击率提高至 100%'})
F.rebuild(cid, new, rename={uc['n']: nu['n']})
e2 = F.eid(cid, 2)
e2['eff'] = [
    {'y': 'state', 't': 'skill', 'tg': '$ally', 'sn': '快速行军', 'v': 1, 'd': 0, 'n': 'E2 快速行军：施放战技时，被指定的我方目标记下【快速行军】（行动后生效）'},
    {'y': 'spd', 'm': 'pct', 't': 'ally', 'aw': 'all', 'as': '快速行军', 'tg': 'evt', 'v': 30, 'd': 1, 'cnt': 'own', 'n': 'E2 快速行军：被指定的我方目标在行动后速度 +30%，持续 1 回合（按目标自己的回合）'},
    {'y': 'state', 't': 'ally', 'aw': 'all', 'as': '快速行军', 'tg': 'evt', 'sn': '快速行军', 'v': 0, 'n': 'E2 快速行军：生效后移除'},
]
e6 = F.eid(cid, 6)
e6['eff'] = [{'y': 'dbuf', 't': 'skill', 'tg': '$ally', 'm': 'dmg', 'v': 66, 'lv': [5, 72.6], 'd': 2, 'bk': 'sk', 'n': 'E6 气贯长虹：战技的增伤持续时间 +1 回合（2 回合）'}]

# ================= 停云 1202 =================
cid = 1202
has(120202, '【赐福】持续#回合且仅对停云战技最新的施放目标生效')
has('r:120201', '得到【赐福】的我方单体施放终结技后速度提高#，持续#回合')
has('r:120202', '得到【赐福】的我方单体在消灭敌方目标时恢复#点能量，该效果每回合只能触发#次')
new = list(C[cid]['eff'])
new.insert(4, {'y': 'state', 't': 'skill', 'tg': '$ally', 'sn': '赐福', 'v': 1, 'd': 3, 'ts': 'src', 'mv': 1, 'n': '战技：指定我方单体获得【赐福】，持续 3 回合（按停云的回合，只对最新的施放目标生效）'})
F.rebuild(cid, new)
e1 = F.eid(cid, 1)
e1['eff'] = [{'y': 'spd', 't': 'aUlt', 'as': '赐福', 'tg': 'evt', 'v': 20, 'd': 1, 'm': 'pct', 'cnt': 'own', 'n': 'E1 春风得意，时运驰骋：得到【赐福】的我方单体施放终结技后速度 +20%，持续 1 回合（按目标自己的回合）'}]
e2 = F.eid(cid, 2)
assert len(e2['eff']) == 1
e2['eff'][0].update({'ns': '赐福', 'so': 'evt', 'n': 'E2 君子惠渥，晏笑承之：得到【赐福】的我方单体消灭敌方目标时 +5 能量（每回合 1 次；消灭敌人要自己在手动事件里加）'})
e2['eff'][0].pop('off', None)

# ================= 阮•梅 1303 =================
cid = 1303
has(130302, '施放战技后阮•梅获得【弦外音】，持续#回合，阮•梅每回合开始时持续回合数减#。当阮•梅拥有【弦外音】时，我方全体伤害提高#')
has(130303, '阮•梅展开结界，持续#回合，自身每回合开始时结界持续回合数减#')
has('r:130306', '终结技展开的结界持续时间延长#回合')
has('r:130301', '终结技展开结界期间，我方全体造成伤害时无视目标#的防御力')
new = []
ren = {}
for e in C[cid]['eff']:
    e = cp(e)
    if e.get('bk') == 'xwy':
        new.append({'y': 'state', 't': 'skill', 'tg': 'self', 'sn': '弦外音', 'v': 1, 'd': 3, 'ts': 1, 'n': '战技：施放战技后阮•梅获得【弦外音】，持续 3 回合（阮•梅每回合开始时 −1）'})
        o = e['n']; e.update({'d': 0, 'bk': 'st:弦外音', 'n': '战技：阮•梅拥有【弦外音】时我方全体伤害 +32%'}); ren[o] = e['n']
    elif e.get('bk') == 'lz':
        e.update({'d': 0, 'bk': 'st:弦外音#lz'})
    elif e.get('bk') == 'jj':
        new.append({'y': 'state', 't': 'ult', 'tg': 'self', 'sn': '阮•梅结界', 'v': 1, 'd': 2, 'ts': 1, 'le': 6, 'lx': {'duration': [2, 3]}, 'n': '终结技：展开结界，持续 2 回合（阮•梅每回合开始时 −1；6 魂 3 回合）'})
        o = e['n']; e.update({'d': 0, 'bk': 'st:阮•梅结界', 'n': '终结技：结界期间我方全体全属性抗性穿透 +25%'}); ren[o] = e['n']
    new.append(e)
F.rebuild(cid, new, rename=ren)
e1 = F.eid(cid, 1)
assert len(e1['eff']) == 1
e1['eff'][0].update({'d': 0, 'bk': 'st:阮•梅结界#e1'})

# ================= 花火【强化版】1306 =================
cid = 1306
has(1130603, '为我方恢复#个战技点，若恢复时战技点溢出，则记录溢出的战技点数，最多记录#点。我方角色回合结束后若战技点小于上限，花火消耗记录值为我方恢复战技点，直至恢复至上限')
has(1130604, '当我方目标每消耗#点战技点，花火获得#层【幻相】')
hast(cid, '岁时记', '持有战技的暴击伤害提高效果的我方角色在消耗战技点时，花火额外恢复#点能量')
hast(cid, '人造花', '若我方角色单回合内消耗的战技点大于等于#，则花火下一次施放战技时不会消耗战技点')
has('r:130601', '终结技施加的【谜诡】的持续时间额外增加#回合')
has('r:130604', '终结技可以额外恢复#点战技点')
p2 = F.prm('1130602'); assert abs(p2[9][1] - 0.45) < 1e-9 and abs(p2[11][1] - 0.486) < 1e-9, p2[9]
old = C[cid]['eff']; ren = {}; new = []
for e in old:
    e = cp(e); o = e['n']
    if e.get('y') == 'sp' and e.get('t') == 'ult':
        e.update({'ovc': 10, 'n': '【强化版】终结技：恢复 6 个战技点，溢出的战技点记下来（最多 10 点）'}); ren[o] = e['n']; new.append(e)
        new.append({'y': 'sp', 't': 'ally', 'aw': 'all', 'tg': 'self', 'm': 'rec', 'v': 0, 'n': '【强化版】终结技：我方角色回合结束后若战技点小于上限，花火消耗记下的溢出战技点补到上限'})
        continue
    if e.get('t') == 'aSk' and e.get('y') == 'energy':
        e.update({'t': 'spUse', 'as': '梦游鱼', 'n': '【强化版】行迹岁时记：持有战技暴伤增益（【梦游鱼】）的我方角色每消耗 1 个战技点，花火 +1 能量'}); ren[o] = e['n']
    if e.get('bk') == 'hx':
        e.update({'t': 'spUse', 'n': '【强化版】天赋：我方每消耗 1 个战技点花火获得 1 层【幻相】，敌方全体受到的伤害 +4%，最多 3 层，持续 2 回合'}); ren[o] = e['n']
    if e.get('bk') == 'mys':
        new.append({'y': 'state', 't': 'skill', 'tg': '$ally', 'sn': '梦游鱼', 'v': 1, 'd': 2, 'ts': 'src', 'n': '【强化版】战技：目标持有战技的暴击伤害提高效果（记作【梦游鱼】，2 回合，和增益同时结束）'})
        e.update({'lx': {'flat': [45, 48.6]}, 'n': '【强化版】战技：目标暴击伤害 +花火暴击伤害的 24% + 45%，持续 2 回合（按卡片面板暴伤；3 魂 26.4% + 48.6%）'}); ren[o] = e['n']
    new.append(e)
    if e.get('y') == 'spmax':
        new.append({'y': 'state', 't': 'spUse', 'aw': 'all', 'tg': 'self', 'sn': '人造花', 'v': 1, 'd': 0, 'tsp': 3, 'n': '【强化版】行迹人造花：我方角色单回合内消耗的战技点 ≥3 时，花火下一次施放战技不消耗战技点'})
        new.append({'y': 'state', 't': 'ally', 'aw': 'self', 'aa': 'skill', 'tg': 'self', 'sn': '人造花', 'v': 0, 'n': '【强化版】行迹人造花：施放战技后移除'})
F.rebuild(cid, new, rename=ren)
C[cid].setdefault('x', {})['freeSkSt'] = ['人造花', 0]
e1 = F.eid(cid, 1)
e1['eff'].append({'y': 'dbuf', 't': 'ult', 'tg': 'enemies', 'm': 'vuln', 'v': 18, 'lv': [5, 19.44], 'd': 4, 'bk': 'mg', 'n': 'E1 悬置怀疑：【谜诡】持续时间 +1 回合（幻相额外增伤按 4 回合）'})
e2 = F.eid(cid, 2)
assert len(e2['eff']) == 1; e2['eff'][0].update({'t': 'spUse', 'n': 'E2：天赋每层（我方每消耗 1 个战技点）额外使我方无视目标 8% 防御力'})
e4 = F.eid(cid, 4)
spx = [e for e in e4['eff'] if e['y'] == 'sp']; assert len(spx) == 1
spx[0].update({'ovc': 10, 'n': 'E4：终结技额外恢复 1 个战技点（溢出的也记下）'})

LOG = '''<li><b>2026-11-10（每日校对：布洛妮娅、停云、阮•梅、花火）</b>：四人上次校对是 10-27 / 10-28，逐条对照官方原文，tv 64（tools/fix64.py）。① <b>花火【强化版】</b>：终结技“恢复时战技点溢出则记录溢出数（最多 10 点），我方角色回合结束后若战技点小于上限，花火消耗记录值恢复至上限”做进模拟（原来要自己加）；天赋【幻相】、E2 改成<b>我方每消耗 1 个战技点</b>叠 1 层（原来按“施放战技”算 1 次）；行迹岁时记 +1 能量改成“持有战技暴伤增益（【梦游鱼】）的角色每消耗 1 点”（原来是任何队友施放战技）；行迹人造花（单回合内消耗 ≥3 个战技点 → 下一次战技不耗点）做上；战技暴伤固定部分 3 魂 48.6%；E1 谜诡多 1 回合也算进幻相额外增伤。② <b>布洛妮娅</b>：E2 按原文改成目标<b>行动后</b>速度 +30%，持续目标自己的 1 回合（原来施放战技时就加、按布洛妮娅的回合到期）；补 E6 战技增伤 2 回合、行迹阵地（开局防御 +20% 2 回合）和号令（普攻暴击率 100%）；终结技暴伤固定部分 3 魂 21.6%。③ <b>停云</b>：【赐福】做成状态（3 回合，按停云的回合，只对最新目标）；E1 改成只认得到【赐福】的队友开大、默认开启、按目标自己的回合；E2 加【赐福】条件后默认开启（消灭敌人要自己加事件）。④ <b>阮•梅</b>：【弦外音】和终结技结界做成状态（阮•梅每回合开始时 −1），增伤 / 抗穿 / E1 跟着状态；补 E6 结界 +1 回合。新字段：战技点 ovc / 方式 rec、条件 tsp。<b>对已有配置</b>：有花火的方案战技点会多（溢出补回、人造花），布洛妮娅 2 魂起、停云 1 魂起的方案速度 / 行动顺序会变；其他角色不变。</li>'''
REC = '''2026-11-10（每日校对，晚）：布洛妮娅（1101）、停云（1202）、阮•梅（1303）、花火【强化版】（1306）—— 四人上次是 10-27 / 10-28。对照 StarRailRes 技能 / 行迹 / 星魂 / 秘技原文与 AvatarSkillConfig（普攻 20 / 战技 30 / 终结技 5、布洛妮娅 E4 追击 5、战技 BPNeed 1、能量上限 120 / 130 / 130 / 110 都对），tv 64（tools/fix64.py）。
  改：见更新日志同日条目。新字段：战技点 ovc（spOvc，溢出记在 u.spRec）/ 方式 rec、条件 tsp（tspN，本回合我方已消耗战技点）。
  核对无误：布洛妮娅战技立即行动 + 增伤 66%/72.6%、终结技攻击 55%/59.4%、天赋拉条 30%/33%、军势、秘技、E1（概率，默认关）、E4（风弱点，默认关）；停云终结技 +50 能量（E6 +10）、驻晴、亨通、止厄、秘技、赐福攻击力 / 附加伤害、天赋 XR；阮•梅天赋队友速度 10%/10.4%、日消遐思长、秘技 cast、战技增伤 32%/35.2%、抗穿 25%/27%；花火战技拉条 50%、终结技 6 点 + E4 1 点、战技点上限 +2（E4 +1）、岁时记 +10、秘技、夜想曲。
  未改 / 存疑：【赐福】、【梦游鱼】（花火战技暴伤）、布洛妮娅战技增伤的“持续 N 回合”按施放者的回合算（原文没写按谁）；花火人造花的“单回合”按任意单位的正常回合算（之后的额外回合算进同一个回合，对应 Archer / 刃的“回合不结束”；真正的额外回合也会算进去），终结技 / 追击里的消耗算进当时那个回合；花火溢出补回按“我方行动后”（含忆灵 / 召唤物行动后）；花火 E6 扩散给谜诡队友、谜诡按 3 层算没改；停云赐福攻击力按停云攻击力 25% 上限算（不比较目标 50%）；阮•梅残梅绽、击破相关（E4、E6 天赋倍率）不算；布洛妮娅 E4 追击伤害没有倍率。'''
F.finish('每日校对：布洛妮娅、停云、阮•梅、花火', LOG, REC)
