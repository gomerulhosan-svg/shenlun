exec(open('common.py').read())
NP=5000
segown=defaultdict(list)
for c in kept:
    for s in c['segs']: segown[(c['paper'],s)].append(c['id'])
single=[c for c in kept if c['nseg']==1]
clean=[c for c in single if len(segown[(c['paper'],c['segs'][0])])==1]
# length terciles over kept
L=sorted(c['len'] for c in kept); t1=L[len(L)//3]; t2=L[2*len(L)//3]
lb=lambda c: 0 if c['len']<=t1 else (1 if c['len']<=t2 else 2)
names=HF+['量化成效','人物引语','新事物','贴合度=2']
res={}
for lab,cs,unit in [('主样本',kept,None),('单段例子',single,None),('单段且该段只切出这一个例子',clean,None),
                    ('层=文章×字数三分位',kept,lambda c:(c['unit'],lb(c))),
                    ('层=文章×字数三分位×贴合度',kept,lambda c:(c['unit'],lb(c),c['A']['贴合度'])),
                    ('层=文章×贴合度',kept,lambda c:(c['unit'],c['A']['贴合度']))]:
    for who in 'AB':
        its=items(cs) if unit is None else items(cs,unit)
        r=mh(its,names,who,NP)
        res[(lab,who)]=r
print('tertile cut',t1,t2)
for lab in ['主样本','单段例子','单段且该段只切出这一个例子','层=文章×字数三分位','层=文章×字数三分位×贴合度','层=文章×贴合度']:
    m=res[(lab,'A')]['_meta']
    print('\n##',lab,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
    for n in names:
        print('  %-10s 甲 %s | 乙 %s'%(n,fmt(res[(lab,'A')][n]),fmt(res[(lab,'B')][n])))
# mechanism: in unselected examples, within-article, does feature prevalence rise with length?
print('\n## 未选例子里，特征 vs 字数（文章内：长于本文未选例子中位数 vs 短于）')
un=[c for c in kept if c['st']=='未选']
by=defaultdict(list)
for c in un: by[c['unit']].append(c)
lst=[]
for u,cs in by.items():
    if len(cs)<2: continue
    med=statistics.median(c['len'] for c in cs)
    for c in cs:
        lst.append((u, c['len']>med, c))
r=S.perm_test(lst, S.fns_for(names,'A'), 2000, 1, nboot=0)
rb=S.perm_test(lst, S.fns_for(names,'B'), 2000, 1, nboot=0)
for n in names: print('  %-10s 长-短 甲 %+.1f pp (p=%s) 乙 %+.1f pp (p=%s)'%(n,100*r[n]['mh'],S.pv(r[n]['p2']),100*rb[n]['mh'],S.pv(rb[n]['p2'])))
json.dump({'%s|%s'%k:{n:(v[n]['mh'],v[n]['ci'],v[n]['p2']) for n in names} for k,v in res.items()},open('a2.json','w'),ensure_ascii=False)
