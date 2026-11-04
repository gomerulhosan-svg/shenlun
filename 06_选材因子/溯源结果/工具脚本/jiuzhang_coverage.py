#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《制造业九章》在各卷的露出度盘点。

要回答的问题：九章这条线，除了 2023 县级卷（会话 2 已经做过），**还覆盖了哪几卷哪些段**？
在此之前，九章只挂在 2023县级 一卷上——`_cache_*` 里除 `_cache_2023县级` 外，
其余 11 个卷目录里九章文件数都是 0。但九章刊发于 2022-12-12 ~ 2023-01-05，
凡笔试日在其后的卷子，都该拿它比一遍。

做法（纯机械、只读、不联网）：
1) 从 `母文件_制造业九章.md` 的引用块里，按 `### 第X章` 切出九章正文；
2) 每套卷按 `材料X〔N〕` 切段（口径同 `mu_compare.py` 的 `split_paper()`）；
3) 每段跟「九章全文拼接」做一次最长连续重合扫描，记下最长块的字数与**落在哪一章**；
4) 按卷汇总：≥门槛的段有几段、最长多少、最像哪一章。

门槛取 `mu_compare.py` 的同一套：MIN=8 入表，DEEP=15 明细，STRONG=25 才算强信号。

只输出事实表，不做命题规律的分析。
"""
import re, os, glob, difflib

RES = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果"
B = "/Users/jianguolingyun/公考/07_申论/申论"
MU = RES + "/母文件_制造业九章.md"
OUT = RES + "/_核对/九章露出度.md"

MIN, DEEP, STRONG = 8, 15, 25

# 政治套话：任何一年任何文章都有，不构成信号
BOILER = ["习近平新时代中国特色社会主义思想", "习近平总书记", "党中央",
          "中国式现代化", "社会主义现代化", "党的二十大精神", "高质量发展是",
          "省委十三届二次全会"]


def nows(s):
    s = re.sub(r"[\s　​]+", "", s)
    # 引号、破折号的排版变体统一，免得因为一个引号漏掉一整句
    for a, b in [("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"),
                 ("—", "-"), ("–", "-"), ("丨", "|")]:
        s = s.replace(a, b)
    return s


def load_chapters():
    """按 `### 第X章 …` 切出九章正文，返回 [(章标签, 正文)]。"""
    t = open(MU, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"(?m)^### (第[一二三四五六七八九]章 [^\n｜|]*)｜",
                         t):
        pass
    # 用「### 第X章 ...」到下一个 ### 或 ## 之间，取其中的引用块
    heads = list(re.finditer(r"(?m)^### (第[一二三四五六七八九]章 [^\n]+)$", t))
    for i, h in enumerate(heads):
        j = heads[i + 1].start() if i + 1 < len(heads) else t.find("\n## ", h.end())
        if j < 0:
            j = len(t)
        chunk = t[h.end():j]
        body = "\n".join(re.sub(r"^\s*>\s?", "", L)
                         for L in chunk.split("\n") if L.strip().startswith(">"))
        label = h.group(1).split("｜")[0].strip()
        out.append((label, nows(body)))
    return out


def split_paper(path):
    """返回 [(定位名, 去空白正文)]。口径同 mu_compare.py。"""
    t = open(path, encoding="utf-8").read()
    m = re.search(r"(?m)^#+\s*题干", t)
    body, stem = (t[:m.start()], t[m.start():]) if m else (t, "")
    out = []
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


def main():
    chapters = load_chapters()
    if len(chapters) != 9:
        raise SystemExit("只切出 %d 章，应为 9 章——母文件的标题格式变了？" % len(chapters))
    # 拼接九章全文，并记下每章在拼接串里的区间，好把命中位置映射回章
    spans, buf, pos = [], [], 0
    for label, txt in chapters:
        spans.append((label, pos, pos + len(txt)))
        buf.append(txt)
        pos += len(txt)
    whole_jz = "".join(buf)

    papers = sorted(glob.glob(B + "/溯源包_2022-2026/*_材料与题干.md"))
    rows = []
    for path in papers:
        base = os.path.basename(path).replace("_材料与题干.md", "")
        segs = split_paper(path)
        sm = difflib.SequenceMatcher(None, whole_jz, None, autojunk=False)
        hits = []
        for name, seg in segs:
            if len(seg) < MIN:
                continue
            sm.set_seq2(seg)
            best = (0, 0, "")
            for b in sm.get_matching_blocks():
                if b.size <= best[0]:
                    continue
                phrase = seg[b.b:b.b + b.size]
                if any(x in phrase for x in BOILER):
                    continue
                best = (b.size, b.a, phrase)
            if best[0] >= MIN:
                size, a, phrase = best
                ch = next((lb for lb, s, e in spans if s <= a < e), "?")
                hits.append((name, size, phrase, ch))
        rows.append((base, hits))

    md = ["# 《制造业九章》在各卷的露出度", "",
          "要回答的问题：九章这条线，**除了 2023 县级卷，还覆盖了哪几卷哪些段**？", "",
          "九章刊发于 **2022-12-12 ~ 2023-01-05**。在此之前，它只挂在一卷上——"
          "`_cache_*` 里除 `_cache_2023县级` 外，其余 11 个卷目录里九章文件数都是 **0**。",
          "凡笔试日在其后的卷子，都该拿它比一遍。本表把这件事一次做完，"
          "**纯机械、只读、不联网**。", "",
          "口径：",
          f"- 每段（`材料X〔N〕`）与「九章全文拼接」做最长连续重合扫描；",
          f"- **≥{MIN} 字**入表，**≥{DEEP} 字**列明细，**≥{STRONG} 字**才算强信号；",
          "- 政治套话（「习近平总书记」「中国式现代化」等）已过滤；",
          "- 引号/破折号的排版变体已统一，免得因为一个引号漏掉一整句；",
          "- 表里「落在哪一章」是**命中最长块**所在的那一章，不是整段的唯一来源。", "",
          "## 一、总表", "",
          "| 卷 | ≥%d 字段数 | ≥%d 字段数 | ≥%d 字段数 | 最长重合 | 最像的章 |"
          % (MIN, DEEP, STRONG),
          "|---|---|---|---|---|---|"]
    for base, hits in rows:
        n_min = len(hits)
        n_deep = sum(1 for h in hits if h[1] >= DEEP)
        n_strong = sum(1 for h in hits if h[1] >= STRONG)
        if not hits:
            md.append("| %s | 0 | 0 | 0 | — | — |" % base)
            continue
        top = max(hits, key=lambda h: h[1])
        from collections import Counter
        cnt = Counter(h[3] for h in hits if h[1] >= DEEP)
        chap = cnt.most_common(1)[0][0] if cnt else top[3]
        md.append("| %s | %d | %d | %d | **%d** | %s |"
                  % (base, n_min, n_deep, n_strong, top[1], chap))

    md += ["", "## 二、明细（只列 ≥%d 字的块）" % DEEP, ""]
    for base, hits in rows:
        deep = sorted([h for h in hits if h[1] >= DEEP], key=lambda h: -h[1])
        md.append("### %s" % base)
        md.append("")
        if not deep:
            md.append("与九章没有 ≥%d 字的连续重合。" % DEEP)
            md.append("")
            continue
        md.append("| 字数 | 卷子里的段 | 九章原话 | 落在 |")
        md.append("|---|---|---|---|")
        for name, size, phrase, ch in deep:
            md.append("| %d | %s | %s | %s |"
                      % (size, name, phrase.replace("|", "丨")[:90], ch))
        md.append("")

    md += ["## 三、这张表的口径与限度", "",
           "- **只比了「材料与题干」**（`溯源包_2022-2026/`），没有把交付件里的来源链接算进来；",
           "- **重合的方向分不出来**：卷子材料取自笔试前几个月的新闻报道，"
           "而报道本身常引九章的原话。所以这一块到底是从九章来的、还是从引了九章的新闻来的，"
           "这张表答不了，得回到各卷的 `溯源结果_*.md` 看那一段的主来源；",
           "- **九章也可能不是源头而是同源**：九章与同期的省政府工作报告、"
           "高质量发展大会讲话共用一大批提法，三者在同一段上都会高。", ""]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(md))
    print("已写 %s" % OUT)
    print()
    print("%-12s %6s %6s %6s   %s" % ("卷", ">=8", ">=15", ">=25", "最长/最像的章"))
    for base, hits in rows:
        if not hits:
            print("%-12s %6d %6d %6d   —" % (base, 0, 0, 0))
            continue
        top = max(hits, key=lambda h: h[1])
        print("%-12s %6d %6d %6d   %d 字 / %s"
              % (base, len(hits), sum(1 for h in hits if h[1] >= DEEP),
                 sum(1 for h in hits if h[1] >= STRONG), top[1], top[3]))


if __name__ == "__main__":
    main()
