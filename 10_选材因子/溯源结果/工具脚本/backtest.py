#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回测：政府工作报告「当年工作安排」那一部分的短语，有多少原样进了申论卷子。

做法是纯机械的——
1) 从 _cache/ 里取当年那份省政府工作报告，切出「二、XXXX年工作安排」之后的正文；
2) 取该年各套卷的题干与材料全文；
3) 用 difflib 找长度 >= MIN 的连续重合块（去掉空白后逐字比），再把每块定位回
   「材料X〔N〕」或「题干」；
4) 对长度 >= DEEP 的块，把报告里的那一整段原文照抄出来，方便逐字对。

只列事实，不做判断。命题规律的结论由使用的人自己下。
"""
import re, os, glob, difflib

B = "/Users/jianguolingyun/公考/07_申论/申论"
RES = B + "/溯源结果"
CACHE = RES + "/_cache"
OUT = RES + "/_核对/回测_政府工作报告短语.md"

MIN = 8           # 入表的门槛：连续重合 8 个字以上
DEEP = 15         # 附录照抄整段原文的门槛

# 「工作安排」那一节的起止标题。换届年编号会变：
#   2023（十四届人大一次会议）是「三、2023年工作安排」；2026（十五五开局）是「三、2026年工作安排」。
REPORTS = {
    # 2022 年那两套卷的笔试是 2022-01-03（广东组织工作网公告，已 --check 核过），
    # 而 2022 年那份报告作于 2022-01-20，**比笔试晚 17 天**，命题时看不到，不能当母文件。
    # 所以 2022 卷比的是 2021 年那份（2021-01-24 马兴瑞作）。
    "2022": ("母文件_2021年广东省政府工作报告_eesia.txt", "三、2021年工作安排", "2022乡镇", "2021"),
    "2023": ("2023年广东省政府工作报告.txt", "三、2023年工作安排", None, "2023"),
    "2024": ("2024_政府工作报告_eesia.txt", "二、2024年工作安排", None, "2024"),
    "2025": ("2025年广东省政府工作报告_163.txt", "二、2025年工作安排", None, "2025"),
    "2026": ("2026年广东省政府工作报告_163.txt", "三、2026年工作安排", None, "2026"),
}
# 工作安排之后必然是这些之一，拿它当终止锚，免得把结束语和附件也算进来
END_PAT = re.compile(r"^(各位代表|附件\d*$|名词解释|四、|五、|六、)")
# 各卷该比哪一份报告：笔试前最近一份
YEAR_REPORT = {"2022": "2022", "2023": "2023", "2024": "2024",
               "2025": "2025", "2026": "2025"}   # 2026 年度笔试在 2025-12-07

BOILER = ["习近平新时代中国特色社会主义思想", "在推进中国式现代化建设中走在前列",
          "新时代中国特色社会主义", "推进中国式现代化", "中国特色社会主义"]


def nows(s):
    return re.sub(r"[\s　]", "", s)


def report_lines(tag):
    """返回工作安排那一节的行列表（未去空白）。"""
    if tag not in REPORTS:
        return None, None
    fn, anchor, sub = REPORTS[tag][:3]
    # sub 非空表示这份报告不在共用的 _cache/ 里，而在该卷自己的快照目录里
    p = os.path.join(RES + "/_cache_" + sub if sub else CACHE, fn)
    if not os.path.exists(p):
        return None, fn
    ls = [L.strip() for L in open(p, encoding="utf-8", errors="ignore")]
    i = next((k for k, L in enumerate(ls) if L.startswith(anchor)), None)
    if i is None:
        return None, fn
    j = next((k for k in range(i + 1, len(ls)) if END_PAT.match(ls[k])), len(ls))
    return [L for L in ls[i + 1:j] if L], fn


def load_report(tag):
    ls, fn = report_lines(tag)
    return (nows("".join(ls)) if ls else None), fn


def rep_label(tag):
    """实际比的是哪一年的报告——2022 卷比的是 2021 那份，标签不能跟着卷号走。"""
    return REPORTS[tag][3] if tag in REPORTS and len(REPORTS[tag]) > 3 else tag


def report_para(tag, phrase):
    """把命中短语所在的整段（前后各多带一段）照抄出来。只从工作安排那一节里取。"""
    segs, _ = report_lines(tag)
    if not segs:
        return []
    for k, s in enumerate(segs):
        if phrase in nows(s):
            return segs[max(0, k - 1): min(len(segs), k + 2)]
    return []


def kind_of(phrase):
    """粗分一下这块重合是「成句」还是「专有名词」。

    块里带逗号、顿号、句号这类断句符号，说明它跨了好几个词组，多半是整句照搬；
    一个标点都没有的，通常是一个机构名／工程名／固定提法（「全国一体化算力网络
    粤港澳大湾区国家枢纽节点」这种），长归长，不代表命题人抄了那句话。
    """
    return "成句" if re.search(r"[，。、；：]", phrase) else "名词"


def split_paper(path):
    """返回 [(定位名, 正文)]，按 材料X〔N〕 切；题干单独一块。"""
    t = open(path, encoding="utf-8").read()
    out = []
    m = re.search(r"(?m)^#+\s*题干", t)
    body, stem = (t[:m.start()], t[m.start():]) if m else (t, "")
    for mm in re.finditer(r"####\s*(材料[一二三四五六七八九十]+)(.*?)(?=####|\Z)", body, re.S):
        name = mm.group(1)
        for sm in re.finditer(r"〔(\d+)〕(.*?)(?=〔\d+〕|\Z)", mm.group(2), re.S):
            out.append(("%s〔%s〕" % (name, sm.group(1)), nows(sm.group(2))))
    if stem:
        out.append(("题干", nows(stem)))
    return out


rows, skipped = [], []
for path in sorted(glob.glob(B + "/溯源包_2022-2026/*_材料与题干.md")):
    base = os.path.basename(path).replace("_材料与题干.md", "")
    year = base[:4]
    rep = YEAR_REPORT.get(year)
    text, fn = load_report(rep) if rep else (None, None)
    if text is None:
        skipped.append((base, "%s 年省政府工作报告未抓取（`_cache/%s` 不存在）" % (rep, fn)))
        continue
    segs = split_paper(path)
    whole = "".join(s for _, s in segs)
    sm = difflib.SequenceMatcher(None, text, whole, autojunk=False)
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
    rows.append((base, rep, fn, hits))

md = ["# 回测：政府工作报告「当年工作安排」的短语，有多少原样进了卷子", "",
      "做法是纯机械的：从页面快照里切出报告「XXXX年工作安排」那一节（从该节标题起，"
      "到「各位代表」/「四、」/「附件」为止，结束语和十件民生实事不算），"
      "和各套卷的题干与材料去空白后逐字比对，列出 **%d 个字以上**的连续重合块，"
      "并定位它落在哪一则的哪一段。没有任何人工挑选。" % MIN, "",
      "**那一节的编号各年不一样**，脚本按实际标题取：2024、2025 是「二、XXXX年工作安排」，"
      "**2023 是「三、2023年工作安排」**（换届年，前面多了「一、过去五年工作回顾」「二、今后五年的目标任务」），"
      "**2026 也是「三、2026年工作安排」**（前面是「一、2025年和“十四五”时期工作回顾」「二、“十五五”时期的主要目标和重点任务」），"
      "**2022 两套卷比的是 2021 那份、取「三、2021年工作安排」**（见文末口径第一条：2022 年那份报告晚于笔试，不能用）。", "",
      "政治套话（「习近平新时代中国特色社会主义思想」「在推进中国式现代化建设中走在前列」等）已过滤，"
      "那几句在任何一年任何一份里都有，不构成信号。", "",
      "**各卷比的是哪一份报告**：按「笔试前最近一份」定。所以 2026 年两套卷比的是 "
      "**2025-01-15** 那份（2026 年度笔试在 2025-12-07，2026-01-26 那份报告在笔试之后）。", "",
      "## 总览", "",
      "| 卷 | 比哪年报告 | 命中处数 | 最长一块 |", "|---|---|---|---|"]
for base, rep, fn, hits in rows:
    top = hits[0] if hits else None
    md.append("| %s | %s | %d | %s |" %
              (base, rep_label(rep) if rep else rep, len(hits),
               ("**%d 字**（%s）　%s" % (top[0], kind_of(top[1]), top[1][:32]))
               if top else "——"))
md.append("")

for base, rep, fn, hits in rows:
    md += ["## %s" % base, "",
           "比对对象：**%s 年**省政府工作报告（`%s`）。命中 %d 处。" % (rep_label(rep), fn, len(hits)), ""]
    if not hits:
        md += ["一处也没有。", ""]
        continue
    md += ["| 字数 | 报告里的原话 | 落在卷子哪里 | 型 |", "|---|---|---|---|"]
    for size, phrase, where in hits:
        md.append("| %d | %s | %s | %s |" %
                  (size, phrase.replace("|", "丨"), where, kind_of(phrase)))
    md.append("")

deep = [(base, rep, s, p, w) for base, rep, fn, hits in rows
        for s, p, w in hits if s >= DEEP]
if deep:
    md += ["## 附：长命中的报告原文整段", "",
           "下面把上面表里 **%d 个字以上**的命中，连同它在报告里所处的整段，"
           "照抄一遍（前后各多带一段）。这样不用回去翻缓存，直接就能逐字对。" % DEEP, ""]
    seen = set()
    for base, rep, s, phrase, where in deep:
        if (rep, phrase) in seen:
            continue
        seen.add((rep, phrase))
        md += ["### %s ｜ %s ｜ %d 字" % (base, where, s), "",
               "- 命中的是这句：`%s`" % phrase, "",
               "- 报告（%s 年省政府工作报告）里的整段原文：" % rep, ""]
        for L in report_para(rep, phrase):
            md.append("  > %s" % L)
        md += ["", ""]

if skipped:
    md += ["## 没能比的", ""]
    for base, why in skipped:
        md.append("- %s：%s" % (base, why))
    md.append("")

md += ["## 这张表的口径", "",
       "- **入表门槛 8 个字**。再短就没有信息量了，政府和媒体共用一套现成表述，"
       "「高质量发展」「城乡区域协调发展」这类词在任何一年任何一份里都会撞上。"
       "表按字数从长到短排，**看得住的是排在最前面那几行**。",
       "- **只比了报告的「工作安排」部分**（「工作回顾」没有比）。"
       "因为要回测的那条规律说的是「第二部分」。",
       "- **表里最后一列「型」是个粗筛**：块里带逗号顿号句号的记「成句」，"
       "一个标点都没有的记「名词」。后者大多是机构名／工程名／固定提法——"
       "比如 2023 县级那处 21 字的「全国一体化算力网络粤港澳大湾区国家枢纽节点」，"
       "字数排第一，可它就是个专有名词，报告里出现在「韶关数据中心集群建设」那句，"
       "卷子材料里接的是「数据中心集群，打造千亿级电子信息和大数据产业集群」，"
       "名头共用、后面各走各的。**真正值得看的是「成句」那一类的长块。**",
       "- **重合的方向是分不出来的**。卷子材料大量取自笔试前几个月的新闻报道，"
       "而新闻报道本身就会引报告里的原话。所以这一块重合到底是从报告来的、"
       "还是从引了报告的新闻来的，这张表答不了，得回到 `溯源结果_*.md` 去看那一段的主来源。",
       "- **各卷比的是「笔试前最近一份」报告，不是「同一年那份」**。这一点在 2022 卷上会翻车："
       "2022 年那两套卷的笔试是 **2022-01-03**（广东组织工作网公告），"
       "而 2022 年那份报告作于 **2022-01-20，比笔试晚 17 天**，命题时看不到。"
       "所以 **2022 卷比的是 2021 年那份**（2021-01-24 马兴瑞作，`三、2021年工作安排`）。"
       "其余各年是：2023 卷比 2023 年那份（2023-01-12）、2024 卷比 2024 年那份、"
       "2025 卷比 2025 年那份、2026 卷比 **2025** 年那份（2026 年度笔试在 2025-12-07）。",
       "- **五年都齐了**。2022、2023 两份报告是后补的，来源都是广东省人民政府门户网站 "
       "（2022：gd.gov.cn/gkmlpt/content/3/3774/post_3774882.html，作于 2022-01-20；"
       "2023：gd.gov.cn/gdywdt/zwzt/2023gdlh/bgsl/content/post_4083408.html，作于 2023-01-12），"
       "两份都过了 `fetch.py --check`；另有 2021 年那份存在 `_cache_2022乡镇/` 下，供 2022 卷比对用。", ""]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(md))
print("已写 %s" % OUT)
for base, rep, fn, hits in rows:
    top = hits[0] if hits else None
    print("%-10s 比%s报告  命中%3d 处  最长：%s" %
          (base, rep_label(rep) if rep else rep, len(hits), ("%d字 %s" % (top[0], top[1][:36])) if top else "——"))
for base, why in skipped:
    print("%-10s 跳过：%s" % (base, why))
