#!/usr/bin/env python3
"""按年汇编：python3 09_按年汇编/tools/build.py

把每套卷的题干、小题（答案、考场上的思路、逐条解析、压缩与成本）、大作文（考场上的思路、作文、逐句解析）
拼成一年一个 Markdown 文件，写到 09_按年汇编/。
- 题干：08_小题重写/samples/<套>/material.txt 里「问题一」以后的作答要求，原文照录；
- 小题：08_小题重写/<套>/Qn.md（第二遍终稿）；
- 大作文：07_句子层/重写/<套>_重写.md 的「考场上的思路」「一、作文」「二、逐句标注」三节。
内容一字不改，只做三件事：标题降两级嵌进年份文件；答案和作文放进引用块；
连续的行拆成段（GitHub 渲染 .md 时单个换行不断行，不拆会连成一段）。
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(OUT, '..'))
SMALL = os.path.join(ROOT, '08_小题重写')
ESSAY = os.path.join(ROOT, '07_句子层', '重写')

# 年 → [(套, 卷名, 简称)]，同一年内的顺序：省市/一卷/县级 → 县镇/二卷/乡镇 → 选调
YEARS = [
    (2026, [('2026省市', '2026 年广东省考《申论》·省市卷', '2026 省市卷'),
            ('2026县镇', '2026 年广东省考《申论》·县镇卷', '2026 县镇卷')]),
    (2025, [('2025省市', '2025 年广东省考《申论》·省市卷', '2025 省市卷'),
            ('2025县镇', '2025 年广东省考《申论》·县镇卷', '2025 县镇卷'),
            ('2025选调', '2025 年广东选调生《申论》', '2025 选调卷')]),
    (2024, [('2024一卷', '2024 年广东省考《申论》·一卷', '2024 一卷'),
            ('2024二卷', '2024 年广东省考《申论》·二卷', '2024 二卷'),
            ('2024选调', '2024 年广东选调生《申论》', '2024 选调卷')]),
    (2023, [('2023县级', '2023 年广东省考《申论》·县级卷', '2023 县级卷'),
            ('2023乡镇', '2023 年广东省考《申论》·乡镇卷', '2023 乡镇卷')]),
    (2022, [('2022县级', '2022 年广东省考《申论》·县级卷', '2022 县级卷'),
            ('2022乡镇', '2022 年广东省考《申论》·乡镇卷', '2022 乡镇卷')]),
    (2021, [('2021县级', '2021 年广东省考《申论》·县级卷', '2021 县级卷'),
            ('2021乡镇', '2021 年广东省考《申论》·乡镇卷', '2021 乡镇卷')]),
    (2020, [('2020县级', '2020 年广东省考《申论》·县级卷', '2020 县级卷'),
            ('2020乡镇', '2020 年广东省考《申论》·乡镇卷', '2020 乡镇卷')]),
]

# 大作文：套 → (主题, 文体)，主题取自题干原话
ESSAY_THEME = {
    '2026省市': ('绿色发展是高质量发展的底色', '议论文'),
    '2026县镇': ('绿美广东生态建设是关系广东长远发展和民生福祉的重要工程', '议论文'),
    '2025省市': ('继续做好创新这篇大文章', '议论文'),
    '2025县镇': ('乡村振兴关键在产业振兴', '议论文'),
    '2025选调': ('广东全面推进海洋强省建设', '议论文'),
    '2024一卷': ('高水平科技自立自强', '议论文'),
    '2024二卷': ('“百千万工程”是广东推动高质量发展的头号工程', '议论文'),
    '2024选调': ('堪当民族复兴重任的时代新人', '议论文'),
    '2023县级': ('把广东制造业这份厚实家当做优做强', '策论文'),
    '2022县级': ('粤港澳大湾区建设取得的实效和经验', '议论文'),
    '2021县级': ('站在新起点，迈向新征程，推动广东高质量发展', '议论文'),
    '2020县级': ('推进国家治理体系和治理能力现代化，推动新时代广东改革发展走在全国前列', '议论文'),
}

# 同一年里题干相同的小题：年 → 说明
TWINS = {
    2026: '省市卷问题一和县镇卷问题一是同一道题（材料逐行相同，省市卷叫材料三、县镇卷叫材料五），两份答案逐字相同，解析只在材料编号上不同。',
    2024: '一卷问题一和二卷问题一是同一道题（题干逐字相同，材料二几乎相同），两份答案逐字相同；解析因为两卷材料分段不同，段号和个别说法有出入。',
}

CN = '一二三四五六七八九十'
FILENAME = '{year}年广东申论_题干答案与逐句解析.md'


def read(path):
    return open(path, encoding='utf-8').read()


# ---------- 题干 ----------

def stem_items(sid):
    """material.txt 里「问题一」以后的作答要求 → [(问题几, 题干, [要求行])]。"""
    mt = read(os.path.join(SMALL, 'samples', sid, 'material.txt'))
    m = re.search(r'\n\s*【?问题一】?[：:]?\s*\n', mt) or re.search(r'\n\s*【?问题一】?', mt)
    lines = []
    for l in (x.strip() for x in mt[m.start():].split('\n')):
        if not l or re.match(r'^(答题纸|第[一二三四五]大题|\d+字)', l):
            continue
        if not lines or re.match(r'^(【?问题[一二三四五六]】?[：:．.]?$|【?问题[一二三四五六]|要求[：:]|（\s*\d\s*）|\(\d\))', l):
            lines.append(l)
        else:
            lines[-1] += l
    items = []
    for l in lines:
        q = re.match(r'^【?问题([一二三四五六])】?[：:．.]?\s*(?:[（(][一二三四五六][）)])?\s*(.*)$', l)
        if q:
            text = q.group(2)
            req = []
            # 题干和「要求」挤在同一行的，从「要求：」处断开
            k = re.search(r'(?<=[）)])\s*(要求[：:].*)$', text)
            if k:
                text, req = text[:k.start()].rstrip(), [k.group(1)]
            items.append(('问题' + q.group(1), text, req))
        else:
            items[-1][2].append(l)
    for _, _, req in items:
        for i, r in enumerate(req):
            req[i] = re.sub(r'^要求[：:]\s*要求[：:]', '要求：', r)
    return items


def stems_md(sid):
    out = ['### 题干', '']
    for label, text, req in stem_items(sid):
        out += ['**%s**　%s' % (label, text), '']
        # 「要求：（1）……；（2）……」挤在一行的，按小项拆开；各项之间用硬换行（行末两个空格）
        parts = [p.strip() for r in req for p in re.split(r'(?=[（(]\d[）)])', r) if p.strip()]
        out += [p + '  ' if i < len(parts) - 1 else p for i, p in enumerate(parts)]
        out.append('')
    return out


# ---------- 小题 ----------

def question_md(path):
    """Qn.md → 嵌进年份文件：标题降两级，答案进引用块。返回 (标题, 行)。"""
    out, sec, title = [], '', ''
    for raw in read(path).split('\n'):
        l = raw.rstrip()
        if l.startswith('#'):
            level = len(l) - len(l.lstrip('#'))
            text = l[level:].strip()
            if level == 1:
                title = text
            if level == 2:
                sec = text
            out += ['#' * (level + 2) + ' ' + text, '']
            continue
        if not l.strip():
            continue
        if sec == '答案':
            out += ['> ' + l.strip(), '>']
            continue
        out += [l, '' if not l.startswith('- ') else None]
    # 引用块末尾的空 > 去掉；列表项之间不加空行，列表结束补空行
    res = []
    for i, l in enumerate(out):
        if l is None:
            nxt = next((x for x in out[i + 1:] if x is not None), '')
            if not nxt.startswith('- '):
                res.append('')
            continue
        if l == '>' and (i + 1 >= len(out) or not (out[i + 1] or '').startswith('>')):
            res.append('')
            continue
        res.append(l)
    return title, squeeze(res)


# ---------- 大作文 ----------

def sections(text):
    """按「## 」切节 → {节名: 正文}。"""
    parts = re.split(r'(?m)^## (.+)$', text)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def essay_md(sid, qnum):
    path = os.path.join(ESSAY, sid + '_重写.md')
    if not os.path.exists(path):
        return None, []
    sec = sections(read(path))
    theme, genre = ESSAY_THEME[sid]
    title = '问题%s　大作文：%s（50 分，%s）' % (CN[qnum - 1], theme, genre)
    out = ['### ' + title, '']

    out += ['#### 考场上的思路', '']
    for l in (x.strip() for x in sec['考场上的思路'].split('\n')):
        if l:
            out += [l, '']

    out += ['#### 作文', '']
    paras = [p.strip() for p in sec['一、作文'].strip().split('\n') if p.strip()]
    head, _, sub = paras[0].partition('——')
    body = paras[1:]
    if sub:
        body = ['——' + sub.strip()] + body
    out += ['> **%s**' % head.strip(), '>']
    if body and body[0].startswith('——'):
        out += ['> **%s**' % body[0], '>']
        body = body[1:]
    for p in body:
        out += ['> ' + p, '>']
    out[-1] = ''

    out += ['#### 逐句解析', '']
    quote = False
    for l in (x.rstrip() for x in sec['二、逐句标注'].split('\n')):
        s = l.strip()
        if not s:
            continue
        if s.startswith('>'):
            if quote:
                out.append('>')
            out.append('> ' + s.lstrip('>').strip())
            quote = True
            continue
        if quote:
            out.append('')
            quote = False
        if s.startswith('### '):
            out += ['##### ' + s[4:].strip(), '']
        elif s.startswith('#### '):
            out += ['###### ' + s[5:].strip(), '']
        else:
            out += [s, '']
    return title, squeeze(out)


