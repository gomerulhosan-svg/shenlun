#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bing 搜索小助手（DDG 被限速时的替代）。
用法: python3 bing.py "关键词" [页码]  -> 打印标题+链接
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


def search(q, page=0):
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(q) + "&setlang=zh-CN&ensearch=0"
    if page:
        url += "&first=%d" % (page * 10 + 1)
    raw = None
    err = None
    for attempt in range(3):
        try:
            raw, final = F.fetch(url)
            break
        except Exception as e:
            err = e
            time.sleep(4)
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
        title = re.sub(r"<[^>]+>", "", a.group(2))
        cap = re.search(r'<p[^>]*>(.*?)</p>', blk, re.S)
        snip = re.sub(r"<[^>]+>", "", cap.group(1)) if cap else ""
        out.append((F.html.unescape(title).strip(), href, F.html.unescape(snip).strip()))
    for i, (t, u, s) in enumerate(out):
        print("%2d. %s\n    %s\n    ~ %s" % (i + 1, t, u, s[:300]))
    return out


if __name__ == "__main__":
    q = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    search(q, p)
