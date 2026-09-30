"""把源稿里的〔相对路径｜日期〕换成读者看的短出处：python3 13_押题缓存/tools/clean_cite.py [--strip] <源稿.md> <输出.md>

--strip：出处整个去掉，覆盖标记（HTML 注释）也去掉，出纯阅读版。

源稿先用 check_quotes.py 核过原句，再用本脚本出阅读版。规则按"路径里含什么"匹配，匹配不上的保留原样并报出来。
"""
import re
import sys

RULES = [
    (r'政治局第十一次集体学习', lambda d: '2024-01-31 中央政治局集体学习讲话'),
    (r'母文件_求是文章', lambda d: '《求是》2025 年第 22 期所收 %s 讲话' % d),
    (r'母文件_2027\.md', lambda d: {'2025-11-08': '2025-11 总书记视察广东通稿', '2025-11-27': '省委十三届七次全会'}.get(d, '省级母文件 %s' % d)),
    (r'政府工作报告_(\d{4})', None),
    (r'母文件_十五五规划纲要', lambda d: '国家"十五五"规划纲要'),
]


def label(path, date):
    for pat, f in RULES:
        m = re.search(pat, path)
        if m:
            if f is None:
                return '%s 年广东省政府工作报告' % m.group(1)
            return f(date)
    return None


def main(src, dst, strip=False):
    t = open(src, encoding='utf-8').read()
    miss = []
    if strip:
        t = re.sub(r'\s*<!--.*?-->', '', t, flags=re.S)
        t = re.sub(r'〔[^｜〕]+｜[^〕]*〕', '', t)
        open(dst, 'w', encoding='utf-8').write(t)
        print('纯阅读版完成')
        return

    def rep(m):
        lab = label(m.group(1), m.group(2).strip())
        if lab is None:
            miss.append(m.group(1))
            return m.group(0)
        return '〔%s〕' % lab
    out = re.sub(r'〔([^｜〕]+)｜([^〕]*)〕', rep, t)
    open(dst, 'w', encoding='utf-8').write(out)
    print('转换完成；没匹配上的出处 %d 个' % len(miss), sorted(set(miss)))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--strip':
        main(a[1], a[2], strip=True)
    else:
        main(a[0], a[1])
