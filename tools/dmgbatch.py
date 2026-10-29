"""伤害增益分批补效果的公共部分：往 DB 里加效果，生成 TPLFIX{tv} / EQFIX{tv}，把 migrateTpl 的版本号 +1。
每批脚本：from dmgbatch import run, D; run(path, TV, BASE, EID, LCADD, RELADD, label)"""
import re, json
D = lambda **k: dict(y='dbuf', **k)

def run(P, TV, BASE, EID, LCADD, RELADD, label):
    s = open(P, encoding='utf-8').read()
    assert f'if (s.tv >= {TV - 1}) return;' in s, '版本号不对，先确认 tv'
    m = re.search(r'const DB = (\{.*?\});\n', s); DB = json.loads(m.group(1))
    C = {c['id']: c for c in DB['chars']}; LC = {l['id']: l for l in DB['lcs']}; RL = {r['id']: r for r in DB['relics']}
    FIX = {}
    for cid, L in BASE.items():
        have = {e.get('n') for e in C[cid]['eff']}
        for x in L: assert x['n'] not in have, ('重复说明', cid, x['n'])
        C[cid]['eff'].extend(L)
        FIX[str(cid)] = {'drop': [], 'map': {}, 'trig': {}, 'add': [x['n'] for x in L], 'sm': {}}
    for cid, R in EID.items():
        for r, L in R.items():
            ent = next((e for e in C[cid]['eid'] if e['r'] == r), None)
            if not ent: ent = {'r': r, 'eff': [], 'notes': []}; C[cid]['eid'].append(ent); C[cid]['eid'].sort(key=lambda e: e['r'])
            ent['eff'].extend(L)
        FIX.setdefault(str(cid), {'drop': [], 'map': {}, 'trig': {}, 'add': [], 'sm': {}})
    for lid, L in LCADD.items(): LC[lid]['eff'].extend(L)
    for (rid, part), L in RELADD.items(): RL[rid].setdefault(part, {'eff': [], 'notes': []})['eff'].extend(L)
    EQ = {'lc': sorted(LCADD), 'rel': sorted({r for r, _ in RELADD})}
    s = s[:m.start(1)] + json.dumps(DB, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
    a = re.search(rf'  const fixTpl{TV - 1} = .*\n', s)
    s = s[:a.end()] + (f'  // tv {TV}：{label}\n  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + f';\n  const EQFIX{TV} = ' + json.dumps(EQ)
        + f';\n  const fixTpl{TV} = s => {{ fixTpl(s, TPLFIX{TV}); for (const u of s.units) if (u.kind === "ally" && !u.sm && !TPLFIX{TV}[String((tplOf(u) || {{}}).id)] && (EQFIX{TV}.lc.includes(u.lc) || [u.rA, u.rB, u.rP].some(r => EQFIX{TV}.rel.includes(r)))) applyEquip(u); }};\n') + s[a.end():]
    def rep(x, y):
        nonlocal s
        assert s.count(x) == 1, (x, s.count(x)); s = s.replace(x, y)
    rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
    rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'if (!(s.tv >= {TV - 1})) fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
    rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep2; }} }}\n    s.tv = {TV - 1};', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep2; }} }}\n    s.tv = {TV};')
    rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
    open(P, 'w', encoding='utf-8').write(s)
    print('ok tv', TV, {k: len(v['add']) for k, v in FIX.items()}, EQ)
