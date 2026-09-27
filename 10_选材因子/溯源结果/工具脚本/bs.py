#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bing 搜索小助手（WebSearch 额度用尽后的替代）。
用法: python3 bs.py "关键词" [页码]  -> 打印标题+链接+摘要
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


def search(q, page=1):
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(q) + "&first=%d" % (1 + (page - 1) * 10)
    raw = None
    err = None
    for _ in range(3):
        try:
            raw, final = F.fetch(url)
            break
        except Exception as e:
            err = e
            time.sleep(3)
    if raw is None:
        print("SEARCH_FAIL", err)
        return []
    out = []
    for m in re.finditer(r'<li class="b_algo".*?</li>', raw, re.S):
        blk = m.group(0)
        a = re.search(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
        if not a:
            continue
        href = F.html.unescape(a.group(1))
        title = F.html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip()
        sn = re.search(r'<p[^>]*>(.*?)</p>', blk, re.S)
        snip = F.html.unescape(re.sub(r"<[^>]+>", "", sn.group(1))) if sn else ""
        out.append((title, href, snip.strip()))
    for i, (t, u, s) in enumerate(out):
        print("%2d. %s\n    %s\n    ~ %s" % (i + 1, t, u, s[:300]))
    return out


if __name__ == "__main__":
    q = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    search(q, p)
