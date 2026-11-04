#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""严格同年检验：把「考试用的到底是哪一份报告」用日期算死

背景：回测_政府工作报告短语.md 用的是「笔试前最近一份报告」口径，并已认定
      2022 卷比 2021 年那份、2026 卷比 2025 年那份。但当时的笔试日期是转引的，
      第三轮用独立检索（每年 ≥2 来源）重新核了一遍，此脚本用核实后的日期复算，
      看那两处「跨年」判断是否成立、有没有别的年份也跨年。

输入：
  - 广东省考笔试日期_2020-2026.md（本目录，独立检索所得）
  - 政府工作报告_YYYY.md 的发布日期（脚本从文件里读，不硬编码）

纯本地计算，不联网。
"""
import re
from pathlib import Path
from datetime import date

BASE = Path('/Users/jianguolingyun/公考/07_申论/申论/第三轮检索')
REP = BASE / '政府工作报告'

# ---- 1. 各年报告的发布日期：从文件里读，不硬编码 ----
def report_date(year):
    t = (REP / f'政府工作报告_{year}.md').read_text(encoding='utf-8')
    m = re.search(r'(20\d{2})年(\d{1,2})月(\d{1,2})日', t)
    if not m:
        return None
    y, mo, d = map(int, m.groups())
    return date(y, mo, d)

REP_DATE = {y: report_date(y) for y in range(2019, 2027)}

# ---- 2. 各年度省考的笔试日期（第三轮独立检索，每年 ≥2 来源，全部「已核实」）----
# 键 = 考试年度；2026 年度的笔试实际在 2025-12-07 举行
EXAM = {
    2020: date(2020, 8, 9),
    2021: date(2021, 3, 14),
    2022: date(2022, 1, 3),
    2023: date(2023, 2, 25),
    2024: date(2024, 3, 16),
    2025: date(2025, 3, 15),
    2026: date(2025, 12, 7),
}

# ---- 3. 对每个考试年度，取「笔试当天已经发布」的最新一份报告 ----
print('=' * 84)
print('严格同年检验：笔试当天，命题人手里最新的是哪一份省政府工作报告')
print('=' * 84)
print(f'{"考试年度":<10}{"笔试日期":<14}{"用哪年报告":<12}{"该报告发布":<14}{"领先笔试":<12}{"跨年?"}')
print('-' * 84)

choices = {}
for ey in sorted(EXAM):
    ed = EXAM[ey]
    avail = [ry for ry in sorted(REP_DATE) if REP_DATE[ry] and REP_DATE[ry] <= ed]
    if not avail:
        print(f'{ey:<10}{ed.isoformat():<14}(无可用报告)')
        continue
    ry = avail[-1]
    gap = (ed - REP_DATE[ry]).days
    cross = '★ 跨年' if ry != ey else ''
    choices[ey] = ry
    print(f'{ey:<10}{ed.isoformat():<14}{ry:<12}{REP_DATE[ry].isoformat():<14}早 {gap:>3} 天   {cross}')

# ---- 4. 反向核对：被「跳过」的报告，是不是都晚于笔试 ----
print()
print('=' * 84)
print('被跳过的报告：确认它们确实晚于笔试（命题人看不到）')
print('=' * 84)
for ey in sorted(EXAM):
    if ey not in choices:
        continue
    ry = choices[ey]
    if ry == ey:
        continue
    skipped = ey          # 跨年时，被跳过的是考试年度同名的那份
    if REP_DATE.get(skipped):
        late = (REP_DATE[skipped] - EXAM[ey]).days
        flag = '晚于笔试 ✓' if late > 0 else '★ 早于笔试，口径有误！'
        print(f'{ey} 年度笔试 {EXAM[ey]} ｜ 跳过 {skipped} 年报告（{REP_DATE[skipped]}）'
              f' ｜ 晚 {late} 天 → {flag}')

# ---- 5. 与回测文档原有判断对表 ----
DOC = {2022: 2021, 2026: 2025}   # 回测文档明确写出的两处「跨年」
print()
print('=' * 84)
print('与回测_政府工作报告短语.md 的对表')
print('=' * 84)
allsame = True
for ey in sorted(choices):
    mine, doc = choices[ey], DOC.get(ey, ey)
    ok = '一致' if mine == doc else '★ 不一致'
    if mine != doc:
        allsame = False
    print(f'{ey} 卷：本脚本算得 {mine} 年报告 ｜ 回测文档写 {doc} 年报告 → {ok}')
print()
print('结论：' + ('七卷口径全部一致，回测文档的两处跨年判断经独立日期复核成立。'
                 if allsame else '存在不一致，需人工复查。'))
