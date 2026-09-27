import json,re,sys
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from lib import *
src=open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/stemkw.py').read()
KW=eval(src.split('KW=')[1].split('\ntot=')[0])
def nch(t): return len(re.sub(r'\s','',t))
for q in qs:
    k=(q['set_id'],q['q'])
    if k not in KW: continue
    blocks=json.load(open(f'{B}/_pool/{q["set_id"]}.json'))['blocks']
    pat=re.compile('|'.join(map(re.escape,KW[k])))
    kin=sum(len(pat.findall('\n'.join(blocks[b]))) for b in q['blocks'])
    din=kin/sum(nch(''.join(blocks[b])) for b in q['blocks'])*1000
    oth={b:len(pat.findall('\n'.join(v)))/nch(''.join(v))*1000 for b,v in blocks.items() if b not in q['blocks']}
    Lout=sum(nch(''.join(v)) for b,v in blocks.items() if b not in q['blocks'])
    pooled=sum(len(pat.findall('\n'.join(v))) for b,v in blocks.items() if b not in q['blocks'])/Lout*1000
    mxb=max(oth,key=oth.get)
    s_pool= kin>=3 and din>3*pooled; s_each= kin>=3 and din>3*oth[mxb]
    if s_pool!=s_each or not s_pool:
        print(k,KW[k],'则内',kin,'%.1f'%din,'其他合并%.1f'%pooled,'最高他则',mxb,'%.1f'%oth[mxb],'合并口径',s_pool,'逐则口径',s_each)
