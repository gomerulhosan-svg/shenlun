#!/usr/bin/env python3
"""选例因子检验：揭盲分析。判定标准照 10_选材因子/选例因子_预登记.md，不改。

python3 10_选材因子/tools/select_analysis.py <底表目录> [输出.md] [--perm N] [--seed S]

<底表目录> 下要有：
- blind/<卷>.json   段 id 和原文（select_blind.py 生成）
- key/<卷>.json     每段的 标 / 用率 / 对应材料 / 快照 / 位置 / 字数
- out/cases_<卷>.json、out/labelsA_<卷>.json、out/labelsB_<卷>.json   例子和两位标注员的标
卷面题干取自 10_选材因子/溯源包/<卷>_材料与题干.md 末尾的"### 题干"。
只用标准库（本机没有 numpy / statsmodels）；条件逻辑回归是手写的精确条件似然 + 牛顿法。

口径（报告开头也会写）：
1. 例子的选用状态：覆盖的段里有任一段"选用"→选用；全部"未选"→未选；其余（只有"部分"或"部分+未选"）剔除。
2. 去重：只在可比较的例子（选用/未选）里做。按卷序（PAPERS）、文章号、例子号依次处理，
   一个例子的文字（逐段取 8 字串）有 ≥80% 已出现在"别的文章（别卷或同卷另一快照）里已保留的例子"中，就算重复，去掉。
   敏感性：改成"选用的副本优先保留"再跑一遍主结果。
3. 文章内置换检验：层 = (卷, 文章)，只用同时有选用和未选例子的层；每次在层内打乱选用标签（保持每层选用数），
   统计量 = 选用例子的特征和。它和 Mantel-Haenszel 加权的层内差值 Σw(p1-p0)/Σw（w = n1·n0/n）是同一个检验，
   报告里的"文章内差值"就是这个加权差值。p 值 = (1+极端次数)/(1+置换次数)。
"""
import json
import math
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
PACK = os.path.join(ROOT, '10_选材因子', '溯源包')
PAPERS = ['2022县级', '2023县级', '2024一卷', '2024二卷', '2024选调',
          '2025省市', '2025县镇', '2025选调', '2026省市', '2026县镇']
PUNCT = r'[\s“”"‘’\'「」『』《》〈〉（）()【】、，。；：！？,.;:!?—…·\-]'
NG = 8
DUP_TH = 0.8
CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}

# 特征：名字 -> (取值函数, 预期方向)。方向 +1 = 预期选用组更高，-1 = 更低，0 = 对照项不设方向。
FEATS = [
    ('出彩_显式', lambda L: L['出彩_显式'] == 1, +1),
    ('出彩_实质≥1', lambda L: L['出彩_实质'] >= 1, +1),
    ('出彩_实质=2', lambda L: L['出彩_实质'] == 2, +1),
    ('可复制_显式', lambda L: L['可复制_显式'] == 1, +1),
    ('可复制_实质=2', lambda L: L['可复制_实质'] == 2, +1),
    ('独特禀赋', lambda L: L['独特禀赋'] == 1, -1),
    ('收益类数≥2', lambda L: len(set(L['收益类'])) >= 2, +1),
    ('资源转化', lambda L: L['资源转化'] == 1, +1),
    ('约束突破', lambda L: L['约束突破'] == 1, +1),
    ('量化成效', lambda L: L['量化成效'] == 1, 0),
    ('人物引语', lambda L: L['人物引语'] == 1, 0),
    ('讲难点', lambda L: L['讲难点'] == 1, 0),
    ('新事物', lambda L: L['新事物'] == 1, 0),
    ('贴合度=2', lambda L: L['贴合度'] == 2, 0),
]
FNAMES = [f[0] for f in FEATS]
FDIR = {f[0]: f[2] for f in FEATS}
# 补充：0–2 分和收益类数的均值，≥1 的阈值
SUPP = [
    ('可复制_实质≥1', lambda L: L['可复制_实质'] >= 1, +1, 'rate'),
    ('收益类数≥1', lambda L: len(set(L['收益类'])) >= 1, +1, 'rate'),
    ('出彩_实质 均分', lambda L: L['出彩_实质'], +1, 'mean'),
    ('可复制_实质 均分', lambda L: L['可复制_实质'], +1, 'mean'),
    ('收益类数 均值', lambda L: len(set(L['收益类'])), +1, 'mean'),
    ('贴合度 均分', lambda L: L['贴合度'], 0, 'mean'),
]
MAIN = ['出彩_显式', '出彩_实质≥1', '出彩_实质=2', '可复制_实质=2', '独特禀赋', '收益类数≥2', '资源转化', '约束突破',
        '量化成效', '人物引语']
HYP = [
    ('H1', '被选的例子更"出彩"', ['出彩_显式', '出彩_实质≥1', '出彩_实质=2'], 'any'),
    ('H2', '被选的例子更"可复制"、更少依赖独特禀赋', ['可复制_实质=2', '独特禀赋'], 'all'),
    ('H3', '被选的例子更"一石多鸟"', ['收益类数≥2'], 'all'),
    ('H4', '被选的例子更多"资源转化"或"约束突破"', ['资源转化', '约束突破'], 'any'),
]


def norm(s):
    return re.sub(PUNCT, '', s)


def grams(t):
    return {t[i:i + NG] for i in range(len(t) - NG + 1)}


# ---------------------------------------------------------------- 读数据
def roles_of(paper):
    t = open(os.path.join(PACK, paper + '_材料与题干.md'), encoding='utf-8').read()
    stem = t.split('### 题干', 1)[1]
    out = {}
    for q, name in (('问题一', '问题一材料'), ('问题二', '问题二材料')):
        m = re.search(r'\*\*' + q + r'\*\*(.*?)(?=\*\*问题|\Z)', stem, re.S)
        for n in re.findall(r'材料\s*(\d+)', m.group(1)):
            out[int(n)] = name
    return out


