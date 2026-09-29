from common import *
from my_labels import M
ids = json.load(open('sample_ids.json'))
C = {c['id']: c for c in kept}
names = ['出彩_显式','出彩_实质','可复制_实质','独特禀赋','收益类数','资源转化','约束突破']
def lab(L):
    return [L['出彩_显式'], L['出彩_实质'], L['可复制_实质'], L['独特禀赋'], len(set(L['收益类'])), L['资源转化'], L['约束突破']]
rows=[]; agreeA=Counter(); agreeB=Counter(); n=0
diffA=defaultdict(list)
guess=Counter()
for i, cid in enumerate(ids, 1):
    c = C[cid]; m = M[i]
    mine = list(m[:7]); a = lab(c['A']); b = lab(c['B'])
    st = c['st']
    segs = ['%s:%s%.2f' % (s, KEY[c['paper']][s]['标'][0], KEY[c['paper']][s]['用率']) for s in c['segs']]
    print('#%02d %s %s 我猜%s | 我 %s | A %s | B %s | %s | %s' % (i, cid, st, '选' if m[8] else '未', mine, a, b, ' '.join(segs), m[7]))
    for k, nm in enumerate(names):
        x, y = mine[k], a[k]
        if nm == '收益类数': x, y = min(x,2)>=2, min(y,2)>=2
        agreeA[nm] += (x == y)
        x2 = b[k] if nm!='收益类数' else b[k]>=2
        agreeB[nm] += ((mine[k] if nm!='收益类数' else mine[k]>=2) == x2)
        diffA[nm].append((a[k] - mine[k], st))
    guess[(m[8]==1, st=='选用')] += 1
print()
print('与 A 一致数/30', dict(agreeA)); print('与 B 一致数/30', dict(agreeB))
for nm in names:
    d=diffA[nm]
    print('  %-8s A−我 均值: 全部 %+.2f | 选用组 %+.2f | 未选组 %+.2f' % (nm, statistics.mean(x for x,_ in d), statistics.mean(x for x,s in d if s=='选用'), statistics.mean(x for x,s in d if s=='未选')))
print('我猜选用 vs 实际', dict(guess), '猜中 %d/30' % (guess[(True,True)]+guess[(False,False)]))
# my labels: within-sample sel vs unsel
for k,nm in enumerate(names):
    s=[M[i][k] for i,cid in enumerate(ids,1) if C[cid]['st']=='选用']; u=[M[i][k] for i,cid in enumerate(ids,1) if C[cid]['st']=='未选']
    f=(lambda v:v>=2) if nm=='收益类数' else ((lambda v:v==2) if nm in ('出彩_实质','可复制_实质') else (lambda v:v==1))
    print('  我的标 %-8s 选用 %d/%d  未选 %d/%d' % (nm, sum(map(f,s)), len(s), sum(map(f,u)), len(u)))
