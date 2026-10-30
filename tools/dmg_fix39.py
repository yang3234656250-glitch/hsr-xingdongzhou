"""tv 39：记忆 / 欢愉角色按官方原文全面补效果（行动轴 + 伤害）。
DB 模板：新加的效果（BASE）、删掉的旧效果（DROP，按说明）、原地改字段的效果（PATCH，老存档同步改）、星魂效果直接改 DB（星魂效果每次套装备都会重建）。
用法：python3 tools/dmg_fix39.py index.html"""
import re, json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
TV = 39
s = open(P, encoding='utf-8').read()
assert f'if (s.tv >= {TV - 1}) return;' in s, '版本号不对'
m = re.search(r'const DB = (\{.*?\});\n', s); DB = json.loads(m.group(1))
C = {c['id']: c for c in DB['chars']}
D = lambda **k: dict(y='dbuf', **k)

def find(cid, sub, where='eff'):
    L = [x for x in C[cid][where] if sub in x['n']]
    assert len(L) == 1, (cid, sub, [x['n'] for x in L]); return L[0]
def eid(cid, r):
    e = next((e for e in C[cid]['eid'] if e['r'] == r), None)
    if not e: e = {'r': r, 'eff': [], 'notes': []}; C[cid]['eid'].append(e); C[cid]['eid'].sort(key=lambda z: z['r'])
    return e
def eid_find(cid, r, sub):
    L = [x for x in eid(cid, r)['eff'] if sub in x['n']]
    assert len(L) == 1, (cid, r, sub, [x['n'] for x in L]); return L[0]
def eid_drop(cid, r, sub):
    e = eid(cid, r); n0 = len(e['eff']); e['eff'] = [x for x in e['eff'] if sub not in x['n']]; assert len(e['eff']) == n0 - 1, (cid, r, sub)
def eid_note_drop(cid, r, sub):
    e = eid(cid, r); n0 = len(e['notes']); e['notes'] = [x for x in e['notes'] if sub not in x]; assert len(e['notes']) < n0, (cid, r, sub)
def note_drop(cid, sub):
    n0 = len(C[cid]['notes']); C[cid]['notes'] = [x for x in C[cid]['notes'] if sub not in x]; assert len(C[cid]['notes']) < n0, (cid, sub)

BASE, DROP, PATCH, SET, FIXADD = {}, {}, {}, {}, {}
def add(cid, *L): BASE.setdefault(cid, []).extend(L)
def drop(cid, sub):
    x = find(cid, sub); DROP.setdefault(cid, []).append((x['n'], x['t'])); C[cid]['eff'].remove(x)
# PATCH：x 键 → 效果对象字段
XK = {'ac': 'allyCap', 'acR': 'acR', 'o': 'or', 'aw': 'allyWho', 'maxEl': 'maxEl', 'mm': 'minMem', 'mgt': 'minGT', 'ste': 'stE',
      'ofs': 'offSt', 'dy': 'dyn', 'te': 'tEl', 'off': 'off', 'n': 'note', 'au': 'allyUlt'}
def patch(cid, sub, **kw):
    x = find(cid, sub); old = x['n']; js = {}
    for k, v in kw.items():
        if v is None or v is False: x.pop(k, None)
        else: x[k] = v
        f = XK[k]; js[f] = None if v is None or v is False else (True if v is True or (k in ('dy', 'au') and v == 1) else v)
    PATCH.setdefault(str(cid), {})[old] = js

