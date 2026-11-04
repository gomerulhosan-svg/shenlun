exec(open('common.py').read())
NP=5000
L=sorted(c['len'] for c in kept); t1=L[len(L)//3]; t2=L[2*len(L)//3]
lb=lambda c: 0 if c['len']<=t1 else (1 if c['len']<=t2 else 2)
comp_=[c for c in kept if c['st']=='未选' or c['role']=='作文材料']
for lab,cs,unit in [('作文材料·层=文章×字数三分位',comp_,lambda c:(c['unit'],lb(c))),
                    ('作文材料·层=文章×贴合度',comp_,lambda c:(c['unit'],c['A']['贴合度'])),
                    ('层=文章×位置前后半',kept,lambda c:(c['unit'],c['pos']<0.5)),
                    ('来源更严：匹配字数≥300且≥2段选用',[c for c in kept if c['art_match']>=300],None)]:
    for w in 'AB':
        r=mh(items(cs) if unit is None else items(cs,unit),HF+['贴合度=2'],w,NP); m=r['_meta']
        print('\n##',lab,w,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
        for n in HF+['贴合度=2']: print('   %-10s %s'%(n,fmt(r[n])))
# specificity: sign-adjusted z of hypothesis features vs control features, A and B
def zs(w):
    by=defaultdict(list)
    for c in kept: by[c['unit']].append(c)
    st=[v for v in by.values() if any(c['st']=='选用' for c in v) and any(c['st']=='未选' for c in v)]
    out={}
    for n in ALLF:
        o=E=V=0
        for v in st:
            x=[val(c,n,w) for c in v]; y=[c['st']=='选用' for c in v]; nn=len(x); n1=sum(y); mu=sum(x)/nn
            o+=sum(a for a,b in zip(x,y) if b); E+=n1*mu; V+=n1*(nn-n1)/nn*(sum((a-mu)**2 for a in x)/(nn-1))
        out[n]=(o-E)/math.sqrt(V) if V>0 else 0
    return out
for w in 'AB':
    z=zs(w)
    hyp={n:z[n]*S.FDIR[n] for n in HF}
    ctl={n:z[n] for n in ['量化成效','人物引语','讲难点','新事物','贴合度=2']}
    print('\n',w,'假设特征(按预期方向调号) z:',{k:round(v,2) for k,v in hyp.items()},'均值 %.2f'%statistics.mean(hyp.values()))
    print('  ',w,'对照特征 z:',{k:round(v,2) for k,v in ctl.items()},'均值 %.2f'%statistics.mean(ctl.values()))
