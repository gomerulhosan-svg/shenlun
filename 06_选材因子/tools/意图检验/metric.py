import json,re,sys
sys.path.insert(0,'/home/user/shenlun/08_小题重写/tools')
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from common import sentences
from kw import SPEC
B='/home/user/shenlun/08_小题重写/'
ZERO={'无票','零票'}
def nchar(t): return len(re.sub(r'\s','',t))
out=[]
verbose='-v' in sys.argv
only=[a for a in sys.argv[1:] if not a.startswith('-')]
for (sid,q),(des,kws) in SPEC.items():
    if only and sid not in only: continue
    pool=json.load(open(B+'_pool/'+sid+'.json'))
    al=json.load(open(B+sid+'/对齐.json'))[q]
    n=al.get('n')
    pts=[p for p in al['points'] if isinstance(p,dict) and p.get('class') not in ZERO]
    ptsent={}
    for p in pts:
        m=re.match(r'(.+?-p\d+-\d+)([a-z]?)$',p['pool_id'])
        ptsent.setdefault(m.group(1),[]).append(p['pool_id'])
    allre='|'.join('(?:%s)'%r for _,r,_ in kws)
    din=dout=0; cin=cout=0; per={k:[0,0] for k,_,_ in kws}
    for b,paras in pool['blocks'].items():
        t=''.join(paras); c=nchar(t)
        hits=len(re.findall(allre,t))
        if b in des: din+=hits; cin+=c
        else: dout+=hits; cout+=c
        for k,r,_ in kws:
            per[k][0 if b in des else 1]+=len(re.findall(r,t))
    rows=[]
    for b in des:
        for pi,para in enumerate(pool['blocks'][b],1):
            for si,s in enumerate(sentences(para),1):
                sid_='%s-p%d-%d'%(b,pi,si)
                if nchar(s)<8: continue
                hk=[k for k,r,_ in kws if re.search(r,s)]
                rows.append((sid_,sid_ in ptsent,hk,s.strip()))
    S=[r for r in rows if r[1]]; NS=[r for r in rows if not r[1]]
    SK=[r for r in S if r[2]]; NSK=[r for r in NS if r[2]]
    # 点级：句含关键词 / 分句含关键词
    ids=pool['ids']
    pin=[p for p in pts if p['pool_id'].split('-')[0] in des]
    ids=pool['ids']
    pt_sent=sum(1 for p in pin if re.search(allre, ids.get(re.match(r'(.+?-p\d+-\d+)',p['pool_id']).group(1),'')))
    pt_cl=sum(1 for p in pin if re.search(allre, ids.get(p['pool_id'],'')))
    dens_in=1000*din/cin; dens_out=1000*dout/cout if cout else 0
    rS=len(SK)/len(S) if S else 0; rN=len(NSK)/len(NS) if NS else 0
    perk={}
    for k,r,nat in kws:
        a=sum(1 for x in S if k in x[2]); b=sum(1 for x in NS if k in x[2])
        ra=a/len(S) if S else 0; rb=b/len(NS) if NS else 0
        pc=sum(1 for p in pin if re.search(r, ids.get(re.match(r'(.+?-p\d+-\d+)',p['pool_id']).group(1),'')))
        perk[k]=dict(nat=nat,a=a,b=b,ra=round(ra,2),rb=round(rb,2),enr=round(ra/rb,1) if rb else ('inf' if ra else None),din=round(1000*per[k][0]/cin,1),dout=round(1000*per[k][1]/cout,1) if cout else 0,pts=pc)
    rec=dict(perk=perk,sid=sid,q=q,n=n,des=''.join(des),kws=[k for k,_,_ in kws],
        dens_in=round(dens_in,1),dens_out=round(dens_out,1),ratio=round(dens_in/dens_out,1) if dens_out else None,
        per={k:(round(1000*v[0]/cin,1),round(1000*v[1]/cout,1) if cout else 0) for k,v in per.items()},
        nsent=len(rows),nS=len(S),nSK=len(SK),nNS=len(NS),nNSK=len(NSK),
        kwsent=len(SK)+len(NSK), rS=round(rS,2), rN=round(rN,2), enr=round(rS/rN,1) if rN else None,
        npts=len(pin),pt_sent=pt_sent,pt_cl=pt_cl, outside=len(pts)-len(pin))
    out.append(rec)
    if verbose:
        print('\n=== %s %s n=%s des=%s'%(sid,q,n,des), json.dumps({k:rec[k] for k in ['dens_in','dens_out','ratio','per','nS','nSK','nNS','nNSK','rS','rN','enr','npts','pt_sent','pt_cl']},ensure_ascii=False))
        for r in rows:
            if r[2]: print('  %s %s %s | %s'%(r[0],'★' if r[1] else '·','/'.join(r[2]),r[3][:110]))
json.dump(out,open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/result.json','w'),ensure_ascii=False,indent=1)
print()
print('套 题 n 材料 | 密度内/外(倍) | 采分句含kw | 非采分句含kw | 富集 | 点(句级/分句级)')
for r in out:
    print('%s %s n=%s %s | %s/%s (%s) | %d/%d=%.0f%% | %d/%d=%.0f%% | %s | %d/%d句 %d分句 外%d'%(r['sid'],r['q'],r['n'],r['des'],r['dens_in'],r['dens_out'],r['ratio'],r['nSK'],r['nS'],100*r['rS'],r['nNSK'],r['nNS'],100*r['rN'],r['enr'],r['pt_sent'],r['npts'],r['pt_cl'],r['outside']))
