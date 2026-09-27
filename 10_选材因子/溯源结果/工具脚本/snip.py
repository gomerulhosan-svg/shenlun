#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 _cache_2022县级 的快照里按起止句截取原文，输出 markdown 引用块。
用法:
  python3 snip.py <cache文件> "起始句" "结束句" [前向段数] [后向段数]
输出: 每行前加 '> '，供直接贴进报告，保证逐字。
"""
import sys, os

BASE = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_cache_2022县级"

def main():
    f, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
    before = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    after = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    p = f if os.path.isabs(f) else os.path.join(BASE, f)
    lines = [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()]
    i = next((k for k, l in enumerate(lines) if start in l), None)
    if i is None:
        print("START_NOT_FOUND"); return 1
    j = next((k for k in range(i, len(lines)) if end in lines[k]), None)
    if j is None:
        print("END_NOT_FOUND"); return 1
    a, b = max(0, i - before), min(len(lines), j + 1 + after)
    for l in lines[a:b]:
        print("> " + l)
    return 0

if __name__ == "__main__":
    sys.exit(main())
