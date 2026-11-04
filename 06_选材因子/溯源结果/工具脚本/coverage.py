#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐段覆盖率：源卷里每一个〔N〕段，交付件里到底做了没有。

为什么不能拿「源卷段数 − 对应程度行数」直接减——交付件里有**合并标题**：
  ### 材料二〔3〕～〔8〕（共 6 段，同一来源）
一个标题、一行「对应程度」，却盖了 6 段。直接减会把已经做完的 5 段算成缺口。
上一轮 2022乡镇 的数字就是这么错的，这次把标题展开成段号再取并集。

判据（保守）：
  已做 = 该段落在某个标题下，该标题下有一行「对应程度」，且这一行/这段正文里
         没有「本轮未完成」「未及」「未做」这类自曝标记。
  缺口 = 源卷里有、交付件里没被任何「已做」标题盖住的段。

只读，不改交付件。
"""
import re, os, glob

B = "/Users/jianguolingyun/公考/07_申论/申论"
RES = B + "/溯源结果"
OUT = RES + "/_核对/逐段覆盖.md"

MAT = "一二三四五六七八九十"
CN = {c: i for i, c in enumerate("零一二三四五六七八九十", 0)}
CN["十"] = 10


def cn2int(s):
    """把「三」「十二」「二十一」这类中文数字转成 int。"""
    if not s:
        return None
    if s == "十":
        return 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN.get(a, 1) if a else 1) * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s)


SEC_MAT = re.compile(r"(?m)^(#{2,4})\s*(材料[" + MAT + r"])(.*)$")
DEG = re.compile(r"(?m)^\s*-\s*对应程度")
SRC_SEG = re.compile(r"〔(\d+)〕")
UNDONE = re.compile(r"本轮未完成|未及|未做|整则未|尚未|待补")


def segs_in(heading_tail):
    """从一个标题的尾部文字里取出它盖住的段号集合。
    〔3〕～〔8〕 / 〔3〕—〔8〕 / 〔3〕〔4〕〔5〕 / 〔3〕 都认。"""
    nums = set()
    # 先处理区间
    for m in re.finditer(r"〔(\d+)〕\s*[～~—\-－]\s*〔(\d+)〕", heading_tail):
        a, b = int(m.group(1)), int(m.group(2))
        if a <= b:
            nums.update(range(a, b + 1))
    # 再把剩下的单个 〔N〕 收进来（已被区间吃掉的重复加一次无妨）
    for m in re.finditer(r"〔(\d+)〕", heading_tail):
        nums.add(int(m.group(1)))
    return nums


def parse_deliverable(path):
    """返回 [(材料名, 标题原文, 段号集合, 已做?)]。"""
    t = open(path, encoding="utf-8").read()
    # 只取正文部分（跳过卷首〇/一节）
    marks = list(SEC_MAT.finditer(t))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(t)
        block = t[m.start():end]
        # 这一块里有没有「对应程度」行、有没有未完成标记
        done = bool(DEG.search(block))
        undone = bool(UNDONE.search(block))
        # 段号：从标题尾部 + 标题下到第一个「对应程度」行之前的引文里都不取，
        # 只认标题本身（引文里出现的〔N〕是引用别人的，不算覆盖声明）
        nums = segs_in(m.group(3))
        out.append((m.group(2), m.group(0).strip(), nums, done and not undone))
    return out


def src_segments(path):
    t = open(path, encoding="utf-8").read()
    mm = re.search(r"(?m)^#+\s*题干", t)
    body = t[:mm.start()] if mm else t
    # 按材料分块
    out = {}
    for m in re.finditer(r"(?m)^#{2,4}\s*(材料[" + MAT + r"])\s*$", body):
        nm = m.group(1)
        nxt = re.search(r"(?m)^#{2,4}\s*材料[" + MAT + r"]\s*$", body[m.end():])
        blk = body[m.end(): m.end() + nxt.start()] if nxt else body[m.end():]
        out[nm] = sorted(int(x) for x in SRC_SEG.findall(blk))
    return out


rows = []
for p in sorted(glob.glob(B + "/溯源包_2022-2026/*_材料与题干.md")):
    name = os.path.basename(p).replace("_材料与题干.md", "")
    f = RES + "/溯源结果_%s.md" % name
    if not os.path.exists(f):
        continue
    src = src_segments(p)
    parsed = parse_deliverable(f)
    covered = {}
    for mat, title, nums, done in parsed:
        covered.setdefault(mat, set())
        if done:
            covered[mat] |= nums
    total = sum(len(v) for v in src.values())
    cov = sum(len(covered.get(k, set()) & set(v)) for k, v in src.items())
    miss = []
    for k, v in src.items():
        for n in v:
            if n not in covered.get(k, set()):
                miss.append("%s〔%d〕" % (k, n))
    # 自曝未做的标题
    selfdec = [t for _, t, _, d in parsed if not d]
    rows.append((name, total, cov, total - cov, miss, selfdec))

md = ["# 逐段覆盖率：源卷每一个〔N〕段，交付件里做了没有", "",
      "**为什么不能拿「源卷段数 − 对应程度行数」直接减**：交付件里有合并标题，"
      "比如 `### 材料二〔3〕～〔8〕（共 6 段，同一来源）`——一个标题、一行「对应程度」，"
      "盖了 6 段。直接减会把已经做完的 5 段算成缺口。这张表把标题展开成段号再取并集。", "",
      "**判据（偏保守）**：一段算「已做」，要满足它落在某个标题下、该标题下有一行"
      "「对应程度」、且这一块里没有「本轮未完成／未及／整则未」这类自曝标记。"
      "宁可把可疑的算成没做，也不虚报完成。", "",
      "| 卷 | 源卷段数 | 已覆盖 | **缺口** | 覆盖率 |", "|---|---|---|---|---|"]
for name, total, cov, gap, miss, sd in rows:
    md.append("| %s | %d | %d | **%d** | %d%% |" % (
        name, total, cov, gap, round(100.0 * cov / total) if total else 0))
T = sum(r[1] for r in rows); C = sum(r[2] for r in rows)
md += ["| **合计** | **%d** | **%d** | **%d** | **%d%%** |" % (T, C, T - C, round(100.0 * C / T)), ""]

md += ["## 逐卷缺口明细", ""]
for name, total, cov, gap, miss, sd in rows:
    md.append("### %s（缺 %d 段）" % (name, gap))
    md.append("")
    if not miss:
        md += ["全部覆盖。", ""]
        continue
    md += ["- 缺的段：%s" % "、".join(miss[:60]), ""]
    if sd:
        md += ["- 交付件里自曝未做的标题："] + ["  - `%s`" % x for x in sd] + [""]
    md.append("")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(md))
print("已写 %s\n" % OUT)
print("%-10s %6s %6s %6s %7s" % ("卷", "源段", "已覆盖", "缺口", "覆盖率"))
for name, total, cov, gap, miss, sd in rows:
    print("%-10s %6d %6d %6d %6d%%" % (name, total, cov, gap, round(100.0 * cov / total) if total else 0))
print("%-10s %6d %6d %6d %6d%%" % ("合计", T, C, T - C, round(100.0 * C / T)))