# ---------------- 1402 阿格莱雅 ----------------
patch(1402, '忆灵天赋：衣匠攻击间隙织线的敌人后速度 +55', ste=[4, 7])
patch(1402, '行迹短视之惩：【至高之姿】时阿格莱雅攻击力 +自身速度的 720%', dy=1, n='行迹短视之惩：【至高之姿】时阿格莱雅攻击力 +自身速度的 720%（按出手时的速度）')
patch(1402, '行迹短视之惩：衣匠同样提高（按阿格莱雅速度的 720%）', dy=1, n='行迹短视之惩：【至高之姿】时衣匠攻击力 +阿格莱雅速度的 720%（按出手时的速度）')
add(1402,
    dict(y='state', t='ult', tg='self', sn='至高之姿', v=1, d=0, n='终结技：进入【至高之姿】'),
    dict(y='state', t='smEnd', sk='supreme', tg='self', sn='至高之姿', v=0, d=0, n='终结技：倒计时回合开始衣匠自毁，退出【至高之姿】'),
    dict(y='spd', t='ult', tg='self', m='pct', v=15, st=6, ste=[4, 7], cpy='gspd', d=0, bk='aspd', n='终结技：【至高之姿】时阿格莱雅获得衣匠忆灵天赋的速度层数，每层速度 +15%'),
    dict(y='spd', t='atk', aw='sm', tg='self', m='pct', v=15, st=6, ste=[4, 7], cpy='gspd', d=0, bk='aspd', ns='至高之姿', n='终结技：【至高之姿】时衣匠叠层后阿格莱雅的层数跟着变'),
    dict(y='spd', t='smEnd', sk='supreme', tg='self', m='pct', v=0, d=0, bk='aspd', n='终结技：退出【至高之姿】，阿格莱雅的速度层数取消'),
    dict(y='spd', t='smEnd', sk='garment', tg='sm:garment', m='flat', v=55, stc=1, d=0, bk='gspd', n='行迹织运之竭：衣匠消失时忆灵天赋的速度层数最多保留 1 层，再次召唤时带着'),
    D(t='smOn', sk='supreme', tg='self', m='atkF', ss='spd', ssm='garment', v=360, dy=1, d=0, bk='dsz2', n='行迹短视之惩：【至高之姿】时阿格莱雅攻击力再 +衣匠速度的 360%（按出手时的速度）'),
    D(t='smOn', sk='supreme', tg='sm:garment', m='atkF', ss='spd', ssm='garment', v=360, dy=1, d=0, bk='dszg2', n='行迹短视之惩：衣匠攻击力再 +衣匠速度的 360%'),
    D(t='smEnd', sk='supreme', tg='self', m='atkF', v=0, d=0, bk='dsz2', n='行迹短视之惩：至高之姿结束，衣匠速度那部分取消'),
    D(t='smEnd', sk='supreme', tg='sm:garment', m='atkF', v=0, d=0, bk='dszg2', n='行迹短视之惩：至高之姿结束，衣匠的衣匠速度那部分取消'),
    dict(y='energy', t='start', tg='self', m='atl', v=50, n='行迹飞驰之阳：战斗开始时能量不足 50% 则恢复至 50%'),
    dict(y='energy', t='start', tg='self', m='er', v=30, off=1, n='秘技披星百裂：进入战斗后恢复 30 点能量（用了秘技再启用）'),
    D(t='smEnd', sk='supreme', tg='self', m='dmg', v=0, d=0, bk='rom', clr=1, n='昔涟献予「浪漫」之诗：退出【至高之姿】时浪漫的增伤结束'),
    D(t='smEnd', sk='supreme', tg='self', m='defIg', v=0, d=0, bk='rom', clr=1, n='昔涟献予「浪漫」之诗：退出【至高之姿】时浪漫的无视防御结束'))
for x in eid(1402, 4)['notes'][:]: eid(1402, 4)['notes'].remove(x)
eid(1402, 4)['eff'].extend([
    dict(y='spd', t='atk', aw='self', tg='sm:garment', m='flat', v=55, st=6, ste=[4, 7], si='in', d=0, bk='gspd', n='E4：阿格莱雅施放攻击后也能使衣匠获得忆灵天赋的速度层数（层数上限 7）'),
    dict(y='spd', t='atk', aw='self', tg='self', m='pct', v=15, st=6, ste=[4, 7], cpy='gspd', d=0, bk='aspd', ns='至高之姿', n='E4：【至高之姿】时阿格莱雅的层数跟着变')])
eid_find(1402, 6, 'E6：衣匠同样 +20%')['n'] = 'E6：衣匠同样 +20%（连携攻击按速度提高的伤害在伤害里算）'
for sub in ['终结技：【至高之姿】状态下', '每层速度 +12.5%', '行迹织运之竭']: note_drop(1402, sub)

# ---------------- 1407 遐蝶 ----------------
patch(1407, '忆灵技【燎尽黯泽的焰息】', ofs='炽意')
eid(1407, 2)['eff'].extend([
    dict(y='state', t='smOn', sk='dragon', tg='self', sn='炽意', v=0, n='E2：召唤死龙时【炽意】重置'),
    dict(y='state', t='smOn', sk='dragon', tg='self', sn='炽意', v=2, ts='chg', n='E2：召唤死龙后获得 2 层【炽意】（最多 2 层），死龙施放焰息时先用它抵扣生命值消耗'),
    dict(y='state', t='smOn', sk='dragon', tg='self', sn='炽意新蕊', v=1, d=0, n='E2：召唤死龙后，下一次施放强化战技获得新蕊（记为【炽意新蕊】）'),
    dict(y='energy', t='skill', si='in', ns='炽意新蕊', tg='self', m='fixed', v=10200, n='E2：下一次施放强化战技获得等同于新蕊上限 30% 的新蕊（按上限 34000）'),
    dict(y='state', t='skill', si='in', ns='炽意新蕊', tg='self', sn='炽意新蕊', v=0, n='E2：用掉【炽意新蕊】')])
add(1407,
    dict(y='energy', t='ult', tg='self', m='zero', ns='献予「生死」之诗', n='昔涟献予「生死」之诗：召唤死龙时消耗所有溢出的新蕊（这只死龙的晦翼倍率按消耗的溢出值提高，伤害里算）'))
note_drop(1407, '昔涟的献予「生死」之诗')
for i, x in enumerate(C[1407]['notes']):
    if 'E2【炽意】' in x: C[1407]['notes'][i] = '忆灵天赋月茧荫蔽的身躯：死龙在场时我方降到 1 点后剩下的生命值由死龙承担 ×500%，已做；E2【炽意】已做（抵扣焰息生命值消耗、行动提前 100%、下一次强化战技获得 30% 新蕊）'; break

