#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DDG 搜索小助手（WebSearch 额度用尽后的替代）。
用法: python3 ddg.py "关键词" [页码]  -> 打印标题+链接
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F

def search(q, page=0):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
    if page:
        url += "&s=%d" % (page * 30)
    for attempt in range(3):
        try:
            raw, final = F.fetch(url)
            break
        except Exception as e:
            err = e
            time.sleep(3)
    else:
        print("SEARCH_FAIL", err); return []
    h = raw
    out = []
    for m in re.finditer(r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', h, re.S):
        href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        href = urllib.parse.unquote(href)
        mm = re.search(r"uddg=([^&]+)", href)
        if mm:
            href = urllib.parse.unquote(mm.group(1))
        out.append((F.html.unescape(title).strip(), href))
    if not out:
        for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S):
            href = urllib.parse.unquote(m.group(1))
            mm = re.search(r"uddg=([^&]+)", href)
            if mm: href = urllib.parse.unquote(mm.group(1))
            out.append((re.sub(r"<[^>]+>", "", m.group(2)).strip(), href))
    # snippets
    snips = [re.sub(r"<[^>]+>", "", s).strip() for s in re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', h, re.S)]
    for i, (t, u) in enumerate(out):
        print("%2d. %s\n    %s" % (i + 1, t, u))
        if i < len(snips):
            print("    ~ %s" % F.html.unescape(snips[i])[:300])
    return out

if __name__ == "__main__":
    q = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    search(q, p)
