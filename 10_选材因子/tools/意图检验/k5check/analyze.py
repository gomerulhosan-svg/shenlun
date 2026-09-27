import json,re,sys,collections
sys.path.insert(0,'.')
from maps import M
R='/home/user/shenlun/08_小题重写/'
qs={(q['set_id'],q['q']):q for q in json.load(open(R+'questions.json'))}
CN={'必答':'必','可选':'可','个案':'个','弱共识':'必','单票':'可','无票':'个','零票':'个','不计票':'个','有':'必','没有':'个'}
def label(m,blk,p,s,cl=''):
    if blk!=m['block']: return m.get('other','其他材料|—')
    for k,d in ((f'{p}-{s}{cl}','clauses'),(f'{p}-{s}','sents')):
        if k in m.get(d,{}): return m[d][k]
    return m['paras'].get(p,'??|?')
def pid_parse(pid):
    mm=re.match(r'(.+)-p(\d+)-(\d+)([a-z]*)$',pid)
    return mm.group(1),int(mm.group(2)),int(mm.group(3)),mm.group(4)
out={}
for (s,q),m in M.items():
    qt=qs[(s,q)]['qtype']; d=json.load(open(R+f'{s}/对齐.json'))[q]
    wenti = qt=='T-问对'; duice = qt=='T-对策'
    cnt=collections.defaultdict(lambda: collections.Counter())
    for p in d['points']:
        if not isinstance(p,dict): continue
        blk,pp,ss,cl=pid_parse(p['pool_id'])
        lab=label(m,blk,pp,ss,cl)
        note=str(p.get('note',''))
        if 'side' in p: side=p['side']
        elif wenti: side='对策' if note.startswith('对策') else '问题'
        elif duice: side='对策'
        else: side='点'
        c=CN.get(p['class'],p['class'])
        cnt[lab][side+c]+=1
    # order of appearance
    order=[]
    for pnum in sorted(m['paras']):
        labs=[m['paras'][pnum]]+[v for k,v in list(m.get('sents',{}).items())+list(m.get('clauses',{}).items()) if int(k.split('-')[0])==pnum]
        for l in labs:
            if l not in order: order.append(l)
    for l in cnt:
        if l not in order: order.append(l)
    # items from Qn.md
    txt=open(R+f"{s}/{m['qf']}.md",encoding='utf-8').read()
    body=txt.split('## 逐条解析',1)[1] if '## 逐条解析' in txt else ''
    items=collections.OrderedDict(); cur=None
    for ln in body.split('\n'):
        if ln.startswith('### '): cur=ln[4:].strip(); items[cur]=collections.Counter(); continue
        if cur and ln.startswith('- 来源'):
            curmat=None;curp=None
            for mm in re.finditer(r'(?:材料([一二三四五六七八九十]+))?(?:第\s*(\d+)\s*段)?第\s*(\d+)\s*句|同段第\s*(\d+)\s*句',ln):
                if mm.group(4):
                    sn=int(mm.group(4))
                else:
                    if mm.group(1): curmat=mm.group(1)
                    if mm.group(2): curp=int(mm.group(2))
                    sn=int(mm.group(3))
                if curp is None: continue
                blk=curmat or m['block']
                items[cur][label(m,blk,curp,sn)]+=1
    out[f'{s}|{q}']=dict(qtype=qt,role=qs[(s,q)]['role'],n=d.get('n'),order=order,cnt={k:dict(v) for k,v in cnt.items()},items={k:dict(v) for k,v in items.items()})
pass
for k,v in out.items():
    print('=====',k,v['qtype'],'n=',v['n'],'|',v['role'])
    for l in v['order']:
        c=v['cnt'].get(l,{})
        if l.startswith('背景') and not c: continue
        print('  ',l.ljust(22),' '.join(f'{a}{b}' for a,b in sorted(c.items())) or '—')
    for it,c in v['items'].items():
        print('   #',it[:22],dict(c))
