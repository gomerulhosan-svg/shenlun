import json,re,sys
BASE='/home/user/shenlun/08_小题重写'
src=open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/kw3.py').read()
CFG=eval(src.split('CFG =')[1].split('\nPROB')[0])
s2=open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/stemkw.py').read()
KW=eval(s2.split('KW=')[1].split('\ntot=')[0])
BIG={'必答':'B','弱共识':'B','有':'B','可选':'O','单票':'O','个案':'C'}
for label,getrx in [('stemkw词',lambda sid,q,kws:'|'.join(map(re.escape,KW[(sid,q)]))),('kw3主词',lambda sid,q,kws:kws[0][1]),('kw3并集',lambda sid,q,kws:'|'.join(r for _,r in kws))]:
    A=Cn=Cc=Nn=0; up=down=0
    for sid,q,blk,kws in CFG:
        n=json.load(open(f'{BASE}/{sid}/对齐.json'))[q].get('n')
        if not (isinstance(n,int) and n>=3): continue
        ids=json.load(open(f'{BASE}/_pool/{sid}.json'))['ids']
        ali=json.load(open(f'{BASE}/{sid}/对齐.json'))[q]
        rx=re.compile(getrx(sid,q,kws))
        cls={}
        for p in ali['points']:
            if isinstance(p,dict) and isinstance(p.get('pool_id'),str):
                s=re.sub(r'[a-z]+$','',p['pool_id']); c=BIG.get(p.get('class'),'?')
                cls.setdefault(s,set()).add(c)
        sents={k:v for k,v in ids.items() if re.fullmatch(re.escape(blk)+r'-p\d+-\d+',k)}
        S=[s for s in sents if 'B' in cls.get(s,())]; N=[s for s in sents if not (cls.get(s,set())&{'B','O','C'})]
        a=sum(bool(rx.search(sents[s])) for s in S); c=sum(bool(rx.search(sents[s])) for s in N)
        A+=a;Cn+=len(S);Cc+=c;Nn+=len(N)
        pa=a/len(S) if S else 0; pc=c/len(N) if N else 0
        if pa>=1.5*pc and pa>0: up+=1
    print(f'{label} (2024-26, n>=3, 12题): 必答含词 {A}/{Cn}={A/Cn:.1%} 不给分 {Cc}/{Nn}={Cc/Nn:.1%}  >=1.5倍的题 {up}/12')
