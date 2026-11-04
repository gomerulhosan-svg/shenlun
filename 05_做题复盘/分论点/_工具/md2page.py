import re, io, sys, html

src, out = sys.argv[1], sys.argv[2]
lines = io.open(src, encoding='utf-8').read().split('\n')

IDS = {
 '怎么用': 'yong', '一页总览': 'yiye', '逐个词': 'zhuge',
 '推：它推着往前走': 'tui', '托：没它不行，在下面撑着': 'tuo', '护：它挡住风险、稳住大局': 'hu',
 '引：它是为了人': 'yin', '卡：它卡在要害上，或者它就是办法': 'ka', '拓：它打开新地方': 'kuo', '连：它把两头接起来': 'lian',
 '先：它先走一步，或者给方向': 'xian', '干：它是干这件事的主力': 'gan', '软：它变成精神、风气、名声': 'ruan',
 '本：它本来就是 B 该有的（少用）': 'ben', '剔掉的词': 'tidiao', '只表示重要的定位词：放开头，不放论点句': 'dingwei',
 '重要提法：完整判断及适用语境': 'tifa', '附：历年论点句用得最多的几类': 'tongji', '复核记录': 'fuhe', '网络来源': 'wangluo',
}

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'「([^」]*)」', r'<span class="yw">「\1」</span>', s)
    s = re.sub(r'【([^】]*)】', r'<span class="src">【\1】</span>', s)
    s = s.replace('★', '<span class="star">★</span>')
    return s

body = []; toc = []; title = ''
i = 0; n = len(lines)
def flush_para(buf):
    if buf: body.append('<p>' + inline(' '.join(x.strip() for x in buf)) + '</p>')
