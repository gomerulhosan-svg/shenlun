import json,re,sys
sys.path.insert(0,'/home/user/shenlun/08_小题重写/tools')
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from common import sentences
from kw import SPEC
B='/home/user/shenlun/08_小题重写/'
Q=json.load(open(B+'questions.json'))
def clean(t): return re.sub(r'[\s，。、“”‘’：；！？（）()《》…—\-]','',t)
for (sid,q),(des,kws) in SPEC.items():
    st=[x for x in Q if x['set_id']==sid and x['q']==q][0]['stem']
    st=re.split(r'要求|（\d+\s*分|\(\d+\s*分',st)[0]
    st=re.sub(r'^.{0,4}根据(给定)?材料\s*\d*[，,]?|请|概括|简要|谈谈|分析说明|简述','',st)
    cs=clean(st)
    pool=json.load(open(B+'_pool/'+sid+'.json'))
    best=('',None)
    for b,paras in pool['blocks'].items():
        for pi,para in enumerate(paras,1):
            for si,s in enumerate(sentences(para),1):
                c=clean(s)
                # longest common substring
                L=0;bs=''
                for i in range(len(cs)):
                    for j in range(i+L+1,len(cs)+1):
                        if cs[i:j] in c:
                            if j-i>L: L=j-i;bs=cs[i:j]
                        else: break
                if L>len(best[0]): best=(bs,'%s-p%d-%d%s(共%d段)'%(b,pi,si,'*' if b in des else '',len(paras)))
    print(sid,q,len(best[0]),best[0],best[1])
