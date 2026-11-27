"""敌人第 7 批（2026-11-25 晚，每日敌人任务，tv 191：B1 要迁移已放上去的敌人卡的出招表）。
用法：python3 -I tools/enemy7.py index.html <官方 ExcelOutput 目录（含 TextMapCHS.json）> <更新日志 li 文件>
官方数据：https://raw.githubusercontent.com/DimbreathBot/TurnBasedGameData/main/ 的 ExcelOutput/*.json 和 TextMap/TextMapCHS.json
（目录里要有 MonsterConfig MonsterTemplateConfig MonsterSkillConfig EliteGroup HardLevelGroup StageConfig TextMapCHS）

A. 新敌人 5 个：活动「承露天人」（StageConfig StageType RealityShowActivity，关卡 43201x0～x6，30～95 级）的 5 个首领。
   和 MON 里同名的深渊 / 主线版本是不同形态（速度、韧性、弱点、技能都不一样），按“同名不同形态要分开”加后缀「（承露天人）」
   （后缀 = 官方关卡名 StageName，和「（历战余响）」「（末日幻影）」一样按出处取名）：
     示死祸源：深魇蝗灾（承露天人）  MonsterID 3024034  速度 190 物火风 韧性 600  多天赋【暗噬】、没有【旋覆甲壳】
     火花大会@Official（承露天人）    MonsterID 5014016  速度 200 物量虚 韧性 960  多天赋【永恒剧目】
     反造物主，流溢之恨（承露天人）  MonsterID 4035012  速度 240 冰雷量 韧性 600  多天赋【逆反】，少 莫要困毙洞中 / 莫要臣服暴政 / 恨
     堕神之血•亚婆离（承露天人）    MonsterID 5034013  速度 180 冰量虚 韧性 1080 少【集群连带应激】
     合金机铠•帕姆王（承露天人）    MonsterID 5014025  速度 142 雷量虚 韧性 600  多天赋【长效抗菌】、开局延后 20%（InitialDelayRatio 0.8）
   关卡速度 = 资料速度（关卡 EliteGroup 432011～432015 SpeedRatio 1，难度组 4701～4705 和 1 组同等级倍率相同），不写 v。
   字段算法同 tools/monlib.py（先用同一函数重建「反造物主，流溢之恨」4035010 验证和 MON 一致）。
B1. 模板默认出招里混进了被动天赋：官方 SkillTypeDesc 写“技能”、SkillTag 是「天赋」（SkillTriggerKey SkillP* / PassiveSkillInitiate）的
   技能以前被当成主动技能放进 k / q，敌人轮到它时什么也不做（不打人、白白空过一回合）。3 个模板：
     喜剧的残渣（冒犯性笑话）、至高，至阳，天空的化身（历战余响）（百眼 雷暴 酷阳 遗骨 黑潮 至暗潮汐）、
     金血忆灵•裁定忘却之形（虚构叙事）（决狱从速）——挪到 p（天赋），从 q 去掉；tools/monlib.py 的 build 以后也按标签判断。
   迁移 fixTpl191：已经放上去的这 3 种敌人卡，u.seq（applyMon 时从 q 复制的）去掉这几个下标。
B2. 怪物效果（MON.sk 新字段，模拟里用；只在“我方伤害扣敌人生命值”开着、敌人真的会被消灭时起作用，关着时和以前完全一样）：
   kr：写在天赋上，其他敌方单位被消灭时自身立即行动（行动提前 100%，和起床铃声 pl 一样的写法）；
   krk：这次行动固定施放的技能（MON.sk 下标，不推进出招表，同 dblF 的写法）；
   krn：只在被消灭的敌人模板名以它开头时触发；kr1：同一个天赋同时最多 1 个单位处在“已触发、还没行动”的状态。
   - 黑潮蚀斧【仇隙】“当其他敌方单位被消灭时，自身立即行动，施放一次【仇心忿火】。场上存在多个【黑潮蚀斧】时，同时最多只能触发1个”
     → kr 1、krk 仇心忿火、kr1 1（按卡片顺序第一个在场的黑潮蚀斧）。
   - 布洛妮娅（幻象）【同仇敌忾】“当杰帕德陷入无法战斗的状态时，将立即行动，进入强化状态，提高自身的速度”
     → kr 1、krn 杰帕德（只做“立即行动”；速度提高原文没写数值、召唤更多银鬃炮手没做）。
（2026-11-25 晚推不上仓库；2026-11-26 敌人第 8 批开工时按项目文档里的补丁原样合回，页面改动取自 claude.ai 页面第 327 版。
 2026-11-27 每日校对按项目文档「敌人任务-2026-11-26-敌人第8批-未推送补丁.md」转录进仓库。）
"""
import sys, json, re, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import Mon, page, grab, num

