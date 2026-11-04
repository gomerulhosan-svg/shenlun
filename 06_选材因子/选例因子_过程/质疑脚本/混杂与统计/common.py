import sys, os, json, math, random, statistics, re
from collections import Counter, defaultdict
sys.path.insert(0, '/home/user/shenlun/10_选材因子/tools')
import select_analysis as S
D = '/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/select'
cases = S.load(D)
comp = [c for c in cases if c['st'] != '部分']
kept, dropped, partial = S.dedup(comp)
HF = ['出彩_显式', '出彩_实质=2', '可复制_实质=2', '独特禀赋', '收益类数≥2', '资源转化', '约束突破']
ALLF = HF + ['出彩_实质≥1', '可复制_显式', '量化成效', '人物引语', '讲难点', '新事物', '贴合度=2']
FD = {f[0]: f for f in S.FEATS}
def val(c, name, who='A'):
    return float(FD[name][1](c[who]))
def mh(items, names, who='A', nperm=0, seed=20260928):
    return S.perm_test(items, S.fns_for(names, who), nperm, seed, nboot=(2000 if nperm else 0))
def items(cs, unit=lambda c: c['unit']):
    return [(unit(c), c['st'] == '选用', c) for c in cs]
def fmt(x):
    if x is None: return '—'
    s = '%+.1f' % (100 * x['mh'])
    if x.get('ci'): s += ' [%+.1f, %+.1f]' % (100 * x['ci'][0], 100 * x['ci'][1])
    if x.get('p2') is not None and x['p2'] != 1.0 or True:
        s += ', p=%s' % S.pv(x['p2'])
    return s
