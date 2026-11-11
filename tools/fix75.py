"""tv 75：远坂凛 1508 —— 战技点已满时的“恢复”要不要算进【宝石能量】做成开关（原文没写，查不到结论，默认不算）。
用法：python3 tools/fix75.py index.html <官方 json 目录>
引擎：spChg 触发的效果带 ovf（字段 spOvf）= 只在“恢复时战技点已满、实际没增加”的那几点上触发；不带的照旧按实际变化。"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from fixlib import Fix
F = Fix(sys.argv[1], 75, sys.argv[2])
C, has = F.C, F.has
NO = 'e => !e.spOvf'
F.rep('''{ const s0 = sp; sp = Math.min(spMax, sp + 1); if (sp > s0) teamFire("spChg", u); }''', '''{ const s0 = sp; sp = Math.min(spMax, sp + 1); if (sp > s0) teamFire("spChg", u, e => !e.spOvf); else teamFire("spChg", u, e => e.spOvf); }''')
F.rep('''teamFire("spUse", u); teamFire("spChg", u); }''', '''teamFire("spUse", u); teamFire("spChg", u, e => !e.spOvf); }''')
F.rep('''teamFire("spUse", who); } teamFire("spChg", who); } } finally { spDepth--; } }''', '''teamFire("spUse", who); } teamFire("spChg", who, e => !e.spOvf); } } finally { spDepth--; } }
          { const ov = eff.mode !== "to" && eff.mode !== "rec" && v > 0 ? Math.round(s0 + v - spMax) : 0;   // 恢复时溢出的点数：只触发带 spOvf 的效果（远坂凛“已满时的恢复也算”开关）
            if (ov > 0 && who && who.kind === "ally" && spDepth < 2) { spDepth++; try { for (let i = 0; i < Math.min(ov, Math.round(v)); i++) teamFire("spChg", who, e => e.spOvf); } finally { spDepth--; } } }''')
F.rep('''      if (x.nw) e.nw = 1;''', '''      if (x.ovf) e.spOvf = 1;   // spChg：只在战技点已满的“恢复”上触发
      if (x.nw) e.nw = 1;''')
has('150804', '每消耗或恢复1点战技点就使远坂凛获得1点【宝石能量】')
c = C[1508]
F.rebuild(1508, list(c['eff']) + [dict(y='count', t='spChg', aw='all', tg='self', v=1, ovf=1, off=1, n='天赋宝石魔术（可选）：战技点已满时队友“恢复”的战技点（实际没增加）也让远坂凛获得 1 点【宝石能量】——原文没写满了算不算，默认不算；游戏里确认会算就启用这条')])
F.finish('远坂凛：战技点已满时的恢复算不算做成开关', '''<li><b>2026-11-11（远坂凛：战技点已满时的“恢复”算不算，做成开关）</b>：tv 75（tools/fix75.py）。天赋原文只写“每消耗或恢复 1 点战技点 +1【宝石能量】”，没写战技点已满时的恢复算不算，查不到确切结论。默认和以前一样不算；远坂凛的效果里多了一条默认关闭的“战技点已满时的恢复也算”，游戏里确认会算就打开。已有方案不变。</li>''',
'''2026-11-11：远坂凛（1508）战技点溢出 —— tv 75（tools/fix75.py）。新：spChg 效果的 ovf。
  未改 / 存疑：溢出的恢复只给【宝石能量】做了开关，暴击伤害增益没做对应的；同谐主 E6（战技额外伤害次数 +2）按每次伤害回 6 点能量算（共 7 次 42 点），原文没单独写回能。''')
