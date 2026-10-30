// 改前 / 改后对比：用模板队伍跑两份页面，比较行动顺序表（去掉伤害数字）和每轮行动次数，并报告页面报错。
// 用法：node tools/regress.js 旧.html 新.html ['[["1409","1407","1413","1415"],…]'] [星魂 0-6]
// 旧.html 一般用 git show HEAD:index.html > /tmp/old.html 得到。需要 Playwright（云端环境已装好）。
const { chromium } = require('playwright');
const path = require('path');
const [oldF, newF, teamsArg, eidArg] = process.argv.slice(2);
const teams = teamsArg ? JSON.parse(teamsArg) : [["1409", "1407", "1413", "1415"], ["1506", "1511", "1504", "1505"], ["1112", "1005", "1308", "1217"], ["1212", "1309", "1306", "1303"]];
async function run(b, file, team) {
  const p = await b.newPage({ viewport: { width: 1400, height: 1100 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(file)); await p.waitForTimeout(1200);
  const opts = await p.evaluate(() => [...document.querySelectorAll('[data-preset="0"] option')].map(o => o.value));
  for (let i = 0; i < 4; i++) { const v = 'db:' + team[i]; if (!opts.includes(v)) { errs.push('没有模板 ' + team[i]); continue; } await p.selectOption(`[data-preset="${i}"]`, v); await p.waitForTimeout(300); }
  if (eidArg != null) { await p.evaluate(e => document.querySelectorAll('[id^=ei-]').forEach(s => { s.value = e; s.dispatchEvent(new Event('change', { bubbles: true })); }), String(eidArg)); await p.waitForTimeout(500); }
  const r = await p.evaluate(() => {
    const t = document.querySelector('#t-order').cloneNode(true);
    t.querySelectorAll('.dmg-cell').forEach(c => c.remove());
    t.querySelectorAll('th').forEach(th => { if (th.textContent.trim() === '伤害') th.remove(); });
    const out = t.innerText.trim().replace(/｜伤害 [0-9.,万亿k]+/g, '');
    const sum = document.querySelector('#t-summary tbody').innerText.split('\n');
    return { out: out + '\n' + sum.filter(l => !l.includes('伤害合计')).join('\n').trim(), dmg: sum.filter(l => l.includes('伤害合计')).join(' ') };
  });
  await p.close(); return Object.assign(r, { errs });
}
(async () => {
  const b = await chromium.launch();
  for (const [k, t] of teams.entries()) {
    const a = await run(b, oldF, t), n = await run(b, newF, t);
    console.log(k, t.join(','), a.out === n.out ? 'SAME' : 'DIFF', '报错:', JSON.stringify(a.errs.concat(n.errs).slice(0, 3)));
    if (/NaN|Infinity/.test(n.dmg)) console.log('  伤害有 NaN：', n.dmg);
    if (a.out !== n.out) { const A = a.out.split('\n'), N = n.out.split('\n'); let c = 0; for (let i = 0; i < Math.max(A.length, N.length) && c < 6; i++) if (A[i] !== N[i]) { console.log('  旧:', A[i]); console.log('  新:', N[i]); c++; } }
  }
  await b.close();
})();
