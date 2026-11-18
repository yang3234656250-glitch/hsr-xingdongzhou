# 队里有多个攻击型秘技（开怪秘技）的角色时，让用户选一个触发（用户要求）。
# 攻击型 = 进战效果里有秘技伤害（start 触发、说明以「秘技」开头、type hitd），或银狼LV.999（秘技盲盒）。
# S.opener = 选中的角色 id（没选 / 选的不是攻击型 = 队伍里第一个攻击型的）；没选中的攻击型角色，开局和转阶段都不触发她 / 他的秘技。
# 界面：攻击型角色有 2 个以上时，这些角色卡名字旁边出现「开怪」单选。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
# 全局判断
rep('  function renderEditor() {\n',
    '  // 攻击型秘技（开怪秘技）：进战效果里有秘技伤害，或银狼LV.999（秘技盲盒）；有几个时用 S.opener 选一个触发\n'
    '  function atkTech(u) { return !!u && u.kind === "ally" && !u.sm && (tidOf(u) === "1506" || (u.effects || []).some(e => !e.off && e.trigger === "start" && e.type === "hitd" && /^秘技/.test(e.note || ""))); }\n'
    '  function openerId(units) { const L = (units || S.units).filter(atkTech); if (!L.length) return null; return (L.find(u => u.id === S.opener) || L[0]).id; }\n'
    '  function renderEditor() {\n')
# 开局：没选中的攻击型角色不放秘技
rep('      const S0 = U.map(u => [u, fx(u, "start")]);\n',
    '      const OPN = openerId(U); const S0 = U.map(u => [u, atkTech(u) && u.id !== OPN ? fx(u, "start").filter(e => !/^秘技/.test(e.note || "")) : fx(u, "start")]);   // 开怪秘技只有选中的那位触发\n')
rep('      if (!swU || swU.gone || W.swq === false) return;\n',
    '      if (!swU || swU.gone || W.swq === false || openerId(U) !== swU.id) return;\n')
rep('.filter(([u, F]) => F.some(e => e.type === "hitd"));   // 攻击型秘技（有秘技伤害的）才算开怪秘技；加状态的、领域类的不算',
    '.filter(([u, F]) => F.some(e => e.type === "hitd") && u.id === openerId(U));   // 攻击型秘技（有秘技伤害的）才算开怪秘技，几个时只有选中的那位；加状态的、领域类的不算')
# 界面：角色卡名字旁边的单选
rep('''              <button class="ghost tr-btn" data-act="trace" data-u="${i}" title="查看行迹（技能 / 额外能力 / 属性强化）" aria-label="查看行迹">迹</button>\n''',
    '''              ${atkTech(u) && S.units.filter(atkTech).length > 1 ? `<label class="hint" title="队里有几个攻击型（开怪）秘技时只有一个触发：选用谁的秘技打怪进战（敌人转阶段时也是她 / 他的再触发）"><input type="radio" name="opener" data-op="${u.id}" ${openerId() === u.id ? "checked" : ""}> 开怪</label>` : ""}\n              <button class="ghost tr-btn" data-act="trace" data-u="${i}" title="查看行迹（技能 / 额外能力 / 属性强化）" aria-label="查看行迹">迹</button>\n''')
rep('''  ed.addEventListener("change", e => {\n    const t = e.target;\n''',
    '''  ed.addEventListener("change", e => {\n    const t = e.target;\n    if (t.dataset.op !== undefined) { S.opener = t.dataset.op; update(); return; }   // 开怪秘技选谁\n''')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/opener47.py）</b>。队里有<b>两个以上攻击型秘技</b>（开怪秘技：进战有秘技伤害的，和银狼LV.999）时，这些角色卡名字旁边出现「开怪」单选，只有选中的那位的秘技在开局和转阶段触发，其他攻击型角色的秘技都不算（游戏里只能用一个人的秘技打怪进战）。没选时默认队伍里第一个。对已有配置：队里只有一个攻击型秘技时不变；有两个以上的，以前每个人的秘技伤害都算了，现在只算一个。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
