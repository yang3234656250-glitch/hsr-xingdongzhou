"""底层优化第 2 轮（不改数据格式和模拟结果）。用法：python3 tools/opt2.py index.html
① 角色卡里光锥 / 遗器 / 敌人模板的隐藏下拉只放“（无）”和当前选中的那一项（原来每张卡都带全部 172 个光锥、64 套遗器、471 个敌人的 <option>，
   一共两千多个节点，每次重画左栏都要重新生成和解析）；真正的选择界面是自定义的弹出列表，选中时把那一项补进下拉再触发 change，行为不变。
② 手机（≤920px）上“行动轴 / 表格 / 设置”一次只显示一块：看不见的行动轴 / 表格先不画，切过去（或窗口变宽）时用上次的模拟结果补画。
"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)
# ① 隐藏下拉
i0 = s.index('  const lcOptions = sel => {'); i1 = s.index('\n\n', i0)
assert 'relicOptions' in s[i0:i1] and s[i0:i1].count('\n') < 12
s = s[:i0] + '''  // 光锥 / 遗器 / 敌人模板的隐藏下拉：只是自定义选择列表（openPop）背后存值用的，放“（无）”和当前这一项就够（选别的时由 openPop 补上那一项）
  const oneOpt = (v, label, ok) => `<option value="">（无）</option>` + (ok ? `<option value="${v}" selected>${esc(label)}</option>` : "");
  const lcOptions = sel => { const c = DB.lcs.find(x => x.id === sel); return oneOpt(sel, c ? "★".repeat(c.rar) + " " + c.name : "", !!c); };
  const relicOptions = (sel, planar) => { const r = DB.relics.find(x => x.id === sel && x.planar === planar); return oneOpt(sel, r ? r.name : "", !!r); };''' + s[i1:]
a = '''<option value="">（无）</option>${MON.m.map((m, k) => `<option value="${k}"${m.n === u.mon ? " selected" : ""}>${esc(m.n)}</option>`).join("")}</select>'''
rep(a, '''${(k => oneOpt(k, k >= 0 ? MON.m[k].n : "", k >= 0))(MON.m.findIndex(m => m.n === u.mon))}</select>''')
rep('      sel.value = it.dataset.v; closePop(); sel.dispatchEvent(new Event("change", { bubbles: true }));',
    '      const v = it.dataset.v; if (v !== "" && !Array.from(sel.options).some(o => o.value === v)) sel.add(new Option((it.querySelector("span") || it).textContent, v));   // 下拉里平时只有当前这一项，选别的先补上\n      sel.value = v; closePop(); sel.dispatchEvent(new Event("change", { bubbles: true }));')
# ② 手机上看不见的那块先不画
rep('''    R_REF = R;
    renderTimeline(R);
    renderSummary(R);
    renderOrder(R);
''', '''    R_REF = R;
    paint.tl = paint.tab = true; paint();   // 行动轴、两张表（手机上看不见的那块等切过去再画）
''')
rep('''  function update() {
    if (updDefer) { updateSoon(); return; }''', '''  // 手机（≤920px）上“行动轴 / 表格 / 设置”一次只显示一块（body[data-mt]）：看不见的行动轴 / 表格先记成“待画”，切标签或窗口变宽时用上次的模拟结果补画。桌面上三块都在，照旧每次都画
  function paneOn(k) { const narrow = window.matchMedia && window.matchMedia("(max-width: 920px)").matches; return !narrow || document.body.dataset.mt === k; }
  function paint() {
    const R = R_REF; if (!R) return;
    if (paint.tl && paneOn("tl")) { paint.tl = false; renderTimeline(R); }
    if (paint.tab && paneOn("tab")) { paint.tab = false; renderSummary(R); renderOrder(R); }
  }
  if (window.matchMedia) { const mq = window.matchMedia("(max-width: 920px)"); if (mq.addEventListener) mq.addEventListener("change", paint); else if (mq.addListener) mq.addListener(paint); }
  function update() {
    if (updDefer) { updateSoon(); return; }''')
rep('''  $("mtabs").addEventListener("click", e => { const b = e.target.closest("[data-mt]"); if (b) { setMt(b.dataset.mt); window.scrollTo(0, 0); } });''',
    '''  $("mtabs").addEventListener("click", e => { const b = e.target.closest("[data-mt]"); if (b) { setMt(b.dataset.mt); paint(); window.scrollTo(0, 0); } });''')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
