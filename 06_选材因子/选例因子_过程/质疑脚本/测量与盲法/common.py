import sys, json, os, re, statistics, random
from collections import Counter, defaultdict
sys.path.insert(0, '/home/user/shenlun/10_选材因子/tools')
import select_analysis as S
SEL = '/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/select'
cases = S.load(SEL)
comp = [c for c in cases if c['st'] != '部分']
kept, dropped, partial = S.dedup(comp)
BL, KEY, TEXT = {}, {}, {}
for p in S.PAPERS:
    b = json.load(open(f'{SEL}/blind/{p}.json'))
    BL[p] = b
    KEY[p] = json.load(open(f'{SEL}/key/{p}.json'))['段']
    for a in b['文章']:
        for s in a['段']:
            TEXT[(p, s['id'])] = s['文']
by_unit = defaultdict(list)
for c in kept:
    by_unit[c['unit']].append(c['st'])
PART = {u for u, s in by_unit.items() if '选用' in s and '未选' in s}
def within(items, fn, nperm=2000, seed=1, d=+1):
    """items: list of (unit, sel, obj) ; fn(obj)->float"""
    r = S.perm_test(items, [('x', fn, d)], nperm, seed, nboot=500)
    return r['x'], r['_meta']
def fmt(r):
    if r is None: return 'NA'
    ci = r['ci']
    return '%+.1f pp [%+.1f,%+.1f] p=%.3f (sel %.1f%% / un %.1f%%)' % (100*r['mh'], 100*ci[0], 100*ci[1], r['p2'], 100*r['in_sel'], 100*r['in_un'])
def fmtm(r):
    ci = r['ci']
    return '%+.3f [%+.3f,%+.3f] p=%.3f (sel %.3f / un %.3f)' % (r['mh'], ci[0], ci[1], r['p2'], r['in_sel'], r['in_un'])
