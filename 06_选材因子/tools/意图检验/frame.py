# 首尾框定：指定材料的前2句/后2句（内容句）里有没有角度词/话题词；这些句是否采分句
import json,re,sys
sys.path.insert(0,'/home/user/shenlun/08_小题重写/tools')
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from common import sentences
from kw import SPEC
B='/home/user/shenlun/08_小题重写/'
ZERO={'无票','零票'}
def nchar(t): return len(re.sub(r'\s','',t))
Q=json.load(open(B+'questions.json'))
for (sid,q),(des,kws) in SPEC.items():
    pool=json.load(open(B+'_pool/'+sid+'.json'))
    al=json.load(open(B+sid+'/对齐.json'))[q]
    sc=set(re.match(r'(.+?-p\d+-\d+)',p['pool_id']).group(1) for p in al['points'] if isinstance(p,dict) and p.get('class') not in ZERO)
    allre='|'.join('(?:%s)'%r for _,r,n in kws if n in('角','话'))
    head=[];tail=[]
    for b in des:
        ss=[]
        for pi,para in enumerate(pool['blocks'][b],1):
            for si,s in enumerate(sentences(para),1):
                if nchar(s)>=8 and not re.match(r'\s*(时间|地点)[：:]',s): ss.append(('%s-p%d-%d'%(b,pi,si),s))
        head+=ss[:2]; tail+=ss[-2:]
    def f(lst):
        o=[]
        for i,s in lst:
            if re.search(allre,s): o.append(i+('★' if i in sc else '·'))
        return o
    qt=[x for x in Q if x['set_id']==sid and x['q']==q][0]['qtype']
    print(sid,q,qt,'首:',f(head),'尾:',f(tail))
