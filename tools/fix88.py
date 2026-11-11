"""tv 88：伤害显示里漏算的部分。
用法：python3 tools/fix88.py index.html <官方 json 目录>
- 额外伤害（XR）新的属性来源 st："sk" = 施放者战技最新的目标（丹恒•腾荒的【同袍】），"tid:XXXX" = 队里这个角色（Archer / Saber）；
  暴击、增伤按那个角色的卡片。
- 丹恒•腾荒：强化【龙灵】追加攻击里【同袍】80% 攻击力的附加伤害、行迹峥嵘对生命值最高的敌人 40%、2 魂 ×2、6 魂终结技时【同袍】对敌方全体 330%。
- 远坂凛连携里 Archer 300%（天赋 12 级 330%）、吉尔伽美什连携里 Saber 600%（660%）。
- 托帕【涨幅惊人！】：账账伤害倍率 +150%（12 级 165%）、暴击伤害 +25%，到账账攻击 2 次（6 魂 3 次）用完为止（原来按 2 回合）。
- 那刻夏战技：场上每有 1 个敌人伤害 +20%（伤害增益条件 ec.enN：按场上还在的敌人数倍乘）。
- 花火 6 魂：战技 / 终结技时战技的暴伤增益扩散给持有【谜诡】的队友（新状态【谜诡】）。"""
import sys, json, re
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 88, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

# ================= 引擎 =================
F.rep('''          const st = r.st || "atk";
          const sv = st === "aatk" ? pick(u, "atk") : st === "hatk" ? pick(allies.find(x => x !== o) || o, "atk") : st === "mult" ? pick(o, e.stat) * e.v : pick(o, st);
          const self = o === u || st === "aatk";
          let crit = self ? c.critM : 1 + Math.min(1, num(o.cr, 5) / 100) * num(o.cd, 50) / 100;''', '''          const st = r.st || "atk";
          const by = st === "sk" ? skPickAt(o, rec) : st.startsWith("tid:") ? allies.find(x => tidOf(x) === st.slice(4)) : null;   // 伤害来自别的角色：同袍 / Archer / Saber
          if ((st === "sk" || st.startsWith("tid:")) && !by) continue;
          const sv = by ? pick(by, "atk") : st === "aatk" ? pick(u, "atk") : st === "hatk" ? pick(allies.find(x => x !== o) || o, "atk") : st === "mult" ? pick(o, e.stat) * e.v : pick(o, st);
          const self = by ? by === u : o === u || st === "aatk", cw = by || o;
          let crit = self ? c.critM : 1 + Math.min(1, num(cw.cr, 5) / 100) * num(cw.cd, 50) / 100;''')
F.rep('''          const dm = self ? c.dmgM : 1 + num(o.dmg, 0) / 100;''', '''          const dm = self ? c.dmgM : 1 + num(cw.dmg, 0) / 100;''')
F.rep('''        if (amt > 0) parts.push({ n: (o === u ? "" : o.name + " ") + r.n.split("：")[0], amt, tr: r.kind === "true" });''',
      '''        if (amt > 0) parts.push({ n: (o === u ? "" : o.name + " ") + r.n.split("：")[0], amt, tr: r.kind === "true" });''')
F.rep('''  const pickAt = (o, rec) => {''', '''  const skPickAt = (o, rec) => { const n = (R_REF ? R_REF.skMarks || [] : []).filter(m => m.uid === o.id && m.t <= num(rec && rec.t) + 1e-9).length; const id = skPickTarget(o, Math.max(1, n), S.units); return S.units.find(x => x.id === id && x.kind === "ally") || null; };   // 这次行动时施放者战技最新的目标
  const pickAt = (o, rec) => {''')
F.rep('''      if (c.pcd != null && num(u.cd, 50) < num(c.pcd) - 1e-9) return 0;''', '''      if (c.pcd != null && num(u.cd, 50) < num(c.pcd) - 1e-9) return 0;
      if (c.enN != null) { const n = U.filter(z => z.kind === "enemy" && !z.gone).length || 1; f0 *= Math.min(num(c.enN), n); }   // 按场上敌人数（没放敌人卡按 1 个）''')
F.rep('''    if (c.pcd != null) L.push(`暴击伤害 ≥${c.pcd}% 时`);''', '''    if (c.pcd != null) L.push(`暴击伤害 ≥${c.pcd}% 时`);
    if (c.enN != null) L.push(`按场上敌人数（最多 ${c.enN} 个）`);''')

