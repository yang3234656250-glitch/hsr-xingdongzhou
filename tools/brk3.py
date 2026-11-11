"""击破：手动添加的敌人（没选怪物库模板）也能填韧性和弱点。用法：python3 tools/brk3.py index.html"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)
rep('''en.__mon = (en.mon && MON.m.find(m => m.n === en.mon)) || null; return en.__mon; };''',
    '''en.__mon = (en.mon && MON.m.find(m => m.n === en.mon)) || (en.wks ? { w: String(en.wks) } : null); return en.__mon; };   // 手动敌人：卡片上填的弱点''')
rep('''nd(m => m.n === u.mon))}</span>` : ""}
        </div>''', '''nd(m => m.n === u.mon))}</span>` : `<label for="tg-${u.id}" title="韧性：30 = 游戏里的 10 点（小怪一般 60～120，精英 240～360，首领 360～720）；不填 = 不模拟这个敌人的韧性和击破">韧性 <input type="number" id="tg-${u.id}" min="0" step="30" value="${u.tough ?? ""}" placeholder="不模拟" data-u="${i}" data-f="tough" style="width:70px"></label>
          <label for="wk-${u.id}" title="弱点属性，写属性的第一个字：物 火 冰 雷 风 量 虚，例如“火冰量”；不填 = 所有属性都算弱点">弱点 <input type="text" id="wk-${u.id}" value="${esc(u.wks || "")}" placeholder="全部" data-u="${i}" data-f="wks" style="width:76px"></label>`}
        </div>''')
rep('''      if (f === "tough" && el.value === "") delete u.tough;''', '''      if (f === "wks") { u.wks = String(el.value || "").replace(/[^物火冰雷风量虚]/g, ""); if (!u.wks) delete u.wks; }
      if (f === "tough" && el.value === "") delete u.tough;''')
li = '<li><b>2026-11-11（手动敌人也能填韧性）</b>：没选怪物库模板的敌人卡现在也有「韧性」和「弱点」两格（30 = 游戏里的 10 点；弱点写“火冰量”这样，不填 = 所有属性都算弱点）。韧性不填就和以前一样不模拟击破，已有方案不变。</li>'
i = s.index('<li>', s.index('id="changelog"')); s = s[:i] + li + '\n' + ' ' * 14 + s[i:]
open(p, 'w', encoding='utf8').write(s); print('ok')
