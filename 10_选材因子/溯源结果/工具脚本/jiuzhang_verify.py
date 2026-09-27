#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《制造业九章》URL ↔ 章 的机械核对。

为什么要有这个脚本：`fetch.py --save` 只落纯文本、不落 URL，所以
`_cache_2023县级/制造业九章*.txt` 这些快照**没有记下自己是从哪个链接抓来的**。
九章要升格成母文件，URL 这一列就空了——而母文件的 URL 是要拿去点开核对的，
不能靠「看标题像」来填。

做法：把候选 URL 逐个抓回，跟每一份章快照逐句比对，
取「章快照里的长句有多少句能在该页面里逐字找到」当分。
一个字都不许猜——分低就是不成，宁可留空写「未核到」。

用法：
  python3 jiuzhang_verify.py              # 跑全部候选
  python3 jiuzhang_verify.py --url <U>    # 只跑一个候选
"""
import os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch, to_text, norm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "_cache_2023县级")
OUT = os.path.join(ROOT, "_cache_九章")

# 章 -> 该章的缓存快照文件名
CHAPTERS = {
    "一·方位": "制造业九章01_起家到当家_粤港澳大湾区门户网20221212.txt",
    "二·集群": "制造业九章02_集群_南方plus20221216.txt",
    "三·企业": "制造业九章03_企业_人民网广东20221221.txt",
    "四·创新": "制造业九章_强化创新驱动_南方plus.txt",
    "五·区域": "制造业九章05_区域_南方日报20221227.txt",
    "六·供应链": "制造业九章06_供应链_南方plus20221228.txt",
    "七·政府": "制造业九章07_政府_南方plus20230102.txt",
    "八·人才": "主心骨_广东锻造制造业当家_南方网.txt",
    "九·未来": None,  # 在 _cache_九章/ 下，单独处理
}
CH9 = os.path.join(OUT, "第九章_未来_粤港澳大湾区门户网20230105.txt")

# 候选 URL。按章分组，同章多个候选就是让脚本自己挑出对的那个。
CANDIDATES = [
    ("一·方位", "https://www.cnbayarea.org.cn/homepage/news/content/post_1032754.html"),
    ("一·方位", "https://news.southcn.com/node_ebf9d884ce/46be3ce32f.shtml"),
    ("二·集群", "http://gd.people.com.cn/n2/2022/1216/c123932-40233524.html"),
    ("二·集群", "https://static.nfnews.com/content/202212/15/c7175949.html"),
    ("二·集群", "https://static.nfapp.southcn.com/content/202212/15/c7179183.html"),
    ("二·集群", "https://news.ycwb.com/2022-12/16/content_41241906.htm"),
    ("三·企业", "http://gd.people.com.cn/n2/2022/1221/c123932-40238688.html"),
    ("三·企业", "https://static.nfapp.southcn.com/content/202212/21/c7194587.html"),
    ("四·创新", "https://static.nfnews.com/content/202212/23/c7200593.html"),
    ("五·区域", "https://static.nfapp.southcn.com/content/202212/27/c7212200.html"),
    ("五·区域", "https://www.cnbayarea.org.cn/news/focus/content/post_1034590.html"),
    ("六·供应链", "https://static.nfapp.southcn.com/content/202212/28/c7214975.html"),
    ("六·供应链", "https://news.ycwb.com/2022-12/28/content_41276119.htm"),
    ("七·政府", "https://static.nfapp.southcn.com/content/202301/02/c7226991.html"),
    ("七·政府", "https://static.nfapp.southcn.com/content/202301/02/c7227024.html"),
    ("八·人才", "https://news.southcn.com/node_54a44f01a2/0742577d49.shtml"),
    ("八·人才", "https://news.southcn.com/node_54a44f01a2/3715350ce6.shtml"),
    ("八·人才", "https://news.southcn.com/node_54a44f01a2/e104183a69.shtml"),
    ("九·未来", "https://static.nfapp.southcn.com/content/202301/05/c7235191.html"),
    ("九·未来", "https://news.southcn.com/node_54a44f01a2/2cdeb6bd50.shtml"),
    ("九·未来", "https://www.gd.gov.cn/gdywdt/zwzt/zqsk/ywsd/content/post_4075791.html"),
    ("九·未来", "http://gd.people.com.cn/n2/2023/0105/c123932-40254548.html"),
    ("九·未来", "https://www.cnbayarea.org.cn/homepage/news/content/post_1035431.html"),
]


def sentences(path, minlen=28, maxn=40):
    """从章快照里取「够长的正文行」当指纹。行太短的不算，免得噪声抬分。"""
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f]
    out = []
    for l in lines:
        l = re.sub(r"\s+", "", l)
        if len(l) >= minlen:
            out.append(l)
    # 均匀取样，避免全挤在头尾
    if len(out) > maxn:
        step = len(out) / maxn
        out = [out[int(i * step)] for i in range(maxn)]
    return out


def score(page_norm, fps):
    if not fps:
        return 0.0, 0, 0
    hit = sum(1 for s in fps if s in page_norm)
    return hit / len(fps), hit, len(fps)


def main():
    os.makedirs(OUT, exist_ok=True)
    only = None
    if "--url" in sys.argv:
        only = sys.argv[sys.argv.index("--url") + 1]

    fps = {}
    for ch, fn in CHAPTERS.items():
        p = CH9 if fn is None else os.path.join(CACHE, fn)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            fps[ch] = sentences(p)

    results = []
    for ch_claim, url in CANDIDATES:
        if only and url != only:
            continue
        tag = re.sub(r"[^0-9A-Za-z]+", "_", url)[-40:]
        save = os.path.join(OUT, "候选_%s.txt" % tag)
        if os.path.exists(save) and os.path.getsize(save) > 500:
            page = open(save, encoding="utf-8", errors="ignore").read()
            print("[cache] %s" % url)
        else:
            try:
                html_text, final = fetch(url)
                page = to_text(html_text)
                if len(page) < 500:
                    print("[SHORT %d] %s" % (len(page), url))
                    results.append((ch_claim, url, None, 0.0, 0, 0))
                    continue
                with open(save, "w", encoding="utf-8") as f:
                    f.write(page)
                print("[fetch] %s -> %s" % (url, os.path.basename(save)))
                time.sleep(1.5)
            except Exception as e:
                print("[FAIL %s] %s" % (e, url))
                results.append((ch_claim, url, None, 0.0, 0, 0))
                continue

        pn = norm(page)
        best, besthit, bestn = None, 0, 0
        row = []
        for ch, f in fps.items():
            r, h, n = score(pn, f)
            row.append((r, ch, h, n))
        row.sort(reverse=True)
        r, ch, h, n = row[0]
        results.append((ch_claim, url, ch, r, h, n))
        print("  声明=%s | 最匹配=%-8s 分=%.2f (%d/%d) | 次=%s %.2f" %
              (ch_claim, ch, r, h, n, row[1][1], row[1][0]))

    print("\n" + "=" * 70)
    print("汇总：声明章 == 实测章 的才算核到正身")
    print("=" * 70)
    ok = {}
    for ch_claim, url, ch, r, h, n in results:
        mark = "OK " if (ch == ch_claim and r >= 0.55) else "!! "
        if mark == "OK ":
            ok.setdefault(ch_claim, []).append((r, url))
        print("%s %-8s -> %-8s %.2f (%d/%d)  %s" % (mark, ch_claim, ch or "取不到", r, h, n, url))
    print("\n每章得分最高的正身 URL：")
    for ch in CHAPTERS:
        if ch in ok:
            ok[ch].sort(reverse=True)
            print("  %-8s %.2f  %s" % (ch, ok[ch][0][0], ok[ch][0][1]))
        else:
            print("  %-8s —— 未核到，留空" % ch)


if __name__ == "__main__":
    main()
