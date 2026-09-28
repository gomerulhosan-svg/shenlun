# -*- coding: utf-8 -*-
# 2026-09-28 定稿核查处理后同步两处：材料五〔4〕并句后 P5 从第 4 句移到第 3 句（S2）；问题一题干改用 R26 原话，D 部分加对象词「公共服务领域」。
# 定稿核查（一致性）用的独立脚本，只读，不改任何文件。
# 用法（仓库根目录）：python3 -B 11_仿真卷/第1套_科技产业融合/_过程/定稿核查_一致性.py [--nf]
# 核什么：
#   A 试卷.md 各则字数、段数（口径：去〔段号〕和空白，含标点）；2025、2026 省市卷同口径字数
#   B 参考答案与解析.md：所有「材料X〔n〕」「〔n〕第 k 句」「第 N 段第 k 句」「同段第 k 句」的段、句是否存在；
#     紧跟在出处后面的「引文」（按省略号拆开）是否逐字在那一句（没写句号就在那一段）里；
#     全文「」引文里能贴回材料的数量（--nf 打印贴不回的，供人工分拣）
#   C 三道题答案字数、问题栏/对策栏字数、范文标题/正文字数；自造字（08_小题重写/tools/cost.py 口径）
#   D 命题说明第十节自检表各项重算：对象词密度、整段零票占比、采分句占比、题干 15 字片段位置、小题材料地名、
#     合成／示意登记表逐条原文在段、按标注计数、答案引到的不同段数
# 句子切法同 08_小题重写/tools/pool.py：按。！？；切，后随的收尾引号跟前一句。
import re, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SET))
CN = '一二三四五六七八'


def cnt(s):
    return len(re.sub(r'\s', '', s))


def sentences(p):
    return [s for s in re.findall(r'[^。！？；]*[。！？；]+[”」’]*|[^。！？；]+$', p) if re.sub(r'[\s”」’]', '', s)]


def pieces(Q):
    return [x for x in re.split(r'……|…', Q) if x.strip()]


def in_text(Q, text):
    pos = 0
    for pc in pieces(Q):
        i = text.find(pc, pos)
        if i < 0:
            return False
        pos = i + len(pc)
    return True


# ---------- A 试卷 ----------
T = open(os.path.join(SET, '试卷.md'), encoding='utf-8').read()
body = T.split('## 给定材料')[1].split('## 作答要求')[0]
mats = {}
for m in re.finditer(r'### 【材料([一二三四五六七八])】\n(.*?)(?=### 【材料|\Z)', body, re.S):
    mats[m.group(1)] = {int(p.group(1)): p.group(2).strip() for p in re.finditer(r'〔(\d+)〕(.*)', m.group(2))}
size = {k: sum(cnt(v) for v in mats[k].values()) for k in CN}
tot = sum(size.values())
print('A 各则字数', size, '合计', tot, '段数', {k: len(mats[k]) for k in CN})
print('  小题两则占比 %.1f%%' % ((size['三'] + size['五']) / tot * 100))
for f, a, b in [('2025', 34, 154), ('2026', 31, 189)]:
    L = open(os.path.join(ROOT, '09_按年汇编', f + '年广东申论_题干答案与逐句解析.md'), encoding='utf-8').read().split('\n')[a:b - 1]
    n = 0; cur = None
    for l in L:
        if re.match(r'#### 材料', l):
            cur = 1; continue
        if l.startswith('#') or not cur:
            continue
        n += cnt(re.sub(r'〔\d+〕', '', l))
    print('  %s 省市卷同口径 %d 字' % (f, n))
ALL = '\n'.join(v for k in CN for v in mats[k].values())

# ---------- B 答案引文 ----------
A = open(os.path.join(SET, '参考答案与解析.md'), encoding='utf-8').read().split('\n')


def default_mat(ln):
    if 33 <= ln < 237: return '三'
    if 237 <= ln < 545: return '五'
    return None


