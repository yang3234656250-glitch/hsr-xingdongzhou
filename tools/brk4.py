"""击破：忆灵 / 召唤物的攻击也削韧。用法：先 python3 tools/build_tgh.py index.html <官方目录（含 AvatarServantSkillConfig.json）> <敌人数据目录>，再 python3 tools/brk4.py index.html
忆灵行动用 TGH[角色].m（忆灵技的削韧；DMGX.mem 写了 k "owner" 的用本体那个键，白厄的卡厄斯兰那）；不是忆灵的召唤物（账账、神君、浮元）行动用本体追加攻击的削韧 f。"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)
rep('''      if (!brkOn || !key || !who) return;
      const o = ownerOf(who) || who, T0 = o.kind === "ally" ? tplOf(o) : null; if (!T0) return;
      const tb = TGH[T0.id]; if (!tb) return;''', '''      if (!brkOn || !who || (!key && !who.sm)) return;
      const o = ownerOf(who) || who, T0 = o.kind === "ally" ? tplOf(o) : null; if (!T0) return;
      const tb = TGH[T0.id]; if (!tb) return;
      if (!key) { const ms = Object.values((DMGX.mem || {})[T0.id] || {})[0]; key = ms ? (ms.k === "owner" && ms.key ? ms.key : "m") : "f"; }   // 忆灵 / 召唤物自己的行动：忆灵技的削韧（m），不是忆灵的召唤物按本体追加攻击的削韧''')
rep('''(z[1] === "es" && key === "s2");''', '''(z[1] === "es" && key === "s2") || (z[1] === "m" && key === "m");''')
li = '<li><b>2026-11-11（忆灵 / 召唤物的攻击也削韧）</b>：忆灵行动按忆灵技的官方削韧值（衣匠 10 + 相邻 5、死龙全体 10、迷迷 5 + 全体 10、长夜 10、晴空乐手全体 10、小伊卡全体 10；卡厄斯兰那按白厄强化普攻），账账、神君、浮元行动按本体追加攻击的削韧值（神君只按 1 段算）。属性和击破特攻、超击破等增益都按本体。只在放了带韧性的敌人时有变化。</li>'
i = s.index('<li>', s.index('id="changelog"')); s = s[:i] + li + '\n' + ' ' * 14 + s[i:]
open(p, 'w', encoding='utf8').write(s); print('ok')
