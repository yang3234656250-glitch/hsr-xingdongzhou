"""tv 90：姬子•启行助战技按官方规则：占用这回合的行动、开拓同行角色用完获得额外回合、【同行协议】自动进入并自动发动额外助战技、1 魂多 1 次弹射。
用法：python3 tools/fix90.py index.html <官方 json 目录>
- 官方说明（TextMap“助战技”）：施放助战技也会消耗当前行动回合 → 用了助战技的回合不再行动（不消耗 / 回复战技点、不回行动能量）。
- 行迹列车的脉搏在轰鸣：除姬子•启行外的开拓同行角色使用助战技后立即获得 1 个额外回合（2 魂：所有角色都获得）；额外回合里不能再用助战技，所以不会重复触发。
- 开拓同行角色（用户确认按攻略站，含各形态）：裁决 = 开拓者各命途、丹恒 / 丹恒•饮月 / 丹恒•腾荒、星期日；歼破 = 三月七 / 三月七（巡猎）/ 长夜月、姬子、瓦尔特。
  这些角色用助战技后，姬子•启行进入对应的【同行协议】（另一个结束），状态在姬子•启行身上，协议的增益跟着状态。
- 【同行协议：裁决】：队友主动施放 2 次终结技（1 魂 1 次）后姬子•启行发动 1 次无消耗的助战技；
  【同行协议：歼破】：我方每击中 1 名敌人 +1 充能（普通助战技也算，额外发动的不算），到 9 点（1 魂 6 点）消耗全部，发动 1 次无消耗的助战技。
  额外助战技单场最多 2 次（1 魂 3 次），姬子•启行施放终结技后刷新。额外助战技按姬子•启行自己用的倍率（200% + 4 × 32%），不算“使用助战技”（不回能、不给协议、不给额外回合）。
- 1 魂：姬子•启行用助战技时额外伤害次数 +1（多 1 次 32%）。"""
import sys, json, re
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 90, sys.argv[2])
C, prm, has, hast = F.C, F.prm, F.has, F.hast

CJ = ['8001', '8002', '8003', '8004', '8005', '8006', '8007', '8008', '8009', '8010', '1002', '1213', '1414', '1313']
JP = ['1001', '1224', '1413', '1003', '1004']
# ================= 引擎 =================
F.rep('''      const S0 = { H, X: tx(H).sup, cap: num(H.eid) >= 2 ? 2 : 1, n: {} }; for (const z of U) if (z.kind === "ally" && !z.sm) S0.n[z.id] = 1; return S0; })();''',
      '''      const S0 = { H, X: tx(H).sup, cap: num(H.eid) >= 2 ? 2 : 1, n: {}, xMax: 2 + (num(H.eid) >= 1 ? 1 : 0), cj: 0, ch: 0 }; S0.xLeft = S0.xMax; for (const z of U) if (z.kind === "ally" && !z.sm) S0.n[z.id] = 1; return S0; })();
    const SUPCJ = %s, SUPJP = %s;   // 开拓同行角色：用助战技后姬子•启行进入【同行协议：裁决】/【同行协议：歼破】（按攻略站，含各形态）
    const supProto = u => { const id = String((tplOf(u) || {}).id || ""); return SUPCJ.includes(id) ? "同行协议：裁决" : SUPJP.includes(id) ? "同行协议：歼破" : null; };
    const supCast = (actor, freeWhy) => {   // 使用（actor）/ 额外发动（freeWhy，姬子•启行无消耗）一次助战技：「拓星者」攻击
      const H = SUP.H, isH = actor === H, zk = isH ? "z2" : "z", e0 = U.find(z => z.kind === "enemy" && !z.gone);
      actSeq++; atkCtx = { u: H, k: zk };
      const r = { t, uid: H.id, en: e0 ? e0.id : null, k: freeWhy ? "额外助战技" : "助战技", sup: zk, db: dbSnap(H), edb: edbSnap(e0), eAll: edbAll(), seq: seq++, ebk: ebkNow() }; dotRecs.push(r);
      marks.push({ t, uid: actor.id, label: freeWhy ? "额外助战技" : "助战技", color: H.color, from: freeWhy || actor.name });
      addLog(freeWhy ? `${H.name} 发动 1 次无消耗的助战技（${freeWhy}，本场还能发动 ${SUP.xLeft} 次）` : `${actor.name} 使用助战技（「拓星者」攻击，占用这回合的行动）${isH ? "" : `，剩 ${SUP.n[actor.id]} 次`}`, false, H.color, actor.id); log[log.length - 1].dd = [r];
      if (freeWhy) { toughHit(H, zk); return; }
      if (!isH && hasEnergy(actor) && num(SUP.X.uE) > 0) { curWhy = "使用助战技"; addEnergy(actor, num(SUP.X.uE), true); }
      toughHit(H, zk);
      const pk = isH ? null : supProto(actor);
      if (pk) { endSt(H, pk === "同行协议：裁决" ? "同行协议：歼破" : "同行协议：裁决"); setSt(H, { stKey: pk, value: 1, duration: 0 }, H, H.color); }
      if (!isH && (pk || num(H.eid) >= 2)) { pendingX.push({ uid: actor.id, temp: 0, from: "列车的脉搏在轰鸣", keep: 0, jh: 0, why: "sup" }); marks.push({ t, uid: actor.id, label: "额外回合", color: H.color, from: "列车的脉搏在轰鸣" }); }   // 行迹列车的脉搏在轰鸣（2 魂：非开拓同行角色也算）
      teamFire("aSup", actor);
      supCharge(U.filter(z => z.kind === "enemy" && !z.gone).length || 1);   // 普通助战技击中的敌人也给歼破充能
    };
    const supCharge = n => {   // 【同行协议：歼破】：我方每击中 1 名敌人 +1 充能，到 9（1 魂 6）发动额外助战技
      if (!SUP || !hasSt(SUP.H, "同行协议：歼破") || SUP.H.gone) return;
      SUP.ch += n; const need = num(SUP.H.eid) >= 1 ? 6 : 9;
      if (SUP.ch >= need && SUP.xLeft > 0) { SUP.ch = 0; SUP.xLeft--; supCast(SUP.H, `同行协议：歼破，充能满 ${need} 点`); }
    };''' % (json.dumps(CJ), json.dumps(JP)))