# ================= 额外伤害表 =================
XR = F.XR   # finish() 会把 F.XR 写回页面
has('141403', '对敌方全体造成等同于丹恒•腾荒#2[i]%攻击力的物理属性伤害和等同于【同袍】#8[f1]%攻击力的相应属性附加伤害')
p10, p12 = prm('141403', 10), prm('141403', 12); assert r4(p10[7]) == 0.8 and r4(p12[7]) == 0.88
hast(1414, '峥嵘', '强化【龙灵】行动时，额外对当前生命值最高的敌方单体造成1次等同于【同袍】#1[i]%攻击力的相应属性附加伤害')
has('r:141402', '强化【龙灵】行动时，【同袍】造成的附加伤害为原伤害的200%'); has('r:141406', '丹恒•腾荒施放终结技时，【同袍】会对敌方全体造成等同于【同袍】330%攻击力的相应属性附加伤害')
XR['1414'] = [
    {"k": "tp", "n": "终结技：强化【龙灵】的追加攻击里【同袍】对敌方全体造成同袍 80% 攻击力的附加伤害（12 级 88%；2 魂 ×2；暴击、增伤按同袍的卡片）", "on": ["f"], "st": "sk", "v": [0.8, 0.88], "lk": "u", "cnt": "N", "e2x": 2},
    {"k": "zr", "n": "行迹峥嵘：强化【龙灵】行动时对生命值最高的敌人再造成 1 次同袍 40% 攻击力的附加伤害（2 魂 ×2）", "on": ["f"], "st": "sk", "v": [0.4], "e2x": 2},
    {"k": "e6", "n": "E6 草木微尘皆入梦中：施放终结技时【同袍】对敌方全体造成同袍 330% 攻击力的附加伤害", "on": ["u"], "st": "sk", "v": [3.3], "cnt": "N", "e": 6}]
has('150805', '远坂凛和Archer对敌方全体发动连携追加攻击，分别造成等同于远坂凛#1[i]%攻击力以及Archer#4[i]%攻击力的量子属性伤害')
assert prm('150805', 10)[3] == 3 and prm('150805', 12)[3] == 3.3
XR.setdefault('1508', []).append({"k": "ar", "n": "天赋自在远坂流：连携追加攻击里 Archer 对敌方全体造成 Archer 300% 攻击力的伤害（12 级 330%；暴击、增伤按 Archer 的卡片；队里没有 Archer 不算）", "on": ["f"], "st": "tid:1015", "v": [3.0, 3.3], "lk": "t", "cnt": "N"})
has('150905', '对敌方全体分别造成等同于吉尔伽美什#1[i]%攻击力的雷属性伤害以及Saber#2[i]%攻击力的风属性伤害')
assert prm('150905', 10)[1] == 6 and prm('150905', 12)[1] == 6.6
XR.setdefault('1509', []).append({"k": "sb", "n": "天赋「本王允许你进攻」：连携追加攻击里 Saber 对敌方全体造成 Saber 600% 攻击力的伤害（12 级 660%；暴击、增伤按 Saber 的卡片；队里没有 Saber 不算）", "on": ["f"], "st": "tid:1014", "v": [6.0, 6.6], "lk": "t", "cnt": "N"})
has('111203', '使账账进入【涨幅惊人！】状态，伤害倍率提高#1[i]%，暴击伤害提高#2[i]%'); assert prm('111203', 10)[0] == 1.5 and prm('111203', 12)[0] == 1.65
XR.setdefault('1112', []).append({"k": "zf", "n": "终结技【涨幅惊人！】：账账的追加攻击伤害倍率 +150%（12 级 165%；到账账攻击 2 次、6 魂 3 次为止）", "on": ["f"], "who": "flag", "flag": "zf", "st": "atk", "v": [1.5, 1.65], "lk": "u"})

def setx(e, **kw):
    for k, v in kw.items():
        if v is None: e.pop(k, None)
        else: e[k] = v
    return e
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]

# ---- 托帕【涨幅惊人！】按账账攻击次数 ----
c = C[1112]; E = c['eff']; z = find(E, '终结技：【涨幅惊人！】账账暴击伤害'); o = z['n']
n = '终结技：【涨幅惊人！】账账暴击伤害 +25%（5 魂 27.5%），到账账攻击 2 次（6 魂 3 次）用完为止'; setx(z, n=n, d=0)
dec = find(E, '终结技：账账每施放 1 次攻击'); i = E.index(dec)
E.insert(E.index(z) + 1, dict(y='dbuf', t='ult', tg='sm:numby', m='rx', sc='zf', v=1, d=0, bk='zfx', n='终结技：【涨幅惊人！】标记（额外伤害里的倍率 +150% 用）'))
i = E.index(dec)
E[i + 1:i + 1] = [dict(y='dbuf', t='atk', aw='sm', tg='sm:numby', m='cd', v=0, d=0, bk='zf', ltc=1, n='终结技：【涨幅惊人！】次数用完时暴伤增益结束'),
                  dict(y='dbuf', t='atk', aw='sm', tg='sm:numby', m='rx', sc='zf', v=0, d=0, bk='zfx', ltc=1, n='终结技：【涨幅惊人！】次数用完时倍率提高结束')]
F.rebuild(1112, E, rename={o: n})

# ---- 那刻夏战技：场上每有 1 个敌人伤害 +20% ----
has('140502', '施放时场上每有1个可攻击的敌方目标，本次战技造成的伤害提高#3[i]%'); assert r4(prm('140502', 10)[2]) == 0.2
c = C[1405]; c['eff'].append(dict(y='dbuf', t='start', tg='self', m='dmg', sc='s', v=20, d=0, bk='fx', ec={'enN': 5}, n='战技：施放时场上每有 1 个敌人，这次战技伤害 +20%'))
c['notes'] = [x.replace('战技“场上每有 1 个可攻击的敌方目标伤害 +20%”、', '') for x in c.get('notes', [])]
F.rebuild(1405, c['eff'])

