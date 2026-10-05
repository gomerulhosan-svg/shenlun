# 说书版生成脚本：把 parts/*.md 里的批注插进原文，生成一个自带样式的 HTML。
#
# 批注块格式（写在 parts/*.md 里）：
#   @@ <行号> <句号k>   插在原文该行第 k 句之后（k 从 0 数，可写 last）
#   @@ PRE <行号>       插在该行之前（开讲前）
#   @@ CLOSE <行号>     插在该行最后一句之后，作为这一条的收尾
# 行号、句号以 04_文件原文/01_2026广东省政府工作报告.md 为准，用 sents.py 查。
# 用法：python3 build.py
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, '04_文件原文', '01_2026广东省政府工作报告.md')
OUT = os.path.join(ROOT, '01_大方向解读', '2026政府工作报告', '2026广东省政府工作报告_说书版.html')

L = open(SRC, encoding='utf-8').read().split('\n')


def split(t):
    s = re.findall(r'[^。]*。', t)
    rest = t[len(''.join(s)):]
    return s + ([rest] if rest else [])


# ---------- 读批注 ----------
notes = {}  # ('after', line, k) / ('pre', line) -> [(kind, lines)]
for fn in sorted(os.listdir(os.path.join(HERE, 'parts'))):
    if not fn.endswith('.md'):
        continue
    cur = None
    for raw in open(os.path.join(HERE, 'parts', fn), encoding='utf-8').read().split('\n'):
        m = re.match(r'^@@\s+(PRE|CLOSE)?\s*(\d+)(?:\s+(\d+|last))?\s*$', raw)
        if m:
            kind, ln = m.group(1), int(m.group(2))
            if kind == 'PRE':
                key = ('pre', ln)
            else:
                n = len(split(L[ln - 1]))
                k = n - 1 if kind == 'CLOSE' or m.group(3) in (None, 'last') else int(m.group(3))
                assert L[ln - 1].strip() and 0 <= k < n, (fn, raw, n)
                key = ('after', ln, k)
            cur = []
            notes.setdefault(key, []).append(((kind or 'note').lower(), cur))
            continue
        if cur is not None:
            cur.append(raw)


# ---------- 批注里的 markdown（只用到粗体、行内代码、列表、表格）----------
def curly(t):
    # 批注里用的是直引号，网页上换成中文弯引号（成对才换）
    if t.count('"') % 2:
        return t
    out, left = [], True
    for ch in t:
        if ch == '"':
            out.append('\u201c' if left else '\u201d')
            left = not left
        else:
            out.append(ch)
    return ''.join(out)


def inline(t):
    t = html.escape(curly(t), quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    return t


def md_blocks(lines):
    blocks, cur = [], []
    for l in lines + ['']:
        if l.strip():
            cur.append(l)
        elif cur:
            blocks.append(cur)
            cur = []
    return blocks


def md(lines):
    out = []
    blocks = md_blocks(lines)
    i = 0
    while i < len(blocks):
        b = blocks[i]
        first = b[0].strip()
        if first.startswith('**这一条用到的数从哪来'):
            inner = md_render(blocks[i + 1:])
            out.append('<details class="src"><summary>数字从哪来</summary>' + inner + '</details>')
            break
        out.append(md_render([b]))
        i += 1
    return '\n'.join(out)


def md_render(blocks):
    out = []
    for b in blocks:
        if all(l.strip().startswith('|') for l in b):
            rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in b]
            head, body = rows[0], [r for r in rows[2:]]
            t = '<div class="tbl"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
            for r in body:
                t += '<tr>' + ''.join(('<td class="nw">' if len(c.replace('*', '')) <= 4 else '<td>') + inline(c) + '</td>' for c in r) + '</tr>'
            out.append(t + '</tbody></table></div>')
        elif all(l.strip().startswith('- ') for l in b):
            out.append('<ul>' + ''.join(f'<li>{inline(l.strip()[2:])}</li>' for l in b) + '</ul>')
        else:
            text = ''.join(l.strip() for l in b)
            cls = ' class="later"' if text.startswith('**后话') else ''
            out.append(f'<p{cls}>{inline(text)}</p>')
    return '\n'.join(out)


LABEL = {'pre': '开讲前', 'note': '说书', 'close': '收'}


def note_html(items):
    out = []
    for kind, lines in items:
        out.append(f'<aside class="note {kind}"><span class="tag">{LABEL[kind]}</span>{md(lines)}</aside>')
    return '\n'.join(out)


