#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量跑特征词检索（360 搜索），把结果落到 _cache_2022乡镇/检索_XX.txt。
用法: python3 batch_2022xz.py
"""
import sys, os, time, re, urllib.parse
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import fetch as F

OUT = "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_cache_2022乡镇"

QUERIES = [
    ("q01_轻骑兵宣讲", "田间地头 榕树 讲党史故事 好人好事 宣讲队"),
    ("q02_文明实践所活动", "文明实践所 反诈宣传 科普展览 道路安全宣传 农业技术咨询 卫生健康宣传"),
    ("q03_龙眼品种改良", "龙眼 品种改良 试点 肉厚 核小 广州 深圳 超市"),
    ("q04_百香果深加工", "百香果 深加工 饮料 糕点 精油 洗洁精 产品"),
    ("q05_幼果期落果", "龙眼 幼果期 落果 技术员 指导 处理"),
    ("q06_网格化管理村", "村 网格化管理 电子监控系统 网格员 走访 解决实际困难"),
    ("q07_复耕复种清表", "撂荒耕地 复耕复种 挖掘机 清表 杂草 林木 隔壁镇 协调"),
    ("q08_大棚膜寒潮", "百香果 大棚膜 寒潮 受灾 农业保险 查勘定损"),
    ("q09_垃圾分类小菜园", "村 小菜园 小果园 小花园 房屋外墙 彩绘 山水田园画"),
    ("q10_龙眼直播", "返乡青年 直播带货 龙眼干 龙眼蜜 土炉 手工烘"),
    ("q11_无人机百香果", "百香果 试验园 无人机 人工智能 系统 浇水 施肥 全过程监控"),
    ("q12_小林村", "广东 十大美丽乡村 小林村 沙坝镇"),
    ("q13_龙眼蜜无公害", "龙眼 不打药 无公害 当天采摘 当天发货 龙眼蜜 纯天然"),
    ("q14_文明实践所剪纸", "文明实践所 剪纸 非遗传承 非遗进校园 小学徒"),
    ("q15_福垌村百香果", "福垌村 百香果 寒潮 受灾"),
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
        print("OK %-22s %d 条" % (name, len(rs)))
        time.sleep(4)


if __name__ == "__main__":
    main()
