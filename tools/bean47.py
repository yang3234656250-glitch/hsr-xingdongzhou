# 银狼每次强普的【怪怪怪味豆】个数可以逐次填：S.sw.beanL = "2,1,1,…"（按强普先后，逗号分隔；没填到的用“每次强普怪味豆”）。
# 依据：4.7 王棋录像 下 3:48 / 4:03 两次强普隐藏分 160 → 166 → 169（第一次 2 个、第二次 1 个，用户确认）。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
rep('    const beanP = rec => { const n = num(W.bean, 1); if (n > 0 && rec && rec.act === "ebasic") addPunch(3 * n, "怪味豆"); };',
    '    let beanI = 0; const beanL = String(W.beanL || "").split(/[,，\\s]+/).filter(x => x !== "");   // 逐次填的怪味豆个数（按强普先后）\n'
    '    const beanP = rec => { if (!(rec && rec.act === "ebasic")) return; const n = beanI < beanL.length ? num(beanL[beanI]) : num(W.bean, 1); beanI++; if (n > 0) addPunch(3 * n, n > 1 ? `怪味豆 ×${n}` : "怪味豆"); };')
rep('S.sw[k] = el.type === "checkbox" ? el.checked : k === "uid" || k === "e2when" ? el.value : num(el.value);',
    'S.sw[k] = el.type === "checkbox" ? el.checked : k === "uid" || k === "e2when" || k === "beanL" ? el.value : num(el.value);')
rep('''style="width:50px"> 个（各 +3 笑点）</label>\n''',
    '''style="width:50px"> 个（各 +3 笑点）</label>\n        <label for="s-beanL" title="按强普先后逐次填怪味豆个数，逗号分隔（例：2,1,1）；没填到的按上面的个数">逐次 <input type="text" id="s-beanL" value="${esc(String(W.beanL ?? ""))}" data-s="beanL" placeholder="如 2,1,1" style="width:90px"></label>\n''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/bean47.py）</b>。银狼设置里“每次强普怪味豆”旁边多了<b>逐次</b>：按强普的先后逐次填个数（逗号分隔，例 2,1,1），没填到的照旧按上面的个数。依据：4.7 王棋录像里两次强普隐藏分 160 → 166 → 169，第一次出了 2 个。没填时和以前一样。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
