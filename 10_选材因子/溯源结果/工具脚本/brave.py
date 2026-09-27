#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brave Search 小助手（DDG/百度/360/搜狗都被限流时的替代）。
用法: python3 brave.py "关键词" [偏移]  -> 打印标题+链接+摘要
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


def search(q, offset=0):
    url = "https://search.brave.com/search?q=" + urllib.parse.quote(q)
    if offset:
        url += "&offset=%d" % offset
    raw = None
    err = None
    for _ in range(3):
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
    for m in re.finditer(r'<div class="snippet[^"]*"[^>]*data-pos="(\d+)"[^>]*>(.*?)(?=<div class="snippet[^"]*"[^>]*data-pos="|</main>)', raw, re.S):
        blk = m.group(2)
        a = re.search(r'<a href="(https?://[^"]+)"[^>]*>.*?<div class="title[^"]*"[^>]*>(.*?)</div>', blk, re.S)
        if not a:
            continue
        href = F.html.unescape(a.group(1))
        title = re.sub(r"<[^>]+>", "", a.group(2)).strip()
        sn = re.search(r'<div class="content[^"]*"[^>]*>(.*?)</div>', blk, re.S)
        snip = re.sub(r"<[^>]+>", " ", sn.group(1)) if sn else ""
        snip = re.sub(r"\s+", " ", F.html.unescape(snip)).strip()
        out.append((title, href, snip))
    for i, (t, u, s) in enumerate(out):
        print("%2d. %s\n    %s\n    ~ %s" % (i + 1, t, u, s[:400]))
    if not out:
        print("NO_RESULTS len=%d" % len(raw))
    return out


if __name__ == "__main__":
    q = sys.argv[1]
    off = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    search(q, off)