# ---------------- 1413 长夜月 ----------------
C[1413]['cnt']['pl'] = [2, 2]
eid_note_drop(1413, 2, '每次获得【忆质】时数量 +2')
patch(1413, '行迹天亮了，雨落了：战技持续期间我方全体忆灵暴击伤害额外 +5%', n='行迹天亮了，雨落了：战技持续期间我方全体忆灵暴击伤害额外 +5%（队伍里有 1 名「记忆」角色）')
patch(1413, '行迹天亮了，雨落了：有 2 名「记忆」角色时改为 +15%', mgt=None, mm=2, n='行迹天亮了，雨落了：有 2 名「记忆」角色时改为 +15%')
patch(1413, '行迹天亮了，雨落了：有 3 名「记忆」角色时改为 +50%', mgt=None, mm=3)
patch(1413, '行迹天亮了，雨落了：有 4 名或以上「记忆」角色时改为 +65%', mgt=None, mm=4)
eid_drop(1413, 1, 'E1 睡吧，长夜有所梦')
eid(1413, 1)['eff'].append(D(t='start', tg='teamMem', m='rx', sc='ev1', v=1, d=0, bk='e1', n='E1 睡吧，长夜有所梦：长夜月在场时我方忆灵造成的伤害按敌人数 1 / 2 / 3 / 4 名以上为原伤害的 150% / 130% / 125% / 120%（按伤害设置里的敌人数）'))

