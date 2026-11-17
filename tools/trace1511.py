# 星神★阿哈的行迹面板数据（可重复运行；并入 tv 144）
# 用户：“啊哈的3个行迹好像没做”——三条额外能力在模拟里都有（盒中蕴藏的世界：开局提前 30% + 速度门槛欢愉度；
# 戏中人的异想国：受到队友治疗 / 护盾 +1 愿力；愚弄众神的玩笑：追加攻击 +1 战技点、额外 20% 欢愉伤害），
# 但 TRACE 表里没有 1511，行迹面板里看不到额外能力和属性强化；戏中人的异想国那条效果的说明也没带行迹名，点节点筛不出来。
# 用法：python3 tools/trace1511.py <Mar-7th StarRailRes index_new/cn/character_skill_trees.json>
import json, re, sys
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

trees = json.load(open(sys.argv[1], encoding='utf8'))
def fmt(v):
    t = ('%.1f' % v).rstrip('0').rstrip('.')
    return t
def sub(desc, ps):
    desc = re.sub(r'<[^>]+>', '', desc)
    def f(m):
        v = ps[int(m.group(1)) - 1]; pct = m.group(3) == '%'
        return (fmt(v * 100) + '%') if pct else fmt(v)
    return re.sub(r'#(\d+)\[(i|f\d)\](%?)', f, desc)
STAT = {'CriticalDamageBase': '暴击伤害强化', 'CriticalChanceBase': '暴击率强化', 'SpeedDelta': '速度强化', 'ElationDamageAddedRatioBase': '欢愉度强化'}
cid = '1511'
pts = {k: v for k, v in trees.items() if k.startswith(cid)}
k = [["普攻", pts[cid + '001']['max_level']], ["战技", pts[cid + '002']['max_level']], ["终结技", pts[cid + '003']['max_level']], ["天赋", pts[cid + '004']['max_level']], ["秘技", pts[cid + '007']['max_level']]]
m = [[pts[cid + x]['name'], sub(pts[cid + x]['desc'], pts[cid + x]['params'][0])] for x in ('101', '102', '103')]
st = []
for x in range(201, 211):
    pr = pts[cid + str(x)]['levels'][0]['properties'][0]
    st.append([STAT[pr['type']], '+' + (fmt(pr['value']) if pr['type'] == 'SpeedDelta' else fmt(pr['value'] * 100) + '%')])
st.append(["欢愉技", ""])
ent = {"k": k, "m": m, "s": st}
print(json.dumps(ent, ensure_ascii=False))

i = s.index('  const TRACE = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
body = line[len('  const TRACE = '):].rstrip('\r').rstrip(';')
T = json.loads(body)
T[cid] = ent
s = s[:i] + '  const TRACE = ' + json.dumps(T, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]

# 戏中人的异想国：说明带上行迹名（点行迹节点时能筛出来）
O2 = '愿力：受到队友治疗或护盾 +1（每次开大后可再触发一次）'
N2 = '行迹戏中人的异想国：受到队友提供的治疗或护盾时 +1 愿力（最多 1 次，施放终结技后重置）'
i = s.index('const DB = '); j = s.index('\n', i); line = s[i:j]; tail = '\r' if line.endswith('\r') else ''
db = json.loads(line[len('const DB = '):].rstrip().rstrip(';'))
hit = 0
for c in db['chars']:
    if str(c['id']) == cid:
        for e in c['eff']:
            if e.get('n') == O2: e['n'] = N2; hit += 1
assert hit or N2 in line
s = s[:i] + 'const DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';' + tail + s[j:]
rep('    for (const u of s.units) { if (u.kind !== "ally" || u.sm) continue;\n',
    '    for (const u of s.units) { if (u.kind !== "ally" || u.sm) continue;\n'
    '      for (const e of u.effects || []) if (e.note === ' + json.dumps(O2, ensure_ascii=False) + ') e.note = ' + json.dumps(N2, ensure_ascii=False) + ';   // 阿哈戏中人的异想国：说明带上行迹名\n')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-17：tv 144 补（tools/trace1511.py）</b>。星神★阿哈的行迹面板：以前行迹表里没有阿哈，点“迹”看不到三条额外能力和属性强化（模拟里这三条一直都在算：盒中蕴藏的世界开局提前 30% 和速度门槛欢愉度、戏中人的异想国受到队友治疗 / 护盾 +1 愿力、愚弄众神的玩笑追加攻击 +1 战技点和额外 20% 欢愉伤害）。现在按官方行迹数据补上；戏中人的异想国那条效果的说明带上行迹名，卡片上的旧说明迁移时换掉（开关不变）。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
