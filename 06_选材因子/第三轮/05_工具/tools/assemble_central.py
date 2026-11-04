#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合装 需求三：中央新部署与广东落地_2025-07至2026-09.md
素材来源：_素材/中央新部署_C{1..5}.md 及其附件
可重复运行，不修改任何素材文件。
"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MAT = BASE / '_素材'
OUT = BASE / '中央新部署与广东落地_2025-07至2026-09.md'

SECTIONS = [
    ('C1', '人工智能与数字经济、数据要素与算力', [
        '中央新部署_C1.md',
    ]),
    ('C2', '民营经济 · 全国统一大市场与综合整治“内卷式”竞争 · 营商环境', [
        '中央新部署_C2.md',
    ]),
    ('C3', '城市更新 · 城乡融合与乡村振兴 · “十五五”规划纲要（国家层面）', [
        '中央新部署_C3.md',
        '中央新部署_C3_附件_十五五规划纲要全文.md',
    ]),
    ('C4', '民生（育儿／养老／就业／医疗／教育）· 社会保障', [
        '中央新部署_C4.md',
        '中央新部署_C4_附件一_原文逐字_2025下半年.md',
        '中央新部署_C4_附件二_原文逐字_2026年.md',
    ]),
    ('C5', '对外开放与自贸试验区 · 共建“一带一路” · 外贸外资', [
        '中央新部署_C5.md',
    ]),
    ('C6', '生态环境（2026-09-28 补）', [
        '中央新部署_C6.md',
    ]),
    ('C7', '文化（2026-09-28 补）', [
        '中央新部署_C7.md',
    ]),
]

# C6/C7 的独立复核结果（从本轮 workflow 的 journal 里读，不重复检索）
JOURNAL = Path('/Users/jianguolingyun/.claude/projects/-Users-jianguolingyun----07---'
               '/0f84f31a-1cbd-42fc-bfdf-108818ec19e3/subagents/workflows'
               '/wf_c7a55566-a0e/journal.jsonl')


def read(p):
    return p.read_text(encoding='utf-8').strip()


def demote(text, levels=2):
    return '\n'.join(
        ('#' * levels + l) if l.startswith('#') else l
        for l in text.split('\n')
    )


def hanzi(s):
    return len(re.findall(r'[一-鿿]', s))


parts = []
parts.append('# 中央新部署与广东落地_2025-07至2026-09\n')
parts.append(
    '> 依据：《国内模型提示词》第三轮需求三\n'
    '> 覆盖范围：2025年7月 — 2026年9月\n'
    '> 内容：党中央、国务院、中办国办、国家部委出台的重要文件，以及新施行的法律法规；'
    '每项给「文件名｜发文机关｜印发或施行日期｜链接｜官方新闻稿导语（照抄，不概括）」，'
    '并逐项查广东有无对应的落地文件或报道。\n'
    '> 重点领域：人工智能与数字经济、民营经济、统一大市场与综合整治“内卷式”竞争、城市更新、'
    '城乡融合与乡村振兴、民生（育儿、养老、就业、医疗）、对外开放与自贸试验区、生态环境、文化。\n'
    '> 抓取方式：curl 抓取 HTML 原文，python3 去标签取正文（不用 WebFetch，避免被摘要化）\n'
    '> 检索日期：2026-09-28\n'
    '> 原文一律逐字粘贴，未作删改。\n'
)

n = 0
for code, desc, files in SECTIONS:
    n += 1
    parts.append(f'## {n} {code}｜{desc}\n')
    for fname in files:
        f = MAT / fname
        if not f.exists():
            parts.append(f'### 未找到素材：{fname}\n')
            continue
        parts.append(demote(read(f), 3) + '\n')

# ---- C6/C7 独立复核补充（正文一字不动，复核结果另起一节）----
import json


def load_reviews():
    if not JOURNAL.exists():
        return {}
    out = {}
    for line in JOURNAL.read_text(encoding='utf-8').splitlines():
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get('type') != 'result':
            continue
        v = o.get('value') or o.get('result')
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except Exception:
                continue
        if isinstance(v, dict) and 'missing' in v:
            out[v.get('domain')] = v
    return out