def load(d):
    cases = []
    for p in PAPERS:
        blind = json.load(open(os.path.join(d, 'blind', p + '.json'), encoding='utf-8'))
        text = {s['id']: s['文'] for a in blind['文章'] for s in a['段']}
        key = json.load(open(os.path.join(d, 'key', p + '.json'), encoding='utf-8'))['段']
        cs = json.load(open(os.path.join(d, 'out', 'cases_%s.json' % p), encoding='utf-8'))['例子']
        la = json.load(open(os.path.join(d, 'out', 'labelsA_%s.json' % p), encoding='utf-8'))
        lb = json.load(open(os.path.join(d, 'out', 'labelsB_%s.json' % p), encoding='utf-8'))
        roles = roles_of(p)
        for c in cs:
            segs = c['段']
            tags = [key[s]['标'] for s in segs]
            st = '选用' if '选用' in tags else ('未选' if all(t == '未选' for t in tags) else '部分')
            arts = sorted({s.split('-')[0] for s in segs})
            role = ''
            if st == '选用':
                best = max((s for s in segs if key[s]['标'] == '选用'), key=lambda s: key[s]['用率'])
                m = re.match(r'材料([一二三四五六七八九十]+)', key[best]['对应材料'])
                role = roles.get(CN.get(m.group(1), 0), '作文材料') if m else '作文材料'
            n_chars = sum(key[s]['字数'] for s in segs)
            art_key = [v for k, v in key.items() if k.split('-')[0] == arts[0]]
            cases.append({
                'paper': p, 'pi': PAPERS.index(p), 'id': c['id'], 'art': arts[0], 'unit': (p, arts[0]),
                'segs': segs, 'st': st, 'role': role, 'A': la[c['id']], 'B': lb[c['id']],
                'len': n_chars, 'nseg': len(segs),
                'pos': statistics.mean(key[s]['位置'] for s in segs),
                'maxuse': max(key[s]['用率'] for s in segs),
                'art_match': sum(v['用率'] * v['字数'] for v in art_key if v['标'] == '选用'),
                'art_maxuse': max(v['用率'] for v in art_key),
                'ntexts': [norm(text[s]) for s in segs], 'multi_art': len(arts) > 1,
            })
    return cases


# ---------------------------------------------------------------- 去重
def dedup(cases, prefer_selected=False):
    """返回 (保留的例子, 去掉的例子[(例子, 覆盖率, 覆盖它的例子)], 部分重叠数)"""
    rank = {'选用': 0, '未选': 1}
    order = sorted(cases, key=lambda c: ((rank[c['st']] if prefer_selected else 0), c['pi'], c['art'], c['id']))
    pool = defaultdict(set)   # 8 字串 -> 已保留例子的下标
    kept, dropped, partial = [], [], 0
    for c in order:
        tot = cov = 0
        hit = Counter()
        for t in c['ntexts']:
            tot += len(t)
            if len(t) < NG:
                continue
            mark = [False] * len(t)
            for i in range(len(t) - NG + 1):
                owners = [k for k in pool.get(t[i:i + NG], ()) if kept[k]['unit'] != c['unit']]
                if owners:
                    for k in owners:
                        hit[k] += 1
                    for j in range(i, i + NG):
                        mark[j] = True
            cov += sum(mark)
        r = cov / tot if tot else 0.0
        if r >= DUP_TH:
            dropped.append((c, r, kept[hit.most_common(1)[0][0]]))
            continue
        if r >= 0.3:
            partial += 1
        idx = len(kept)
        kept.append(c)
        for t in c['ntexts']:
            for g in grams(t):
                pool[g].add(idx)
    kept.sort(key=lambda c: (c['pi'], c['art'], c['id']))
    return kept, dropped, partial


# ---------------------------------------------------------------- 统计
def kappa(xs, ys):
    n = len(xs)
    if n == 0:
        return None, None
    cats = sorted(set(xs) | set(ys))
    po = sum(1 for a, b in zip(xs, ys) if a == b) / n
    pe = sum((xs.count(k) / n) * (ys.count(k) / n) for k in cats)
    return po, (None if pe >= 1 else (po - pe) / (1 - pe))


def wkappa(xs, ys, cats=(0, 1, 2)):
    """线性加权 kappa"""
    n = len(xs)
    if n == 0:
        return None
    k = len(cats)
    w = lambda i, j: 1 - abs(i - j) / (k - 1)
    ix = {c: i for i, c in enumerate(cats)}
    po = sum(w(ix[a], ix[b]) for a, b in zip(xs, ys)) / n
    px = [xs.count(c) / n for c in cats]
    py = [ys.count(c) / n for c in cats]
    pe = sum(w(i, j) * px[i] * py[j] for i in range(k) for j in range(k))
    return None if pe >= 1 else (po - pe) / (1 - pe)


