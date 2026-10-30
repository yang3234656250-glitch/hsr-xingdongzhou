"""把仓库的 index.html 去掉发布外壳（第一行 <!doctype html><html><head>…<body> 和末尾的 </body></html>），
写成可以用 Artifact 发布到 claude.ai 页面的文件。
用法：python3 tools/pub.py index.html 输出路径（比如 /tmp/…/scratchpad/publish/index.html）"""
import sys, os
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read().replace('\r\n', '\n')
L = s.split('\n'); assert L[0].startswith('<!doctype html><html><head>'), '第一行不是发布外壳'
body = '\n'.join(L[1:]).rstrip(); assert body.endswith('</body></html>'), '结尾不是 </body></html>'
body = body[:-len('</body></html>')]
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, 'w', encoding='utf-8').write(body)
print('ok', out, len(body))
