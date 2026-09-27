#!/usr/bin/env python3
"""按材料用途统计改写程度：python3 10_选材因子/tools/rewrite_by_role.py

读 溯源结果_<卷>.md 每段的"对应程度"，按这段材料的用途分三类：小题指定材料、材料一、其他作文材料。
看越接近采分点的材料是不是越找不到原样出处。
"""
import re, json, glob, collections
D = '10_选材因子/溯源结果/'
Q = json.load(open('08_小题重写/questions.json', encoding='utf-8'))
used = collections.defaultdict(set)
for q in Q:
    for b in q['blocks']: used[q['set_id']].add(b)
CAT = [('逐字', r'逐字'), ('小改', r'小改|删改搬运'), ('大改写', r'大改写'), ('多源拼接', r'多源拼接|拼接'),
       ('自撰/未找到', r'自撰|未找到|无对应'), ('仅摘要', r'仅摘要')]
def cat(line):
    for k, p in CAT:
        if re.search(p, line): return k
    return '其他'
stat = {'小题材料': collections.Counter(), '材料一': collections.Counter(), '其他作文材料': collections.Counter()}
per = []
for f in sorted(glob.glob(D + '溯源结果_*.md')):
    sid = f.split('溯源结果_')[1][:-3]
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'\n#{2,3} *(材料([一二三四五六七八九十]+)〔[^\n]*)\n(.*?)(?=\n#{2,3} |\Z)', t, re.S):
        name = m.group(2); body = m.group(3)
        lines = re.findall(r'对应程度[：:]\s*([^\n]*)', body)
        if not lines: continue
        c = cat(lines[0][:40])
        role = '小题材料' if name in used[sid] else ('材料一' if name == '一' else '其他作文材料')
        stat[role][c] += 1
        per.append((sid, name, role, c))
print('按材料用途统计「对应程度」（每段一条）：')
cols = ['逐字','小改','大改写','多源拼接','自撰/未找到','仅摘要','其他']
print('%-10s %5s ' % ('用途','段数') + ' '.join('%7s' % c for c in cols))
for r, cnt in stat.items():
    n = sum(cnt.values())
    print('%-10s %5d ' % (r, n) + ' '.join('%6.0f%%' % (cnt[c]/n*100) for c in cols))
# 排除乡镇两卷（未找到大多是没搜深）
print('\n排除 2022乡镇、2023乡镇（两卷 98% 判未找到，国内模型自己说很可能是搜浅了）：')
stat2 = {k: collections.Counter() for k in stat}
for sid, name, role, c in per:
    if sid in ('2022乡镇','2023乡镇'): continue
    stat2[role][c] += 1
for r, cnt in stat2.items():
    n = sum(cnt.values())
    print('%-10s %5d ' % (r, n) + ' '.join('%6.0f%%' % (cnt[c]/n*100) for c in cols))