# ---------- 原文分组 ----------
SEC_HEADS = [i for i, l in enumerate(L, 1) if re.match(r'^（[一二三四五六七八九十]+）', l)]
SEC_NAMES = ['大湾区', '产业体系', '科技创新', '扩内需', '改革', '开放', '百千万', '城市', '海洋',
             '绿美生态', '文化', '民生', '安全', '政府自身建设']
CN = '一二三四五六七八九十'
last = len(L)
while not L[last - 1].strip():
    last -= 1

GROUPS = [  # (id, 目录里的名字, 起, 止, 前面要不要放一个大标题)
    ('p1-2025', '2025 年做了什么（六条）', 17, 29, ('part1', 15)),
    ('p1-145', '"十四五"五年回顾', 31, 49, None),
    ('p1-ill', '"清醒地看到"：自己认的短板', 51, 51, None),
    ('p2', '"十五五"目标和五个方面', 55, 73, ('part2', 53)),
    ('p3-goal', '2026 年预期目标', 77, 77, ('part3', 75)),
]
for n, (a, name) in enumerate(zip(SEC_HEADS, SEC_NAMES)):
    b = (SEC_HEADS[n + 1] if n + 1 < len(SEC_HEADS) else 233) - 1
    label = '十' + CN[n - 10] if n >= 10 else CN[n]
    GROUPS.append((f's{n + 1}', f'（{label}）{name}', a, b, None))
GROUPS += [
    ('end', '结束语', 233, 233, None),
    ('ms', '附件 1：十件民生实事', 235, 259, ('annex', None)),
    ('gloss', '附件 2：名词解释', 261, last, None),
]


def annotated(a, b):
    return any((k[0] == 'pre' and a <= k[1] <= b) or (k[0] == 'after' and a <= k[1] <= b) for k in notes)


emitted = []  # 原文字句，最后核对一字不差


def para(i):
    line = L[i - 1]
    s = split(line)
    out = []
    if ('pre', i) in notes:
        out.append(note_html(notes[('pre', i)]))
    is_sec = i in SEC_HEADS
    is_item = 239 < i < 260 and re.match(r'^[一二三四五六七八九十]+、', line)
    is_gloss = i > 263
    lead_ok = (is_item or (len(s) > 1 and len(s[0]) <= 22)) and not is_sec
    chunks, buf = [], []
    for k, x in enumerate(s):
        buf.append(x)
        if ('after', i, k) in notes:
            chunks.append((buf, notes[('after', i, k)]))
            buf = []
    if buf:
        chunks.append((buf, None))
    sent0 = True
    for ci, (sents, ns) in enumerate(chunks):
        parts = []
        for x in sents:
            emitted.append(x)
            if sent0 and is_sec:
                out.append(f'<h3 class="sec" data-line="{i}">{html.escape(x)}</h3>')
            elif sent0 and lead_ok:
                parts.append(f'<strong class="lead">{html.escape(x)}</strong>')
            else:
                parts.append(html.escape(x))
            sent0 = False
        if parts:
            cls = ['o']
            if ci > 0 or is_sec:
                cls.append('cont')
            if is_gloss:
                cls.append('gloss')
            dl = f' data-line="{i}"' if ci == 0 and not is_sec else ''
            out.append(f'<p class="{" ".join(cls)}"{dl}>{"".join(parts)}</p>')
        if ns:
            out.append(note_html(ns))
    return '\n'.join(out)


def plain(i, tag, cls=''):
    emitted.append(L[i - 1])
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} data-line="{i}">{html.escape(L[i - 1])}</{tag}>'


body = []
# 封面：第 1—13 行
meta = ''.join(plain(i, 'div', 'meta') for i in (1, 2, 3))
body.append(f'<header class="cover"><div class="metas">{meta}</div>'
            f'{plain(5, "h1")}{plain(7, "div", "sub")}{plain(9, "div", "by")}</header>')
body.append('<section class="front">' + plain(11, 'p', 'o cont') + para(13) + '</section>')