# ---------------- 1415 昔涟：此诗，献予一切生命（对每次大招目标施放） ----------------
GT8 = [8007, 8008]
add(1415,
    D(t='ult', tg='ultpickm', pg=-1, m='dmg', v=40, lv=[3, 44], d=2, bk='p_all', n='忆灵技此诗，献予一切生命：对非黄金裔角色施放时，其造成的伤害 +40%，持续 2 回合（对它的忆灵也生效）'),
    D(t='ult', tg='ultpickm', ptp=GT8, m='atkF', ss='hp', v=16, lv=[3, 17.6], d=0, bk='p_cs', n='献予「创世」之诗：开拓者•记忆和迷迷攻击力 +德谬歌生命上限的 16%，整场生效（德谬歌生命上限 = 昔涟的，按昔涟当前生命上限）'),
    D(t='ult', tg='ultpickm', ptp=GT8, m='cr', ss='cr', v=72, hf=36, lv=[3, 79.2], d=0, bk='p_cs2', n='献予「创世」之诗：开拓者•记忆和迷迷暴击率 +德谬歌暴击率的 72%（德谬歌暴击率 = 昔涟面板 + 往昔的涟漪 50%）'),
    dict(y='state', t='ult', tg='self', ptp=GT8, sn='献予「创世」之诗', v=1, d=0, n='献予「创世」之诗：整场生效（记为【献予「创世」之诗】）'),
    dict(y='extra', t='ally', aw='oc', aa=['ebasic'], at=GT8, ns='献予「创世」之诗', tg='sm:demiurge', v=0, n='献予「创世」之诗：开拓者•记忆施放强化普攻后，德谬歌立即获得 1 个额外回合并施放【花与箭的舞曲】'),
    dict(y='state', t='ult', tg='ultpick', ptp=1402, sn='浪漫', v=1, d=0, n='献予「浪漫」之诗：阿格莱雅获得【浪漫】'),
    dict(y='spd', t='ult', tg='ultpickm', ptp=1402, tsm=1, ow=1, fl=1, m='flat', v=55, st=6, ste=[4, 7], d=0, bk='gspd', n='献予「浪漫」之诗：衣匠忆灵天赋的速度层数立即叠满'),
    dict(y='energy', t='atk', aw='all', **{'as': '浪漫'}, tg='evto', m='fixed', v=70, n='献予「浪漫」之诗：阿格莱雅或衣匠攻击后消耗【浪漫】，阿格莱雅恢复 70 点能量'),
    dict(y='state', t='atk', aw='all', **{'as': '浪漫'}, tg='evto', sn='浪漫', v=0, n='献予「浪漫」之诗：消耗【浪漫】'),
    D(t='ult', tg='ultpickm', ptp=1402, m='dmg', v=72, lv=[3, 79.2], d=0, bk='rom', n='献予「浪漫」之诗：阿格莱雅与衣匠造成的伤害 +72%，持续到阿格莱雅退出【至高之姿】'),
    D(t='ult', tg='ultpickm', ptp=1402, m='defIg', v=36, lv=[3, 39.6], d=0, bk='rom', n='献予「浪漫」之诗：阿格莱雅与衣匠无视目标 36% 防御力，持续到阿格莱雅退出【至高之姿】'),
    D(t='ult', tg='ultpick', ptp=1403, m='defIg', v=12, lv=[3, 13.2], d=0, bk='p_mj', n='献予「门径」之诗：缇宝造成的伤害无视 12% 防御力，整场生效'),
    D(t='ult', tg='ultpick', ptp=1403, m='rx', sc='men', v=1, d=0, bk='p_mjx', n='额外伤害标记：献予「门径」之诗（缇宝追加攻击触发结界附加伤害时再多 1 次）'),
    dict(y='advance', t='ult', tg='ultpick', ptp=1404, ns='!血仇', so='pick', v=100, n='献予「纷争」之诗：万敌不处于【血仇】时行动提前 100%'),
    dict(y='extra', t='ult', tg='ultpick', ptp=1404, ns='血仇', so='pick', v=0, n='献予「纷争」之诗：万敌处于【血仇】时自动施放 1 次不消耗充能的【弑神登神】（按给万敌 1 个额外回合；这一下暴伤 +200% 没算）'),
    dict(y='sp', t='ult', tg='self', ptp=1405, v=1, n='献予「理性」之诗：为我方恢复 1 个战技点'),
    dict(y='advance', t='ult', tg='ultpick', ptp=1405, v=100, n='献予「理性」之诗：那刻夏立即行动'),
    dict(y='state', t='ult', tg='ultpick', ptp=1405, sn='献予「理性」之诗', v=1, d=0, n='献予「理性」之诗：那刻夏下一次施放普攻 / 战技时获得【真知】'),
    D(t='ult', tg='ultpick', ptp=1405, m='rx', sc='rsn', v=1, d=1, bk='p_lx', n='额外伤害标记：献予「理性」之诗（那刻夏战技的伤害次数 +3，持续 1 回合）'),
    dict(y='state', t='ally', aw='sm', tg='oc', tt=1409, sn='献予「天空」之诗', v=2, ts='chg', n='献予「天空」之诗：德谬歌施放忆灵技时风堇获得 2 层【献予「天空」之诗】（持有时计入小伊卡的治疗数值额外 +72%，风堇施放战技 / 终结技后消耗 1 层）'),
    D(t='ult', tg='ultpick', ptp=1406, m='dmg', v=36, lv=[3, 39.6], d=0, bk='p_gj', n='献予「诡计」之诗：赛飞儿造成的伤害 +36%，整场生效'),
    D(t='ult', tg='enemies', ptp=1406, m='defRed', v=20, lv=[3, 22], d=0, bk='p_gj2', n='献予「诡计」之诗：【老主顾】防御力 −20%（其他敌人 −12%；按攻击目标是老主顾）'),
    dict(y='energy', t='ult', tg='ultpick', ptp=1408, m='fixed', v=6, n='献予「负世」之诗：白厄获得 6 点【火种】'),
    dict(y='state', t='ult', tg='ultpick', ptp=1408, sn='献予「负世」之诗', v=1, d=0, n='献予「负世」之诗：整场生效（白厄变身时获得【永续的燃烧】）'),
    D(t='ult', tg='ultpick', ptp=1410, m='dmg', v=120, lv=[3, 132], d=0, bk='p_hy', n='献予「海洋」之诗：海瑟音造成的伤害 +120%，整场生效'),
    dict(y='state', t='ult', tg='ultpick', ptp=1410, sn='暖流', v=1, d=0, n='献予「海洋」之诗：海瑟音获得【暖流】'),
    dict(y='energy', t='atk', aw='all', **{'as': '暖流'}, tg='evto', m='fixed', v=60, n='献予「海洋」之诗：海瑟音施放攻击后消耗【暖流】恢复 60 点能量'),
    dict(y='state', t='atk', aw='all', **{'as': '暖流'}, tg='evto', sn='暖流', v=0, n='献予「海洋」之诗：消耗【暖流】'),
    D(t='ult', tg='team', ptp=1412, m='rx', sc='law', v=1, d=0, bk='p_law', n='额外伤害标记：献予「律法」之诗（持有【军功】的角色暴击伤害 +30%）'),
    dict(y='state', t='ally', aw='sm', tg='oc', tt=1414, sn='献予「大地」之诗', v=1, d=0, n='献予「大地」之诗：德谬歌施放忆灵技时丹恒•腾荒获得【献予「大地」之诗】（同袍造成的伤害 +24%）'),
    dict(y='state', t='ult', tg='ultpick', ptp=1407, sn='献予「生死」之诗', v=1, d=0, n='献予「生死」之诗：整场生效（记为【献予「生死」之诗】）'),
    dict(y='ecap', t='ult', tg='ultpick', ptp=1407, v=200, n='献予「生死」之诗：遐蝶的【新蕊】可以溢出至 200%'))
