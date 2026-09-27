import json,re,sys,collections,random,math
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from lib import *
src=open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/stemkw.py').read()
KW=eval(src.split('KW=')[1].split('\ntot=')[0])
rows=[]
for q in qs:
    k=(q['set_id'],q['q'])
    if k not in KW: continue
    al,core,hit,sents=load_q(q)
    n=al.get('n') if isinstance(al,dict) else None
    n=int(n) if str(n).isdigit() else n
    pat=re.compile('|'.join(map(re.escape,KW[k])))
    sd=dict(sents)
    C=[s for s,v in sents if s in core]; N=[s for s,v in sents if s not in hit]
    a=sum(bool(pat.search(sd[s])) for s in C); b=len(C)-a
    c=sum(bool(pat.search(sd[s])) for s in N); d=len(N)-c
    rows.append(dict(k=k,n=n,qtype=q['qtype'],a=a,b=b,c=c,d=d,C=C,N=N,pat=pat,sd=sd))
def pooled(rs):
    A=sum(r['a'] for r in rs);Cn=sum(r['a']+r['b'] for r in rs);Cc=sum(r['c'] for r in rs);Nn=sum(r['c']+r['d'] for r in rs)
    # Mantel-Haenszel OR
    num=sum(r['a']*r['d']/(r['a']+r['b']+r['c']+r['d']) for r in rs if r['a']+r['b']+r['c']+r['d'])
    den=sum(r['b']*r['c']/(r['a']+r['b']+r['c']+r['d']) for r in rs if r['a']+r['b']+r['c']+r['d'])
    return A,Cn,Cc,Nn,(num/den if den else float('inf'))
def perm(rs,it=20000,seed=1):
    random.seed(seed)
    obs=pooled(rs); obsdiff=obs[0]/obs[1]-obs[2]/obs[3]
    ge=0; diffs=[]
    for _ in range(it):
        A=Cn=Cc=Nn=0
        for r in rs:
            lab=[1]*(r['a']+r['c'])+[0]*(r['b']+r['d'])
            random.shuffle(lab)
            nc=r['a']+r['b']
            A+=sum(lab[:nc]); Cc+=sum(lab[nc:]); Cn+=nc; Nn+=len(lab)-nc
        dd=A/Cn-Cc/Nn; diffs.append(dd)
        if dd>=obsdiff: ge+=1
    diffs.sort()
    return obsdiff,ge/it,diffs[int(.025*it)],diffs[int(.975*it)]
def show(name,rs):
    A,Cn,Cc,Nn,mh=pooled(rs)
    od,p,lo,hi=perm(rs)
    print(f'{name}: 题数{len(rs)} 必答含词 {A}/{Cn}={A/Cn:.1%}  不给分含词 {Cc}/{Nn}={Cc/Nn:.1%}  差{od:+.1%}  MH-OR={mh:.2f}  置换单侧p={p:.3f} 零分布95%区间[{lo:+.1%},{hi:+.1%}]')
show('全部29',rows)
show('n>=3',[r for r in rows if isinstance(r['n'],int) and r['n']>=3])
show('n<=2',[r for r in rows if not(isinstance(r['n'],int) and r['n']>=3)])
show('n=0',[r for r in rows if r['n']==0])
show('n=1',[r for r in rows if r['n']==1])
# informative: keyword appears in >=3 sentences of designated
inf=[r for r in rows if r['a']+r['c']>=3]
show('含词句>=3(可检验)',inf)
show('n>=3且含词句>=3',[r for r in inf if isinstance(r['n'],int) and r['n']>=3])
print()
print('逐题（n, 必答含词率, 不给分含词率, 比值）')
for r in rows:
    pc=r['a']/(r['a']+r['b']) if r['a']+r['b'] else float('nan'); pn=r['c']/(r['c']+r['d']) if r['c']+r['d'] else float('nan')
    print(r['k'],'n=',r['n'],r['qtype'],f"{r['a']}/{r['a']+r['b']}={pc:.0%}",f"{r['c']}/{r['c']+r['d']}={pn:.0%}", 'ratio=%.1f'%(pc/pn) if pn>0 else ('inf' if pc>0 else '-'))