SN = r'(?:\s*第\s*(?P<s1>\d+)(?:\s*[、–\-]\s*(?P<s2>\d+))?\s*句)?'
CIT = re.compile(r'(?:材料(?P<mat>[一二三四五六七八])\s*)?(?:〔(?P<p1>\d+)〕|第\s*(?P<p2>\d+)\s*段)' + SN +
                 r'|(?P<same>同段|同句)?(?<![段\d])第\s*(?P<t1>\d+)(?:\s*[、–\-]\s*(?P<t2>\d+))?\s*句')
QT = re.compile(r'「([^「」]*)」')
st = dict(出处=0, 段不存在=0, 句不存在=0, 紧跟引文=0, 紧跟引文对不上=0, 引文=0, 引文在材料=0)
probs, nf, paras_seen = [], [], set()
cur_mat = cur_para = None
for ln, line in enumerate(A, 1):
    dm = default_mat(ln)
    if line.startswith('#'):
        cur_mat, cur_para = dm, None
    if cur_mat is None:
        cur_mat = dm
    qs = [(m.start(), m.end()) for m in QT.finditer(line)]
    ev = [(m.start(), 'c', m) for m in CIT.finditer(line) if not any(a < m.start() < b for a, b in qs)]
    ev += [(m.start(), 'q', m) for m in QT.finditer(line)]
    ev.sort(key=lambda e: e[0])
    last = None
    for pos, kind, m in ev:
        if kind == 'c':
            g = m.groupdict()
            if g['p1'] or g['p2']:
                mat = g['mat'] or cur_mat; para = int(g['p1'] or g['p2']); s1, s2 = g['s1'], g['s2']
            else:
                mat, para, s1, s2 = cur_mat, cur_para, g['t1'], g['t2']
            st['出处'] += 1
            if mat is None or para is None:
                last = None; continue
            if para not in mats[mat]:
                st['段不存在'] += 1; probs.append((ln, '段不存在', mat, para)); last = None; continue
            paras_seen.add((mat, para))
            ss = sentences(mats[mat][para])
            for s in (s1, s2):
                if s and int(s) > len(ss):
                    st['句不存在'] += 1; probs.append((ln, '句不存在', mat, para, s))
            cur_mat, cur_para = mat, para
            last = (mat, para, s1, s2, m.end())
        else:
            Q = m.group(1); st['引文'] += 1
            ok = in_text(Q, ALL)
            st['引文在材料'] += ok
            if not ok:
                nf.append((ln, Q))
            if last and pos - last[4] <= 12 and not re.search(r'[。；，（）]', line[last[4]:pos]):
                mat, para, s1, s2, _ = last
                st['紧跟引文'] += 1
                ss = sentences(mats[mat][para])
                tgt = ''.join(ss[int(s1) - 1:int(s2 or s1)]) if s1 else mats[mat][para]
                if not in_text(Q, tgt):
                    st['紧跟引文对不上'] += 1
                    probs.append((ln, '紧跟引文对不上', '材料%s〔%d〕第%s句' % (mat, para, s1), Q[:60]))
                last = None
print('B 答案引文', st, '引到的不同段', len(paras_seen))
for p in probs:
    print('  ', p)
if '--nf' in sys.argv:
    for ln, Q in nf:
        print('   贴不回', ln, Q[:80])

# ---------- C 字数 ----------
def blk(a, b):
    return [re.sub(r'^>\s?', '', l).replace('**', '') for l in A[a - 1:b] if l.startswith('>') and re.sub(r'^>\s?', '', l).strip()]
q1, q2, es = blk(37, 45), blk(241, 267), blk(563, 577)
i = q2.index('对策：')
print('C 问题一', [cnt(l) for l in q1], sum(map(cnt, q1)))
print('  问题二', sum(map(cnt, q2)), '问题栏', sum(map(cnt, q2[:i])), '对策栏', sum(map(cnt, q2[i:])))
print('  作文', sum(map(cnt, es)), '标题', cnt(es[0]) + cnt(es[1]), '正文', sum(map(cnt, es[2:])))
sys.path.insert(0, os.path.join(ROOT, '08_小题重写', 'tools'))
from cost import cover, runs, abbr, GLUE, SHELL, STRUCT  # noqa
from common import norm  # noqa
W = norm(ALL)


