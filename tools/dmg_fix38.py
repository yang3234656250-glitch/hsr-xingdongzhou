"""tv 38：翡翠【收债人】额外伤害标记。"""
import sys; sys.path.insert(0, 'tools')
from dmgbatch import run, D
BASE = {1314: [D(t='skill', tg='$ally', m='rx', v=1, sc='jade', d=3, bk='rx', n='额外伤害标记：【收债人】（3 回合，收债人 = 模板里的第一个队友）')]}
run(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 38, BASE, {}, {}, {}, '翡翠收债人标记')
