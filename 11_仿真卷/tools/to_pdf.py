#!/usr/bin/env python3
"""仿真卷出 PDF：python3 11_仿真卷/tools/to_pdf.py <文件.md> [...]

沿用 09_按年汇编/tools/to_pdf.py 的排版和 Chromium 打印，另外支持 markdown 表格。
每个 .md 在同目录写出同名 .pdf。
"""
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    'base', os.path.join(HERE, '..', '..', '09_按年汇编', 'tools', 'to_pdf.py'))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

CSS = base.CSS + """
table { border-collapse: collapse; margin: 4pt 0 10pt; font-size: 9.5pt; width: 100%; }
th, td { border: 0.5px solid #999; padding: 3pt 5pt; vertical-align: top; }
th { background: #eef1f4; }
"""


def cells(row):
    return [c.strip() for c in row.strip().strip('|').split('|')]


def table(rows):
    head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
    out = ['<table><tr>' + ''.join('<th>%s</th>' % base.inline(c) for c in head) + '</tr>']
    for r in body:
        out.append('<tr>' + ''.join('<td>%s</td>' % base.inline(c) for c in r) + '</tr>')
    return '\n'.join(out) + '</table>'


def convert(md):
    lines, out, buf, i = md.split('\n'), [], [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            out.append(base.md_to_html('\n'.join(buf)))
            buf, rows = [], []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append(lines[i])
                i += 1
            out.append(table(rows))
        else:
            buf.append(lines[i])
            i += 1
    out.append(base.md_to_html('\n'.join(buf)))
    return '\n'.join(out)


def main(paths):
    tmp, jobs = tempfile.mkdtemp(), []
    for p in paths:
        p = os.path.abspath(p)
        md = open(p, encoding='utf-8').read()
        title = md.split('\n', 1)[0].lstrip('# ').strip()
        doc = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>%s</title>'
               '<style>%s</style></head><body>%s</body></html>') % (html.escape(title), CSS, convert(md))
        hp = os.path.join(tmp, os.path.basename(p)[:-3] + '.html')
        open(hp, 'w', encoding='utf-8').write(doc)
        jobs.append([hp, p[:-3] + '.pdf', html.escape(title)])
    js = os.path.join(tmp, 'print.js')
    open(js, 'w').write(base.NODE)
    env = dict(os.environ)
    npm_root = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    env['NODE_PATH'] = npm_root + os.pathsep + env.get('NODE_PATH', '')
    subprocess.run(['node', js, json.dumps(jobs)], check=True, env=env)


if __name__ == '__main__':
    main(sys.argv[1:])
