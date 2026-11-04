#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""头条搜索结构化版（tt.py 的补充，不动 tt.py）。
用法: python3 tt2.py "关键词" [页]
输出: 标题 | 摘要(常含日期/来源) + 落地页URL
"""
import sys, urllib.parse, re, json, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


def _un(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s


def _grab(raw):
    ts, ss, us = [], [], []
    for m in re.finditer(r'"title":\{(?:[^{}])*?"text":"((?:[^"\\]|\\.)*)"', raw):
        ts.append(re.sub(r"</?em>", "", _un(m.group(1))).strip())
    for m in re.finditer(r'"summary":\{(?:[^{}])*?"text":"((?:[^"\\]|\\.)*)"', raw):
        ss.append(re.sub(r"</?em>", "", _un(m.group(1))).strip())
    for m in re.finditer(r'"preload":\{"html":\["((?:[^"\\]|\\.)*)"', raw):
        us.append(_un(m.group(1)))
    return ts, ss, us


def search(q, page=0, tries=4):
    url = "https://so.toutiao.com/search?keyword=" + urllib.parse.quote(q)
    if page:
        url += "&offset=%d" % (page * 10)
    allt, alls, allu = [], [], []
    for _ in range(tries):
        try:
            raw, final = F.fetch(url)
        except Exception as e:
            print("SEARCH_FAIL", e)
            time.sleep(3)
            continue
        ts, ss, us = _grab(raw)
        for x in ts:
            if x and x not in allt:
                allt.append(x)
        for x in ss:
            if x and x not in alls:
                alls.append(x)
        for x in us:
            if x not in allu:
                allu.append(x)
        time.sleep(1.5)
    n = max(len(allt), len(alls))
    for i in range(n):
        t = allt[i] if i < len(allt) else ""
        s = alls[i] if i < len(alls) else ""
        print("%2d. %s\n    ~ %s" % (i + 1, t, re.sub(r"\s+", " ", s)[:320]))
    if allu:
        print("--- 落地页 ---")
        for u in allu[:20]:
            print("   ", u[:170])
    if not allt and not alls:
        print("NO_PARSE")
    return allt, alls, allu


if __name__ == "__main__":
    q = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    search(q, p)
