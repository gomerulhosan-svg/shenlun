import json,re,sys,collections
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/k5check')
from maps import M
R='/home/user/shenlun/08_小题重写/'
HIT={'必答','弱共识','有','可选','个案','单票'}
CORE={'必答','弱共识','有'}
TARGET=[('2024一卷','问题二'),('2024二卷','问题二'),('2025省市','问题一'),('2025省市','问题二'),('2025县镇','问题二'),('2026省市','问题二'),('2026县镇','问题二'),('2023县级','问题二')]
agg=collections.Counter()
for key in TARGET:
    m=M[key]; s,q=key
    d=json.load(open(R+f'{s}/对齐.json'))[q]
    hit=set();core=set()
    for p in d['points']:
        if not isinstance(p,dict): continue
        mm=re.match(r'(.+?-p\d+-\d+)',p['pool_id'])
        if p['class'] in HIT: hit.add(mm.group(1))
        if p['class'] in CORE: core.add(mm.group(1))
    ids=json.load(open(R+f'_pool/{s}.json'))['ids']
    b=m['block']
    sents=collections.defaultdict(list)
    for k in ids:
        mm=re.fullmatch(re.escape(b)+r'-p(\d+)-(\d+)',k)
        if mm: sents[int(mm.group(1))].append(int(mm.group(2)))
    prev=None;slots=[]
    for p in sorted(m['paras']):
        lab=m['paras'][p]
        if lab.startswith('背景') or lab.startswith('叙述'):
            prev=lab;continue
        if lab!=prev:
            slots.append((lab,p))
        prev=lab
    out=[]
    for i,(lab,p) in enumerate(slots):
        sid=f'{b}-p{p}-1'
        z= sid not in hit; zc= sid not in core
        out.append((i,lab.split('|')[0],sid,'0票' if z else ('非必' if zc else '必')))
        t='first' if i==0 else 'other'
        agg[t+'_n']+=1; agg[t+'_zero']+=z; agg[t+'_notcore']+=zc
    # base: all sentences in block
    allk=[f'{b}-p{p}-{x}' for p in sents for x in sents[p]]
    agg['all_n']+=len(allk); agg['all_zero']+=sum(k not in hit for k in allk)
    # all paragraph-first sentences
    pf=[f'{b}-p{p}-1' for p in sents]
    agg['pfirst_n']+=len(pf); agg['pfirst_zero']+=sum(k not in hit for k in pf)
    print(s,q,out)
print(dict(agg))
