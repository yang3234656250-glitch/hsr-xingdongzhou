"""tv 141（2026-11-17）：差异清单第 23 批（卢卡裂伤上限、罗刹 E1 / E2 / E4、停云【赐福】上限）
1. 卢卡 1111 战技裂伤：原文“每回合开始时受到等同于自身 24% 生命上限的物理属性持续伤害，最多不超过卢卡攻击力的 338%”。
   以前一律按上限 338% 攻击力算。现在 dot 新字段 hpv（字段 hpV）= 敌人生命上限的 X%：模拟里持续伤害记录带 hpB（那个敌人的生命上限：
   开了敌人生命值时按当前阶段的上限 ehx，否则按敌人卡 / 官方资料 eHpMaxOf）和 hpV（× 本次倍数，引爆 85% 也按比例），
   伤害层 dotDmgOf 取两者较小的（不暴击、增伤 / 易伤等其他乘区一样）。没有敌人生命值资料时仍按 338% 攻击力。
2. 罗刹 1203
   - E1「结界生效时我方全体攻击力提高 20%」：原来挂在计数满（展开结界）上、持续 2 回合；改成跟着【结界】状态（bk st:结界，结界结束 / 罗刹倒下一起消失），
     并补上秘技“进战立即触发天赋”展开的结界（战斗开始时，有【结界】才生效）。
   - E4「结界生效时使敌方目标陷入虚弱」：补上秘技展开的结界。
   - E2「若指定我方目标当前生命值百分比小于 50%，则罗刹提供的治疗量提高 30%」：原来是另外回复一次 30%（再乘治疗加成，等于治疗量 ×1.3），
     改成治疗加成 +30%（和卡片治疗加成相加）。引擎：hbup 方式 cast 现在认 tgh（目标当前生命值条件，按治疗前判断），
     也认 hpLoss 触发（罗刹战技的自动触发版）。
3. 停云 1202 战技【赐福】：原文“攻击力提高 50%，最高不超过停云当前攻击力的 25%”（5 魂 55% / 27%）。以前一律按停云攻击力 25% 给；
   dbuf 新字段 tca（字段 tCapA）= 不超过目标基础攻击力的 X%（目标没有基础攻击力数据时不封顶），取两者较小的。
另：修正迁移入口——tv 139 / 140 没有加进“老存档（tv ≥2）”那条路径（那里仍写 s.tv = 138），老存档每次打开都重跑迁移、fixTpl139 一直没跑到；这里补上。

用法：python3 tools/fix141.py index.html <官方 json 目录>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 141
P = sys.argv[1]
raw = open(P, encoding='utf-8', newline='').read()
CRLF = '\r\n' in raw
F = Fix(P, 140 + 1, sys.argv[2])   # Fix 只检查 if (s.tv >= 140) return;


def mig(cid, old, new, trig):
    """基础效果原地改（加字段 + 换说明）：迁移时旧说明 → 新说明（用户关掉的仍关着；触发改过的保留并抄数值）"""
    fx = F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
    fx['drop'].append(old); fx['trig'][old] = trig; fx['map'][old] = new; fx['add'].append(new); fx['keep'] = 1


# ---------------- 引擎 ----------------
# DB 缩写
F.rep('if (x.dk) e.dk = x.dk; if (x.vps != null) e.vps = x.vps;',
      'if (x.dk) e.dk = x.dk; if (x.hpv) e.hpV = x.hpv; if (x.tca) e.tCapA = x.tca; if (x.vps != null) e.vps = x.vps;')
# dot 对象带 hpV
F.rep('vps: num(eff.vps), stm: !!eff.stm, stat: eff.srcS || "atk",', 'vps: num(eff.vps), hpV: num(eff.hpV), stm: !!eff.stm, stat: eff.srcS || "atk",')
# dotHit：记录敌人生命上限和这次的生命上限倍率
F.rep('      mk(dotMult(d) * k);\n',
      '      { const r0 = mk(dotMult(d) * k); if (num(d.hpV) > 0) { const mx = num(en.ehx) || eHpMaxOf(en); if (mx > 0) { r0.hpB = mx; r0.hpV = num(d.hpV) / 100 * k; } } }   // 按敌人生命上限 X%、最多不超过攻击力倍率（卢卡裂伤）\n')
# dotDmgOf：取较小的
old = '''    const d = dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, hpm: r.hpm, ebk: r.ebk }, brk ? LVBRK * (1 + (num(u.be) + dsum(r.db, "be", "k")) / 100) : undefined);
    if (brk && d) { d.noPanel = false; d.stat = "击破基础值（80 级）"; }
    return (r.__dmg = d);'''
new = '''    let d = dmgCalc(u, e, { t: r.t, uid: u.id, db: r.db, edb: r.edb, hpm: r.hpm, ebk: r.ebk }, brk ? LVBRK * (1 + (num(u.be) + dsum(r.db, "be", "k")) / 100) : undefined);
    if (brk && d) { d.noPanel = false; d.stat = "击破基础值（80 级）"; }
    if (!brk && d && num(r.hpB) > 0 && num(r.hpV) > 0) {   // 按敌人生命上限 X%，最多不超过攻击力倍率：取较小的（卢卡裂伤）
      const d2 = dmgCalc(u, Object.assign({}, e, { v: num(r.hpV) }), { t: r.t, uid: u.id, db: r.db, edb: r.edb, ebk: r.ebk }, num(r.hpB));
      if (d2 && d2.total < d.total) { d2.noPanel = false; d2.stat = "敌人生命上限（未达到攻击力上限）"; d = d2; }
    }
    return (r.__dmg = d);'''
F.rep(old, new)
# 伤害增益：不超过目标基础攻击力的 X%（停云【赐福】）
old = '        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: (amt0 + ovx) * n, n };'
new = ('        let amtT = amt0; if (num(eff.tCapA) > 0 && eff.mode === "atkF") { const ow = ownerOf(tg) || tg, bA = num(ow.atkB); if (bA > 0) amtT = Math.min(amt0, bA * num(eff.tCapA) / 100); }   // tCapA：不超过目标基础攻击力的 X%（停云【赐福】）\n'
       '        const b = { key, kind: "d", st: eff.mode, sc: eff.dsc || "", src: src ? src.id : null, v: (amtT + ovx) * n, n };')
F.rep(old, new)
# 治疗加成 cast：认目标生命值条件、认 hpLoss 触发
old = '''    const castHb = (H, src, eff) => {
      if (!H || src !== H || !eff) return 0;
      const ks = [eff.trigger, eff.or].filter(k => CASTK.includes(k)); if (!ks.length) return 0;
      let b = 0;
      for (const x of H.effects) if (x.type === "hbup" && x.mode === "cast" && !x.off && (ks.includes(x.trigger) || ks.includes(x.or)) && !(x.ms && spdOf(H) < num(x.ms))) b += num(x.value);
      return b;
    };
    const healBonus = (H, src, eff, tick) => num(H && H.hb) + hbOf(H, "hb") + (tick ? 0 : castHb(H, src, eff));'''
new = '''    const castHb = (H, src, eff, tg) => {
      if (!H || src !== H || !eff) return 0;
      const ks = [eff.trigger, eff.or].filter(k => CASTK.includes(k) || k === "hpLoss"); if (!ks.length) return 0;   // hpLoss：自动触发的“等同于战技的效果”（罗刹）
      let b = 0;
      for (const x of H.effects) if (x.type === "hbup" && x.mode === "cast" && !x.off && (ks.includes(x.trigger) || ks.includes(x.or)) && !(x.ms && spdOf(H) < num(x.ms)) && !(x.tgHp && tg && !cmpP(hpPct(tg), x.tgHp))) b += num(x.value);   // tgHp：按治疗前目标的当前生命值（罗刹 E2）
      return b;
    };
    const healBonus = (H, src, eff, tick, tg) => num(H && H.hb) + hbOf(H, "hb") + (tick ? 0 : castHb(H, src, eff, tg));'''
F.rep(old, new)
F.rep('return (base * p / 100 + f) * (1 + (healBonus(H, src, eff, tick) + lowHb(H, tg)', 'return (base * p / 100 + f) * (1 + (healBonus(H, src, eff, tick, tg) + lowHb(H, tg)')
F.rep('o = healBonus(H, src, eff, tick) - num(H && H.hb) + lowHb(H, tg)', 'o = healBonus(H, src, eff, tick, tg) - num(H && H.hb) + lowHb(H, tg)')

# 迁移：fixTpl 的 keep（新）= 被换掉的旧效果开着的，新效果也开着（以前只保留“关着”）
F.rep("""      for (const e of u.effects) if (!e.eq && fx.drop.includes(e.note) && !kept.has(e) && fx.map && fx.map[e.note] && e.off && !(fx.off0 || []).includes(e.note)) offWas[fx.map[e.note]] = 1;""",
      """      for (const e of u.effects) if (!e.eq && fx.drop.includes(e.note) && !kept.has(e) && fx.map && fx.map[e.note] && !(fx.off0 || []).includes(e.note)) { if (e.off) offWas[fx.map[e.note]] = 1; else if (fx.keep) offWas[fx.map[e.note]] = -1; }   // keep：原来开着的也照旧开着（tv 141 起）""")