P, D, LOGF = sys.argv[1], sys.argv[2], sys.argv[3]
M = Mon(D)
s, crlf = page(P)
TV = 191
assert f'if (s.tv >= {TV - 1}) return;' in s and f'if (s.tv >= {TV}) return;' not in s, '页面 tv 不是 190'
assert 'actor.krS' not in s and 'z.krP' not in s, '已经跑过'
mM = grab(s, 'MON', r'\{'); MON = json.loads(mM.group(2))
idx = {m['n']: i for i, m in enumerate(MON['m'])}
nm0, sk0 = len(MON['m']), len(MON['sk'])
SN = lambda o: [MON['sk'][i]['n'] for i in o]
untag = lambda x: re.sub(r'<[^>]+>', '', x or '')

# ---------- 验证 monlib 算法：重建主线 / 深渊版「反造物主，流溢之恨」 ----------
base = MON['m'][idx['反造物主，流溢之恨']]
tmp = {'sk': list(MON['sk'])}; ref = M.build(tmp, 4035010)
assert {k: v for k, v in ref.items() if k not in ('k', 'p', 'q', 'x')} == {k: v for k, v in base.items() if k not in ('k', 'p', 'q', 'x')}, (ref, base)
assert [tmp['sk'][i] for i in ref['k'] + ref['p']] == [MON['sk'][i] for i in base['k'] + base['p']]
assert {tmp['sk'][int(i)]['n']: v for i, v in ref['x'].items()} == {MON['sk'][int(i)]['n']: v for i, v in base['x'].items()}

# ---------- A. 承露天人 5 个首领 ----------
ST = M.L('StageConfig')
use = collections.defaultdict(collections.Counter)
for st in ST:
    for w in st['MonsterList']:
        for k in w: use[w[k]][(st.get('StageType'), untag(M.T(st.get('StageName'))))] += 1
NEW = [(3024034, '示死祸源：深魇蝗灾'), (5014016, '火花大会@Official'), (4035012, '反造物主，流溢之恨'), (5034013, '堕神之血•亚婆离'), (5014025, '合金机铠•帕姆王')]
EXP = {   # MonsterID: (速度, 弱点, 韧性, 开局延迟, 技能名集合)
    3024034: (190, '物火风', 600, 0.5, {'恶变鞘翅', '饕虐外肢', '侵掠，撕碎，进食', '分裂，腐化，吞吃', '荒潮到临，蝗灾示死', '原始饥饿', '诸界噩兆，蚀生虫鸣', '暗噬', '共生，群集，噬咬'}),
    5014016: (200, '物量虚', 960, 0.5, {'开始控评！', '弹幕满载！', '网络对线！', '节奏带起来！', '抬你上麦！', '推流', '好感度调整', '粉丝的狂欢', '永恒剧目'}),
    4035012: (240, '冰雷量', 600, 0.5, {'掷下血与伤', '编织受难与死亡', '神的冠冕将要粉碎', '灵的囚笼必遭焚毁', '去反抗，去毁灭', '烧尽神国，弃绝世界', '三千万转，罪业回环', '逆反'}),
    5034013: (180, '冰量虚', 1080, 0.5, {'猎食标记', '饥饿的鸣响', '宏观生态系统', '万物于我之中', '兽瞳百相', '胎儿之梦', '血脑屏障'}),
    5014025: (142, '雷量虚', 600, 0.8, {'灵魂修正剪', '高温消毒模式', '无死角洗涤', '强效肥皂泡', '值日准备中…', '饱和式大扫除！', '洗地机之乱', '长效抗菌'}),
}
added = []
for mid, n0 in NEW:
    assert M.name(mid) == n0 and n0 in idx, (mid, M.name(mid))
    places = set(use[mid]); assert places == {('RealityShowActivity', '承露天人')}, (mid, places)
    NM = n0 + '（承露天人）'; assert NM not in idx and not any(m['n'] == NM for m in MON['m'])
    o = M.build(MON, mid, NM)
    sp, w, tn, d, sks = EXP[mid]
    assert (o['s'], o['w'], o['tn'], o.get('d', 1)) == (sp, w, tn, d), (NM, o)
    assert set(SN(o['k'] + o.get('p', []))) == sks, (NM, SN(o['k'] + o.get('p', [])))
    bm = MON['m'][idx[n0]]
    assert set(SN(bm['k'] + bm.get('p', []))) != sks or (bm['s'], bm.get('w'), bm.get('tn')) != (sp, w, tn)   # 确实是不同形态
    # 「蓄力」后面紧跟它点名的招（建模板时 qfix 的规则）；没有「锁定」
    for j, i in enumerate(o['q']):
        k = MON['sk'][i]; assert k['t'] != '锁定'
        if k['t'] == '蓄力':
            nx = re.findall(r'【([^】]+)】', k['d']); tg = [x for x in nx if x in SN(o['k']) and x != k['n']]
            assert tg and MON['sk'][o['q'][j + 1]]['n'] == tg[-1], (NM, k['n'], tg)
    MON['m'].append(o); idx[NM] = len(MON['m']) - 1; added.append((NM, mid, o))