def squeeze(lines):
    """连续空行压成一个，去掉首尾空行。"""
    res = []
    for l in lines:
        if l == '' and (not res or res[-1] == ''):
            continue
        res.append(l)
    while res and res[-1] == '':
        res.pop()
    return res


# ---------- 年份文件 ----------

def build_year(year, papers):
    toc, body = [], []
    for sid, name, short in papers:
        qs = sorted(f for f in os.listdir(os.path.join(SMALL, sid)) if re.match(r'^Q\d\.md$', f))
        body += ['---', '', '## ' + name, '']
        body += stems_md(sid)
        toc.append('- **%s**' % name)
        for f in qs:
            title, lines = question_md(os.path.join(SMALL, sid, f))
            body += lines + ['']
            toc.append('  - ' + title)
        title, lines = essay_md(sid, len(qs) + 1)
        if lines:
            body += lines + ['']
            toc.append('  - ' + title)
        else:
            toc.append('  - （这套卷没有大作文）')

    names = '、'.join(p[1] for p in papers)
    head = [
        '# %d 年广东申论：题干 · 答案 · 逐句解析' % year, '',
        '收 %d 套卷：%s。' % (len(papers), names), '',
        '每套卷依次是：', '',
        '1. **题干**：试卷的作答要求，照原卷录入。',
        '2. **小题**：每道题依次是答案、考场上的思路、逐条解析、压缩与成本。逐条解析先说每个要点「现实里是一件什么事」「为什么归成这一条」，'
        '再对答案里的每个分句写来源（材料几第几段第几句的原话）、怎么改的、为什么这么改、不这么写会怎样、以后遇到怎么办。',
        '3. **大作文**：考场上的思路、作文、逐句解析。逐句解析按标题、开头、各段、结尾分块，每句写来源、怎么改的、为什么、以后遇到怎么办。',
        '',
        '解析里的「材料几第几段」指原卷给定材料的自然段，材料原文见仓库根目录同年份的真题 PDF。',
        '',
    ]
    if year in TWINS:
        head += ['**同题说明**：' + TWINS[year], '']
    if year == 2024:
        head += ['2024 年另有一套三卷（行政执法），这批答案没有做，不收。', '']
    if any(sid.endswith('乡镇') for sid, _, _ in papers):
        head += ['乡镇卷是五道小题，没有大作文。', '']
    head += ['## 目录', ''] + toc + ['']
    return '\n'.join(squeeze(head + body)) + '\n'