F.rep("""        if (offWas[x.n]) z.off = true;
""", """        if (offWas[x.n] === 1) z.off = true; else if (offWas[x.n] === -1) delete z.off;
""")

# ---------------- 1. 卢卡 ----------------
F.has('111102', '敌方目标每回合开始时受到等同于自身24%生命上限的物理属性持续伤害，最多不超过卢卡攻击力的338%')
assert F.prm('111102', 10)[2] == 0.24 and F.prm('111102', 12)[2] == 0.24 and F.prm('111102', 10)[3] == 3.38
for frag, new_n in [('战技：使目标陷入裂伤', '战技：使目标陷入裂伤，每回合开始受到 24% 生命上限的物理属性持续伤害，最多不超过卢卡攻击力的 338%（3 魂 371.8%；两者取较小的，没有敌人生命值资料时按攻击力上限），持续 3 回合（基础概率按命中算）'),
                    ('秘技抢先者：进入战斗后使目标陷入与战技相同的裂伤', None)]:
    z = F.eff(1111, frag); assert z['y'] == 'dot' and z['dk'] == '裂伤'
    z['hpv'] = 24
    nn = new_n or z['n'] + '（伤害同战技：生命上限 24% 和攻击力 338% 取较小的）'
    mig(1111, z['n'], nn, z['t']); z['n'] = nn

