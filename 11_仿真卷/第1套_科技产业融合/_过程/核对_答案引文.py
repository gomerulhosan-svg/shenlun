# -*- coding: utf-8 -*-
# 核对 参考答案与解析.md 和当前材料是否对得上。
# 用法（仓库根目录）：
#   python3 11_仿真卷/第1套_科技产业融合/_过程/核对_答案引文.py          # 全部核对
#   python3 11_仿真卷/第1套_科技产业融合/_过程/核对_答案引文.py --pool 三  # 打印材料三的编号句池（写解析时对句号用）
# 材料默认读 _过程/材料_作文.md 和 _过程/材料_小题.md；同目录有 试卷.md 时改读 试卷.md（--src 过程 可强制读过程稿）。
# 核什么：
#   1 引文：「材料X〔n〕第 k 句「……」」「〔n〕第 k–m 句「……」」「材料X〔n〕「……」」，引号里的话（按省略号拆开）必须逐字在那一句（那几句、那一段）里；
#   2 段号、句号：解析正文里出现的「材料X〔n〕」「〔n〕第 k 句」「第 N 段」「第 N 段第 a–b 句」，段必须存在，句号不超过该段句数；
#   3 答案分句都在逐条解析里有一个「#####  「分句」」小节，小节标题也都能在答案里找到；
#   4 「来源：」行里所有「……」（含没带段号的）逐字在材料里；
#   5 字数：问题一 ≤200、问题二 ≤300、作文（含标题）1000 左右；自造字按 08_小题重写/tools/cost.py 的贪心覆盖口径（MIN=2，单个胶水字不计，行首序号和「问题：」「对策：」算结构字）。
# 切句口径同 08_小题重写/tools/pool.py：按。！？；切，后随的收尾引号跟前一句。
import re, os, sys, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SET))
sys.path.insert(0, os.path.join(ROOT, '08_小题重写', 'tools'))
from cost import cover, runs, abbr, GLUE, SHELL, STRUCT  # noqa: E402
from common import norm as cnorm  # noqa: E402

CN = '一二三四五六七八'


def parse(path):
    mats, cur = {}, None
    for line in open(path, encoding='utf-8').read().split('\n'):
        s = line.strip()
        m = re.match(r'^#*\s*【材料(.)】', s)
        if m:
            cur = m.group(1); mats[cur] = {}; continue
        if s.startswith('## ') or s.startswith('# '):
            if not re.match(r'^#*\s*【材料', s):
                cur = None
        m = re.match(r'^〔(\d+)〕(.*)$', s)
        if m and cur:
            mats[cur][int(m.group(1))] = m.group(2).strip()
    return mats


def sents(p):
    out, buf, i = [], '', 0
    while i < len(p):
        c = p[i]; buf += c
        if c in '。！？；':
            j = i + 1
            while j < len(p) and p[j] in '”’」』）)》': buf += p[j]; j += 1
            out.append(buf); buf = ''; i = j; continue
        i += 1
    if buf.strip(): out.append(buf)
    return out


def load(src):
    paper = os.path.join(SET, '试卷.md')
    if src != '过程' and os.path.exists(paper):
        return parse(paper), '试卷.md'
    M = {}
    M.update(parse(os.path.join(HERE, '材料_作文.md')))
    M.update(parse(os.path.join(HERE, '材料_小题.md')))
    return M, '_过程/材料_作文.md + _过程/材料_小题.md'


def L(s):
    return len(re.sub(r'\s', '', s))


