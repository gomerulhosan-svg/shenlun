exec(open('common.py').read())
NP=3000
L=sorted(c['len'] for c in kept); t1=L[len(L)//3]; t2=L[2*len(L)//3]
lb=lambda c: 0 if c['len']<=t1 else (1 if c['len']<=t2 else 2)
names=['出彩_显式','出彩_实质=2','收益类数≥2','约束突破']
print('阈值扫描（甲/乙；文章内差 pp, p）')
for th in [0,100,150,200,250,300,400,500,700]:
    cs=[c for c in kept if c['art_match']>=th]
    ra=mh(items(cs),names,'A',NP); rb=mh(items(cs),names,'B',NP); m=ra['_meta']
    print('≥%d: %d篇 %d/%d  '%(th,m['层数'],m['选用'],m['未选'])+'  '.join('%s %+.1f(p=%s)/%+.1f(p=%s)'%(n,100*ra[n]['mh'],S.pv(ra[n]['p2']),100*rb[n]['mh'],S.pv(rb[n]['p2'])) for n in names))
cs=[c for c in kept if c['art_match']>=300]
for lab,unit,filt in [('严来源·层=文章×字数三分位',lambda c:(c['unit'],lb(c)),None),('严来源·贴合度=2',None,lambda c:c['A']['贴合度']==2),
                      ('严来源·单段例子',None,lambda c:c['nseg']==1)]:
    sub=[c for c in cs if filt is None or filt(c)]
    for w in 'AB':
        r=mh(items(sub) if unit is None else items(sub,unit),HF,w,NP); m=r['_meta']
        print('\n##',lab,w,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
        for n in HF: print('   %-10s %s'%(n,fmt(r[n])))
# length diff in strict subset
r=S.perm_test(items(cs),[('log字数',lambda c:math.log(c['len']),0),('覆盖段数',lambda c:c['nseg'],0)],2000,1)
print('\n严来源 log字数 文章内差 %+.2f p=%s; 覆盖段数 %+.2f p=%s'%(r['log字数']['mh'],S.pv(r['log字数']['p2']),r['覆盖段数']['mh'],S.pv(r['覆盖段数']['p2'])))
r=S.perm_test(items(kept),[('log字数',lambda c:math.log(c['len']),0)],2000,1)
print('全样本 log字数 文章内差 %+.2f'%r['log字数']['mh'])
# cond logit in strict subset: feature + loglen + fit + pos
conf=[lambda c,w: c[w]['贴合度'], lambda c,w: math.log(c['len']), lambda c,w: c['pos']]
for n in ['出彩_显式','出彩_实质=2','收益类数≥2','约束突破']:
    row=[n]
    for w in 'AB':
        st=defaultdict(list)
        for c in cs: st[c['unit']].append((1 if c['st']=='选用' else 0,[val(c,n,w)]+[f(c,w) for f in conf]))
        b,se,ll,ll0,conv,it,ns=S.clogit(list(st.values()),4)
        z=b[0]/se[0]; row.append('%s OR=%.2f [%.2f,%.2f] p=%.3f'%('甲' if w=='A' else '乙',math.exp(b[0]),math.exp(b[0]-1.96*se[0]),math.exp(b[0]+1.96*se[0]),math.erfc(abs(z)/math.sqrt(2))))
    print('严来源 clogit(+贴合度+log字数+位置):',' | '.join(row))
