#!/usr/bin/env python3
"""题目核心对象 × 六份政府工作报告的矩阵：python3 10_选材因子/tools/report_matrix.py

核心对象沿用 report_baseline.py 里事先定好的清单（没有看结果再挑词）。
每道题的"最近报告"是笔试前最近一份：2022 卷→2021 年报告（2022 卷 2022-01-03 考，早于 2022 年报告），
2023→2023，2024→2024，2025→2025，2026 卷→2025（2025-12-07 考）。
只比报告"XXXX 年工作安排"那一节。报告原文在 溯源结果/页面快照/ 下。
"""
import re, sys, importlib.util
P = '10_选材因子/溯源结果/页面快照/'
FILES = {
 2021: P+'_cache_2022乡镇/母文件_2021年广东省政府工作报告_eesia.txt',
 2022: P+'_cache/2022年广东省政府工作报告.txt',
 2023: P+'_cache/2023年广东省政府工作报告.txt',
 2024: P+'_cache/2024_政府工作报告_eesia.txt',
 2025: P+'_cache/2025年广东省政府工作报告_163.txt',
 2026: P+'_cache/2026年广东省政府工作报告_163.txt',
}
def norm(s): return re.sub(r'[\s　“”"‘’「」]', '', s)
SEC = {}
for y, f in FILES.items():
    t = norm(open(f, encoding='utf-8', errors='ignore').read())
    m = re.search(r'[一二三四五六]、%d年工作安排' % y, t)
    s = m.end()
    e = min([i for i in (t.find('各位代表', s + 3000), t.find('附件', s + 3000)) if i > 0] or [len(t)])
    SEC[y] = t[s:e]
    print(y, '工作安排', len(SEC[y]), '字')
# 沿用 10_选材因子/tools/report_baseline.py 的核心对象清单
spec = importlib.util.spec_from_file_location('rb', '10_选材因子/tools/report_baseline.py')
src = open('10_选材因子/tools/report_baseline.py', encoding='utf-8').read()
Q = eval(src[src.index('Q = [') + 4: src.index(']\nfrom collections') + 1])
# 各卷"笔试前最近一份报告"
NEAR = {'2022': 2021, '2023': 2023, '2024': 2024, '2025': 2025, '2026': 2025}
rows = []
for sid, q, _, obj, near, _ in Q:
    y = sid[:4]
    if y not in NEAR or obj.startswith('（'): continue
    r0 = NEAR[y]
    hits = {ry: (obj in SEC[ry]) for ry in SEC}
    prev = r0 - 1
    new = hits[r0] and (prev in SEC) and not hits[prev]
    rows.append((sid, q, obj, r0, hits, new))
print()
print('%-8s %-4s %-14s 最近报告 | ' % ('卷','题','核心对象') + ' '.join(str(y) for y in SEC) + ' | 最近报告里新增')
for sid, q, obj, r0, hits, new in rows:
    cells = ' '.join(('【●】' if ry == r0 else ' ● ') if h else ('【·】' if ry == r0 else ' · ') for ry, h in hits.items())
    print('%-8s %-4s %-14s %d | %s | %s' % (sid, q, obj[:14], r0, cells, '新增' if new else ''))
# 汇总
n = len(rows)
diag = sum(h[r0] for _,_,_,r0,h,_ in rows)
off = [(h[ry]) for _,_,_,r0,h,_ in rows for ry in h if ry != r0]
print('\n题数', n)
print('最近那份报告命中：%d/%d = %.0f%%' % (diag, n, diag/n*100))
print('其他年份报告命中：%d/%d = %.0f%%' % (sum(off), len(off), sum(off)/len(off)*100))
fut = [h[ry] for _,_,_,r0,h,_ in rows for ry in h if ry > r0]
past = [h[ry] for _,_,_,r0,h,_ in rows for ry in h if ry < r0]
print('  其中更早的报告：%d/%d = %.0f%%；更晚的报告：%d/%d = %.0f%%' % (sum(past), len(past), sum(past)/max(len(past),1)*100, sum(fut), len(fut), sum(fut)/max(len(fut),1)*100))
newc = sum(1 for r in rows if r[5]); hitc = diag
print('最近报告里命中的 %d 题中，是当年新增（上一年报告里没有）的：%d' % (hitc, newc))
for y in ['2022','2023','2024','2025','2026']:
    rr = [r for r in rows if r[0].startswith(y)]
    if rr: print('  %s 卷：最近报告命中 %d/%d，其中新增 %d' % (y, sum(r[4][r[3]] for r in rr), len(rr), sum(1 for r in rr if r[5])))
print('\n—— 只看 2024–2026 年的卷（13 题）——')
rr = [r for r in rows if r[0][:4] in ('2024','2025','2026')]
d = sum(r[4][r[3]] for r in rr)
o = [r[4][ry] for r in rr for ry in r[4] if ry != r[3]]
e = [r[4][ry] for r in rr for ry in r[4] if ry < r[3]]
l = [r[4][ry] for r in rr for ry in r[4] if ry > r[3]]
print('最近报告命中 %d/%d = %.0f%%；其他年份 %d/%d = %.0f%%（更早 %.0f%%，更晚 %.0f%%）' % (d, len(rr), d/len(rr)*100, sum(o), len(o), sum(o)/len(o)*100, sum(e)/len(e)*100, sum(l)/len(l)*100))
# 每题在六份报告里出现几年
for r in rr:
    print('  %-8s %-4s %-14s 六份报告里出现 %d 份' % (r[0], r[1], r[2][:14], sum(r[4].values())))
# 看 2027 卷的候选：2026 报告工作安排 vs 2025 报告，新增的具体词（用 4-8 字 n-gram 粗筛，只看完全不在 2021-2025 任何一份里的）