note_drop(1415, '战技的结界（额外真实伤害）只影响伤害')
note_drop(1415, '忆灵技此诗，献予一切生命：昔涟每次开大')
C[1415]['notes'].append('忆灵技此诗，献予一切生命：昔涟每次开大，德谬歌的额外回合对“每次大招目标”里选的队友施放（选昔涟自己 = 这次改用花与箭的舞曲）。已做：非黄金裔 +40% 增伤；创世（开拓者•记忆）、浪漫（阿格莱雅）、门径（缇宝）、纷争（万敌）、理性（那刻夏）、天空（风堇）、诡计（赛飞儿）、负世（白厄）、海洋（海瑟音）、律法（刻律德菈）、岁月（长夜月）、大地（丹恒•腾荒）、生死（遐蝶）。没做：纷争那一下暴伤 +200%、负世变身时火种超过 12 的暴伤和 4 点毁伤、海洋立即结算持续伤害、律法奇袭后刻律德菈 +1 充能、大地龙灵的附加伤害和强化')
# 那刻夏：真知
add(1405,
    D(t='skill', o='basic', ns='献予「理性」之诗', tg='team', tp='智识', m='atkP', v=60, lv=[3, 66], d=1, bk='p_zz', n='昔涟献予「理性」之诗：下一次施放普攻 / 战技时获得【真知】，所有「智识」角色攻击力 +60%，到下一个那刻夏回合开始'),
    D(t='skill', o='basic', ns='献予「理性」之诗', tg='team', tp='智识', m='dmg', sc='s', v=40, lv=[3, 44], d=1, bk='p_zz2', n='昔涟献予「理性」之诗：【真知】期间「智识」角色战技伤害 +40%'),
    dict(y='state', t='skill', o='basic', ns='献予「理性」之诗', tg='self', sn='献予「理性」之诗', v=0, n='昔涟献予「理性」之诗：获得【真知】后移除'))
# 风堇：天空层数消耗
add(1409, dict(y='state', t='skill', o='ult', tg='self', sn='献予「天空」之诗', v=-1, ts='chg', n='昔涟献予「天空」之诗：风堇施放战技 / 终结技后消耗 1 层'))
# 丹恒•腾荒：大地
add(1414, D(t='ally', aw='osm', ns='献予「大地」之诗', tg='$ally', m='dmg', v=24, lv=[3, 26.4], d=0, bk='p_dd', n='昔涟献予「大地」之诗：持有时【同袍】造成的伤害 +24%（同袍 = 模板里的第一个队友）'))
# 白厄：永续的燃烧
add(1408,
    dict(y='life', t='smOn', sk='khaslana', tg='sm:khaslana', v=8, ns='献予「负世」之诗', n='昔涟献予「负世」之诗：变身时获得【永续的燃烧】，卡厄斯兰那的额外回合耗尽后不结束变身、刷新全部额外回合（按多 8 次行动；每个额外回合开始消耗 15% 当前生命值、4 点毁伤没算）'),
    D(t='smOn', sk='khaslana', tg='self', ns='献予「负世」之诗', m='cr', v=16, lv=[3, 17.6], d=0, bk='p_fs', n='昔涟献予「负世」之诗：持有【永续的燃烧】时卡厄斯兰那暴击率 +16%'),
    D(t='smEnd', sk='khaslana', tg='self', m='cr', v=0, d=0, bk='p_fs', n='昔涟献予「负世」之诗：变身结束，暴击率加成取消'),
    D(t='smOn', sk='khaslana', tg='self', ns='献予「负世」之诗', m='rx', sc='fs', v=1, d=0, bk='p_fsx', n='额外伤害标记：【永续的燃烧】卡厄斯兰那攻击后 5 次各 10% 攻击力的附加伤害'),
    D(t='smEnd', sk='khaslana', tg='self', m='rx', v=0, d=0, bk='p_fsx', n='额外伤害标记：变身结束'))

# ---------------- 1501 火花 ----------------
drop(1501, '行迹沸腾！真伪调色盘')
eid_drop(1501, 1, 'E1：每有 1 个笑点我方全体全属性抗性穿透')
eid_note_drop(1501, 1, 'E1 #全网热搜') if any('E1 #全网热搜' in x for x in eid(1501, 1)['notes']) else None
x = eid_find(1501, 2, 'E2：每消耗 1 个爆点')
x.update(t='skill', n='E2：每消耗 1 个爆点暴击伤害 +10%，持续 2 回合，最多 4 层（按每次施放战技消耗 1 个爆点）'); x.pop('off', None)
eid_note_drop(1501, 6, 'E6 #锵锵')
note_drop(1501, '行迹沸腾！真伪调色盘')
add(1501, dict(y='sp', t='start', tg='self', v=2, off=1, n='秘技流量变现：进入战斗后为我方恢复 2 个战技点（主动攻击【拉黑】的敌人进战时启用）'))
C[1501]['notes'].append('行迹沸腾！真伪调色盘（每个笑点我方全体暴伤 +8%，最多 80%）和 1 魂（每个笑点全属性抗性穿透 +1.5%，最多 15%）按出手时队伍持有的笑点自动算（阿哈时刻里按清零前计入的笑点）')

# ---------------- 1503 真珠 ----------------
x = eid_find(1503, 6, 'E6：我方全体欢愉伤害增笑 15%'); eid(1503, 6)['eff'].remove(x)
x['n'] = 'E2：我方全体欢愉伤害增笑 15%'; x['bk'] = 'e2lm'; eid(1503, 2)['eff'].append(x)
eid_note_drop(1503, 2, 'E2：我方全体欢愉伤害增笑 15%')
eid_find(1503, 6, 'E6：【深度学习】时我方全体全属性抗性穿透')['n'] = 'E6：【深度学习】时我方全体全属性抗性穿透 +20%（按开大后 3 回合算，近似；强化普攻额外的 240% 欢愉伤害在伤害里算）'