# ---- 花火 6 魂：暴伤增益扩散给持有【谜诡】的队友 ----
has('130603', '使我方全体获得【谜诡】'); has('r:130606', '花火施放战技时，使战技的暴击伤害提高效果对持有【谜诡】的队友都会生效，花火施放终结技时，若我方单体中有目标持有战技的暴击伤害提高效果，使该效果扩散至持有【谜诡】的队友')
c = C[1306]; E = c['eff']
E.append(dict(y='state', t='ult', tg='self', sn='谜诡', v=1, d=3, ts='src', n='终结技：我方全体获得【谜诡】，持续 3 回合（记在花火身上）'))
F.rebuild(1306, E)
e1 = F.eid(1306, 1); e1['eff'] = [x for x in e1['eff'] if x.get('sn') != '谜诡'] + [dict(y='state', t='ult', tg='self', sn='谜诡', v=1, sx=1, n='E1：【谜诡】持续时间 +1 回合')]
sk, rp = find(E, '【强化版】战技：目标暴击伤害 +花火暴击伤害'), find(E, '【强化版】行迹夜想曲：持有战技暴伤增益')
e6 = F.eid(1306, 6); x6 = find(e6['eff'], 'E6：战技暴伤增益额外'); setx(x6, n='E6：战技暴伤增益额外 +花火暴击伤害的 30%')
sp = []
for tr, cond, w in (('skill', {'ns': '谜诡'}, '施放战技时'), ('ult', {'ns': '梦游鱼', 'so': 'team'}, '施放终结技时（有人持有战技暴伤增益）')):
    sp += [dict(y='state', t=tr, tg='others', sn='梦游鱼', v=1, d=2, ts='src', **cond, n='E6：' + w + '战技的暴伤增益对持有【谜诡】的队友都生效（【梦游鱼】）'),
           dict({k: v for k, v in sk.items() if k not in ('n', 'tg', 't')}, t=tr, tg='others', **cond, n='E6：' + w + '扩散：暴击伤害 +花火暴击伤害的 24% + 45%'),
           dict({k: v for k, v in x6.items() if k not in ('n', 'tg', 't')}, t=tr, tg='others', **cond, n='E6：' + w + '扩散：再 +花火暴击伤害的 30%'),
           dict({k: v for k, v in rp.items() if k not in ('n', 'tg', 't')}, t=tr, tg='others', **cond, n='E6：' + w + '扩散：行迹夜想曲全属性抗性穿透 +10%')]
e6['eff'] = [x for x in e6['eff'] if not x.get('n', '').startswith('E6：施放')] + sp

# ---- 黄泉 6 魂说明 ----
e6 = F.eid(1308, 6); setx(find(e6['eff'], 'E6：终结技伤害全属性抗性穿透'), n='E6：终结技伤害全属性抗性穿透 +20%')

c = C[1414]; c['notes'] = [x for x in c.get('notes', []) if '没算进伤害显示' not in x]; F.touch(1414)
for cid in (1508, 1509):
    C[cid]['notes'] = [x.replace('；连携追加攻击里 Archer 的 300% 攻击力伤害没算', '').replace('；连携追加攻击里 Saber 的 600% 攻击力伤害没算', '') for x in C[cid].get('notes', [])]; F.touch(cid)

F.finish('伤害显示补漏', '''<li><b>2026-11-11（伤害补漏）</b>：tv 88（tools/fix88.py）。伤害里补上原来没算的部分：丹恒•腾荒强化【龙灵】追加攻击里【同袍】80% 攻击力的附加伤害、峥嵘对生命值最高的敌人 40%、2 魂两者 ×2、6 魂终结技时【同袍】对敌方全体 330%（暴击、增伤按【同袍】的卡片）；远坂凛连携里 Archer 的 300%、吉尔伽美什连携里 Saber 的 600%（队里有对应角色时）；托帕【涨幅惊人！】账账伤害倍率 +150%，暴伤增益改成到账账攻击 2 次（6 魂 3 次）为止；那刻夏战技按场上敌人数 +20% / 个；花火 6 魂战技 / 终结技时暴伤增益扩散给持有【谜诡】的队友。对已有配置：这些角色的伤害会变高。</li>''',
'''2026-11-11：伤害补漏 —— tv 88（tools/fix88.py）。新：XR st "sk" / "tid:XXXX"、skPickAt、ec.enN、花火状态【谜诡】。
  未改 / 存疑：【同袍】附加伤害用同袍卡片的暴击 / 增伤（不含同袍身上的增益），丹恒•腾荒 6 魂无视防御对附加伤害没算；Archer / Saber 那段用他们卡片的暴击 / 增伤；不死途消耗【婪酣】的额外伤害、姬子•启行同行协议的额外助战技 / 列车的脉搏额外回合 / 1 魂多 1 次弹射还没做''')
