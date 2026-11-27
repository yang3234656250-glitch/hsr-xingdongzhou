"""敌人第 8 批（2026-11-26 晚，每日敌人任务，没改 tv：只改 MON.sk 的 ht，敌人卡里存的是技能下标，不用迁移）。
用法：python3 -I tools/enemy8.py index.html <更新日志 li 文件>

B. 不打人的敌人技能被当成了攻击：标签是「单攻 / 群攻 / 妨害」、但原文没有任何伤害、也不是对我方单位施加负面状态，
   只是 ① 为我方恢复能量 / 战技点，② 减少我方战技点（不针对某个角色），③ 只作用于敌方（行动提前、人气值）。
   以前按标签选目标：被选中的角色触发“受到攻击时”（克拉拉反击、白露生息回复等）和“生命值降低时”（风堇小伊卡记下、遐蝶新蕊等），
   有【滋扰】的关卡还会让那个角色行动延后。这些技能被打回能都是 0（官方 SPHitBase 0），所以能量本来就不变。
   改法：给这些技能写 ht "辅助"（按这个标签选目标 = 不选任何我方角色；ht 是敌人第 2 批 tools/enemy2.py 的字段），
   bp（锁元的战技点 −1）照旧结算。原文依据（TextMapCHS，技能描述原样）见 EXP。
   没做的部分（原文没写数值）：惊喜综艺 / 狼的怜悯 / 蕉喜假期 恢复多少能量、狼的赠予恢复几个战技点、坏猴来了记大过 / 狼的讥讽 减几个、
   孤狼永不下班 / 上课铃，都坐好！ 敌方全体行动提前多少——都还是不结算（和以前一样），记在差异清单「二」。
（2026-11-26 晚推不上仓库；2026-11-27 每日校对按项目文档「敌人任务-2026-11-26-敌人第8批-未推送补丁.md」转录进仓库，页面改动取自 claude.ai 页面第 328 版。）
"""
import sys, json, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monlib import page, grab

P, LOGF = sys.argv[1], sys.argv[2]
s, crlf = page(P)
assert 'enemy8' not in s, '已经跑过'
mM = grab(s, 'MON', r'\{'); MON = json.loads(mM.group(2))
HIT = {'单攻', '妨害', '扩散', '弹射', '群攻', '横扫', '分摊'}
EXP = {   # 技能名: (标签, 原文)
    '惊喜综艺': ('单攻', '使指定我方单体恢复能量。只能在【惊喜频道】状态下使用。'),
    '狼的怜悯': ('单攻', None),   # 两个版本：【讥讽】状态 / 【怜悯】状态，都是“使指定我方单体恢复能量。”
    '蕉喜假期': ('单攻', '使指定我方单体恢复能量。只能在【课间频道】状态下使用。'),
    '狼的赠予': ('群攻', '使我方战技点恢复。只能在【讥讽】状态下使用。'),
    '锁元': ('妨害', '使我方战技点减少1个。'),
    '坏猴来了记大过': ('妨害', '减少我方战技点。只能在【课堂频道】状态下使用。'),
    '狼的讥讽': ('妨害', '使我方战技点减少。只能在【狂乱】状态下使用。'),
    '孤狼永不下班': ('妨害', '使敌方全体行动提前。只能在【狂乱】状态下使用。'),
    '上课铃，都坐好！': ('妨害', '使敌方全体行动提前。只能在【课堂频道】状态下使用。'),
    '掉粉': ('妨害', '若【对方人气值】降低，则使处于副战场的敌方目标失去【对方打赏】。'),
}
xr = {int(k) for m in MON['m'] for k in (m.get('x') or {})}
used = {i for m in MON['m'] for i in m.get('k', [])}
chg = []
for i, k in enumerate(MON['sk']):
    if k['n'] not in EXP: continue
    t, d = EXP[k['n']]
    if i not in used: continue
    assert k['t'] == t and k['t'] in HIT and 'ht' not in k and not k.get('ha'), (i, k)
    if d: assert k['d'] == d, (i, k['d'])
    else: assert k['d'].startswith('使指定我方单体恢复能量。'), (i, k['d'])
    assert '伤害' not in k['d'] and i not in xr and k['sp'] == 0, (i, k)
    k['ht'] = '辅助'; chg.append(i)
names = [MON['sk'][i]['n'] for i in chg]
assert sorted(names) == sorted(list(EXP) + ['狼的怜悯']), names   # 狼的怜悯两个版本
assert MON['sk'][[i for i in chg if MON['sk'][i]['n'] == '锁元'][0]].get('bp') == -1
users = sorted({m['n'] for m in MON['m'] for i in m.get('k', []) if i in chg})
s = s[:mM.start(2)] + json.dumps(MON, ensure_ascii=False, separators=(',', ':')) + s[mM.end(2):]
# ht 的注释补一句（只改注释，不改代码）
a = 'const tT = sk.ht || sk.t;   // sk.ht：按这个标签选目标、算伤害（标签是扫射 / 强化 / 锁定 / 妨害、原文写了打谁的，敌人第 2 批 tools/enemy2.py）'
assert s.count(a) == 1
s = s.replace(a, a + '；ht "辅助" = 原文不打人（恢复我方能量 / 战技点、只作用于敌方，敌人第 8 批 tools/enemy8.py）')
log = open(LOGF, encoding='utf-8').read().strip()
ul = '<ul class="hint" style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px">\n'
i = s.index(ul, s.index('<details id="changelog">')) + len(ul)
s = s[:i] + log + '\n' + s[i:]
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('改了', len(chg), '招：', [(i, MON['sk'][i]['n']) for i in chg])
print('用到的敌人', len(users), users)
