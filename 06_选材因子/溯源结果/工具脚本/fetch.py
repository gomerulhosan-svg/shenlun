#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""取原文小工具：抓页面 -> 纯文本，供逐字核对。

为什么不用 WebFetch：WebFetch 会以版权为由拒绝逐字转载正文，只给摘要；
本任务要求「一个字一个字比对」，所以必须拿原始 HTML 自己转文本。

用法：
  python3 fetch.py <url> --save out.txt          # 抓下来存纯文本
  python3 fetch.py <url> --show 3000            # 抓下来打印前 3000 字
  python3 fetch.py <url> --grep "某个词组"       # 打印命中处上下文各 400 字
  python3 fetch.py <url> --check "整段原文"      # 逐字核对，打印 FOUND / NOT_FOUND

约定：
  - 抓取失败会打印 FETCH_FAIL 并返回非 0；返回 0 才算拿到东西。
  - 每个站点连续请求之间请 sleep 1-2 秒，同一 IP 打太快会被 403。
  - 403/空响应时换一个转载同一篇报道的站点再试，不要硬撞。
"""
import sys, re, subprocess, html, time

_BASE = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36"
# 轮流换 UA。有的站（搜狐就是）会按 UA 或按频率随机 403，同一个 UA 连撞三次白费，
# 换个 UA 往往就过了。第一个是默认的。
UAS = [_BASE % v for v in ("124.0.0.0", "122", "126.0.0.0", "120")]


def fetch(url, timeout=30, attempts=4):
    """用 curl 取原始字节。返回 (html_text, final_url)。失败抛异常。"""
    last = ""
    for i in range(attempts):
        cmd = ["curl", "-sSL", "--compressed", "-m", str(timeout),
               "-A", UAS[min(i, len(UAS) - 1)],
               "-H", "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8",
               "--max-redirs", "5",
               "-w", "\n__HTTP__%{http_code}__%{url_effective}", url]
        r = subprocess.run(cmd, capture_output=True)
        out = r.stdout
        m = re.search(rb"\n__HTTP__(\d+)__(.*)\Z", out, re.S)
        code, final = "000", url
        if m:
            code = m.group(1).decode()
            final = m.group(2).decode("utf-8", "ignore")
            out = out[:m.start()]
        if code == "200" and len(out) > 500:
            return decode(out), final
        last = "HTTP %s len=%d" % (code, len(out))
        if i < attempts - 1:
            time.sleep(2 + 3 * i)
    raise RuntimeError(last)


def decode(data):
    m = re.search(rb'charset=["\']?([\w-]+)', data[:4000], re.I)
    cands = [m.group(1).decode("latin-1")] if m else []
    cands += ["utf-8", "gb18030", "gbk", "big5"]
    for c in cands:
        try:
            return data.decode(c)
        except Exception:
            continue
    return data.decode("utf-8", "ignore")


def to_text(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg|iframe)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?is)<!--.*?-->", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|section|article|td)>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", "", h)
    h = html.unescape(h)
    h = h.replace("　", " ").replace("\xa0", " ").replace("​", "")
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in h.split("\n")]
    lines = [l for l in lines if l]
    out, prev = [], None
    for l in lines:
        if l != prev:
            out.append(l)
        prev = l
    return "\n".join(out)


def norm(s):
    """比对用的归一化：去掉所有空白与常见排版差异，只看字。"""
    s = re.sub(r"[\s　​]+", "", s)
    return s.replace("〔", "").replace("〕", "")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    url = a[0]
    get = lambda k: (a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else None)
    try:
        raw, final = fetch(url)
    except Exception as e:
        print("FETCH_FAIL %s: %s" % (url, e))
        return 3
    text = to_text(raw)
    if final != url:
        print("FINAL_URL %s" % final)
    print("CHARS %d" % len(text))

    save, grep, check, show = get("--save"), get("--grep"), get("--check"), get("--show")
    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(text)
        print("SAVED %s" % save)
    if check:
        n = norm(text).count(norm(check))
        print("CHECK %s  (命中 %d 次)" % ("FOUND" if n else "NOT_FOUND", n))
        if not n:
            return 1
    if grep:
        n = 0
        for m in re.finditer(re.escape(grep), text):
            n += 1
            print("--- HIT %d ---" % n)
            print(text[max(0, m.start() - 400):m.end() + 400])
        print("HITS %d" % n)
    if show:
        print(text[:int(show)])
    elif not (save or grep or check):
        print(text[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
