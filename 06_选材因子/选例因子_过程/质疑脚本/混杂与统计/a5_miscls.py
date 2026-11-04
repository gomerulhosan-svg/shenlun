exec(open('common.py').read())
NP=5000
PACK='/home/user/shenlun/10_选材因子/溯源包'
blindtext={}
for p in S.PAPERS:
    b=json.load(open(os.path.join(D,'blind',p+'.json')))
    for a in b['文章']:
        for s in a['段']: blindtext[(p,s['id'])]=s['文']
casesraw={}
for p in S.PAPERS:
    for c in json.load(open(os.path.join(D,'out','cases_%s.json'%p)))['例子']: casesraw[c['id']]=c
mat={}
for p in S.PAPERS:
    t=open(os.path.join(PACK,p+'_材料与题干.md')).read().split('### 题干')[0]
    t=t.split('### 给定材料',1)[-1]
    mat[p]=S.norm(t)
def ngr(t,n): return {t[i:i+n] for i in range(len(t)-n+1)}
matg4={p:ngr(t,4) for p,t in mat.items()}
matg6={p:ngr(t,6) for p,t in mat.items()}
def cov(t,g,n):
    if len(t)<n: return 0
    m=[False]*len(t)
    for i in range(len(t)-n+1):
        if t[i:i+n] in g:
            for j in range(i,i+n): m[j]=True
    return sum(m)/len(t)
NUM=re.compile(r'\d[\d\.]*\s*(?:万|亿|千|百)?(?:余|多)?(?:元|吨|亩|个|家|项|人|户|公里|千米|米|平方米|%|％|倍|座|条|台|艘|种|名|所|次|年)')
GENERIC={'广东省','广东','广州市','深圳市','全省','我省','省委','省政府','国家','中国','我国'}
flag={}
rows=[]
for c in kept:
    txt=''.join(blindtext[(c['paper'],s)] for s in c['segs'])
    nt=S.norm(txt)
    c4=cov(nt,matg4[c['paper']],4); c6=cov(nt,matg6[c['paper']],6)
    nums={m.group(0).replace(' ','') for m in NUM.finditer(txt)}
    numhit=[x for x in nums if x in mat[c['paper']] and len(re.sub(r'\D','',x))>=2]
    subj=casesraw[c['id']]['主体']
    subjs=[x for x in re.split(r'[、，,（）()与和及“”"]',subj) if len(S.norm(x))>=3 and S.norm(x) not in GENERIC]
    subjhit=[x for x in subjs if S.norm(x) in mat[c['paper']]]
    c['c4']=c4; c['c6']=c6; c['numhit']=numhit; c['subjhit']=subjhit
    rows.append(c)
for st in ['选用','未选']:
    cs=[c for c in kept if c['st']==st]
    print(st,len(cs),'6字覆盖≥30%%: %d  4字覆盖≥50%%: %d  数字命中≥1: %d  主体命中: %d'%(
        sum(c['c6']>=0.3 for c in cs),sum(c['c4']>=0.5 for c in cs),sum(len(c['numhit'])>=1 for c in cs),sum(len(c['subjhit'])>=1 for c in cs)))
sus=[c for c in kept if c['st']=='未选' and (c['c6']>=0.3 or len(c['numhit'])>=1 or len(c['subjhit'])>=1)]
print('可疑未选(可能改写后被用):',len(sus))
for c in sorted(sus,key=lambda c:-c['c6'])[:25]:
    print('  %s c6=%.2f c4=%.2f num=%s subj=%s | %s'%(c['id'],c['c6'],c['c4'],c['numhit'][:3],c['subjhit'],casesraw[c['id']]['主体']+'：'+casesraw[c['id']]['做法'][:40]))
json.dump({c['id']:{'c6':c['c6'],'c4':c['c4'],'num':c['numhit'],'subj':c['subjhit']} for c in kept},open('a5_flags.json','w'),ensure_ascii=False)
names=HF
for lab,cs in [('去掉可疑未选',[c for c in kept if c not in sus]),
               ('可疑未选改判为选用',None)]:
    if cs is None:
        ids={id(c) for c in sus}
        cs=[dict(c,st='选用') if id(c) in ids else c for c in kept]
    for w in 'AB':
        r=mh(items(cs),names,w,NP); m=r['_meta']
        print('\n##',lab,w,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
        for n in names: print('   %-10s %s'%(n,fmt(r[n])))
# features of suspicious vs other unselected
print('\n可疑未选 vs 其余未选 的特征率（甲）')
oth=[c for c in kept if c['st']=='未选' and c not in sus]
for n in names+['贴合度=2','量化成效']:
    print('  %-10s 可疑 %.0f%%  其余 %.0f%%  选用 %.0f%%'%(n,100*statistics.mean(val(c,n) for c in sus),100*statistics.mean(val(c,n) for c in oth),100*statistics.mean(val(c,n) for c in kept if c['st']=='选用')))
