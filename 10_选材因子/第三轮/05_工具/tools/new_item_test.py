#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务三兑现：「报告短语变题目」的新增检验

依据 检验_政府工作报告短语.md 第 2 点指明的待办：
  「要验证这一点，得知道这些短语在 2024 年报告里有没有，也就是它们是不是 2025 年才新增的。」

做法：拿该文档已经点名的三组短语，逐年查其在 2019—2026 八份报告第二部分中的出现情况，
     看「发布后组命中」的短语是不是集中在最近一两年才出现，「对照组命中」的是不是年年都写。

纯本地计算，不联网、不耗检索额度。
数据：政府工作报告/政府工作报告_2019..2026.md（第二部分全文）
"""
import re
from pathlib import Path

REP_DIR = Path('/Users/jianguolingyun/公考/07_申论/申论/第三轮检索' ) / '政府工作报告'
YEARS = list(range(2019, 2027))


def norm(s):
    return re.sub(r'[^一-鿿0-9]', '', s)


def load(year):
    t = (REP_DIR / f'政府工作报告_{year}.md').read_text(encoding='utf-8')
    m = re.search(r'## 二、第二部分全文', t)
    if not m:
        raise SystemExit(f'{year} 未找到「## 二、第二部分全文」标记')
    return norm(t[m.end():])


NORM = {y: load(y) for y in YEARS}

# 该文档已点名的三组短语（原文照录，不增不减）
HIT_AFTER = [                    # 发布后组命中的 6 道
    ('强化企业科技创新主体地位', '2025 省市 问题一'),
    ('土特产',                 '2025 县镇 问题一'),
    ('红树林',                 '2025 选调 问题一'),
    ('海洋牧场',               '2025 选调 问题二'),
    ('零碳园区',               '2026 省市 问题二'),
    ('古树名木',               '2026 县镇 问题二'),
]
MISS_AFTER = [                   # 发布后组未命中的 3 道（报告里用的是别的说法）
    ('科研成果转化', '2025 省市 问题二', '报告里写的是「科技成果」'),
    ('科技赋能农业', '2025 县镇 问题二', '报告里是「智慧农业」'),
    ('绿色工厂',     '2026 县镇 问题一', '报告里只有「绿色化」'),
]
CONTROL = [                      # 对照组（2020–2024 年卷）命中的 7 道
    ('百县千镇万村高质量发展工程', '百千万工程'),
    ('软联通',                 '软联通'),
    ('数字政府',               '数字政府'),
    ('农村集体经济',            '农村集体经济'),
    ('撂荒耕地复耕复种',         '撂荒耕地复耕复种'),
    ('返贫',                   '返贫'),
    ('乡村振兴',               '乡村振兴'),
]

W = 20


def row(phrase):
    return ''.join('●' if phrase in NORM[y] else '·' for y in YEARS)


def first_last(phrase):
    ys = [y for y in YEARS if phrase in NORM[y]]
    return (ys[0], ys[-1], len(ys)) if ys else (None, None, 0)


def table(title, items, note_col=False):
    print(f'\n{title}')
    print(f'{"短语":<{W}}' + ''.join(f'{y%100:>3}' for y in YEARS) + '   首现  末现  年数')
    print('-' * (W + len(YEARS) * 3 + 22))
    for it in items:
        phrase = it[0]
        f, l, c = first_last(phrase)
        mark = '' if c == 0 else ''
        print(f'{phrase:<{W}}' + row(phrase) + f'   {str(f or "—"):>4}  {str(l or "—"):>4}  {c:>3}{mark}')
    print(f'（列头 19–26 表示 2019—2026 年报告第二部分；● 有，· 无）')


print('=' * 78)
print('新增检验：短语在 2019—2026 年八份省政府工作报告第二部分中的出现情况')
print('=' * 78)
table('A. 发布后组·命中的 6 道', HIT_AFTER)
table('B. 发布后组·未命中的 3 道', MISS_AFTER)
table('C. 对照组（2020–2024 年卷）命中的 7 道', CONTROL)

# ---- 汇总判读 ----
print('\n' + '=' * 78)
print('判读')
print('=' * 78)
for name, items in [('A 发布后组命中', HIT_AFTER), ('B 发布后组未命中', MISS_AFTER), ('C 对照组命中', CONTROL)]:
    lens = [first_last(i[0])[2] for i in items]
    avg = sum(lens) / len(lens)
    print(f'  {name}: {len(items)} 条，平均出现在 {avg:.1f} 份报告里（满值 8）')
    for i in items:
        f, l, c = first_last(i[0])
        if c:
            print(f'      {i[0]:<{W}} 首现 {f}，共 {c} 份')
        else:
            print(f'      {i[0]:<{W}} 八年报告里都没有')
