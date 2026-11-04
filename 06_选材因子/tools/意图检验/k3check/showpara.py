import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from parse import load
s=sys.argv[1]; mats,_=load(s)
for a in sys.argv[2:]:
    m,i=a.split(':'); 
    print(f'--- {s} 材料{m}〔{i}〕'); print(mats[m][int(i)])
