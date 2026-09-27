#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多引擎搜索（360 被限流时换百度）。
用法: python3 srch2.py "关键词" [引擎: so|baidu]
"""
import sys, urllib.parse, re, time, subprocess
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F


def resolve(u):
    try:
        r = subprocess.run(["curl", "-sSL", "-m", "20", "-A", F.UA, u], capture_output=True)
        m = re.search(rb'location\.replace\("([^"]+)"\)', r.stdout)
        if m:
            return m.group(1).decode("utf-8", "ignore")
    except Exception:
        pass
    return u


def so(q):
    raw, final = F.fetch("https://www.so.com/s?q=" + urllib.parse.quote(q))
    out = []
    for m in re.finditer(r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S):
        href = F.html.unescape(m.group(1))
        if "so.com/link" in href:
            href = resolve(href)
        title = F.html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        tail = raw[m.end():m.end() + 3000]
        sn = re.search(r'class="res-desc"[^>]*>(.*?)</p>', tail, re.S)
        snip = re.sub(r"\s+", " ", F.html.unescape(re.sub(r"<[^>]+>", "", sn.group(1)))).strip() if sn else ""
        out.append((title, href, snip))
    return out


def baidu(q):
    raw, final = F.fetch("https://www.baidu.com/s?wd=" + urllib.parse.quote(q) + "&rn=20")
    out = []
    for m in re.finditer(r'<h3[^>]*class="[^"]*t[^"]*"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S):
        href = F.html.unescape(m.group(1))
        title = re.sub(r"<[^>]+>", "", F.html.unescape(m.group(2))).strip()
        tail = raw[m.end():m.end() + 4000]
        sn = re.search(r'class="[^"]*c-abstract[^"]*"[^>]*>(.*?)</div>', tail, re.S)
        snip = re.sub(r"\s+", " ", F.unescape(re.sub(r"<[^>]+>", "", sn.group(1)))).strip() if sn else ""
        out.append((title, href, snip))
    return out


def show(rs):
    for i, (t, u, s) in enumerate(rs):
        print("%2d. %s\n    %s\n    ~ %s" % (i + 1, t, u, s[:400]))


if __name__ == "__main__":
    q = sys.argv[1]
    eng = sys.argv[2] if len(sys.argv) > 2 else "so"
    try:
        rs = so(q) if eng == "so" else baidu(q)
    except Exception as e:
        print("SEARCH_FAIL", e)
        rs = []
    if not rs and eng == "so":
        try:
            rs = baidu(q)
            print("[[fallback baidu]]")
        except Exception as e:
            print("BAIDU_FAIL", e)
    show(rs)