# ---------------- 2. 罗刹 ----------------
F.has('r:120301', '结界生效时我方全体攻击力提高#')
F.has('r:120304', '结界生效时使敌方目标陷入虚弱状态，造成的伤害降低#')
F.has('r:120302', '触发战技效果时，若指定我方目标当前生命值百分比小于#，则罗刹提供的治疗量提高#')
F.has('120307', '使用秘技后，下一次战斗开始时立即触发天赋')
z = F.eff(1203, '秘技愚者的悲悯'); assert z['t'] == 'start' and z['sn'] == '结界' and z.get('off')
e1 = F.eid(1203, 1); assert len(e1['eff']) == 1 and e1['eff'][0]['bk'] == 'e1'
e1['eff'] = [
    {'y': 'dbuf', 't': 'cnt', 'tg': 'team', 'm': 'atkP', 'v': 20, 'd': 0, 'bk': 'st:结界', 'n': 'E1 濯洗生者：结界生效时我方全体攻击力 +20%（结界结束时消失）'},
    {'y': 'dbuf', 't': 'start', 'tg': 'team', 'm': 'atkP', 'v': 20, 'd': 0, 'bk': 'st:结界', 'ns': '结界', 'n': 'E1：秘技进战展开的结界同样 +20% 攻击力（秘技那条开了才生效）'},
]
e4 = F.eid(1203, 4); assert len(e4['eff']) == 1 and e4['eff'][0]['bk'] == 'st:结界#e4'
e4['eff'].append({'y': 'dbuf', 't': 'start', 'tg': 'enemies', 'm': 'wkn', 'v': 12, 'd': 0, 'bk': 'st:结界#e4', 'ns': '结界', 'n': 'E4：秘技进战展开的结界同样使敌人虚弱 12%（秘技那条开了才生效）'})
e2 = F.eid(1203, 2); assert [x['y'] for x in e2['eff']] == ['heal', 'heal', 'shield'], e2
sh = e2['eff'][2]
e2['eff'] = [
    {'y': 'hbup', 'm': 'cast', 'v': 30, 't': 'skill', 'tg': 'self', 'tgh': ['lt', 50], 'n': 'E2 净庭赐礼：施放战技时，若目标当前生命值 <50%，罗刹提供的治疗量 +30%（和治疗加成相加，按治疗前的生命值）'},
    {'y': 'hbup', 'm': 'cast', 'v': 30, 't': 'hpLoss', 'tg': 'self', 'tgh': ['lt', 50], 'n': 'E2：自动触发的战技效果同样治疗量 +30%（目标当前生命值 <50% 时）'},
    sh,
]