PART_TITLES = {'part1': 15, 'part2': 53, 'part3': 75}
toc = []
for gid, name, a, b, big in GROUPS:
    if big:
        kind, ln = big
        if ln:
            body.append(f'<h2 id="{kind}" data-line="{ln}">{html.escape(L[ln - 1])}</h2>')
            emitted.append(L[ln - 1])
            toc.append(('h', L[ln - 1]))
        else:
            body.append('<h2 id="annex">附件</h2>')
            toc.append(('h', '附件'))
    done = annotated(a, b)
    toc.append(('g', gid, name, done))
    inner = []
    for i in range(a, b + 1):
        if not L[i - 1].strip():
            continue
        if i in (235, 261):
            inner.append(plain(i, 'div', 'annex-no'))
        elif i in (237, 263):
            inner.append(plain(i, 'h3', 'annex-title'))
        else:
            inner.append(para(i))
    badge = '<span class="badge on">已批</span>' if done else '<span class="badge">原文</span>'
    body.append(f'<details class="grp{" done" if done else ""}" id="{gid}"{" open" if done else ""}>'
                f'<summary><span class="gname">{html.escape(name)}</span>{badge}</summary>'
                f'<div class="gbody">{"".join(inner)}</div></details>')

assert ''.join(emitted) == ''.join(l for l in L if l.strip()), 'original text altered'

toc_html = []
for item in toc:
    if item[0] == 'h':
        toc_html.append(f'<li class="th">{html.escape(item[1])}</li>')
    else:
        _, gid, name, done = item
        toc_html.append(f'<li><a href="#{gid}" class="{"on" if done else ""}">{html.escape(name)}</a></li>')

n_done = sum(1 for t in toc if t[0] == 'g' and t[3])
n_all = sum(1 for t in toc if t[0] == 'g')

