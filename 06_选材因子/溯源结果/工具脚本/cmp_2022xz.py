#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2022乡镇卷：把每一段材料与母文件逐字比，找出最长公共片段。

用法:
  python3 cmp_2022xz.py <母文件.txt> [最小匹配长度]
输出: 每段命中的最长公共片段（>= 最小长度），带上下文。
"""
import sys, re, os, difflib

BASE = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果"
MAT = "/Users/jianguolingyun/公考/07_申论/申论/溯源包_2022-2026/2022乡镇_材料与题干.md"


def norm(s):
    s = re.sub(r"[\s　​]+", "", s)
    return s.replace("〔", "").replace("〕", "")


def load_segments():
    """返回 [(标签, 正文), ...]，标签形如 材料一〔1〕。"""
    txt = open(MAT, encoding="utf-8").read()
    txt = txt.split("### 题干")[0]
    out = []
    cur = None
    for line in txt.split("\n"):
        line = line.rstrip()
        if line.startswith("#### "):
            cur = line[5:].strip()
            continue
        m = re.match(r"^〔(\d+)〕(.*)$", line.strip())
        if m and cur:
            out.append(("%s〔%s〕" % (cur, m.group(1)), m.group(2)))
    return out


def blocks(seg, doc, n):
    """用 n-gram 索引找 seg 在 doc 中的所有匹配块，返回 [(长度, doc起, doc止), ...]"""
    dnorm = norm(doc)
    snorm = norm(seg)
    # 索引 doc 的 n-gram
    idx = {}
    for i in range(len(dnorm) - n + 1):
        idx.setdefault(dnorm[i:i + n], []).append(i)
    hits = []
    i = 0
    while i <= len(snorm) - n:
        g = snorm[i:i + n]
        pos = idx.get(g)
        if not pos:
            i += 1
            continue
        # 向前后扩展
        best = None
        for p in pos:
            a, b = i, p
            while a > 0 and b > 0 and snorm[a - 1] == dnorm[b - 1]:
                a -= 1
                b -= 1
            x, y = i + n, p + n
            while x < len(snorm) and y < len(dnorm) and snorm[x] == dnorm[y]:
                x += 1
                y += 1
            cand = (x - a, b - (i - a), (i - a, x), b + (x - a))
            if best is None or cand[0] > best[0]:
                best = cand
        if best:
            hits.append((best[0], best[1], best[2], dnorm, best[3]))
            i += max(1, best[2][1] - best[2][0])
        else:
            i += 1
    # 合并重叠、去掉被包含的
    hits.sort(key=lambda h: -h[0])
    kept = []
    for h in hits:
        s, e = h[2]
        if any(not (e <= k[2][0] or s >= k[2][1]) for k in kept):
            continue
        kept.append(h)
    kept.sort(key=lambda h: h[2][0])
    return kept


def main():
    doc_path = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    doc = open(doc_path, encoding="utf-8").read()
    print("== 母文件 %s（%d 字） n=%d ==" % (os.path.basename(doc_path), len(norm(doc)), n))
    segs = load_segments()
    print("== 材料段数 %d ==" % len(segs))
    for label, seg in segs:
        hs = blocks(seg, doc, n)
        hs = [h for h in hs if h[0] >= n]
        if not hs:
            continue
        print("\n### %s  （段长 %d）" % (label, len(norm(seg))))
        for ln, dstart, (s, e), dnorm, dend in hs[:6]:
            print("   · 长 %d ： %s" % (ln, dnorm[max(0, dstart - 15):dend + 15]))


if __name__ == "__main__":
    main()