# ---------------- 3. 停云 ----------------
F.has('120202', '使其攻击力提高50%，最高不超过停云当前攻击力的25%')
p10, p12 = F.prm('120202', 10), F.prm('120202', 12)
assert (p10[1], p10[3], p12[1], p12[3]) == (0.5, 0.25, 0.55, 0.27), (p10, p12)
z = F.eff(1202, '战技：【赐福】攻击力 +50%'); assert z['m'] == 'atkF' and z['ss'] == 'atk' and z['v'] == 25 and z['lv'] == [5, 27]
new_n = '战技：【赐福】攻击力提高 50%（目标基础攻击力），最高不超过停云攻击力的 25%（5 魂 55% / 27%；两者取较小的）'
mig(1202, z['n'], new_n, z['t'])
z['tca'] = 50; z['lx'] = {'tCapA': [50, 55]}; z['n'] = new_n

log = """<li><b>2026-11-17（差异清单第 23 批）：tv 141（tools/fix141.py）</b>。依据官方原文（Mar-7th character_skills / character_ranks）。① <b>卢卡裂伤</b>「每回合开始时受到等同于自身 24% 生命上限的物理属性持续伤害，最多不超过卢卡攻击力的 338%」：以前一律按 338% 攻击力，现在取敌人生命上限 24% 和攻击力 338%（3 魂 371.8%）里较小的（敌人生命上限：开了「我方伤害扣敌人生命值」按当前阶段的上限，否则按敌人卡填的 / 官方资料；都没有时仍按攻击力上限），【碎天拳】引爆 85% 也一样。② <b>罗刹 E1</b>（结界生效时我方全体攻击力 +20%）原来是展开结界时给 2 回合，现在跟着【结界】走（结界结束或罗刹倒下时消失）；E1、<b>E4</b>（虚弱 12%）补上秘技进战展开的结界。③ <b>罗刹 E2</b>「目标当前生命值 &lt;50% 时罗刹提供的治疗量提高 30%」原来是另外多回复一次 30%（相当于治疗量 ×1.3），改成治疗加成 +30%、和卡片治疗加成相加（卡片治疗加成为 0 时数值不变）。④ <b>停云【赐福】</b>「攻击力提高 50%，最高不超过停云当前攻击力的 25%」以前一律按停云攻击力 25%，现在和目标基础攻击力 × 50% 取较小的（5 魂 55% / 27%）。⑤ 修正：tv 139 / 140 没加进老存档的迁移路径，老存档每次打开都重跑迁移、tv 139 的光锥 / 遗器重建没生效，这次一起补上。<b>对已有配置</b>：行动顺序不变（这几条只影响伤害显示和罗刹 E2 的治疗量）；罗刹 E1 在结界被提前刷新 / 结束时攻击力加成的持续时间会变。</li>"""
record = """2026-11-17（差异清单第 23 批）：tv 141（tools/fix141.py）。改：卢卡战技 / 秘技裂伤 hpv 24（dot 新字段 hpV，伤害层取敌人生命上限 24% 和攻击力 338% 较小的）；罗刹 E1 改 bk st:结界 d 0 + start 版（ns 结界），E4 加 start 版，E2 治疗改 hbup cast 30 tgh lt 50（skill / hpLoss 两条）；停云【赐福】攻击力 dbuf 加 tca 50（lx 55，字段 tCapA）。引擎：castHb 认 tgHp 和 hpLoss；迁移入口补 fixTpl139。
  核对无误：罗刹 E6、E2 护盾；停云赐福 3 回合 / 只对最新目标。存疑：击破造成的裂伤（7% / 16% 生命上限、上限按等级和韧性）仍按上限算。"""