REV = load_reviews()
parts.append(f'## {n+1} C6/C7 独立复核补充\n')
parts.append(
    '> 生态环境、文化两组的检索员交件后，各配一路**独立复核员**重新检索一遍'
    '（不看检索员那份），并逐条 curl 打开链接核对。\n'
    '> 本节把复核结果与检索员原件**分开列**：原件在 C6／C7 两节里一字未动，'
    '复核发现的漏项与错项列在这里，标明「原件未收」／「原件有误」。\n'
)
tot = {'m': 0, 'e': 0, 'f': 0, 'c': 0, 'b': 0}
for dom in ('生态环境', '文化'):
    r = REV.get(dom)
    if not r:
        parts.append(f'\n### {dom}｜**未找到复核结果**\n')
        continue
    miss = r.get('missing') or []
    errs = r.get('errors') or []
    fabs = r.get('fabricated') or []
    tot['m'] += len(miss); tot['e'] += len(errs); tot['f'] += len(fabs)
    tot['c'] += r.get('links_checked') or 0
    tot['b'] += r.get('links_broken') or 0

    parts.append(f'\n### {dom}｜漏 {len(miss)} 条 · 错 {len(errs)} 条'
                 f' · 无法核实 {len(fabs)} 条 · 复核链接 {r.get("links_checked")}'
                 f'（坏 {r.get("links_broken")}）\n')
    if miss:
        parts.append(f'\n#### 复核补充条目（{len(miss)} 条，原件未收）\n')
        for i, m in enumerate(miss, 1):
            parts.append(f'\n**补-{i}**　{m.get("name", "")}\n')
            parts.append(f'- 发文机关：{m.get("issuer", "")}\n')
            parts.append(f'- 日期：{m.get("date", "")}\n')
            parts.append(f'- 链接：{m.get("link", "")}\n')
            parts.append(f'- 复核员说明：{m.get("why", "")}\n')
    if errs:
        parts.append(f'\n#### 复核订正（{len(errs)} 处）\n')
        for i, e in enumerate(errs, 1):
            parts.append(f'\n{i}. **原件说法**：{e.get("claim", "")}\n')
            parts.append(f'   **问题**：{e.get("problem", "")}\n')
    if fabs:
        parts.append(f'\n#### 无法核实 / 疑编造（{len(fabs)} 条，**不要采信**）\n')
        for i, f in enumerate(fabs, 1):
            parts.append(f'\n{i}. **条目**：{f.get("item", "")}\n')
            parts.append(f'   **核实情况**：{f.get("evidence", "")}\n')
    if r.get('summary'):
        parts.append(f'\n#### 复核员总判\n\n{r["summary"]}\n')

parts.append(f'\n---\n\n**C6/C7 复核合计**：漏 {tot["m"]} ｜ 错 {tot["e"]} '
             f'｜ 无法核实 {tot["f"]} ｜ 复核链接 {tot["c"]} ｜ 坏链接 {tot["b"]}\n')

parts.append(f'\n## {n+2} 核验记录\n')
parts.append(
    f'- {len(SECTIONS)} 个领域分组（C1–C7）各自独立检索、独立落盘，原始素材保留在 `_素材/`。\n'
    '- 每项均给出「文件名｜发文机关｜印发或施行日期｜链接｜是否打开全文」，导语为官方新闻稿照抄，未作概括。\n'
    '- 广东落地情况逐项对照，列在各自分组的「广东落地」小节内。\n'
    '- C6（生态环境）、C7（文化）于 2026-09-28 补齐，各配一路独立复核员，结果见上一节。\n'
    '- 本文件由 `tools/assemble_central.py` 自动合装，可重复生成。\n'
)

text = '\n'.join(parts)
OUT.write_text(text, encoding='utf-8')
print(f'已写出: {OUT}')
print(f'总字符: {len(text)} | 汉字: {hanzi(text)} | 分组: {len(SECTIONS)}')
