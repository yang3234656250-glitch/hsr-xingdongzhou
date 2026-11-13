"""tv 100：开场 / 直接伤害。新效果类型 hitd（直接造成一次伤害）：字段 hk（hitK）= 伤害表里的键；
记录和助战技一样进 dotRecs（r.sup = 键），按施放者当时的增益算、能暴击。伤害表新键 q = 秘技。
Archer、吉尔伽美什秘技进入战斗后的 200% 攻击力全体伤害。"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix, r4
F = Fix(sys.argv[1], 100, sys.argv[2])
C, has = F.C, F.has
F.rep('''      if (x.stx) e.stX = x.stx;''', '''      if (x.hk) e.hitK = x.hk;   // 直接伤害用伤害表的哪个键
      if (x.stx) e.stX = x.stx;''')
F.rep('''      if (eff.type === "shield" && SHM.includes(eff.mode)) { doShield(eff, src, srcColor, val); return; }''', '''      if (eff.type === "hitd") {   // 直接造成一次伤害（秘技进战伤害）：记录按伤害表的键算
        const o = src ? ownerOf(src) : null; if (!o || !eff.hitK) return;
        const e0 = U.find(z => z.kind === "enemy" && !z.gone);
        const r = { t, uid: o.id, en: e0 ? e0.id : null, k: healLabel(eff) === "治疗" ? "直接伤害" : healLabel(eff), sup: eff.hitK, db: dbSnap(o), edb: edbSnap(e0), eAll: edbAll(), seq: seq++, ebk: ebkNow() }; dotRecs.push(r);
        addLog(`${o.name}「${r.k}」造成伤害`, false, srcColor, o.id); log[log.length - 1].dd = [r];
        return;
      }
      if (eff.type === "shield" && SHM.includes(eff.mode)) { doShield(eff, src, srcColor, val); return; }''')
F.rep('''z: "z", z2: "z" };''', '''z: "z", z2: "z", q: "q" };''')
F.rep('''f: "t", z: "t", z2: "t" };''', '''f: "t", z: "t", z2: "t", q: "b" };''')
F.rep('''const TYPEL = { advance: "拉条",''', '''const TYPEL = { hitd: "直接伤害", advance: "拉条",''')
def find(L, pre):
    R = [e for e in L if (e.get('n') or '').startswith(pre)]; assert len(R) == 1, (pre, [e.get('n') for e in R]); return R[0]
has('101507', '进入战斗后对敌方全体造成等同于Archer#1[i]%攻击力的量子属性伤害'); has('150907', '进入战斗后对敌方全体造成等同于吉尔伽美什#2[i]%攻击力的雷属性伤害')
for cid, pre, n1, n2 in ((1015, '秘技千里眼', '秘技千里眼：进入战斗后获得 1 点充能（用了秘技再启用）', '秘技千里眼：进入战斗后对敌方全体造成 200% 攻击力的伤害（用了秘技再启用）'),
                         (1509, '秘技天之锁', '秘技天之锁：进入战斗后立即获得 3 点【兴致】（用了秘技再启用）', '秘技天之锁：进入战斗后对敌方全体造成 200% 攻击力的伤害（用了秘技再启用）')):
    c = C[cid]; E = c['eff']; x = find(E, pre); o = x['n']; x['n'] = n1
    E.insert(E.index(x) + 1, dict(y='hitd', t='start', tg='enemies', hk='q', v=0, off=1, n=n2))
    F.DMG[str(cid)]['q'] = {"v": [2.0] * 15, "adj": [], "rnd": [], "tg": 3, "el": 0, "stat": "atk", "n": "秘技进战伤害", "max": 15}
    F.rebuild(cid, E, rename={o: n1})
F.finish('秘技进战伤害', '''<li><b>2026-11-13</b>：tv 100（tools/fix100.py）。新效果类型“直接伤害”：Archer、吉尔伽美什的秘技进入战斗后对敌方全体 200% 攻击力的伤害（和秘技的其他效果一样默认关，用了秘技再启用）。</li>''',
'''2026-11-13：秘技进战伤害 —— tv 100（tools/fix100.py）。新：效果类型 hitd、字段 hk、伤害表键 q。
  未改 / 存疑：其他角色的秘技进战伤害大多没有做成效果；编辑器的效果类型下拉里没有“直接伤害”（只在模板里用）''')
