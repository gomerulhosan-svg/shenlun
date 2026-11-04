#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多引擎搜索（WebSearch 额度用尽后的替代）。
用法: python3 s.py "关键词" [eng]      eng in {so,baidu}  默认 so
"""
import sys, urllib.parse, re, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F

ENGINES = {
    "so": "https://www.so.com/s?q=",
    "baidu": "https://www.baidu.com/s?wd=",
    "ddg": "https://html.duckduckgo.com/html/?q=",
}

def run(q, eng="so"):
    url = ENGINES[eng] + urllib.parse.quote(q)
    err = None
    for attempt in range(3):
        try:
            raw, final = F.fetch(url, timeout=25, attempts=1)
            t = F.to_text(raw)
            if len(t) > 300:
                print(t[:6000])
                return 0
            err = "short %d" % len(t)
        except Exception as e:
            err = e
        time.sleep(4 + 4 * attempt)
    print("SEARCH_FAIL", err)
    return 1

if __name__ == "__main__":
    q = sys.argv[1]
    eng = sys.argv[2] if len(sys.argv) > 2 else "so"
    sys.exit(run(q, eng))
