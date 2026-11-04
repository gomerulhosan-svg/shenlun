from common import *
import math
F=['出彩_显式','出彩_实质=2','收益类数≥2','资源转化','贴合度=2','量化成效']
mx=lambda c: max(KEY[c['paper']][s]['用率'] for s in c['segs'])
print('阈值曲线（文章内差 pp，A / B）')
for th in (0.3,0.4,0.5,0.6,0.7,0.8,0.9):
    sub=[c for c in kept if c['st']=='未选' or mx(c)>=th]
    it=S.items_of(sub)
    ra=S.perm_test(it, S.fns_for(F,'A'), 0, 3, nboot=0); rb=S.perm_test(it, S.fns_for(F,'B'), 0, 3, nboot=0)
    m=ra['_meta']
    print(' ≥%.1f (%d篇 %d/%d) ' % (th, m['层数'], m['选用'], m['未选']) + '  '.join('%s %+.0f/%+.0f' % (n, 100*ra[n]['mh'], 100*rb[n]['mh']) for n in F))
# length / nseg of high-use selected
for th in (0.3,0.7):
    s=[c for c in kept if c['st']=='选用' and mx(c)>=th]
    print('选用 max用率≥%.1f: n=%d 字数中位 %d 段数均值 %.2f' % (th, len(s), statistics.median(c['len'] for c in s), statistics.mean(c['nseg'] for c in s)))
s=[c for c in kept if c['st']=='选用' and mx(c)<0.5]
print('选用 max用率<0.5: n=%d 字数中位 %d 段数均值 %.2f' % (len(s), statistics.median(c['len'] for c in s), statistics.mean(c['nseg'] for c in s)))
# robustness at >=0.7
sub=[c for c in kept if c['st']=='未选' or mx(c)>=0.7]
for lab,flt in [('贴合度=2(甲)', lambda c:c['A']['贴合度']==2), ('段数<=2', lambda c:c['nseg']<=2), ('单段', lambda c:c['nseg']==1)]:
    it=S.items_of([c for c in sub if flt(c)])
    for who in 'AB':
        r=S.perm_test(it, S.fns_for(['出彩_实质=2','收益类数≥2','资源转化'],who), 3000, 5, nboot=500)
        print(' ≥0.7 %s %s %s' % (lab, who, r['_meta']['选用']), ' | '.join('%s %s' % (n, fmt(r[n])) for n in ['出彩_实质=2','收益类数≥2','资源转化']))
# conditional logit single-feature + fit + loglen + pos, at >=0.7
def clog(sub, who, feat):
    fn={'收益类数≥2':lambda L:float(len(set(L['收益类']))>=2),'资源转化':lambda L:float(L['资源转化']),'出彩_实质=2':lambda L:float(L['出彩_实质']==2)}[feat]
    strata=defaultdict(list)
    for c in sub:
        strata[c['unit']].append((1 if c['st']=='选用' else 0, [fn(c[who]), float(c[who]['贴合度']), math.log(c['len']), c['pos']]))
    strata=[v for v in strata.values() if any(y for y,_ in v) and any(not y for y,_ in v)]
    return S.clogit(strata, 4)
for who in 'AB':
    for feat in ['出彩_实质=2','收益类数≥2','资源转化']:
        try:
            r=clog(sub, who, feat)
            print(' clogit ≥0.7', who, feat, {k:(v if not isinstance(v,list) else [round(x,3) for x in v]) for k,v in r.items() if k in ('beta','se','p','ll','conv')})
        except Exception as e:
            print('clogit err', e); break
