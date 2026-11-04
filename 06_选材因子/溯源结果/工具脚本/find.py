#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""搜索小助手（WebSearch 额度用尽后的替代；DDG/Bing/Baidu 均被封，用 360）。
360 搜索结果里 <a ... data-mdurl="真实地址"> 带着真实 URL，直接取出来。
用法: python3 find.py "关键词" [页码]
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


def search(q, page=1):
    url = "https://www.so.com/s?q=" + urllib.parse.quote(q) + "&pn=%d" % page
    raw = None
    err = None
    for attempt in range(4):
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
        md = re.search(r'data-mdurl="([^"]+)"', blk)
        real = F.html.unescape(md.group(1)) if md else ""
        title = F.html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip()
        txt = F.html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", blk))).strip()
        # 摘掉尾部噪声
        txt = re.sub(r"\s*反馈\s*$", "", txt)
        out.append((title, real, txt[:400]))
    for i, (t, u, s) in enumerate(out):
        print("%2d. %s\n    REAL: %s\n    ~ %s" % (i + 1, t, u or "(no mdurl)", s))
    return out


if __name__ == "__main__":
    q = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    search(q, p)
