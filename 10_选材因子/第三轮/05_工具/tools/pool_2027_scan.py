#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2027 候选池 · 第一道筛：从 2026 年报告里捞出「新增原文」

口径依据：任务三_严格同年检验.md 第六节
  2027 年度省考若沿用 2026 年起的提前节奏，笔试在 2026 年底，
  命题时最新、且唯一能看到的那份报告 = 2026 年报告（2026-01-26）。
  故候选池从 2026 年报告的「当年工作安排」（本文件标记为「## 二、第二部分全文」）里取。

办法（不引用任何外部清单，纯机械）：
  把「2026 年报告 − 以往报告」的差集用最长公共子串的补集算出来，
  得到两批「新增原文」：
    T1 = 2026 有、2019—2025 七年全没有   → 首现 2026（距离 0 年）
    T2 = 2026 有、2019—2024 六年全没有   → 首现 2025（距离 1 年）
  距离的参照系来自严格同年检验：已命中的 7 条短语，首现距考前报告平均 2.1 年，
  分布集中在 0—3 年。所以 T1/T2 是命中率最高的两档，T3（首现 2024，距离 2）作补充。

为什么用 8-gram 覆盖法而不是逐条查短语：
  逐条查只能验证「我已经想到的词」，覆盖法能捞出「我没想到的词」，避免自我确认。

纯本地计算，不联网、不耗检索额度。
数据：政府工作报告/政府工作报告_2019..2026.md
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REP_DIR = HERE / '政府工作报告'
YEARS = list(range(2019, 2027))
MINL = 8                     # 判定「同一段话」的最短重合长度（汉字）


def norm(s):
    return re.sub(r'[^一-鿿0-9]', '', s)


def load(year):
    """取该报告的「当年工作安排」全文。

    坑：2026 年报告的「结构说明」里引用了「## 二、第二部分全文」这几个字，
    用 re.search 会先命中那处引文，把目录、名词解释一起吞进来。
    故标记必须**顶格成行**（^## 二、第二部分全文$），且取最后一处。
    """
    t = (REP_DIR / f'政府工作报告_{year}.md').read_text(encoding='utf-8')
    ms = list(re.finditer(r'^## 二、第二部分全文\s*$', t, re.M))
    if not ms:
        raise SystemExit(f'{year} 未找到顶格的「## 二、第二部分全文」标记')
    return t[ms[-1].end():]


RAW = {y: load(y) for y in YEARS}
NORM = {y: norm(RAW[y]) for y in YEARS}
T26 = RAW[2026]


def ngrams(text, n=MINL):
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def sentences(text):
    """按句切开，保留句子本身（去掉标点后）。

    只切分句号与分号：申论命题取材的单位通常是一句话讲一件事，
    逗号内部还是同一件事，切开会把事项切碎。
    """
    out = []
    for s in re.split(r'[。；！？]', text):
        s = norm(s)
        if len(s) >= 12:          # 太短的碎句没有判断价值
            out.append(s)
    return out


def coverage(sent, bgset):
    """这句话的 8-gram 有多大比例是旧报告里已有的。

    1.0 = 整句都是老话；0.0 = 整句都是新话。
    比「有没有某个词」细，比「逐字比对」稳：个别新词不会把整句判成新句。
    """
    if len(sent) < MINL:
        return 1.0
    grams = [sent[i:i + MINL] for i in range(len(sent) - MINL + 1)]
    hit = sum(1 for g in grams if g in bgset)
    return hit / len(grams)


def novel_sentences(target, background_years, thresh=0.35):
    bg = ''.join(NORM[y] for y in background_years)
    bgset = ngrams(bg)
    scored = [(coverage(s, bgset), s) for s in sentences(target)]
    return [(c, s) for c, s in scored if c < thresh]


def year_vector(phrase):
    """某短语在八年报告里逐年有无。"""
    return {y: (phrase in NORM[y]) for y in YEARS}


def fmt_vec(phrase):
    return ''.join('●' if phrase in NORM[y] else '·' for y in YEARS)


def first_year(phrase):
    for y in YEARS:
        if phrase in NORM[y]:
            return y
    return None


if __name__ == '__main__':
    print('=' * 78)
    print('2027 候选池 · 新增原文扫描（2026 年报告 vs 2019—2025 年报告）')
    print(f'2026 年报告第二部分：{len(T26)} 汉字')
    print('=' * 78)

    sents = sentences(T26)
    print(f'2026 年报告第二部分切出 {len(sents)} 句')

    for name, bg_years, thresh in [
        ('T1  首现 2026（对比 2019—2025 全七年，距离 0 年）', list(range(2019, 2026)), 0.35),
        ('T2  首现 2025（对比 2019—2024 六年，距离 1 年）', list(range(2019, 2025)), 0.35),
        ('T3  首现 2024（对比 2019—2023 五年，距离 2 年）', list(range(2019, 2024)), 0.35),
    ]:
        res = novel_sentences(T26, bg_years, thresh)
        res.sort()
        print('\n' + '=' * 78)
        print(f'【{name}】新句 {len(res)} 句（重合率 < {thresh}）')
        print('=' * 78)
        for c, s in res:
            v = fmt_vec(s[:12])
            print(f'  [{c:.2f}] {s}')
            print(f'         ↑ 开头 12 字「{s[:12]}」的八年出现向量：{v}')
