#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cn.bing.com 搜索（mkt=zh-CN），打印标题+链接+摘要。"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F

def search(q, page=0):
    url = "https://cn.bing.com/search?q=" + urllib.parse.quote(q) + "&mkt=zh-CN&setlang=zh-CN"
    if page: url += "&first=%d" % (page*10+1)
    raw=None; err=None
    for _ in range(3):
        try:
            raw,final = F.fetch(url); break
        except Exception as e:
            err=e; time.sleep(4)
    if raw is None:
        print("SEARCH_FAIL", err); return []
    out=[]
    for m in re.finditer(r'<li class="b_algo".*?</li>', raw, re.S):
        blk=m.group(0)
        a=re.search(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
        if not a: continue
        href=F.html.unescape(a.group(1)); title=re.sub(r'<[^>]+>','',a.group(2))
        p=re.search(r'<p[^>]*>(.*?)</p>', blk, re.S)
        snip=F.html.unescape(re.sub(r'<[^>]+>','',p.group(1))).strip() if p else ''
        out.append((F.html.unescape(title).strip(),href,snip))
    for i,(t,u,s) in enumerate(out):
        print("%2d. %s\n    %s\n    ~ %s" % (i+1,t,u,s[:300]))
    if not out:
        print("[no b_algo blocks] len=%d" % len(raw))
    return out

if __name__=="__main__":
    search(sys.argv[1], int(sys.argv[2]) if len(sys.argv)>2 else 0)
