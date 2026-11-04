import json,re,collections
from parse import SETS
R='/home/user/shenlun'
qs=json.load(open(f'{R}/08_小题重写/questions.json',encoding='utf-8'))
qb=collections.defaultdict(set)
for x in qs: qb[x['set_id']].update(x['blocks'])
for s in SETS:
    t=open(f'{R}/07_句子层/重写/{s}_重写.md',encoding='utf-8').read()
    ann=t[t.find('## 二、逐句标注'):]
    ann=ann[:ann.find('## 三、')] if '## 三、' in ann else ann
    cnt=collections.Counter(); n=0
    for line in ann.split('\n'):
        if line.startswith('> 来源'):
            n+=1
            ms=set(re.findall(r'材料([一二三四五六七八九])',line))
            for m in ms: cnt[m]+=1
    small=sorted(qb[s]); tot=sum(cnt.values())
    sm=sum(cnt[m] for m in small)
    print(s,'来源条',n,'小题则',''.join(small),'小题则被引',sm,'/',tot,f'{sm*100//max(tot,1)}%',dict(sorted(cnt.items(),key=lambda x:'一二三四五六七八九'.index(x[0]))))
