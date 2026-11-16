# 4.7 王棋隐藏关卡的赛季效果 / 关卡效果：做成“关卡”框里的按钮，给每个我方角色卡加 / 去掉一组带「关卡·」前缀的效果（可重复运行）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b):
    global s
    if b in s: return
    assert s.count(a) == 1, a
    s = s.replace(a, b)
rep('          <button type="button" id="stg-go" class="primary">换上这一波敌人</button>',
    '          <button type="button" id="stg-go" class="primary">换上这一波敌人</button>\r\n          <button type="button" id="stg-fx47" title="给每个我方角色卡加 / 去掉 4.7 王棋隐藏关卡的赛季效果和关卡效果（效果说明都以「关卡·」开头，在卡片的“其他”里，可以单独关掉）">加上 / 去掉 4.7 王棋的关卡效果</button>')
code = r'''  const FX47 = [
    { trigger: "start", type: "dbuf", mode: "dmg", dsc: "s", value: 40, duration: 0, note: "关卡·终结之吻：我方战技伤害 +40%" },
    { trigger: "start", type: "dbuf", mode: "dmg", dsc: "u", value: 40, duration: 0, note: "关卡·终结之吻：我方终结技伤害 +40%" },
    { trigger: "start", type: "energy", mode: "maxp", value: 25, duration: 0, note: "关卡·终结之吻：恢复 25% 能量（官方是我方任意目标回合开始时全场一次，这里按每人开局算）" },
    { trigger: "ult", type: "aha", value: 30, once: true, duration: 0, note: "关卡·无上喜悦：施放终结技后获得 30 个笑点（每位角色只一次）" },
    { trigger: "heal", or: "shield", type: "dbuf", mode: "resPen", value: 20, duration: 2, note: "关卡·锤砧战术：受到治疗 / 护盾后 全属性抗性穿透 +20%（2 回合；官方是“别人施加的”，这里自己给自己的也算）" },
    { trigger: "start", type: "hpcost", mode: "set", value: 50, duration: 0, note: "关卡·残秽：战斗开始时损失自身最大生命值的 50%" },
  ];
  $("stg-fx47").onclick = () => {
    const al = S.units.filter(u => u.kind === "ally" && !u.sm), has = al.some(u => u.effects.some(e => String(e.note || "").startsWith("关卡·")));
    for (const u of S.units) u.effects = u.effects.filter(e => !String(e.note || "").startsWith("关卡·"));
    if (!has) for (const u of al) for (const x of FX47) u.effects.push({ id: nid(), every: 1, target: "self", ...x });
    renderEditor(); update();
  };
'''
code = code.replace('\n', '\r\n')
rep('  $("add-enemy").onclick = () => addUnit("enemy");', code + '  $("add-enemy").onclick = () => addUnit("enemy");')
open(p, 'w', encoding='utf8', newline='').write(s)
