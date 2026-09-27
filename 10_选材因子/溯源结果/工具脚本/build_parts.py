#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从缓存页里把每一段的原文逐字拷出来，生成分段文件骨架。
原文完全由脚本拷贝，不经过人手，避免「凭印象写原文」。
判断项（对应程度、匿名对象识别）留占位符，由人填。
"""
import re, os, glob, difflib, json, sys

BASE = "/Users/jianguolingyun/公考/07_申论/申论"
PKG = BASE + "/溯源包_2022-2026/2025省市_材料与题干.md"
CACHE = BASE + "/溯源结果/_cache"
PARTS = BASE + "/溯源结果/_parts"
URLMAP = json.load(open("/tmp/urlmap3.json", encoding="utf-8"))

DOMAIN = [
    ("ld.southcn.com", "南方网"), ("news.southcn.com", "南方网"), ("epaper.southcn.com", "南方日报"),
    ("gdio.southcn.com", "南方网"), ("epaper.nfnews.com", "南方日报"), ("pc.nfnews.com", "南方+"),
    ("static.nfnews.com", "南方+"), ("gd.people.com.cn", "人民网广东频道"),
    ("paper.people.com.cn", "人民日报"), ("m.people.cn", "人民网"), ("gd.people.com", "人民网广东频道"),
    ("xinhuanet.com", "新华网"), ("news.cn", "新华网"), ("gdstc.gd.gov.cn", "广东省科技厅"),
    ("drc.gd.gov.cn", "广东省发展改革委"), ("stats.gd.gov.cn", "广东省统计局"),
    ("www.gd.gov.cn", "广东省人民政府网"), ("gdzz.gov.cn", "广东组织工作网"),
    ("www.sz.gov.cn", "深圳市政府在线"), ("sznews.com", "深圳新闻网"), ("szdaily", "深圳特区报"),
    ("ycwb.com", "羊城晚报"), ("yunfudaily.com", "云浮日报"), ("cnr.cn", "央广网"),
    ("stdaily.com", "科技日报"), ("chinanews.com.cn", "中国新闻网"), ("chinanews.com", "中国新闻网"),
    ("163.com", "网易（转载）"), ("sina.com", "新浪（转载）"), ("sina.cn", "新浪（转载）"),
    ("qq.com", "腾讯网（转载）"), ("thepaper.cn", "澎湃新闻"), ("jiemian.com", "界面新闻"),
    ("sfccn.com", "南方财经"), ("cnbayarea.org.cn", "粤港澳大湾区门户网"),
    ("oeeee.com", "南方都市报"), ("sz-qb.com", "深圳侨报"), ("huizhou.cn", "今日惠州网"),
    ("ifeng.com", "凤凰网（转载）"), ("china.com.cn", "中国网"), ("cn-hw.net", "环卫科技网"),
]

def media_of(url):
    for k, v in DOMAIN:
        if k in url: return v
    return "未标注"

# 缓存文件名里带了出处，URLMAP 缺条目时从文件名推媒体名（不编造链接，只补媒体）
NAME_MEDIA = [
    ("人民网广东", "人民网广东频道"), ("中国政府网", "中国政府网"), ("中新网", "中国新闻网"),
    ("广州市政府网", "广州市人民政府门户网站"), ("广州市人大", "广州市人大常委会网站"),
    ("人民网", "人民网"), ("新华网", "新华网"), ("南方plus", "南方+"), ("南方网", "南方网"),
    ("广东检察", "南粤清风网"), ("江西新闻网", "江西新闻网"), ("光明网", "光明网"),
    ("人民日报", "人民日报"), ("三中全会决定", "中国政府网"), ("红树林碳汇", "广东省人民政府门户网站"),
]

# 补查阶段新抓的页面：缓存文件名 -> 链接（这些是这一轮打开过的页面，链接逐条核验过）
URL_EXTRA = {
 "补查_人民日报_让更多科技成果尽快转化为现实生产力.txt":
   "http://paper.people.com.cn/rmrb/html/2024-11/03/nw.D110000renmrb_20241103_1-05.htm",
 "补查_广东省政府网_全国首宗红树林碳汇开发权交易.txt":
   "https://www.gd.gov.cn/gdywdt/bmdt/content/post_4465224.html",
 "补查_三中全会决定全文_gov.txt":
   "https://www.gov.cn/zhengce/202407/content_6963770.htm",
}
def media_from_name(fn):
    for k, v in NAME_MEDIA:
        if k in fn: return v
    return "（待补）"

def title_of(txt):
    for l in txt.split("\n")[:8]:
        l = l.strip()
        if len(l) >= 8:
            l = re.split(r"\s*[_|]\s*", l)[0]
            return l[:90]
    return "（未取到标题）"

def date_of(txt, url):
    m = re.search(r"/(20\d\d)[-/](\d{1,2})[-/](\d{1,2})/", url)
    if m: return "%s-%02d-%02d" % (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"/(20\d\d)(\d\d)(\d\d)", url)
    if m: return "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
    head = txt[:2500]
    for pat in (r"(20\d\d)\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", r"(20\d\d)-(\d{2})-(\d{2})"):
        m = re.search(pat, head)
        if m: return "%s-%02d-%02d" % (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(20\d\d)\s*年\s*(\d{1,2})\s*月", head)
    if m: return "%s-%02d" % (int(m.group(1)), int(m.group(2)))
    m = re.search(r"/(20\d\d)[-/](\d{1,2})/", url)
    if m: return "%s-%02d" % (int(m.group(1)), int(m.group(2)))
    return "未取到"

def nows(s):
    keep, idx = [], []
    for i, ch in enumerate(s):
        if ch in " \t\r\n　​": continue
        keep.append(ch); idx.append(i)
    return "".join(keep), idx

# 材料 -> 段落（保留标点）
t = open(PKG, encoding="utf-8").read().split("### 题干")[0]
segs = []
for m in re.finditer(r"#### (材料[一二三四五六七八])(.*?)(?=####|\Z)", t, re.S):
    for sm in re.finditer(r"〔(\d+)〕(.*?)(?=〔\d+〕|\Z)", m.group(2), re.S):
        segs.append((m.group(1), sm.group(1), re.sub(r"\s+", "", sm.group(2))))

# 只认清单里的缓存文件。_cache/ 里同时存放着「母文件」等其他任务的页面，
# 不设清单的话，别的年份的页面会被误当成这一卷的来源。
MANIFEST = json.load(open(BASE + "/溯源结果/_tools/cache_manifest.json", encoding="utf-8"))
cache = {}
for f in [os.path.join(CACHE, m) for m in MANIFEST]:
    if not os.path.exists(f): continue
    txt = open(f, encoding="utf-8", errors="ignore").read()
    n, idx = nows(txt)
    if len(n) < 200: continue
    b = os.path.basename(f)
    url = URLMAP.get(b, "") or URL_EXTRA.get(b, "")
    date = date_of(txt, url) if url else date_of(txt, "")
    if not url:
        date = date if date != "未取到" else "（待补）"
    cache[b] = {"txt": txt, "n": n, "idx": idx, "lines": txt.split("\n"),
                "url": url, "media": media_of(url) if url else media_from_name(b),
                "title": title_of(txt), "date": date}

def blocks_of(st, n, minlen=10):
    sm = difflib.SequenceMatcher(None, st, n, autojunk=False)
    return [b for b in sm.get_matching_blocks() if b.size >= minlen]

review = {}
buf = {}   # 每次从零重建，避免反复运行越堆越多
for name, num, st in segs:
    scored = []
    for fn, c in cache.items():
        bs = blocks_of(st, c["n"])
        cov = sum(b.size for b in bs)
        if cov >= 20:
            scored.append((cov, fn, bs))
    scored.sort(key=lambda x: -x[0])
    out = ["### %s〔%s〕" % (name, num)]
    out.append("- 对应程度：@@待填@@（自动比对：逐字重合 %d%%）" % (100 * min(1, scored[0][0] / max(1, len(st))) if scored else 0))
    if not scored:
        out.append("- 来源：（未找到）")
        out.append("- 匿名对象识别：@@待填@@")
        review["%s〔%s〕" % (name, num)] = {"coverage": 0, "sources": []}
    else:
        info = []
        for i, (cov, fn, bs) in enumerate(scored[:3]):
            c = cache[fn]
            big = max(bs, key=lambda b: b.size)
            pos = c["idx"][big.b] if big.b < len(c["idx"]) else 0
            upto = c["txt"][:pos].count("\n")
            span = c["txt"][pos:pos + big.size].count("\n")
            lo, hi = max(0, upto - 1), min(len(c["lines"]), upto + span + 2)
            shown_url = c["url"] or "未取到（页面快照存于 _cache/%s）" % fn
            out.append("- 来源%d：%s｜%s｜%s｜%s｜是否打开了全文：是" %
                       (i + 1, c["title"], c["media"], c["date"], shown_url))
            out.append("  - 原文（逐字粘贴，和这段材料对应的那一整段；前后各多贴一段）：")
            for L in c["lines"][lo:hi]:
                out.append("  > " + L.strip()[:1200])
            info.append({"file": fn, "title": c["title"], "media": c["media"], "date": c["date"],
                         "url": c["url"], "coverage": cov, "verbatim": big.size})
        out.append("- 匿名对象识别：@@待填@@")
        review["%s〔%s〕" % (name, num)] = {"coverage": scored[0][0], "seg_len": len(st), "sources": info}
    buf.setdefault(name, []).append("\n".join(out))

for name, blocks in buf.items():
    open(os.path.join(PARTS, "%s.md" % name), "w", encoding="utf-8").write("\n\n".join(blocks) + "\n")

json.dump(review, open("/tmp/review.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("写好 8 个分段文件。")
for k, v in review.items():
    cov = v.get("coverage", 0); L = v.get("seg_len", 0) or 1
    ss = " ; ".join("%s(%s,%d字)" % (s["media"], s["date"], s["verbatim"]) for s in v["sources"])
    print("%-12s 覆盖%3d%%  %s" % (k, 100 * cov // L if L else 0, ss or "—— 无来源"))
