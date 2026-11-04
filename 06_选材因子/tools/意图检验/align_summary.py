import json,glob,os,re,collections
B='/home/user/shenlun/08_小题重写'
qs=json.load(open(B+'/questions.json'))
qmap={(q['set_id'],q['q']):q for q in qs}
for f in sorted(glob.glob(B+'/*/对齐.json')):
    sid=f.split('/')[-2]
    d=json.load(open(f))
    for qn,v in d.items():
        if not isinstance(v,dict):
            print(sid,qn,'NONDICT',str(v)[:80]);continue
        pts=v.get('points',[])
        if not isinstance(pts,list):
            print(sid,qn,'points not list',str(pts)[:80]);continue
        c=collections.Counter()
        for p in pts:
            if isinstance(p,dict): c[p.get('class','?')]+=1
            else: c['str']+=1
        keys=set()
        for p in pts:
            if isinstance(p,dict): keys|=set(p.keys())
        q=qmap.get((sid,qn),{})
        print(sid,qn,q.get('points'),q.get('qtype'),'n=',v.get('n'),dict(c),sorted(keys))
