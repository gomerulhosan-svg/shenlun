from common import *
it = S.items_of(kept)
F = ['出彩_显式','出彩_实质=2','可复制_实质=2','独特禀赋','收益类数≥2','资源转化','约束突破']
for who in 'AB':
    fns = S.fns_for(F, who)
    print('== 留一卷（%s）' % who)
    base = S.perm_test(it, fns, 0, 1, nboot=0)
    print('  全部       ' + '  '.join('%s %+.1f' % (n, 100*base[n]['mh']) for n in F))
    for p in S.PAPERS:
        sub = [i for i in it if i[0][0] != p]
        r = S.perm_test(sub, fns, 0, 1, nboot=0)
        print('  去掉%-6s ' % p + '  '.join('%s %+.1f' % (n, 100*r[n]['mh']) for n in F))
    print('== 每卷单独（%s；选用/未选 例子数）' % who)
    for p in S.PAPERS:
        sub = [i for i in it if i[0][0] == p]
        r = S.perm_test(sub, fns, 0, 1, nboot=0)
        m = r['_meta']
        if m['层数'] == 0: continue
        print('  %-6s (%d/%d) ' % (p, m['选用'], m['未选']) + '  '.join('%s %+.0f' % (n, 100*r[n]['mh']) for n in F))
