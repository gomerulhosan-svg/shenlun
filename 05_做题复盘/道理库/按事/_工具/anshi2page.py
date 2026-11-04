"""把 按事/ 下的十七份 md 合成一个单文件网页。用法：python3 anshi2page.py <按事目录> <输出html>"""
import re, io, sys, html, glob, os

src_dir, out = sys.argv[1], sys.argv[2]
files = sorted(f for f in glob.glob(os.path.join(src_dir, '*.md')))
order = ['00_名单', '00_总纲'] + [f'{i:02d}_' for i in range(1, 17)]
def key(f):
    b = os.path.basename(f)
    for i, o in enumerate(order):
        if b.startswith(o):
            return i
    return 99
files.sort(key=key)

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'「([^」]*)」', r'<span class="yw">「\1」</span>', s)
    s = re.sub(r'【([^】]*)】', r'<span class="src">【\1】</span>', s)
    return s

def render(lines, shift):
    """markdown → html 片段；标题级别整体下沉 shift 级"""
    body = []; i = 0; n = len(lines); para = []
    def flush():
        nonlocal para
        if para:
            body.append('<p>' + inline(' '.join(x.strip() for x in para)) + '</p>'); para = []
    while i < n:
        l = lines[i]
        m = re.match(r'^(#{1,4}) (.*)$', l)
        if m:
            flush(); lvl = min(len(m.group(1)) + shift, 5)
            body.append(f'<h{lvl}>{inline(m.group(2).strip())}</h{lvl}>'); i += 1; continue
        if l.strip() == '---':
            flush(); i += 1; continue
        if l.startswith('|'):
            flush(); rows = []
            while i < n and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            head, rest = rows[0], rows[2:]
            cls = 'tbl wide' if len(head) >= 4 else 'tbl'
            h = [f'<div class="{cls}"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>']
            for r in rest:
                h.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>')
            h.append('</tbody></table></div>'); body.append(''.join(h)); continue
        mm = re.match(r'^(\s*)(-|\d+\.)\s+(.*)$', l)
        if mm:
            flush(); items = []
            while i < n:
                m2 = re.match(r'^(\s*)(-|\d+\.)\s+(.*)$', lines[i])
                if m2:
                    items.append((len(m2.group(1)) // 2, 'ol' if m2.group(2)[0].isdigit() else 'ul', m2.group(3))); i += 1
                elif lines[i].strip() and lines[i].startswith('  ') and items:
                    lvl, kind, txt = items[-1]; items[-1] = (lvl, kind, txt + ' ' + lines[i].strip()); i += 1
                else:
                    break
            out_html = []; stack = []
            for lvl, kind, txt in items:
                while len(stack) > lvl + 1:
                    out_html.append(f'</li></{stack.pop()}>')
                if len(stack) == lvl + 1:
                    out_html.append('</li>')
                while len(stack) < lvl + 1:
                    stack.append(kind); out_html.append(f'<{kind}>')
                out_html.append('<li>' + inline(txt))
            while stack:
                out_html.append(f'</li></{stack.pop()}>')
            body.append(''.join(out_html)); continue
        if l.startswith('> '):
            flush(); q = []
            while i < n and lines[i].startswith('> '):
                q.append(lines[i][2:]); i += 1
            body.append('<blockquote><p>' + inline(' '.join(q)) + '</p></blockquote>'); continue
        if not l.strip():
            flush(); i += 1; continue
        para.append(l); i += 1
    flush()
    return ''.join(body)

sections = []; chips = []
for idx, f in enumerate(files):
    lines = io.open(f, encoding='utf-8').read().split('\n')
    title = next((l[2:].strip() for l in lines if l.startswith('# ')), os.path.basename(f))
    rest = [l for l in lines if not l.startswith('# ')]
    sid = f'e{idx}'
    base = os.path.basename(f)
    if base.startswith('00_名单'):
        short = '名单'
    elif base.startswith('00_总纲'):
        short = '总纲'
    else:
        short = re.sub(r'^\d+ ', '', title).split('：')[0]
        if len(short) > 9:
            short = short.split('、')[0]
    chips.append(f'<a class="chip{" chip2" if idx < 2 else ""}" href="#{sid}">{html.escape(short)}</a>')
    opened = ' open' if idx < 2 else ''
    sections.append(f'<details id="{sid}"{opened}><summary><h2>{inline(title)}</h2></summary><div class="sec">{render(rest, 1)}</div></details>')

css = """
:root{--bg:#f5f6f8; --surface:#ffffff; --surface2:#eef0f3; --line:#d9dde3; --fg:#1d2127; --muted:#5b6471;
  --accent:#a3322b; --accent-soft:#f6e3e1; --quote:#2b3a4a;
  --serif:"Noto Serif SC","Songti SC","STSong",serif; --sans:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#121418; --surface:#191c22; --surface2:#20242b; --line:#2d323a; --fg:#e5e7ea; --muted:#9aa3ad; --accent:#e2776e; --accent-soft:#3a2321; --quote:#c9d4df; color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121418; --surface:#191c22; --surface2:#20242b; --line:#2d323a; --fg:#e5e7ea; --muted:#9aa3ad; --accent:#e2776e; --accent-soft:#3a2321; --quote:#c9d4df; color-scheme:dark}
*{box-sizing:border-box} body{margin:0}
body{background:var(--bg); color:var(--fg); font-family:var(--sans); font-size:15.5px; line-height:1.8;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 64px}
.wrap{max-width:46em; margin:0 auto; display:flex; flex-direction:column; gap:12px; min-width:0}
header{display:flex; flex-direction:column; gap:10px; padding-bottom:16px; border-bottom:2px solid var(--accent)}
.eyebrow{font-size:12.5px; letter-spacing:.12em; color:var(--accent)}
h1{font-family:var(--serif); font-size:28px; line-height:1.3; margin:0; text-wrap:balance}
h2{font-family:var(--serif); font-size:19px; line-height:1.4; margin:0; display:inline; text-wrap:balance}
h3{font-family:var(--serif); font-size:17px; margin:16px 0 0; padding-top:10px; border-top:1px solid var(--line)}
h4{font-size:15.5px; margin:12px 0 0; color:var(--accent)}
p{margin:0} p,li,td,th,summary{overflow-wrap:anywhere}
ul,ol{margin:0; padding-left:1.25em; display:flex; flex-direction:column; gap:5px}
li ul, li ol{margin-top:4px} li::marker{color:var(--muted)}
strong{font-weight:600}
code{font-size:.88em; background:var(--surface2); padding:1px 5px; border-radius:4px; word-break:break-all}
.yw{color:var(--quote)} .src{font-size:12px; color:var(--muted)}
blockquote{margin:0; padding:8px 12px; border-left:3px solid var(--accent); background:var(--accent-soft); border-radius:0 6px 6px 0}
.toc{display:flex; flex-wrap:wrap; gap:6px}
.chip{font-size:13px; text-decoration:none; color:var(--fg); background:var(--surface); border:1px solid var(--line); border-radius:999px; padding:2px 10px}
.chip2{border-color:var(--accent); color:var(--accent)}
.tools{display:flex; gap:8px; flex-wrap:wrap}
button{font:inherit; font-size:13px; color:var(--fg); background:var(--surface); border:1px solid var(--line); border-radius:999px; padding:3px 12px; cursor:pointer}
.chip:focus-visible, a:focus-visible, summary:focus-visible, button:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.tbl{overflow-x:auto; border:1px solid var(--line); border-radius:6px; background:var(--surface); margin-top:8px}
table{border-collapse:collapse; width:100%; font-size:14px; line-height:1.65}
.tbl.wide table{min-width:640px}
th,td{text-align:left; vertical-align:top; padding:7px 9px; border-bottom:1px solid var(--line)}
th{background:var(--surface2); font-weight:600; white-space:nowrap}
tr:last-child td{border-bottom:none}
td:first-child{font-weight:600; min-width:4em}
details{background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:10px 14px}
details[open]{padding-bottom:16px}
summary{cursor:pointer; list-style:none; display:flex; gap:8px; align-items:baseline}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸"; color:var(--accent); flex:none}
details[open]>summary::before{content:"▾"}
.sec{display:flex; flex-direction:column; gap:8px; margin-top:6px}
.sec>p:first-child{margin-top:4px}
html{scroll-behavior:smooth} @media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
"""
js = """
function setAll(o){document.querySelectorAll('details').forEach(d=>d.open=o)}
function openHash(){var h=location.hash&&document.querySelector(location.hash); if(h&&h.tagName==='DETAILS'){h.open=true}}
window.addEventListener('hashchange',openHash); openHash();
"""
page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2026 候选池：按事</title>
<meta name="description" content="广东省考申论大作文 2026-12-07 候选池，按出题人的"事"列，每件事四样齐全">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600&family=Noto+Serif+SC:wght@600;700&display=swap">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header><div class="eyebrow">广东省考申论 · 大作文 · 2026-12-07</div><h1>候选池：按出题人的"事"列</h1>
<p>十六件事加一份总纲。每件事：总书记怎么定性、省委的意义句和原则句、报告的成绩段和 2026 年安排、官方拆的面、省委承认的代价、考过没有、可搭问题二的文件、命题人会怎么出。「」里的字和 <code>04_文件原文/</code> 逐字一致，【】是文件编号和行号，脚本核过 402 处。</p>
<nav class="toc" aria-label="目录">{''.join(chips)}</nav>
<div class="tools"><button type="button" onclick="setAll(true)">全部展开</button><button type="button" onclick="setAll(false)">全部收起</button></div></header>
{''.join(sections)}
</div>
<script>{js}</script>
</body>
</html>
"""
io.open(out, 'w', encoding='utf-8').write(page)
print('ok', len(page), 'chars;', len(files), 'files')
