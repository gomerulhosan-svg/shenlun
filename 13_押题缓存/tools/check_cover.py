"""检查讲解稿是不是覆盖了一条线的全部条目：python3 13_押题缓存/tools/check_cover.py <动作卡.md> <讲解源稿.md>

编号集合取自动作卡（H、Q、L 编号）。讲解源稿里用 HTML 注释标覆盖：<!-- 覆盖: H01 H05 Q03 L02 -->。
报出没被任何注释标到的编号；全覆盖退出码 0，否则 1。
"""
import re
import sys


def main(card, src):
    ids = set(re.findall(r'\b([HQL]\d{2})\b', open(card, encoding='utf-8').read()))
    t = open(src, encoding='utf-8').read()
    got = set()
    for m in re.finditer(r'<!--\s*覆盖[:：]([^>]*)-->', t):
        got |= set(re.findall(r'\b([HQL]\d{2})\b', m.group(1)))
    miss = sorted(ids - got, key=lambda x: (x[0], x))
    extra = sorted(got - ids)
    print('%s：应覆盖 %d 个，已覆盖 %d 个，漏 %d 个' % (src, len(ids), len(ids & got), len(miss)))
    if miss:
        print('  漏：' + ' '.join(miss))
    if extra:
        print('  标了动作卡里没有的编号：' + ' '.join(extra))
    return 1 if miss else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