def selfmade(lines, desig, whole):
    # 返回：对指定材料的自造字数、结构字数、自造片段、对整卷的自造字数（同 cost.py 的 self_d / self_w）
    tot, st, detail, totw = 0, 0, [], 0
    for l in lines:
        structs = [m.group(2) for m in STRUCT.finditer(l)]
        body = STRUCT.sub(lambda m: m.group(1), l)
        e = cnorm(body)
        cd = cover(e, desig); cw = cover(e, whole)
        sd = [r for r in runs(e, [not c for c in cd]) if not (len(r) == 1 and r in GLUE)]
        sw = [r for r in runs(e, [not c for c in cw]) if not (len(r) == 1 and r in GLUE)]
        real = [r for r in sd if not abbr(r, whole) and r not in SHELL]
        tot += sum(len(r) for r in real); st += sum(len(cnorm(s)) for s in structs)
        totw += sum(len(r) for r in sw if not abbr(r, whole) and r not in SHELL)
        detail += real
    return tot, st, detail, totw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pool'); ap.add_argument('--src', default='')
    a = ap.parse_args()
    MAT, srcname = load(a.src)
    if a.pool:
        for k in a.pool:
            print(f'######## 材料{k}（{len(MAT[k])} 段，{sum(L(p) for p in MAT[k].values())} 字）')
            for pno, p in MAT[k].items():
                print(f'[〔{pno}〕 {L(p)} 字]')
                for i, s in enumerate(sents(p), 1):
                    print(f'  {i}  {s}')
        return
    print('材料来源：', srcname)
    print('各则字数：', {k: sum(L(p) for p in v.values()) for k, v in MAT.items()}, '合计', sum(L(p) for v in MAT.values() for p in v.values()))
    ans = open(os.path.join(SET, '参考答案与解析.md'), encoding='utf-8').read()
    lines = ans.split('\n')
    bad = []; nq = 0; nref = 0
    qpat = re.compile(r'(材料([一二三四五六七八]))?〔(\d+)〕(第\s*(\d+)(?:\s*[–-]\s*(\d+))?\s*句)?(「((?:[^「」]|「[^「」]*」)*)」)?')
    dpat = re.compile(r'(材料([一二三四五六七八]))?第\s*(\d+)\s*段(第\s*(\d+)(?:\s*[–-]\s*(\d+))?\s*句)?')
    sec = None
    for ln, line in enumerate(lines, 1):
        if line.startswith('## 问题一'): sec = '三'
        elif line.startswith('## 问题二'): sec = '五'
        elif line.startswith('## 问题三'): sec = None
        last = None
        for mm in qpat.finditer(line):
            mat = mm.group(2) or last or sec
            if mm.group(2): last = mm.group(2)
            if not mat:
                bad.append((ln, f'〔{mm.group(3)}〕前面没有材料名，也不在小题节里')); continue
            pno = int(mm.group(3)); nref += 1
            para = MAT.get(mat, {}).get(pno)
            if para is None:
                bad.append((ln, f'材料{mat}没有〔{pno}〕')); continue
            ss = sents(para)
            k = k2 = None
            if mm.group(5):
                k = int(mm.group(5)); k2 = int(mm.group(6) or k)
                if k2 > len(ss) or k < 1:
                    bad.append((ln, f'材料{mat}〔{pno}〕只有 {len(ss)} 句，引了第 {k}–{k2} 句')); continue
            if mm.group(8) is not None:
                nq += 1
                target = ''.join(ss[k - 1:k2]) if k else para
                for pc in [x for x in re.split(r'……|…', mm.group(8)) if x.strip()]:
                    if pc.strip() not in target:
                        loc = [i + 1 for i, s in enumerate(ss) if pc.strip() in s]
                        bad.append((ln, f'材料{mat}〔{pno}〕第{k}句引文对不上（实际在第{loc}句）', pc[:30]))
        # 散文里的「第 N 段」「材料X第 N 段第 a–b 句」
        last = None
        for mm in qpat.finditer(line):
            if mm.group(2): last = mm.group(2)
        for mm in dpat.finditer(line):
            mat = mm.group(2)
            if not mat:
                pre = line[:mm.start()]
                ms = re.findall(r'材料([一二三四五六七八])', pre)
                mat = ms[-1] if ms else sec
            if not mat:
                continue
            pno = int(mm.group(3)); nref += 1
            para = MAT.get(mat, {}).get(pno)
            if para is None:
                bad.append((ln, f'散文里的「第 {pno} 段」：材料{mat}没有这一段')); continue
            if mm.group(5):
                k = int(mm.group(5)); k2 = int(mm.group(6) or k); n = len(sents(para))
                if k2 > n:
                    bad.append((ln, f'散文里的「第 {pno} 段第 {k}–{k2} 句」：材料{mat}〔{pno}〕只有 {n} 句'))
    print(f'段号、句号引用 {nref} 处；带引文 {nq} 条；对不上 {len(bad)} 条')
    for b in bad: print('  ', b)

    # 答案分句与解析小节
    def block(title, nxt):
        i = ans.index(title); j = ans.index(nxt, i)
        return ans[i:j]
    whole = cnorm(''.join(p for v in MAT.values() for p in v.values()))
    res = {}
    for q, mat, lim in (('## 问题一', '三', 200), ('## 问题二', '五', 300)):
        sec_t = block(q, '## 问题' + ('二' if q.endswith('一') else '三'))
        a0 = sec_t.index('### 答案'); a1 = sec_t.index('\n（', a0)
        al = [l[1:].strip() for l in sec_t[a0:a1].split('\n') if l.startswith('>') and l[1:].strip()]
        n = sum(L(x) for x in al)
        desig = cnorm(''.join(MAT[mat].values()))
        sm, st, det, smw = selfmade(al, desig, whole)
        heads = re.findall(r'^##### 「(.+)」\s*$', sec_t, re.M)
        body = ''.join(al)
        miss_h = [h for h in heads if h.replace('“', '').replace('”', '') not in body.replace('“', '').replace('”', '')]
        clauses = []
        for x in al:
            x = STRUCT.sub(lambda m: m.group(1), x)
            if x in ('问题：', '对策：'): continue
            clauses += [c for c in re.split(r'[，；。：]', x) if c.strip()]
        hs = set(h.replace('“', '').replace('”', '') for h in heads)
        miss_c = [c for c in clauses if c.replace('“', '').replace('”', '') not in hs]
        res[q] = n
        print(f'{q[3:]}：答案 {n} 字 / 上限 {lim}{"　⚠ 超字" if n > lim else ""}；{len(al)} 行；自造 {sm} 字（对指定则）{det}，对整卷 {smw} 字；结构字 {st}')
        print(f'    解析小节 {len(heads)} 个；答案里找不到的小节标题 {miss_h or "无"}；没有解析小节的答案分句 {miss_c or "无"}')
    e0 = ans.index('### 作文'); e1 = ans.index('### 逐句解析', e0)
    el = [l[1:].strip().replace('*', '') for l in ans[e0:e1].split('\n') if l.startswith('>') and l[1:].strip()]
    en = sum(L(x) for x in el)
    esm, _, edet, _ = selfmade(el, whole, whole)
    print(f'作文：含标题 {en} 字（标题 {sum(L(x) for x in el[:2])}，正文 {en - sum(L(x) for x in el[:2])}）；自造 {esm} 字 {edet}')
    # 范文每句在逐句解析里有一个加粗小节
    eb = ans[e1:]
    heads = set(re.findall(r'^\*\*(.+)\*\*\s*$', eb, re.M))
    sent = []
    for x in el:
        x = x.strip('*')
        sent += [s.strip() for s in re.findall(r'[^。！？；：]*[。！？；：]?', x) if s.strip()]
    miss = [s for s in sent if not any(s in h or h in s for h in heads)]
    print(f'    逐句解析小节 {len(heads)} 个；范文里没有对应小节的片段：{miss or "无"}')
    # 5 「来源：」行里的每一处「……」（不论有没有段号）：按省略号拆开，4 字以上的片段要逐字在材料里（引号统一成“”再比）
    qn = lambda s: s.replace('‘', '“').replace('’', '”')
    pool_all = qn(''.join(p for v in MAT.values() for p in v.values()))
    loose, nsrc = [], 0
    for ln, line in enumerate(lines, 1):
        if '来源：' not in line:
            continue
        for mm in re.finditer(r'「((?:[^「」]|「[^「」]*」)*)」', line):
            for pc in re.split(r'……|…', mm.group(1)):
                pc = qn(pc.strip())
                if len(pc) < 4:
                    continue
                nsrc += 1
                if pc not in pool_all:
                    loose.append((ln, pc[:30]))
    print(f'「来源：」行里的引文片段 {nsrc} 个；贴不回材料的 {len(loose)} 个', loose)
    bad += loose
    return len(bad)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
