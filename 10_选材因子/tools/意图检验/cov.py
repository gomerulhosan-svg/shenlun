import sys
from parse import load,norm,SETS
def cov(q,p,mn=4):
    q=norm(q);p=norm(p);i=0;c=0
    while i<len(q):
        k=0
        for L in range(len(q)-i,mn-1,-1):
            if q[i:i+L] in p: k=L;break
        if k: c+=k;i+=k
        else: i+=1
    return c,len(q)
def best(s,q,n=3):
    mats,_=load(s);r=[]
    for m,ps in mats.items():
        for i,t in ps.items():
            c,L=cov(q,t);r.append((c,m,i,L))
    r.sort(reverse=True)
    return ' | '.join(f'材料{m}〔{i}〕{c}/{L}={c*100//L}%' for c,m,i,L in r[:n])
if __name__=='__main__':
    s=sys.argv[1]
    for q in sys.argv[2:]: print(f'「{q}」->',best(s,q))
