exec(open('common.py').read())
NP=5000
fl=json.load(open('a5_flags.json'))
def strongnum(x):
    if re.fullmatch(r'\d{4}年',x): return False
    return len(re.sub(r'\D','',x))>=2
for c in kept:
    f=fl[c['id']]; c['sn']=[x for x in f['num'] if strongnum(x)]; c['c4']=f['c4']; c['c6']=f['c6']
sus=[c for c in kept if c['st']=='未选' and (c['c4']>=0.35 or len(c['sn'])>=2 or (len(c['sn'])>=1 and c['c4']>=0.25))]
print('强可疑未选',len(sus), Counter(c['paper'] for c in sus))
casesraw={}
for p in S.PAPERS:
    for x in json.load(open(os.path.join(D,'out','cases_%s.json'%p)))['例子']: casesraw[x['id']]=x
for c in sus[:40]: print('  %s c4=%.2f nums=%s | %s'%(c['id'],c['c4'],c['sn'][:4],(casesraw[c['id']]['主体']+'：'+casesraw[c['id']]['做法'])[:50]))
ids={id(c) for c in sus}
for lab,cs in [('去掉强可疑未选',[c for c in kept if id(c) not in ids])]:
    for w in 'AB':
        r=mh(items(cs),HF,w,NP); m=r['_meta']
        print('\n##',lab,w,'strata=%d sel=%d un=%d'%(m['层数'],m['选用'],m['未选']))
        for n in HF: print('   %-10s %s'%(n,fmt(r[n])))
