#!/usr/bin/env python3
"""选例因子检验的底表：同一篇来源文章里，哪些段被命题人选进了材料，哪些没选。

python3 10_选材因子/tools/select_pairs.py <输出目录> [卷 ...]

做法：
- 卷面材料取自 10_选材因子/溯源包/<卷>_材料与题干.md（按"#### 材料X"和〔段号〕切段）。
- 来源文章取自 10_选材因子/溯源结果/页面快照/ 下全部 .txt。每行算一段，去掉标点空白后不足 30 字的行
  （导航、版权、按钮）不要。
- 一段来源被材料"用了多少" = 这段里有多少字落在与材料共有的连续 8 字里（和 check_trace.py 同一个比法，
  方向反过来：以来源段为分母）。
- 一篇快照算这张卷的来源文章：至少有一段用了 ≥50%，且这段里落在共有 8 字串里的字 ≥60 个
  （官方套话多在 30 字以内，这样可以排除只是共用套话的文件）。文件名带"检索日志""公告"的不要。
- 来源文章里每段打标：选用（≥30%）、未选（<10%）、部分（10%–30%，不参加比较）。
- 同一张卷里文字完全相同的段（同一篇报道存了几个转载页）只留一次。

输出：<输出目录>/<卷>.json，结构 {卷, 材料段数, 文章:[{快照, 段:[{序, 文, 用率, 标, 对应材料}]}]}；
另写 <输出目录>/汇总.tsv。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
PACK = os.path.join(ROOT, '10_选材因子', '溯源包')
SNAP = os.path.join(ROOT, '10_选材因子', '溯源结果', '页面快照')
N = 8
PUNCT = r'[\s“”"‘’\'「」『』《》〈〉（）()【】、，。；：！？,.;:!?—…·\-]'
PAPERS = ['2022县级', '2023县级', '2024一卷', '2024二卷', '2024选调',
          '2025省市', '2025县镇', '2025选调', '2026省市', '2026县镇']


def norm(s):
    return re.sub(PUNCT, '', s)


def material(paper):
    t = open(os.path.join(PACK, paper + '_材料与题干.md'), encoding='utf-8').read()
    t = t.split('### 题干')[0] if '### 题干' in t else t
    out = []
    for m in re.finditer(r'#### 材料([一二三四五六七八九十]+)\s*\n(.*?)(?=\n#### |\Z)', t, re.S):
        for p in re.finditer(r'〔(\d+)〕([^〔]*)', m.group(2)):
            out.append(('材料%s〔%s〕' % (m.group(1), p.group(1)), p.group(2).strip()))
    return out


def used_rate(para_n, g):
    if len(para_n) < N:
        return 0.0
    m = [False] * len(para_n)
    for i in range(len(para_n) - N + 1):
        if para_n[i:i + N] in g:
            for j in range(i, i + N):
                m[j] = True
    return sum(m) / len(para_n)


def main(outdir, papers):
    os.makedirs(outdir, exist_ok=True)
    snaps = []
    for d, _, fs in os.walk(SNAP):
        for f in sorted(fs):
            if f.endswith('.txt'):
                p = os.path.join(d, f)
                lines = open(p, encoding='utf-8', errors='ignore').read().split('\n')
                paras = [(i, l.strip()) for i, l in enumerate(lines) if len(norm(l)) >= 30]
                snaps.append((os.path.relpath(p, SNAP), paras))
    rows = ['卷\t材料段数\t来源文章数\t选用段\t未选段\t部分段']
    for paper in papers:
        mat = material(paper)
        mg = {}
        allg = set()
        for k, txt in mat:
            t = norm(txt)
            g = {t[i:i + N] for i in range(len(t) - N + 1)}
            mg[k] = g
            allg |= g
        seen, arts = set(), []
        for rel, paras in snaps:
            scored = []
            for i, l in paras:
                ln = norm(l)
                r = used_rate(ln, allg)
                scored.append((i, l, ln, r))
            if re.search(r'检索日志|日志|公告', rel):
                continue
            if not any(r >= 0.5 and r * len(ln) >= 60 for _, _, ln, r in scored):
                continue
            segs = []
            for i, l, ln, r in scored:
                if ln in seen:
                    continue
                seen.add(ln)
                tag = '选用' if r >= 0.3 else ('未选' if r < 0.1 else '部分')
                best = ''
                if tag != '未选':
                    lg = {ln[j:j + N] for j in range(len(ln) - N + 1)}
                    best = max(mg, key=lambda k: len(mg[k] & lg))
                segs.append({'序': i, '文': l, '用率': round(r, 3), '标': tag, '对应材料': best})
            if any(s['标'] == '选用' for s in segs):
                arts.append({'快照': rel, '段': segs})
        json.dump({'卷': paper, '材料段数': len(mat), '文章': arts},
                  open(os.path.join(outdir, paper + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        c = lambda t: sum(1 for a in arts for s in a['段'] if s['标'] == t)
        rows.append('\t'.join(map(str, [paper, len(mat), len(arts), c('选用'), c('未选'), c('部分')])))
    open(os.path.join(outdir, '汇总.tsv'), 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
    print('\n'.join(rows))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:] or PAPERS)
