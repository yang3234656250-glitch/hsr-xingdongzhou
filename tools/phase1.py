# 敌人分阶段（转阶段）：敌人卡「分阶段生命值」，打空一条血 → 转阶段（生命值换成下一条、溢出不继承、敌人身上的减益全部清除）。
# 同时修了 hurtEnemy 里“打空就消灭”被 // 注释吞掉的老问题。没填分阶段生命值的敌人和以前完全一样。
import sys
p = sys.argv[1] if len(sys.argv) > 1 else "index.html"
s = open(p, "rb").read().decode("utf8").replace("\r\n", "\n")
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)

# 1. 解析分阶段生命值
rep("    const eHpMaxOf = en =>", "    const phOf = en => String(en.phs || \"\").split(/[,，\\s\\/]+/).map(Number).filter(x => x > 0);   // 分阶段生命值（逗号分隔）\n    const eHpMaxOf = en =>")
# 2. 开局：有分阶段就用第 1 条
rep('if (z.kind === "enemy") { const mx = eHpMaxOf(z); if (mx > 0) { z.ehx = mx; z.ehc = mx; } }',
    'if (z.kind === "enemy") { let mx = eHpMaxOf(z); const ph = phOf(z); if (ph.length) { z.phs = ph; z.ph = 0; mx = ph[0]; } if (mx > 0) { z.ehx = mx; z.ehc = mx; } }')
# 3. 打空一条血：还有下一阶段就转阶段，否则消灭
rep("    const ahaU = U.find(z => z.kind === \"ally\"",
"""    const endBar = (en, killer) => {   // 这一条血打空（或达到欢愉负债）：还有下一阶段 → 转阶段；否则消灭
      if (!(en.phs && en.ph < en.phs.length - 1)) { killEnemy(en, killer); return; }
      const over = Math.max(0, -en.ehc), old = en.ph + 1, nd = (en.buffs || []).length + (en.dots || []).length + (en.wk || []).length + Object.keys(en.st || {}).length; en.ph++;
      en.ehx = en.ehc = en.phs[en.ph];   // 欢愉负债不清除（写在阿哈的效果里）
      en.buffs = []; en.dots = []; en.wk = []; en.st = {}; en.frozen = false; en.cmz = null; en.cmzUsed = false; en.yh = 0;   // 敌人身上的减益（易伤 / 减抗 / 减速 / 持续伤害 / 弱点 / 状态）不继承；【欢愉负债】不清除
      en.broken = false; en.tcur = toughMax(en);   // 韧性回满
      marks.push({ t, uid: en.id, label: "转阶段", color: "var(--enemy)", from: killer ? killer.name : "" });
      addLog(`${en.name} 第 ${old} 阶段生命值打空，转入第 ${en.ph + 1} 阶段（生命值 ${Math.round(en.ehx)}；上一阶段溢出的 ${Math.round(over)} 点伤害不继承；敌人身上的减益全部清除，共 ${nd} 项）`, false, "var(--enemy)");
    };
    const ahaU = U.find(z => z.kind === "ally\"""".replace('"ally\\"', '"ally"'))
rep('fireEv("ehp50", en);   // 生命值跌破 50%（黑塔天赋） if (en.ehc <= 1e-6) { killEnemy(en, killer); return; }',
    'fireEv("ehp50", en);   // 生命值跌破 50%（黑塔天赋）\n      if (en.ehc <= 1e-6) { endBar(en, killer); return; }')
rep("addLog(`${en.name} 剩余生命值（${Math.round(en.ehc)}）不高于【欢愉负债】（${Math.round(d)}）`, false, ahaU.color, ahaU.id); killEnemy(en, killer); }",
    "addLog(`${en.name} 剩余生命值（${Math.round(en.ehc)}）不高于【欢愉负债】（${Math.round(d)}）`, false, ahaU.color, ahaU.id); endBar(en, killer); }")
# 4. 敌人卡输入框 + 保存
rep('data-f="ehp" style="width:96px"></label>', 'data-f="ehp" style="width:96px"></label>${S.dg && S.dg.eHp ? `<label for="ph-${u.id}" title="分阶段生命值，逗号分隔（比如 16768365,16768365,31859894）。填了就按这几条血依次打：打空一条转下一阶段，溢出的伤害不继承，敌人身上的减益全部清除（欢愉负债不清除），韧性回满；污染关卡的贪婪生命值可以当成最后多一条血；清空 = 不分阶段（用左边的生命值）">分阶段 <input type="text" id="ph-${u.id}" value="${esc(u.phs || \'\')}" placeholder="如 1000000,2000000" data-u="${i}" data-f="phs" style="width:210px"></label>` : ""}', 2)
rep('      if (f === "tough" && el.value === "") delete u.tough;',
    '      if (f === "phs") { u.phs = String(el.value || "").replace(/[^0-9.,，\\s\\/]/g, "").trim(); if (!u.phs) delete u.phs; }   // 分阶段生命值\n      if (f === "tough" && el.value === "") delete u.tough;')
# 5. 更新日志
rep('<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n<li><b>2026-11-16（敌人转阶段，没改 tv）</b>。新：敌人卡（开了“我方伤害扣敌人生命值”时）多一个<b>分阶段生命值</b>（逗号分隔，如 4.7 王棋归寂 16768365,16768365,31859894）。一条血打空就转阶段：生命值换成下一条、<b>溢出的伤害不继承</b>、<b>敌人身上的减益全部清除</b>（易伤 / 减抗 / 减速 / 持续伤害 / 植入弱点 / 状态；用户说的“boss 的 debuff 不继承”，<b>欢愉负债不清除</b>，它写在阿哈的效果里）、韧性回满，行动轴标“转阶段”，日志写清溢出多少。污染关卡的「贪婪生命值」（受到致命伤害时回血、压制生命上限）按用户说法相当于多一次转阶段，填成最后多一条血就行（归寂：16768365,16768365,31859894,6707346）。转阶段时敌人行动条怎么变、BOSS 自己的阶段机制原文没有，没做（等用户给）。没填就和以前一样。顺手修了一个老问题：敌人生命值打空就消灭那一行被 // 注释吞掉了，没带星神★阿哈的队伍里敌人其实打不死，现在修好了（带阿哈的队伍不受影响，靠【欢愉负债】消灭的照旧）。依据：用户说明 + nanoka 4.7 隐藏关卡归寂三条血量。</li>\n')
open(p, "wb").write(s.replace("\n", "\r\n").encode("utf8"))
print("ok")
