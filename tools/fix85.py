"""tv 85：消灭 / 击破 / 救下目标引起的效果，状态的触发次数，持续治疗跟着护盾。
用法：python3 tools/fix85.py index.html <官方 json 目录>
引擎：
- 受到致命攻击时，效果字段 fps（fPost）= 只在“这张卡上前面的效果把目标救回来”之后才生效（藿藿禳命 −1、万敌退出【血仇】、千冶•刃解除结界）。teamFire 的过滤函数多传一个参数 u。
- 新触发 ekill（敌人被消灭时，事件对象 = 被消灭的敌人；要开“我方伤害扣敌人生命值”）。
- 状态字段 sx 可以是负数：已有的状态持续回合 −N（减到 0 结束），没有就不加。
- 伤害增益字段 dx（dExt）：只把已有的这组增益延长 N 回合。
- 伤害增益条件 ec.brk：目标处于弱点击破状态（灵砂 1 魂）。
- 需要状态的效果字段 scp（stCap）：每次获得这个状态最多触发 N 次（白露【生息】）。
- 持续治疗字段 hsk（hotSh）：目标不再持有这一组护盾时持续治疗消失（三月七 6 魂）。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 85, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('''      if (x.alv) e.alv = 1;''', '''      if (x.alv) e.alv = 1;
      if (x.fps) e.fPost = 1; if (x.scp) e.stCap = x.scp; if (x.hsk) e.hotSh = x.hsk; if (x.dx) e.dExt = x.dx;   // 救下目标后才生效；每次获得状态最多触发 N 次；持续治疗跟着护盾；延长已有增益''')
F.rep('''(filt && !filt(e))''', '''(filt && !filt(e, u))''')
F.rep('''      teamFire("fatal", tg, () => (hpCur(tg) ?? 1) <= 1e-6);''', '''      let saver = null, lastU = null;   // 谁把目标救回来了：救回来之后只有它的 fps 效果（禳命 −1、退出血仇……）还生效
      teamFire("fatal", tg, (e, u) => { const dead = (hpCur(tg) ?? 1) <= 1e-6; if (!dead && !saver) saver = lastU; if (e.fPost) return !dead && saver === u; if (!dead) return false; lastU = u; return true; });''')
F.rep('''      if (num(eff.stExt) > 0 && tg.st[k] && tg.st[k].tick !== "chg") { tg.st[k].left += Math.round(num(eff.stExt)); return; }''',
      '''      if (num(eff.stExt) < 0) { const s0 = tg.st[k]; if (s0 && s0.tick !== "chg") { s0.left += Math.round(num(eff.stExt)); if (s0.left <= 0) endSt(tg, k); } return; }   // 已有的状态持续回合 −N（藿藿救人后【禳命】−1）
      if (num(eff.stExt) > 0 && tg.st[k] && tg.st[k].tick !== "chg") { tg.st[k].left += Math.round(num(eff.stExt)); return; }''')
F.rep('''      if (eff.mv && bk && !teamT && !onEnemy) for (const z of U) if (!tgs.includes(z)) z.buffs = z.buffs.filter(b => b.key !== key);''',
      '''      if (num(eff.dExt) > 0) {   // 只延长已有的这组增益（彦卿 6 魂：消灭敌人时终结技增益延长 1 回合）
        for (const tg of tgs) { const kk = teamT ? key + ":" + (eff.target === "teamMem" ? "mem" : "all") : key, old = tg.buffs.find(b => b.key === kk); if (old) { if (old.own) old.left += Math.round(num(eff.dExt)); else if (isFinite(old.expire)) old.expire += Math.round(num(eff.dExt)); } }
        return;
      }
      if (eff.mv && bk && !teamT && !onEnemy) for (const z of U) if (!tgs.includes(z)) z.buffs = z.buffs.filter(b => b.key !== key);''')
F.rep('''      if (c.hpv && ePct(en) < hpPct(u) - 1e-9) return 0;''', '''      if (c.hpv && ePct(en) < hpPct(u) - 1e-9) return 0;
      if (c.brk && !(toughMax(en) > 0 && en.broken)) return 0;   // 目标处于弱点击破状态''')
F.rep('''c.hpv == null && c.dfr == null''', '''c.hpv == null && c.brk == null && c.dfr == null''')
F.rep('''        if (k && has === neg) return;
      }''', '''        if (k && has === neg) return;
        if (!neg && k && num(eff.stCap) > 0) { const T = eff.stOn === "evt" ? evTarget : eff.stOn ? null : src, s0 = T && T.st && T.st[k]; if (s0) { if (num(s0.used) >= num(eff.stCap)) return; s0.used = num(s0.used) + 1; } }   // 每次获得这个状态最多触发 N 次（白露【生息】）
      }''')
F.rep('''      for (const x of u.hots) {
        const a = healAmt(x.eff, x.src, u, num(x.eff.value), num(x.eff.flat), true);''', '''      for (const x of u.hots) {
        if (x.eff.hotSh && !(shOf(u, x.eff.hotSh) > 0)) continue;   // 护盾没了，跟着护盾的持续治疗也没了（三月七 6 魂）
        const a = healAmt(x.eff, x.src, u, num(x.eff.value), num(x.eff.flat), true);''')
F.rep('''      if (killer && killer.kind === "ally") fireEv("kill", killer);''', '''      if (killer && killer.kind === "ally") fireEv("kill", killer);
      fireAll("ekill", en);   // 敌人被消灭时（事件对象 = 这个敌人）''')
F.rep('''["kill", "消灭敌人时"], ''', '''["kill", "消灭敌人时"], ["ekill", "敌人被消灭时"], ''', 2)
F.rep('''kill: "消灭敌人时"''', '''kill: "消灭敌人时", ekill: "敌人被消灭时"''')
F.rep('''const EVTT = ["break", "kill", ''', '''const EVTT = ["break", "kill", "ekill", ''')
F.rep('''    if (e.alv) h.push("施加者倒下时消失");''', '''    if (e.alv) h.push("施加者倒下时消失");
    if (e.fPost) h.push("前面那条救下目标后才生效");
    if (num(e.stCap) > 0) h.push(`每次获得【${String(e.needSt || "").trim()}】最多触发 ${num(e.stCap)} 次`);
    if (e.hotSh) h.push("目标没有这组护盾时持续治疗消失");
    if (num(e.dExt) > 0) h.push(`只把已有的这组增益延长 ${num(e.dExt)} 回合`);''')
F.rep('''    if (c.dbf != null) L.push(`目标负面效果 ≥${c.dbf} 个时`);''', '''    if (c.dbf != null) L.push(`目标负面效果 ≥${c.dbf} 个时`);
    if (c.brk) L.push("目标处于弱点击破状态时");''')
assert '    const fireAll = ' in F.s and F.s.index('    const fireAll = ') < F.s.index('    const killEnemy = ')

def setx(e, **kw):
    for k, v in kw.items():
        if v is None: e.pop(k, None)
        else: e[k] = v
    return e
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]

# ---- 彦卿：受到伤害后【智剑连心】消失；6 魂消灭敌人时延长 ----
has('120904', '当彦卿受到伤害后，【智剑连心】将会消失'); has('r:120906', '消灭敌方目标时，如果当前持有【智剑连心】或终结技的增益效果，则使这些增益效果的持续时间全部延长1回合')
c = C[1209]; E = c['eff']; e = find(E, '战技：为彦卿附加【智剑连心】'); o = e['n']; n = '战技：为彦卿附加【智剑连心】，持续 1 回合（施放战技的这个回合结束时不算，所以这里写 2）'; e['n'] = n
E.insert(E.index(e) + 1, dict(y='state', t='hit2', tg='self', sn='智剑连心', v=0, n='天赋：受到伤害后【智剑连心】消失（受到攻击后）'))
c['notes'] = [x for x in c.get('notes', []) if '智剑连心' not in x] + ['【智剑连心】按“受到攻击后”消失（敌人没有伤害数值、或被护盾挡住时也算受到伤害）']
F.rebuild(1209, E, rename={o: n})
e6 = F.eid(1209, 6); e6['eff'] = [x for x in e6['eff'] if x.get('t') != 'kill'] + [
    dict(y='state', t='kill', tg='self', sn='智剑连心', v=1, sx=1, ns='智剑连心', n='E6 自在：消灭敌方目标时【智剑连心】持续时间延长 1 回合（要开“我方伤害扣敌人生命值”）'),
    dict(y='dbuf', t='kill', tg='self', m='cd', v=50, d=1, bk='ultc', dx=1, n='E6：消灭敌方目标时终结技的暴击伤害增益延长 1 回合')]

# ---- 藿藿 2 魂：救人后【禳命】−1 ----
has('r:121702', '使【禳命】的持续回合数减1')
e2 = F.eid(1217, 2); h = find(e2['eff'], 'E2 判官书符'); h['n'] = 'E2 判官书符，镇尾锁灵：拥有【禳命】时我方目标受到致命攻击不倒下，回复其 50% 生命上限（每场 2 次）'
e2['eff'] = [x for x in e2['eff'] if not x.get('fps')]; e2['eff'].insert(e2['eff'].index(h) + 1, dict(y='state', t='fatal', aw='all', tg='self', sn='禳命', v=1, sx=-1, fps=1, n='E2：救下目标后【禳命】持续回合数 −1'))

# ---- 万敌：救下自己后清空充能、退出【血仇】 ----
has('140404', '【血仇】状态期间，万敌受到致命攻击时不会陷入无法战斗状态，但会清空充能退出【血仇】状态并回复等同于自身#4[i]%生命上限的生命值')
c = C[1404]; E = c['eff']; h = find(E, '天赋：【血仇】期间受到致命攻击'); o = h['n']
n = '天赋：【血仇】期间受到致命攻击不倒下，清空充能、退出【血仇】，回复自身 50% 生命上限（按退出【血仇】后的生命上限：×2/3）'
setx(h, n=n, hpm=r4(100 / 1.5))
i = E.index(h)
E[i + 1:i + 1] = [dict(y='count', t='fatal', aw='self', tg='self', m='set', v=0, fps=1, n='天赋：救下自己后清空充能'),
                  dict(y='state', t='fatal', aw='self', tg='self', sn='血仇', v=0, fps=1, n='天赋：救下自己后退出【血仇】')]
F.rebuild(1404, E, rename={o: n})

# ---- 千冶•刃：救下自己后解除结界 ----
has('150703', '若受到致命攻击时，不会陷入无法战斗状态，但会解除结界退出【无量忿怒】状态并回复等同于自身#6[i]%生命上限的生命值')
c = C[1507]; E = c['eff']; h = find(E, '终结技：【无量忿怒】中受到致命攻击'); o = h['n']; n = '终结技：【无量忿怒】中受到致命攻击不倒下，回复自身 50% 生命上限，并解除结界'; h['n'] = n
E.insert(E.index(h) + 1, dict(y='dismiss', t='fatal', aw='self', tg='sm:wl', v=0, fps=1, n='终结技：救下自己后解除结界（【无量忿怒】倒计时离场，退出【无量忿怒】）'))
F.rebuild(1507, E, rename={o: n})

# ---- 寒鸦：【承负】的敌人被消灭 ----
hast(1215, '幽府', '持有【承负】的敌方目标被消灭时，如果【承负】为全队回复战技点的触发次数小于等于#1[i]，则额外回复#2[i]点战技点')
c = C[1215]; E = c['eff']
st = find(E, '战技：敌方目标陷入【承负】'); i = E.index(st)
E[i + 1:i + 1] = [dict(y='state', t='ally', aw='self', aa=['skill'], tg='enemies', sn='承负', v=0, n='战技：【承负】只对最新的目标生效（先从别的敌人身上去掉）'),
                  dict(y='state', t='ally', aw='self', aa=['skill'], tg='efirst', sn='承负', v=1, d=0, n='战技：被打的敌人（主目标）挂上【承负】')]
en = find(E, '战技：【承负】触发 2 次战技点恢复后自动解除'); i = E.index(en)
E.insert(i + 1, dict(y='state', t='atk', aw='all', aa=['basic', 'ebasic', 'skill', 'fskill', 'ult'], ns='承负', nc=4, tg='enemies', sn='承负', v=0, n='战技：【承负】解除时敌人身上的标记一起去掉'))
E += [dict(y='sp', t='ekill', tg='self', v=1, ns='承负', so='evt', ltc=4, n='行迹幽府：持有【承负】的敌人被消灭时，若【承负】恢复战技点的次数 ≤1，额外恢复 1 个战技点'),
      dict(y='state', t='ekill', tg='self', sn='承负', v=0, ns='承负', so='evt', n='【承负】的敌人被消灭：【承负】结束'),
      dict(y='count', t='ekill', tg='self', m='set', v=0, ns='承负', so='evt', n='【承负】的敌人被消灭：计数清零')]
c['notes'] = [x for x in c.get('notes', []) if '幽府' not in x] + ['【承负】挂在战技主目标（第一个敌人）上；按我方所有普攻 / 战技 / 终结技都打到承负目标算；幽府要开“我方伤害扣敌人生命值”']
F.rebuild(1215, E)

# ---- 流萤 2 魂：击破 / 消灭时额外回合 ----
has('r:131002', '「完全燃烧」状态下施放强化普攻、强化战技消灭敌方目标或使目标陷入弱点击破状态时，装甲「萨姆」立即获得1个额外回合。该效果在1回合后可再次触发')
e2 = F.eid(1310, 2); x = find(e2['eff'], 'E2 自破碎的天空坠落')
setx(x, off=None, ac=None, bby=1, cdt=1, n='E2 自破碎的天空坠落：「完全燃烧」状态下击破或消灭敌人时立即获得 1 个额外回合（1 回合后可再次触发；消灭要开“我方伤害扣敌人生命值”）')

# ---- 灵砂 1 魂：被击破的敌人防御力 −20% ----
has('r:122201', '当有敌方单位的弱点被击破时，使其防御力降低20%')
e1 = F.eid(1222, 1); x = find(e1['eff'], 'E1：敌人被击破时防御力')
setx(x, t='start', d=0, off=None, ec={'brk': 1}, n='E1：被击破的敌人防御力 −20%（处于弱点击破状态期间）')

# ---- 白露【生息】触发次数 ----
has('121104', '拥有【生息】的我方目标，在受到攻击后会回复等同于白露#1[f1]%生命上限+#2[i]的生命值，该效果可以触发#5[i]次'); hast(1211, '持明龙脉', '【生息】效果的触发次数增加#1[i]次')
c = C[1211]; x = find(c['eff'], '天赋：拥有【生息】的我方目标受到攻击'); o = x['n']; n = '天赋：拥有【生息】的我方目标受到攻击后回复生命值（每次获得【生息】可触发 3 次，含行迹持明龙脉 +1）'
setx(x, n=n, scp=3); c['notes'] = [y for y in c.get('notes', []) if '次数限制' not in y]
F.rebuild(1211, c['eff'], rename={o: n})

# ---- 艾丝妲【蓄能】----
has('100904', '每击中1名不同的敌方目标获得1层蓄能，若受到攻击的敌方目标弱点为火属性，则额外获得1层蓄能'); has('100904', '从自身的第2回合开始，艾丝妲每回合开始时蓄能层数减少#3[i]层')
c = C[1009]; E = c['eff']; x = find(E, '天赋：每层蓄能'); o = x['n']; n = '天赋：每击中 1 名不同的敌人获得 1 层蓄能，每层我方全体攻击力 +14%，最多 5 层'
setx(x, n=n, ph=1); i = E.index(x)
E[i + 1:i + 1] = [dict(x, n='天赋：被攻击的敌人（主目标）有火属性弱点时额外获得 1 层蓄能', ph=None, ewl='火'),
                  dict(x, n='天赋：从自身的第 2 回合开始，每回合开始时蓄能 −3 层', t='turn', aw=None, ph=None, sa=-3, s1=1)]
for z in E[i + 1:i + 3]:
    for k in [k for k, v in z.items() if v is None]: z.pop(k)
F.rebuild(1009, E, rename={o: n})

# ---- 三月七 6 魂：持续治疗跟着战技护盾 ----
has('r:100106', '在战技提供的护盾保护下的我方目标，每回合开始时回复等同于各自4%生命上限+106的生命值')
c = C[1001]; c['eff'][0]['shk'] = 'mq'; F.rebuild(1001, c['eff'])
e6 = F.eid(1001, 6); x = find(e6['eff'], 'E6 就这样'); setx(x, off=None, hsk='mq', n='E6 就这样，一直…：战技护盾保护下的我方目标每回合开始时回复各自 4% 生命上限 +106（护盾没了就停止）')

F.finish('消灭 / 击破 / 救人引起的效果', '''<li><b>2026-11-11（消灭、击破、救人）</b>：tv 85（tools/fix85.py）。<b>救人后的效果</b>：藿藿 2 魂救下目标后【禳命】−1；万敌【血仇】期间被救时清空充能、退出【血仇】；千冶•刃【无量忿怒】期间被救时解除结界。<b>敌人被消灭</b>（新触发，要开“我方伤害扣敌人生命值”）：寒鸦幽府（【承负】的敌人被消灭时额外 +1 战技点，【承负】结束）、彦卿 6 魂（延长【智剑连心】和终结技增益）、流萤 2 魂（击破或消灭时额外回合，1 回合冷却，默认开）。<b>其他</b>：彦卿受到攻击后【智剑连心】消失；灵砂 1 魂只给处于击破状态的敌人减防；白露【生息】每次最多触发 3 次；艾丝妲【蓄能】按击中敌人数叠层、火弱点多 1 层、第 2 回合起每回合 −3 层；三月七 6 魂的持续治疗在护盾破了以后停止（默认开）。对已有配置：彦卿【智剑连心】比原来消失得早（受击就没）；艾丝妲的攻击力加成变成随回合衰减。</li>''',
'''2026-11-11：消灭 / 击破 / 救人 —— tv 85（tools/fix85.py）。新：效果字段 fps / scp / hsk / dx、负数 sx、触发 ekill、ec.brk；teamFire 过滤函数多一个参数 u；fatalOf 记录救人者。
  未改 / 存疑：万敌被救时的回复按“退出【血仇】后的生命上限”换算（×2/3，【血仇】生命上限 +50% 才对）；白厄被救后立即最后一击、罗刹 2 魂护盾、白露岐黄精义（过量治疗）还没做；艾丝妲火弱点那 1 层按主目标；寒鸦【承负】按挂在主目标''')

s = open(sys.argv[1], encoding='utf-8').read()
open(sys.argv[1], 'w', encoding='utf-8').write(s)
