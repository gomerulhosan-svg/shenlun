import re
from parse import load,SETS
for s in SETS:
    mats,_=load(s)
    print('=====',s)
    for m in ['一','二']:
        ps=mats.get(m,{})
        nyao=sum(len(re.findall(r'要(?![求素点闻])',t)) for t in ps.values())
        print(f' 材料{m}: 段数{len(ps)} “要”字{nyao}')
        for i,t in ps.items():
            for sent in re.split(r'[。！？；]',t):
                if sent.count('、')>=2 or re.search(r'一是|第一|四个|五个|六个|“六',sent):
                    print(f'   〔{i}〕{sent.strip()[:150]}')
