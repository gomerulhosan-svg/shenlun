import sys,re
sys.path.insert(0,'..')
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from parse import load,norm,SETS
BOIL=['请结合给定材料','请根据全部给定材料','仅限给定材料','联系实际','联系广东实际','自拟题目','自拟标题','撰写一篇议论文','撰写一篇策论文','进行深入思考','围绕','的主题','这一主题','主题','习近平总书记指出','习近平总书记强调','请你结合给定材料','结合给定材料','50分','50 分']
for s in SETS:
    mats,stem=load(s)
    q3=stem[stem.find('**问题三**'):].replace('**问题三**','')
    q3=q3.split('要求')[0]
    t=norm(q3)
    for b in BOIL: t=t.replace(norm(b),'|')
    allp=[(m,i,norm(x)) for m,ps in mats.items() for i,x in ps.items()]
    # greedy maximal substrings
    res=[];i=0
    while i<len(t):
        best=0;where=None
        for L in range(len(t)-i,5,-1):
            sub=t[i:i+L]
            if '|' in sub: continue
            hits=[f'{m}〔{k}〕' for m,k,x in allp if sub in x]
            if hits: best=L;where=hits;break
        if best: res.append((t[i:i+best],where)); i+=best
        else: i+=1
    mx=max([len(r[0]) for r in res],default=0)
    print(f'== {s} 最长逐字片段={mx}')
    for sub,w in res: print(f'   {len(sub):2d} 「{sub}」 in {" ".join(w[:6])}{" ..." if len(w)>6 else ""} (共{len(w)}段)')
