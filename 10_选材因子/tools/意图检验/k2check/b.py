import json,re,sys,math
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from lib import *
from math import comb
src=open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/stemkw.py').read()
KW=eval(src.split('KW=')[1].split('\ntot=')[0])
def nch(t): return len(re.sub(r'\s','',t))
lock=0; lockw=0; seen=set(); f3=0; f3n=0; exp_sum=0; rows=[]
for q in qs:
    k=(q['set_id'],q['q'])
    if k not in KW: continue
    pool=json.load(open(f'{B}/_pool/{q["set_id"]}.json'))
    blocks=pool['blocks']; ids=pool['ids']
    pat=re.compile('|'.join(map(re.escape,KW[k])))
    kin=sum(len(pat.findall(''.join(blocks[b]))) for b in q['blocks'])
    din=kin/sum(nch(''.join(blocks[b])) for b in q['blocks'])*1000
    others={b:len(pat.findall(''.join(v)))/nch(''.join(v))*1000 for b,v in blocks.items() if b not in q['blocks'] and b!='导'}
    mx=max(others.values()) if others else 0
    strict = kin>=3 and din>3*mx
    lock+=strict
    # first-three-paragraph test per designated material (each block separately; dedupe identical material text)
    for b in q['blocks']:
        txt=''.join(blocks[b])
        key=(txt[:50])
        if key in seen: continue
        seen.add(key)
        sents=[(s,v) for s,v in ids.items() if re.fullmatch(re.escape(b)+r'-p(\d+)-\d+',s)]
        Ns=len(sents); n3=sum(1 for s,v in sents if int(s.split('-p')[1].split('-')[0])<=3)
        K=[s for s,v in sents if pat.search(v)]
        k3=[s for s in K if int(s.split('-p')[1].split('-')[0])<=3]
        npara=len(blocks[b]); c3=nch(''.join(blocks[b][:3]))/nch(txt)
        if not K: 
            rows.append((k,b,npara,Ns,n3,0,0,None,c3)); continue
        f3n+=1; f3+=bool(k3)
        # null: K sentences placed at random among Ns sentences
        pnull=1-comb(Ns-n3,len(K))/comb(Ns,len(K)) if Ns-n3>=len(K) else 1.0
        exp_sum+=pnull
        rows.append((k,b,npara,Ns,n3,len(K),len(k3),round(pnull,2),round(c3,2)))
print('严口径 >=3次且密度>其他每一则的3倍:',lock,'/29')
print('去重后材料数(含词>=1):',f3n,' 前三段含词:',f3,' 随机放置的期望:',round(exp_sum,1))
for r in rows: print(r)