para = []
while i < n:
    l = lines[i]
    if l.startswith('# '):
        flush_para(para); para = []; title = l[2:].strip(); i += 1; continue
    if l.startswith('## ') or l.startswith('### '):
        flush_para(para); para = []
        lvl = 2 if l.startswith('## ') else 3
        t = l[lvl+1:].strip(); hid = IDS.get(t, 's%d' % len(toc))
        toc.append((lvl, t, hid))
        body.append(f'<h{lvl} id="{hid}">{inline(t)}</h{lvl}>'); i += 1; continue
    if l.strip() == '---':
        flush_para(para); para = []; body.append('<hr>'); i += 1; continue
    if l.startswith('|'):
        flush_para(para); para = []
        rows = []
        while i < n and lines[i].startswith('|'):
            rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
        head, rest = rows[0], [r for r in rows[2:]]
        cls = 'tbl wide' if len(head) >= 3 else 'tbl'
        h = [f'<div class="{cls}"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>']
        for r in rest: h.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>')
        h.append('</tbody></table></div>'); body.append(''.join(h)); continue
    m = re.match(r'^(\s*)(-|\d+\.)\s+(.*)$', l)
    if m:
        flush_para(para); para = []
        # collect list block
        items = []
        while i < n:
            mm = re.match(r'^(\s*)(-|\d+\.)\s+(.*)$', lines[i])
            if mm:
                items.append((len(mm.group(1)) // 2, 'ol' if mm.group(2)[0].isdigit() else 'ul', mm.group(3))); i += 1
            elif lines[i].strip() and lines[i].startswith('  ') and items:
                lvl, kind, txt = items[-1]; items[-1] = (lvl, kind, txt + ' ' + lines[i].strip()); i += 1
            else: break
        out_html = []; stack = []
        for lvl, kind, txt in items:
            while len(stack) > lvl + 1: out_html.append(f'</li></{stack.pop()}>')
            if len(stack) == lvl + 1: out_html.append('</li>')
            while len(stack) < lvl + 1:
                stack.append(kind); out_html.append(f'<{kind}>')
            out_html.append('<li>' + inline(txt))
        while stack: out_html.append(f'</li></{stack.pop()}>')
        body.append(''.join(out_html)); continue
    if not l.strip():
        flush_para(para); para = []; i += 1; continue
    para.append(l); i += 1
flush_para(para)

chips = []
for lvl, t, hid in toc:
    if lvl == 2 and hid not in ('yong',): chips.append(f'<a class="chip chip2" href="#{hid}">{inline(t.split("：")[0])}</a>')
    elif hid in ('tui','tuo','hu','yin','ka','kuo','lian','xian','gan','ruan','ben'): chips.append(f'<a class="chip" href="#{hid}">{inline(t.split("：")[0])}</a>')

css = """
:root{
  /* 版式：单栏阅读，最宽 46em；表格各自横向滚动 */
  --bg:#f5f6f8; --surface:#ffffff; --surface2:#eef0f3; --line:#d9dde3; --fg:#1d2127; --muted:#5b6471;
  --accent:#a3322b; --accent-soft:#f6e3e1; --quote:#2b3a4a;
  --serif:"Noto Serif SC","Songti SC","STSong",serif; --sans:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121418; --surface:#191c22; --surface2:#20242b; --line:#2d323a; --fg:#e5e7ea; --muted:#9aa3ad;
  --accent:#e2776e; --accent-soft:#3a2321; --quote:#c9d4df; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121418; --surface:#191c22; --surface2:#20242b; --line:#2d323a; --fg:#e5e7ea; --muted:#9aa3ad;
  --accent:#e2776e; --accent-soft:#3a2321; --quote:#c9d4df; color-scheme:dark}
body{background:var(--bg); color:var(--fg); font-family:var(--sans); font-size:15.5px; line-height:1.8;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:28px 64px}
.wrap{max-width:46em; margin:0 auto; display:flex; flex-direction:column; gap:14px}
header{display:flex; flex-direction:column; gap:10px; padding-bottom:18px; border-bottom:2px solid var(--accent)}
.eyebrow{font-size:12.5px; letter-spacing:.12em; color:var(--accent)}
h1{font-family:var(--serif); font-size:30px; line-height:1.3; margin:0; text-wrap:balance}
h2{font-family:var(--serif); font-size:21px; line-height:1.4; margin:22px 0 0; padding-top:16px; border-top:1px solid var(--line); text-wrap:balance}
h3{font-family:var(--serif); font-size:17.5px; margin:14px 0 0; color:var(--fg)}
p{margin:0}
p,li{overflow-wrap:anywhere}
.wrap{min-width:0}
hr{display:none}
ul,ol{margin:0; padding-left:1.25em; display:flex; flex-direction:column; gap:4px}
li ul, li ol{margin-top:4px}
li::marker{color:var(--muted)}
strong{font-weight:600}
code{font-size:.88em; background:var(--surface2); padding:1px 5px; border-radius:4px; word-break:break-all}
.yw{color:var(--quote)}
.src{font-size:12px; color:var(--muted); white-space:nowrap}
.star{color:var(--accent)}
.toc{display:flex; flex-wrap:wrap; gap:6px}
.chip{font-size:13px; text-decoration:none; color:var(--fg); background:var(--surface); border:1px solid var(--line); border-radius:999px; padding:2px 10px}
.chip2{border-color:var(--accent); color:var(--accent)}
.chip:focus-visible, a:focus-visible, summary:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.tbl{overflow-x:auto; border:1px solid var(--line); border-radius:6px; background:var(--surface)}
table{border-collapse:collapse; width:100%; font-size:14px; line-height:1.65}
.tbl.wide table{min-width:600px}
th,td{text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid var(--line)}
th{background:var(--surface2); font-weight:600; white-space:nowrap}
tr:last-child td{border-bottom:none}
td:first-child{font-weight:600; min-width:5em}
details{background:var(--accent-soft); border:1px solid var(--line); border-radius:6px; padding:10px 14px}
summary{cursor:pointer; font-weight:600}
details p{margin-top:8px}
@media (prefers-reduced-motion: reduce){*{scroll-behavior:auto}}
html{scroll-behavior:smooth}
"""
review = ('<details id="shenhe" open><summary>给审核人的说明</summary>'
  '<p>这张表给广东省考考生用，只管大作文论点句后半句的判断名词（动力、根基、屏障、关键……）。请重点看三处：'
  '一是"固定提法"表里每条说法给的主语和"之于什么"对不对，有没有漏掉常用的；'
  '二是每个词"注意"里的说法有没有说死、说偏，会不会让考生写出观点不正确的句子；'
  '三是有没有常用的判断名词没收。</p>'
  '<p>表里「」引文已用脚本逐字核对过出处，【】是仓库文件编号和行号。标"仓库无原文"的是常见的中央提法，请顺手核一下。</p></details>')

page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>论点句名词表</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600&family=Noto+Serif+SC:wght@600;700&display=swap">
<style>*{{box-sizing:border-box}} body{{margin:0}} {css}</style>
</head>
<body>
<div class="wrap">
<header><div class="eyebrow">广东省考申论 · 大作文</div><h1>{html.escape(title)}</h1>
<nav class="toc" aria-label="目录">{''.join(chips)}</nav></header>
{review}
{''.join(body)}
</div>
</body>
</html>
"""
io.open(out, 'w', encoding='utf-8').write(page)
print('ok', len(page), 'chars;', len(toc), 'headings')
