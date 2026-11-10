"""校对脚本公共部分（tv 57 起）：读写 index.html 里的 DB / DMG / XR，生成 TPLFIX 迁移表，插入迁移代码、更新日志和校对记录。
用法见 tools/fix57.py。官方数据目录（StarRailRes index_new/cn 的 json）作为第二个命令行参数传入。
"""
import re, json, sys


class Fix:
    def __init__(self, path, tv, src):
        self.P, self.TV, self.src = path, tv, src
        self.s = open(path, encoding='utf-8').read()
        assert f'if (s.tv >= {tv - 1}) return;' in self.s, '页面 tv 不是 %d' % (tv - 1)
        ld = lambda n: json.load(open(f'{src}/{n}.json', encoding='utf-8'))
        self.SK, self.CH, self.RK, self.TR = ld('character_skills'), ld('characters'), ld('character_ranks'), ld('character_skill_trees')
        self.DB = self.grab('DB'); self.DMG = self.grab('DMG'); self.XR = self.grab('XR')
        self.C = {c['id']: c for c in self.DB['chars']}
        self.OLD = {c['id']: [(e.get('n'), e.get('t')) for e in c.get('eff', []) if e.get('y') != 'info'] for c in self.DB['chars']}   # 改之前的说明和触发（脚本里会原地改效果）
        self.FIX = {}

    # ---- 文本读写 ----
    def _m(self, name):
        m = re.search(r'const ' + name + r' ?= ?(\{.*?\});\n', self.s); assert m, name; return m
    def grab(self, name): return json.loads(self._m(name).group(1))
    def put(self, name, obj):
        m = self._m(name)
        self.s = self.s[:m.start(1)] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + self.s[m.end(1):]
    def rep(self, x, y, n=1):
        assert self.s.count(x) == n, (x[:100], self.s.count(x)); self.s = self.s.replace(x, y)

    # ---- 官方数据 ----
    def prm(self, sid, lv=None):
        p = self.SK[sid]['params']; return p if lv is None else p[lv - 1]
    def has(self, sid_or_text, frag):
        """断言官方原文里有这句话（技能 id / 星魂 id / 行迹 id，或直接给文本）"""
        k = str(sid_or_text)
        t = (self.RK.get(k[2:], {}) if k.startswith('r:') else self.SK.get(k) or self.RK.get(k) or self.TR.get(k) or {}).get('desc', k)
        nz = lambda z: re.sub(r'\d+(\.\d+)?%?', '#', re.sub(r'#\d+\[\w+\]%?', '#', re.sub(r'<[^>]+>', '', z)))   # 数字和占位符都当成 #
        assert nz(frag) in nz(t), (frag, t[:300])

    def hast(self, cid, name, frag):
        """断言行迹原文里有这句话（数字和占位符都当成 #）；同名行迹取最后一个（强化版）"""
        d = {self.TR[t]['name']: self.TR[t]['desc'] for t in self.CH[str(cid)]['skill_trees'] if self.TR[t].get('desc')}
        self.has(d[name], frag)

    # ---- 模板 ----
    def eff(self, cid, frag, r=None):
        """按说明里的一段文字找模板效果（r = 几魂的星魂效果）"""
        c = self.C[cid]
        L = c['eff'] if r is None else [x for e in c['eid'] if e['r'] == r for x in e['eff']]
        R = [x for x in L if frag in (x.get('n') or '')]
        assert len(R) == 1, (cid, frag, [x.get('n') for x in R]); return R[0]
    def rebuild(self, cid, new, rename=None, set=None, off0=None, x=None, cnt=None, notes=None, sm=None):
        """整组换掉角色的基础效果：旧效果全部进 drop（触发被用户改过的会保留），map = 同名或 rename 指定的新说明，add = 全部新说明。"""
        c = self.C[cid]; rename = rename or {}
        old = self.OLD[cid]
        nn = [e['n'] for e in new if e.get('y') != 'info']
        assert len(set_(nn)) == len(nn), ('说明重复', cid, [n for n in nn if nn.count(n) > 1])
        on = [n for n, t in old]; assert len(set_(on)) == len(on), ('旧说明重复', cid, [n for n in on if on.count(n) > 1])
        for k, v in rename.items(): assert k in on and v in nn, (k, v)
        mp = {}
        for n in on:
            t = rename.get(n, n)
            if t in nn: mp[n] = t
        fx = {'drop': on, 'trig': {n: t for n, t in old}, 'map': mp, 'add': nn, 'sm': {}}
        if set: fx['set'] = set
        if off0: fx['off0'] = off0
        c['eff'] = new
        if x is not None: c.setdefault('x', {}).update(x)
        if cnt is not None: c['cnt'] = cnt
        if notes is not None: c['notes'] = notes
        if sm is not None: c['sm'] = sm
        self.FIX[str(cid)] = fx
    def touch(self, cid, set=None):
        """只改了星魂 / x 的角色：给个空表，让迁移对它重建星魂效果"""
        fx = self.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})
        if set: fx.setdefault('set', {}).update(set)
    def eid(self, cid, r):
        c = self.C[cid]
        R = [e for e in c['eid'] if e['r'] == r]
        if not R:
            c['eid'].append({'r': r, 'eff': [], 'notes': []}); c['eid'].sort(key=lambda e: e['r'])
            R = [e for e in c['eid'] if e['r'] == r]
        self.touch(cid); return R[0]
    def xr(self, cid, rows, drop=()):
        L = [r for r in self.XR.get(str(cid), []) if r['k'] not in drop]
        ks = {r['k'] for r in L}
        for r in rows: assert r['k'] not in ks, r['k']
        self.XR[str(cid)] = L + list(rows)

    # ---- 收尾 ----
    def finish(self, title, log_html, record):
        TV = self.TV
        self.put('DB', self.DB); self.put('DMG', self.DMG); self.put('XR', self.XR)
        s = self.s
        a = re.search(rf'  // tv {TV - 1}：', s); assert a
        s = s[:a.start()] + (f'  // tv {TV}：{title}（tools/fix{TV}.py）\n'
            f'  const TPLFIX{TV} = ' + json.dumps(self.FIX, ensure_ascii=False) + ';\n'
            f'  function fixTpl{TV}(s) {{ const keep = S; S = s; try {{ fixTpl(s, TPLFIX{TV}); }} finally {{ S = keep; }} }}\n') + s[a.start():]
        self.s = s
        self.rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
        self.rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
        self.rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
        self.rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
        ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
        i = self.s.index(ul, self.s.index('<details id="changelog">')) + len(ul)
        self.s = self.s[:i] + log_html.strip() + '\n' + self.s[i:]
        head = '<!-- 校对记录（每日任务按此挑选最久未校对的项目）\n'
        i = self.s.index(head) + len(head)
        self.s = self.s[:i] + record.strip() + '\n' + self.s[i:]
        open(self.P, 'w', encoding='utf-8').write(self.s)
        print('ok tv', TV, {k: len(v['add']) for k, v in self.FIX.items()})


set_ = set
r4 = lambda v: round(v, 4)
