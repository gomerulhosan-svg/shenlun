from common import *
exec(open('a3_kw.py').read().split('# (a)')[0].split('from common import *')[1])
# corrected 出彩_显式 (A): selected examples whose keyword is only in non-selected segs -> 0
bad = set()
for c in kept:
    if c['st']=='选用' and c['nseg']>1 and c['A']['出彩_显式']==1:
        sel=[s for s in c['segs'] if KEY[c['paper']][s]['标']=='选用']
        if not any(KW.search(TEXT[(c['paper'],s)]) for s in sel): bad.add(c['id'])
it = S.items_of(kept)
r,_=within(it, lambda c: c['A']['出彩_显式']==1 and c['id'] not in bad, nperm=5000)
print('A 出彩_显式 修正(关键词不在选用段的记 0):', fmt(r))
r,_=within(it, lambda c: c['A']['出彩_显式']==1, nperm=5000)
print('A 出彩_显式 原样:', fmt(r))
# kappa by group
print('\nkappa 分组（选用组 / 未选组）')
for name, fn, d in S.FEATS:
    out=[]
    for g in ['选用','未选']:
        sub=[c for c in kept if c['st']==g]
        xa=[fn(c['A']) for c in sub]; xb=[fn(c['B']) for c in sub]
        po,k=S.kappa(xa,xb)
        out.append('%s n=%d 一致 %.2f kappa %s  A=1:%d B=1:%d' % (g,len(sub),po,('%.2f'%k) if k is not None else 'NA', sum(xa), sum(xb)))
    print('  %-12s | %s | %s' % (name, out[0], out[1]))
for nm, fn in [('出彩_实质', lambda L:L['出彩_实质']), ('可复制_实质', lambda L:L['可复制_实质']), ('收益类数', lambda L:min(len(set(L['收益类'])),3))]:
    for g in ['选用','未选']:
        sub=[c for c in kept if c['st']==g]
        xa=[fn(c['A']) for c in sub]; xb=[fn(c['B']) for c in sub]
        cats=(0,1,2,3) if nm=='收益类数' else (0,1,2)
        print('  %s %s 线性加权kappa %.2f  均值 A %.2f B %.2f' % (nm, g, S.wkappa(xa,xb,cats), statistics.mean(xa), statistics.mean(xb)))
# B - A difference by group, within article
print('\nB−A 差（文章内，选用 vs 未选）')
for nm, fn in [('收益类数', lambda L:len(set(L['收益类']))), ('收益类数≥2', lambda L:len(set(L['收益类']))>=2), ('出彩_实质', lambda L:L['出彩_实质']), ('可复制_实质', lambda L:L['可复制_实质']), ('出彩_显式', lambda L:L['出彩_显式']), ('资源转化', lambda L:L['资源转化'])]:
    r,_=within(it, lambda c,fn=fn: float(fn(c['B']))-float(fn(c['A'])), nperm=3000)
    print('  %-10s %s' % (nm, fmtm(r)))
# does B-A in 收益类数 grow with length?
import math
xs=[math.log(c['len']) for c in kept]; ys=[len(set(c['B']['收益类']))-len(set(c['A']['收益类'])) for c in kept]
mx,my=statistics.mean(xs),statistics.mean(ys)
cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/len(xs)
print('corr(log len, B−A 收益类数) = %.3f' % (cov/statistics.pstdev(xs)/statistics.pstdev(ys)))
for lo,hi in [(0,150),(150,300),(300,600),(600,99999)]:
    sub=[c for c in kept if lo<=c['len']<hi]
    print('  len[%d,%d) n=%d  B−A 收益类数均值 %.2f; A≥2 %.2f B≥2 %.2f' % (lo,hi,len(sub), statistics.mean(len(set(c['B']['收益类']))-len(set(c['A']['收益类'])) for c in sub), statistics.mean(len(set(c['A']['收益类']))>=2 for c in sub), statistics.mean(len(set(c['B']['收益类']))>=2 for c in sub)))
