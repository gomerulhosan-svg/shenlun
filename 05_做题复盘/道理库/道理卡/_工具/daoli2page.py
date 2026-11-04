"""把 道理卡/ 下的 md 合成一个单文件网页。用法：python3 daoli2page.py <道理卡目录> <输出html>"""
import re, io, sys, html, glob, os

src_dir, out = sys.argv[1], sys.argv[2]
PAGE_TITLE = sys.argv[3] if len(sys.argv) > 3 else None
PAGE_INTRO = sys.argv[4] if len(sys.argv) > 4 else None
files = sorted(f for f in glob.glob(os.path.join(src_dir, '*.md')))
order = ['00_优先级', '00_说明', '00_怎么用', '00_B是什么', '00_总纲'] + [f'{i:02d}_' for i in range(1, 100)]
def key(f):
    b = os.path.basename(f)
    for i, o in enumerate(order):
        if b.startswith(o):
            return i
    return 99
files.sort(key=key)

def tags(s):
    out = []; depth = 0; buf = ''
    for ch in s:
        if ch == '〔':
            if depth == 0:
                out.append(buf); buf = ''
            depth += 1; buf += ch
        elif ch == '〕' and depth > 0:
            depth -= 1; buf += ch
            if depth == 0:
                body = buf[1:]
                cls = 'pin' if body.startswith(('拼', '自拟')) else ('hf' if body.startswith(('高分卷', '参考范文')) or '参考范文' in body[:12] else 'tag')
                out.append(buf if buf == '〔B〕' else f'<span class="{cls}">{buf}</span>'); buf = ''
        else:
            buf += ch
    out.append(buf)
    return ''.join(out)

def inline(s):
    s = html.escape(s, quote=False).replace('&lt;br&gt;', '<br>')
    s = tags(s)
    s = re.sub(r'^([^：「」〔【<>*]{1,12})：', r'<span class="lb">\1：</span>', s)
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
                h.append('<tr>' + ''.join(f'<td data-label="{html.escape(re.sub(r"[*`]", "", head[k]) if k < len(head) else "")}">{inline(c)}</td>' for k, c in enumerate(r)) + '</tr>')
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
                out_html.append(('<li class="lz">' if txt.startswith('例子要证') else '<li class="zl">' if txt.startswith('作用链') else '<li>') + inline(txt))
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
    if base.startswith('00_优先级'):
        short = '先读哪个'
    elif base.startswith('00_说明'):
        short = '说明'
    elif base.startswith('00_'):
        short = re.sub(r'^\d+ ', '', title).split('：')[0].replace('道理卡', '').strip() or '怎么用'
    else:
        short = re.sub(r'^\d+ ', '', title).split('：')[0]
        if len(short) > 9:
            short = re.split(r'[、与]', short)[0]
    chips.append(f'<a class="chip{" chip2" if idx < 3 else ""}" href="#{sid}">{html.escape(short)}</a>')
    opened = ' open' if idx < 1 else ''
    sections.append(f'<details id="{sid}"{opened}><summary><h2>{inline(title)}</h2></summary><div class="sec">{render(rest, 1)}</div></details>')

css = """
:root{--bg:#f5f6f8; --surface:#ffffff; --surface2:#eef0f3; --line:#d9dde3; --fg:#1d2127; --muted:#5b6471;
  --accent:#a3322b; --accent-soft:#f6e3e1; --quote:#2b3a4a; --warn:#9a5b00; --ok:#2f6b3f;
  --serif:"Noto Serif SC","Songti SC","STSong",serif; --sans:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#121418; --surface:#191c22; --surface2:#20242b; --line:#2d323a; --fg:#e5e7ea; --muted:#9aa3ad; --accent:#e2776e; --accent-soft:#3a2321; --quote:#c9d4df; --warn:#e0a84f; --ok:#7cc48f; color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121418; --surface:#191c22; --surface2:#20242b; --line:#2d323a; --fg:#e5e7ea; --muted:#9aa3ad; --accent:#e2776e; --accent-soft:#3a2321; --quote:#c9d4df; --warn:#e0a84f; --ok:#7cc48f; color-scheme:dark}
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
.tag{font-size:12.5px; color:var(--muted)} .pin{font-size:12.5px; color:var(--warn); font-weight:600} .hf{font-size:12.5px; color:var(--ok)}
.lb{font-weight:600; color:var(--accent)} li.lz{color:var(--muted)} li.lz .lb{color:var(--ok)} li.zl .lb{color:var(--ok)}
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
@media (max-width: 640px){
  .tbl.wide{overflow:visible; border:none; background:none}
  .tbl.wide table{min-width:0}
  .tbl.wide thead{display:none}
  .tbl.wide tr{display:block; border:1px solid var(--line); border-radius:6px; margin-bottom:8px; background:var(--surface); padding:6px 10px}
  .tbl.wide td{display:block; border:none; padding:3px 0; min-width:0}
  .tbl.wide td::before{content:attr(data-label) "："; font-weight:600; color:var(--accent)}
  .tbl.wide td:first-child::before{content:""}
}
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
<title>道理卡</title>
<meta name="description" content="广东省考申论大作文 2026-12-07：十六件事的论点句、道理句和例子要证的那一环，考场上认出来就用">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600&family=Noto+Serif+SC:wght@600;700&display=swap">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header><div class="eyebrow">广东省考申论 · 大作文 · 2026-12-07</div><h1>道理卡：认出来就用</h1>
<p>十六件事加总纲和"B 是什么"。每件事：他要你证明什么、开头几句、每一面的论点和道理、例子要证的那一环、结尾。「」里是原文逐字，【】是文件和行号，〔2024二卷 材料六〕是真题材料，都用脚本核过；<span class="pin">〔拼〕</span>是拼的，原文里没有这句话。</p>
<nav class="toc" aria-label="目录">{''.join(chips)}</nav>
<div class="tools"><button type="button" onclick="setAll(true)">全部展开</button><button type="button" onclick="setAll(false)">全部收起</button></div></header>
{''.join(sections)}
</div>
<script>{js}</script>
</body>
</html>
"""
if PAGE_TITLE:
    page = page.replace('<title>道理卡</title>', f'<title>{html.escape(PAGE_TITLE)}</title>').replace('<h1>道理卡：认出来就用</h1>', f'<h1>{html.escape(PAGE_TITLE)}</h1>')
if PAGE_INTRO:
    page = re.sub(r'(</h1>\n)<p>.*?</p>', lambda m: m.group(1) + '<p>' + inline(PAGE_INTRO) + '</p>', page, count=1, flags=re.S)
io.open(out, 'w', encoding='utf-8').write(page)
print('ok', len(page), 'chars;', len(files), 'files')
