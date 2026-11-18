# 4.7 归寂：按录像行动条重做【三面合一】（用户认图：第一管血带小格的金色小丑头像 = 归寂「成」，每回合连续行动两次；第三管血深紫半身 = 「坏」；
# 橙色面具 = 「住」（178 收束命运的博弈）；白色带翅膀 = 【好戏开场】（210 令欢愉终归死寂，天赋原文）。
# phm 每一管：「主形态[@开始%[@速度倍数[@每回合几招]]]」+「另一面@开始%@速度倍数@每回合几招@第二招技能下标」+ …；
#   名字写成「好戏开场#45」= 不在 MON 里的单位，只放技能 45。开始% = 转入这管血后离第一次出手是归寂一个间隔的百分之几；
#   主形态写了开始% 就不吃【转面】拉条（坏是新出现的面，录像 214 才第一次出手）。
# 默认（按录像 4.7归寂下 1:39～2:30 的行动条推算）：
#   第 1、2 管：成，每回合两招；格式第 5 项（主形态）/ 第 6 项（另一面）= 从出招表第几招开始（录像：坏 214 埋梗时刻 = 第 7 招，成 151 虚无 = 第 3 招，住 178 博弈 = 第 3 招）；第 3、4 管：坏@116 + 成@0@1.35@2@43（跟着转面马上出手、间隔约 40、第二招固定清除存在的球戏）
#   + 住@52（178 博弈）+ 好戏开场#45@111（约 211 令欢愉终归死寂）。（可重复运行，没改 tv）
p = 'index.html'
s = open(p, encoding='utf8', newline='').read()
def rep(a, b, n=1):
    global s
    a = a.replace('\r\n', '\n').replace('\n', '\r\n'); b = b.replace('\r\n', '\n').replace('\n', '\r\n')
    if b in s: return
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
C, Z, K = '万色返空主，归寂•「成」', '万色返空主，归寂•「住」', '万色返空主，归寂•「坏」'
OLD = f'{C}|{C}|{K}+{C}+{Z}|{K}+{C}+{Z}'
P3 = f'{K}@116@@@6+{C}@0@1.35@2@43@2+{Z}@52@@@@2+好戏开场#45@111'
NEW = f'{C}@@@2|{C}@@@2|{P3}|{P3}'
s = s.replace(OLD, NEW)
rep('fl = String(pm[en.ph] || "").split("+").map(x => x.trim()), mn = fl[0], m2 = mn && MON.m.find(x => x.n === mn);',
    'fl = String(pm[en.ph] || "").split("+").map(x => x.trim().split("@")), mn = fl[0][0], m2 = mn && MON.m.find(x => x.n === mn);   // 每段：名字@开始%@速度倍数@每回合几招@第二招\n'
    '        en.dblN = Math.max(1, num(fl[0][3]) || 1); en.dblI = 0; en.moX = fl[0][1] != null && fl[0][1] !== "" ? num(fl[0][1]) : null; if (fl[0][4] != null && fl[0][4] !== "") en.sqo = num(fl[0][4]) - en.turns;')
rep('const sk = MON.sk[seq[(actor.turns - 1) % seq.length]];', 'const sqI = ((actor.turns - 1 + (FG ? 0 : num(actor.sqo))) % seq.length + seq.length) % seq.length, sk = MON.sk[seq[sqI]];   // sqo：换形态后从出招表第几招开始（phm 第 5 项）')
rep('((monOf(actor) || {}).x || {})[seq[(actor.turns - 1) % seq.length]]', '((monOf(actor) || {}).x || {})[seq[sqI]]')
rep('          const skIdx = seq[(actor.turns - 1) % seq.length];', '          const skIdx = seq[sqI];')
rep('if (num(actor.zr) > 0 && ZRT.includes(sk.t)) for', 'if (num(actor.zr) > 0 && ZRT.includes(sk.t) && !(FG ? FG.i2 > 0 : num(actor.dblI) > 0)) for')   # 【滋扰】一个回合只算一次（连续行动的第二下不再推条，按录像）
rep('''        if (fl.length > 1 && !FACE.some(f => f.boss === en)) {   // 【三面合一】：另外几面不可选中、共享生命值，各自跑条出手（录像）
          const fo = String(en.fo ?? "0|50").split("|").map(x => num(x)), sp0 = Math.max(1e-9, spdOf(en));
          fl.slice(1).forEach((nm, i) => { const mf = MON.m.find(x => x.n === nm); if (mf) FACE.push({ boss: en, n: nm.split("「")[1] ? "「" + nm.split("「")[1] : nm, seq: (mf.q || []).slice(), k: en.turns, at: t + num(fo[i]) * 100 / sp0, o: i }); });
          addLog(`${en.name}【三面合一】：${fl.slice(1).map(x => "「" + (x.split("「")[1] || x)).join("、")}不可选中，和${m2 ? "「" + (m2.n.split("「")[1] || m2.n) : "本体"}共享生命值，各自按自己的出招表行动`, false, "var(--enemy)");
        } }''',
'''        if (fl.length > 1 && !FACE.some(f => f.boss === en)) {   // 【三面合一】：另外几面不可选中、共享生命值，各自跑条出手（录像行动条）
          const sp0 = Math.max(1e-9, spdOf(en)), nm0 = x => x.includes("「") ? "「" + x.split("「")[1] : x.split("#")[0];
          fl.slice(1).forEach((a, i) => { const [nm, off, sm, n2, s2, k0] = a, fix = nm.includes("#") ? [num(nm.split("#")[1])] : null, mf = fix ? null : MON.m.find(x => x.n === nm);
            if (fix || mf) FACE.push({ boss: en, o0: i, n: nm0(nm), seq: fix || (mf.q || []).slice(), k: k0 != null && k0 !== "" ? num(k0) : en.turns, at: t + num(off) * 100 / sp0, o: i, sm: num(sm) || 1, n2: Math.max(1, num(n2) || 1), s2: s2 != null && s2 !== "" ? num(s2) : null, i2: 0 }); });
          addLog(`${en.name}【三面合一】：${fl.slice(1).map(a => nm0(a[0])).join("、")}各自在行动序列上行动（不可选中，和${m2 ? "「" + (m2.n.split("「")[1] || m2.n) : "本体"}共享生命值）`, false, "var(--enemy)");
        } }''')
