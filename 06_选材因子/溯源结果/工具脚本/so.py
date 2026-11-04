#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""360 搜索小助手（DDG 403 时的替代）。
用法: python3 so.py "关键词" [页码]  -> 打印标题+链接+摘要
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


def search(q, page=1):
    url = "https://www.so.com/s?q=" + urllib.parse.quote(q) + "&pn=%d" % page
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
    for m in re.finditer(r'<li class="res-list[^"]*".*?(?=<li class="res-list|</ol>)', raw, re.S):
        blk = m.group(0)
        a = re.search(r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
        if not a:
            continue
        href = F.html.unescape(a.group(1))
        title = re.sub(r"<[^>]+>", "", a.group(2))
        txt = re.sub(r"<[^>]+>", " ", blk)
        txt = F.html.unescape(re.sub(r"\s+", " ", txt)).strip()
        out.append((title.strip(), href, txt[:400]))
    for i, (t, u, s) in enumerate(out):
        print("%2d. %s\n    %s\n    ~ %s" % (i + 1, t, u, s))
    return out


if __name__ == "__main__":
    q = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    search(q, p)
