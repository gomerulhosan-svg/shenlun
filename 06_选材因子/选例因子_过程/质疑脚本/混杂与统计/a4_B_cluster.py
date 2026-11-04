exec(open('common.py').read())
NP=5000
L=sorted(c['len'] for c in kept); t1=L[len(L)//3]; t2=L[2*len(L)//3]
lb=lambda c: 0 if c['len']<=t1 else (1 if c['len']<=t2 else 2)
# 1) B-A disagreement on 收益类数≥2 by selection, within article, and vs length
def nb(c,w): return len(set(c[w]['收益类']))
for c in kept:
    c['Bmore']= float(nb(c,'B')>=2 and nb(c,'A')<2); c['Amore']=float(nb(c,'A')>=2 and nb(c,'B')<2)
    c['Bcnt_minus_A']=nb(c,'B')-nb(c,'A')
fns=[('乙判≥2而甲判<2',lambda c:c['Bmore'],0),('甲判≥2而乙判<2',lambda c:c['Amore'],0),('乙减甲收益类数',lambda c:c['Bcnt_minus_A'],0)]
r=S.perm_test(items(kept),fns,NP,1)
for n,_,_ in fns: print('%s: 选用 %.3f 未选 %.3f 文章内差 %+.3f %s p=%s'%(n,r[n]['in_sel'],r[n]['in_un'],r[n]['mh'],S.cim(r[n]['ci']),S.pv(r[n]['p2'])))
r=S.perm_test(items(kept,lambda c:(c['unit'],lb(c))),fns,NP,1)
for n,_,_ in fns: print('  控字数三分位后 %s: 文章内差 %+.3f %s p=%s'%(n,r[n]['mh'],S.cim(r[n]['ci']),S.pv(r[n]['p2'])))
# B-more vs length among all
for k in range(3):
    cs=[c for c in kept if lb(c)==k]
    print('字数三分位',k,'n=%d 乙多判率 %.3f 甲多判率 %.3f'%(len(cs),statistics.mean(c['Bmore'] for c in cs),statistics.mean(c['Amore'] for c in cs)))
# per paper B-A
print('各卷 乙多判/甲多判:',{p:(sum(c['Bmore'] for c in kept if c['paper']==p),sum(c['Amore'] for c in kept if c['paper']==p)) for p in S.PAPERS})
# 2) cluster: connected components of examples sharing segments (within paper)
parent={}
def f(x):
    while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
    return x
for c in kept: parent[c['id']]=c['id']
own=defaultdict(list)
for c in kept:
    for s in c['segs']: own[(c['paper'],s)].append(c['id'])
for v in own.values():
    for x in v[1:]: parent[f(x)]=f(v[0])
comp=defaultdict(list)
for c in kept: comp[f(c['id'])].append(c)
sizes=Counter(len(v) for v in comp.values()); print('cluster sizes',sorted(sizes.items()))
mixed=sum(1 for v in comp.values() if len({c['st'] for c in v})>1); print('mixed-status clusters',mixed)
# Cluster-level analysis: collapse each cluster to one unit: status = any selected? use majority; features = mean over examples
cl=[]
for k,v in comp.items():
    st='选用' if any(c['st']=='选用' for c in v) else '未选'
    cl.append({'unit':v[0]['unit'],'st':st,'v':v,'len':sum(c['len'] for c in v)})
def cfn(n,w): return lambda C: statistics.mean(val(c,n,w) for c in C['v'])
for w in 'AB':
    fns=[(n,cfn(n,w),S.FDIR[n]) for n in HF]
    r=S.perm_test([(C['unit'],C['st']=='选用',C) for C in cl],fns,NP,1)
    m=r['_meta']; print('\n## 聚类（共用段的例子并成一个单位，特征取均值）',w,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
    for n in HF: print('   %-10s %s'%(n,fmt(r[n])))
# random one-example-per-cluster, repeated: distribution of p for B 收益 and A features
print('\n## 每个聚类随机取一个例子，重复 200 次：p<0.05 的比例 / 差值中位数')
rng=random.Random(3)
acc=defaultdict(list)
for it in range(200):
    pick=[rng.choice(v) for v in comp.values()]
    for w in 'AB':
        r=S.perm_test(items(pick),S.fns_for(HF,w),500,it,nboot=0)
        for n in HF: acc[(n,w)].append((r[n]['mh'],r[n]['p2']))
for n in HF:
    s=[]
    for w in 'AB':
        v=acc[(n,w)]; s.append('%s 中位差 %+.1f, p<0.05 占 %.0f%%'%('甲' if w=='A' else '乙',100*statistics.median(x for x,_ in v),100*sum(p<0.05 for _,p in v)/len(v)))
    print('  %-10s %s'%(n,' | '.join(s)))
