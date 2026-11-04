#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""严格同年检验：每道题，查它落在「考前最近那份报告」里没有

与 new_item_test.py 的区别：
  new_item_test.py 只数「这条短语在八份报告里出现过几次」——是横着比。
  本脚本竖着切：对每道题，把它**只**放到命题人当时真能看到的那一份报告里查，
  再用「未来报告」（笔试后才发布的）做安慰剂对照。

口径来自 exam_vs_report.py 算出的表（已用独立核实的笔试日期复核）：
  2020卷→2020报告  2021卷→2021  2022卷→2021★  2023卷→2023
  2024卷→2024      2025卷→2025  2026卷→2025★
"""
import re
from pathlib import Path

BASE = Path('/Users/jianguolingyun/公考/07_申论/申论/第三轮检索')
REP = BASE / '政府工作报告'
YEARS = list(range(2019, 2027))


def norm(s):
    return re.sub(r'[^一-鿿0-9]', '', s)


def load(year):
    t = (REP / f'政府工作报告_{year}.md').read_text(encoding='utf-8')
    m = re.search(r'## 二、第二部分全文', t)
    return norm(t[m.end():])


NORM = {y: load(y) for y in YEARS}

# 考试年度 → 考前最近报告年（exam_vs_report.py 算得，已复核）
PRE = {2020: 2020, 2021: 2021, 2022: 2021, 2023: 2023,
       2024: 2024, 2025: 2025, 2026: 2025}
# 考试年度 → 下一份报告（笔试之后才发布，命题人看不到）
NEXT = {ey: (r + 1 if r + 1 in YEARS else None) for ey, r in PRE.items()}

ITEMS = [
    ('强化企业科技创新主体地位', 2025, '2025 省市 问题一'),
    ('土特产',               2025, '2025 县镇 问题一'),
    ('红树林',               2025, '2025 选调 问题一'),
    ('海洋牧场',             2025, '2025 选调 问题二'),
    ('零碳园区',             2026, '2026 省市 问题二'),
    ('古树名木',             2026, '2026 县镇 问题二'),
    ('科研成果转化',          2025, '2025 省市 问题二'),
    ('科技赋能农业',          2025, '2025 县镇 问题二'),
    ('绿色工厂',             2026, '2026 县镇 问题一'),
]

print('=' * 100)
print('严格同年检验：只查命题人当时能看到的那一份报告')
print('=' * 100)
print(f'{"短语":<24}{"卷别":<18}{"考前报告":<9}{"考前":<6}{"更早报告":<16}{"未来报告":<14}{"安慰剂"}')
print('-' * 100)

hit_pre = hit_next = 0
future_only = []       # 首现落在未来报告（考前报告口径解释不了）
in_both = []

for phrase, ey, tag in ITEMS:
    r = PRE[ey]
    nxt = NEXT[ey]
    in_pre = phrase in NORM[r]
    earlier = [y for y in YEARS if y < r and phrase in NORM[y]]
    future = [y for y in YEARS if y > r and phrase in NORM[y]]
    in_next = (nxt is not None and phrase in NORM[nxt])

    hit_pre += in_pre
    hit_next += in_next
    if not in_pre and not earlier and future:
        future_only.append((phrase, tag, r, future))

    early_s = f'首现{earlier[0]} 共{len(earlier)}份' if earlier else '从未出现'
    fut_s = f'首现{future[0]} 共{len(future)}份' if future else '从未出现'

    print(f'{phrase:<24}{tag:<18}{r:<9}'
          f'{"有 ●" if in_pre else "无 ·":<6}'
          f'{early_s:<16}{fut_s:<14}'
          f'{"有" if in_next else "无"}')

print()
print('=' * 100)
print('判读')
print('=' * 100)
print(f'  真检验 · 考前最近报告：命中 {hit_pre}/9 = {hit_pre/9:.1%}')
print(f'  安慰剂 · 未来报告（命题人看不到）：命中 {hit_next}/9 = {hit_next/9:.1%}')
print()
if hit_pre == hit_next:
    print('  ★ 安慰剂没有区分力：两者相同。原因是相邻年份报告重叠度高——')
    print('    2026 年报告基本继承了 2025 年报告的说法，所以「用哪一份」在这批短语上分辨不出来。')
    print('    要区分，得用「首现年份」而不是「有无」。')
print()
if future_only:
    print('  ★ 有短语首现就落在未来报告，考前报告口径解释不了：')
    for p, t, r, f in future_only:
        print(f'      {p}（{t}）：{r} 年报告无，{f} 年报告才有')
else:
    print('  没有任何一道题是「首现在未来报告」的——凡命题人用到的说法，')
    print('  在他当时能看到的那份报告里都已有踪迹。这是「考前报告」口径的必要条件，成立。')

# ---- 用「首现距考前报告的距离」代替有无，做区分度检验 ----
print()
print('=' * 100)
print('改用「首现距考前报告年数」看区分度')
print('=' * 100)
print(f'{"短语":<24}{"首现":<8}{"考前报告":<10}{"距离":<8}')
print('-' * 100)
dists = []
for phrase, ey, tag in ITEMS:
    r = PRE[ey]
    ys = [y for y in YEARS if phrase in NORM[y]]
    if not ys:
        print(f'{phrase:<24}{"从未":<8}{r:<10}{"—":<8}')
        continue
    d = r - ys[0]
    dists.append(d)
    print(f'{phrase:<24}{ys[0]:<8}{r:<10}{d:<8}')
if dists:
    print(f'\n  有首现可查的 {len(dists)} 条，平均距离 {sum(dists)/len(dists):.1f} 年')
    print(f'  随机期望：八份报告里任取一条，平均距离约 3.5 年')
    print(f'  距离越小，说明越像「从最新报告里挑刚写进去的新事项」。')

# ---- 关键个案：绿色工厂 ----
print()
print('=' * 100)
print('关键个案：「绿色工厂」——两种口径给出相反答案')
print('=' * 100)
gf = [y for y in YEARS if '绿色工厂' in NORM[y]]
print(f'  「绿色工厂」出现在：{gf}')
print(f'  2026 年度笔试 2025-12-07；考前最近报告 = 2025 年那份（2025-01-15）')
print(f'  → 考前最近报告口径：2025 年报告{"有" if 2025 in gf else "没有"} → '
      f'{"命中" if 2025 in gf else "未命中"}')
print(f'  → 考试年度同名报告口径：2026 年报告{"有" if 2026 in gf else "没有"} → '
      f'{"命中" if 2026 in gf else "未命中"}')
print()
print('  两种口径只在 2022、2026 两个年度分岔。2026 年度笔试在 2025-12-07，')
print('  2026 年报告要到 2026-01-26 才发布——命题时那份还不存在，只能取 2025 年那份。')
