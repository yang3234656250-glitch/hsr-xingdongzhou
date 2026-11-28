"""敌人第 9 批（2026-11-27 晚，每日敌人任务，没改 tv：只加 MON.sk 的新字段和引擎里“没有就是旧行为”的分支，敌人卡不用迁移）。
用法：python3 -I tools/enemy9.py index.html <更新日志 li 文件>

B1. 锁定单体 → 下次行动的点名招式打被锁定的角色（新字段 MON.sk[].lk = 点名招式的名字）。
    原文（TextMapCHS，技能描述原样）：
      灭世纪的预兆「锁定我方单体，下次行动对该目标施放【裂魂寒流】。」（可可利亚，虚妄之母 / （幻象）/ （历战余响）/ 无望冽风的幻灭者•虚妄之母）
      BHF-轰炎推进「对指定我方单体造成少量火属性伤害，并锁定目标，下次行动对其施放【DHGDR-流火飞烬】。」（「星核猎手」萨姆（完整））
      开牌下注「……并锁定我方单体，下次行动对其施放【孤注一掷】。……」（孤注一掷的掷骰者；孤注一掷「对锁定的我方单体造成……」）
      目标锁定「锁定指定我方单体，下次行动对其施放【砍伐指令】。」（「机械格斗流」尊者、齿狼系列等）
      点亮未来「锁定1个我方目标，进入【点亮未来】状态，下次行动施放【赞美艾格勒】。」（正阳狮鹫；赞美艾格勒「对锁定目标及其相邻目标造成……」）
      螺旋的弓矢「锁定我方单体，下次行动对该目标施放【强弩的终结】。」（虚卒•践踏者）
      剑气凝「锁定我方单体，两回合后对其施放【风归云动，天河泻梦】。」（彦卿师父 / 云骑骁卫•彦卿；出招表里点名招就排在下一次，“两回合后”没模拟）
    以前：锁定招不打人，下一招按“轮流”选到的是下一个角色，不是被锁定的那个。
    现在：锁定招施放时记下这次选到的角色（u.lkT），这个敌人下一次行动如果施放的就是点名招式，打这个角色（还在场时）；
          下一次行动不管放什么都清掉锁定。被嘲讽、【谐星荟萃】、敌人卡“攻击：全体”时照旧（不按锁定）。
    没做（原文锁 2 个 / 全体或由别的敌人施放，等用户确认）：瞄准指令 / 协力指令「锁定2个我方目标」、两倍上弦月「锁定2个我方目标」→ 六倍满月、
          亿年苦厄燃放「锁定2个我方目标」→ 反造物主【灵的囚笼必遭焚毁】、亵渎的咒诅 / 痴愚的求索（被囚禁的秘所思 / 被操弄的逻各斯锁定，反造物主施放）、
          劫数将至（幻胧锁定，破灭玄莲施放）、使者带锁链（蓄力期间攻击它的角色也被锁定）、罪血眈视（“数个回合内”）。
B2. 冰锋（幻象）【冰冷凝视】/ 无尽寒冬之槊（幻象）【冷酷追击】「锁定一个目标，【可可利亚（幻象）】/【可可利亚，虚妄之母（幻象）】的部分技能会对被锁定的目标
    额外追加释放一次，持续直到冰锋（幻象）/ 无尽寒冬之槊（幻象）被弱点击破或击杀。」+ 首领技能「该技能会对【冰锋（幻象）】/【无尽寒冬之槊（幻象）】锁定的目标追加释放。」
    新字段 MON.sk[].flk（锁定招：记下这次选到的角色 u.flT）、MON.sk[].fl（首领技能：模板名 = fl、还在场、没被弱点击破过的敌人锁定的角色再挨一次这招：
    受击回能、受到攻击时、行动延后 / 减速（敌人卡这招的 skx）都再结算一次）。被弱点击破（doBreak）就清掉 flT。
（2026-11-27 晚推不上仓库时，按项目文档「敌人任务-2026-11-27-敌人第9批-未推送补丁.md」重做。2026-11-28 每日校对按该文档转录进仓库，index.html 取自 claude.ai 页面第 330 版。）
"""
import sys, json, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import page, grab

P, LOGF = sys.argv[1], sys.argv[2]
s, crlf = page(P)
assert 'enemy9' not in s, '已经跑过'
mM = grab(s, 'MON', r'\{'); MON = json.loads(mM.group(2))
SK = MON['sk']

# ---- B1：lk ----
LK = {   # 技能名: (原文里锁定的写法, 点名招式)
    '灭世纪的预兆': ('锁定我方单体，下次行动对该目标施放【裂魂寒流】', '裂魂寒流'),
    'BHF-轰炎推进': ('并锁定目标，下次行动对其施放【DHGDR-流火飞烬】', 'DHGDR-流火飞烬'),
    '开牌下注': ('并锁定我方单体，下次行动对其施放【孤注一掷】', '孤注一掷'),
    '目标锁定': ('锁定指定我方单体，下次行动对其施放【砍伐指令】', '砍伐指令'),
    '点亮未来': ('锁定1个我方目标，进入【点亮未来】状态，下次行动施放【赞美艾格勒】', '赞美艾格勒'),
    '螺旋的弓矢': ('锁定我方单体，下次行动对该目标施放【强弩的终结】', '强弩的终结'),
    '剑气凝': ('锁定我方单体，两回合后对其施放【风归云动，天河泻梦】', '风归云动，天河泻梦'),
}
users = {}
for m in MON['m']:
    for i in m.get('k', []): users.setdefault(i, []).append(m)