# ---------- B1. 默认出招里的被动天赋 ----------
B1 = {}
for j, m in enumerate(MON['m'][:nm0]):
    bad = [i for i in m.get('k', []) if MON['sk'][i]['t'] == '天赋']
    if not bad: continue
    B1[m['n']] = bad
    m['k'] = [i for i in m['k'] if i not in bad]; m['q'] = [i for i in m['q'] if i not in bad]
    m['p'] = m.get('p', []) + bad
    for i in bad: m.get('x', {}).pop(str(i), None)
assert {n: SN(v) for n, v in B1.items()} == {'喜剧的残渣': ['冒犯性笑话'], '至高，至阳，天空的化身（历战余响）': ['百眼', '雷暴', '酷阳', '遗骨', '黑潮', '至暗潮汐'],
                                         '金血忆灵•裁定忘却之形（虚构叙事）': ['决狱从速']}, B1
for mid, nm in ((5032040, '喜剧的残渣'), (4015011, '至高，至阳，天空的化身（历战余响）'), (4064014, '金血忆灵•裁定忘却之形（虚构叙事）')):   # 官方：这些都是 SkillTag 天赋、触发键 SkillP* / Passive*
    for sid in M.MC[mid]['SkillList']:
        sk = M.MS.get(sid)
        if sk and M.T(sk.get('SkillName')) in SN(B1[nm]):
            assert M.T(sk.get('SkillTag')) == '天赋' and re.match(r'(SkillP\d|Passive)', sk.get('SkillTriggerKey', '')), (nm, sid)
assert not any(MON['sk'][i]['t'] == '天赋' for m in MON['m'] for i in m.get('k', []))

# ---------- B2. kr / krk / krn / kr1 ----------
KR = {}
for j, m in enumerate(MON['m']):
    for i in m.get('p', []):
        k = MON['sk'][i]
        if k['n'] == '仇隙':
            assert k['d'] == '当其他敌方单位被消灭时，自身立即行动，施放一次【仇心忿火】。场上存在多个【黑潮蚀斧】时，同时最多只能触发1个【黑潮蚀斧】的【仇隙】天赋。', k['d']
            h = [x for x in m['k'] if MON['sk'][x]['n'] == '仇心忿火']; assert len(h) == 1 and m['n'] == '黑潮蚀斧'
            if 'kr' in k: assert k['krk'] == h[0]; continue
            k.update({'kr': 1, 'krk': h[0], 'kr1': 1}); KR[m['n']] = (i, k['n'], h[0])
        if k['n'] == '同仇敌忾':
            assert k['d'] == '当杰帕德陷入无法战斗的状态时，将立即行动，进入强化状态，提高自身的速度。此状态下，布洛妮娅将会召唤更多的【银鬃炮手】。', k['d']
            assert m['n'] == '布洛妮娅（幻象）'
            if 'kr' in k: continue
            k.update({'kr': 1, 'krn': '杰帕德'}); KR[m['n']] = (i, k['n'], None)
assert set(KR) == {'黑潮蚀斧', '布洛妮娅（幻象）'}, KR

s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]

def rep(x, y, n=1):
    global s
    assert s.count(x) == n, (x[:120], s.count(x)); s = s.replace(x, y)

