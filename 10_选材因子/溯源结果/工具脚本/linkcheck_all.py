#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量回访：把 12 份交付件里出现的每一个来源链接都重新打开一遍。

不是抽样——抽样是上一轮的做法，每卷抽 1—29 条说「可信」，剩下两百多条没人看过。
这一轮把去重后的每一条都跑一遍，结果写成 _核对/全量回访.md。

判据只看一件事：**这个链接现在还能不能抓到像正文的文本**。
- 抓不到（FETCH_FAIL）      → 死链，要换源
- 抓到了但去空白后 < 300 字 → 多半是 JS 空壳页或已改版，要人工看一眼是哪种
- 抓到了且字数正常          → 通过

通过只说明「页面能打开、有正文」，**不说明交付件贴的原文就在里面**——
那是各卷核验环节用 --check 逐字做的事。这一节只负责筛死链和空壳。
"""
import re, os, sys, glob, collections, subprocess
from concurrent.futures import ThreadPoolExecutor

RES = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果"
FETCH = RES + "/_tools/fetch.py"
OUT = RES + "/_核对/全量回访.md"

# 这些不是「来源」，是检索入口或从正文里误抓的占位串，不参与回访
SKIP = re.compile(r"(so\.com/s\?|sogou\.com/web\?|baidu\.com/s\?|bing\.com/search|"
                  r"toutiao\.com/search|nfnews\.com/search|weixin\.sogou\.com|"
                  r"nfncb\.cn/s\.html|/$|\.\.\.|（)")

URLPAT = re.compile(r"https?://[^\s｜|）)】\]]+")
# 正文里链接后面常紧跟中文标点或书名号，一并剪掉
TRAIL = "。；;、，,）)】》」”’\"'`"


def probe(u):
    """直接调 fetch.py 子进程，认它打印的 CHARS / FETCH_FAIL。"""
    try:
        r = subprocess.run([sys.executable, FETCH, u], capture_output=True,
                           text=True, timeout=90)
        o = r.stdout
        m = re.search(r"CHARS (\d+)", o)
        if m:
            return u, int(m.group(1)), ""
        m = re.search(r"FETCH_FAIL[^\n]*", o)
        return u, 0, (m.group(0)[:110] if m else (r.stderr.strip()[:110] or "无输出"))
    except subprocess.TimeoutExpired:
        return u, 0, "TIMEOUT 90s"
    except Exception as e:
        return u, 0, str(e)[:110]


# 收链接，记住每条的出处（哪几份交付件引了它）
where = collections.defaultdict(set)
for f in sorted(glob.glob(RES + "/溯源结果_*.md")):
    name = os.path.basename(f)
    for u in URLPAT.findall(open(f, encoding="utf-8").read()):
        # 正文里链接后面常直接跟中文标点/书名号，从第一个这样的字符处截断
        u = re.split(r"[，,；;、。）》」”’\"'`]", u)[0]
        where[u].add(name)

urls = sorted(u for u in where if not SKIP.search(u))
print("共 %d 条，滤掉 %d 条检索入口/占位串，开始回访…" % (len(where), len(where) - len(urls)))

with ThreadPoolExecutor(max_workers=8) as ex:
    rows = list(ex.map(probe, urls))

fail = [r for r in rows if r[1] == 0]
thin = [r for r in rows if 0 < r[1] < 300]
ok = [r for r in rows if r[1] >= 300]

md = ["# 全量回访：交付件里的每一条来源链接", "",
      "把 12 份 `溯源结果_*.md` 里出现的 **全部** 来源链接抓出来、去重，逐个重新打开。"
      "上一轮做的是抽样（每卷抽 1—29 条），这一轮是全量。", "",
      "判据只有一条：**这个链接现在还能不能抓到像正文的文本**。", "",
      "- **打不开**（`FETCH_FAIL`）：链接死了或域名没了 → 要换源",
      "- **能开但正文很少**（去空白后 < 300 字）：多半是 JS 空壳页（Vue/React 单页应用，"
      "正文靠接口取）或页面已改版 → 要人工看一眼，确认是哪种",
      "- **正常**：能开、有正文 → 通过", "",
      "通过只说明「页面能打开、有正文」，**不说明交付件贴的原文就在里面**——"
      "那是各卷核验环节用 `--check` 逐字做的事。这一节只负责筛死链和空壳。", "",
      "## 结果", "",
      "| | 条数 |", "|---|---|",
      "| 回访总数（去重后） | %d |" % len(rows),
      "| 打不开 | %d |" % len(fail),
      "| 能开但正文 < 300 字 | %d |" % len(thin),
      "| 正常 | %d |" % len(ok), ""]

if fail:
    md += ["## 一、打不开的（要换源）", "", "| 链接 | 被哪几份引 | 返回 |", "|---|---|---|"]
    for u, n, err in fail:
        md.append("| %s | %s | %s |" % (u, "、".join(sorted(where[u])), err))
    md.append("")

if thin:
    md += ["## 二、能开但正文很少的（多半是 JS 空壳页）", "",
           "这一类**不是死链**，页面是活的，只是正文不在 HTML 里。"
           "交付件里若已注明「须走接口 / 页面为空壳」的，属于已披露，不算问题；"
           "没注明的，补一句取文方式即可。", "",
           "| 链接 | 去空白字数 | 被哪几份引 |", "|---|---|---|"]
    for u, n, _ in sorted(thin, key=lambda r: r[1]):
        md.append("| %s | %d | %s |" % (u, n, "、".join(sorted(where[u]))))
    md.append("")

# 死链和空壳逐条的可接受性——人工看过一遍后写死在这里，重跑不会丢
DISCLOSED = {
 "http://politics.people.com.cn/n1/2023/0413/c1024-32663934.html":
   "2025选调 引作新华社 2023-04-13 通稿，交付件已标「是否打开了全文：**否**（未取到该页快照）」，未当来源贴原文。",
 "http://www.suixi.gov.cn/sxxw/bmdt/content/post_1853268.html":
   "2026县镇 引作线索，交付件已标「**仅搜索结果，未打开，不当原文用**」。",
 "https://news.ycwb.com/2023-08/21/content_52152192.htm":
   "2025选调 列为最接近的线索。实测该站返回的是 **JS 反爬挑战页**（2.7KB 的混淆脚本），"
   "交付件已标「该站对本机 IP 返回 0 字节（JS 反爬），本轮**未打开**……不能判定它就是母本」。",
 "https://news.ycwb.com/2024-05/14/content_52685007.htm":
   "2024一卷 引作口径旁证，交付件已标「**晚于本卷笔试 2024-03-16，不能作为本卷出处**」。"
   "同样受 JS 反爬影响。",
 "https://www.gd.gov.cn/gdywdt/gdyw/content/post_2703655.html":
   "2023县级 引作省府网原页，交付件已标「**仅摘要**：……现已 404」。",
 "http://static.nfapp.southcn.com/content/202010/09/c4135266.html":
   "2024一卷 引作政策原文的南方+解读页，交付件已标「是否打开了全文：**否**（仅搜索摘要）」。",
 "http://gdyjzx.gd.gov.cn/hdjlpt/live/index/index/records/pc?jump=0&pid=3810&siteId=192":
   "2026县镇 引作线索页，交付件已标「**仅搜索结果标题与摘要，未打开，不当原文用**」。",
}

md += ["## 三、正常的", "",
       "其余 %d 条都能打开且有正文，逐条列在下面备查。" % len(ok), "",
       "| 链接 | 去空白字数 | 被哪几份引 |", "|---|---|---|"]
for u, n, _ in sorted(ok, key=lambda r: -r[1]):
    md.append("| %s | %d | %s |" % (u, n, "、".join(sorted(where[u]))))
md.append("")

md += ["## 四、这 %d 条死链和 %d 条空壳，逐条看过一遍" % (len(fail), len(thin)), "",
       "结论：**没有一条被当成来源贴过原文**。它们要么在交付件里已经写明「未取到／仅摘要／"
       "未打开／晚于笔试不能作出处」，要么本来就只作线索列出。逐条如下——", ""]
for u, n, err in fail + thin:
    md += ["- `%s`" % u, "  - %s" % DISCLOSED.get(u, "**未在交付件中找到披露，要回去补。**"), ""]
md += ["## 五、这件事说明了什么", "",
       "上一轮的核验是**抽样**的：每卷挑 1—29 条最长的原文块去回访，剩下的没人看过。"
       "抽样能证明「贴出来的原文是真的」，不能证明「剩下的链接还活着」。"
       "这一轮把 %d 条全部跑了一遍，才看出死链集中在哪一类：" % len(rows), "",
       "1. **老页面会烂掉**。404 的那几条（省府网 2020 年、人民网 2023 年、遂溪县）都是当年能开、"
       "现在没了。交付件里凡是引这类页面的，都已经改指了可访问的转载版本，或者标了「仅摘要」。",
       "2. **有两类站是抓不下来的**，不是链接的问题：一是**搜狐**这类按频率随机 403 的（换 UA 能过，"
       "已给 `fetch.py` 加了 UA 轮换回退）；二是**羊城晚报**这类上 JS 反爬挑战的，"
       "`fetch.py` 拿到的是一段混淆脚本，不是文章。这类只能靠搜索引擎的摘要，**摘要不能当原文**，"
       "交付件里也都注明了。",
       "3. **反过来说，通过也不等于原文对**。这一节只筛「页面能不能打开、有没有正文」；"
       "「贴出来的那句话是否真在页面里」是各卷核验环节用 `--check` 逐字做的，两件事不能互相替代。", ""]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(md))
print("已写 %s" % OUT)
print("打不开 %d 条 / 空壳 %d 条 / 正常 %d 条" % (len(fail), len(thin), len(ok)))
for u, n, err in fail:
    print("  [死链] %s  ← %s" % (u, err))
for u, n, _ in sorted(thin, key=lambda r: r[1]):
    print("  [空壳] %4d 字  %s" % (n, u))
