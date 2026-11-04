# 维度路标率：终稿答案每个"要点"的来源句（及同段前后一句）里有没有关键词
import json,re,sys,os
sys.path.insert(0,'/home/user/shenlun/08_小题重写/tools')
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/kwseed_mine')
from common import sentences
from kw import SPEC
B='/home/user/shenlun/08_小题重写/'
QN={'问题一':'Q1','问题二':'Q2','问题三':'Q3','问题四':'Q4','问题五':'Q5'}
CN='零一二三四五六七八九十'
def nchar(t): return len(re.sub(r'\s','',t))
res={}
verbose='-v' in sys.argv
only=[a for a in sys.argv[1:] if not a.startswith('-')]
for (sid,q),(des,kws) in SPEC.items():
    if only and sid not in only: continue
    f=B+sid+'/'+QN[q]+'.md'
    if not os.path.exists(f): continue
    pool=json.load(open(B+'_pool/'+sid+'.json'))
    sent={}
    for b,paras in pool['blocks'].items():
        for pi,para in enumerate(paras,1):
            ss=sentences(para)
            for si,s in enumerate(ss,1): sent[(b,pi,si)]=s
    txt=open(f).read()
    parts=re.split(r'(?m)^### ',txt)[1:]
    dims=[]
    for p in parts:
        title=p.split('\n')[0].strip()
        refs=set()
        for line in p.split('\n'):
            if '来源' not in line: continue
            for m in re.finditer(r'材料([一二三四五六七八九十]+)\s*第\s*(\d+)\s*段(?:\s*第\s*(\d+)\s*句)?',line):
                refs.add((m.group(1),int(m.group(2)),int(m.group(3)) if m.group(3) else 0))
        if refs: dims.append((title,refs))
    out={}
    for k,r,nat in kws+[('ANY','|'.join('(?:%s)'%x for _,x,_ in kws),'')]:
        cs=cw=cp=0; det=[]
        for title,refs in dims:
            hs=hw=hp=False
            for (b,pi,si) in refs:
                para=pool['blocks'].get(b,[])
                if pi-1<len(para) and re.search(r,para[pi-1]): hp=True
                cands=[si] if si else [x[2] for x in sent if x[0]==b and x[1]==pi]
                for s in cands:
                    if re.search(r,sent.get((b,pi,s),'')): hs=True
                    for d in (-1,0,1):
                        if re.search(r,sent.get((b,pi,s+d),'')): hw=True
            cs+=hs; cw+=hw; cp+=hp; det.append((title[:14],hs,hw,hp))
        # 基线：指定材料中所有内容句，±1 窗口含词的比例
        tot=hit=hit1=0
        for (b,pi,si),s in sent.items():
            if b not in des or nchar(s)<8: continue
            tot+=1
            if re.search(r,s): hit1+=1
            if any(re.search(r,sent.get((b,pi,si+d),'')) for d in (-1,0,1)): hit+=1
        b1=hit1/tot if tot else 0
        exp=0
        for title,refs in dims:
            ks=set()
            for (b,pi,si) in refs:
                if b not in des: continue
                if si: ks.add((b,pi,si))
                else: ks.update(x for x in sent if x[0]==b and x[1]==pi)
            ks=[x for x in ks if nchar(sent.get(x,''))>=8]
            if ks: exp+=1-(1-b1)**len(ks)
        out[k]=dict(nat=nat,nd=len(dims),s=cs,w=cw,p=cp,base=round(hit/tot,2) if tot else None,base1=round(b1,2),exp=round(exp,2),det=det)
    res['%s|%s'%(sid,q)]=out
    if verbose:
        print('\n==',sid,q,'维度数',len(dims))
        for k,v in out.items():
            print('   %-12s %s 句%d 邻%d 段%d /%d  基线(±1)%.0f%%'%(k,v['nat'],v['s'],v['w'],v['p'],v['nd'],100*(v['base'] or 0)))
        for t,refs in dims: print('     ',t[:20],sorted(refs))
json.dump(res,open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/kwseed_mine/dims.json','w'),ensure_ascii=False,indent=1)
if not verbose:
    for key,out in res.items():
        a=out['ANY']
        print(key,'维度',a['nd'],' | '.join('%s[%s]句%d(基%.0f%%)/邻%d(基%.0f%%)'%(k,v['nat'],v['s'],100*(v['base1'] or 0),v['w'],100*(v['base'] or 0)) for k,v in out.items()))
