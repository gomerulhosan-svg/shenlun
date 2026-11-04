exec(open('common.py').read())
NP=5000
names=HF
# role: 问题一 selected examples and where they sit
sel=[c for c in kept if c['st']=='选用']
by=defaultdict(list)
for c in kept: by[c['unit']].append(c)
for role in ['问题一材料','问题二材料','作文材料']:
    rs=[c for c in sel if c['role']==role]
    inpart=[c for c in rs if any(x['st']=='未选' for x in by[c['unit']])]
    print(role,'selected',len(rs),'in articles with unselected',len(inpart), Counter(c['paper'] for c in rs))
# within-article: 作文材料-only (drop selected examples of other roles)
for lab,filt in [('只留作文材料的选用例子',lambda c:c['st']=='未选' or c['role']=='作文材料'),
                 ('只留问题一/二材料的选用例子',lambda c:c['st']=='未选' or c['role'] in('问题一材料','问题二材料'))]:
    cs=[c for c in kept if filt(c)]
    for who in 'AB':
        r=mh(items(cs),names,who,NP)
        m=r['_meta']
        print('\n##',lab,who,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
        for n in names: print('   %-10s %s   (全部: %.0f%% vs %.0f%%)'%(n,fmt(r[n]),100*r[n]['all_sel'],100*r[n]['all_un']))
# 问题一 selected vs unselected of the SAME PAPER (paper-level strata, weaker control)
cs=[c for c in kept if c['st']=='未选' or c['role']=='问题一材料']
cs=[c for c in cs if c['paper'] in {x['paper'] for x in cs if x['st']=='选用'}]
for who in 'AB':
    r=mh(items(cs,lambda c:c['paper']),names+['贴合度=2'],who,NP)
    m=r['_meta']; print('\n## 问题一选用 vs 同卷未选（层=卷）',who,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
    for n in names+['贴合度=2']: print('   %-10s %s'%(n,fmt(r[n])))
# leave-one-paper-out
print('\n## 去掉一张卷（甲 / 乙 文章内差值 pp）')
papers=S.PAPERS
hdr='%-10s'%'去掉' + ''.join('%16s'%n for n in names)
print(hdr)
for p in [None]+papers:
    cs=[c for c in kept if c['paper']!=p]
    ra=mh(items(cs),names,'A',0); rb=mh(items(cs),names,'B',0)
    print('%-10s'%(p or '无')+''.join('%16s'%('%+.1f/%+.1f'%(100*ra[n]['mh'],100*rb[n]['mh'])) for n in names))
# per-paper
print('\n## 各卷单独（甲/乙），层数 sel/un')
for p in papers:
    cs=[c for c in kept if c['paper']==p]
    ra=mh(items(cs),names,'A',0); rb=mh(items(cs),names,'B',0)
    m=ra['_meta']
    if m['层数']==0: print(p,'无可比文章'); continue
    print('%-10s %d篇 %d/%d '%(p,m['层数'],m['选用'],m['未选'])+''.join('%16s'%('%+.0f/%+.0f'%(100*ra[n]['mh'],100*rb[n]['mh'])) for n in names))
# leave-one-article-out max influence
print('\n## 去掉一篇文章后的范围（甲）')
units=sorted({c['unit'] for c in kept})
rng={n:[] for n in names}
for u in units:
    cs=[c for c in kept if c['unit']!=u]
    r=mh(items(cs),names,'A',0)
    if r['_meta']['层数']<41: 
        for n in names: rng[n].append((r[n]['mh'],u))
for n in names: 
    v=sorted(rng[n]); print('  %-10s min %+.1f (%s) max %+.1f (%s)'%(n,100*v[0][0],v[0][1],100*v[-1][0],v[-1][1]))
