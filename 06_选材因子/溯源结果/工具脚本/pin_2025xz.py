#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 2025 县镇卷的每一段材料，拿去和 _cache_2025县镇/ 里所有页面快照做最长逐字重合比对。

输出：每段的最佳命中（快照名 + 行号 + 逐字片段）。
只报长度 >= MIN 的命中；没有的报 NONE。

用法:
  python3 pin_2025xz.py                 # 全部段
  python3 pin_2025xz.py 材料六           # 只看某则
  python3 pin_2025xz.py 材料四 12        # 只看材料四〔12〕
"""
import io, os, re, sys

BASE = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果"
CACHE = os.path.join(BASE, "_cache_2025县镇")
SRC = "/Users/jianguolingyun/公考/07_申论/申论/溯源包_2022-2026/2025县镇_材料与题干.md"
N = 12          # n-gram 长度
MIN = 12        # 最短命中长度


def load_segments():
    segs = {}
    cur = None
    for ln in io.open(SRC, encoding="utf-8"):
        ln = ln.rstrip("\n")
        m = re.match(r"^####\s*(材料[一二三四五六七八九十]+)\s*$", ln)
        if m:
            cur = m.group(1)
            continue
        if ln.startswith("###") and cur:
            cur = None
            continue
        m = re.match(r"^〔(\d+)〕(.*)$", ln)
        if m and cur:
            segs[(cur, int(m.group(1)))] = m.group(2).strip()
    return segs


def load_snaps():
    out = {}
    for fn in sorted(os.listdir(CACHE)):
        if not fn.endswith(".txt"):
            continue
        p = os.path.join(CACHE, fn)
        try:
            out[fn] = io.open(p, encoding="utf-8").read()
        except Exception:
            pass
    return out


def build_idx(txt):
    idx = {}
    for i in range(len(txt) - N + 1):
        idx.setdefault(txt[i:i + N], []).append(i)
    return idx


def best_match(seg, txt, idx):
    """返回 (最长逐字片段, 起始位置)。用 n-gram 索引 + 前后扩。"""
    best = ""
    bestpos = -1
    seen = set()
    for i in range(len(seg) - N + 1):
        g = seg[i:i + N]
        for p in idx.get(g, ())[:8]:
            # 从这对 (i,p) 出发，向前扩
            a, b = i, p
            while a > 0 and b > 0 and seg[a - 1] == txt[b - 1]:
                a -= 1
                b -= 1
            # 向后扩
            c, d = i + N, p + N
            while c < len(seg) and d < len(txt) and seg[c] == txt[d]:
                c += 1
                d += 1
            key = (a, b)
            if key in seen:
                continue
            seen.add(key)
            if c - a > len(best):
                best = seg[a:c]
                bestpos = b
    return best, bestpos


def lineof(txt, pos):
    if pos < 0:
        return 0, 0
    ln = txt.count("\n", 0, pos) + 1
    col = pos - (txt.rfind("\n", 0, pos) + 1)
    return ln, col


def main():
    segs = load_segments()
    snaps = load_snaps()
    print("材料段数 %d，快照 %d 个\n" % (len(segs), len(snaps)))
    want = sys.argv[1:]
    keys = sorted(segs, key=lambda k: (k[0], k[1]))
    hit = dict((k, []) for k in keys)
    for name, txt in snaps.items():          # 外层走快照，索引只建一次
        idx = build_idx(txt)
        for k in keys:
            b, p = best_match(segs[k], txt, idx)
            if len(b) >= MIN:
                ln, col = lineof(txt, p)
                hit[k].append((len(b), name, ln, col, b))
    for k in keys:
        if want:
            if len(want) == 1 and want[0] != k[0]:
                continue
            if len(want) == 2 and (want[0] != k[0] or str(k[1]) != want[1]):
                continue
        res = sorted(hit[k], reverse=True)
        print("### %s〔%d〕  段长 %d" % (k[0], k[1], len(segs[k])))
        if not res:
            print("    NONE（与所有快照无 >=%d 字逐字重合）" % MIN)
        for L, name, ln, col, b in res[:3]:
            print("    %3d 字  %s  L%d:C%d" % (L, name, ln, col))
            print("        %s" % b[:120].replace("\n", "⏎"))
        print()


main()
