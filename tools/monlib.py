"""敌人数据公共函数（从 tools/mon149.py 抽出来，算法完全相同，每日敌人任务用）。
用法：from monlib import Mon; M = Mon(官方 ExcelOutput 目录); o = M.build(MON, MonsterID, ...)
目录里要有 MonsterConfig MonsterTemplateConfig MonsterSkillConfig EliteGroup HardLevelGroup TextMapCHS（.json），
来源 https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/ 和 TextMap/。

MON 条目字段（同 mon149.py 开头的说明）：
  n 名字；r 模板 Rank（BigBoss B / LittleBoss L / Elite E / Minion、MinionLv2 M）；s = SpeedBase × SpeedModifyRatio + SpeedModifyValue；
  w = StanceWeakList 首字；d = InitialDelayRatio（≠1 才写）；tn = StanceBase × StanceModifyRatio；
  k = 有名字、类型不是“天赋”的技能；p = 有名字的天赋；q = 默认出招；a / h = 攻击 / 生命基础 × 修正 × 怪物自己的 EliteGroup；x = 技能倍率。
（2026-11-20 敌人任务写的；定时任务当时推不上仓库，2026-11-21 从 claude.ai 页面合回仓库时按项目文档补进来）
"""
import json, re

WK = {'Physical': '物', 'Fire': '火', 'Ice': '冰', 'Thunder': '雷', 'Wind': '风', 'Quantum': '量', 'Imaginary': '虚'}
RK = {'BigBoss': 'B', 'LittleBoss': 'L', 'Elite': 'E', 'Minion': 'M', 'MinionLv2': 'M'}


def num(v): return int(v) if float(v).is_integer() else round(v, 4)


class Mon:
    def __init__(self, D):
        L = lambda n: json.load(open(f'{D}/{n}.json', encoding='utf-8'))
        self.L = L
        self.TM = L('TextMapCHS')
        self.MC = {m['MonsterID']: m for m in L('MonsterConfig')}
        self.MT = {m['MonsterTemplateID']: m for m in L('MonsterTemplateConfig')}
        self.MS = {r['SkillID']: r for r in L('MonsterSkillConfig')}
        self.EG = {r['EliteGroup']: r for r in L('EliteGroup')}

    def T(self, h):
        return self.TM.get(str(h['Hash'])) if isinstance(h, dict) and 'Hash' in h else (h if isinstance(h, str) else None)

    @staticmethod
    def V(d, k, dv=1): return (d.get(k) or {}).get('Value', dv)

    def name(self, mid): return re.sub(r'<[^>]+>', '', self.T(self.MC[mid]['MonsterName']) or '')

    @staticmethod
    def fmt(v, pct):
        if pct: x = round(v * 100, 4); return (str(int(x)) if float(x).is_integer() else str(x)) + '%'
        return str(int(v)) if float(v).is_integer() else str(round(v, 4))

    def desc(self, sk):
        d = self.T(sk.get('SkillDesc')) or ''
        pl = [p['Value'] for p in sk.get('ParamList') or []]
        d = re.sub(r'#(\d+)\[([^\]]*)\](%?)', lambda m: self.fmt(pl[int(m.group(1)) - 1] if int(m.group(1)) - 1 < len(pl) else 0, m.group(3) == '%'), d)
        return re.sub(r'<[^>]+>', '', d)

    def ratios(self, sk, tag):   # 和 tools/build_monstat.py 一样
        pl = [p['Value'] for p in sk.get('ParamList') or []]
        d = re.sub(r'<[^>]+>', '', self.T(sk.get('SkillDesc')) or '') if sk.get('SkillDesc') else ''
        if not pl or sk.get('DamageType') in (None, 'None') or '伤害' not in d: return None
        x = pl[0]
        if tag in ('弹射', '扫射'):
            n = next((v for v in pl[1:] if v >= 2 and float(v).is_integer()), 1)
            return [round(x, 4), round(x, 4), int(n)]
        x2 = pl[1] if tag in ('扩散',) and len(pl) > 1 and pl[1] < x else x
        return [round(x, 4), round(x2, 4), 1]

    def rawspd(self, mc):
        t = self.MT[mc['MonsterTemplateID']]; V = self.V
        return V(t, 'SpeedBase', 0) * V(mc, 'SpeedModifyRatio') + V(mc, 'SpeedModifyValue', 0)

    def stats(self, mid):
        """a / h / tn（同 build_monstat.py）"""
        mc = self.MC[mid]; t = self.MT[mc['MonsterTemplateID']]; eg = self.EG.get(mc['EliteGroup'], {}); V = self.V
        return {'tn': num(V(t, 'StanceBase', 0) * V(mc, 'StanceModifyRatio')),
                'a': round(V(t, 'AttackBase', 0) * V(mc, 'AttackModifyRatio') * V(eg, 'AttackRatio'), 4),
                'h': round(V(t, 'HPBase', 0) * V(mc, 'HPModifyRatio') * V(eg, 'HPRatio'), 4)}

    def build(self, MON, mid, name=None, qfix=None, nox=(), ht=None):
        """按 MonsterID 生成一个 MON 条目，技能追加到 MON.sk 末尾。qfix：[(蓄力技能名, 它点名的招)]；nox：不写倍率的技能名；ht：{技能名: 选目标用的标签}"""
        mc = self.MC[mid]; t = self.MT[mc['MonsterTemplateID']]; V = self.V; T = self.T
        o = {'n': name or self.name(mid), 'r': RK[t['Rank']], 's': num(self.rawspd(mc)),
             'w': ''.join(WK[x] for x in mc.get('StanceWeakList', []))}
        if V(t, 'InitialDelayRatio', 1) != 1: o['d'] = V(t, 'InitialDelayRatio', 1)
        act, pas, xr = [], [], {}
        for sid in mc.get('SkillList', []):
            sk = self.MS.get(sid)
            if not sk or not T(sk.get('SkillName')): continue
            typ, tag = T(sk.get('SkillTypeDesc')), T(sk.get('SkillTag'))
            d = self.desc(sk)
            e = {'n': T(sk['SkillName']), 't': tag, 'sp': num(V(sk, 'SPHitBase', 0)), 'd': d if len(d) <= 110 else d[:110] + '…'}
            if ht and e['n'] in ht: e['ht'] = ht[e['n']]
            i = len(MON['sk']); MON['sk'].append(e)
            (pas if typ == '天赋' else act).append(i)
            if typ != '天赋' and e['n'] not in nox:
                r = self.ratios(sk, tag)
                if r: xr[str(i)] = r
        o['k'] = act
        if pas: o['p'] = pas
        q = list(act)
        for a, b in qfix or []:
            ia = next(i for i in q if MON['sk'][i]['n'] == a); ib = next(i for i in q if MON['sk'][i]['n'] == b)
            assert MON['sk'][ia]['t'] == '蓄力' and f'【{b}】' in MON['sk'][ia]['d'], (a, b)
            q.remove(ib); q.insert(q.index(ia) + 1, ib)
        o['q'] = q
        o.update(self.stats(mid))
        if xr: o['x'] = xr
        return o


def page(P):
    raw = open(P, encoding='utf-8', newline='').read()
    return raw.replace('\r\n', '\n'), '\r\n' in raw[:200000]


def grab(s, name, op):
    m = re.search(r'\n(\s*)const ' + name + r' ?= ?(' + op + r'.*?);\n', s); assert m, name; return m