# 敌人被消灭时：其他敌人的 kr 天赋
rep('      fireAll("ekill", en);   // 敌人被消灭时（事件对象 = 这个敌人）\n',
    '      fireAll("ekill", en);   // 敌人被消灭时（事件对象 = 这个敌人）\n'
    '      { const busy = new Set(U.filter(z => z.kind === "enemy" && !z.gone && z.krP).map(z => z.krP));   // MON.sk.kr：其他敌方单位被消灭时自身立即行动（仇隙、同仇敌忾；敌人第 7 批）\n'
    '        for (const z of U) { if (z.kind !== "enemy" || z === en || z.gone || z.noAct) continue; const m = monOf(z);\n'
    '          for (const i of (m && m.p) || []) { const k = MON.sk[i]; if (!k || !k.kr || (k.krn && !String(en.mon || en.name || "").startsWith(k.krn)) || (k.kr1 && busy.has(String(i)))) continue;\n'
    '            busy.add(String(i)); z.krP = String(i); const kk = k.krk != null && MON.sk[k.krk] ? k.krk : null; if (kk != null) z.krS = kk; pull(z, 10000);\n'
    '            marks.push({ t, uid: z.id, label: k.n, color: "var(--enemy)", from: en.name });\n'
    '            addLog(`${z.name}【${k.n}】：${en.name} 被消灭，立即行动（行动提前 100%）${kk != null ? "，下次行动施放【" + MON.sk[kk].n + "】" : ""}`, false, "var(--enemy)"); break; } } }\n')
# 敌方回合开始：清掉“已触发”
rep('        actor.dlC = {};   // 每回合推条次数清零',
    '        actor.krP = null;   // 【仇隙】这类“同时最多触发 1 个”：轮到它行动就算触发完了（敌人第 7 批）\n'
    '        actor.dlC = {};   // 每回合推条次数清零')
# 出招：kr 触发后这次固定施放 krk，不推进出招表
rep('const fxA = !FG && actor.dblF != null && !(num(actor.dblI) > 0) && MON.sk[actor.dblF] ? actor.dblF : null; if (fxA != null) actor.sqo = num(actor.sqo) - 1;',
    'const krA = !FG && actor.krS != null && MON.sk[actor.krS] ? actor.krS : null; if (krA != null) { actor.krS = null; actor.sqo = num(actor.sqo) - 1; }   // MON.sk.krk：【仇隙】立即行动施放【仇心忿火】（敌人第 7 批）\n'
    '          const fxA = krA != null ? krA : !FG && actor.dblF != null && !(num(actor.dblI) > 0) && MON.sk[actor.dblF] ? actor.dblF : null; if (fxA != null && krA == null) actor.sqo = num(actor.sqo) - 1;')

# 迁移：已放上去的敌人卡出招表去掉这些天赋
MF = {n: v for n, v in B1.items()}
a = re.search(rf'  // tv {TV - 1}：', s); assert a
s = s[:a.start()] + (f'  // tv {TV}：敌人第 7 批：模板默认出招里混进的被动天赋去掉（tools/enemy7.py）。只改已经放上去的这几种敌人卡的出招表 u.seq\n'
    f'  const MONFIX{TV} = ' + json.dumps(MF, ensure_ascii=False) + ';\n'
    f'  function fixTpl{TV}(s) {{ for (const u of s.units || []) {{ const d = u.kind === "enemy" && u.mon ? MONFIX{TV}[u.mon] : null; if (!d || !Array.isArray(u.seq)) continue; '
    f'const q = u.seq.filter(i => !d.includes(num(i))); if (q.length && q.length !== u.seq.length) u.seq = q; }} }}\n') + s[a.start():]
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'if (!(s.tv >= {TV - 1})) fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'if (!(s.tv >= {TV - 1})) fixTpl{TV - 1}(s); if (!(s.tv >= {TV})) fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'    fixTpl{TV - 1}(s);\n    s.tv = {TV - 1};', f'    fixTpl{TV - 1}(s);\n    fixTpl{TV}(s);\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')

log = open(LOGF, encoding='utf-8').read().strip()
ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('MON', nm0, '→', len(MON['m']), '；sk', sk0, '→', len(MON['sk']))
for NM, mid, o in added:
    print(' ', NM, mid, {k: o[k] for k in ('r', 's', 'w', 'tn', 'a', 'h')}, o.get('d'), 'k', SN(o['k']), 'p', SN(o.get('p', [])), 'q', SN(o['q']), 'x', {MON['sk'][int(i)]['n']: v for i, v in o.get('x', {}).items()})
print('KR', KR)
print('B1', {n: (v, SN(v)) for n, v in B1.items()})
