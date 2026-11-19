# 用户：敌人出招可以自己选，默认按顺序（2026-11-19，没改 tv；可重复运行）。
# 敌人卡字段 skOv = {"第几次行动": 技能下标}（按这个敌人在模拟里的行动次数编号，含另一面借本体出手、连续行动的第二下）；
# 没指定的按原来的出招顺序。行动记录 rec.eKey / eNat（按顺序会出的招）/ eOpts（可选的招）。界面：敌人卡“每次出招”。
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# 1) 模拟：按顺序选出来的招 → 有单独指定就换
rep('''          const sqI = ((actor.turns - 1 + (FG ? 0 : num(actor.sqo))) % seq.length + seq.length) % seq.length, skI = fxA ?? seq[sqI], sk = MON.sk[skI];''',
    '''          const sqI = ((actor.turns - 1 + (FG ? 0 : num(actor.sqo))) % seq.length + seq.length) % seq.length, skN = fxA ?? seq[sqI];
          actor.eAct = num(actor.eAct) + 1; const eKey = String(actor.eAct), ovK = actor.skOv ? actor.skOv[eKey] : null;   // 用户单独指定的出招（敌人卡“每次出招”），键 = 第几次行动
          const skI = ovK != null && MON.sk[+ovK] ? +ovK : skN, sk = MON.sk[skI];
          rec.eKey = eKey; rec.eNat = skN; rec.eOpts = [...new Set(seq.concat(((FG ? MON.m.find(m => m.n === FG.n) : monOf(actor)) || {}).k || []))].filter(k => MON.sk[k]);''')
# 2) 界面：敌人卡
rep('''          ${(m.p || []).map(k => `<p class="hint">天赋：${esc(MON.sk[k].d)}</p>`).join("")}''',
    '''          <div class="turn-acts e-acts" data-ei="${i}"></div>
          ${u.skOv ? `<div class="ult-list"><span class="hint">单独指定了 ${Object.keys(u.skOv).length} 次出招</span><button class="ghost" data-act="del-skov" data-u="${i}" style="font-size:12px;padding:1px 8px">全部改回按顺序</button></div>` : ""}
          ${(m.p || []).map(k => `<p class="hint">天赋：${esc(MON.sk[k].d)}</p>`).join("")}''')
rep('''    renderTurnActs(R); renderKActs(R);''', '''    renderTurnActs(R); renderKActs(R); renderEActs(R);''')
rep('''  function renderKActs(R) {''', '''  function renderEActs(R) {   // 敌人卡“每次出招”：显示范围内这个敌人的每次行动，默认按出招顺序，可以单独改
    document.querySelectorAll(".e-acts").forEach(box => {
      const i = +box.dataset.ei, u = S.units[i]; if (!u) return;
      const acts = R.actions.filter(a => a.uid === u.id && a.eKey);
      if (!acts.length) { box.innerHTML = ""; return; }
      box.innerHTML = `<span class="hint">每次出招（默认按顺序）：</span>` + acts.map(a => {
        const ov = !!(u.skOv && u.skOv[a.eKey]), cur = ov ? +u.skOv[a.eKey] : a.eNat;
        const opts = (a.eOpts || []).concat(a.eOpts && a.eOpts.includes(cur) ? [] : [cur]).filter(k => MON.sk[k]);
        const when = `第 ${a.eKey} 次行动${a.face ? `（${a.face}）` : ""}，AV ${fmt(a.t, 2)}；按顺序是「${MON.sk[a.eNat] ? MON.sk[a.eNat].n : "?"}」`;
        return `<span class="ta-wrap"><label class="ta${ov ? " ov" : ""}" title="${esc(when)}${ov ? "（单独指定过）" : ""}">${a.eKey}<span class="hint" style="font-size:11px">·${fmt(a.t, 1)}</span><select data-esk="${i}" data-k="${a.eKey}" data-nat="${a.eNat}" aria-label="${esc(when)}">${opts.map(k => `<option value="${k}"${k === cur ? " selected" : ""}>${esc(MON.sk[k].n)}${k === a.eNat ? "（顺序）" : ""}</option>`).join("")}</select></label></span>`;
      }).join("");
    });
  }
  function renderKActs(R) {''')
rep('''    if (t.dataset.tact !== undefined) {''', '''    if (t.dataset.esk !== undefined) {   // 敌人卡“每次出招”：选回按顺序的那招就删掉单独指定
      const u = S.units[+t.dataset.esk], k = t.dataset.k;
      u.skOv = Object.assign({}, u.skOv);
      if (t.value === t.dataset.nat) delete u.skOv[k]; else u.skOv[k] = +t.value;
      if (!Object.keys(u.skOv).length) delete u.skOv;
      renderEditor(); update(); return;
    }
    if (t.dataset.tact !== undefined) {''')
rep('''      case "del-actov":''', '''      case "del-skov": delete S.units[i].skOv; break;
      case "del-actov":''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-19（没改 tv；tools/eskov.py）</b>：用户要求：<b>敌人出招可以自己选</b>。套了敌人模板的敌人卡上多一行“每次出招”，列出显示范围内这个敌人的每次行动（按行动次数编号，归寂另一面借本体出手、连续行动的第二下也各算一次），默认就是原来的出招顺序，下拉改成别的招只改这一次；选回标“（顺序）”的那招就恢复，“全部改回按顺序”一次清掉。改了出招以后，这一招的打谁、受击回能、推条减速、伤害都按新选的招算；后面没改的照旧按顺序轮。没改的配置结果不变。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
