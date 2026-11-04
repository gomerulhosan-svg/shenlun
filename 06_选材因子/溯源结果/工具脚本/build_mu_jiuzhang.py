#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 母文件_制造业九章.md。

《南方日报》「广东'制造业当家'深调研·制造业九章」系列（2022-12-12 ~ 2023-01-05），
九个角度：方位、集群、企业、创新、区域、供应链、政府、人才、未来。

九章正文一律从 `_cache_九章/` 的页面快照里由脚本拷贝，不经过人手转写。
每一章的 URL 都是 `jiuzhang_verify.py` 逐句比对核到 1.00 分的那个（见该脚本输出），
不是照标题猜的。

用法：python3 build_mu_jiuzhang.py
"""
import os, re

RES = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果"
CACHE = os.path.join(RES, "_cache_九章")
OUT = os.path.join(RES, "母文件_制造业九章.md")

# 每章：快照文件、正文起止标记、正身信息
# start_after 用来跳过页面顶部导航里重复出现的标题。
CHAPTERS = [
    dict(
        no="第一章", name="方位",
        title="由“起家”到“当家” 广东制造业加速跃升",
        date="2022-12-12", media="南方日报",
        byline="记者 昌道励 王彪 袁佩如",
        url="https://www.cnbayarea.org.cn/homepage/news/content/post_1032754.html",
        mirror="粤港澳大湾区门户网转载（南方日报）",
        snap="候选__homepage_news_content_post_1032754_html.txt",
        start="开栏的话：制造业是国民经济的主体",
        start_after="来源：南方日报",
        end="扫一扫，分享到微信朋友圈",
    ),
    dict(
        no="第二章", name="集群",
        title="产业集群如何架起广东制造业的“四梁八柱”？",
        date="2022-12-16", media="南方日报",
        byline="南方日报记者 彭琳 张子俊 许宁宁 李赫",
        url="https://static.nfapp.southcn.com/content/202212/15/c7179183.html",
        mirror="南方+（正身页）；人民网广东同日转载作《广东制造业产业集群乘势而上》"
               " http://gd.people.com.cn/n2/2022/1216/c123932-40233524.html",
        snap="候选_thcn_com_content_202212_15_c7179183_html.txt",
        start="▍制造业九章·第二章 集群",
        start_after="▍制造业九章·第二章 集群",
        end="编辑 甘韵矶 陈梅玉",
    ),
    dict(
        no="第三章", name="企业",
        title="“顶天立地”的企业生态，如何炼就广东制造业的真金本色？",
        date="2022-12-21", media="南方日报",
        byline="南方日报记者 叶洁纯 袁佩如 许宁宁",
        url="http://gd.people.com.cn/n2/2022/1221/c123932-40238688.html",
        mirror="人民网广东转载（南方日报）；同日《南方日报》纸版作《广东制造业企业炼就真金本色》",
        snap="候选_om_cn_n2_2022_1221_c123932_40238688_html.txt",
        start="广州番禺汽车城，这里的工厂之间没有",
        start_after="2022年12月21日09:20",
        end="(责编：朴馨语、初梓瑞)",
    ),
    dict(
        no="第四章", name="创新",
        title="强化创新驱动，广东制造业如何挺起科技“脊梁”？",
        date="2022-12-23", media="南方日报",
        byline="（页面未署记者；广工大转载页亦未署）",
        url="https://static.nfnews.com/content/202212/23/c7200593.html",
        mirror="南方+（正身页）；广东工业大学官网转载页写明「来源：南方+2022年12月23日」"
               " https://www.gdut.edu.cn/info/2045/17469.htm",
        snap="候选_news_com_content_202212_23_c7200593_html.txt",
        start="▍制造业九章·第四章 创新",
        start_after="▍制造业九章·第四章 创新",
        end="编辑 冯颖妍 陈梅玉",
    ),
    dict(
        no="第五章", name="区域",
        title="珠三角与粤东粤西粤北由区域共建到携手升级 广东制造业“并线”竞跑",
        date="2022-12-27", media="南方日报",
        byline="记者 苏力 黄叙浩",
        url="https://www.cnbayarea.org.cn/news/focus/content/post_1034590.html",
        mirror="粤港澳大湾区门户网转载（南方日报）",
        snap="候选__cn_news_focus_content_post_1034590_html.txt",
        start="■广东“制造业当家”深调研·制造业九章",
        start_after="来源：南方日报",
        end="扫一扫，分享到微信朋友圈",
    ),
    dict(
        no="第六章", name="供应链",
        title="补链、延链、固链、强链，广东制造业如何增强韧性？",
        date="2022-12-28", media="南方日报",
        byline="【主笔】吴欣宁 许宁宁",
        url="https://static.nfapp.southcn.com/content/202212/27/c7212200.html",
        mirror="南方+（正身页，URL 路径为 12-27，纸版刊期为 12-28）；"
               "大湾区门户网同日转载作《促进产业链“补链、延链、固链、强链” 广东制造业筑起强大防波堤》"
               " https://www.cnbayarea.org.cn/homepage/news/content/post_1034719.html",
        snap="候选_thcn_com_content_202212_27_c7212200_html.txt",
        start="▍制造业九章·第六章 供应链",
        start_after="▍制造业九章·第六章 供应链",
        end="编辑 张会玲 张志超",
    ),
    dict(
        no="第七章", name="政府",
        title="“有为政府”精准发力，广东如何构建制造业一流“大环境”",
        date="2023-01-02", media="南方日报",
        byline="【主笔】陈晓 宾红霞 唐柳雯 刘倩",
        url="https://static.nfapp.southcn.com/content/202301/02/c7227024.html",
        mirror="南方+（正身页）；页面标注「南方日报2023年1月2日A03版」",
        snap="候选_thcn_com_content_202301_02_c7227024_html.txt",
        start="▍制造业九章·第七章·政府",
        start_after="▍制造业九章·第七章·政府",
        end="编辑 童慧 甘韵矶",
    ),
    dict(
        no="第八章", name="人才",
        title="聚天下英才，广东如何锻造制造业当家“主心骨”？",
        date="2023-01-04", media="南方日报",
        byline="●南方日报记者 肖文舸 曾美玲 唐亚冰",
        url="https://news.southcn.com/node_54a44f01a2/0742577d49.shtml",
        mirror="南方网转载（南方日报）；纸版标题作《广东锻造制造业当家“主心骨”》",
        snap="候选_hcn_com_node_54a44f01a2_0742577d49_shtml.txt",
        start="■广东“制造业当家”深调研·制造业九章",
        start_after="来源：南方日报",
        end="返回南方网首页",
    ),
    dict(
        no="第九章", name="未来",
        title="春山在望 未来可期——广东坚持制造业当家迈出新步伐",
        date="2023-01-05", media="南方日报",
        byline="记者 袁佩如 丁建庭 苏力",
        url="https://www.cnbayarea.org.cn/homepage/news/content/post_1035431.html",
        mirror="粤港澳大湾区门户网转载（南方日报）；南方+正身页"
               " https://static.nfapp.southcn.com/content/202301/05/c7235191.html"
               "（本会话另核，逐句比对 0.93）",
        snap="候选__homepage_news_content_post_1035431_html.txt",
        start="新年的阳光，照耀气象万千的南粤大地；",
        start_after="2023年01月05日",
        end="扫一扫，分享到微信朋友圈",
    ),
]

INDEX = dict(
    title="广东如何“制造业当家”？南方日报制造业九章全面解读",
    date="2023-01-05", media="南方+",
    url="https://static.nfapp.southcn.com/content/202301/05/c7235648.html",
    snap="制造业九章_系列解读_南方plus20230105.txt",
    cachedir="_cache_2023县级",
    start="制造业是国民经济的主体，是立国之本、强国之基。",
    start_after="记者",
    end="您已点过",
)


def body(path, start, end, start_after=None):
    """从快照里取正文：从 start 起、到 end 止。start_after 用来跳过顶部导航的重复标题。"""
    t = open(path, encoding="utf-8", errors="ignore").read()
    base = 0
    if start_after:
        k = t.find(start_after)
        if k < 0:
            raise SystemExit("找不到跳过标记 %r @ %s" % (start_after, path))
        base = k
    i = t.find(start, base)
    if i < 0:
        raise SystemExit("找不到起点 %r @ %s" % (start, path))
    j = t.find(end, i)
    if j < 0:
        raise SystemExit("找不到终点 %r @ %s" % (end, path))
    lines = [L.strip() for L in t[i:j].split("\n")]
    return "\n".join(L for L in lines if L)


def quoted(text):
    return "\n".join("> " + L if L else ">" for L in text.split("\n"))


def main():
    parts = []
    parts.append("""# 母文件_制造业九章

