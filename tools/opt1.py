"""底层优化第 1 轮（不改任何数据格式和模拟结果）。用法：python3 tools/opt1.py index.html
① tplOf 用 Map 索引（原来每次在 99 个角色里线性查找，模拟里每个效果都会查）；② 模拟里 tx / smDef 按单位缓存；
③ 每个单位的效果按触发建索引（fx(u, 触发)），事件分发不再把所有效果扫一遍；④ hpNow 不再 filter + reduce；
⑤ 拖滑块 / 连续输入时把多次重算合并成每帧一次（updateSoon），其余操作仍然立即重算；⑥ 每次重算只 JSON.stringify(S) 一次。
"""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70]); s = s.replace(a, b)
# ① tplOf
rep('  const tplOf = u => DB.chars.find(c => c.id === u.tplId) || DB.chars.find(c => normName(c.name) === normName(u.name));',
    '''  // 索引：按 id、按名字（都取数组里的第一个，和原来的 find 一样）；DB.chars 条数变了就重建
  let TPLIX = null;
  const tplIx = () => {
    if (!TPLIX || TPLIX.n !== DB.chars.length) { const id = new Map(), nm = new Map(); for (const c of DB.chars) { if (!id.has(c.id)) id.set(c.id, c); const k = normName(c.name); if (!nm.has(k)) nm.set(k, c); } TPLIX = { n: DB.chars.length, id, nm }; }
    return TPLIX;
  };
  const tplOf = u => { const X = tplIx(); return X.id.get(u.tplId) || X.nm.get(normName(u.name)); };''')
# ② tx / smDef 缓存（单位的模板在一次模拟里不变）
rep('    const tx = u => ((u && !u.sm && tplOf(u)) || {}).x || {};',
    '    const NOX = {}, txC = new Map();\n    const tx = u => { if (!u || u.sm) return NOX; let x = txC.get(u); if (x === undefined) { x = (tplOf(u) || {}).x || NOX; txC.set(u, x); } return x; };')
rep('    const smDef = u => { const o = u && u.sm && byId[u.sm.owner], T = o && tplOf(o); return (T && (T.sm || []).find(m => m.k === u.sm.key)) || null; };',
    '    const smC = new Map();\n    const smDef = u => { if (!u || !u.sm) return null; let d = smC.get(u); if (d === undefined) { const o = byId[u.sm.owner], T = o && tplOf(o); d = (T && (T.sm || []).find(m => m.k === u.sm.key)) || null; smC.set(u, d); } return d; };')
# ④ hpNow
rep('      return h0 + (u.buffs || []).filter(b => b.kind === "hp").reduce((s, b) => s + b.v, 0);',
    '      let h = h0; const B = u.buffs; if (B) for (let i = 0; i < B.length; i++) if (B[i].kind === "hp") h += B[i].v;\n      return h;')
# ③ 触发索引
rep('    const byId = Object.fromEntries(U.map(u => [u.id, u]));\n    // 召唤物 / 忆灵 / 倒计时',
    '''    const byId = Object.fromEntries(U.map(u => [u.id, u]));
    // 每个单位的效果按触发建索引（顺序和效果列表一致；关闭的不进）。一次模拟里效果列表不会变，事件分发直接取 fx(u, 触发)，等价于原来逐条 trig(e, 触发)
    const NOFX = [];
    const mkTk = u => { const m = new Map(); for (const e of u.effects || []) { if (e.off) continue; const ks = e.or && e.or !== e.trigger && (e.trigger !== "turn" || e.or === "xturn") ? [e.trigger, e.or] : [e.trigger]; for (const k of ks) { let a = m.get(k); if (!a) m.set(k, a = []); a.push(e); } } return m; };
    const tkM = new Map();   // 放在这次模拟自己的 Map 里，不往单位对象上写东西（不会进存档）
    const fx = (u, k) => { let m = tkM.get(u); if (!m) tkM.set(u, m = mkTk(u)); return m.get(k) || NOFX; };
    // 召唤物 / 忆灵 / 倒计时''')
i0 = s.index('  function simulate() {'); i1 = s.index('\n  function ', i0 + 10)
body = s[i0:i1]
b0 = body
body, n1 = re.subn(r'for \(const e of (\w+)\.effects\) if \(trig\(e, ("[A-Za-z0-9]+"|\w+)\)\) apply\(', r'for (const e of fx(\1, \2)) apply(', body)
body, n2 = re.subn(r'for \(const e of (\w+)\.effects\) if \(trig\(e, ("[A-Za-z0-9]+"|\w+)\) && ', r'for (const e of fx(\1, \2)) if (', body)
a = 'for (const e of u.effects) {\n          if (!trig(e, key) || !okWho(e, u, who) || (filt && !filt(e))) continue;'
assert body.count(a) == 1; body = body.replace(a, 'for (const e of fx(u, key)) {\n          if (!okWho(e, u, who) || (filt && !filt(e))) continue;')
a = 'for (const e of u.effects) {\n          if (!trig(e, kind)) continue;\n'
assert body.count(a) == 1; body = body.replace(a, 'for (const e of fx(u, kind)) {\n')
a = 'u.effects.some(e => trig(e, "cntUp"))'; assert body.count(a) == 1; body = body.replace(a, 'fx(u, "cntUp").length')
print('fx replacements', n1, n2, 'trig left in simulate:', body.count('trig('))
s = s[:i0] + body + s[i1:]
# ⑥ stringify 一次
rep('  const save = () => {\n    const s = JSON.stringify(S);', '  const save = s0 => {\n    const s = typeof s0 === "string" ? s0 : JSON.stringify(S);')
rep('''    save();
    const io = $("io"); if (document.activeElement !== io) io.value = JSON.stringify(S);''',
    '''    const sNow = JSON.stringify(S);
    save(sNow);
    const io = $("io"); if (document.activeElement !== io) io.value = sNow;''')
# ⑤ 连续输入合并
rep('  function update() {\n', '''  // 拖滑块 / 连续敲数字时（input 事件）把多次重算合并成每帧一次；其他操作（change、点击、载入）照旧立即重算，并取消还没跑的那次
  let updDefer = false, updRaf = 0, updTo = 0;
  const updClear = () => { if (updRaf) cancelAnimationFrame(updRaf); if (updTo) clearTimeout(updTo); updRaf = updTo = 0; };
  const updFlush = () => { if (updRaf || updTo) { updClear(); update(); } };
  const updateSoon = () => { if (updRaf || updTo) return; updRaf = requestAnimationFrame(updFlush); updTo = setTimeout(updFlush, 80); };   // 标签页在后台时 rAF 不跑，靠定时器兜底
  window.addEventListener("pagehide", updFlush);
  function update() {
    if (updDefer) { updateSoon(); return; }
    updClear();
''')
rep('''  ed.addEventListener("input", e => { const t = e.target; if ((t.dataset.f || t.dataset.a || t.dataset.s) && t.tagName !== "SELECT" && t.type !== "checkbox") onField(t, false); });''',
    '''  ed.addEventListener("input", e => { const t = e.target; if ((t.dataset.f || t.dataset.a || t.dataset.s) && t.tagName !== "SELECT" && t.type !== "checkbox") { updDefer = true; try { onField(t, false); } finally { updDefer = false; } } });''')
rep('''  $("qspd").addEventListener("input", e => { const t = e.target; if (t.dataset.f === "spd") onField(t, false); });''',
    '''  $("qspd").addEventListener("input", e => { const t = e.target; if (t.dataset.f === "spd") { updDefer = true; try { onField(t, false); } finally { updDefer = false; } } });''')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
