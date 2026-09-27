import json,re,random,statistics as st,collections
B='/home/user/shenlun/08_小题重写/'
qs=json.load(open(B+'questions.json'))
HIT={'必答','弱共识','有','可选','个案','单票'}
SENT=re.compile(r'^([一二三四五六七八九十导]+)-p(\d+)-(\d+)$')
random.seed(1)
rows=[]
first=[];last=[];mid=[]
for q in qs:
    if not q['blocks']: continue
    sid=q['set_id']
    pool=json.load(open(B+'_pool/'+sid+'.json'))
    al=json.load(open(B+sid+'/对齐.json')).get(q['q'])
    if not isinstance(al,dict): continue
    n=al.get('n')
    hit=set()
    for p in al.get('points',[]):
        if not isinstance(p,dict): continue
        m=re.match(r'([一二三四五六七八九十导]+)-p(\d+)-(\d+)',str(p.get('pool_id','')))
        if not m: continue
        if p.get('class') in HIT: hit.add('%s-p%s-%s'%m.groups())
    # sentences by paragraph
    paras=collections.OrderedDict()
    for k,v in pool['ids'].items():
        m=SENT.match(k)
        if not m or m.group(1) not in q['blocks']: continue
        paras.setdefault((m.group(1),int(m.group(2))),[]).append((k,len(v)))
    sents=[s for ps in paras.values() for s in ps]
    H=sum(1 for k,_ in sents if k in hit)
    S=len(sents)
    zero_paras=[pk for pk,ps in paras.items() if not any(k in hit for k,_ in ps)]
    # null: permute hits among sentences
    keys=[k for k,_ in sents]
    sims=0;simcnt=[]
    R=2000
    for _ in range(R):
        hs=set(random.sample(keys,H))
        z=sum(1 for ps in paras.values() if not any(k in hs for k,_ in ps))
        simcnt.append(z); sims+= z>0
    # first/last paragraph per block
    for b in q['blocks']:
        pk=sorted(p for (bb,p) in paras if bb==b)
        if not pk: continue
        for i,p in enumerate(pk):
            z=(b,p) in zero_paras
            L=len(paras[(b,p)])
            if i==0: first.append((sid,q['q'],b,z,L,n))
            elif i==len(pk)-1: last.append((sid,q['q'],b,z,L,n))
            else: mid.append((sid,q['q'],b,z,L,n))
    rows.append(dict(sid=sid,q=q['q'],n=n,paras=len(paras),S=S,H=H,zero=len(zero_paras),null_mean=round(st.mean(simcnt),2),p_any_null=round(sims/R,3)))
for r in rows: print(r)
print('questions',len(rows),'with >=1 zero para',sum(r['zero']>0 for r in rows))
print('expected # of questions with >=1 zero para under random placement',round(sum(r['p_any_null'] for r in rows),1))
print('obs zero paras total',sum(r['zero'] for r in rows),'null expected',round(sum(r['null_mean'] for r in rows),1),'total paras',sum(r['paras'] for r in rows))
def rate(lst,cond=lambda x:True):
    l=[x for x in lst if cond(x)]
    return '%d/%d'%(sum(x[3] for x in l),len(l))
print('first para zero',rate(first),'mid',rate(mid),'last',rate(last))
print('n>=3 only: first',rate(first,lambda x:(x[5] or 0)>=3),'mid',rate(mid,lambda x:(x[5] or 0)>=3),'last',rate(last,lambda x:(x[5] or 0)>=3))
print('n<3: first',rate(first,lambda x:(x[5] or 0)<3),'mid',rate(mid,lambda x:(x[5] or 0)<3),'last',rate(last,lambda x:(x[5] or 0)<3))
print('first para lengths(sent)',st.median([x[4] for x in first]),'mid',st.median([x[4] for x in mid]) if mid else None,'last',st.median([x[4] for x in last]))
# length-matched: zero rate of paras by sentence count
allp=[(x[4],x[3],'F') for x in first]+[(x[4],x[3],'M') for x in mid]+[(x[4],x[3],'L') for x in last]
by=collections.defaultdict(lambda:[0,0])
for L,z,t in allp:
    k=min(L,4)
    by[(t,k)][0]+=z; by[(t,k)][1]+=1
for k in sorted(by): print(k,by[k])
QT={(q['set_id'],q['q']):q['qtype'] for q in qs}
def grp(sid,qq):
    t=QT[(sid,qq)]
    return 'wd' if t in ('T-问对','T-对策') else ('zf' if t in ('T-做法','T-表现') else 'other')
for g in ('zf','wd','other'):
    f=[x for x in first if grp(x[0],x[1])==g]; l=[x for x in last if grp(x[0],x[1])==g]; m_=[x for x in mid if grp(x[0],x[1])==g]
    print(g,'first',rate(f),'mid',rate(m_),'last',rate(l))
    print('   last detail',[(x[0],x[1],x[2],x[3],x[5]) for x in l])
