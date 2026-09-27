#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需求五合装：把 9 个月的检索原件 + 9 份独立复核的结果，并成一份广东大事_2026.md

原则：
  - 检索员原件**一字不动**整块保留（含其自曝的未找到、来源分布说明）。
  - 复核员发现的**漏项**另起一节附在该月之后，标明「原件未收」，不混入正文。
  - 复核员指出的**错项与无法核实项**再起一节，逐条列出。

输入：_素材/广东大事_2026_MM.md × 9
      journal.jsonl（wf_91902fdd-d46）里的 9 个复核 result
输出：广东大事_2026.md
"""
import json
import re
from pathlib import Path

BASE = Path('/Users/jianguolingyun/公考/07_申论/申论/第三轮检索')
MAT = BASE / '_素材'
JOURNAL = Path('/Users/jianguolingyun/.claude/projects/-Users-jianguolingyun----07---'
               '/0f84f31a-1cbd-42fc-bfdf-108818ec19e3/subagents/workflows'
               '/wf_91902fdd-d46/journal.jsonl')
OUT = BASE / '广东大事_2026.md'

MONTHS = [f'{m:02d}' for m in range(1, 10)]


def parse_date(s):
    """从五花八门的日期串里取出第一个 YYYY-MM-DD 或 YYYY年M月D日，用于排序。"""
    if not s:
        return (9999, 99, 99)
    m = re.search(r'(20\d{2})[-年](\d{1,2})[-月](\d{1,2})', str(s))
    if m:
        return tuple(int(x) for x in m.groups())
    return (9999, 99, 99)


# ---- 载入复核结果 ----
rev = {}
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
    if not isinstance(v, dict) or 'missing' not in v:
        continue
    # month 字段两种写法都有：'2026-01' 与 '2026年3月'
    ms = str(v.get('month', ''))
    mm = re.search(r'(\d{1,2})\s*月', ms) or re.search(r'20\d{2}-(\d{1,2})\b', ms)
    if mm:
        rev[f'{int(mm.group(1)):02d}'] = v

missing_rev = [m for m in MONTHS if m not in rev]
if missing_rev:
    print(f'★ 警告：这些月份没有复核结果 {missing_rev}')

# ---- 合装 ----
parts = []
parts.append("""# 广东大事 2026 · 时间线（1—9 月）

> 需求五成品。九个独立月份，每月一路检索员 + 一路独立复核员。
> **检索员原件一字未动**整块保留；复核员独立重查后发现的漏项、错项，另起小节附在该月之后，
> 并明确标注「原件未收」或「原件有误」，不与正文混淆——这样哪一条是谁说的、哪一条经谁核过，一目了然。
> 取文方式：全程 `curl` 抓 HTML + `python3` 剥标签取正文，**未使用 WebFetch**。
> 复核方法：复核员各自独立爬取省政府网要闻栏全量列表、文件库五个文种栏、常务会议频道等，
> 与检索员清单逐条对表，并对每一条链接实际 curl 打开、逐字比对标题与导语。
> 合装日期：2026-09-28

""")

tot = {'missing': 0, 'errors': 0, 'fab': 0, 'checked': 0, 'broken': 0}

for mm in MONTHS:
    src = MAT / f'广东大事_2026_{mm}.md'
    if not src.exists():
        parts.append(f'\n---\n\n# 2026 年 {int(mm)} 月\n\n**★ 原件缺失**（{src.name} 不存在）\n')
        continue
    body = src.read_text(encoding='utf-8').strip()

    parts.append(f'\n---\n\n')
    parts.append(f'<!-- ===== 检索员原件：{src.name}（逐字保留） ===== -->\n')
    parts.append(body + '\n')

    r = rev.get(mm)
    if not r:
        parts.append('\n**★ 本月无复核结果**\n')
        continue

    miss = sorted(r.get('missing') or [], key=lambda x: parse_date(x.get('date')))
    errs = r.get('errors') or []
    fabs = r.get('fabricated') or []
    tot['missing'] += len(miss)
    tot['errors'] += len(errs)
    tot['fab'] += len(fabs)
    tot['checked'] += r.get('links_checked') or 0
    tot['broken'] += r.get('links_broken') or 0

    parts.append(f'\n## 【复核补充】{int(mm)} 月 · 独立复核发现的漏项（{len(miss)} 条）\n')
    parts.append('> 以下条目由复核员**独立检索**发现，检索员原清单未收。'
                 '复核员已逐条 curl 打开链接核对过标题与日期。\n')
    if not miss:
        parts.append('\n本月无漏项。\n')
    for i, m in enumerate(miss, 1):
        parts.append(f'\n### 补-{i}｜{m.get("date", "")}\n')
        parts.append(f'- 标题：{m.get("title", "")}\n')
        parts.append(f'- 链接：{m.get("link", "")}\n')
        parts.append(f'- 复核员说明：{m.get("why", "")}\n')

    parts.append(f'\n## 【复核订正】{int(mm)} 月 · 错项与无法核实项（{len(errs)} 条）\n')
    if not errs:
        parts.append('\n本月无错项。\n')
    for i, e in enumerate(errs, 1):
        parts.append(f'\n{i}. **原文说法**：{e.get("claim", "")}\n')
        parts.append(f'   **问题**：{e.get("problem", "")}\n')

    if fabs:
        parts.append(f'\n### 无法核实 / 疑编造（{len(fabs)} 条，**不要采信**）\n')
        for i, f in enumerate(fabs, 1):
            parts.append(f'\n{i}. **条目**：{f.get("item", "")}\n')
            parts.append(f'   **核实情况**：{f.get("evidence", "")}\n')

    if r.get('summary'):
        parts.append(f'\n### 复核员总判\n\n{r["summary"]}\n')

    parts.append(f'\n> 本月复核链接数：{r.get("links_checked")} ｜ 坏链接：{r.get("links_broken")}\n')

# ---- 卷末总表 ----
parts.append('\n\n---\n\n# 附：九个月复核总表\n\n')
parts.append('| 月份 | 漏 | 错 | 无法核实 | 复核链接数 | 坏链接 |\n|---|---|---|---|---|---|\n')
for mm in MONTHS:
    r = rev.get(mm)
    if not r:
        parts.append(f'| {int(mm)} 月 | — | — | — | — | — |\n')
        continue
    parts.append(f'| {int(mm)} 月 | {len(r.get("missing") or [])} | {len(r.get("errors") or [])} '
                 f'| {len(r.get("fabricated") or [])} | {r.get("links_checked")} '
                 f'| {r.get("links_broken")} |\n')
parts.append(f'| **合计** | **{tot["missing"]}** | **{tot["errors"]}** | **{tot["fab"]}** '
             f'| **{tot["checked"]}** | **{tot["broken"]}** |\n')

OUT.write_text(''.join(parts), encoding='utf-8')

han = len(re.findall(r'[一-鿿]', OUT.read_text(encoding='utf-8')))
print(f'已写出 {OUT.name}')
print(f'  汉字数 {han:,}')
print(f'  漏项合计 {tot["missing"]} ｜ 错项 {tot["errors"]} ｜ 无法核实 {tot["fab"]}')
print(f'  复核链接 {tot["checked"]} ｜ 坏链接 {tot["broken"]}')
