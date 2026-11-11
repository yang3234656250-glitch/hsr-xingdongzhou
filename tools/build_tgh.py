"""生成削韧表 const TGH（每个角色每类技能的削韧值，官方 AvatarSkillConfig.ShowStanceList = [主目标, 全体, 相邻]，30 = 游戏里显示的 10 点）
并给 MON.m 每个敌人补韧性 tn（MonsterTemplateConfig.StanceBase × MonsterConfig.StanceModifyRatio，同名多个版本取最常见的）。
用法：python3 tools/build_tgh.py index.html <官方 json 目录（StarRailRes + AvatarSkillConfig*.json）> <敌人数据目录（MonsterConfig / MonsterTemplateConfig / TextMapCHS）>
"""
import sys, json, re, collections
p, off, mon = sys.argv[1:4]
s = open(p, encoding='utf-8').read()
def grab(name):
    m = re.search(r'\n\s*const ' + name + r' ?= ?(\{.*?\});\n', s); return m, json.loads(m.group(1))
mD, DMG = grab('DMG'); mM, MON = grab('MON'); mB, DB = grab('DB')
C = json.load(open(off + '/characters.json', encoding='utf-8')); SK = json.load(open(off + '/character_skills.json', encoding='utf-8'))
A = {}
for f in ('AvatarSkillConfig.json', 'AvatarSkillConfigLD.json'):
    for r in json.load(open(off + '/' + f, encoding='utf-8')):
        if r.get('Level') == 1: A[str(r['SkillID'])] = r
TY = {'Normal': 'b', 'BPSkill': 's', 'Ultra': 'u', 'Talent': 'f'}
TGH = {}; miss = []
for c in DB['chars']:
    cid = str(c['id'])
    if cid not in C: continue
    sk = C[cid]['skills']; out = {}
    def st(sid):   # 强化版 id（1 + 原 id）自己没有削韧值时用原技能的
        for k in (sid, sid[1:] if len(sid) == 7 and sid.startswith('1' + cid) else None):
            v = [int(round(x.get('Value', 0))) for x in (A.get(k) or {}).get('ShowStanceList') or []] if k else []
            if any(v): return v
        return []
    names = collections.defaultdict(list)
    for sid in sk: names[SK[sid]['name']].append(sid)
    for key, e in (DMG.get(cid) or {}).items():
        if not isinstance(e, dict) or 'v' not in e: continue
        ids = names.get(e.get('n')) or []
        if not ids:   # 倍率表里的名字带了“（强化版）”之类的后缀：去掉括号再按包含关系找
            base = re.sub(r'[（(].*$', '', e.get('n') or '').strip()
            ids = [i for i in sk if base and (SK[i]['name'] == base or base in SK[i]['name'] or SK[i]['name'] in base)]
        ids = sorted(ids, key=lambda x: (not x.startswith('1' + cid), x))   # 强化版优先
        cand = [st(i) for i in ids if any(st(i))]
        v = (max(cand, key=sum) if key.endswith('2') else cand[0]) if cand else None   # 同名的普通版 / 强化版：b、s、u 用第一条（普通版或 1 开头的强化版），b2 / s2 / u2 用削韧最多的那条
        if v is None and key in ('b', 's', 'u'):   # 名字对不上：按技能类型找（强化版优先）
            ids = sorted([i for i in sk if TY.get(SK[i].get('type')) == key], key=lambda x: (not x.startswith('1' + cid), x))
            v = next((st(i) for i in ids if any(st(i))), None)
        if v and any(v): out[key] = v
        elif key in ('b', 's', 'u', 'b2', 's2', 'u2', 'f'): miss.append((cid, c['name'], key, e.get('n')))
    if out: TGH[cid] = out
print('TGH 角色', len(TGH), '没找到削韧的条目', len(miss)); [print('  ', m) for m in miss]
# 敌人韧性
TM = json.load(open(mon + '/TextMapCHS.json', encoding='utf-8')); T = {t['MonsterTemplateID']: t for t in json.load(open(mon + '/MonsterTemplateConfig.json', encoding='utf-8'))}
norm = lambda x: re.sub(r'[\s·•・]', '', re.sub(r'<[^>]+>', '', x))
bn = collections.defaultdict(list)
for m in json.load(open(mon + '/MonsterConfig.json', encoding='utf-8')):
    t = T.get(m['MonsterTemplateID']); v = ((t or {}).get('StanceBase') or {}).get('Value')
    if v is None: continue
    bn[norm(TM.get(str(m['MonsterName']['Hash']), ''))].append(int(round(v * m.get('StanceModifyRatio', {}).get('Value', 1))))
n0 = 0
for m in MON['m']:
    v = bn.get(norm(m['n']))
    if v: m['tn'] = collections.Counter(v).most_common(1)[0][0]
    else: m.pop('tn', None); n0 += 1
print('敌人', len(MON['m']), '没有韧性数据', n0)
dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
s = s[:mM.start(1)] + dump(MON) + s[mM.end(1):]
line = 'const TGH = ' + dump(TGH) + ';   // 削韧表：tools/build_tgh.py 生成，[主目标, 全体, 相邻]，30 = 游戏里的 10 点\n'
s = re.sub(r'\n[ \t]*const TGH ?= ?\{[^\n]*', '', s)   # 去掉旧的
m3 = re.search(r'\n(\s*)const DMG ?= ?', s); s = s[:m3.start() + 1] + m3.group(1).replace('\n', '') + line + s[m3.start() + 1:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
