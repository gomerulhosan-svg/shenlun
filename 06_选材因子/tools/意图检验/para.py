import json,re,collections,statistics as st
from lib import *
tot=collections.Counter(); shares=[]; rows=[]
EFF=re.compile(r'取得|成效|增长|提升|提高|达到|突破|位居|第一|累计|实现|同比|占比|超过|带动|受益|效果|成为|迈上|首位|领先|显著|明显|大幅|已有|证明|缩影')
for q in qs:
    if not q['blocks']: continue
    al,core,hit,sents=load_q(q)
    if not isinstance(al,dict): continue
    ids=json.load(open(f'{B}/_pool/{q["set_id"]}.json'))
    paras=[]
    for b in q['blocks']:
        for i,p in enumerate(ids['blocks'][b],1): paras.append((b,i,p,len(ids['blocks'][b])))
    zero=[];
    for b,i,p,n in paras:
        ss=[k for k,v in sents if k.startswith('%s-p%d-'%(b,i))]
        h=[k for k in ss if k in hit]
        if not h:
            pos='首段' if i==1 else ('末段' if i==n else '中段')
            zero.append((b,i,pos,len(p),p[:28]))
    L=sum(len(p) for _,_,p,_ in paras); Lz=sum(z[3] for z in zero)
    shares.append(Lz/L)
    for z in zero: tot[z[2]]+=1
    tot['zero']+=len(zero); tot['paras']+=len(paras); tot['q']+=1; tot['q_with_zero']+=bool(zero)
    # 首段/末段 为零命中的比例
    tot['first_total']+=len(q['blocks']); 
    rows.append((q['set_id'],q['q'],q['qtype'],len(paras),len(zero),'%.0f%%'%(100*Lz/L),[(z[0]+str(z[1]),z[2],z[4]) for z in zero]))
for r in rows: print(r[:6]); [print('   ',x) for x in r[6]]
print(dict(tot)); print('整段不得分的字数占比 中位 %.0f%% 范围 %.0f%%-%.0f%%'%(100*st.median(shares),100*min(shares),100*max(shares)))