# ---------------- 1505 绯英 ----------------
eid_drop(1505, 6, 'E6：每持有 100 点好活当赏额外增笑 2%')
eid_find(1505, 6, 'E6：绯英欢愉伤害增笑 15%')['n'] = 'E6：绯英欢愉伤害增笑 15%（每持有 100 点好活当赏再 +2%、最多计入 1000 点，伤害里按出手时的好活当赏算）'

# ---------------- 1512 知更鸟•晴歌 ----------------
C[1512]['cnt']['lm'] = [2, 70]
add(1512,
    dict(y='energy', t='ult', tg='ultpick', m='maxp', v=20, n='终结技：目标固定恢复等同于其能量上限 20% 的能量'),
    dict(y='state', t='ult', tg='ultpick', sn='特邀嘉宾', v=1, d=2, ts='start', n='终结技：目标获得【特邀嘉宾】，持续 2 回合（目标每回合开始时 −1；持有者无法使其他友方行动提前没做）'),
    dict(y='count', t='atk', aw='all', **{'as': '特邀嘉宾'}, tg='self', v=2, n='终结技【特邀嘉宾】：持有者及其召唤物攻击时晴歌额外 +2 气氛值'),
    dict(y='count', t='aGive', aw='all', ptn=1, tg='self', v=1, n='天赋：任意目标回合内我方第一次提供治疗或护盾时 +1 气氛值'),
    dict(y='state', t='heal', o='shield', tg='self', sn='律动', v=0, n='行迹即兴蓝调：受到治疗或护盾时【律动】重置'),
    dict(y='state', t='heal', o='shield', tg='self', sn='律动', v=12, ts='chg', n='行迹即兴蓝调：知更鸟•晴歌受到治疗或护盾时获得 12 层【律动】（上限 12；晴空乐手受到的没算）'),
    dict(y='energy', t='cntUp', ptn=1, ns='律动', tg='self', m='fixed', v=3, n='行迹即兴蓝调：任意目标回合内第一次获得气氛值时若持有【律动】，固定恢复 3 点能量'),
    dict(y='state', t='cntUp', ptn=1, ns='律动', tg='self', sn='律动', v=-1, ts='chg', n='行迹即兴蓝调：消耗 1 层【律动】'),
    dict(y='advance', t='start', tg='self', v=20, off=1, n='秘技我们自成旋律：下一次战斗开始时行动提前 20%（用了秘技再启用）'),
    dict(y='count', t='start', tg='self', v=6, off=1, n='秘技我们自成旋律：立即获得 6 点气氛值（用了秘技再启用）'))
for sub in ['终结技：随后使其获得【特邀嘉宾】', '行迹即兴蓝调']: note_drop(1512, sub)
eid(1512, 2)['eff'].append(dict(y='count', t='atk', aw='all', ptn=1, tg='self', v=2, n='E2：任意目标回合内我方第一次施放技能使晴歌获得气氛值时额外 +2；气氛值上限 +20（70）'))
eid(1512, 4)['notes'] = []
eid(1512, 4)['eff'].extend([
    dict(y='count', t='smOn', sk='band', tg='self', v=12, n='E4：进入【Fever】时立即获得 12 点气氛值'),
    dict(y='spd', t='smOn', sk='band', tg='sm:band', m='pct', v=20, vc=[0.5, 70], d=0, bk='e4spd', n='E4：晴空乐手速度 +（20% + 气氛值 × 0.5%）'),
    dict(y='spd', t='cntUp', si='in', tg='sm:band', m='pct', v=20, vc=[0.5, 70], d=0, bk='e4spd', n='E4：晴空乐手加速——气氛值增加后刷新'),
    dict(y='spd', t='smTurn', sk='fever', tg='sm:band', m='pct', v=20, vc=[0.5, 70], d=0, bk='e4spd', n='E4：晴空乐手加速——倒计时扣气氛值后刷新')])
eid(1512, 6)['notes'] = []
eid(1512, 6)['eff'].extend([
    dict(y='energy', t='smOn', sk='band', first=1, tg='self', m='fixed', v=140, n='E6：本场战斗第一次进入【Fever】后固定恢复 140 点能量'),
    dict(y='energy', t='smTurn', sk='fever', tg='self', m='fixed', v=140, n='E6：【Fever】倒计时回合开始时固定恢复 140 点能量'),
    dict(y='ecap', t='smOn', sk='band', tg='self', v=200, n='E6：【Fever】时终结技最多储存 2 次（能量最多存到上限的 200%）'),
    dict(y='ecap', t='smEnd', sk='band', tg='self', v=100, n='E6：退出【Fever】，能量储存恢复 1 次')])

