exec(open('common.py').read())
# Westfall-Young maxT over the 7 hypothesis indicators (出彩_实质≥1 dropped: ceiling), A and B jointly, and all 14 features
def maxT(cs, specs, nperm=10000, seed=7):
    # specs: list of (name, who, dir) ; statistic = standardized within-stratum deviation (S - E)/sqrt(Var) under hypergeometric
    by = defaultdict(list)
    for c in cs: by[c['unit']].append(c)
    strata = [v for v in by.values() if any(c['st']=='选用' for c in v) and any(c['st']=='未选' for c in v)]
    K = len(specs)
    X = [[[val(c, n, w) for (n, w, d) in specs] for c in v] for v in strata]
    Y = [[c['st']=='选用' for c in v] for v in strata]
    obs=[0.0]*K; E=[0.0]*K; V=[0.0]*K
    for x,y in zip(X,Y):
        n=len(x); n1=sum(y)
        for k in range(K):
            col=[r[k] for r in x]; T=sum(col); mu=T/n
            obs[k]+=sum(v for v,s in zip(col,y) if s); E[k]+=n1*mu
            s2=sum((v-mu)**2 for v in col)/(n-1) if n>1 else 0
            V[k]+=n1*(n-n1)/n*s2
    z=[(obs[k]-E[k])/math.sqrt(V[k]) if V[k]>0 else 0 for k in range(K)]
    rng=random.Random(seed); cnt_max=[0]*K; cnt_raw=[0]*K
    # two-sided: |z|
    order=sorted(range(K), key=lambda k:-abs(z[k]))
    wy=[0]*K
    for _ in range(nperm):
        acc=[0.0]*K
        for x,y in zip(X,Y):
            n=len(x); n1=sum(y)
            for i in rng.sample(range(n), n1):
                r=x[i]
                for k in range(K): acc[k]+=r[k]
        zz=[abs((acc[k]-E[k])/math.sqrt(V[k])) if V[k]>0 else 0 for k in range(K)]
        # step-down
        m=0.0
        succ=[0.0]*K
        for j in reversed(order):
            m=max(m,zz[j]); succ[j]=m
        for k in range(K):
            if succ[k]>=abs(z[k])-1e-9: wy[k]+=1
            if zz[k]>=abs(z[k])-1e-9: cnt_raw[k]+=1
    adj=[(1+wy[k])/(1+nperm) for k in range(K)]
    # enforce monotonicity
    run=0
    for k in order:
        run=max(run,adj[k]); adj[k]=run
    return [(specs[k][0], specs[k][1], z[k], (1+cnt_raw[k])/(1+nperm), adj[k]) for k in range(K)]
out=[]
for label, specs in [('甲 7 项', [(n,'A',S.FDIR[n]) for n in HF]),
                     ('乙 7 项', [(n,'B',S.FDIR[n]) for n in HF]),
                     ('甲+乙 14 项', [(n,w,S.FDIR[n]) for w in 'AB' for n in HF]),
                     ('甲 14 特征(含对照)', [(n,'A',S.FDIR.get(n,0)) for n in ALLF])]:
    r=maxT(kept, specs)
    out.append('### '+label)
    for n,w,z,p,a in r: out.append('%s·%s z=%+.2f p_raw=%.4f p_WY=%.4f'%(n,'甲' if w=='A' else '乙',z,p,a))
# Holm / BH on reported p-values
print('\n'.join(out))
