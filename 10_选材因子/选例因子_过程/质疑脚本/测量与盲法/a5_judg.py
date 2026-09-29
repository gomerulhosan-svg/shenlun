from common import *
import math
def rate(sub, f): return 100*statistics.mean(f(c) for c in sub) if sub else float('nan')
K=kept
print('出彩_实质=2 的比例，按 出彩_显式 / 量化成效 / 字数分组（A 标）')
for who in 'AB':
    for nm, g in [('显式=1', lambda c:c[who]['出彩_显式']==1), ('显式=0', lambda c:c[who]['出彩_显式']==0),
                  ('量化=1', lambda c:c[who]['量化成效']==1), ('量化=0', lambda c:c[who]['量化成效']==0),
                  ('字数>中位', lambda c:c['len']>194), ('字数≤中位', lambda c:c['len']<=194),
                  ('独特禀赋=1', lambda c:c[who]['独特禀赋']==1), ('独特禀赋=0', lambda c:c[who]['独特禀赋']==0),
                  ('贴合=2', lambda c:c[who]['贴合度']==2), ('贴合<2', lambda c:c[who]['贴合度']<2)]:
        sub=[c for c in K if g(c)]
        print('  %s %-10s n=%3d  出彩实质=2 %.0f%%  出彩实质=0 %.0f%%' % (who, nm, len(sub), rate(sub, lambda c:c[who]['出彩_实质']==2), rate(sub, lambda c:c[who]['出彩_实质']==0)))
print()
# cross-tab 可复制_实质 vs 独特禀赋
for who in 'AB':
    ct=Counter((c[who]['独特禀赋'], c[who]['可复制_实质']) for c in K)
    print(who, '独特禀赋 x 可复制_实质', dict(sorted(ct.items())))
    ct=Counter((c[who]['出彩_实质'], c[who]['可复制_实质']) for c in K)
    print(who, '出彩_实质 x 可复制_实质', dict(sorted(ct.items())))
# how much of 出彩_实质=2 is explained by surface: simple logistic via counts
print()
# 出彩_实质 distribution
for who in 'AB':
    print(who, '出彩_实质分布', Counter(c[who]['出彩_实质'] for c in K), '可复制_实质', Counter(c[who]['可复制_实质'] for c in K))
# theory: 可复制_实质 is judged by scale of actor: province-level/big-city actors -> 0.
# check the 理由 text for mention of 省级/深圳/广州
kwbig=re.compile(r'省级|全省|深圳|广州|国家|央企|巨额|大企业|头部|龙头')
for who in 'AB':
    a=[c for c in K if kwbig.search(c[who].get('理由',''))]
    print(who,'理由提到 省级/深广/国家/龙头 的例子 n=%d, 其中 可复制_实质=0 占 %.0f%%; 其余 %.0f%%' % (len(a), rate(a, lambda c:c[who]['可复制_实质']==0), rate([c for c in K if c not in a], lambda c:c[who]['可复制_实质']==0)))
# 出彩_实质=2 within article, conditioning on 出彩_显式 (A): stratify
it=S.items_of(K)
for who in 'AB':
    for v in (0,1):
        r,_=within([i for i in it if i[2][who]['出彩_显式']==v], lambda c:c[who]['出彩_实质']==2, nperm=3000)
        print(who,'出彩_显式=%d 层里 出彩_实质=2 文章内差'%v, fmt(r))
