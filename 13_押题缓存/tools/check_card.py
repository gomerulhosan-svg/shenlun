"""检查动作卡（训练版）有没有压坏：python3 13_押题缓存/tools/check_card.py <研究版图谱.md> <动作卡.md>

查四样，任何一样不过就退出码 1：
1. 研究版里出现的每个编号（H01、Q01、L01……）动作卡里都要有；
2. 动作卡里"标准表述"列的每一格，去掉空白和标点后要能在研究版里原样找到（不许改措辞）；
3. 动作卡总长（去掉空白）不超过 4000 字；
4. 不许有排序建议（"先写哪条""排在前面""一句带过""调先后"之类）。
"""
import re
import sys

PUNCT = r'[\s“”"‘’\'「」『』《》〈〉（）()【】、，。；：！？,.;:!?—…·\-*`|#>]'
BAN = ['先写哪条', '排在前面', '一句带过', '调先后', '排在后面']


def norm(s):
    return re.sub(PUNCT, '', s)


def tables(md):
    lines, i = md.split('\n'), 0
    while i < len(lines):
        if lines[i].lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            head = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                row = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if len(row) == len(head):
                    yield head, row
                i += 1
            continue
        i += 1


def main(graph_path, card_path):
    g = open(graph_path, encoding='utf-8').read()
    c = open(card_path, encoding='utf-8').read()
    bad = []
    ids = sorted(set(re.findall(r'\b([HQL]\d{2})\b', g)))
    miss = [x for x in ids if not re.search(r'\b%s\b' % x, c)]
    if miss:
        bad.append('动作卡漏了编号：' + '、'.join(miss))
    gn = norm(g)
    n_std = 0
    for head, row in tables(c):
        for h, cell in zip(head, row):
            if '标准表述' in h:
                for part in re.split(r'[；;]|<br>|／', cell):
                    p = norm(part)
                    if len(p) < 4:
                        continue
                    n_std += 1
                    if p not in gn:
                        bad.append('标准表述不在研究版里（可能改了措辞）：' + part.strip()[:40])
    length = len(re.sub(r'\s', '', c))
    if length > 4000:
        bad.append('动作卡 %d 字，超过 4000' % length)
    for w in BAN:
        if w in c:
            bad.append('有排序建议：' + w)
    print('%s：编号 %d 个，标准表述 %d 格，%d 字；问题 %d 个' % (card_path, len(ids), n_std, length, len(bad)))
    for b in bad:
        print('  - ' + b)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
