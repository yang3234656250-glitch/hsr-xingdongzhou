"""tv 113：卡厄斯兰那细节（用户说明 + 官方原文）。
- 用户：支柱没有 4 点【毁伤】也能放（0 点也照选的放）；反击和最后一击也触发“攻击后”。
- 【毁伤】：上限 7 点，未变身时也保留（用户截图的名词解释）。变身时 +4（不再重置），强化普攻 / 灾厄 / 秘技加的都封顶 7。秘技的 2 点改成进入战斗时获得。
- 最后一击、弑魂之炽反击：造成伤害后走一遍“施放攻击”（攻击后效果、削韧、附加伤害标记都算）。
- 修正：卡厄斯兰那自己行动的伤害之前只用了挂在卡厄斯兰那身上的增益（白厄身上的变身攻击力 +80%、暴击等都没算），现在用白厄的（召唤物模板 own）。
- 昔涟献予「负世」之诗【永续的燃烧】：卡厄斯兰那施放攻击后 5 次附加伤害（每次随机单体 10% 攻击力，3 魂 11%）；额外回合刷新时获得 4 点【毁伤】；
  变身时【火种】超过 12 点，每超出 1 点暴击伤害 +12%（3 魂 13.2%），最多 6 点。
召唤物模板新字段：own（本体变身：行动快照用本体的增益）、rcap（毁伤上限）、ref = [主人身上的状态, 剩几次时算刷新, 刷新给几点毁伤]、fz = [状态, 每点 %, 升级后每点 %, 升级要谁几魂, 最多几点, 那个角色的 id]。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 113, sys.argv[2])
C, has = F.C, F.has
F.rep('''          if (eff.mode === "rot") { if (tg.sm) tg.rot = Math.max(0, num(tg.rot) + v); continue; }''',
'''          if (eff.mode === "rot") { if (tg.sm) tg.rot = Math.max(0, Math.min(num((smDef(tg) || {}).rcap) || Infinity, num(tg.rot) + v)); continue; }   // 封顶 rcap（7 点）''')
F.rep('''        if (!was && sd.rot) u.rot = num(sd.rot[0]); if (!was) u.tailOn = false;''',
'''        if (!was && sd.rot) u.rot = Math.min(num(sd.rcap) || Infinity, num(u.rot) + num(sd.rot[0])); if (!was) u.tailOn = false;   // 变身时 +4 点【毁伤】，没用完的保留（上限 7）
        if (!was && sd.fz && o && hasSt(o, String(sd.fz[0]))) {   // 【永续的燃烧】：变身时【火种】每超出开大所需 1 点，暴击伤害 +X%
          const F0 = sd.fz, src0 = U.find(z => z.kind === "ally" && !z.sm && tidOf(z) === String(F0[5])), per = src0 && num(src0.eid) >= num(F0[3]) ? num(F0[2]) : num(F0[1]);
          const ov = Math.min(num(F0[4]), Math.max(0, num(o.ueb) - eCfg(o).ultCost));
          o.buffs = o.buffs.filter(b => b.key !== "fz:" + u.id);
          if (ov > 0) { o.buffs.push({ key: "fz:" + u.id, kind: "d", st: "cd", sc: "", src: u.id, v: ov * per, n: 1 }); marks.push({ t, uid: u.id, label: `火种超出 ${ov} 点：暴伤 +${Math.round(ov * per * 10) / 10}%`, color: u.color, from: u.name }); } }''')
F.rep('''        if (!was && sd.rot) { u.kNo = num(u.kNo) + 1; u.kTurn = 0; delete u.kz; } }''',
'''        if (!was && sd.rot) { u.kNo = num(u.kNo) + 1; u.kTurn = 0; delete u.kz; u.kRef = false; } }''')
OLD = '''      if (!u || !u.sm || u.gone) return;
      u.gone = true; u.dist = Infinity;
      if (u.kz) kzEnd(u);   // 变身结束：没来得及反击的【弑魂之炽】直接没了
      { const fk = (smDef(u) || {}).fin, o0 = byId[u.sm.owner];   // 离场时直接造成一次伤害（白厄最后一击：变身结束 = 最后一击，按这时的增益）
        if (fk && o0) { const e0 = U.find(z => z.kind === "enemy" && !z.gone);
          const r = { t, uid: o0.id, en: e0 ? e0.id : null, k: "最后一击", sup: String(fk), db: dbSnap(o0), edb: edbSnap(e0), eAll: edbAll(), seq: seq++, ebk: ebkNow() };
          if (num(u.lsCutF) > 0) r.lsCut = num(u.lsCutF); delete u.lsCutF; dotRecs.push(r);
          addLog(`${o0.name}「最后一击」造成伤害${r.lsCut ? `（倍率 −${Math.round(r.lsCut * 1000) / 10}%）` : ""}`, false, o0.color, o0.id); log[log.length - 1].dd = [r]; } }
'''
NEW = '''      if (!u || !u.sm || u.gone) return;
      if (u.kz) kzEnd(u);   // 变身结束：没来得及反击的【弑魂之炽】直接没了
      { const fk = (smDef(u) || {}).fin, o0 = byId[u.sm.owner];   // 离场时直接造成一次伤害（白厄最后一击：变身结束 = 最后一击，按这时的增益），之后算一次施放攻击
        if (fk && o0) { const e0 = U.find(z => z.kind === "enemy" && !z.gone);
          const r = { t, uid: o0.id, en: e0 ? e0.id : null, k: "最后一击", sup: String(fk), db: dbSnap(o0), edb: edbSnap(e0), eAll: edbAll(), seq: seq++, ebk: ebkNow() };
          if (num(u.lsCutF) > 0) r.lsCut = num(u.lsCutF); delete u.lsCutF; dotRecs.push(r);
          addLog(`${o0.name}「最后一击」造成伤害${r.lsCut ? `（倍率 −${Math.round(r.lsCut * 1000) / 10}%）` : ""}`, false, o0.color, o0.id); log[log.length - 1].dd = [r];
          atkAct(u, false, fk === "u" ? "ult" : "skill"); } }
      u.gone = true; u.dist = Infinity;
      { const o1 = byId[u.sm.owner]; if (o1) o1.buffs = o1.buffs.filter(b => b.key !== "fz:" + u.id); }   // 【永续的燃烧】火种暴伤：变身结束取消
'''
F.rep(OLD, NEW)
F.rep('''      marks.push({ t, uid: k.id, label: `反击（弑魂之炽 ${z.n} 层）`, color: k.color, from: k.name });
      addLog(`${k.name} ${why}：反击（【弑魂之炽】${z.n} 层，倍率 ×${Math.round(mul * 100) / 100}）`, false, k.color, o.id); log[log.length - 1].dd = [r];''',
'''      marks.push({ t, uid: k.id, label: `反击（弑魂之炽 ${z.n} 层）`, color: k.color, from: k.name });
      addLog(`${k.name} ${why}：反击（【弑魂之炽】${z.n} 层，倍率 ×${Math.round(mul * 100) / 100}）`, false, k.color, o.id); log[log.length - 1].dd = [r];
      if (!k.gone) atkAct(k, false, "skill");   // 反击也算施放攻击（攻击后效果、附加伤害）''')
F.rep('''          if (a === "pl" && !(num(actor.rot) > 0)) { lab("没有【毁伤】，改用强化普攻"); a = "eb"; }
''', '')
F.rep('''            actor.rot = num(actor.rot) + ens.length; rec.smk = "-";''', '''            actor.rot = Math.min(num(D.rcap) || Infinity, num(actor.rot) + ens.length); rec.smk = "-";''')
F.rep('''          else { actor.rot = num(actor.rot) + num(R[1]); rec.smk = undefined;''', '''          else { actor.rot = Math.min(num(D.rcap) || Infinity, num(actor.rot) + num(R[1])); rec.smk = undefined;''')
F.rep('''      if (actor.sm && actor.life > 0 && --actor.life <= 0) {   // 持续回合用完离场''',
'''      { const D0 = actor.sm && smDef(actor), rf = D0 && D0.ref, o2 = rf && byId[actor.sm.owner];   // 【永续的燃烧】：前一组额外回合用完、刷新时获得 4 点【毁伤】
        if (rf && o2 && !actor.kRef && hasSt(o2, String(rf[0])) && num(actor.life) - 1 === num(rf[1])) { actor.kRef = true; actor.rot = Math.min(num(D0.rcap) || Infinity, num(actor.rot) + num(rf[2])); marks.push({ t, uid: actor.id, label: `额外回合刷新：毁伤 +${rf[2]}（${actor.rot}）`, color: actor.color, from: actor.name }); } }
      if (actor.sm && actor.life > 0 && --actor.life <= 0) {   // 持续回合用完离场''')
F.rep('''    const dbSnap = (u, en) => !u || !u.buffs''', '''    // 行动时的增益快照：“本体变身”的召唤物（模板 sm.own，卡厄斯兰那）用本体身上的增益，再加上只挂在召唤物身上的
    const snapOf = a => { const o = a && a.sm && (smDef(a) || {}).own ? byId[a.sm.owner] : null; if (!o) return dbSnap(a); const ok = new Set((o.buffs || []).map(b => b.key)); return dbSnap(o).concat(dbSnap(Object.assign({}, a, { buffs: (a.buffs || []).filter(b => !ok.has(b.key)) }))); };
    const dbSnap = (u, en) => !u || !u.buffs''')
F.rep('''rec.db = dbSnap(a); rec.edb = edbSnap(); rec.eAll = edbAll(); rec.pAt = pool;''', '''rec.db = snapOf(a); rec.edb = edbSnap(); rec.eAll = edbAll(); rec.pAt = pool;''', 2)
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('140807', '进入战斗后，为我方队友恢复#3[i]点能量，获得#2[i]点【毁伤】')
has('1141521', '刷新全部卡厄斯兰那的额外回合并获得#9[i]点【毁伤】'); has('1141521', '施放攻击后，造成#3[i]次附加伤害，每次伤害对敌方随机单体造成等同于卡厄斯兰那#4[f1]%攻击力的火属性附加伤害')
has('1141521', '变身时若【火种】大于#5[i]点，每超出1点，卡厄斯兰那的暴击伤害提高#6[i]%，最多可提高#7[i]%')
P = F.SK['1141521']['params']; assert P[5][3] == 0.1 and P[6][3] == 0.11 and abs(P[5][5] - 0.12) < 1e-9 and abs(P[6][5] - 0.132) < 1e-9 and P[5][8] == 4 and P[5][2] == 5 and P[5][4] == 12
has('r:141503', '忆灵技等级+1')
c = C[1408]; m = c['sm'][0]; assert m['k'] == 'khaslana'
m.update(own=1, rcap=7, ref=['献予「负世」之诗', 8, 4], fz=['献予「负世」之诗', 12, 13.2, 3, 6, '1415'])
E = c['eff']
q = find(E, '秘技终结之始：获得 2 点【毁伤】'); o1 = q['n']; q['t'] = 'start'; q['n'] = '秘技终结之始：进入战斗后获得 2 点【毁伤】（用了秘技再启用）'
lf = find(E, '昔涟献予「负世」之诗：变身时获得【永续的燃烧】'); o2 = lf['n']
lf['n'] = '昔涟献予「负世」之诗：变身时获得【永续的燃烧】，卡厄斯兰那的额外回合耗尽后不结束变身、刷新全部额外回合并获得 4 点【毁伤】（按多 8 次行动）'
fx = find(E, '额外伤害标记：【永续的燃烧】'); o3 = fx['n']; fx['n'] = '额外伤害标记：【永续的燃烧】卡厄斯兰那施放攻击后 5 次附加伤害（含反击、最后一击）'
c['notes'] = [n for n in c['notes'] if '毁伤】上限' not in n] + ['【毁伤】上限 7 点，未变身时也保留：变身时 +4，强化普攻 +2，灾厄 + 敌人数；支柱最多消耗 4 点，没有 4 点也能放', '昔涟【永续的燃烧】：变身时【火种】超过 12 点，每超出 1 点卡厄斯兰那暴击伤害 +12%（昔涟 3 魂 13.2%）']
F.rebuild(1408, E, rename={o1: q['n'], o2: lf['n'], o3: fx['n']}, notes=c['notes'])
F.XR.setdefault('1415', [])
assert not any(r['k'] == 'fs' for r in F.XR['1415'])
F.XR['1415'].append({"k": "fs", "n": "献予「负世」之诗【永续的燃烧】：卡厄斯兰那施放攻击后 5 次附加伤害，每次随机单体 10% 攻击力（3 魂 11%；火属性，这里按这次攻击的属性算抗性）", "who": "flag", "flag": "fs", "st": "aatk", "v": [0.1, 0.11], "upE": 3, "cnt": 5})
F.finish('卡厄斯兰那毁伤上限、反击和最后一击算攻击、永续的燃烧', '''<li><b>2026-11-14</b>：tv 113（tools/fix113.py）。卡厄斯兰那：【毁伤】上限 7 点、没用完的留到下次变身（变身时 +4）；支柱任何时候都能选；最后一击和弑魂之炽反击也算施放攻击，会触发攻击后效果。另外修正了一个老问题：卡厄斯兰那自己行动的伤害之前没吃到白厄身上的增益（变身攻击力 +80%、暴击等），现在算上了，伤害会明显变高。昔涟【永续的燃烧】补全：卡厄斯兰那每次攻击后 5 次附加伤害（之前没算）、额外回合刷新时 +4 点【毁伤】、变身时【火种】超过 12 点的暴伤加成。</li>''',
'''2026-11-14：卡厄斯兰那毁伤上限、反击和最后一击算攻击、永续的燃烧 —— tv 113（tools/fix113.py）。用户说明：支柱没 4 点毁伤也能放，反击和最后一击也触发攻击后；截图：毁伤上限 7、未变身也保留。
  未改 / 存疑：【永续的燃烧】附加伤害是火属性，这里按这次攻击（物理）的抗性和弱点算；最后一击记为终结技类型的攻击、反击记为战技类型的攻击（削韧按白厄的终结技 / 战技削韧）''')
