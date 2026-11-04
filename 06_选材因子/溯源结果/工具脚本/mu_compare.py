#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""母文件机械比对：每一套卷，跟手上每一份母文件都逐字比一遍。

为什么要有这个：提示词要求「每段先拿母文件逐句比一遍，再去搜新闻；母文件里有的，
不要判成命题人自撰」。但 12 份交付件里只有少数几份留下了比对的痕迹，有的连笔试
日期都没写（不知道时间窗，就不知道该比哪一份）。

这个脚本把这件事一次做完，纯机械、只读：
1) 把手上六份省政府工作报告（2021—2026）和三份高质量发展大会讲话全文都当候选母文件；
2) 每套卷的题干+材料去空白后，跟每个候选做一次最长重合扫描；
3) 按「一份报告 vs 一套卷」汇总：≥MIN 字的段有几段、最长多少、落在哪一段。

**它不判断该用哪份母文件**——那要看笔试日期。它只把「跟每一份各重合多少」摆出来，
哪一份明显高出来，那份多半就是母文件；都不高，说明这套卷跟母文件关系不大。

只输出事实表，不做命题规律的分析。
"""
import re, os, glob, difflib

B = "/Users/jianguolingyun/公考/07_申论/申论"
RES = B + "/溯源结果"
OUT = RES + "/_核对/母文件机械比对.md"

MIN = 8            # 入表门槛
DEEP = 15          # 明细里值得照抄原文的门槛

# 候选母文件：能拿到全文的，都算
SOURCES = {
    "2021报告": RES + "/_cache_2022乡镇/母文件_2021年广东省政府工作报告_eesia.txt",
    "2022报告": RES + "/_cache/2022年广东省政府工作报告.txt",
    "2023报告": RES + "/_cache/2023年广东省政府工作报告.txt",
    "2024报告": RES + "/_cache/2024_政府工作报告_eesia.txt",
    "2025报告": RES + "/_cache/2025年广东省政府工作报告_163.txt",
    "2026报告": RES + "/_cache/2026年广东省政府工作报告_163.txt",
}
# 讲话全文藏在母文件_*.md 的引用块里，抓 > 开头的行
SPEECHES = {
    "2024大会讲话": RES + "/_parts2/母文件_2024.md",
    "2025大会讲话": RES + "/母文件_2025.md",
    "2026大会讲话": RES + "/_parts2/母文件_2026.md",
}

BOILER = ["习近平新时代中国特色社会主义思想", "在推进中国式现代化建设中走在前列",
          "新时代中国特色社会主义", "推进中国式现代化", "中国特色社会主义",
          "以习近平同志为核心的党中央", "习近平总书记"]


def nows(s):
    return re.sub(r"[\s　​]", "", s)


def load_source(path):
    """正文纯文本；.md 的只取引用块（> 开头），免得把我们的注释也当母文件。"""
    if not os.path.exists(path):
        return None
    lines = open(path, encoding="utf-8", errors="ignore").read().split("\n")
    if path.endswith(".md"):
        lines = [re.sub(r"^\s*>\s?", "", l) for l in lines if l.strip().startswith(">")]
    return nows("".join(lines))


def split_paper(path):
    """返回 [(定位名, 去空白正文)]，两种标题风格都认；题干单独一块。"""
    t = open(path, encoding="utf-8").read()
    m = re.search(r"(?m)^#+\s*题干", t)
    body, stem = (t[:m.start()], t[m.start():]) if m else (t, "")
    out, cur = [], None
    for line in body.split("\n"):
        h = re.match(r"^#{2,4}\s*(材料[一二三四五六七八九十]+)\s*$", line)
        if h:
            cur = h.group(1)
            continue
        for sm in re.finditer(r"〔(\d+)〕", line):
            pass
    # 用「标题 + 〔n〕」两级切：先按材料标题分段，再按〔n〕切
    for mm in re.finditer(r"^#{2,4}\s*(材料[一二三四五六七八九十]+)\s*$(.*?)(?=^#{2,4}\s|\Z)",
                          body, re.S | re.M):
        name = mm.group(1)
        chunk = mm.group(2)
        parts = re.split(r"^〔(\d+)〕", chunk, flags=re.M)
        for k in range(1, len(parts), 2):
            out.append(("%s〔%s〕" % (name, parts[k]), nows(parts[k + 1])))
    if stem:
        out.append(("题干", nows(stem)))
    return out


srcs = {}
for tag, path in list(SOURCES.items()) + list(SPEECHES.items()):
    t = load_source(path)
    if t:
        srcs[tag] = t
    else:
        print("!! 取不到：%s（%s）" % (tag, path))

papers = sorted(glob.glob(B + "/溯源包_2022-2026/*_材料与题干.md"))
matrix = []          # (卷, {源: (段数, 最长, 最长串)})
for path in papers:
    base = os.path.basename(path).replace("_材料与题干.md", "")
    segs = split_paper(path)
    whole = "".join(s for _, s in segs)
    per = {}
    for tag, txt in srcs.items():
        sm = difflib.SequenceMatcher(None, txt, whole, autojunk=False)
        best, n = 0, 0
        for b in sm.get_matching_blocks():
            if b.size < MIN:
                continue
            phrase = whole[b.b:b.b + b.size]
            if any(x in phrase for x in BOILER):
                continue
            n += 1
            best = max(best, b.size)
        per[tag] = (n, best, whole[b.b:b.b + best] if best else "")
    matrix.append((base, per, segs))

md = ["# 母文件机械比对：每套卷 vs 手上的每一份母文件", "",
      "提示词要求「每段先拿母文件逐句比一遍，再去搜新闻」。12 份交付件里只有少数几份留下了"
      "比对的痕迹，有几份连笔试日期都没写。这个脚本把这件事**一次做完，纯机械、只读**：", "",
      f"1. 候选母文件＝手上能拿到全文的 **{len(srcs)} 份**（六份省政府工作报告 2021—2026，"
      "三份全省高质量发展大会讲话——讲话全文从 `母文件_*.md` 的引用块里取）；",
      "2. 每套卷的题干+材料去空白后，跟每个候选做一次最长连续重合扫描；",
      f"3. 按「一份母文件 vs 一套卷」汇总：≥{MIN} 字的**重合块**有几块、最长多少。", "",
      "**它不替你判断该用哪份母文件**——那要看笔试日期。它只把「跟每一份各重合多少」摆出来："
      "哪一份明显高出来，那份多半就是母文件；**都不高，说明这套卷跟母文件关系不大**，"
      "这是结论，不是失败。", "",
      "政治套话（「习近平新时代中国特色社会主义思想」「习近平总书记」等）已过滤，"
      "那几句在任何一年任何一份里都有，不构成信号。", "",
      "## 一、矩阵：横看一套卷，跟每份母文件各重合多少", "",
      "每格是「≥%d 字的重合**块**数 ／ 最长重合字数」。" % MIN, "",
      "| 卷 | " + " | ".join(srcs) + " |",
      "|---" * (len(srcs) + 1) + "|"]
for base, per, _ in matrix:
    cells = []
    for tag in srcs:
        n, best, _s = per[tag]
        cells.append("**%d ／ %d**" % (n, best) if n else "—")
    md.append("| %s | %s |" % (base, " | ".join(cells)))
md.append("")

md += ["## 二、每套卷最好的那一份，及明细", "",
       "下面只列**最强的那一份母文件**，以及它跟这套卷重合 ≥%d 字的每一块。" % MIN, ""]
for base, per, segs in matrix:
    tag, (n, best, _s) = max(per.items(), key=lambda kv: (kv[1][1], kv[1][0]))
    whole = "".join(s for _, s in segs)
    md += ["### %s", ""][:1]
    md[-1] = "### %s" % base
    md += ["最强的一份：**%s**（≥%d 字的重合 %d 段，最长 %d 字）。" % (tag, MIN, n, best), ""]
    if not n:
        md += ["一套卷跟手上任何一份母文件都没有 %d 字以上的连续重合。" % MIN, ""]
        continue
    txt = srcs[tag]
    sm = difflib.SequenceMatcher(None, txt, whole, autojunk=False)
    hits = []
    for b in sm.get_matching_blocks():
        if b.size < MIN:
            continue
        phrase = whole[b.b:b.b + b.size]
        if any(x in phrase for x in BOILER):
            continue
        where = next((nm for nm, s in segs if s.find(phrase) >= 0), "?")
        hits.append((b.size, phrase, where))
    hits.sort(key=lambda h: -h[0])
    md += ["| 字数 | 母文件里的原话 | 落在卷子哪里 |", "|---|---|---|"]
    for size, phrase, where in hits:
        md.append("| %d | %s | %s |" % (size, phrase.replace("|", "丨"), where))
    md.append("")

md += ["## 三、这张表的口径", "",
       "- **门槛 %d 字**。政府和媒体共用一套现成表述，「高质量发展」这类词在任何一份里都会撞上；"
       "表按字数从长到短排，**看得住的是最前面那几行**。" % MIN,
       "- **只比了「材料与题干」**，没有把交付件里的来源链接也算进来。",
       "- **重合的方向分不出来**：卷子材料大量取自笔试前几个月的新闻报道，而报道本身就会引"
       "母文件里的原话。所以重合到底是从母文件来的、还是从引了母文件的新闻来的，这张表答不了，"
       "得回到各卷的 `溯源结果_*.md` 去看那一段的主来源。",
       "- **两份母文件可能互相重**：大会讲话和政府工作报告常共用同一批提法，所以一套卷可能在"
       "两份上都高。这不是矛盾，是两个文本本来就像。", ""]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(md))
print("已写 %s" % OUT)
print()
hdr = "%-12s" % "卷" + "".join("%-12s" % t for t in srcs)
print(hdr)
for base, per, _ in matrix:
    row = "%-12s" % base
    for tag in srcs:
        n, best, _s = per[tag]
        row += "%-12s" % ("%d/%d" % (n, best) if n else "—")
    print(row)