lk = []
for i, k in enumerate(SK):
    if k['n'] not in LK or i not in users: continue
    pat, f = LK[k['n']]
    if pat not in k['d']: continue   # 点亮未来 有一个版本是“锁定我方全体目标”（狮震八方），不改
    assert 'lk' not in k
    for m in users[i]:   # 同一个敌人身上要有点名招式，且它是打单体 / 扩散的（打被锁定的人才有意义）
        fs = [j for j in m['k'] if SK[j]['n'] == f]
        assert fs, (m['n'], f)
        for j in fs: assert (SK[j].get('ht') or SK[j]['t']) in ('单攻', '妨害', '扩散'), (m['n'], SK[j])
    k['lk'] = f; lk.append(i)
assert sorted({SK[i]['n'] for i in lk}) == sorted(LK), [SK[i]['n'] for i in lk]
skipped = [(i, k['n'], k['d'][:30]) for i, k in enumerate(SK) if k['n'] in LK and i in users and i not in lk]
assert [x[1] for x in skipped] == ['BHF-轰炎推进', '点亮未来'] and '锁定' not in SK[skipped[0][0]]['d'] and '锁定我方全体目标' in SK[skipped[1][0]]['d'], skipped   # 萨姆（非完整）的轰炎推进没有锁定

# ---- B2：flk / fl ----
FLK = {'冰冷凝视': '冰锋（幻象）', '冷酷追击': '无尽寒冬之槊（幻象）'}
flk = []
for i, k in enumerate(SK):
    if k['n'] in FLK and i in users:
        assert k['d'].startswith('锁定一个目标，') and '额外追加释放一次' in k['d'], k
        k['flk'] = 1; flk.append(i)
        assert any(m['n'] == FLK[k['n']] for m in users[i]), (k['n'], [m['n'] for m in users[i]])
fl = []
for i, k in enumerate(SK):
    mm = re.search(r'该技能会对【([^】]+)】锁定的目标追加释放', k['d'])
    if not mm or i not in users: continue
    assert mm.group(1) in FLK.values(), mm.group(1)
    assert (k.get('ht') or k['t']) in ('单攻', '妨害'), k
    k['fl'] = mm.group(1); fl.append(i)
assert len(flk) == 2 and len(fl) == 3, (flk, fl, [SK[i]['n'] for i in fl])

s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]

# ---- 引擎 ----
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

rep('        const main = aw === "all" ? null : aw === "rot" ? pool[(actor.turns - 1) % Math.max(1, pool.length)] : pool.find(x => x.id === aw);',
    '        let main = aw === "all" ? null : aw === "rot" ? pool[(actor.turns - 1) % Math.max(1, pool.length)] : pool.find(x => x.id === aw);')
a = '          const skI = ovK != null && MON.sk[+ovK] ? +ovK : skN, sk = MON.sk[skI];\n'
rep(a, a + '          if (actor.lkT) { const L = actor.lkT, z = !tz && actor.xqK == null && aw !== "all" && sk.n === L.n ? pool.find(x => x.id === L.id) : null; actor.lkT = null; if (z) { main = z; addLog(`${actor.name}【${sk.n}】打上次锁定的 ${z.name}`, false, "var(--enemy)"); } }   // MON.sk.lk：锁定的目标只管下一次行动（敌人第 9 批 tools/enemy9.py）\n')
a = '          if (sk.ctr != null && MON.sk[sk.ctr]) { actor.ctr = { k: sk.ctr, n: sk.ctn != null ? num(sk.ctn) : null }; marks.push({ t, uid: actor.id, label: "反击状态", color: "var(--enemy)", from: "" }); }   // MON.sk.ctr：以牙还牙（敌人第 4 批）\n'
rep(a, a +
    '          if ((sk.lk || sk.flk) && main && aw !== "all") { if (sk.lk) actor.lkT = { id: main.id, n: sk.lk }; if (sk.flk) actor.flT = main.id; addLog(`${actor.name}【${sk.n}】：锁定 ${main.name}${sk.lk ? `，下次行动的【${sk.lk}】打这个目标` : "（首领的部分技能会对他追加释放）"}`, false, "var(--enemy)"); }   // MON.sk.lk / flk：锁定单体（敌人第 9 批）\n'
    '          if (sk.fl) for (const z of U) { if (z.kind !== "enemy" || z.gone || !z.flT || String(z.mon || "") !== sk.fl) continue; const tg = pool.find(x => x.id === z.flT); if (!tg) continue;   // MON.sk.fl：对【冰锋（幻象）】这类锁定的目标追加释放一次（敌人第 9 批）\n'
    '            addLog(`${actor.name}【${sk.n}】：对 ${z.name} 锁定的 ${tg.name} 追加释放一次`, false, "var(--enemy)");\n'
    '            batchFx(() => apply({ id: actor.id + "-hit", type: "hit", target: tg.id, value: num(sk.sp), dmg: dmgTo(tg) }, actor, actor.color)); enemyDebuff(actor, [tg], (actor.skx || {})[skIdx], "sk" + skIdx); }\n')
rep('    const doBreak = (en, o, el, mx) => {\n      en.tcur = 0; en.broken = true;\n',
    '    const doBreak = (en, o, el, mx) => {\n      en.tcur = 0; en.broken = true; en.flT = null;   // 冰锋（幻象）这类被弱点击破：锁定解除（敌人第 9 批）\n')

log = open(LOGF, encoding='utf-8').read().strip()
ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('lk', [(i, SK[i]['n'], SK[i]['lk'], [m['n'] for m in users[i]]) for i in lk])
print('flk', [(i, SK[i]['n']) for i in flk]); print('fl', [(i, SK[i]['n'], SK[i]['fl'], [m['n'] for m in users[i]]) for i in fl])
