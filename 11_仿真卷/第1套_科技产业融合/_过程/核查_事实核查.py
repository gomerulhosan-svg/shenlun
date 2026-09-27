# -*- coding: utf-8 -*-
# 第 1 套 事实核查脚本（独立于 核对_作文材料出处.py，不读它的键表）
# 用法（仓库根目录）：python3 11_仿真卷/第1套_科技产业融合/_过程/核查_事实核查.py
# 做五件事：
#   A 作文材料：每个阿拉伯数字向两边扩到来源里能逐字命中的最长片段，片段太短的列出来人工核；
#   B 作文材料：每段最外层引号里的话逐字 grep；
#   C 作文材料：8 字窗口覆盖，列出贴不回任何来源的字（自撰部分：日期、说话人、连接词），供人工核说话人和层级；
#   D 小题材料：真实地名/企业名黑名单扫描；数量词和时间词抽出来，看合成说明里有没有登记；
#   E 参考答案：「材料X〔n〕第 k 句「……」」逐条核句号；范文 5 字窗口贴回本卷材料。
# 来源只用任务单列出的真实材料：溯源结果/母文件_2027.md、第三轮/01_成品/*.md、政府工作报告/*.md。
import re, glob, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SET = os.path.join(ROOT, '11_仿真卷', '第1套_科技产业融合')
SRCFILES = [ROOT + '/10_选材因子/溯源结果/母文件_2027.md'] \
    + sorted(glob.glob(ROOT + '/10_选材因子/第三轮/01_成品/*.md')) \
    + sorted(glob.glob(ROOT + '/10_选材因子/第三轮/01_成品/政府工作报告/*.md'))

def norm(t):
    return re.sub(r'[ \t　\r\n]+', '', t).replace('*', '')

SRC = {os.path.basename(p)[:-3]: norm(open(p, encoding='utf-8').read()) for p in SRCFILES}
CORPUS = '\u0001'.join(SRC.values())
def where(s): return [k for k, v in SRC.items() if s in v]

def parse(path):
    mats, cur = {}, None
    for line in open(path, encoding='utf-8').read().split('\n'):
        m = re.match(r'^#*\s*【材料(.)】', line.strip())
        if m: cur = m.group(1); mats[cur] = {}; continue
        m = re.match(r'^〔(\d+)〕(.*)$', line.strip())
        if m and cur: mats[cur][int(m.group(1))] = m.group(2).strip()
    return mats
MAT = {}
MAT.update(parse(SET + '/_过程/材料_作文.md'))
MAT.update(parse(SET + '/_过程/材料_小题.md'))
ESSAY_M = ['一', '二', '四', '六', '七', '八']

def sents(p):  # 同 08_小题重写/tools/pool.py：按。！？；切，后随的收尾引号跟前一句
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

print('=' * 20, 'A 作文材料数字', '=' * 20)
nA = 0; shortA = []
for m in ESSAY_M:
    for pno, p in MAT[m].items():
        s = norm(p)
        for mt in re.finditer(r'[0-9][0-9.,/]*', s):
            a, b = mt.start(), mt.end(); l, r = a, b; nA += 1
            grow = True
            while grow:
                grow = False
                if r < len(s) and s[l:r + 1] in CORPUS: r += 1; grow = True
                if l > 0 and s[l - 1:r] in CORPUS: l -= 1; grow = True
            ctx = len(s[l:r]) - (b - a)
            if ctx < 6: shortA.append((f'材料{m}〔{pno}〕', s[a:b], s[l:r], s[max(0, a - 8):b + 8]))
print(f'数字 {nA} 个；来源里带 6 字以上上下文命中的 {nA - len(shortA)} 个；下面这些只带很短的上下文命中（多为日期，需人工对说话人和场合）：')
for x in shortA: print('  ', x)

print('=' * 20, 'B 作文材料引语', '=' * 20)
def outer_quotes(s):
    res, depth, st = [], 0, None
    for i, c in enumerate(s):
        if c == '“':
            if depth == 0: st = i + 1
            depth += 1
        elif c == '”':
            depth -= 1
            if depth == 0 and st is not None: res.append(s[st:i]); st = None
    return res
nB = 0
for m in ESSAY_M:
    for pno, p in MAT[m].items():
        for q in outer_quotes(norm(p)):
            nB += 1
            pieces = [x for x in q.split('……') if x]
            # 材料里引号套引号时内层写成‘’，来源里是“”，两种都试
            miss = [x for x in pieces if x not in CORPUS and x.replace('‘', '“').replace('’', '”') not in CORPUS]
            if miss: print(f'  未逐字命中 材料{m}〔{pno}〕：', miss)
print(f'引语 {nB} 处核完（含省略号的按省略号拆开核）')

print('=' * 20, 'C 作文材料自撰部分（8 字窗口贴不回来源的字）', '=' * 20)
N = 8; grams = set()
for v in SRC.values():
    for i in range(len(v) - N + 1): grams.add(hash(v[i:i + N]))