> 《南方日报》「广东‘制造业当家’深调研·制造业九章」系列报道（2022-12-12 ~ 2023-01-05）全文。
> 这是该系列**第一次被整份立档**：在此之前，九章只有零散八篇躺在
> `_cache_2023县级/` 里当 2023 县级卷的段级来源用，**没有一份能按章点开的清单**；
> **第九章全项目都没抓到过**，第八章虽认对了章次，却记成「无明确日期」、也没有正身 URL。
>
> 本文件补的正是这一块：
>
> 1. **九章九条正身 URL 全部核过**——不是照标题猜的。`_tools/jiuzhang_verify.py`
>    把候选 URL 逐个抓回，跟章快照逐句比对，取「章快照里的长句有多少句能在该页面逐字找到」
>    当分，**1.00 才算正身**。九章全部核到 1.00。
> 2. **第八章核实为正身**：快照第 237 行有 `■广东“制造业当家”深调研·制造业九章` 栏头，
>    刊发日 **2023-01-04**，来源南方日报——**它不是替代品，就是第八章本身**
>    （此前会话 2 认对了章次，但只记了文件名，没记日期与 URL）。
>    **第九章本次新抓补入**（2023-01-05）——这一篇此前全项目没有。
> 3. 正文**一律由脚本从页面快照拷贝**（`_tools/build_mu_jiuzhang.py`），
>    没有经过人手转写。图片说明、栏头、版权块、调研团队名单**一并保留原样**，
>    一个字未删——这是本项目对「逐字」的约定。
>
> 为什么九章值得单独立一份母文件：2023 年广东省考申论（笔试 2023-02-25）的材料二、
> 材料五绝大多数段落都落在这条线上。会话 2 的原话是「本轮最大收获：《制造业九章》
> 全系列打通」——上一轮把这两则整则判「未找到」，根因就是没定位到「系列报道」这个载体。

