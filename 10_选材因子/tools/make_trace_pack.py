#!/usr/bin/env python3
"""溯源包：python3 10_选材因子/tools/make_trace_pack.py

给国内模型联网溯源用。2022–2026 年每套卷一个文件，只放给定材料（每段标段号）和题干，
写到 10_选材因子/溯源包/，同时出 .pdf，并打一个压缩包。段号和 09_按年汇编、各份解析一致。
"""
import html, json, os, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.normpath(os.path.join(HERE, '..', '溯源包'))
sys.path.insert(0, os.path.join(ROOT, '09_按年汇编', 'tools'))
import build  # noqa: E402
import to_pdf  # noqa: E402

PAPERS = [p for year, papers in build.YEARS if year >= 2022 for p in papers]
# 笔试日期：2024–2026 已查证，2022、2023 待国内模型核实
EXAM = {'2026': '2025-12-07', '2025': '2025-03-15', '2024': '2024-03-16'}


def pack_md(sid, name):
    mat, nmat = build.materials_md(sid)
    head = [
        '# %s：给定材料与题干' % name, '',
        '卷号：%s。笔试日期：%s。本卷 %d 则材料。每段前面的〔段号〕是这一则里的第几段，回报出处时请按「材料几〔段号〕」指认。' % (
            sid, EXAM.get(sid[:4], '待核实'), nmat), '',
    ]
    return '\n'.join(build.squeeze(head + mat + build.stems_md(sid))) + '\n'


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    jobs, files = [], []
    for sid, name, short in PAPERS:
        fn = '%s_材料与题干' % sid
        md = pack_md(sid, name)
        open(os.path.join(OUT, fn + '.md'), 'w', encoding='utf-8').write(md)
        title = md.split('\n', 1)[0].lstrip('# ').strip()
        doc = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s</body></html>' % (
            html.escape(title), to_pdf.CSS.replace('break-before: page;', ''), to_pdf.md_to_html(md))
        hp = os.path.join(tmp, fn + '.html')
        open(hp, 'w', encoding='utf-8').write(doc)
        jobs.append([hp, os.path.join(OUT, fn + '.pdf'), html.escape(title)])
        files += [fn + '.md', fn + '.pdf']
        print('%-8s %6d 字符' % (sid, len(md)))
    js = os.path.join(tmp, 'print.js')
    open(js, 'w').write(to_pdf.NODE)
    env = dict(os.environ)
    env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', js, json.dumps(jobs)], check=True, env=env, stdout=subprocess.DEVNULL)
    zp = os.path.join(OUT, '溯源包_2022-2026.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            z.write(os.path.join(OUT, f), '溯源包_2022-2026/' + f)
    print('写出 %s（%d 个文件）' % (os.path.relpath(zp, ROOT), len(files)))


if __name__ == '__main__':
    main()
