"""核对道理卡里的引文。
「…」后面紧跟【代号 行n】的，到 04_文件原文/代号_*.md 第 n 行找逐字子串；
「…」后面紧跟〔2024二卷 材料六…〕这类真题标记的，到 03_真题/文本/2024_二卷*.txt 全文找（去掉换行）。
比较前去掉引号和空白；引文里的省略号当作跳过。
另外把"道理："后面的卷面句子量一下字数，超过 30 字的列出来。
用法：python3 核对出处.py [卡片.md ...]（不给参数就核道理卡目录下全部）"""
import re, sys, glob, os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
files = sys.argv[1:] or sorted(glob.glob(os.path.join(here, '*.md')))
pat04 = re.compile(r'「([^」]+)」(?:（[^）]*）)?【([0-9A-Za-z\-]+) 行(\d+)】')
patzt = re.compile(r'「([^」]+)」〔(\d{4})\s*(省市|县镇|一卷|二卷|三卷|选调|县级|乡镇)')
strip = lambda s: re.sub(r'[\s“”"‘’\'「」『』]', '', s)

def doc04(code, _c={}):
    if code not in _c:
        m = glob.glob(f'{root}/04_文件原文/{code}_*.md')
        _c[code] = open(m[0], encoding='utf-8').read().split('\n') if m else None
    return _c[code]

def doczt(year, kind, _c={}):
    k = (year, kind)
    if k not in _c:
        m = glob.glob(f'{root}/03_真题/文本/{year}_{kind}*.txt')
        _c[k] = strip(open(m[0], encoding='utf-8').read()) if m else None
    return _c[k]

ok = bad = 0; long_ = []
for f in files:
    name = os.path.basename(f)
    for i, line in enumerate(open(f, encoding='utf-8'), 1):
        for q, code, n in pat04.findall(line):
            lines = doc04(code)
            parts = [strip(p) for p in re.split(r'……|…', q) if strip(p)]
            if lines is None:
                print(f'{name}:{i} ? 【{code}】没有这个文件'); bad += 1; continue
            n = int(n); tgt = strip(lines[n - 1]) if n - 1 < len(lines) else ''
            if all(p in tgt for p in parts):
                ok += 1
            else:
                hits = [j + 1 for j, L in enumerate(lines) if all(p in strip(L) for p in parts)]
                print(f'{name}:{i} ✗ 【{code} 行{n}】「{q[:30]}」' + (f' → 在行 {hits[:3]}' if hits else ' → 全文没有')); bad += 1
        for q, year, kind in patzt.findall(line):
            t = doczt(year, kind)
            parts = [strip(p) for p in re.split(r'……|…', q) if strip(p)]
            if t is None:
                print(f'{name}:{i} ? 没有 {year}{kind} 的文本'); bad += 1; continue
            if all(p in t for p in parts):
                ok += 1
            else:
                print(f'{name}:{i} ✗ 〔{year}{kind}〕「{q[:30]}」 → 材料里没有'); bad += 1
        m = re.match(r'\s*- 道理：(.*)$', line)
        if m:
            s = re.split(r'〔|【', m.group(1))[0]
            s = re.sub(r'[「」\s]', '', s)
            if len(s) > 30:
                long_.append(f'{name}:{i} {len(s)} 字 {s[:36]}')
print(f'核对 {ok + bad} 处，通过 {ok}，有问题 {bad}')
if long_:
    print('超过 30 字的道理句：'); print('\n'.join(long_))
