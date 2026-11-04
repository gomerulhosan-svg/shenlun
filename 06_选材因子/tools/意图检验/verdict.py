import json
D='/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/'
R=json.load(open(D+'result.json')); M=json.load(open(D+'dims.json'))
def judge(v,d,nd):
    din,dout=v['din'],v['dout']
    A= (dout==0 and din>0) or (dout>0 and din/dout>=2)
    cov=d['w']/nd if nd else 0
    base=d['base'] or 0
    enr=v['enr']; enr_ok = enr=='inf' or (isinstance(enr,(int,float)) and enr>=1.5)
    sel = d['s']/d['exp'] if d['exp'] else (9 if d['s'] else 0)
    C= sel>=1.3 or enr_ok
    B= cov>=0.6
    if A and B and C: return ('成立(饱和)' if base>=0.7 else '成立'),cov
    if A and B and not C: return ('饱和' if base>=0.5 else '覆盖无选择'),cov
    if (not A) and B and C: return '部分(非集中)',cov
    if A and cov>=0.4 and C: return '部分',cov
    return '不成立',cov
rows=[]
for r in R:
    key='%s|%s'%(r['sid'],r['q']); m=M.get(key)
    if not m: continue
    nd=m['ANY']['nd']
    res={}
    for k,v in r['perk'].items():
        res[k]=judge(v,m[k],nd)+(v['nat'],)
    order={'成立':6,'成立(饱和)':5,'饱和':4,'部分(非集中)':3,'部分':2,'覆盖无选择':1,'不成立':0}
    ang=[(k,x) for k,x in res.items() if x[2] in ('角','U')]
    top=[(k,x) for k,x in res.items() if x[2]=='话']
    ba=max(ang,key=lambda t:(order[t[1][0]],t[1][1])) if ang else None
    bt=max(top,key=lambda t:(order[t[1][0]],t[1][1])) if top else None
    rows.append((r['sid'],r['q'],r['n'],ba,bt))
    def f(t):
        if not t: return '-'
        k,x=t; v=r['perk'][k]; d=m[k]
        return '%s:%s 邻覆盖%d/%d(基%.0f%%) 句覆盖%d/期望%.1f 密%s/%s 采%.0f%%/非%.0f%% 富%s'%(k,x[0],d['w'],nd,100*(d['base'] or 0),d['s'],d['exp'],v['din'],v['dout'],100*v['ra'],100*v['rb'],v['enr'])
    pu=[(k,x) for k,x in res.items() if x[2]=='推']
    bp=max(pu,key=lambda t:(order[t[1][0]],t[1][1])) if pu else None
    print(r['sid'],r['q'],'n=%s'%r['n'],'| 角→',f(ba),'| 话→',f(bt),'| 推→',f(bp))
    rows[-1]=rows[-1]+(bp,)
json.dump([(a,b,c,d,e,f) for a,b,c,d,e,f in rows],open(D+'verdict.json','w'),ensure_ascii=False)
