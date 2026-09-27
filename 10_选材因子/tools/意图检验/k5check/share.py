import json,re,random,statistics as st,collections
B='/home/user/shenlun/08_小题重写/'
qs=json.load(open(B+'questions.json'))
HIT={'必答','弱共识','有','可选','个案','单票'}
SENT=re.compile(r'^([一二三四五六七八九十导]+)-p(\d+)-(\d+)$')
random.seed(2)
obs=[];nul=[]
for q in qs:
    if not q['blocks']: continue
    sid=q['set_id']; pool=json.load(open(B+'_pool/'+sid+'.json'))
    al=json.load(open(B+sid+'/对齐.json')).get(q['q'])
    hit=set()
    for p in al.get('points',[]):
        if isinstance(p,dict):
            m=re.match(r'(.+?-p\d+-\d+)',str(p.get('pool_id','')))
            if m and p.get('class') in HIT: hit.add(m.group(1))
    paras=collections.defaultdict(list)
    for k,v in pool['ids'].items():
        m=SENT.match(k)
        if m and m.group(1) in q['blocks']: paras[(m.group(1),m.group(2))].append((k,len(v)))
    tot=sum(l for ps in paras.values() for _,l in ps)
    def zshare(hs): return sum(l for ps in paras.values() if not any(k in hs for k,_ in ps) for _,l in ps)/tot
    keys=[k for ps in paras.values() for k,_ in ps]; H=len([k for k in keys if k in hit])
    obs.append(zshare(hit)); nul.append(st.mean(zshare(set(random.sample(keys,H))) for _ in range(500)))
print('obs median zero-para char share',round(st.median(obs),3),'null median',round(st.median(nul),3))
print('obs>null in',sum(o>n for o,n in zip(obs,nul)),'of',len(obs))