PAGE = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>政府工作报告说书版</title>
<style>
:root {
  --bg: #f4f0e8; --paper: #fffdf8; --ink: #22201c; --ink2: #4a4640; --muted: #8a8378;
  --rule: #e4ddcf; --accent: #b23a26; --note-bg: #fbf4ec; --note-ink: #2b2723;
  --pre: #2f5f7f; --pre-bg: #eef4f7; --close: #5a4a2f; --close-bg: #f3efe4;
  --later: #2f6b4a; --later-bg: #edf5ef; --code-bg: #f1ece2; --th-bg: #f3ebe0; --shadow: 0 1px 2px rgba(60,40,20,.06);
  --serif: "Songti SC", "STSong", "Noto Serif SC", "Source Han Serif SC", "SimSun", serif;
  --sans: -apple-system, "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Microsoft YaHei", sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #17161a; --paper: #1e1d21; --ink: #e8e3da; --ink2: #c9c2b6; --muted: #8f897f;
    --rule: #34313a; --accent: #e0745e; --note-bg: #26221f; --note-ink: #e6e0d6;
    --pre: #7fb2d3; --pre-bg: #1f262b; --close: #d1bf98; --close-bg: #25231e;
    --later: #8cc9a5; --later-bg: #1d2721; --code-bg: #2b2925; --th-bg: #2c2824; --shadow: none;
  }
}
:root[data-theme="dark"] {
  --bg: #17161a; --paper: #1e1d21; --ink: #e8e3da; --ink2: #c9c2b6; --muted: #8f897f;
  --rule: #34313a; --accent: #e0745e; --note-bg: #26221f; --note-ink: #e6e0d6;
  --pre: #7fb2d3; --pre-bg: #1f262b; --close: #d1bf98; --close-bg: #25231e;
  --later: #8cc9a5; --later-bg: #1d2721; --code-bg: #2b2925; --th-bg: #2c2824; --shadow: none;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--serif); -webkit-text-size-adjust: 100%; }
.wrap { max-width: 780px; margin: 0 auto; padding: 0 16px 120px; }
.intro { font-family: var(--sans); background: var(--paper); border: 1px solid var(--rule); border-radius: 14px; padding: 20px 22px; margin: 28px 0 18px; box-shadow: var(--shadow); color: var(--ink2); font-size: 15px; line-height: 1.8; }
.intro h2 { font-family: var(--serif); font-size: 22px; color: var(--ink); margin: 0 0 8px; letter-spacing: .04em; }
.intro p { margin: .4em 0; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 14px; margin-top: 10px; font-size: 13px; color: var(--muted); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
nav.toc { font-family: var(--sans); background: var(--paper); border: 1px solid var(--rule); border-radius: 14px; padding: 16px 20px; margin-bottom: 28px; box-shadow: var(--shadow); }
nav.toc .row { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; flex-wrap: wrap; }
nav.toc h3 { margin: 0; font-size: 15px; color: var(--ink); }
nav.toc .prog { font-size: 13px; color: var(--muted); }
nav.toc ul { list-style: none; padding: 0; margin: 10px 0 0; columns: 2; column-gap: 24px; font-size: 14px; line-height: 1.9; }
nav.toc li.th { color: var(--muted); font-size: 12.5px; margin-top: 6px; break-after: avoid; }
nav.toc a { color: var(--ink2); text-decoration: none; }
nav.toc a.on { color: var(--accent); font-weight: 600; }
nav.toc a.on::after { content: " ●"; font-size: 9px; vertical-align: 2px; }
nav.toc .btns { margin-top: 10px; display: flex; gap: 8px; }
nav.toc button { font: inherit; font-size: 12.5px; color: var(--ink2); background: transparent; border: 1px solid var(--rule); border-radius: 999px; padding: 3px 12px; cursor: pointer; }
@media (max-width: 560px) { nav.toc ul { columns: 1; } }
.cover { text-align: center; padding: 34px 0 10px; border-top: 3px double var(--accent); margin-top: 8px; }
.cover .metas { font-family: var(--sans); font-size: 12px; color: var(--muted); line-height: 1.7; text-align: left; margin-bottom: 22px; }
.cover h1 { font-size: 34px; letter-spacing: .3em; margin: 0 0 10px; padding-left: .3em; }
.cover .sub, .cover .by { color: var(--ink2); font-size: 15.5px; line-height: 1.9; }
.front { margin: 16px 0 6px; }
h2 { font-size: 22px; margin: 46px 0 14px; padding-bottom: 8px; border-bottom: 1px solid var(--rule); letter-spacing: .03em; scroll-margin-top: 12px; }
p.o { font-size: 17.5px; line-height: 2; margin: 0 0 14px; text-indent: 2em; text-align: justify; position: relative; }
p.o.cont { text-indent: 0; }
p.o.gloss { font-size: 15px; line-height: 1.8; text-indent: 0; color: var(--ink2); }
strong.lead { font-weight: 700; }
h3.sec { font-size: 19.5px; line-height: 1.75; margin: 6px 0 12px; color: var(--ink); font-weight: 700; }
h3.annex-title { text-align: center; font-size: 19px; margin: 6px 0 14px; }
.annex-no { font-family: var(--sans); font-size: 13px; color: var(--muted); }
[data-line] { scroll-margin-top: 12px; }
@media (min-width: 980px) {
  p.o[data-line]::before, h3.sec[data-line]::before { content: attr(data-line); position: absolute; left: -54px; top: .45em; width: 40px; text-align: right; font-family: var(--sans); font-size: 11px; color: var(--muted); opacity: .55; text-indent: 0; font-weight: 400; }
  h3.sec { position: relative; }
}
details.grp { border-top: 1px solid var(--rule); scroll-margin-top: 12px; }
h2 + details.grp { border-top: none; }
details.grp > summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px; padding: 12px 2px; font-family: var(--sans); font-size: 14.5px; color: var(--muted); }
details.grp > summary::-webkit-details-marker { display: none; }
details.grp > summary::before { content: "▸"; font-size: 12px; transition: transform .15s; }
details.grp[open] > summary::before { transform: rotate(90deg); }
details.grp.done > summary { color: var(--ink); font-weight: 600; }
.badge { font-size: 11.5px; font-weight: 500; border: 1px solid var(--rule); border-radius: 999px; padding: 0 8px; color: var(--muted); }
.badge.on { color: var(--accent); border-color: var(--accent); }
.gbody { padding: 4px 0 18px; }
aside.note { font-family: var(--sans); background: var(--note-bg); color: var(--note-ink); border-left: 3px solid var(--accent); border-radius: 2px 12px 12px 2px; padding: 14px 18px 6px; margin: 2px 0 24px; font-size: 15.5px; line-height: 1.85; position: relative; }
aside.note .tag { display: inline-block; font-size: 12px; font-weight: 600; letter-spacing: .1em; color: var(--accent); border: 1px solid var(--accent); border-radius: 3px; padding: 0 6px 0 7px; margin-bottom: 6px; }
aside.note.pre { background: var(--pre-bg); border-left-color: var(--pre); }
aside.note.pre .tag { color: var(--pre); border-color: var(--pre); }
aside.note.close { background: var(--close-bg); border-left-color: var(--close); }
aside.note.close .tag { color: var(--close); border-color: var(--close); }
aside.note p { margin: 0 0 10px; }
aside.note strong { font-weight: 650; }
aside.note ul { margin: 0 0 10px; padding-left: 1.3em; }
aside.note li { margin: 2px 0; }
aside.note p.later { background: var(--later-bg); border-radius: 8px; padding: 8px 12px; color: var(--ink); }
aside.note p.later strong:first-child { color: var(--later); }
aside.note code { font-family: ui-monospace, Menlo, monospace; font-size: .86em; background: var(--code-bg); padding: 1px 5px; border-radius: 4px; word-break: break-all; }
.tbl { overflow-x: auto; margin: 4px 0 12px; -webkit-overflow-scrolling: touch; }
table { border-collapse: collapse; width: 100%; font-size: 14px; line-height: 1.6; }
td.nw { white-space: nowrap; }
th, td { border: 1px solid var(--rule); padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: var(--th-bg); font-weight: 600; }
details.src { margin: 6px 0 12px; font-size: 13.5px; color: var(--ink2); }
details.src summary { cursor: pointer; color: var(--muted); }
details.src ul { margin-top: 6px; }
a.fab { position: fixed; right: 16px; bottom: 18px; font-family: var(--sans); font-size: 13px; text-decoration: none; color: var(--paper); background: var(--accent); border-radius: 999px; padding: 8px 14px; box-shadow: 0 2px 8px rgba(0,0,0,.18); }
@media (max-width: 560px) {
  p.o { font-size: 16.5px; line-height: 1.95; }
  aside.note { font-size: 15px; padding: 12px 14px 4px; }
  .cover h1 { font-size: 27px; }
  h3.sec { font-size: 18px; }
}
</style>
</head>
<body>
<div class="wrap">
<section class="intro">
<h2>2026 年广东省政府工作报告 · 说书版</h2>
<p>原文一字不改，照原样往下排；<b style="color:var(--accent)">带“说书”标记的卡片</b>是插进去的解读，跳过卡片读下来就是原报告。</p>
<p>这份报告不只是念给人大和老百姓听的。台下坐着的省直部门、各市县的负责人，事后要拿着它拆任务，年底照着它考。他们手里有真实的数，知道每句话会落到谁头上。所以同一句话，外面听着平常，台下听着可能很重。解读里会把这一层一起说出来。</p>
<p>还没批的部分先收起来，点标题就能展开读原文。原文的干净版在 <code>04_文件原文/01_2026广东省政府工作报告.md</code>；宽屏时正文左边的小号数字是它的行号，和大词卡里的【01 行xx】对得上。</p>
<div class="legend"><span><i class="dot" style="background:var(--pre)"></i>开讲前：先摆账</span><span><i class="dot" style="background:var(--accent)"></i>说书：逐句解读</span><span><i class="dot" style="background:var(--later)"></i>后话：报告之后实际怎样</span><span><i class="dot" style="background:var(--close)"></i>收：这一条的总结</span></div>
</section>
<nav class="toc" id="toc">
<div class="row"><h3>目录</h3><span class="prog">已批 __DONE__ / __ALL__</span></div>
<ul>__TOC__</ul>
<div class="btns"><button type="button" data-act="open">全部展开</button><button type="button" data-act="close">只看已批</button></div>
</nav>
__BODY__
</div>
<a class="fab" href="#toc">目录</a>
<script>
(function () {
  function openFor(hash) {
    if (!hash) return;
    var el = document.getElementById(decodeURIComponent(hash.slice(1)));
    if (el && el.tagName === 'DETAILS') el.open = true;
  }
  document.querySelectorAll('nav.toc a').forEach(function (a) {
    a.addEventListener('click', function () { openFor(a.getAttribute('href')); });
  });
  window.addEventListener('hashchange', function () { openFor(location.hash); });
  openFor(location.hash);
  document.querySelectorAll('nav.toc button').forEach(function (b) {
    b.addEventListener('click', function () {
      var all = b.getAttribute('data-act') === 'open';
      document.querySelectorAll('details.grp').forEach(function (d) { d.open = all || d.classList.contains('done'); });
    });
  });
})();
</script>
</body>
</html>
'''

page = (PAGE.replace('__TOC__', '\n'.join(toc_html))
        .replace('__DONE__', str(n_done)).replace('__ALL__', str(n_all))
        .replace('__BODY__', '\n'.join(body)))
open(OUT, 'w', encoding='utf-8').write(page)
print('ok:', OUT, len(page), 'bytes;', sum(len(v) for v in notes.values()), 'note blocks;', n_done, '/', n_all, 'groups annotated')
