import sys
from parse import load,norm
s=sys.argv[1]; mats,_=load(s)
for h in sys.argv[2:]:
    hits=[f'{m}〔{i}〕' for m,ps in mats.items() for i,t in ps.items() if norm(h) in norm(t)]
    print(f'「{h}」:',' '.join(hits) or '无')
