"""对照官方技能参数修 DMG 表里错的条目（2026-10-30 复查）。用法：python3 tools/fix_dmg.py <官方 json 目录> index.html"""
import json, re, sys
O = sys.argv[1].rstrip('/') + '/'; P = sys.argv[2]
SK = json.load(open(O + 'character_skills.json')); CH = json.load(open(O + 'characters.json'))
s = open(P, encoding='utf-8').read(); m = re.search(r'const DMG=(\{.*?\});\n', s); D = json.loads(m.group(1))
def params(cid, name, sid=None):
    x = SK[sid] if sid else [SK[k] for k in CH[cid]['skills'] if SK[k]['name'] == name][0]
    return x['params']
def setv(cid, k, f, sid=None, **kw):
    e = D[cid][k]; ps = params(cid, e['n'], sid)
    e['v'] = [round(f(p), 4) for p in ps]
    for a, b in kw.items():
        if callable(b): e[a] = [round(b(p), 4) for p in ps]
        else: e[a] = b
FIX = [
 ('1001', 'u', lambda p: p[0], {}),                      # 冻结的附加伤害不算进开大
 ('1004', 's', lambda p: p[0] * 5, {'tg': 0, 'rnd': []}),    # 强化版：主目标 + 额外 4 次（模板用强化版）
 ('1005', 'u', lambda p: p[0], {}),                      # 引爆触电是持续伤害，不算
 ('1009', 's', lambda p: p[0] * 5, {'tg': 0}),            # 主目标 + 额外 4 次
 ('1103', 's', lambda p: p[0], {}),
 ('1104', 's', lambda p: p[0], {}),
 ('1109', 's', lambda p: p[0], {}),
 ('1205', 'f', lambda p: p[3], {}),                      # 生命上限部分（攻击力部分没算）
 ('1206', 's', lambda p: p[0], {}),                      # 剑势是概率附加伤害
 ('1209', 'f', lambda p: p[3], {}),                      # 冻结的附加伤害不算
 ('1210', 's', lambda p: p[0], {}),
 ('1222', 's', lambda p: p[0], {}),
 ('1222', 'u', lambda p: p[0], {}),
 ('1223', 'f', lambda p: p[2], {}),                      # 附加伤害改由额外伤害表算
 ('1321', 'u', lambda p: p[0], {'tg': 0}),               # 由敌方全体均分
 ('1403', 'u', lambda p: p[0], {}),                      # 结界附加伤害改由额外伤害表算
 ('1408', 'u', lambda p: p[0], {'tg': 0}),               # 由敌方全体均分
 ('1415', 'b2', lambda p: p[0], {'tg': 3, 'rnd': lambda p: p[2]}),  # 全体 #1 + 主目标 #3（放进 rnd）
 ('1505', 'u', lambda p: p[0], {'rnd': lambda p: p[1] * p[2]}),
 ('1505', 'f', lambda p: p[0], {'tg': 3}),
 ('1508', 'u', lambda p: p[0], {'tg': 4, 'adj': lambda p: p[1]}),
 ('1508', 's2', lambda p: p[0], {'tg': 3, 'rnd': lambda p: p[2] if len(p) > 2 else p[0]}),
 ('1509', 'f', lambda p: p[0], {}),                      # 只算吉尔伽美什自己那段（Saber 的那段按 Saber 卡）
 ('1508', 'f', lambda p: p[0], {}),                      # 只算远坂凛自己那段
 ('1222', 'f', lambda p: p[1], {'rnd': lambda p: p[7]}),             # 全体 + 随机单体一次
 ('1401', 's2', lambda p: p[0] * 3 + p[2], {'tg': 2, 'adj': lambda p: p[0] * 2 + p[2]}),   # 主目标 3 次 + 最后全体；相邻 2 次 + 全体
 ('1308', 'u', lambda p: p[5], {'tg': 4, 'adj': lambda p: p[6]}),   # 主目标最多 372%、其他目标最多 300%
 ('8001', 'u', lambda p: p[0], {}), ('8002', 'u', lambda p: p[0], {}),   # 按【全胜•再见安打】单体
 ('8005', 's', lambda p: p[0] * 5, {}), ('8006', 's', lambda p: p[0] * 5, {}),
]
for cid, k, f, kw in FIX:
    sid = '1100402' if (cid, k) == ('1004', 's') else None
    e = D[cid][k]; ps = params(cid, e['n'], sid)
    e['v'] = [round(f(p), 4) for p in ps]
    for a, b in kw.items():
        if a == 'rnd' and b is None:
            e['rnd'] = [round(p[0], 4) for p in ps]   # 1415 强普：单体那段
        elif callable(b): e[a] = [round(b(p), 4) for p in ps]
        else: e[a] = b
    print(cid, k, e['n'], 'Lv10' if len(e['v']) > 9 else 'Lv6', e['v'][min(9, len(e['v']) - 1)] if len(e['v']) > 9 else e['v'][5], {a: (e[a][min(9, len(e[a]) - 1)] if isinstance(e.get(a), list) and e[a] else e.get(a)) for a in kw})
# 1503 真珠强普：按官方参数（6 级 100% 防御力）
e = D['1503']['b2']; ps = params('1503', e['n']); e['v'] = [round(p[0], 4) for p in ps]; e.pop('br', None)
# 不造成伤害的技能（护盾 / 增益）清零；附加伤害改由额外伤害表算
for cid, k in [('1001', 's'), ('1104', 'u'), ('1304', 's'), ('1414', 's'), ('1224', 's'), ('1202', 's'), ('1314', 's'), ('1309', 'u'), ('1503', 'u')]:
    if k in D.get(cid, {}): D[cid][k]['v'] = [0.0] * len(D[cid][k]['v']); D[cid][k].pop('rnd', None)
# 1408 卡厄斯兰那战技：敌方全体 + 随机
D['1408']['s2']['tg'] = 3
s = s[:m.start(1)] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
open(P, 'w', encoding='utf-8').write(s); print('ok')
