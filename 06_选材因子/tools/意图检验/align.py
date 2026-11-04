import json,re,collections
B='/home/user/shenlun/08_小题重写/'
qs=json.load(open(B+'questions.json'))
res={}
for q in qs:
    s=q['set_id']
    try: d=json.load(open(B+s+'/对齐.json'))
    except Exception as e: print(s,'ERR',e); continue
    x=d.get(q['q'])
    if not isinstance(x,dict): print(s,q['q'],'非dict',str(x)[:80]); continue
    n=x.get('n'); pts=x.get('points',[])
    if not isinstance(pts,list): print(s,q['q'],'points非list'); continue
    c=collections.Counter(); cm=collections.Counter()
    for p in pts:
        if not isinstance(p,dict): continue
        pid=p.get('pool_id') or ''
        m=re.match(r'([一二三四五六七八九十导]+)-',str(pid))
        b=m.group(1) if m else '?'+str(pid)[:10]
        c[b]+=1
        if p.get('class')=='必答': cm[b]+=1
    print(s,q['q'],'n=',n,'pts',len(pts),'blocks',dict(c),'必答',dict(cm))
