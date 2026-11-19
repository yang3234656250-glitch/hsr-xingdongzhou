"""敌人第 1 批（tv 149）第 2 部分：标签是「妨害」、原文写“对我方全体（目标）造成……伤害”的敌人技能打我方全体。
用法：python3 -I tools/mon149b.py index.html
MON.sk 新字段 ha = 1：按群攻选目标（没有 = 旧行为，按标签）。依据官方 MonsterSkillConfig 的 SkillDesc：
  点数喷泉 803401003、收益抽成 803401203、极乐螺旋 502202004、儆惧 201301002 / 201301302、原初的圣餐 503301004。
页面里的敌人技能用标签决定打谁（单攻 / 妨害打一个），这 5 招以前只打一个人。
"""
import sys, json, re
P = sys.argv[1]
raw = open(P, encoding='utf-8', newline='').read(); crlf = '\r\n' in raw[:200000]; s = raw.replace('\r\n', '\n')
assert 'if (s.tv >= 149) return;' in s
m = re.search(r'\n(\s*)const MON ?= ?(\{.*?\});\n', s); MON = json.loads(m.group(2))
pat = re.compile(r'^(提高【惩戒度】等级，并)?对我方全体(目标)?造成')
hit = []
for i, k in enumerate(MON['sk']):
    if k['t'] == '妨害' and pat.search(k['d']):
        assert 'ha' not in k; k['ha'] = 1; hit.append((i, k['n']))
assert sorted({n for i, n in hit}) == sorted(['点数喷泉', '收益抽成', '极乐螺旋', '儆惧', '原初的圣餐']), hit
s = s[:m.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[m.end(2):]
def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:80], s.count(x)); s = s.replace(x, y)
rep('if (HITALL.includes(sk.t) || aw === "all") tgs = HIT1.concat(HIT3, HITALL).includes(sk.t) ? pool : [];',
    'if (HITALL.includes(sk.t) || sk.ha || aw === "all") tgs = HIT1.concat(HIT3, HITALL).includes(sk.t) ? pool : [];   // sk.ha：标签是妨害、原文是“对我方全体造成伤害”（tv 149）')
rep('tg === main || !main || HITALL.includes(sk.t) ? num(xr[0]) : num(xr[1])', 'tg === main || !main || HITALL.includes(sk.t) || sk.ha ? num(xr[0]) : num(xr[1])')
old = '已经放上去、速度没手改过的这几种敌人卡跟着改（tv 149 迁移）。没用到这几种敌人的配置行动顺序不变。</li>'
rep(old, '已经放上去、速度没手改过的这几种敌人卡跟着改（tv 149 迁移）。④ <b>标签是「妨害」、原文写“对我方全体造成伤害”的 5 招改成打我方全体</b>（以前按标签只打一个人）：点数喷泉（「石心十人」诡弈砂金）、收益抽成（孤注一掷的掷骰者）、极乐螺旋（乐变化天人）、儆惧（边塞诗人、金人司阍）、原初的圣餐（渊兽原体）——被打的每个角色都受击回能、触发“受到攻击时”和卡片上填的推条 / 减速。没用到这些敌人的配置行动顺序不变。</li>')
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('ha', hit)
