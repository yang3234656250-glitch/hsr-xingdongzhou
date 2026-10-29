"""生成 index.html 里的 const DMGX = {...}（一行）。
数据来源：StarRailRes index_new/cn 的 characters / character_skills / character_ranks。
用法：python3 tools/build_dmgx.py <放这三个 json 的目录> index.html  → 打印那一行
- adj：DMG 表里扩散技能缺了“相邻目标”倍率的，按官方描述里“相邻目标…#N”补上（运行时 DMG 的 adj 为空才用它）
- lvup：每个角色几魂给 普攻(b) / 战技(s) / 终结技(u) / 天赋(t) / 忆灵技(m) 加等级
- mem：忆灵 / 召唤物行动的伤害（按官方忆灵技参数，满级 6 级，星魂 +1 → 7 级；每项给 [6 级, 7 级, 几魂升级]）
"""
import json, sys, os, re
d = sys.argv[1]
S = json.load(open(os.path.join(d, 'character_skills.json')))
C = json.load(open(os.path.join(d, 'characters.json')))
R = json.load(open(os.path.join(d, 'character_ranks.json')))

RANK = {}               # 技能 id → 几魂 +1 级
for cid, c in C.items():
    for rid in c['ranks']:
        for x in R[rid].get('level_up_skills') or []:
            RANK.setdefault(str(x['id']), int(str(rid)[-1]))

def p(sid, i):          # 第 i 个参数：[6 级, 7 级, 几魂升到 7 级]（忆灵技满级 6，星魂 +1）
    ps = S[sid]['params']
    return [round(ps[5][i], 6), round(ps[min(6, len(ps) - 1)][i], 6), RANK.get(sid, 9)]

lvup = {}
for cid, c in C.items():
    o = {}
    for rid in c['ranks']:
        r = R[rid]; n = int(str(rid)[-1])
        for x in r.get('level_up_skills') or []:
            sid = str(x['id'])
            if len(sid) == 7 and sid.startswith('1'):        # 忆灵技 / 忆灵天赋
                o.setdefault('m', n); continue
            k = {'01': 'b', '02': 's', '03': 'u', '04': 't'}.get(sid[-2:])
            if k: o.setdefault(k, n)
    if o: lvup[cid] = o

mem = {
  # 阿格莱雅 衣匠：刺纹之陷（扩散，衣匠攻击力 = 阿格莱雅攻击力）
  '1402': {'garment': {'k': 'std', 'n': '刺纹之陷', 'v': p('1140201', 0), 'adj': p('1140201', 1), 'tg': 2, 'stat': 'oatk'}},
  # 开拓者•记忆 迷迷：坏人！麻烦！（4 次随机单体 + 全体），充能满时的【我会！帮你！】不造成伤害（这里不区分）
  '8007': {'mimi': {'k': 'std', 'n': '坏人！麻烦！', 'v': p('1800701', 2), 'rnd': [round(p('1800701', 0)[0] * 4, 6), round(p('1800701', 0)[1] * 4, 6), RANK.get('1800701', 9)], 'tg': 3, 'stat': 'oatk'}},
  '8008': {'mimi': {'k': 'std', 'n': '坏人！麻烦！', 'v': p('1800701', 2), 'rnd': [round(p('1800701', 0)[0] * 4, 6), round(p('1800701', 0)[1] * 4, 6), RANK.get('1800701', 9)], 'tg': 3, 'stat': 'oatk'}},
  # 知更鸟•晴歌 晴空乐手：叽叽啾啾四重奏（全体，晴空乐手生命上限）
  '1512': {'band': {'k': 'std', 'n': '叽叽啾啾四重奏', 'v': p('1151201', 1), 'tg': 3, 'stat': 'mhp'}},
  # 昔涟 德谬歌：花与箭的舞曲（全体，德谬歌生命上限）；对别人施放此诗时不造成伤害
  '1415': {'demiurge': {'k': 'dem', 'n': '花与箭的舞曲', 'v': p('1141501', 0), 'tg': 3, 'stat': 'mhp'}},
  # 长夜月 长夜：追忆，蹁跹，如雨（单体 + 每 4 点忆质额外），忆质 ≥16 时 迷梦，流失，如露（每点忆质 主目标 / 其他目标）
  '1413': {'evernight': {'k': 'ev', 'n': '追忆，蹁跹，如雨', 'n2': '迷梦，流失，如露', 'v': p('1141301', 0), 'per': p('1141301', 1), 'perN': p('1141301', 2)[0],
           'mv': p('1141307', 0), 'madj': p('1141307', 1), 'need': p('1141307', 2)[0], 'stat': 'mhp'}},
  # 遐蝶 死龙：燎尽黯泽的焰息（全体，遐蝶生命上限，连续发动倍率依次提高），自爆时 灼掠幽墟的晦翼（随机单体 × 次数）；
  # 没有连续发动记录时按 擘裂冥茫的爪痕（全体）
  '1407': {'dragon': {'k': 'dragon', 'n': '燎尽黯泽的焰息', 'fl': [p('1140702', 1), p('1140702', 2), p('1140702', 3)],
           'wing': p('1140706', 0), 'wingN': p('1140706', 1)[0], 'claw': p('1140701', 0), 'stat': 'ohp'}},
  # 风堇 小伊卡：乌云乌云快走开！（全体，按风堇与小伊卡累计治疗数值的 %）
  '1409': {'ika': {'k': 'ika', 'n': '乌云乌云快走开！', 'v': p('1140901', 0), 'tg': 3}},
  # 白厄 卡厄斯兰那：行动按 创生•血棘渡亡（本体的强化普攻）
  '1408': {'khaslana': {'k': 'owner', 'key': 'b2'}},
}
adj = {}
if len(sys.argv) > 2:
    html = open(sys.argv[2], encoding='utf-8').read()
    DMG = json.loads(re.search(r'const DMG=(\{.*?\});\n', html).group(1))
    for k, dd in DMG.items():
        for kk, v in dd.items():
            if v['tg'] != 2 or any(v.get('adj') or []) or k not in C: continue
            for sid in C[k]['skills']:
                if S[sid]['name'] != v['n']: continue
                m = re.search(r'相邻目标[^。#]*?#(\d)\[', S[sid]['desc'])
                if m:
                    i = int(m.group(1)) - 1
                    adj.setdefault(k, {})[kk] = [round(q[i], 6) for q in S[sid]['params']]
                    break
print('const DMGX=' + json.dumps({'lvup': lvup, 'mem': mem, 'adj': adj}, ensure_ascii=False, separators=(',', ':')) + ';')