def check():
    """逐行核对：每道小题 Qn.md、每篇大作文三节里的每一行、每道题的题干，都在年份文件里。返回缺的行数。"""
    def norm(l):
        l = re.sub(r'^(#+|>|-)\s*', '', l.strip()).strip()
        return re.sub(r'^\*\*(.*)\*\*$', r'\1', l).rstrip()
    miss = nq = ne = 0
    for year, papers in YEARS:
        have = set(norm(x) for x in read(os.path.join(OUT, FILENAME.format(year=year))).split('\n'))
        for sid, _, _ in papers:
            want = []
            for f in sorted(f for f in os.listdir(os.path.join(SMALL, sid)) if re.match(r'^Q\d\.md$', f)):
                nq += 1
                want += [(f, l) for l in read(os.path.join(SMALL, sid, f)).split('\n')]
            path = os.path.join(ESSAY, sid + '_重写.md')
            if os.path.exists(path):
                ne += 1
                sec = sections(read(path))
                essay = [p.strip() for p in sec['一、作文'].split('\n') if p.strip()]
                head, _, sub = essay[0].partition('——')
                essay = [head, '——' + sub] + essay[1:] if sub else essay
                want += [('大作文', l) for l in sec['考场上的思路'].split('\n') + essay + sec['二、逐句标注'].split('\n')]
            for where, l in want:
                if l.strip() and norm(l) not in have:
                    miss += 1
                    print('缺：%s %s %s' % (sid, where, l.strip()[:40]))
            for label, text, _ in stem_items(sid):
                if '**%s**　%s' % (label, text) not in have:
                    miss += 1
                    print('缺：%s 题干 %s' % (sid, label))
    print('核对：小题 %d 道、大作文 %d 篇，缺 %d 行' % (nq, ne, miss))
    return miss


def main():
    written = []
    for year, papers in YEARS:
        path = os.path.join(OUT, FILENAME.format(year=year))
        text = build_year(year, papers)
        open(path, 'w', encoding='utf-8').write(text)
        written.append((path, len(text)))
    for path, n in written:
        print('%6d 字符  %s' % (n, os.path.relpath(path, ROOT)))
    if check():
        sys.exit(1)


if __name__ == '__main__':
    main()
