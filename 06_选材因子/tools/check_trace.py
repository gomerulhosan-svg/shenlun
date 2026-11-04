#!/usr/bin/env python3
"""核对国内模型的溯源结果：python3 10_选材因子/tools/check_trace.py 2025省市 [材料四〔3〕 ...]

读 10_选材因子/溯源结果/ 下的「母文件_<年>.md」和「溯源结果_<卷>.md」，
把卷面每一段材料和两样东西逐字比：母文件（讲话、政府工作报告等）和溯源结果里贴的原文。
比法：去掉标点空白后，材料里凡是连续 8 个字在原文里原样出现，就算"找得到"。
输出每段的覆盖率（找得到的字占这段的比例）；后面跟段号时，再把这几段里找不到的字用【】标出来。

覆盖率怎么读：70% 以上基本是照搬原文加删减；30%–70% 是改写或拼接；30% 以下要么是命题人
自己写的，要么是国内模型给的原文不对，需要补查。
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
DIR = os.path.join(ROOT, '10_选材因子', '溯源结果')
sys.path.insert(0, os.path.join(ROOT, '08_小题重写', 'tools'))
from common import split_blocks  # noqa: E402

N = 8
PUNCT = r'[\s“”"‘’\'「」『』《》〈〉（）()【】、，。；：！？,.;:!?—…·\-]'


def norm(s):
    return re.sub(PUNCT, '', s)


def grams(t):
    t = norm(t)
    return {t[i:i + N] for i in range(len(t) - N + 1)}


def cover(para, g):
    p = norm(para)
    m = [False] * len(p)
    for i in range(len(p) - N + 1):
        if p[i:i + N] in g:
            for j in range(i, i + N):
                m[j] = True
    return (sum(m) / len(p) if p else 0), p, m


def mother_sections(text):
    """母文件按「### 」「## 」小节切开，每节一个来源。"""
    parts = re.split(r'\n(#{2,3} .+)\n', '\n' + text)
    return {parts[i].lstrip('# ').strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def trace_sources(text):
    """溯源结果：每段 → [(来源标题, 贴的原文)]。"""
    blocks = re.split(r'\n#{2,3} *(材料[一二三四五六七八九十]+〔\d+〕)[^\n]*\n', text)
    out = {}
    for k in range(1, len(blocks), 2):
        srcs = re.split(r'\n- 来源\d*：', '\n' + blocks[k + 1])
        items = []
        for s in srcs[1:]:
            title = s.split('\n', 1)[0]
            quote = '\n'.join(l.strip()[1:] for l in s.split('\n') if l.strip().startswith('>'))
            items.append((title, quote))
        out[blocks[k]] = items
    return out


def main():
    sid, marks = sys.argv[1], sys.argv[2:]
    year = sid[:4]
    mother = mother_sections(open(os.path.join(DIR, '母文件_%s.md' % year), encoding='utf-8').read())
    trace = trace_sources(open(os.path.join(DIR, '溯源结果_%s.md' % sid), encoding='utf-8').read())
    mg = {k: grams(v) for k, v in mother.items() if len(norm(v)) > 200}
    print('%-12s %5s  %-24s %5s  %-30s %5s' % ('段', '字数', '母文件里最像的一节', '覆盖', '溯源贴的原文里最像的一篇', '合计'))
    for name, paras in split_blocks(sid):
        for i, para in enumerate(paras, 1):
            key = '材料%s〔%d〕' % (name, i)
            srcs = trace.get(key, [])
            best_m = max(((cover(para, g)[0], k) for k, g in mg.items()), default=(0, ''))
            best_t = max(((cover(para, grams(q))[0], t.split('｜')[0]) for t, q in srcs), default=(0, '（未找到）'))
            allg = set().union(*mg.values(), *(grams(q) for _, q in srcs))
            tot, p, m = cover(para, allg)
            print('%-12s %5d  %-24s %4.0f%%  %-30s %4.0f%%  %4.0f%%' % (
                key, len(p), best_m[1][:24], best_m[0] * 100, best_t[1][:30], best_t[0] * 100, tot * 100))
            if key in marks:
                out, cur, flag = [], '', None
                for ch, f in zip(p, m):
                    if f != flag and cur:
                        out.append(cur if flag else '【' + cur + '】')
                        cur = ''
                    cur += ch
                    flag = f
                out.append(cur if flag else '【' + cur + '】')
                print('    ' + ''.join(out))


if __name__ == '__main__':
    main()