F.rep('''          if (!isH) SUP.n[actor.id]--;
          rec.sup = true;
          const zk = isH ? "z2" : "z", e0 = U.find(z => z.kind === "enemy" && !z.gone);
          const r = { t, uid: H.id, en: e0 ? e0.id : null, k: "助战技", sup: zk, db: dbSnap(H), edb: edbSnap(e0), seq: seq++, ebk: ebkNow() }; dotRecs.push(r);
          marks.push({ t, uid: actor.id, label: "助战技", color: H.color, from: actor.name });
          addLog(`${actor.name} 使用助战技（「拓星者」攻击）${isH ? "" : `，剩 ${SUP.n[actor.id]} 次`}`, false, H.color, actor.id); log[log.length - 1].dd = [r];
          if (!isH && hasEnergy(actor) && num(SUP.X.uE) > 0) { curWhy = "使用助战技"; addEnergy(actor, num(SUP.X.uE), true); }
          toughHit(H, zk);
          teamFire("aSup", actor);''', '''          if (!isH) SUP.n[actor.id]--;
          rec.sup = true;
          supCast(actor, null);
          rec.act = null; rec.supTurn = true;   // 官方：施放助战技也会消耗当前行动回合''')
F.rep('''      if (u.atkUlt !== false) atkAct(u, false, "ult");''', '''      if (u.atkUlt !== false) atkAct(u, false, "ult");
      if (SUP && u === SUP.H) { SUP.xLeft = SUP.xMax; SUP.cj = 0; }   // 姬子•启行施放终结技后刷新额外助战技次数
      else if (SUP && u.kind === "ally" && !u.sm && !SUP.H.gone && hasSt(SUP.H, "同行协议：裁决")) {   // 【同行协议：裁决】：队友主动施放 2 次终结技（1 魂 1 次）后发动额外助战技
        SUP.cj++; const need = num(SUP.H.eid) >= 1 ? 1 : 2;
        if (SUP.cj >= need && SUP.xLeft > 0) { SUP.cj = 0; SUP.xLeft--; supCast(SUP.H, `同行协议：裁决，队友施放了 ${need} 次终结技`); }
      }''')
F.rep('''jdHit(who, fromFua ? "f" : ACT2K[act]); teamFire("atk", who, fromFua ? e => !e.nf : null); };''', '''jdHit(who, fromFua ? "f" : ACT2K[act]); teamFire("atk", who, fromFua ? e => !e.nf : null); if (SUP && who && who.kind === "ally") supCharge(hitEns().length); };''')
F.rep('''    if (tidOf(u) === "1505" && e.key === "u" && e.rnd > 0) {''', '''    if (tidOf(u) === "1510" && e.key === "z2" && num(u.eid) >= 1 && e.rnd > 0) mult += e.rnd / 4;   // 姬子•启行 1 魂：自己用助战技时额外伤害次数 +1（4 → 5 次）
    if (tidOf(u) === "1505" && e.key === "u" && e.rnd > 0) {''')

