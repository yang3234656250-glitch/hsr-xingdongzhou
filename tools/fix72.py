"""tv 72：击破第 5 批 —— 乱破 1317 天赋（充能、第 3 段击破伤害和无视弱点削韧）、行迹枯叶、E6；大丽花 1321 E1 固定削韧。
用法：python3 tools/fix72.py index.html <官方 json 目录>
引擎：效果类型 tfix（直接削韧：v = 游戏里的点数，vpc = 施放者每点计数另加几点，cz = 读完计数后清零，ig = 无视弱点属性，
pmx = [韧性上限的 %, 最少几点, 最多几点]，opt = 每个敌人只触发 1 次；不吃击破效率，不转超击破）；brkd 也支持 vpc（每点计数倍率另加 %）。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 72, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast
def lvE(cid, base):
    for r in range(1, 7):
        for z in (F.RK[str(cid * 100 + r)].get('level_up_skills') or []):
            if str(z.get('id')) == str(base): return r
    raise KeyError(base)
D = lambda **k: dict(dict(y='dbuf', d=0), **k)

# ---------- 引擎 ----------
F.rep('''      const shGave = new Set();   // 一次护盾效果只算一次“提供护盾”
''', '''      const shGave = new Set();   // 一次护盾效果只算一次“提供护盾”
      let tfc = null;   // tfix：这一次效果开始时施放者的计数（cz 会在读完后清零）
''')
F.rep('''        if (eff.type === "brkd") {''', '''        if (eff.type === "tfix") {   // 直接削韧（固定削韧 / 无视弱点属性的削韧）：不吃击破效率，削到 0 照常击破
          const own = src ? (ownerOf(src) || src) : null; if (!own || tg.kind !== "enemy" || !brkOn) continue;
          const mx = toughMax(tg); if (!(mx > 0)) continue;
          if (tfc == null) { tfc = Math.round(num(own.cnt)); if (eff.cz && tfc > 0) { own.cnt = 0; addLog(`${own.name} 消耗全部 ${tfc} 点${own.cntName || "计数"}`, false, own.color); } }
          if (tg.broken) continue;
          const key = own.id + ":" + (eff.bk || eff.id);
          if (eff.opt) { if ((tg.tf1 || {})[key]) continue; (tg.tf1 = tg.tf1 || {})[key] = 1; }
          const wl = ELW[(tplOf(own) || {}).elem] || "物", m = monOf(tg);
          if (!eff.ig && m && m.w && !m.w.includes(wl) && !(tg.wk || []).some(z => z.el === "all" || z.el.includes(wl))) continue;
          const pts = Array.isArray(eff.pmx) ? Math.min(num(eff.pmx[2]), Math.max(num(eff.pmx[1]), mx / 3 * num(eff.pmx[0]) / 100)) : v + num(eff.vpc) * tfc; if (!(pts > 0)) continue;
          if (tg.tcur == null) tg.tcur = mx;
          tg.tcur -= pts * 3;
          addLog(`${src.name} 对 ${tg.name} 削韧 ${fmt(pts, 1)} 点${eff.ig ? "（无视弱点属性）" : ""}`, false, srcColor);
          if (tg.tcur <= 1e-9) doBreak(tg, own, wl, mx);
          continue;
        }
        if (eff.type === "brkd") {''')
F.rep('''const vv = Array.isArray(eff.vcn) ? num(eff.vcn[Math.min(eff.vcn.length, Math.round(num(own.cnt))) - 1]) : v; if (!(vv > 0)) continue;''',
      '''const vv = (Array.isArray(eff.vcn) ? num(eff.vcn[Math.min(eff.vcn.length, Math.round(num(own.cnt))) - 1]) : v) + num(eff.vpc) * Math.round(num(own.cnt)); if (!(vv > 0)) continue;''')
F.rep('''      if (x.wel) e.wel = x.wel;''', '''      if (x.vpc) e.vpc = x.vpc; if (x.cz) e.cz = 1; if (x.ig) e.ig = 1; if (x.opt) e.opt = 1; if (x.pmx) e.pmx = x.pmx;   // 直接削韧 tfix
      if (x.wel) e.wel = x.wel;''')
F.rep('''["brkd", "造成一次击破伤害"], ''', '''["brkd", "造成一次击破伤害"], ["tfix", "直接削韧（点数）"], ''')

# ---------- 乱破 ----------
c = C[1317]
has('131704', '每当敌方目标的弱点被击破时，乱破获得1点充能，最多拥有#1[i]点充能'); has('131704', '额外对敌方全体造成等同于乱破#3[i]%虚数属性击破伤害的击破伤害，该伤害可无视弱点属性削减#4[i]点韧性，并消耗所有充能，每点充能使本次击破伤害倍率提高#5[i]%，并使无视弱点属性的削韧值提高#6[i]点')
hast(1317, '忍法帖•魔天', '乱破额外获得#2[i]点充能'); hast(1317, '忍法帖•枯叶', '敌方目标的弱点被击破时，受到的击破伤害提高#1[i]%')
has('r:131706', '战斗开始时乱破获得5点天赋效果的充能，且充能上限增加5点。发动【忍具•降魔花弁】第3段攻击后获得5点充能')
et = lvE(1317, 131704); t10, t12 = prm('131704', 10), prm('131704', 12); assert [r4(v) for v in t10] == [10, 0, 0.6, 2, 0.5, 1] and [r4(t12[2]), r4(t12[4])] == [0.66, 0.55]
assert F.TR['1317103']['params'][0] == [0.02, 2400, 0.01, 0.08, 2] and not c.get('cnt')
c['notes'] = [n for n in c.get('notes', []) if '天赋的充能' not in n]
old_mt = [n for n, t in F.OLD[1317] if n and n.startswith('行迹忍法帖•魔天')][0]
for e in c['eff']:
    if (e.get('n') or '').startswith('行迹忍法帖•魔天'): e['n'] = '行迹忍法帖•魔天：精英级别及以上的敌方目标的弱点被击破时恢复 10 点能量（按敌人都是精英及以上算，打小怪时关掉）'
new = list(c['eff']) + [
    dict(y='count', t='break', tg='self', v=1, n='天赋：每当敌方目标的弱点被击破时获得 1 点充能（最多 10 点）'),
    dict(y='count', t='break', tg='self', v=1, n='行迹忍法帖•魔天：精英级别及以上的敌方目标的弱点被击破时额外获得 1 点充能（按敌人都是精英及以上算，打小怪时关掉）'),
    dict(y='brkd', t='ebasic', tg='enemies', nb=1, v=60, vpc=50, xe=et, n='天赋：【忍具•降魔花弁】第 3 段攻击时，额外对敌方全体造成 60%% 虚数属性击破伤害的击破伤害，每点充能倍率 +50%%（%d 魂 66%% / 55%%）' % et),
    dict(y='brkd', t='ebasic', tg='enemies', nb=1, v=66, vpc=55, me=et, n='天赋（%d 魂起）：第 3 段的击破伤害倍率 66%%，每点充能 +55%%' % et),
    dict(y='tfix', t='ebasic', tg='enemies', v=2, vpc=1, cz=1, ig=1, bk='tf', n='天赋：这次击破伤害无视弱点属性削减 2 点韧性，每点充能 +1 点，并消耗所有充能'),
    dict(y='dbuf', t='break', tg='evt', m='vuln', sc='k', v=2, d=2, bk='ky', n='行迹忍法帖•枯叶：敌方目标的弱点被击破时，受到的击破伤害 +2%，持续 2 回合（乱破攻击力高于 2400 时每超过 100 点再 +1%，最多再 +8%，自己改数值）'),
]
F.rebuild(1317, new, rename={old_mt: '行迹忍法帖•魔天：精英级别及以上的敌方目标的弱点被击破时恢复 10 点能量（按敌人都是精英及以上算，打小怪时关掉）'},
          cnt={'n': '充能', 'at': 0, 'max': 10, 'lm': [6, 15]}, notes=['天赋的击破伤害和削韧排在强化普攻本身的削韧之前结算（游戏里是第 3 段时）；E2（前 2 段对单体削韧 +50%）、秘技的削韧和击破伤害还没做'])
e6 = F.eid(1317, 6); e6['eff'] = e6.get('eff', []) + [
    dict(y='count', t='start', tg='self', v=5, n='E6：战斗开始时获得 5 点充能（充能上限 15 点）'),
    dict(y='count', t='ebasic', tg='self', v=5, n='E6：发动【忍具•降魔花弁】第 3 段攻击后获得 5 点充能')]
# ---------- 大丽花 E1 ----------
has('r:132101', '对受到攻击的敌方目标额外造成等同于其韧性上限25%的固定削韧（至少10点，至多300点）。该效果每个敌方目标只能触发1次')
e1 = F.eid(1321, 1); e1['eff'] = e1.get('eff', []) + [
    dict(y='tfix', t='atk', aw='self', tg='efirst', pmx=[25, 10, 300], opt=1, ig=1, bk='e1f', n='E1：【共舞者】（大丽花）施放攻击后，对受到攻击的敌方目标额外造成其韧性上限 25% 的固定削韧（至少 10 点，至多 300 点），每个敌方目标只触发 1 次（按主目标算）'),
    dict(y='tfix', t='atk', aw='others', **{'as': '共舞者'}, tg='efirst', pmx=[25, 10, 300], opt=1, ig=1, bk='e1f', n='E1：【共舞者】（另一位）施放攻击后的固定削韧，和上一条共用每个敌方目标 1 次')]

F.finish('击破第 5 批（乱破天赋、大丽花 E1 固定削韧）', '''<li><b>2026-11-11（击破第 5 批：乱破天赋、大丽花 E1）</b>：tv 72（tools/fix72.py）。新效果类型「直接削韧」（按游戏里的点数，可以无视弱点属性、按计数加点、按韧性上限的百分比）。<b>乱破</b>：敌方弱点被击破时获得 1 点充能（魔天再 +1，最多 10 点；E6 开局 5 点、上限 15、第 3 段后 +5）；强化普攻第 3 段额外对敌方全体造成 60% 虚数属性击破伤害（每点充能 +50%），无视弱点削 2 点韧性（每点充能 +1），并清空充能；行迹枯叶（被击破的敌人受到的击破伤害 +2%）。<b>大丽花 E1</b>：【共舞者】攻击后对主目标造成韧性上限 25% 的固定削韧，每个敌人 1 次。只在放了带韧性的敌人时有变化。</li>''',
'''2026-11-11（击破第 5 批）：乱破（1317）天赋 / 枯叶 / E6、大丽花（1321）E1 固定削韧 —— tv 72（tools/fix72.py）。新：效果类型 tfix、brkd 的 vpc。
  未改 / 存疑：乱破天赋的击破伤害和削韧在强化普攻本身的削韧之前结算；E1 固定削韧和上面“每个敌方目标 1 次”两条共用，按主目标；枯叶按 2%；乱破 E2、秘技，同谐主随波逐流（官方数据没有战技每段的削韧值），大丽花弃旧恋新的 20 点固定削韧没做。''')
