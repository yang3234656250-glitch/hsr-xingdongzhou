"""tv 78：自动化 —— 开拓者•记忆 8007 / 8008【史诗】（终结技后获得，持有且迷迷在场时普攻自动强化）、青雀 1201【暗杠】（终结技后下个回合开始自动进入，
不能施放战技、普攻自动变【杠上开花！】）、星期日 1313 E6（暴击率溢出转暴伤）、游戏尘寰 23021【彩焰】（装备者每恢复 4 个战技点再获得【假面】）。
用法：python3 tools/fix78.py index.html <官方 json 目录>
引擎：模板 x.ebSm（ebSt 之外还要自己的某个忆灵在场）、x.ebAll（拥有 ebSt 状态时战技也改成强普）、x.stTurn = [状态 A, 状态 B]（自己回合开始、选动作之前：有 A 就换成 B）；
spChg 效果的 spr（字段 spR）= 只算恢复（含溢出）；伤害增益类型 crO（暴击率超过 100% 的部分每 1% 暴伤 +X%，取最大）。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 78, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('''      if (a === "basic" && ((num(X.ebCnt) > 0 && num(u.cnt) >= num(X.ebCnt) - 1e-9) || (X.ebSt && hasSt(u, String(X.ebSt))))) a = "ebasic";''',
'''      const ebOn = X.ebSt && hasSt(u, String(X.ebSt)) && (!X.ebSm || U.some(z => z.sm && z.sm.owner === u.id && z.sm.key === X.ebSm && !z.gone));   // ebSm：还要自己的这个忆灵在场（开拓者•记忆【史诗】）
      if (a === "basic" && ((num(X.ebCnt) > 0 && num(u.cnt) >= num(X.ebCnt) - 1e-9) || ebOn)) a = "ebasic";
      if (a === "skill" && ebOn && X.ebAll) a = "ebasic";   // ebAll：拥有这个状态时不能施放战技（青雀【暗杠】）''')
F.rep('''      const rec = { uid: actor.id, t, turn: actor.turns, spd, cycle: cycleOf(t), seq: seq++, ult: actor === swU && sw.inUlt };''',
'''      { const sT = tx(actor).stTurn; if (Array.isArray(sT) && hasSt(actor, String(sT[0]))) { endSt(actor, String(sT[0])); setSt(actor, { stKey: String(sT[1]), value: 1, duration: 0 }, actor, actor.color); } }   // 回合开始、选动作之前换状态（青雀：四张同花色 → 【暗杠】）
      const rec = { uid: actor.id, t, turn: actor.turns, spd, cycle: cycleOf(t), seq: seq++, ult: actor === swU && sw.inUlt };''')
F.rep('''for (let i = 0; i < Math.abs(d); i++) { if (d < 0) { spSpent(1); teamFire("spUse", who); } teamFire("spChg", who, e => !e.spOvf); }''',
      '''for (let i = 0; i < Math.abs(d); i++) { if (d < 0) { spSpent(1); teamFire("spUse", who); } teamFire("spChg", who, d < 0 ? (e => !e.spOvf && !e.spR) : (e => !e.spOvf)); }''')
F.rep('''for (let i = 0; i < Math.min(ov, Math.round(v)); i++) teamFire("spChg", who, e => e.spOvf);''', '''for (let i = 0; i < Math.min(ov, Math.round(v)); i++) teamFire("spChg", who, e => e.spOvf || e.spR);''')
F.rep('''if (sp > s0) teamFire("spChg", u, e => !e.spOvf); else teamFire("spChg", u, e => e.spOvf);''', '''if (sp > s0) teamFire("spChg", u, e => !e.spOvf); else teamFire("spChg", u, e => e.spOvf || e.spR);''')
F.rep('''teamFire("spUse", u); teamFire("spChg", u, e => !e.spOvf); }''', '''teamFire("spUse", u); teamFire("spChg", u, e => !e.spOvf && !e.spR); }''')
F.rep('''      if (x.ovf) e.spOvf = 1;''', '''      if (x.ovf) e.spOvf = 1; if (x.spr) e.spR = 1;   // spR：只算恢复（含溢出）''')
F.rep('''    const critM = e.dot || e.brk ? 1 : 1 + Math.min(1, Math.max(0, cr) / 100) * Math.max(0, cd) / 100;''',
      '''    { const co = DB0.reduce((p, x) => x[0] === "crO" ? Math.max(p, num(x[2])) : p, 0); if (co > 0 && cr > 100) cd += (cr - 100) * co; }   // 暴击率溢出转暴伤（星期日 E6）
    const critM = e.dot || e.brk ? 1 : 1 + Math.min(1, Math.max(0, cr) / 100) * Math.max(0, cd) / 100;''')
F.rep('''const DBM = [["be", "击破特攻 %"], ''', '''const DBM = [["be", "击破特攻 %"], ["crO", "暴击率超过 100% 时每 1% 换暴伤 X%"], ''')
F.rep('''be: "击破特攻", bkd: "击破伤害提高",''', '''be: "击破特攻", crO: "溢出暴击率转暴伤 ×", bkd: "击破伤害提高",''')

# ================= 开拓者•记忆 =================
for cid in (8007, 8008):
    hast(cid, '未完的尾声', '施放终结技后，获得1层【史诗】，最多持有2层。持有【史诗】且迷迷在场时，普攻强化为【明天，一同写下！】')
    has(str(cid * 100 + 8), '消耗1层【史诗】')
    c = C[cid]
    new = list(c['eff']) + [
        dict(y='state', t='ult', tg='self', sn='史诗2', v=1, d=0, ns='史诗', n='行迹未完的尾声：施放终结技后获得 1 层【史诗】（已有 1 层时变成 2 层，最多 2 层）'),
        dict(y='state', t='ult', tg='self', sn='史诗', v=1, d=0, n='行迹未完的尾声：持有【史诗】且迷迷在场时，普攻自动强化为【明天，一同写下！】'),
        dict(y='state', t='ebasic', tg='self', sn='史诗', v=0, d=0, ns='!史诗2', n='强化普攻【明天，一同写下！】：消耗 1 层【史诗】（只剩 1 层时）'),
        dict(y='state', t='ebasic', tg='self', sn='史诗2', v=0, d=0, n='强化普攻【明天，一同写下！】：消耗 1 层【史诗】（有 2 层时剩 1 层）'),
    ]
    F.rebuild(cid, new, x={'ebSt': '史诗', 'ebSm': 'mimi'}, notes=['【史诗】：每次开大 +1 层（最多 2 层），持有【史诗】且迷迷在场时普攻自动强化（每次行动选“普攻”才会变；选战技仍是战技）'])

# ================= 青雀 =================
c = C[1201]
has('120104', '处于【暗杠】状态时无法再次施放战技'); has('120103', '并获得4张相同花色的琼玉牌')
new = list(c['eff']) + [
    dict(y='state', t='ult', tg='self', sn='四暗刻', v=1, d=0, n='终结技：获得 4 张相同花色的琼玉牌（下一个自己的回合开始时进入【暗杠】）'),
    dict(y='state', t='ebasic', tg='self', sn='暗杠', v=0, d=0, n='天赋：【暗杠】在施放【杠上开花！】后结束'),
]
c['notes'] = [n for n in c.get('notes', []) if '这里没有自动切换' not in n] + ['终结技后下一个自己的回合开始时自动进入【暗杠】：不能施放战技，普攻自动变【杠上开花！】；靠随机抽牌凑齐四张同花色的情况没法模拟，需要时在“每次行动”里点成强普']
F.rebuild(1201, new, x={'ebSt': '暗杠', 'ebAll': 1, 'stTurn': ['四暗刻', '暗杠']})

# ================= 星期日 E6 =================
has('r:131306', '天赋的暴击率提高效果生效时，当目标的暴击率超过100%，每溢出1%暴击率提高2%暴击伤害')
e6 = F.eid(1313, 6); e6['eff'] = e6.get('eff', []) + [
    dict(y='dbuf', t='skill', tg='skpick', m='crO', v=2, d=4, cnt='own', bk='tfo', n='E6：天赋的暴击率提高效果生效时，目标暴击率超过 100% 的部分每 1% 暴击伤害 +2%（战技目标）'),
    dict(y='dbuf', t='ult', tg='ultpick', m='crO', v=2, d=4, cnt='own', bk='tfo', n='E6：同上（终结技目标）')]

# ================= 游戏尘寰 =================
LR = json.load(open(sys.argv[2] + '/light_cone_ranks.json', encoding='utf-8'))
F.has(LR['23021']['desc'], '装备者每恢复1个战技点，获得1层【彩焰】，恢复时溢出的战技点也会被计算在内。当【彩焰】达到#4[i]层后，移除所有【彩焰】并获得【假面】，持续#3[i]回合')
P = LR['23021']['params']; assert [p[3] for p in P] == [4] * 5 and [p[2] for p in P] == [4] * 5 and [p[5] for p in P] == [3] * 5
cr = [r4(p[4] * 100) for p in P]; cd = [r4(p[1] * 100) for p in P]
L = {c['id']: c for c in F.DB['lcs']}
L[23021]['eff'] = [
    dict(y='state', t='start', tg='self', sn='假面', v=1, d=3, n='光锥【假面】：战斗开始时获得【假面】，持续 3 回合'),
    dict(y='dbuf', t='start', tg='others', m='cr', v=cr, d=0, bk='st:假面', n='光锥【假面】：装备者持有【假面】时，队友暴击率提高'),
    dict(y='dbuf', t='start', tg='others', m='cd', v=cd, d=0, bk='st:假面#2', n='光锥【假面】：装备者持有【假面】时，队友暴击伤害提高'),
    dict(y='state', t='spChg', aw='self', spr=1, nth=4, tg='self', sn='假面', v=1, d=4, n='光锥【彩焰】：装备者每恢复 1 个战技点（含溢出）获得 1 层，4 层时移除并获得【假面】，持续 4 回合'),
    dict(y='dbuf', t='spChg', aw='self', spr=1, nth=4, tg='others', m='cr', v=cr, d=0, bk='st:假面', n='光锥【彩焰】：重新获得【假面】时队友暴击率提高'),
    dict(y='dbuf', t='spChg', aw='self', spr=1, nth=4, tg='others', m='cd', v=cd, d=0, bk='st:假面#2', n='光锥【彩焰】：重新获得【假面】时队友暴击伤害提高'),
]

F.finish('自动化：开拓者•记忆【史诗】、青雀【暗杠】、星期日 E6、游戏尘寰【彩焰】', '''<li><b>2026-11-11（自动化：开拓者•记忆【史诗】、青雀【暗杠】、星期日 E6、游戏尘寰【彩焰】）</b>：tv 78（tools/fix78.py）。<b>开拓者•记忆</b>：开大后获得【史诗】（最多 2 层），持有且迷迷在场时“普攻”自动变强化普攻并消耗 1 层（选战技的回合不变）。<b>青雀</b>：开大后下一个自己的回合开始自动进入【暗杠】，这一回合不能施放战技、普攻变【杠上开花！】，之后【暗杠】结束（随机抽牌凑齐的情况仍要手动点强普）。<b>星期日 E6</b>：天赋的暴击率加成在身上时，暴击率超过 100% 的部分每 1% 换 2% 暴击伤害（伤害显示）。<b>游戏尘寰</b>：装备者每恢复 4 个战技点（含溢出）重新获得【假面】 4 回合。对已有配置：开拓者•记忆开大后、青雀开大后的那次行动会自动变成强普，行动顺序、战技点会变。</li>''',
'''2026-11-11：开拓者•记忆（8007 / 8008）【史诗】、青雀（1201）【暗杠】、星期日（1313）E6、光锥游戏尘寰 —— tv 78（tools/fix78.py）。新：x.ebSm / x.ebAll / x.stTurn、spChg 的 spr、伤害增益 crO。
  未改 / 存疑：开拓者•记忆的【史诗】只在每次行动选“普攻”时自动强化；青雀只做了终结技给的四张同花色，抽牌随机不模拟；游戏尘寰【彩焰】只算装备者自己的恢复。''')

s = open(sys.argv[1], encoding='utf-8').read()
a = 'fixTpl(s, TPLFIX78); } finally { S = keep; } }'
assert s.count(a) == 1
s = s.replace(a, 'fixTpl(s, TPLFIX78); for (const u of s.units) if (u.kind === "ally" && !u.sm && u.lc === 23021) applyEquip(u); } finally { S = keep; } }   // 游戏尘寰改了')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('eq migration ok')