# ---------------- 1513 砂金•戏浪 ----------------
C[1513]['cnt'].update(keep=True, max=30, lm=[2, 50], ats=[[0, [10]], [1, [10, 20, 30]], [2, [10, 20, 30, 40, 50]]])
SET['1513'] = {'cntKeep': True, 'cntMax': 30}
patch(1513, '行迹纵享惊涛：队友攻击后 +1 笑点', maxEl=1, n='行迹纵享惊涛：只有砂金•戏浪 1 名欢愉角色时，队友攻击后 +1 笑点（+2 点好活当赏在伤害里算）')
patch(1513, '行迹纵享惊涛：阿哈速度 +25（到阿哈时刻结束）', maxEl=1, n='行迹纵享惊涛：只有砂金•戏浪 1 名欢愉角色时，队友攻击后阿哈速度 +25（到阿哈时刻结束）')
patch(1513, '行迹纵享惊涛：队伍里只有砂金•戏浪 1 名欢愉角色时，欢愉技视为追加攻击', maxEl=1, off=False, o='cnt', n='行迹纵享惊涛：只有砂金•戏浪 1 名欢愉角色时，欢愉技造成伤害时视为发动了追加攻击')
patch(1513, '行迹旧梦淘金：队友施放普攻、战技、追加攻击或终结技后', aw='oc', ac=6, acR='skill', o='aFua', n='行迹旧梦淘金：队友施放普攻、战技、追加攻击或终结技后我方全体暴击伤害 +48%，持续 3 回合（最多 6 次，砂金•戏浪施放战技时重置）')
add(1513,
    dict(y='count', t='skill', tg='self', v=4, n='战技：获得 4 点【热意】'),
    dict(y='count', t='ult', tg='self', v=8, n='终结技：获得 8 点【热意】'),
    dict(y='count', t='ally', o='aFua', aw='oc', au=1, ac=6, acR='skill', tg='self', v=2, n='行迹旧梦淘金：队友施放普攻、战技、追加攻击或终结技后额外获得 2 点【热意】（最多 6 次，砂金•戏浪施放战技时重置）'),
    dict(y='state', t='cnt', tg='self', sn='All in', v=1, d=0, n='天赋：施放【举杯】后，下一次在阿哈时刻中施放的欢愉技强化为【All in！敬炽烈一夏】'),
    dict(y='count', t='aha', tg='self', m='set', v=0, ns='All in', cmk='All in 消耗热意', n='天赋【All in！】：阿哈时刻中施放时消耗所有【热意】（每点额外 1 次随机单体 21% 欢愉伤害，伤害里算）'),
    dict(y='state', t='aha', tg='self', sn='All in', v=0, ns='All in', n='天赋【All in！】：施放后恢复为【举杯】'),
    dict(y='count', t='start', tg='self', v=2, off=1, n='秘技于静水掀起风浪：进入战斗后获得 2 点【热意】和 20 点好活当赏（用了秘技再启用；好活当赏没算）'))
eid(1513, 1)['notes'] = [x for x in eid(1513, 1)['notes'] if '热意' not in x]
eid(1513, 2)['notes'] = [x for x in eid(1513, 2)['notes'] if '热意' not in x]
eid(1513, 2)['eff'].extend([
    dict(y='count', t='aha', tg='self', v=4, n='E2：施放欢愉技后额外获得 4 点【热意】（阿哈时刻）'),
    dict(y='count', t='cnt', tg='self', v=4, n='E2：施放欢愉技后额外获得 4 点【热意】（热意达到门槛时的举杯）')])
eid(1513, 6)['notes'] = [x for x in eid(1513, 6)['notes'] if 'All in' not in x]
eid(1513, 6)['eff'].append(dict(y='state', t='aha', tg='self', sn='All in', v=1, d=0, n='E6：施放 2 次欢愉技后所有欢愉技都是【All in！】（按第 1 次阿哈时刻之后；阿哈时刻外的 All in 不消耗热意，伤害里算）'))

# ---------------- 8007 / 8008 开拓者•记忆 ----------------
for cid in (8007, 8008):
    if cid not in C: continue
    C[cid]['cnt']['src'] = 'tenergy'
    SET[str(cid)] = {'cntSrc': 'tenergy'}
    patch(cid, '忆灵天赋：充能满 100% 时迷迷立即行动', n='忆灵天赋：充能满 100% 时迷迷立即行动（我方全体每累计恢复 10 点能量 +1% 充能，已按模拟里的回能算）')
    old = find(cid, '战技：迷迷 +10% 充能'); DROP.setdefault(cid, []).append((old['n'], old['t']))
    k = C[cid]['eff'].index(old); C[cid]['eff'].remove(old)
    j = next(i for i, x in enumerate(C[cid]['eff']) if x['y'] == 'summon' and x['t'] == 'skill')
    nw = dict(y='count', t='skill', tg='self', v=10, si='in', n='战技：迷迷已在场时获得 10% 充能（先看在不在场，再召唤）')
    C[cid]['eff'].insert(j, nw); FIXADD.setdefault(cid, []).append(nw['n'])
    add(cid,
        dict(y='count', t='ebasic', tg='self', v=10, n='强化普攻【明天，一同写下！】：迷迷获得 10% 充能'),
        dict(y='count', t='ally', aw='sm', tg='self', v=5, n='行迹袖珍的事诗：迷迷施放【坏人！麻烦！】时获得 5% 充能'),
        dict(y='count', t='smOn', sk='mimi', first=1, tg='self', v=40, n='行迹追念之权杖：首次召唤迷迷时获得 40% 充能'),
        dict(y='delay', t='start', tg='enemies', v=50, off=1, n='秘技记忆如往日重现：与时停的敌人进入战斗后敌方全体行动延后 50%（用了秘技再启用）'))
    e1 = eid(cid, 1); e1['eff'] = [
        D(t='cnt', tg='$allym', m='cr', v=10, d=3, bk='e1', n='E1：持有【迷迷的声援】的目标暴击率 +10%（持有者 = 模板里的第一个队友；对它的忆灵也生效）'),
        D(t='cnt', tg='$allym', m='rx', sc='mimi', v=1, d=3, bk='rx', n='E1：【迷迷的声援】对持有者的忆灵也生效')]
    x = eid_find(cid, 2, 'E2：除迷迷以外的我方忆灵行动时'); x.update(aw='osm', ac=1, n='E2：除迷迷以外的我方忆灵行动时开拓者恢复 8 点能量（每回合 1 次）')
    eid(cid, 4)['notes'] = []
    eid(cid, 4)['eff'].append(dict(y='count', t='ally', aw='oc', au=1, ae0=1, tg='self', v=3, n='E4：能量上限为 0 的我方目标主动施放技能时迷迷也获得 3% 充能（声援的真实伤害 +6% 在伤害里算）'))