---

## 0 系列概况与时间窗

- **系列名**：广东“制造业当家”深调研·**制造业九章**
- **刊发单位**：《南方日报》（南方+、南方网同步）
- **起止**：2022 年 12 月 12 日（第一章）— 2023 年 1 月 5 日（第九章）
- **九个角度**：方位、集群、企业、创新、区域、供应链、政府、人才、未来
- **性质**：《南方日报》推出的**首个系列报道**
- **与 2023 年广东省考申论的关系**：笔试日 2023-02-25，九章全部刊发于笔试前
  2 个半月内，**整条系列都落在取材时间窗内**

### 0.1 九章一览（标题｜刊发日｜记者）

| 章 | 角度 | 标题 | 刊发日 | 署名 |
|---|---|---|---|---|""")
    for c in CHAPTERS:
        parts.append("| %s | %s | 《%s》 | %s | %s |" % (
            c["no"], c["name"], c["title"], c["date"], c["byline"]))

    parts.append("""
### 0.2 九章共用的版权块

第七章页末所载，九章共用：

> 【总策划】郑广宁
> 【总统筹】王更辉 王义军 郎国华
> 【执行】王溪勇 林焕辉 袁佩如
> 【调研团队】彭琳 昌道励 苏力 吴少敏 丁建庭 王彪 肖文舸 叶洁纯 吴欣宁 陈晓 王良珏 陈颖 刘倩 唐柳雯 宾红霞 李赫 黄叙浩 张子俊 曾美玲 许宁宁 唐亚冰 卞德龙 马立敏

（各章另有自己的【主笔】，见各章正文末尾。）

### 0.3 同一批记者的姊妹系列（不是九章，别混）

本轮核 URL 时撞出来的：南方日报另有一组**《制造业当家 金融有作为》**系列
（南方日报联合广东银保监局推出），刊期与九章重叠，但**不属于九章**：

| 篇 | 标题 | 快照 |
|---|---|---|
| ③ | 《中长期贷款如何夯实制造业家底？》 | `_cache_九章/候选_news_com_content_202212_15_c7175949_html.txt` |
| — | 《金融如何支持制造业？南方日报联合广东银保监局推出系列深调研》 | `_cache_九章/候选_thcn_com_content_202212_28_c7214975_html.txt` |

这两篇**不要当成九章的章次**——它们各自独立成篇。

---

## 1 九章全文

