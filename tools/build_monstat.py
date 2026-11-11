"""给敌人数据加攻击力、生命值、技能倍率（官方 MonsterConfig / MonsterTemplateConfig / EliteGroup / HardLevelGroup / MonsterSkillConfig）。
用法：python3 tools/build_monstat.py index.html <敌人数据目录：MonsterConfig.json、MonsterTemplateConfig.json、MonsterSkillConfig.json、EliteGroup.json、HardLevelGroup.json、TextMapCHS.json>
写入 MON.hl = [[攻击倍数, 生命倍数], …]（等级 1 起，等级成长组 1——现有敌人全是这一组）；MON.m[].a / .h = 1 级时的攻击力 / 生命值（基础值 × 怪物修正 × 精英组），
MON.m[].x = {技能下标: [主目标倍率, 相邻 / 其他目标倍率, 段数]}（ParamList 第 1 个数 = 主目标倍率；扩散 / 横扫第 2 个数比第 1 个小时是相邻倍率；弹射 / 扫射按段数）。
同名敌人取最常见的一组配置。"""
import sys, json, re, collections
P, D = sys.argv[1], sys.argv[2]
L = lambda n: json.load(open(f'{D}/{n}.json', encoding='utf-8'))
TM = L('TextMapCHS'); T = lambda h: TM.get(str(h['Hash'])) if isinstance(h, dict) and 'Hash' in h else None
MC, MT = L('MonsterConfig'), {r['MonsterTemplateID']: r for r in L('MonsterTemplateConfig')}
EG = {r['EliteGroup']: r for r in L('EliteGroup')}
HL = sorted([r for r in L('HardLevelGroup') if r['HardLevelGroup'] == 1], key=lambda r: r['Level'])
MS = {r['SkillID']: r for r in L('MonsterSkillConfig')}
V = lambda d, k, dv=1: (d.get(k) or {}).get('Value', dv)
s = open(P, encoding='utf-8').read()
m0 = re.search(r'\n(\s*)const MON ?= ?(\{.*?\});\n', s); MON = json.loads(m0.group(2))
assert all(m['HardLevelGroup'] == 1 for m in MC)
MON['hl'] = [[round(V(r, 'AttackRatio'), 6), round(V(r, 'HPRatio'), 6)] for r in HL]
assert [r['Level'] for r in HL] == list(range(1, len(HL) + 1))
byName = collections.defaultdict(list)
for m in MC:
    nm = T(m['MonsterName'])
    t = MT.get(m['MonsterTemplateID'])
    if not nm or not t: continue
    eg = EG.get(m['EliteGroup'], {})
    a = round(V(t, 'AttackBase', 0) * V(m, 'AttackModifyRatio') * V(eg, 'AttackRatio'), 4)
    h = round(V(t, 'HPBase', 0) * V(m, 'HPModifyRatio') * V(eg, 'HPRatio'), 4)
    byName[nm].append((a, h, tuple(m.get('SkillList') or [])))
def ratios(sk, tag):
    pl = [p['Value'] for p in sk.get('ParamList') or []]
    d = re.sub(r'<[^>]+>', '', T(sk.get('SkillDesc')) or '') if sk.get('SkillDesc') else ''
    if not pl or sk.get('DamageType') in (None, 'None') or '伤害' not in d: return None
    x = pl[0]
    if tag in ('弹射', '扫射'):
        n = next((v for v in pl[1:] if v >= 2 and float(v).is_integer()), 1)
        return [round(x, 4), round(x, 4), int(n)]
    x2 = pl[1] if tag in ('扩散',) and len(pl) > 1 and pl[1] < x else x
    return [round(x, 4), round(x2, 4), 1]
hit = miss = 0
for m in MON['m']:
    L0 = byName.get(m['n'])
    if not L0: miss += 1; continue
    a, h, sl = collections.Counter(L0).most_common(1)[0][0]
    m['a'], m['h'] = a, h
    idx = {}
    for k in list(m.get('k') or []) + list(m.get('p') or []):
        idx.setdefault(MON['sk'][k]['n'], []).append(k)
    xr = {}
    for sid in sl:
        sk = MS.get(sid)
        if not sk: continue
        nm = T(sk.get('SkillName'))
        for k in idx.get(nm, []):
            r = ratios(sk, MON['sk'][k].get('t'))
            if r and str(k) not in xr: xr[str(k)] = r
    if xr: m['x'] = xr
    hit += 1
print('敌人', hit, '没对上', miss, '有技能倍率', sum(1 for m in MON['m'] if m.get('x')))
s = s[:m0.start()] + '\n' + m0.group(1) + 'const MON = ' + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + ';\n' + s[m0.end():]
open(P, 'w', encoding='utf-8').write(s)
print('ok')