# ---------------- 收尾（tv 140 没按 fixlib 的格式写，这里自己处理迁移入口） ----------------
F.put('DB', F.DB)
s = F.s
a = s.index('  // tv 139：')
s = s[:a] + (f'  // tv {TV}：差异清单第 23 批（卢卡裂伤上限、罗刹 E1 / E2 / E4、停云【赐福】上限）（tools/fix{TV}.py）\n'
             f'  const TPLFIX{TV} = ' + json.dumps(F.FIX, ensure_ascii=False) + ';\n'
             f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a:]
F.s = s
# 老存档路径：tv 43 起的迁移以前没有版本判断，每次升版本都从 fixTpl43 重跑一遍（中途会删掉说明改过的效果、丢掉用户的开关），这里加上判断，只跑存档之后的
L0 = [l for l in F.s.split('\n') if l.startswith('    if (s.tv >= 2) { const keep = S; S = s; try {')]
assert len(L0) == 1
L1 = re.sub(r'(?<!\) )fixTpl(\d+)\(s\);', lambda m: m.group(0) if int(m.group(1)) < 43 else f'if (!(s.tv >= {m.group(1)})) fixTpl{m.group(1)}(s);', L0[0])
F.rep(L0[0], L1)
F.rep('if (s.tv >= 140) return;', f'if (s.tv >= {TV}) return;')
F.rep('if (!(s.tv >= 138)) fixTpl138(s); } finally { S = keep; } s.tv = 138; return; }', f'if (!(s.tv >= 138)) fixTpl138(s); if (!(s.tv >= 139)) fixTpl139(s); if (!(s.tv >= {TV})) fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
F.rep('tools/fix140.py）\n    s.tv = 140;', f'tools/fix140.py）\n    fixTpl{TV}(s);\n    s.tv = {TV};')
F.rep('if (!(S.tv >= 140)) { migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
i = F.s.index(ul, F.s.index('<details id="changelog">')) + len(ul)
F.s = F.s[:i] + log.strip() + '\n' + F.s[i:]
head = '<!-- 校对记录（每日任务按此挑选最久未校对的项目）\n'
i = F.s.index(head) + len(head)
F.s = F.s[:i] + record.strip() + '\n' + F.s[i:]
out = F.s.replace('\r\n', '\n')
if CRLF: out = out.replace('\n', '\r\n')
open(P, 'w', encoding='utf-8', newline='').write(out)
print('ok tv', TV, {k: len(v['add']) for k, v in F.FIX.items()})