""")

    for c in CHAPTERS:
        p = os.path.join(CACHE, c["snap"])
        txt = body(p, c["start"], c["end"], c.get("start_after"))
        n = len(re.sub(r"\s", "", txt))
        parts.append("### %s %s｜《%s》\n" % (c["no"], c["name"], c["title"]))
        parts.append("- 刊发日：%s" % c["date"])
        parts.append("- 媒体：%s" % c["media"])
        parts.append("- 署名：%s" % c["byline"])
        parts.append("- 链接：%s" % c["url"])
        parts.append("- 转载情况：%s" % c["mirror"])
        parts.append("- 界面快照：`%s`" % ("_cache_九章/" + c["snap"]))
        parts.append("- 正文（脚本逐字拷贝，%d 字）：\n" % n)
        parts.append(quoted(txt) + "\n")

    # 系列解读
    ip = os.path.join(RES, INDEX["cachedir"], INDEX["snap"])
    itxt = body(ip, INDEX["start"], INDEX["end"], INDEX["start_after"])
    parts.append("""---

## 2 系列解读（九章导语合辑）

这一篇是九章的**收官索引**，本身不是九章中的任何一章，但含金量很高：
它把九章的**导语全文**都留下了（方位、集群、企业、创新、区域、供应链、政府、人才、
未来九段导语一字不缺），还带总策划与调研团队名单。
九章正文若有个别章取不到时，这一篇是可用的退路。

- 标题：《%s》
- 刊发日：%s
- 媒体：%s
- 链接：%s
- 界面快照：`%s/%s`
- 正文（脚本逐字拷贝）：

""" % (INDEX["title"], INDEX["date"], INDEX["media"], INDEX["url"],
       INDEX["cachedir"], INDEX["snap"]))
    parts.append(quoted(itxt) + "\n")

    parts.append("""---

## 3 核验记录

### 3.1 URL ↔ 章 的逐句比对（`_tools/jiuzhang_verify.py`）

做法：把候选 URL 逐个抓回，与每一份章快照逐句比对，取
「章快照里的长句有多少句能在该页面逐字找到」当分。**声明章 == 实测章，且 ≥0.55 才算核到**。

| 章 | 得分 | 裁定 | URL |
|---|---|---|---|
| 一·方位 | 1.00 (40/40) | 正身 | `post_1032754`（大湾区门户网） |
| 二·集群 | 1.00 (40/40) | 正身 | `c7179183`（南方+） |
| 三·企业 | 1.00 (40/40) | 正身 | `40238688`（人民网广东） |
| 四·创新 | 1.00 (40/40) | 正身 | `c7200593`（南方+） |
| 五·区域 | 1.00 (40/40) | 正身 | `post_1034590`（大湾区门户网） |
| 六·供应链 | 1.00 (40/40) | 正身 | `c7212200`（南方+） |
| 七·政府 | 1.00 (40/40) | 正身 | `c7227024`（南方+） |
| 八·人才 | 1.00 (40/40) | 正身 | `0742577d49`（南方网） |
| 九·未来 | 1.00 (40/40) | 正身 | `post_1035431`（大湾区门户网） |

### 3.2 脚本纠出来的两处错位（记下来，免得下轮再踩）

1. **`c7212200` 被当成第五章，实测是第六章。** 我按 URL 日期 12-27 预判它是
   「第五章 区域」（第五章刊于 12-27），逐句比对面，它跟**第六章 供应链**快照
   满 1.00——它与 `_cache_2023县级/制造业九章06_供应链_南方plus20221228.txt`
   字节数完全相同（18585）。**说明缓存文件名里的日期（20221228）是纸版刊期，
   URL 路径里的日期（12-27）是网络发布时间，两者不是一回事。**
   凡「文件名日期 ≠ URL 路径日期」的，必须以页面上写的为准。
2. **`c7214975`、`c7175949` 根本不是九章**，是姊妹系列《制造业当家 金融有作为》
   （见 §0.3）。它们对九章九份快照的得分全是 0.00。

### 3.3 仍未核到的

- **第四章的记者署名**：南方+ 正身页与广工大转载页**都没有署记者**，
  只署了摄影记者。搜索概述称「吴少敏、卞德龙 等」，但那是二手概述，
  **按本项目规矩不采信为署名**，故正文件写「页面未署记者」。
  若要补，需查《南方日报》2022-12-23 纸版版面。
- **第九章的独立正身**：大湾区门户网那页已核 1.00，可直接用；
  南方+ 正身页 `c7235191` 也核到 0.93（差异来自页面壳里的重复行），列在转载情况里备查。
""")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("SAVED %s  (%d 字节)" % (OUT, os.path.getsize(OUT)))
    for c in CHAPTERS:
        p = os.path.join(CACHE, c["snap"])
        t = body(p, c["start"], c["end"], c.get("start_after"))
        print("  %s %s: %d 字" % (c["no"], c["name"], len(re.sub(r"\s", "", t))))


if __name__ == "__main__":
    main()