# ================= 模板 =================
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('151025', '姬子•启行造成的伤害提高#8[i]%，造成的终结技伤害额外提高#10[i]%。姬子•启行的队友主动施放#9[i]次终结技后，姬子•启行立即对敌方发动1次无消耗的助战技')
has('151026', '我方全体暴击伤害提高#8[i]%，战技造成的暴击伤害额外提高#10[i]%。我方每击中1名敌方目标均可获得1点充能，当充能到达#9[i]点后消耗所有充能，姬子•启行立即对敌方发动1次无消耗的助战技。本次助战技无法获得充能')
has('151022', '所有特殊效果发动的额外助战技单场战斗中最多发动#8[i]次，姬子•启行施放终结技后刷新发动次数'); assert prm('151022', 10)[7] == 2 and prm('151025', 10)[8] == 2 and prm('151026', 10)[8] == 9
has('r:151001', '【同行协议：裁决】状态下，发动助战技所需的终结技施放次数减少1次。【同行协议：歼破】状态下，发动助战技所需的充能减少3点。姬子•启行发动助战技时，造成额外伤害的效果次数增加1次')
hast(1510, '列车的脉搏在轰鸣', '除姬子•启行外的开拓同行角色使用助战技时，该角色会立即获得1个可插入施放终结技的额外回合')
c = C[1510]; E = c['eff']; ren = {}
for pre, st, n in [('助战技同行协议：裁决：姬子•启行造成的伤害', '同行协议：裁决', '【同行协议：裁决】：姬子•启行造成的伤害 +100%（5 魂 110%）'),
                   ('助战技同行协议：裁决：终结技伤害额外', '同行协议：裁决', '【同行协议：裁决】：终结技伤害额外 +100%'),
                   ('助战技同行协议：歼破：我方全体暴击伤害', '同行协议：歼破', '【同行协议：歼破】：我方全体暴击伤害 +100%（5 魂 110%）'),
                   ('助战技同行协议：歼破：战技的暴击伤害额外', '同行协议：歼破', '【同行协议：歼破】：战技的暴击伤害额外 +100%')]:
    e = find(E, pre); ren[e['n']] = n
    e.update(n=n, t='aSup', aw='all', ns=st, bk='st:%s#%s' % (st, e['bk'])); e.pop('off', None)
c['notes'] = ['助战技：每个角色卡上“每次行动”旁边勾“助”（或勾“有次数时都用助战技”），在那个角色的回合开始时使用，并占用这回合的行动（官方：施放助战技也会消耗当前行动回合）。开局每人 1 次（2 魂起上限 2），姬子•启行自己用不消耗；其他人用了恢复 4 点能量；持有【领航旗语】时每个我方回合开始恢复 1 次（2 魂 2 次）；姬子•启行回合开始时次数满就恢复 5 点能量',
              '开拓同行角色（按攻略站，含各形态）用助战技：立即获得额外回合（行迹列车的脉搏在轰鸣；2 魂起所有角色都有），姬子•启行进入【同行协议】——裁决：开拓者各命途、丹恒 / 丹恒•饮月 / 丹恒•腾荒、星期日；歼破：三月七 / 三月七（巡猎）/ 长夜月、姬子、瓦尔特',
              '【同行协议】的额外助战技（裁决：队友开 2 次大；歼破：击中敌人充能 9 点；1 魂 1 次 / 6 点）自动发动，单场最多 2 次（1 魂 3 次），姬子•启行开大后刷新',
              '助战技伤害按姬子•启行的面板和当时的增益算（其他人用 160% 全体 + 3×24% 弹射，姬子•启行自己用和额外发动的 200% + 4×32%，1 魂多 1 次）；【源能】和 6 魂源能的额外伤害没做']
F.rebuild(1510, E, rename=ren, off0=list(ren.keys()))

F.finish('姬子•启行助战技按官方规则', '''<li><b>2026-11-11（姬子•启行）</b>：tv 90（tools/fix90.py）。助战技按官方规则：<b>使用助战技占用这回合的行动</b>（官方说明“施放助战技也会消耗当前行动回合”；原来用完还会照常行动）。开拓同行角色用完立即获得 1 个额外回合（行迹列车的脉搏在轰鸣，2 魂起所有角色都有），并让姬子•启行进入【同行协议】：裁决（开拓者各命途、丹恒 / 丹恒•饮月 / 丹恒•腾荒、星期日）或歼破（三月七 / 三月七（巡猎）/ 长夜月、姬子、瓦尔特；对照按攻略站）。协议的增益自动生效（原来要手动开），并自动发动额外助战技：裁决是队友开 2 次大（1 魂 1 次），歼破是我方击中敌人累计 9 点充能（1 魂 6 点），单场最多 2 次（1 魂 3 次），姬子•启行开大后刷新。1 魂自己用助战技多 1 次弹射。对已有配置：勾了“助”的回合不再行动，行动顺序、战技点会变。</li>''',
'''2026-11-11：姬子•启行助战技 —— tv 90（tools/fix90.py）。新：supCast / supCharge / supProto、SUP.xLeft / cj / ch，助战技回合 rec.act = null。
  未改 / 存疑：开拓同行角色与协议的对照按攻略站（官方数据里没有）；“使用助战技视为姬子•启行施放了战技”没做；【源能】、6 魂源能额外伤害没做；额外回合里不能用助战技''')
