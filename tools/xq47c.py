# 用户说明：【谐星荟萃】行动时，四个喜剧学家都活着就每人打我方一个不同的角色（每个人都挨一下）。少于 4 个时怎么挑用户也不清楚，
# 先按同样的规则：第 k 个出手的打我方第 k 个在场角色（按队伍顺序）。嘲讽照旧优先。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
rep('aw = tz ? tz.id : actor.atkWho;   // 嘲讽：单体 / 扩散攻击改打施加嘲讽的角色\n',
    'aw = tz ? tz.id : actor.xqK != null && pool.length ? pool[actor.xqK % pool.length].id : actor.atkWho;   // 嘲讽：单体 / 扩散攻击改打施加嘲讽的角色；【谐星荟萃】里第 k 个出手的打第 k 个角色（每人挨一下）\n')
rep('al.forEach((z, i) => { z.xqGo = true; z.dist = 0; z.zpre = t + i * 1e-9; });',
    'al.forEach((z, i) => { z.xqGo = true; z.xqK = i; z.dist = 0; z.zpre = t + i * 1e-9; });')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/xq47c.py）</b>。【谐星荟萃】里喜剧学家<b>每人打我方一个不同的角色</b>（你说的：四个都活着时每个人都挨一下）：第 k 个出手的打队伍里第 k 个在场角色。少于 4 个时先同样按顺序打前几个（你也不确定，等确认）。被嘲讽时照旧打嘲讽的人。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