for m in ESSAY_M:
    for pno, p in MAT[m].items():
        s = norm(p); cov = [False] * len(s)
        for i in range(len(s) - N + 1):
            if hash(s[i:i + N]) in grams:
                for j in range(i, i + N): cov[j] = True
        spans, i = [], 0
        while i < len(s):
            if not cov[i]:
                j = i
                while j < len(s) and not cov[j]: j += 1
                if j - i >= 2: spans.append(s[i:j])
                i = j
            else: i += 1
        if spans: print(f'  材料{m}〔{pno}〕 覆盖{sum(cov) * 100 // len(s)}%：', ' | '.join(spans))

print('=' * 20, 'D 小题材料', '=' * 20)
BLACK = ('广东 粤 深圳 广州 佛山 东莞 珠海 惠州 中山 江门 湛江 茂名 肇庆 清远 韶关 河源 梅州 汕头 汕尾 潮州 揭阳 云浮 阳江 '
         '南沙 前海 横琴 大湾区 香港 澳门 珠三角 顺德 宝安 番禺 天河 黄埔 光明 松山湖 北京 上海 亿航 大疆 美团 顺丰 丰翼 '
         '峰飞 小鹏 汇天 华为 腾讯 粤省事 粤医智影 开放广东 湾擎 全省 全国').split()
note = open(SET + '/_过程/小题材料_合成说明.md', encoding='utf-8').read()
reg = note[note.index('### 2.2'):note.index('### 2.3')] + note[note.index('### 3.4'):note.index('### 3.5')]
for m in ['三', '五']:
    t = ''.join(MAT[m].values())
    print(f'  材料{m} 黑名单命中：', [(w, t.count(w)) for w in BLACK if w in t] or '无')
    for pno, p in MAT[m].items():
        qty = re.findall(r'[0-9][0-9.]*万?(?:多|余)?(?:个|家|项|张|人次|小时|分钟|架次|岁|%)?|[几上两三十百千万]+(?:多|余)?(?:个|家|批|秒钟|分钟|小时|天|成|架次|岁|部门|件)|大半天|半天|一个多月|每季度|三年', p)
        tim = re.findall(r'今年以来|今年汛期|今年3月|年初|近日|这两年|去年', p)
        realsent = '深化拓展“人工智能+”，在公共服务领域充分挖掘所有可能的应用场景，支持人工智能深度赋能千行百业、造福千家万户'
        key = lambda x: re.sub(r'[多余\s]', '', x)
        unreg = [x for x in qty + tim if x not in ('千家', '几个', '12345') and key(x) not in key(reg)]
        if qty or tim: print(f'  材料{m}〔{pno}〕 数量：{qty} 时间：{tim} → 2.2/3.4 清单未登记：{unreg}')

print('=' * 20, 'E 参考答案', '=' * 20)
ans = open(SET + '/参考答案与解析.md', encoding='utf-8').read()
pat = re.compile(r'(材料([一二三四五六七八]))?〔(\d+)〕(第\s*(\d+)(?:\s*[–-]\s*(\d+))?\s*句)?(「((?:[^「」]|「[^「」]*」)*)」)?')
cur = None; nE = 0; badE = []
for ln, line in enumerate(ans.split('\n'), 1):
    if line.startswith('## 问题一'): cur = '三'
    elif line.startswith('## 问题二'): cur = '五'
    elif line.startswith('## 问题三'): cur = None
    last = None
    for mm in pat.finditer(line):
        mat = mm.group(2) or last or cur
        if mm.group(2): last = mm.group(2)
        if not mat or not mm.group(8): continue
        pno = int(mm.group(3)); para = MAT[mat].get(pno)
        if para is None: badE.append((ln, f'材料{mat}没有〔{pno}〕')); continue
        ss = sents(para)
        if mm.group(5):
            k = int(mm.group(5)); k2 = int(mm.group(6) or k)
            target = ''.join(ss[k - 1:k2]) if k2 <= len(ss) else ''
        else: target = para
        nE += 1
        for pc in [x for x in re.split(r'……|…', mm.group(8)) if x.strip()]:
            if pc.strip() not in target:
                loc = [i + 1 for i, s in enumerate(ss) if pc.strip() in s]
                badE.append((ln, f'材料{mat}〔{pno}〕第{mm.group(5)}句对不上，实际在第{loc}句', pc[:40]))
print(f'带引文的出处 {nE} 条，对不上 {len(badE)} 条', badE)
a = ans.index('### 作文'); b = ans.index('### 逐句解析')
essay = [norm(l[1:]) for l in ans[a:b].split('\n') if l.startswith('>') and l[1:].strip()]
allm = ''.join(norm(p) for mm in MAT.values() for p in mm.values())
g5 = set(allm[i:i + 5] for i in range(len(allm) - 4))
out = []
for para in essay:
    cov = [False] * len(para)
    for i in range(len(para) - 4):
        if para[i:i + 5] in g5:
            for j in range(i, i + 5): cov[j] = True
    i = 0
    while i < len(para):
        if not cov[i]:
            j = i
            while j < len(para) and not cov[j]: j += 1
            if j - i >= 2: out.append(para[i:j])
            i = j
        else: i += 1
print('范文里贴不回本卷材料的片段（应只有连接词和自造架子）：', out)
print('范文字数', sum(len(x) for x in essay))
