#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""360 搜索小助手（WebSearch 额度用尽后的替代）。
用法: python3 srch.py "关键词" [页码]  -> 打印标题+链接+摘要
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


import subprocess


def resolve(u):
    """so.com/link 跳转页里藏着真实地址，取出来。"""
    try:
        r = subprocess.run(["curl", "-sSL", "-m", "20", "-A", F.UA, u], capture_output=True)
        m = re.search(rb'location\.replace\("([^"]+)"\)', r.stdout)
        if m:
            return m.group(1).decode("utf-8", "ignore")
    except Exception:
        pass
    return u


def search(q, page=1):
    url = "https://www.so.com/s?q=" + urllib.parse.quote(q)
    if page > 1:
        url += "&pn=%d" % page
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
    # 结果块：<h3 ...><a href=...>title</a></h3> ... 摘要
    out = []
    for m in re.finditer(r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S):
        href = F.html.unescape(m.group(1))
        if "so.com/link" in href:
            href = resolve(href)
        title = F.html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        tail = raw[m.end():m.end() + 3000]
        sn = re.search(r'class="res-desc"[^>]*>(.*?)</p>', tail, re.S)
        if not sn:
            sn = re.search(r'class="res-rich[^"]*"[^>]*>(.*?)</div>', tail, re.S)
        snip = F.html.unescape(re.sub(r"<[^>]+>", "", sn.group(1))) if sn else ""
        snip = re.sub(r"\s+", " ", snip).strip()
        out.append((title, href, snip))
    for i, (t, u, s) in enumerate(out):
        print("%2d. %s\n    %s\n    ~ %s" % (i + 1, t, u, s[:400]))
    return out


if __name__ == "__main__":
    q = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    search(q, p)
