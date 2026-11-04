#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 溯源结果_2025县镇.md 里每一条「原文」块回访核验一遍。

做法：解析 md，找出每个「- 来源N：……｜<url>｜是否打开了全文：是」子弹后面紧跟的 `> ` 原文块，
对块内每一条长度 >= MINLEN 的行，用 `_tools/fetch.py <url> --check "<该行>"` 回访，
打印 CHECK FOUND / NOT_FOUND。带 1.5 秒间隔，别把站点打 403。

用法:
  python3 verify_2025xz.py            # 全跑
  python3 verify_2025xz.py --dry      # 只列出要核验的 (url, 行) 清单，不联网
"""
import io, os, re, subprocess, sys, time

BASE = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果"
TARGET = os.path.join(BASE, "溯源结果_2025县镇.md")
FETCH = os.path.join(BASE, "_tools", "fetch.py")
MINLEN = 25

txt = io.open(TARGET, encoding="utf-8").read()
lines = txt.split("\n")

src_re = re.compile(r"^\s*-\s*(来源\d+[^：]*|依据[^：]*|来源\s*\d*)[：:](.*)$")
url_re = re.compile(r"https?://[^\s｜|）)（(，,、]+")

jobs = []          # [(行号, url, 原文行)]
cur_url = None
for i, ln in enumerate(lines, 1):
    m = src_re.match(ln)
    if m:
        u = url_re.search(m.group(2))
        # 来源行里没有 URL 的（例如 §1.2 引母文件报告），把 cur_url 清空，免得张冠李戴
        cur_url = u.group(0).rstrip("，。").rstrip("）)") if u else None
        continue
    if ln.startswith(">"):
        body = ln[1:].strip()
        # 跳过说明性的块引用（以 ** 开头的是提醒/要点，不是原文）
        if body.startswith("**") or body.startswith("`"):
            continue
        if body.startswith("匿名对象识别") or body.startswith("说明"):
            continue
        if len(body) >= MINLEN:
            jobs.append((i, cur_url, body))
    elif "是否打开了全文" in ln:
        # §1.2 那种「**材料七〔1〕**｜…｜《2025 年广东省政府工作报告》｜是否打开了全文：是：」
        # 引的是母文件快照，不是网页；清掉 cur_url，免得张冠李戴
        u = url_re.search(ln)
        cur_url = u.group(0).rstrip("，。").rstrip("）)") if u else None
    elif ln.strip() == "":
        pass

# 去重
seen = set()
uniq = []
for i, u, b in jobs:
    k = (u, b[:40])
    if k in seen:
        continue
    seen.add(k)
    uniq.append((i, u, b))

print("待核验 %d 条（去重后），最小长度 %d" % (len(uniq), MINLEN))
if "--dry" in sys.argv:
    for i, u, b in uniq:
        print("  L%-5d %s\n         %s" % (i, u, b[:70]))
    sys.exit(0)

ok = bad = skip = 0
for i, u, b in uniq:
    if not u:
        print("L%-5d  [无URL，跳过] %s" % (i, b[:50]))
        skip += 1
        continue
    r = subprocess.run([sys.executable, FETCH, u, "--check", b],
                       capture_output=True, text=True, timeout=180)
    out = r.stdout
    if "CHECK FOUND" in out:
        ok += 1
        print("L%-5d  FOUND      %s" % (i, b[:40]))
    else:
        bad += 1
        tag = "NOT_FOUND" if "CHECK NOT_FOUND" in out else "FETCH_FAIL"
        print("L%-5d  %s  %s\n          url=%s\n          txt=%s" % (i, tag, b[:60], u, b[:80]))
    time.sleep(1.5)

print("\n汇总：FOUND %d / 异常 %d / 跳过 %d" % (ok, bad, skip))
