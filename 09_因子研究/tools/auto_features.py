#!/usr/bin/env python3
"""自动因子：不依赖人工判断、可重复计算的申论答卷特征。

既用于研究（对 68 份真人卷计算），也用于日常练习（对你自己的答案计算）。

用法（练习时）：
  python auto_features.py --answer 我的答案.txt --material 试题材料.txt [--landing 落点词1,落点词2]
答案文件格式：用"第一题""第二题""第三题"分隔三道题（每题后面直接写答案，不要抄题干）。
"""
import argparse, json, re, sys

GENERIC = r'加强|完善|推动|提升|优化|强化|健全|加大|促进|推进|深化|提高|注重|重视'
TOOL = (r'资金|补贴|基金|奖补|贷款|保险|平台|机制|清单|档案|台账|无人机|监测|培训|招聘|引进|奖励|表彰|考核|评价|'
        r'标准|试点|专项|一网通办|热线|系统|数据库|联席|督查|巡查|讲座|手册|短视频|公众号|示范|联合体|园区|基地|'
        r'合作社|结对|帮扶|认养|补偿|处罚|执法|规划|目录|指南|课程|学院|驿站|窗口')
NUM_ITEM = re.compile(r'(?:^|\n)\s*(?:\d{1,2}\s*[\.、．:：]|[①②③④⑤⑥⑦⑧⑨⑩]|[（(]\d{1,2}[)）]|[一二三四五六七八九十]、)')
def _loose(word):
    """允许题干被 PDF 换行打断：每个字之间都可以有空白。"""
    return r'\s*'.join(re.escape(c) if not c.startswith('\\') else c for c in word)


REQ_END = re.compile(
    r'(?:' + _loose('不超过') + r'\s*\d+\s*' + _loose('字') +
    r'|\d+\s*[-—～~]\s*\d+\s*' + _loose('字') +
    r'|\d+\s*' + _loose('字左右') +
    r'|' + _loose('字数') + r'[^。]{0,20}?' + _loose('字') +
    r')[\s。）)；;]*')


def han(s):
    return re.sub(r'[^一-鿿]', '', s)


def ngrams(s, n=4):
    s = han(s)
    return [s[i:i + n] for i in range(len(s) - n + 1)]


def split_questions(text):
    """按题号切成三段，并尽量去掉题干。返回 {1: 答案, 2: ..., 3: ...}（缺失的题为空串）。"""
    marks = []
    for q, pat in ((1, r'(第一题|第一大题|问题一|(?:^|\n)\s*一、)'), (2, r'(第二题|第二大题|问题二|(?:^|\n)\s*二、)'),
                   (3, r'(第三题|第三大题|问题三|(?:^|\n)\s*三、)')):
        m = re.search(pat, text)
        if m:
            marks.append((m.start(), q))
    marks.sort()
    out = {1: '', 2: '', 3: ''}
    for k, (pos, q) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else len(text)
        seg = text[pos:end]
        head = seg[:520]
        ends = list(REQ_END.finditer(head))
        if ends:
            seg = seg[ends[-1].end():]
        out[q] = seg.strip()
    return out


def features(answer_text, material_text=None, landing=None):
    qs = split_questions(answer_text)
    mat_grams = set(ngrams(material_text)) if material_text else None
    f = {}
    for q in (1, 2, 3):
        s = qs[q]
        h = han(s)
        f[f'q{q}_chars'] = len(h) if s else None
        f[f'q{q}_items'] = len(NUM_ITEM.findall(s)) if s else None
        if s and mat_grams is not None:
            g = ngrams(s)
            f[f'q{q}_material_overlap'] = round(sum(x in mat_grams for x in g) / len(g), 4) if g else None
        else:
            f[f'q{q}_material_overlap'] = None
    s2 = qs[2]
    if s2:
        n = max(len(han(s2)), 1)
        f['q2_generic_per100'] = round(len(re.findall(GENERIC, s2)) * 100 / n, 3)
        f['q2_tool_per100'] = round(len(re.findall(TOOL, s2)) * 100 / n, 3)
    else:
        f['q2_generic_per100'] = f['q2_tool_per100'] = None
    s3 = qs[3]
    if s3 and landing:
        f['q3_landing_hits_per1000'] = round(sum(s3.count(w) for w in landing) * 1000 / max(len(han(s3)), 1), 3)
    else:
        f['q3_landing_hits_per1000'] = None
    return f


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--answer', required=True)
    ap.add_argument('--material')
    ap.add_argument('--landing', help='题干落点词，逗号分隔')
    a = ap.parse_args()
    ans = open(a.answer, encoding='utf-8').read()
    mat = open(a.material, encoding='utf-8').read() if a.material else None
    land = [w for w in (a.landing or '').split(',') if w]
    print(json.dumps(features(ans, mat, land), ensure_ascii=False, indent=1))