def perm_test(items, fns, nperm, seed):
    """items: [(层, 是否选用, 标注字典)]；fns: [(名字, 取值函数, 方向)]。
    返回 {名字: 结果}，并附 '_meta'。只有同时含选用和未选的层参加置换。"""
    F = len(fns)
    allsel = [[] for _ in range(F)]
    allun = [[] for _ in range(F)]
    strata = defaultdict(list)
    for u, s, L in items:
        v = [float(fn(L)) for _, fn, *_ in fns]
        strata[u].append((s, v))
        for f in range(F):
            (allsel if s else allun)[f].append(v[f])
    part = [(u, rows) for u, rows in strata.items()
            if any(s for s, _ in rows) and any(not s for s, _ in rows)]
    obs = [0.0] * F
    exp_ = [0.0] * F
    W = 0.0
    s1 = [0.0] * F
    s0 = [0.0] * F
    n1t = n0t = 0
    prep = []
    for u, rows in part:
        n = len(rows)
        n1 = sum(1 for s, _ in rows if s)
        n0 = n - n1
        W += n1 * n0 / n
        n1t += n1
        n0t += n0
        X = [v for _, v in rows]
        for f in range(F):
            T = sum(x[f] for x in X)
            S = sum(v[f] for s, v in rows if s)
            obs[f] += S
            exp_[f] += n1 * T / n
            s1[f] += S
            s0[f] += T - S
        prep.append((n, n1, X))
    res = {'_meta': {'层数': len(part), '选用': n1t, '未选': n0t,
                     '全_选用': len(allsel[0]) if F else 0, '全_未选': len(allun[0]) if F else 0}}
    if not part:
        for f, (name, *_r) in enumerate(fns):
            res[name] = None
        return res
    rng = random.Random(seed)
    ge = [0] * F
    le = [0] * F
    ab = [0] * F
    dev = [abs(obs[f] - exp_[f]) - 1e-9 for f in range(F)]
    rng_sample = rng.sample
    for _ in range(nperm):
        acc = [0.0] * F
        for n, n1, X in prep:
            for i in rng_sample(range(n), n1):
                x = X[i]
                for f in range(F):
                    acc[f] += x[f]
        for f in range(F):
            a = acc[f]
            if a >= obs[f] - 1e-9:
                ge[f] += 1
            if a <= obs[f] + 1e-9:
                le[f] += 1
            if abs(a - exp_[f]) >= dev[f]:
                ab[f] += 1
    for f, (name, fn, d, *_r) in enumerate(fns):
        mh = (obs[f] - exp_[f]) / W
        p1 = None
        if d > 0:
            p1 = (1 + ge[f]) / (1 + nperm)
        elif d < 0:
            p1 = (1 + le[f]) / (1 + nperm)
        res[name] = {
            'all_sel': statistics.mean(allsel[f]) if allsel[f] else None,
            'all_un': statistics.mean(allun[f]) if allun[f] else None,
            'in_sel': s1[f] / n1t, 'in_un': s0[f] / n0t, 'mh': mh,
            'p2': (1 + ab[f]) / (1 + nperm), 'p1': p1, 'dir': d,
        }
    return res


