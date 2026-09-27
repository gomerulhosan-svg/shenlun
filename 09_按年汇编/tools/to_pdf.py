#!/usr/bin/env python3
"""按年汇编出 PDF：python3 09_按年汇编/tools/to_pdf.py

读 09_按年汇编/ 下的年份 .md，转成 HTML，用 Playwright 的 Chromium 打印成同名 .pdf。
只认 build.py 写出来的那几种 Markdown：标题、分隔线、引用块、列表、段落、**加粗**、行末两空格换行。
"""
import html, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..'))

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm; }
body { font-family: "WenQuanYi Zen Hei", "Noto Sans CJK SC", sans-serif; font-size: 10.5pt; line-height: 1.75;
       color: #222; text-align: justify; }
h1 { font-size: 20pt; text-align: center; margin: 0 0 14pt; }
h2 { font-size: 16pt; border-bottom: 1.5px solid #333; padding-bottom: 4pt; margin: 0 0 10pt; break-before: page; }
h2.toc { break-before: auto; }
h3 { font-size: 13.5pt; margin: 18pt 0 8pt; padding: 4pt 8pt; background: #eef1f4; border-left: 4px solid #4a6178; }
h4 { font-size: 12pt; margin: 14pt 0 6pt; color: #33475b; }
h5 { font-size: 11pt; margin: 14pt 0 4pt; padding-top: 6pt; border-top: 0.5px solid #ccc; }
h6 { font-size: 10.5pt; margin: 10pt 0 2pt; color: #000; }
p { margin: 0 0 6pt; }
blockquote { margin: 4pt 0 10pt; padding: 6pt 10pt; background: #f6f6f3; border-left: 3px solid #b9b9ad; }
blockquote p { margin: 0 0 5pt; }
ul, ol { margin: 0 0 8pt; padding-left: 20pt; }
li { margin: 0 0 2pt; }
hr { display: none; }
h3, h4, h5, h6 { break-after: avoid; }
b { color: #1f3a57; }
blockquote p.t { text-align: center; font-size: 12pt; }
p.s { margin: 10pt 0 3pt; padding-left: 6pt; border-left: 3px solid #4a6178; break-after: avoid; }
"""


def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)


def para(lines, quoted=False):
    """整段只有一个 **加粗**：引用块里是作文标题（居中），引用块外是逐句解析里被解析的那句。"""
    whole = len(lines) == 1 and re.match(r'^\*\*[^*]+\*\*$', lines[0].strip())
    cls = (' class="t"' if quoted else ' class="s"') if whole else ''
    return '<p%s>' % cls + '<br>'.join(inline(l.rstrip()) for l in lines) + '</p>'


def md_to_html(md):
    lines = md.split('\n')
    out, i, first_h2 = [], 0, True
    while i < len(lines):
        l = lines[i]
        if not l.strip() or l.strip() == '---':
            i += 1; continue
        m = re.match(r'^(#{1,6}) (.*)$', l)
        if m:
            n = len(m.group(1))
            cls = ''
            if n == 2 and first_h2:
                cls, first_h2 = ' class="toc"', False
            out.append('<h%d%s>%s</h%d>' % (n, cls, inline(m.group(2)), n)); i += 1; continue
        if l.startswith('>'):
            block = []
            while i < len(lines) and lines[i].startswith('>'):
                block.append(lines[i][1:].lstrip()); i += 1
            paras, cur = [], []
            for b in block:
                if b.strip():
                    cur.append(b)
                elif cur:
                    paras.append(cur); cur = []
            if cur:
                paras.append(cur)
            out.append('<blockquote>' + ''.join(para(p, True) for p in paras) + '</blockquote>'); continue
        if re.match(r'^\s*(- |\d+\. )', l):
            items = []
            while i < len(lines) and re.match(r'^\s*(- |\d+\. )', lines[i]):
                items.append(lines[i]); i += 1
            ordered = bool(re.match(r'^\d+\. ', items[0]))
            html_items, depth = [], 0
            tag = 'ol' if ordered else 'ul'
            html_items.append('<%s>' % tag)
            for it in items:
                d = (len(it) - len(it.lstrip())) // 2
                while d > depth:
                    html_items.append('<ul>'); depth += 1
                while d < depth:
                    html_items.append('</ul>'); depth -= 1
                text = re.sub(r'^\s*(- |\d+\. )', '', it)
                html_items.append('<li>%s</li>' % inline(text))
            while depth > 0:
                html_items.append('</ul>'); depth -= 1
            html_items.append('</%s>' % tag)
            out.append(''.join(html_items)); continue
        block = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6} |>|\s*- |\d+\. |---$)', lines[i]):
            block.append(lines[i]); i += 1
        out.append(para([b[:-2] if b.endswith('  ') else b for b in block]))
    return '\n'.join(out)


NODE = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [htmlPath, pdfPath, title] of jobs) {
    await page.goto('file://' + htmlPath);
    await page.pdf({ path: pdfPath, format: 'A4', printBackground: true, displayHeaderFooter: true,
      margin: { top: '18mm', bottom: '18mm', left: '17mm', right: '17mm' },
      headerTemplate: `<div style="font-size:7pt;color:#999;width:100%;text-align:right;margin-right:17mm;font-family:'WenQuanYi Zen Hei'">${title}</div>`,
      footerTemplate: '<div style="font-size:8pt;color:#999;width:100%;text-align:center;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
    console.log('写出 ' + pdfPath);
  }
  await browser.close();
})();
"""


def main():
    mds = sorted(f for f in os.listdir(OUT) if re.match(r'^\d{4}年.*\.md$', f))
    tmp = tempfile.mkdtemp()
    jobs = []
    for f in mds:
        md = open(os.path.join(OUT, f), encoding='utf-8').read()
        title = md.split('\n', 1)[0].lstrip('# ').strip()
        doc = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s</body></html>' % (
            html.escape(title), CSS, md_to_html(md))
        hp = os.path.join(tmp, f[:-3] + '.html')
        open(hp, 'w', encoding='utf-8').write(doc)
        jobs.append([hp, os.path.join(OUT, f[:-3] + '.pdf'), html.escape(title)])
    js = os.path.join(tmp, 'print.js')
    open(js, 'w').write(NODE)
    env = dict(os.environ)
    npm_root = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    env['NODE_PATH'] = npm_root + os.pathsep + env.get('NODE_PATH', '')
    import json
    subprocess.run(['node', js, json.dumps(jobs)], check=True, env=env)


if __name__ == '__main__':
    main()