# ---------------- 8009 / 8010 开拓者•欢愉 ----------------
for cid in (8009, 8010):
    if cid not in C: continue
    patch(cid, '终结技（目标需有欢愉技）', te=1, n='终结技：目标拥有欢愉技（欢愉角色）时，使其立即施放 1 次固定计入 20 笑点的欢愉技')
    patch(cid, '终结技：目标没有欢愉技时行动提前 50%', te=-1, off=False)

# ---------------- DMG：遐蝶骸爪 = 遐蝶 + 死龙两段 ----------------
md = re.search(r'const DMG=(\{.*?\});\n', s); DM = json.loads(md.group(1))
off = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None
if off:
    p = off['140709']['params']
    DM['1407']['s2']['v'] = [round(x[1] + x[2], 4) for x in p]
    print('1407 s2', DM['1407']['s2']['v'][9])

# ---------------- 写回 ----------------
for cid, L in BASE.items():
    have = {e['n'] for e in C[cid]['eff']}
    for x in L: assert x['n'] not in have, ('重复说明', cid, x['n'])
    C[cid]['eff'].extend(L)
FIX = {}
for cid in set(BASE) | set(DROP) | {int(k) for k in PATCH} | {int(k) for k in SET}:
    dn = DROP.get(cid, [])
    FIX[str(cid)] = {'drop': [n for n, _ in dn], 'map': {}, 'trig': {n: t for n, t in dn}, 'add': [x['n'] for x in BASE.get(cid, [])] + FIXADD.get(cid, []), 'sm': {}}
    if str(cid) in SET: FIX[str(cid)]['set'] = SET[str(cid)]
s = s[:md.start(1)] + json.dumps(DM, ensure_ascii=False, separators=(',', ':')) + s[md.end(1):]
m = re.search(r'const DB = (\{.*?\});\n', s)
s = s[:m.start(1)] + json.dumps(DB, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
a = re.search(rf'  const fixTpl{TV - 1} = .*\n', s)
js = (f'  // tv {TV}：记忆 / 欢愉角色按官方原文补效果（PATCH = 老存档里原地改的效果字段，null = 删掉）\n'
      f'  const TPLFIX{TV} = ' + json.dumps(FIX, ensure_ascii=False) + ';\n'
      f'  const PATCH{TV} = ' + json.dumps(PATCH, ensure_ascii=False) + ';\n'
      f'  const fixTpl{TV} = s => {{\n'
      f'    for (const u of s.units) {{ const T = u.kind === "ally" && !u.sm ? tplOf(u) : null, P = T && PATCH{TV}[T.id]; if (!P) continue;\n'
      f'      for (const e of u.effects) if (!e.eq && P[e.note]) for (const [k, v] of Object.entries(P[e.note])) {{ if (v === null) delete e[k]; else e[k] = JSON.parse(JSON.stringify(v)); }} }}\n'
      f'    fixTpl(s, TPLFIX{TV});\n  }};\n')
s = s[:a.end()] + js + s[a.end():]
def rep(x, y):
    global s
    assert s.count(x) == 1, (x, s.count(x)); s = s.replace(x, y)
rep(f'if (s.tv >= {TV - 1}) return;', f'if (s.tv >= {TV}) return;')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep; }} s.tv = {TV - 1}; return; }}', f'if (!(s.tv >= {TV - 1})) fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep; }} s.tv = {TV}; return; }}')
rep(f'fixTpl{TV - 1}(s); }} finally {{ S = keep2; }} }}\n    s.tv = {TV - 1};', f'fixTpl{TV - 1}(s); fixTpl{TV}(s); }} finally {{ S = keep2; }} }}\n    s.tv = {TV};')
rep(f'if (!(S.tv >= {TV - 1})) {{ migrateTpl(S);', f'if (!(S.tv >= {TV})) {{ migrateTpl(S);')
open(P, 'w', encoding='utf-8').write(s)
print('ok tv', TV, {k: (len(v['add']), len(v['drop'])) for k, v in FIX.items()}, 'patch', {k: len(v) for k, v in PATCH.items()})
