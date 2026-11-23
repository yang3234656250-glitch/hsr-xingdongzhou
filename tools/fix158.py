"""tv 158（2026-11-23）：差异清单第 34 批
1. 大丽花 1321 E1（132101）“对受到攻击的敌方目标额外造成等同于其韧性上限25%的固定削韧”：两条 tfix 目标 efirst → ehit（每个被击中的敌人）。
2. 海瑟音 1410 天赋（141004）“使被击中的敌方目标陷入……其中1种状态”和 E1：目标 efirst → ehit。
3. 阿格莱雅 1402 E1（140201）“阿格莱雅或衣匠攻击该目标后额外恢复20点能量”：两条回能加 si in（衣匠在场时阿格莱雅攻击会挂【间隙织线】），默认开。
4. 貊泽 1223 行迹墨毫绣衣（1223102）“施放天赋的追加攻击后，恢复1个战技点，该效果在1回合后可再次触发”：加 cdt 1（冷却 1 回合），默认开。

用法：python3 tools/fix158.py index.html <官方 json 目录>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixlib import Fix

TV = 158
F = Fix(sys.argv[1], TV, sys.argv[2])


def fix_of(cid):
    return F.FIX.setdefault(str(cid), {'drop': [], 'trig': {}, 'map': {}, 'add': [], 'sm': {}})


def swap(cid, oldn, oldt, newn, was_off=False):
    fx = fix_of(cid)
    fx['drop'].append(oldn); fx['trig'][oldn] = oldt; fx['map'][oldn] = newn; fx['add'].append(newn); fx['keep'] = 1
    if was_off: fx.setdefault('off0', []).append(oldn)


# 1. 大丽花 E1
F.has('r:132101', '对受到攻击的敌方目标额外造成等同于其韧性上限#的固定削韧')
L = [x for x in F.eid(1321, 1)['eff'] if x['y'] == 'tfix']; assert len(L) == 2
for x in L:
    assert x['tg'] == 'efirst'; x['tg'] = 'ehit'; x['n'] = x['n'].replace('（按主目标算）', '（每个受到攻击的敌人）')
# 2. 海瑟音天赋 / E1
F.has('141004', '使被击中的敌方目标')
e = F.eff(1410, '天赋：我方目标攻击时，使被击中的敌方目标陷入'); oldn = e['n']
assert e['tg'] == 'efirst'; e['tg'] = 'ehit'; e['n'] = oldn.replace('（按主目标；', '（每个被击中的敌人；')
swap(1410, oldn, 'atk', e['n'])
L = [x for x in F.eid(1410, 1)['eff'] if x['y'] == 'dot']; assert len(L) == 1 and L[0]['tg'] == 'efirst'
L[0]['tg'] = 'ehit'
# 3. 阿格莱雅 E1
F.has('r:140201', '阿格莱雅或衣匠攻击该目标后额外恢复#点能量')
L = [x for x in F.eid(1402, 1)['eff'] if x['y'] == 'energy']; assert len(L) == 2 and all(x.get('off') == 1 for x in L)
for x, who in zip(L, ('阿格莱雅', '衣匠')):
    del x['off']; x['si'] = 'in'; x['n'] = f'E1：{who}攻击【间隙织线】的敌人后额外恢复 20 点能量（衣匠在场时）'
# 4. 貊泽墨毫绣衣
F.hast(1223, '墨毫绣衣', '施放天赋的追加攻击后，恢复#个战技点，该效果在#回合后可再次触发')
e = F.eff(1223, '行迹墨毫绣衣：天赋的追加攻击后恢复 1 个战技点'); oldn = e['n']
assert e.get('off') == 1
del e['off']; e['cdt'] = 1; e['n'] = '行迹墨毫绣衣：施放天赋的追加攻击后恢复 1 个战技点（1 回合后可再次触发）'
swap(1223, oldn, 'fua', e['n'], True)

log = """<li><b>2026-11-23（差异清单第 34 批）：tv 158（tools/fix158.py）</b>。① 大丽花 E1 的固定削韧、② 海瑟音天赋 / E1 的风化 / 裂伤 / 灼烧 / 触电改成对<b>每个被击中的敌人</b>（以前只给主目标）；③ 阿格莱雅 E1“攻击【间隙织线】目标后回 20 能量”在衣匠在场时默认开启（以前默认关）；④ 貊泽行迹墨毫绣衣“天赋追加攻击后 +1 战技点，1 回合后可再次触发”加上冷却、默认开启。<b>对已有配置</b>：有阿格莱雅（1 魂以上）、貊泽的方案能量 / 战技点会变，开大时机可能变；大丽花、海瑟音只在放了多个敌人时影响伤害 / 削韧。</li>"""
record = """2026-11-23（差异清单第 34 批）：tv 158（tools/fix158.py）。大丽花 E1 tfix → ehit；海瑟音天赋 / E1 → ehit；阿格莱雅 E1 回能 si in 默认开；貊泽墨毫绣衣 cdt 1 默认开。"""
F.finish('差异清单第 34 批（大丽花 E1、海瑟音、阿格莱雅 E1、貊泽墨毫绣衣）', log, record)
print('done tv', TV)
