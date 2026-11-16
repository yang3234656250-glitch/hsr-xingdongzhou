# 4.7 异相仲裁「王棋」隐藏关卡的归寂：加成单独一组关卡敌人（可重复运行）
import json, sys
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
i = s.index('const STG = '); j = s.index('\n', i)
line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
body = line[len('const STG = '):].rstrip().rstrip(';')
stg = json.loads(body)
NAME = '异相仲裁·4.7 王棋（隐藏关卡）归寂'
# 官方：ChallengePeak 1104 → 关卡 30511021（普通，Lv.100，HardLevelGroup 3），怪物 801503006（归寂）
# 基础生命 14880 × HPRatio 484.69086 × HPModify 0.375 = 2704575；三条血 = ×6.2 / ×6.2 / ×11.78，贪婪（污染4级）= ×2.48
phs = '16768365,16768365,31859894,6707346'
# 喜剧学家（MonsterID 801204002，HardLevelGroup 3 Lv.100 生命 247919 × 关卡倍率 6.2 = 1537100；nanoka 贪饕 +614840 = 40%）开场 4 只；被消灭后【粉墨登场】再召唤没做
cm = {'n': '喜剧学家', 'i': 312, 's': 167.0, 'lv': 100, 'ehp': 1537100}
grp = {'g': NAME, 'f': [{'f': 1, 'h': [[[{'n': '万色返空主，归寂', 'i': 5, 's': 140.0, 'lv': 100, 'phs': phs}, cm, cm, cm, cm]]]}]}   # 归寂排第一 = 主目标
stg = [x for x in stg if x['g'] != NAME] + [grp]
new = 'const STG = ' + json.dumps(stg, ensure_ascii=False, separators=(',', ':')) + ';' + tail
s = s[:i] + new + s[j:]
def rep(a, b):
    global s
    if b in s: return
    assert s.count(a) == 1, a
    s = s.replace(a, b)
old = 'u.monS = m.s; u.lv = m.lv; u.spd = u.base = monSpeed(u); u.name = m.n;'
new = old + ' if (m.phs) u.phs = m.phs; if (m.ehp) u.ehp = m.ehp;'
if new not in s:
    s = s.replace(old + ' if (m.phs) u.phs = m.phs;', old)
    assert s.count(old) == 1; s = s.replace(old, new)
rep('`${m.n}（速度 ${fmt(m.s * monRatio(m.lv))}，${m.lv} 级）`).join("、")',
    '`${m.n}（速度 ${fmt(m.s * monRatio(m.lv))}，${m.lv} 级${m.phs ? "，分阶段生命值 " + m.phs.split(",").join(" / ") + "（最后一条是贪婪）" : ""}）`).join("、")')
open(p, 'w', encoding='utf8', newline='').write(s)