def selfmade(lines, desig):
    out = []
    for l in lines:
        e = norm(STRUCT.sub(lambda m: m.group(1), l))
        cd = cover(e, desig)
        out += [r for r in runs(e, [not c for c in cd]) if not (len(r) == 1 and r in GLUE) and not abbr(r, W) and r not in SHELL]
    return sum(map(len, out)), out
print('  自造 问题一', selfmade(q1, norm(''.join(mats['三'].values()))), '问题二', selfmade(q2, norm(''.join(mats['五'].values()))), '作文', selfmade(es, W))

# ---------- D 自检表重算 ----------
txt = {k: ''.join(mats[k].values()) for k in CN}
for w in ['人工智能+', '公共服务领域', '公共服务场景', '低空经济']:
    print('D %s 各则次数' % w, {k: txt[k].count(w) for k in CN}, '每千字', {k: round(txt[k].count(w) / size[k] * 1000, 2) for k in CN if txt[k].count(w)},
          '材料三前三段', [p for p in (1, 2, 3) if w in mats['三'][p]])
z3 = sum(cnt(mats['三'][p]) for p in (1, 2, 8)); z5 = sum(cnt(mats['五'][p]) for p in (1, 2))
print('  整段零票 材料三 %d（%.1f%%） 材料五 %d（%.1f%%）' % (z3, z3 / size['三'] * 100, z5, z5 / size['五'] * 100))


def ssum(k, spec):
    return sum(cnt(sentences(mats[k][p])[s - 1]) for p, s in spec)
S1 = [(3, 2), (4, 4), (4, 5), (5, 2), (5, 3), (5, 7), (5, 8), (6, 2), (6, 3), (6, 6), (7, 2), (7, 3), (7, 5)]
S2 = [(3, 3), (3, 5), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (5, 4), (6, 2), (6, 3), (6, 5), (7, 2), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (9, 2), (9, 3), (10, 3)]
a, b = ssum('三', S1), ssum('五', S2)
print('  采分句 材料三 %d 字、零票句约 %.1f%%；材料五 %d 字、零票句约 %.1f%%' % (a, (1 - a / size['三']) * 100, b, (1 - b / size['五']) * 100))
stem = '强化科技创新和产业创新深度融合'
print('  题干引语 %d 字，逐字所在段' % len(stem), [(k, p) for k in CN for p in mats[k] if stem in mats[k][p]],
      '；近形「科技创新和产业创新深度融合」所在段', [(k, p) for k in CN for p in mats[k] if '科技创新和产业创新深度融合' in mats[k][p]])
places = ['广东', '广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮', '香港', '澳门', '大湾区', '粤港澳', '南沙', '前海', '横琴', '北京', '上海', '南海', '顺德', '松山湖', '光明']
print('  小题材料真实地名', {k: [p for p in places if p in txt[k]] for k in '三五'})
M = open(os.path.join(SET, '命题说明.md'), encoding='utf-8').read().split('\n')
rows = [l for l in M if re.match(r'\| M[35]-\d+', l)]
lab = {}; bad = []
for r in rows:
    c = [x.strip() for x in r.strip('|').split('|')]
    k, p = re.match(r'材料([三五])〔(\d+)〕', c[1]).groups()
    Q = re.match(r'「(.*)」$', c[2]).group(1)
    if not in_text(Q, mats[k][int(p)]):
        bad.append(c[0])
    first = c[3].split('；')[0]
    for key in ['真实原句', '合成', '示意', '真实文件用语']:
        if first.startswith(key):
            lab[key] = lab.get(key, 0) + 1
    if '；示意' in c[3]:
        lab['（另带示意）'] = lab.get('（另带示意）', 0) + 1
print('  合成／示意登记 %d 条，按第一个标注' % len(rows), lab, '原文不在登记段', bad)
