"""选例因子检验·写报告时的补算（事后分析，只当线索）。

用法：python3 select_extra_highuse.py <select 目录>
<select 目录> 里要有 select_pairs.py / select_blind.py 生成的底表、blind/、key/，
以及标注 out/（cases_*、labelsA_*、labelsB_*）。口径和 select_analysis.py 完全一样。

算三件事：
1. 用率门槛 ≥0.7（只保留例子里最高用率 ≥0.7 的选用例子，未选组不变）下，
   主样本、按"文章×字数三分位"分层、再加贴合度分层后的文章内差值；
2. 单段例子里独特禀赋的原始比例和文章内加权比例；
3. 乙−甲 收益类数在选用/未选组的文章内加权均值。
"""
import sys
import statistics
import json
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import select_analysis as S

SEL = sys.argv[1]
cases = S.load(SEL)
kept, _, _ = S.dedup([c for c in cases if c['st'] != '部分'])
KEY = {p: json.load(open(f'{SEL}/key/{p}.json'))['段'] for p in S.PAPERS}
mx = lambda c: max(KEY[c['paper']][s]['用率'] for s in c['segs'])
L = sorted(c['len'] for c in kept)
t1, t2 = L[len(L) // 3], L[2 * len(L) // 3]
lb = lambda c: 0 if c['len'] <= t1 else (1 if c['len'] <= t2 else 2)
F = ['出彩_显式', '出彩_实质=2', '可复制_实质=2', '独特禀赋', '收益类数≥2', '资源转化', '约束突破', '贴合度=2']


def show(label, items, names=F, nperm=5000):
    for who in 'AB':
        r = S.perm_test(items, S.fns_for(names, who), nperm, 7, nboot=1000)
        m = r['_meta']
        print(f"{label} {'甲' if who == 'A' else '乙'}  {m['层数']} 层 选用 {m['选用']} / 未选 {m['未选']}")
        print('   ' + ' | '.join('%s %+.1f [%+.1f,%+.1f] p=%.3f' % (
            n, 100 * r[n]['mh'], 100 * r[n]['ci'][0], 100 * r[n]['ci'][1], r[n]['p2']) for n in names))


hi = [c for c in kept if c['st'] == '未选' or mx(c) >= 0.7]
show('用率≥0.7·主样本', S.items_of(hi))
show('用率≥0.7·层=文章×字数三分位', [((c['unit'], lb(c)), c['st'] == '选用', c) for c in hi])
show('用率≥0.7·层=文章×字数三分位×贴合度', [((c['unit'], lb(c), c['A']['贴合度']), c['st'] == '选用', c) for c in hi])
show('段数≤2', S.items_of([c for c in kept if c['nseg'] <= 2]))

single = [c for c in kept if c['nseg'] == 1]
for who in 'AB':
    s = [c for c in single if c['st'] == '选用']
    u = [c for c in single if c['st'] == '未选']
    r = S.perm_test(S.items_of(single), S.fns_for(['独特禀赋'], who), 0, 1, nboot=0)['独特禀赋']
    print('单段·独特禀赋 %s：原始 选用 %.1f%%（n=%d）/ 未选 %.1f%%（n=%d）；文章内加权 选用 %.1f%% / 未选 %.1f%%' % (
        who, 100 * statistics.mean(c[who]['独特禀赋'] for c in s), len(s),
        100 * statistics.mean(c[who]['独特禀赋'] for c in u), len(u), 100 * r['in_sel'], 100 * r['in_un']))

nb = lambda Lb: len(set(Lb['收益类']))
r = S.perm_test(S.items_of(kept), [('d', lambda c: nb(c['B']) - nb(c['A']), +1)], 3000, 1, nboot=500)['d']
print('乙−甲 收益类数：文章内加权 选用 %+.3f / 未选 %+.3f，差 %+.3f，p=%.3f' % (r['in_sel'], r['in_un'], r['mh'], r['p2']))