# 主形态写了开始% 就不吃【转面】拉条
rep('        pull(en, 10000); sumT0 = t;', '        if (en.moX != null) { en.dist = en.moX * 100; en.zpre = null; } else pull(en, 10000); sumT0 = t;   // 新出现的主形态（坏）按开始% 排，不拉条')
# 另一面：速度倍数、每回合几招、第二招固定
rep('move(f.at - t); t = f.at; f.at = t + 10000 / Math.max(1e-9, spdOf(f.boss)); const b = f.boss;',
    'move(f.at - t); t = f.at; f.at = t + 10000 / Math.max(1e-9, spdOf(f.boss) * f.sm); const b = f.boss;')
rep('const FG = actor.faceGo || null; if (FG) { actor.faceGo = null; actor.tSv = actor.turns; actor.turns = FG.k; FG.k++; actor.seqSv = actor.seq; actor.seq = FG.seq; }',
    'const FG = actor.faceGo || null; if (FG) { actor.faceGo = null; actor.tSv = actor.turns; const fx2 = FG.i2 > 0 && FG.s2 != null; actor.turns = fx2 ? FG.k - 1 : FG.k; if (!fx2) FG.k++; actor.seqSv = actor.seq; actor.seq = fx2 ? [FG.s2] : FG.seq; }')
# 连续行动：主形态用 again，另一面马上再排一次
rep('      if (actor.again) { actor.again = false;',
    '      if (FG && FG.n2 > 1) { FG.i2 = (FG.i2 + 1) % FG.n2; if (FG.i2) { FG.at = t; FG.o = -1; marks.push({ t, uid: actor.id, label: "连续行动", color: "var(--enemy)" }); } else FG.o = FG.o0 ?? FG.o; }   // 每回合连续行动几次\n'
    '      else if (!FG && actor.kind === "enemy" && num(actor.dblN ?? (actor.dice ? 2 : 1)) > 1 && !actor.gone) { actor.dblI = (num(actor.dblI) + 1) % num(actor.dblN ?? 2);   // 4.7 归寂没写 phm 时第 1 管也是每回合两招\n        if (actor.dblI) actor.again = true; }\n'
    '      if (actor.again) { actor.again = false;')
rep('label: "再次行动", color: "var(--enemy)" }); } }   // 「清', 'label: "连续行动", color: "var(--enemy)" }); } }   // 「清')
rep('          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n',
    '          <ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
    '<li><b>2026-11-18（没改 tv；tools/face47b.py）</b>。4.7 归寂按录像行动条重做（用户认的头像）：归寂「成」<b>每回合连续行动两次</b>（第 1 管 54：讥讽的目光 + 存在的闹剧）。第 3、4 管【三面合一】：本体换成「坏」，第一次出手在转阶段后约 63 行动值（录像 214 埋梗时刻，不吃【转面】拉条）；「成」跟着【转面】马上出手、间隔约 40（录像 151、191；比归寂的速度快，原因不明，按录像取 1.35 倍）、每回合两招且第二招固定「清除存在的球戏」；「住」在转阶段后半个间隔出手（178 收束命运的博弈）；<b>【好戏开场】</b>在转阶段后约 60 行动值放「令欢愉终归死寂」（天赋原文，录像约 211）。这些位置和倍数是按一次录像推算的，敌人卡 phm 里可改（格式：名字@开始%@速度倍数@每回合几招@第二招技能下标）。</li>\n')
open(p, 'w', encoding='utf8', newline='').write(s)
print('ok')
