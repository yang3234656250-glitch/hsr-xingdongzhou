# 银狼隐藏分够了自动开大（S.sw.auto / S.sw.autoAt；没有就是旧行为），可重复运行
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b):
    global s
    a = a.replace('\n', '\r\n'); b = b.replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep('''        const ready = U.filter(u => !u.gone && !u.domP && hasEnergy(u) && (eCfg(u).autoUlt || (ultQ[u.id] && ultQ[u.id].length)) && u.e >= eCfg(u).maxE - 1e-6);
        if (!ready.length) return;''',
'''        const ready = U.filter(u => !u.gone && !u.domP && hasEnergy(u) && (eCfg(u).autoUlt || (ultQ[u.id] && ultQ[u.id].length)) && u.e >= eCfg(u).maxE - 1e-6);
        const swAt = Math.max(num(W.gate, 60), num(W.autoAt, 60)), swGo = swU && W.auto && !swU.gone && !sw.inUlt && sw.score >= swAt;   // 银狼：隐藏分够了自动开大
        if (swGo) castUlt(`隐藏分 ${sw.score} ≥ ${swAt}，自动`);
        if (!ready.length) { if (swGo) continue; return; }''')
rep('''      <div class="row">
        ${sc("sig", "专武：开大时笑点 +")}''',
'''      <div class="row">
        ${sc("auto", "隐藏分达到")}<input type="number" id="s-autoAt" value="${W.autoAt ?? 60}" data-s="autoAt" min="0" step="10" aria-label="自动开大的隐藏分" style="width:56px"><span title="和其他人的“满能量自动开大”同一个时机：每次行动结束后检查；开着时“开大时机”里安排的也照开">时自动开大</span>
      </div>
      <div class="row">
        ${sc("sig", "专武：开大时笑点 +")}''')
open(p, 'w', encoding='utf8', newline='').write(s)
