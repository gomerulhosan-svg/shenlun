#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量跑特征词检索（360 搜索，用带引号的短词组），结果落 _cache_2022乡镇/检索_XX.txt"""
import sys, os, time, re, urllib.parse
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F

OUT = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_cache_2022乡镇"

QUERIES = [
    ("q01", "\"龙眼\"\"品种改良\" 广东"),
    ("q02", "\"百香果\"\"大棚膜\""),
    ("q03", "\"十大美丽乡村\"\"小林村\""),
    ("q04", "\"百香果\"\"精油\"\"洗洁精\""),
    ("q05", "\"龙眼蜜\" 直播"),
    ("q06", "\"轻骑队\" 宣讲 镇"),
    ("q07", "\"非遗进校园\" 剪纸 镇"),
    ("q08", "\"撂荒耕地复耕复种\" 现场"),
    ("q09", "\"百香果\" 无人机 试验园"),
    ("q10", "\"农超对接\"\"农企对接\""),
    ("q11", "\"新时代文明实践所\" 宣讲 榕树"),
    ("q12", "\"龙眼\" 直播带货 返乡"),
    ("q13", "\"文明实践\" 反诈宣传 科普展览"),
    ("q14", "\"生态停车场\" 碧道 村 广东"),
    ("q15", "\"制止耕地非粮化\" 撂荒 广东"),
]


def so(q, pn=1):
    url = "https://www.so.com/s?q=" + urllib.parse.quote(q)
    if pn > 1:
        url += "&pn=%d" % pn
    for a in range(3):
        try:
            raw, final = F.fetch(url, timeout=25, attempts=1)
            return raw
        except Exception as e:
            err = e
            time.sleep(5 + 5 * a)
    raise RuntimeError(err)


def parse(raw):
    out = []
    for m in re.finditer(r'<li class="res-list[^"]*".*?(?=<li class="res-list|</ol>)', raw, re.S):
        blk = m.group(0)
        a = re.search(r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
        if not a:
            continue
        md = re.search(r'data-mdurl="([^"]+)"', blk)
        real = F.html.unescape(md.group(1)) if md else a.group(1)
        title = F.html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip()
        txt = F.html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", blk))).strip()
        out.append((title, real, txt[:500]))
    return out


def main():
    for name, q in QUERIES:
        path = os.path.join(OUT, "检索_%s.txt" % name)
        if os.path.exists(path):
            print("SKIP", name)
            continue
        try:
            raw = so(q)
            rs = parse(raw)
        except Exception as e:
            print("FAIL", name, e)
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write("QUERY: %s\n\n" % q)
            for i, (t, u, s) in enumerate(rs):
                f.write("%d. %s\n   %s\n   ~ %s\n\n" % (i + 1, t, u, s))
        print("OK %-6s %-32s %d 条" % (name, q, len(rs)), flush=True)
        time.sleep(3)


if __name__ == "__main__":
    main()