# ---------------------------------------------------------------- 条件逻辑回归（按文章分层，精确条件似然）
def _solve(M, b):
    n = len(M)
    A = [row[:] + [b[i]] for i, row in enumerate(M)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-12:
            raise ZeroDivisionError
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c:
                f = A[r][c] / A[c][c]
                for k in range(c, n + 1):
                    A[r][k] -= f * A[c][k]
    return [A[i][n] / A[i][i] for i in range(n)]


def _inv(M):
    n = len(M)
    cols = [_solve(M, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def clogit(strata, P, maxit=60):
    """strata: [[(y, x向量), ...], ...]。返回 (beta, se, loglik, 收敛, 迭代次数)。
    每层的分母 = 所有同样大小子集 exp(Ση) 之和，用递推算，连同一阶、二阶导数。"""
    prep = []
    for rows in strata:
        m = sum(y for y, _ in rows)
        n = len(rows)
        if m == 0 or m == n:
            continue
        mu = [sum(x[k] for _, x in rows) / n for k in range(P)]
        X = [[x[k] - mu[k] for k in range(P)] for _, x in rows]
        Y = [y for y, _ in rows]
        if m > n / 2:   # 取补集，递推更短
            X = [[-v for v in x] for x in X]
            Y = [1 - y for y in Y]
            m = n - m
        prep.append((X, Y, m))

    def evaluate(beta):
        ll = 0.0
        g = [0.0] * P
        H = [[0.0] * P for _ in range(P)]
        for X, Y, m in prep:
            B = [1.0] + [0.0] * m
            dB = [[0.0] * P for _ in range(m + 1)]
            d2 = [[[0.0] * P for _ in range(P)] for _ in range(m + 1)]
            for x in X:
                w = math.exp(sum(b * v for b, v in zip(beta, x)))
                for j in range(m, 0, -1):
                    b0, db0, d20 = B[j - 1], dB[j - 1], d2[j - 1]
                    if b0 == 0.0:
                        continue
                    B[j] += w * b0
                    dBj = dB[j]
                    for k in range(P):
                        dBj[k] += w * (x[k] * b0 + db0[k])
                    d2j = d2[j]
                    for k in range(P):
                        xk = x[k]
                        rowj, row0 = d2j[k], d20[k]
                        for l in range(P):
                            rowj[l] += w * (xk * x[l] * b0 + xk * db0[l] + db0[k] * x[l] + row0[l])
            Bm, dBm, d2m = B[m], dB[m], d2[m]
            xs = [sum(x[k] for x, y in zip(X, Y) if y) for k in range(P)]
            ll += sum(b * v for b, v in zip(beta, xs)) - math.log(Bm)
            for k in range(P):
                g[k] += xs[k] - dBm[k] / Bm
                for l in range(P):
                    H[k][l] -= d2m[k][l] / Bm - dBm[k] * dBm[l] / Bm / Bm
        return ll, g, H

    beta = [0.0] * P
    ll, g, H = evaluate(beta)
    ll0 = ll
    conv = False
    it = 0
    for it in range(1, maxit + 1):
        try:
            step = _solve([[-h for h in row] for row in H], g)
        except ZeroDivisionError:
            break
        t = 1.0
        while True:
            nb = [b + t * s for b, s in zip(beta, step)]
            try:
                nll, ng, nH = evaluate(nb)
            except OverflowError:
                nll = -math.inf
            if nll >= ll - 1e-10 or t < 1e-6:
                break
            t /= 2
        if nll == -math.inf:
            break
        done = abs(nll - ll) < 1e-9
        beta, ll, g, H = nb, nll, ng, nH
        if done:
            conv = True
            break
    try:
        cov = _inv([[-h for h in row] for row in H])
        se = [math.sqrt(cov[k][k]) if cov[k][k] > 0 else float('nan') for k in range(P)]
    except ZeroDivisionError:
        se = [float('nan')] * P
    return beta, se, ll, ll0, conv, it, len(prep)


# ---------------------------------------------------------------- 输出格式
def pc(x):
    return '—' if x is None else '%.1f%%' % (100 * x)


def pp(x):
    return '—' if x is None else '%+.1f' % (100 * x)


def pv(x):
    if x is None:
        return '—'
    return '<0.001' if x < 0.001 else '%.3f' % x


def num(x, k=2):
    return '—' if x is None else ('%.' + str(k) + 'f') % x


def table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)


def feat_table(res, names, mean_names=()):
    m = res['_meta']
    head = ['特征', '预期', '全部·选用组', '全部·未选组', '全部·差(pp)',
            '文章内·选用组', '文章内·未选组', '文章内差值(MH, pp)', 'p 双侧', 'p 单侧(预期方向)']
    rows = []
    for n in names:
        r = res.get(n)
        d = {1: '↑', -1: '↓', 0: '对照'}[FDIR.get(n, dict((s[0], s[2]) for s in SUPP).get(n, 0))]
        if r is None:
            rows.append([n, d] + ['—'] * 8)
            continue
        if n in mean_names:
            rows.append([n, d, num(r['all_sel']), num(r['all_un']), '%+.2f' % (r['all_sel'] - r['all_un']),
                         num(r['in_sel']), num(r['in_un']), '%+.2f' % r['mh'], pv(r['p2']), pv(r['p1'])])
        else:
            rows.append([n, d, pc(r['all_sel']), pc(r['all_un']), pp(r['all_sel'] - r['all_un']),
                         pc(r['in_sel']), pc(r['in_un']), pp(r['mh']), pv(r['p2']), pv(r['p1'])])
    cap = ('全部：选用 %d 个、未选 %d 个例子；文章内：%d 篇文章参加置换，其中选用 %d 个、未选 %d 个。'
           % (m['全_选用'], m['全_未选'], m['层数'], m['选用'], m['未选']))
    return cap + '\n\n' + table(head, rows)


def fns_for(names, who):
    d = {f[0]: f for f in FEATS}
    d.update({s[0]: s for s in SUPP})
    return [(n, (lambda fn: (lambda L: fn(L[who])))(d[n][1]), d[n][2]) for n in names]


def items_of(cases, filt=None):
    return [(c['unit'], c['st'] == '选用', c) for c in cases if (filt is None or filt(c))]


# ---------------------------------------------------------------- 主程序
def main():
    args = [a for a in sys.argv[1:]]
    nperm, seed = 10000, 20260928
    if '--perm' in args:
        i = args.index('--perm')
        nperm = int(args[i + 1])
        del args[i:i + 2]
    if '--seed' in args:
        i = args.index('--seed')
        seed = int(args[i + 1])
        del args[i:i + 2]
    d = args[0]
    outp = args[1] if len(args) > 1 else os.path.join(d, '分析结果.md')
    cases = load(d)
    st_all = Counter(c['st'] for c in cases)
    comp = [c for c in cases if c['st'] != '部分']
    kept, dropped, partial = dedup(comp)
    kept2, dropped2, _ = dedup(comp, prefer_selected=True)
    out = []
    W = out.append
    W('# 选例因子检验：揭盲分析结果')
    W('')
    W('脚本：`10_选材因子/tools/select_analysis.py`（可重跑）。判定标准照 `选例因子_预登记.md`，没有改。'
      '置换次数 %d，随机种子 %d。' % (nperm, seed))
    W('')
    W('## 0. 口径')
    W('')
    W('- **例子的选用状态**：例子覆盖的段里有任一段"选用"（用率 ≥30%）算选用；全部"未选"（<10%）算未选；其余剔除。')
    W('- **去重**：只在选用/未选例子里做。按卷序（2022县级→2026县镇）、文章号、例子号依次过，'
      '一个例子的文字（逐段取 8 字连续串，去标点）有 ≥80%% 已出现在别的文章（别卷或同卷的另一个转载快照）里'
      '已保留的例子中，就算重复，去掉；保留的是先出现的那份。敏感性分析改成"选用的副本优先保留"。'
      '一段里挤着几个例子、两卷的标注员切法不同时，按文字去重会把后一卷多切出来的例子一并去掉，这是按段文字去重的代价。')
    W('- **文章内置换检验**：层 = (卷, 文章)，只有同时含选用和未选例子的文章参加；每次只在文章内打乱选用标签'
      '（每篇的选用数不变），统计量 = 选用例子的特征和，%d 次。这个检验和"文章内差值"'
      '（Mantel-Haenszel 加权的层内差 Σw·(p选−p未)/Σw，w = n选·n未/n）一一对应，所以判"≥10 个百分点"用的就是这个加权差值。'
      'p 值 = (1+至少一样极端的次数)/(1+%d)。双侧 p 用于判定；有预期方向的特征另报单侧 p。' % (nperm, nperm))
    W('- **"全部"列**：所有选用/未选例子的原始比例，不控制文章，只作描述。')
    W('- **判定规则**（把预登记的文字落成可执行的规则，在看结果前写进脚本）：')
    W('  - 主判定用甲的标（甲切例子并先标，乙独立复标用来算一致率）。')
    W('  - 单项特征"达标" = 文章内差值方向符合预期、绝对值 ≥10 个百分点、双侧 p < 0.05。')
    W('  - 单项特征判"支持" = 甲的标达标，且在贴合度=2（按甲）的例子里也达标，且乙的标和两人一致子集的文章内差值方向相同。')
    W('  - kappa < 0.4 → 该项"证据不足"（预登记：不下结论）。')
    W('  - 全样本达标但贴合度=2 子集只是方向相同、差值 ≥10pp 而 p ≥ 0.05，或乙/一致子集方向相反 → "证据不足"；'
      '全样本不达标（差值不到 10pp、p ≥ 0.05 或方向相反）→ "不支持"；全样本达标但贴合度=2 子集差值不到 10pp 或方向相反 → "不支持"（被贴合度解释）。')
    W('  - H1、H4 任一指标支持即支持（另报 Bonferroni 校正后是否仍显著）；H2 要可复制和独特禀赋两项都支持；'
      '一项支持一项不支持判"不支持"并写明分项。')
    W('')

    # ------------------------------------------------ 1. 样本
    W('## 1. 样本量')
    W('')
    per = defaultdict(Counter)
    for c in cases:
        per[c['paper']][c['st']] += 1
    for c, r, o in dropped:
        per[c['paper']]['去重' + c['st']] += 1
    res_meta = perm_test(items_of(kept), fns_for(['出彩_显式'], 'A'), 0, seed)['_meta']
    by_unit = defaultdict(list)
    for c in kept:
        by_unit[c['unit']].append(c['st'])
    part_units = {u for u, s in by_unit.items() if '选用' in s and '未选' in s}
    rows = []
    for p in PAPERS:
        k = [c for c in kept if c['paper'] == p]
        pu = [u for u in part_units if u[0] == p]
        rows.append([p, sum(per[p][s] for s in ('选用', '未选', '部分')), per[p]['选用'], per[p]['未选'], per[p]['部分'],
                     per[p]['去重选用'] + per[p]['去重未选'], sum(1 for c in k if c['st'] == '选用'),
                     sum(1 for c in k if c['st'] == '未选'), len({c['unit'] for c in k}), len(pu),
                     sum(1 for c in k if c['unit'] in part_units and c['st'] == '选用')])
    tot = [sum(r[i] for r in rows) for i in range(1, len(rows[0]))]
    rows.append(['合计'] + tot)
    W(table(['卷', '例子', '选用', '未选', '部分(剔除)', '去重去掉', '留下·选用', '留下·未选', '有例子的文章',
             '参加置换的文章', '其中选用例子'], rows))
    W('')
    xp = Counter()
    conflict = 0
    for c, r, o in dropped:
        xp['同卷另一快照' if o['paper'] == c['paper'] else '跨卷'] += 1
        if o['st'] != c['st']:
            conflict += 1
    pairs = Counter((o['paper'], c['paper']) for c, r, o in dropped if o['paper'] != c['paper'])
    W('- 例子共 %d 个：选用 %d、未选 %d、部分 %d（剔除）。' % (len(cases), st_all['选用'], st_all['未选'], st_all['部分']))
    W('- 去重去掉 %d 个（选用 %d、未选 %d）：跨卷重复 %d 个，同卷不同转载快照重复 %d 个；'
      '其中 %d 个的保留副本选用状态和它不同（保留的是先出现的那份）。另有 %d 个例子和别处部分重叠（30%%–80%%），保留。'
      % (len(dropped), sum(1 for c, _, _ in dropped if c['st'] == '选用'), sum(1 for c, _, _ in dropped if c['st'] == '未选'),
         xp['跨卷'], xp['同卷另一快照'], conflict, partial))
    W('- 跨卷去重最多的卷对：' + '；'.join('%s→%s %d 个' % (a, b, n) for (a, b), n in pairs.most_common(8)) + '。')
    W('- 分析样本：%d 个例子（选用 %d、未选 %d），分布在 %d 篇文章；参加文章内置换的文章 %d 篇，含选用 %d 个、未选 %d 个。'
      % (len(kept), sum(1 for c in kept if c['st'] == '选用'), sum(1 for c in kept if c['st'] == '未选'),
         len(by_unit), res_meta['层数'], res_meta['选用'], res_meta['未选']))
    W('')

    # ------------------------------------------------ 2. 一致率
    W('## 2. 两位标注员的一致率')
    W('')
    W('分析样本（去重后的选用+未选例子，n=%d）和全部例子（n=%d）各算一遍。判定用分析样本的 kappa。' % (len(kept), len(cases)))
    W('')
    kap = {}
    rows = []
    for name, fn, _d in FEATS + [(s[0], s[1], s[2]) for s in SUPP if s[3] == 'rate']:
        xa = [int(fn(c['A'])) for c in kept]
        xb = [int(fn(c['B'])) for c in kept]
        po, k = kappa(xa, xb)
        ya = [int(fn(c['A'])) for c in cases]
        yb = [int(fn(c['B'])) for c in cases]
        po2, k2 = kappa(ya, yb)
        kap[name] = k
        rows.append([name, '%d / %d' % (sum(xa), sum(xb)), num(po), num(k), num(po2), num(k2),
                     '<0.4 不下结论' if (k is None or k < 0.4) else ''])
    W(table(['特征', '甲/乙 为 1 的个数(分析样本)', '一致率', 'kappa', '一致率(全部)', 'kappa(全部)', '备注'], rows))
    W('')
    rows = []
    for name in ('出彩_实质', '可复制_实质', '贴合度'):
        xa = [c['A'][name] for c in kept]
        xb = [c['B'][name] for c in kept]
        po, k = kappa(xa, xb)
        rows.append([name + '（0/1/2 三档）', num(po), num(k), num(wkappa(xa, xb))])
    xa = [min(len(set(c['A']['收益类'])), 3) for c in kept]
    xb = [min(len(set(c['B']['收益类'])), 3) for c in kept]
    po, k = kappa(xa, xb)
    rows.append(['收益类数（0/1/2/3+ 四档）', num(po), num(k), num(wkappa(xa, xb, (0, 1, 2, 3)))])
    W(table(['原始分值', '完全一致率', 'kappa', '线性加权 kappa'], rows))
    W('')

    # ------------------------------------------------ 3. 主结果
    W('## 3. 选用组 vs 未选组')
    W('')
    W('### 3.1 甲的标（主判定）')
    W('')
    rA = perm_test(items_of(kept), fns_for(FNAMES, 'A'), nperm, seed)
    W(feat_table(rA, FNAMES))
    W('')
    W('### 3.2 乙的标')
    W('')
    rB = perm_test(items_of(kept), fns_for(FNAMES, 'B'), nperm, seed)
    W(feat_table(rB, FNAMES))
    W('')
    W('### 3.3 两人一致的子集（每项特征只留甲乙判得一样的例子）')
    W('')
    rows = []
    rAg = {}
    for name, fn, dd in FEATS:
        sub = [c for c in kept if fn(c['A']) == fn(c['B'])]
        r = perm_test(items_of(sub), [(name, (lambda f: lambda L: f(L['A']))(fn), dd)], nperm, seed)
        rAg[name] = r
        x = r[name]
        m = r['_meta']
        if x is None:
            rows.append([name, len(sub), m['层数'], '—', '—', '—', '—', '—', '—', '—'])
            continue
        rows.append([name, len(sub), '%d（%d/%d）' % (m['层数'], m['选用'], m['未选']), pc(x['all_sel']), pc(x['all_un']),
                     pc(x['in_sel']), pc(x['in_un']), pp(x['mh']), pv(x['p2']), pv(x['p1'])])
    W(table(['特征', '一致例子数', '参加文章（选用/未选）', '全部·选用组', '全部·未选组', '文章内·选用组', '文章内·未选组',
             '文章内差值(pp)', 'p 双侧', 'p 单侧'], rows))
    W('')
    W('### 3.4 补充：0–2 分、收益类数的均值和 ≥1 阈值（甲 / 乙）')
    W('')
    sn = [s[0] for s in SUPP]
    mn = [s[0] for s in SUPP if s[3] == 'mean']
    W('甲：')
    W('')
    W(feat_table(perm_test(items_of(kept), fns_for(sn, 'A'), nperm, seed), sn, mn))
    W('')
    W('乙：')
    W('')
    W(feat_table(perm_test(items_of(kept), fns_for(sn, 'B'), nperm, seed), sn, mn))
    W('')
    W('均值行的差值单位是分（不是百分点）。')
    W('')

    # ------------------------------------------------ 4. 混杂
    W('## 4. 混杂检查')
    W('')
    W('### 4.1 只看贴合度=2（按甲）的例子')
    W('')
    fit2 = lambda c: c['A']['贴合度'] == 2
    rF = perm_test(items_of(kept, fit2), fns_for(FNAMES[:-1], 'A'), nperm, seed)
    W('甲的标：')
    W('')
    W(feat_table(rF, FNAMES[:-1]))
    W('')
    rFB = perm_test(items_of(kept, fit2), fns_for(FNAMES[:-1], 'B'), nperm, seed)
    W('乙的标（同一批例子）：')
    W('')
    W(feat_table(rFB, FNAMES[:-1]))
    W('')

    W('### 4.2 段长和位置')
    W('')
    sel = [c for c in kept if c['st'] == '选用']
    un = [c for c in kept if c['st'] == '未选']

    def q(xs):
        xs = sorted(xs)
        if not xs:
            return '—'
        qs = statistics.quantiles(xs, n=4) if len(xs) > 1 else [xs[0]] * 3
        return '%.0f [%.0f, %.0f]' % (qs[1], qs[0], qs[2]) if max(xs) > 2 else '%.2f [%.2f, %.2f]' % (qs[1], qs[0], qs[2])

    cont = [('字数', lambda c: c['len'], 0), ('log 字数', lambda c: math.log(c['len']), 0),
            ('覆盖段数', lambda c: c['nseg'], 0), ('位置（0=篇首，1=篇尾）', lambda c: c['pos'], 0)]
    rC = perm_test([(c['unit'], c['st'] == '选用', c) for c in kept], cont, nperm, seed)
    rows = []
    for name, fn, _ in cont:
        r = rC[name]
        rows.append([name, q([fn(c) for c in sel]), q([fn(c) for c in un]), num(r['in_sel']), num(r['in_un']),
                     '%+.2f' % r['mh'], pv(r['p2'])])
    W(table(['变量', '选用组 中位数 [四分位]', '未选组 中位数 [四分位]', '文章内·选用组均值', '文章内·未选组均值',
             '文章内差值(MH)', 'p 双侧'], rows))
    W('')
    med = statistics.median(c['len'] for c in kept)
    W('字数中位数（分析样本）= %.0f 字；位置用例子所覆盖各段的平均相对位置，"前半" = 位置 < 0.5。' % med)
    W('')
    strat = [('字数 > 中位数', lambda c: c['len'] > med), ('字数 ≤ 中位数', lambda c: c['len'] <= med),
             ('位置前半', lambda c: c['pos'] < 0.5), ('位置后半', lambda c: c['pos'] >= 0.5)]
    head = ['特征']
    rs = []
    for sname, sf in strat:
        r = perm_test(items_of(kept, sf), fns_for(MAIN, 'A'), nperm, seed)
        rs.append(r)
        m = r['_meta']
        head.append('%s（%d 篇，%d/%d）' % (sname, m['层数'], m['选用'], m['未选']))
    rows = []
    for n in MAIN:
        row = [n]
        for r in rs:
            x = r[n]
            row.append('—' if x is None else '%s pp（p=%s）' % (pp(x['mh']), pv(x['p2'])))
        rows.append(row)
    W('分层重算（甲的标，文章内差值和双侧 p；表头括号里是参加文章数和选用/未选例子数）：')
    W('')
    W(table(head, rows))
    W('')

    W('### 4.3 条件逻辑回归（按文章分层）')
    W('')
    W('本机没有 statsmodels / numpy，脚本用纯 Python 写了精确条件似然（每篇文章的分母是所有同样大小子集的和，递推求）'
      '加牛顿法，等价于带文章固定效应的条件 logit；只有同时含选用和未选例子的文章进入似然。系数的 p 值用 Wald 检验。')
    W('')
    W('模型：选用 ~ 出彩_实质 + 可复制_实质 + 独特禀赋 + 收益类数 + 资源转化 + 约束突破 + 量化成效 + 人物引语 + 贴合度 + log字数 + 位置')
    W('')
    covs = [('出彩_实质(0–2)', lambda c, w: c[w]['出彩_实质']), ('可复制_实质(0–2)', lambda c, w: c[w]['可复制_实质']),
            ('独特禀赋', lambda c, w: c[w]['独特禀赋']), ('收益类数', lambda c, w: len(set(c[w]['收益类']))),
            ('资源转化', lambda c, w: c[w]['资源转化']), ('约束突破', lambda c, w: c[w]['约束突破']),
            ('量化成效', lambda c, w: c[w]['量化成效']), ('人物引语', lambda c, w: c[w]['人物引语']),
            ('贴合度(0–2)', lambda c, w: c[w]['贴合度']), ('log 字数', lambda c, w: math.log(c['len'])),
            ('位置', lambda c, w: c['pos'])]
    reg = {}
    for who in ('A', 'B'):
        st = defaultdict(list)
        for c in kept:
            st[c['unit']].append((1 if c['st'] == '选用' else 0, [float(f(c, who)) for _, f in covs]))
        beta, se, ll, ll0, conv, it, ns = clogit(list(st.values()), len(covs))
        reg[who] = (beta, se)
        W('**%s的标**：%d 篇文章进入似然；对数似然 %.2f（全零模型 %.2f），似然比 χ²=%.2f（df=%d）；%s，%d 次迭代。'
          % ('甲' if who == 'A' else '乙', ns, ll, ll0, 2 * (ll - ll0), len(covs),
             '收敛' if conv else '**未收敛（可能有完全分离）**', it))
        W('')
        rows = []
        for (name, _), b, s in zip(covs, beta, se):
            z = b / s if s and s == s and s > 0 else float('nan')
            p = math.erfc(abs(z) / math.sqrt(2)) if z == z else None
            flag = '（系数很大，疑似分离）' if abs(b) > 8 else ''
            rows.append([name, '%+.3f' % b, '%.3f' % s, '%.2f' % math.exp(max(min(b, 50), -50)) + flag,
                         '%.2f' % z if z == z else '—', pv(p)])
        W(table(['变量', '系数', '标准误', '优势比 OR', 'z', 'p'], rows))
        W('')
    # 模型外的置换版：只控制文章的单变量对照已在第 3 节
    W('### 4.4 来源文章误判的敏感性')
    W('')
    W('只保留"来源证据强"的文章：文章里被选段的匹配字数（用率×字数，求和）≥ 150 字，且至少一段用率 ≥ 0.5。'
      '只共用套话的文件达不到这个量。')
    W('')
    strong = lambda c: c['art_match'] >= 150 and c['art_maxuse'] >= 0.5
    rS = perm_test(items_of(kept, strong), fns_for(MAIN, 'A'), nperm, seed)
    W(feat_table(rS, MAIN))
    W('')
    W('### 4.5 去重口径的敏感性（选用副本优先保留）')
    W('')
    rD = perm_test(items_of(kept2), fns_for(MAIN, 'A'), nperm, seed)
    W('这个口径去掉 %d 个（主口径 %d 个），留下选用 %d、未选 %d。甲的标：'
      % (len(dropped2), len(dropped), sum(1 for c in kept2 if c['st'] == '选用'), sum(1 for c in kept2 if c['st'] == '未选')))
    W('')
    W(feat_table(rD, MAIN))
    W('')
    W('### 4.6 不去重（对照）')
    W('')
    rN = perm_test(items_of(comp), fns_for(MAIN, 'A'), nperm, seed)
    W(feat_table(rN, MAIN))
    W('')

    # ------------------------------------------------ 5. 题目角色
    W('## 5. 按题目角色看选用例子（只描述，没有对照组）')
    W('')
    W('角色按例子里用率最高的那一段"选用"段的对应材料定：题干里问题一点名的材料 → 问题一材料，问题二点名的 → 问题二材料，其余 → 作文材料。'
      '最后一列是全部未选例子的比例，作参照。格子里是"甲 / 乙"。')
    W('')
    groups = [('问题一材料', [c for c in sel if c['role'] == '问题一材料']),
              ('问题二材料', [c for c in sel if c['role'] == '问题二材料']),
              ('作文材料', [c for c in sel if c['role'] == '作文材料']),
              ('（参照）未选', un)]
    head = ['特征'] + ['%s n=%d' % (g, len(cs)) for g, cs in groups]
    rows = []
    for name, fn, _ in FEATS:
        row = [name]
        for g, cs in groups:
            if not cs:
                row.append('—')
                continue
            a = sum(1 for c in cs if fn(c['A'])) / len(cs)
            b = sum(1 for c in cs if fn(c['B'])) / len(cs)
            row.append('%.0f%% / %.0f%%' % (100 * a, 100 * b))
        rows.append(row)
    for name, fn in (('字数中位数', lambda c: c['len']), ('位置均值', lambda c: c['pos'])):
        rows.append([name] + [('%.0f' if name == '字数中位数' else '%.2f') % (statistics.median(fn(c) for c in cs)
                                                                        if name == '字数中位数' else statistics.mean(fn(c) for c in cs))
                              if cs else '—' for g, cs in groups])
    W(table(head, rows))
    W('')
    W('各卷的角色分布：' + '；'.join('%s %s' % (p, '、'.join('%s %d' % (r[:3], n) for r, n in
                                                         sorted(Counter(c['role'] for c in sel if c['paper'] == p).items())))
                                  for p in PAPERS if any(c['paper'] == p for c in sel)) + '。')
    W('')

    # ------------------------------------------------ 6. 假设判定
    W('## 6. H1–H4 判定')
    W('')

    def passes(x, d):
        if x is None:
            return None
        ok_dir = x['mh'] * d > 0
        return ok_dir and abs(x['mh']) >= 0.10 and x['p2'] < 0.05

    def verdict(n):
        d = FDIR[n]
        x, xf, xb, xg = rA[n], rF.get(n), rB[n], rAg[n][n]
        k = kap[n]
        note = []
        if k is None or k < 0.4:
            return '证据不足', 'kappa=%s < 0.4，按预登记不下结论' % num(k)
        if not passes(x, d):
            why = []
            if x['mh'] * d <= 0:
                why.append('方向相反或为 0')
            elif abs(x['mh']) < 0.10:
                why.append('差值不到 10pp')
            if x['p2'] >= 0.05:
                why.append('p≥0.05')
            return '不支持', '全样本不达标（%s）' % '，'.join(why)
        if xf is None:
            return '证据不足', '贴合度=2 子集没有可比文章'
        if not passes(xf, d):
            if xf['mh'] * d > 0 and abs(xf['mh']) >= 0.10:
                return '证据不足', '贴合度=2 子集方向相同、差值够大，但 p=%s' % pv(xf['p2'])
            return '不支持', '贴合度=2 子集里差值 %s pp，不成立（被贴合度解释）' % pp(xf['mh'])
        if xb['mh'] * d <= 0 or (xg is not None and xg['mh'] * d <= 0):
            return '证据不足', '乙的标或一致子集方向不同'
        return '支持', ''

    vs = {}
    rows = []
    for n in sorted({f for h in HYP for f in h[2]}, key=FNAMES.index):
        v, why = verdict(n)
        vs[n] = v
        x, xf, xb, xg = rA[n], rF[n], rB[n], rAg[n][n]
        rows.append([n, {1: '↑', -1: '↓'}[FDIR[n]], num(kap[n]),
                     '%s pp, p=%s' % (pp(x['mh']), pv(x['p2'])),
                     '—' if xf is None else '%s pp, p=%s' % (pp(xf['mh']), pv(xf['p2'])),
                     '%s pp, p=%s' % (pp(xb['mh']), pv(xb['p2'])),
                     '—' if xg is None else '%s pp, p=%s' % (pp(xg['mh']), pv(xg['p2'])),
                     '**%s**' % v + ('：' + why if why else '')])
    W(table(['指标', '预期', 'kappa', '甲·全样本', '甲·贴合度=2', '乙·全样本', '一致子集', '单项判定'], rows))
    W('')
    for h, desc, fs, mode in HYP:
        vv = [vs[f] for f in fs]
        if mode == 'any':
            if '支持' in vv:
                v = '支持'
            elif all(x == '不支持' for x in vv):
                v = '不支持'
            else:
                v = '证据不足'
        else:
            if all(x == '支持' for x in vv):
                v = '支持'
            elif '不支持' in vv:
                v = '不支持'
            else:
                v = '证据不足'
        det = '；'.join('%s 文章内 %s pp（p=%s；贴合度=2：%s pp，p=%s；kappa %s）→ %s' % (
            f, pp(rA[f]['mh']), pv(rA[f]['p2']), pp(rF[f]['mh']) if rF[f] else '—', pv(rF[f]['p2']) if rF[f] else '—',
            num(kap[f]), vs[f]) for f in fs)
        bon = ''
        if len(fs) > 1 and v == '支持':
            a = 0.05 / len(fs)
            bon = '（Bonferroni 校正后阈值 %.4f：%s）' % (a, '、'.join(
                '%s %s' % (f, '仍显著' if rA[f]['p2'] < a else '不再显著') for f in fs if vs[f] == '支持'))
        W('- **%s %s：%s**%s。%s。' % (h, desc, v, bon, det))
    W('')
    open(outp, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('写到', outp)
    summary = {h: None for h, *_ in HYP}
    print(json.dumps({'样本': {'例子': len(cases), '分析例子': len(kept), '去重去掉': len(dropped),
                              '参加置换文章': res_meta['层数'], '选用(参加)': res_meta['选用'],
                              '未选(参加)': res_meta['未选']},
                      '单项': vs, 'kappa': {k: (None if v is None else round(v, 3)) for k, v in kap.items()}},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
