import json,sys
s,q=sys.argv[1],sys.argv[2]
d=json.load(open(f'/home/user/shenlun/08_小题重写/{s}/对齐.json'))
pool=json.load(open(f'/home/user/shenlun/08_小题重写/_pool/{s}.json'))
ids=pool.get('ids',{})
v=d[q]
print('n=',v.get('n'), 'structure=',v.get('structure'), 'absent=',str(v.get('absent'))[:300])
for p in v['points']:
    if not isinstance(p,dict): print('  RAW',p); continue
    pid=p.get('pool_id')
    np_=len(p.get('papers',[])) if isinstance(p.get('papers'),list) else p.get('papers')
    extra={k:p[k] for k in ('side','what','votes') if k in p}
    print(f"{pid:12s} {p.get('class')}\t{p.get('kind')}\t{np_}\t{extra}\t{ids.get(pid,'?')[:50]}\t|| {str(p.get('note',''))[:120]}")
print('NOTES:',str(v.get('notes'))[:1500])
