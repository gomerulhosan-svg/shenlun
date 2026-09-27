#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2027 候选池 · 第二道筛：从 2026 年报告里挑出「具体的新事项」

为什么不用第一版的整句比对：
  省政府工作报告逐年重写，措辞本就不照抄，8 字逐字重合的尺子在这个文体上
  会把 89% 的句子判成「新句」，没有分辨力（见 pool_2027_scan.py 的失败记录）。
  本项目已有的检验单位一直是**固定术语**（「零碳园区」「土特产」「海洋牧场」
  「古树名木」），命题人挑的也正是这种词。故改回术语级。

单位怎么定：
  1. 报告里带引号的词（“……”）——写报告的人自己标出来的专有说法，
     天然就是「事项级」的粒度，且不会切碎、不会跨句。
  2. 未加引号但有事项后缀的短语（……工程／行动／试点／平台／基地／园区／
     走廊／试验区……）——补引号漏掉的。

怎么判「新」：
  逐条算它在 2019—2026 八份报告「当年工作安排」里的出现向量，
  取「首现年份」= 第一次出现的那年。严格同年检验给出参照系——
  已命中的 7 条短语首现距考前报告平均 2.1 年，分布 0—3 年。
  2027 卷的考前报告是 2026 年那份，故 首现 2024—2026 的是第一梯队。

纯本地计算，不联网、不耗检索额度。
"""
import re
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REP_DIR = HERE / '政府工作报告'
OUT = HERE / '_候选池原始数据.json'
YEARS = list(range(2019, 2027))
TARGET_YEAR = 2026          # 扫描哪一年报告的「新增事项」


def norm(s):
    return re.sub(r'[^一-鿿0-9]', '', s)


def load(year):
    """取「当年工作安排」全文（原文，含标点）。

    坑：2026 年报告的「结构说明」里引用了「## 二、第二部分全文」这几个字，
    无锚点的 re.search 会先命中那处引文，把目录、名词解释一起吞进来。
    故标记须顶格成行，且取最后一处。
    """
    t = (REP_DIR / f'政府工作报告_{year}.md').read_text(encoding='utf-8')
    ms = list(re.finditer(r'^## 二、第二部分全文\s*$', t, re.M))
    if not ms:
        raise SystemExit(f'{year} 未找到顶格的「## 二、第二部分全文」标记')
    return t[ms[-1].end():]


RAW = {y: load(y) for y in YEARS}
NORM = {y: norm(RAW[y]) for y in YEARS}

# ---- 排除词：不是「事项」，是连接词、年份、政治表述等 ----
STOP = set("""
十五五 十四五 十三五 一带一路 一国两制 两个毫不动摇 两个确立 四个意识 四个自信 两个维护
四个出新出彩 五篇大文章 两新 两重 九五 各位代表 附件1 附件2 走出去
""".split())

# 事项后缀（未加引号时用来捞术语）
SUFFIX = ('工程', '行动', '计划', '方案', '试点', '示范', '平台', '基地', '园区', '中心',
          '走廊', '试验区', '示范区', '集群', '机制', '体系', '模式', '通道', '枢纽',
          '实验室', '研究院', '交易所', '基金', '债券', '清单', '目录', '标准', '条例',
          '办法', '规划', '纲要', '综合体', '联合体', '共同体', '先行区', '引领区')


def quoted_terms(text):
    return [x for x in re.findall(r'[“]([^“”]{2,14})[”]', text)]


def suffixed_terms(text):
    """捞「……工程／试点／平台……」形式的术语。

    从后缀字往前取 2—6 字做候选，再向右扩展到后缀末尾。
    """
    out = []
    for suf in SUFFIX:
        for m in re.finditer(suf, text):
            end = m.end()
            for back in range(2, 7):
                start = m.start() - back
                if start < 0:
                    break
                cand = text[start:end]
                if re.search(r'[，。；、：（）“”]', cand):
                    break
                out.append(cand)
    return out


def vec(term):
    n = norm(term)
    if len(n) < 2:
        return None
    return ''.join('●' if n in NORM[y] else '·' for y in YEARS)


def first_year(term):
    n = norm(term)
    for y in YEARS:
        if n in NORM[y]:
            return y
    return None


def appearances(term):
    n = norm(term)
    return [y for y in YEARS if n in NORM[y]]


def collect():
    text = RAW[TARGET_YEAR]
    cands = {}
    for t, src in [(x, 'quoted') for x in quoted_terms(text)] + \
                  [(x, 'suffix') for x in suffixed_terms(text)]:
        n = norm(t)
        if len(n) < 3 or len(n) > 14:
            continue
        if n in STOP or t in STOP:
            continue
        if re.fullmatch(r'[0-9]+', n):
            continue
        cands.setdefault(n, {'term': t, 'src': src})
    rows = []
    for n, meta in cands.items():
        v = vec(n)
        rows.append({
            'term': meta['term'], 'norm': n, 'src': meta['src'],
            'vec': v, 'first': first_year(n), 'years': appearances(n),
            'count': v.count('●'),
        })
    return rows


if __name__ == '__main__':
    rows = collect()
    print('=' * 86)
    print(f'2027 候选池 · 术语级扫描（源：{TARGET_YEAR} 年报告「当年工作安排」）')
    print(f'候选术语 {len(rows)} 条')
    print('=' * 86)

    by_first = {}
    for r in rows:
        by_first.setdefault(r['first'], []).append(r)

    for fy in [2026, 2025, 2024, 2023]:
        grp = by_first.get(fy, [])
        # 首现越晚越新；同年之内按在近期报告里的延续性排序（延续多 = 不是一次性提法）
        grp.sort(key=lambda r: (-r['count'], r['term']))
        print(f'\n【首现 {fy}】{len(grp)} 条  —— 距 2027 卷考前报告({TARGET_YEAR}) {TARGET_YEAR-fy} 年')
        print(f'  {"术语":<26}{"来源":<8}{"向量 19-26":<12}首现  延续')
        for r in grp[:80]:
            print(f'  {r["term"]:<26}{r["src"]:<8}{r["vec"]:<12}{r["first"]}   {r["count"]}')

    json.dump(rows, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n原始数据已存：{OUT}')
