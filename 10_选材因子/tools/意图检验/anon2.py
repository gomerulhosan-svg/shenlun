import json,re,statistics as st,collections
from anon import ANON,REAL,B,qs
LET=ANON[0]
two=[s for s in dict.fromkeys(q['set_id'] for q in qs) if not any(q['set_id']==s and q['q']=='问题三' for q in qs)]
out=collections.defaultdict(list)
print('set  Q1块:字母实体/不同匿名实体/真实地名  Q2块:同  作文各则中含字母实体的比例 / 作文块不同匿名实体均值')
for sid in sorted(two):
    blocks=json.load(open(f'{B}/_pool/{sid}.json'))['blocks']
    role={}
    for q in qs:
        if q['set_id']==sid:
            for b in q['blocks']: role[b]='Q1' if q['q']=='问题一' else 'Q2'
    def feat(t):
        let=set(re.sub(r'\s','',m) for m in re.findall(LET,t))
        ents=set()
        for i,p in enumerate(ANON):
            for m in re.findall(p,t):
                m=re.sub(r'\s','',m)
                if i==3: m=m[1:]
                ents.add(m)
        real=set(re.findall(REAL,t))
        return len(let)>0,len(ents),len(real)
    per={}
    ess=[]
    for b,ps in blocks.items():
        f=feat('\n'.join(ps))
        r=role.get(b,'作文')
        if r=='作文': ess.append(f)
        else: per[r]=f
    period='2020-23' if sid<'2024' else '2024-26'
    e_let=sum(x[0] for x in ess)/len(ess); e_ent=st.mean(x[1] for x in ess)
    print(sid,per.get('Q1'),per.get('Q2'),'作文: %.2f / %.1f'%(e_let,e_ent))
    for r in('Q1','Q2'):
        if r in per:
            out[(period,r,'let')].append(per[r][0]); out[(period,r,'ent')].append(per[r][1]); out[(period,r,'real')].append(per[r][2])
    out[(period,'作文','let')]+= [x[0] for x in ess]; out[(period,'作文','ent')]+=[x[1] for x in ess]; out[(period,'作文','real')]+=[x[2] for x in ess]
print()
for period in ['2020-23','2024-26']:
    for r in ['Q1','Q2','作文']:
        L=out[(period,r,'let')]
        print(period,r,'块数',len(L),'含字母实体 %d/%d'%(sum(L),len(L)),'不同匿名实体均值 %.1f'%st.mean(out[(period,r,'ent')]),'不同真实地名均值 %.1f'%st.mean(out[(period,r,'real')]))
