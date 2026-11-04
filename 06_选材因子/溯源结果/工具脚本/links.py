#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 360 搜索结果页抽真实链接（data-mdurl）+ 标题摘要。
用法: python3 links.py "关键词" [页码]
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F

def run(q, pn=1):
    url = "https://www.so.com/s?q=" + urllib.parse.quote(q)
    if pn > 1:
        url += "&pn=%d" % pn
    for a in range(3):
        try:
            raw, final = F.fetch(url, timeout=25, attempts=1)
            break
        except Exception as e:
            err = e; time.sleep(4 + 4 * a)
    else:
        print("SEARCH_FAIL", err); return 1
    seen = {}
    # title blocks: <h3 ...>...</h3>  plus data-mdurl in enclosing block
    for m in re.finditer(r'data-mdurl="([^"]+)"', raw):
        u = F.html.unescape(m.group(1))
        if any(d in u for d in ("360.com", "bing.com", "baidu.com", "weibo.com", "so.com")):
            continue
        seen[u] = seen.get(u, 0) + 1
    t = F.to_text(raw)
    print("---- 结果 URL ----")
    for u in seen:
        print(u)
    print("---- 页面文本（含摘要）----")
    print(t[:7000])
    return 0

if __name__ == "__main__":
    q = sys.argv[1]
    pn = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    sys.exit(run(q, pn))
