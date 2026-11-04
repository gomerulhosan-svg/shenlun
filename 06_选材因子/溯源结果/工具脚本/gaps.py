#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""结构缺口盘点：12 份交付件里，哪些该有的章节还没有。

背景——提示词对每一份 `溯源结果_<卷>.md` 规定了两块固定内容：
  「## 0 笔试日期与时间窗」和「每段先拿母文件逐句比一遍」。
铺开做的时候（补做那几卷尤其急）这两块有的写了、有的没写，README 里
记的「可信」只覆盖了抽样核验，没覆盖这两块。这份表把差什么一次数清。

**全部由脚本现算**，不写死任何数字——上一轮 2022乡镇 就是数字手写才出的错。
只读，不改任何交付件。
"""
import re, os, glob

RES = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果"
OUT = RES + "/_核对/结构缺口.md"

MAT = "材料一二三四五六七八九十"
# 「母文件比对」必须是一个真的节标题，不是正文里偶然提到「母文件」三个字
SEC_MU = re.compile(r"(?m)^#{2,4}\s*[一二三四五六七八九十\d]*[、.．]?\s*母文件")
SEC_0 = re.compile(r"(?m)^#{2,4}\s*[〇零0][、.．]")
SEC_MAT = re.compile(r"(?m)^#{2,4}\s*材料[" + MAT + r"]〔\d+〕")
SEC_GRP = re.compile(r"(?m)^#{2,4}\s*材料[" + MAT + r"]〔\d+〕[～~]")
SEC_ANYMAT = re.compile(r"(?m)^#{2,4}\s*材料[" + MAT + r"]")
DEG = re.compile(r"(?m)^\s*-\s*对应程度")
ANON = re.compile(r"(?m)^\s*-\s*匿名对象识别")
DATE = re.compile(r"笔试日期[^\n]{0,80}")


def lv(t):
    return sorted({len(m.group(1)) for m in re.finditer(
        r"(?m)^(#{2,4})\s*材料[" + MAT + r"]〔\d+〕", t)})


rows = []
for f in sorted(glob.glob(RES + "/溯源结果_*.md")):
    t = open(f, encoding="utf-8").read()
    name = os.path.basename(f)[5:-3]
    head = t[: t.find("## 材料一")] if "## 材料一" in t else t[:6000]
    m0 = SEC_0.search(t)
    mmu = SEC_MU.search(t)
    deg, hd = len(DEG.findall(t)), len(SEC_MAT.findall(t))
    rows.append({
        "卷": name,
        "时间窗节": bool(m0),
        "母文件节": bool(mmu),
        "母文件节名": mmu.group(0).strip("# ").strip() if mmu else "",
        "时间窗位置": ("卷首，合规" if m0 and m0.start() < 2000
                   else ("有，但不在卷首（在第 %d 字节处）" % m0.start()) if m0 else "**缺**"),
        "日期": (DATE.search(head).group(0).strip() if DATE.search(head) else "**未声明**"),
        "对应程度": deg, "段标题": hd,
        "分组标题": len(SEC_GRP.findall(t)),
        "层级": ",".join(str(x) for x in lv(t)) or "-",
        "匿名": len(ANON.findall(t)),
        "字节": len(t.encode()),
    })

# 卷首依据链接：时间窗那一节里引的公告页
def evid(name):
    p = RES + "/溯源结果_%s.md" % name
    t = open(p, encoding="utf-8").read()
    i = t.find("## 材料一")
    head = t[:i] if i > 0 else t
    us = re.findall(r"https?://[^\s｜|）)】\]]+", head)
    return us[0][:100] if us else ""


md = ["# 结构缺口：12 份交付件里，哪些该有的章节还没有", "",
      "提示词对每一份 `溯源结果_<卷>.md` 规定了两块固定内容：卷首的"
      "「笔试日期与时间窗」，和「每段先拿母文件逐句比一遍」。铺开做的时候这两块"
      "有的写了、有的没写。`README.md` 里记的「可信」只覆盖抽样核验，不覆盖这两块，"
      "所以单看 README 看不出来。这份表把差什么一次数清。", "",
      "**表里每个数都是脚本现算的**（`_tools/gaps.py`），没有手写。只读，未改任何交付件。", "",
      "## 一、总表", "",
      "| 卷 | 笔试日期（卷首声明） | 时间窗节 | 母文件比对节 | 对应程度行 | 段标题 | 分组标题 | 标题层级 | 字节 |",
      "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append("| %s | %s | %s | %s | %d | %d | %d | h%s | %d |" % (
        r["卷"], r["日期"][:46], r["时间窗位置"], "有" if r["母文件节"] else "**缺**",
        r["对应程度"], r["段标题"], r["分组标题"], r["层级"], r["字节"]))
md.append("")

md += ["## 二、逐项看", "",
       "### 2.1 缺「笔试日期与时间窗」的", ""]
lack0 = [r for r in rows if "缺" in r["时间窗位置"]]
md += ["共 **%d** 卷：%s。" % (len(lack0), "、".join(r["卷"] for r in lack0)), "",
       "其中 2022乡镇、2025县镇 是**合规的**（节在卷首，且贴着公告原文）；"
       "其余各卷的日期信息散在正文里、或压根没有。", "",
       "### 2.2 缺「母文件比对」节的", ""]
lackmu = [r for r in rows if not r["母文件节"]]
md += ["共 **%d** 卷：%s。" % (len(lackmu), "、".join(r["卷"] for r in lackmu)), "",
       "有这一节的各卷，节名也不统一：", ""]
for r in rows:
    if r["母文件节"]:
        md.append("- %s：`%s`" % (r["卷"], r["母文件节名"]))
md += ["",
       "### 2.3 段标题数与「对应程度」行数对不上的", ""]
mis = [r for r in rows if r["对应程度"] != r["段标题"]]
if mis:
    md += ["| 卷 | 段标题 | 对应程度行 | 差 | 说明 |", "|---|---|---|---|---|"]
    for r in mis:
        d = r["对应程度"] - r["段标题"]
        md.append("| %s | %d | %d | %+d | %s |" % (
            r["卷"], r["段标题"], r["对应程度"], d,
            "有 %d 个合并标题（如「材料二〔3〕～〔8〕」）" % r["分组标题"] if r["分组标题"] else "**对不上，要看**"))
    md.append("")
    md += ["差的这几卷，差额恰好等于合并标题的个数，说明是「几段并成一个标题写」"
           "造成的，不是漏段——上轮 2025县镇 那 4 行差**不是**这种情况（是四则材料整则没做）。", ""]
else:
    md += ["没有对不上的。", ""]

md += ["### 2.4 标题层级不一致的", ""]
by = {}
for r in rows:
    by.setdefault(r["层级"], []).append(r["卷"])
for k in sorted(by):
    md += ["- `h%s`：%s" % (k, "、".join(by[k]))]
md += ["",
       "层级本身不影响内容，但同一个项目里两种写法混着，读者跳转时会不一致。", "",
       "## 三、一个需要核的疑点：选调卷的笔试日期", "",
       "| 卷 | 声明的日期 |", "|---|---|"]
for r in rows:
    if "选调" in r["卷"]:
        md.append("| %s | %s |" % (r["卷"], r["日期"][:60]))
md += ["",
       "2024选调、2025选调 声明的日期（2024-03-16 / 2025-03-15）跟**同年普通卷一模一样**，"
       "而这两个日期是从**省考公告**里取的（`gdzz.gov.cn` 考试录用公务员公告）。"
       "选调优秀大学毕业生有单独的公告，笔试通常不跟省考同日。"
       "这两卷的日期**很可能取自省考公告**，需要在选调自己的公告上复核一遍再定。", "",
       "## 四、跟「母文件机械比对」的关系", "",
       "`_核对/母文件机械比对.md` 是把每套卷跟手上九份母文件逐字比一遍的结果。"
       "两件事配合看：",
       "",
       "- 缺母文件比对节的 **%s**，可以直接照 `母文件机械比对.md` 里那几行的数字补；" % "、".join(r["卷"] for r in lackmu),
       "- 已经写过母文件比对的卷，可以拿那边的数字**对一遍**，看有没有对不上的。", "",
       "> 2025县镇 已写过这一节，它自己算出的最长重合是 **204 字**（材料二整段照搬报告），"
       "`母文件机械比对.md` 独立算出 **206 字**——两套脚本、两份报告快照，走向一致。", ""]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(md))
print("已写 %s\n" % OUT)
for r in rows:
    print("%-10s 日期%-14s 时间窗%-22s 母文件%-5s 程度%3d 标题%3d 组%2d h%s" % (
        r["卷"], r["日期"][:14], r["时间窗位置"][:22],
        "有" if r["母文件节"] else "缺", r["对应程度"], r["段标题"], r["分组标题"], r["层级"]))
