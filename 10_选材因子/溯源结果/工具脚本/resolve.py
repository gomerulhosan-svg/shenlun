#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 360 搜索的跳转链接还原成真实地址（不下载正文，只看 Location）。
用法: python3 resolve.py <so.com/link?...> [...]
"""
import sys, subprocess

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def resolve(url):
    cmd = ["curl", "-sSL", "-o", "/dev/null", "-m", "20", "-A", UA,
           "-H", "Accept-Language: zh-CN,zh;q=0.9", "--max-redirs", "5",
           "-w", "%{url_effective}"]
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout.decode("utf-8", "ignore").strip() or "RESOLVE_FAIL"


if __name__ == "__main__":
    for u in sys.argv[1:]:
        print(resolve(u))
