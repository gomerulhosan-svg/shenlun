import json,sys,re
s,q=sys.argv[1],sys.argv[2]
d=json.load(open(f'/home/user/shenlun/08_小题重写/{s}/对齐.json'))
ids=json.load(open(f'/home/user/shenlun/08_小题重写/_pool/{s}.json'))['ids']
for p in d[q]['points']:
    pid=p['pool_id']; m=re.match(r'(.+-p\d+-\d+)',pid); base=m.group(1)
    np_=len(p['papers']) if isinstance(p.get('papers'),list) else p.get('papers')
    print(pid, p['class'], np_, '|', ids.get(base, ids.get(pid,'?'))[:70], '||', str(p.get('note',''))[:40])
