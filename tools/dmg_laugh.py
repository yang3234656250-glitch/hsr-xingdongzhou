"""增笑：欢愉伤害单独的乘区（1 + 增笑），按官方原文给 5 个 6 魂补上。"""
import sys; sys.path.insert(0, 'tools')
from dmgbatch import run, D
EID = {
 1502: {6: [D(t='start', tg='team', m='lm', v=25, d=0, bk='e6lm', n='E6：我方全体欢愉伤害增笑 25%')]},
 1503: {6: [D(t='start', tg='team', m='lm', v=15, d=0, bk='e6lm', n='E6：我方全体欢愉伤害增笑 15%')]},
 1505: {6: [D(t='start', tg='self', m='lm', v=15, d=0, bk='e6lm', n='E6：绯英欢愉伤害增笑 15%'),
            D(t='start', tg='self', m='lm', v=20, d=0, bk='e6lm2', off=1, n='E6：每持有 100 点好活当赏额外增笑 2%，最多 1000 点（按满额写，需要时启用）')]},
 1506: {6: [D(t='start', tg='self', m='lm', v=50, sc='eb', d=0, bk='e6lm', n='E6：强化普攻期间造成的欢愉伤害增笑 50%')]},
 1513: {6: [D(t='start', tg='self', m='lm', v=25, d=0, bk='e6lm', n='E6：砂金•戏浪欢愉伤害增笑 25%')]},
}
run(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 36, {}, EID, {}, {}, '增笑')
