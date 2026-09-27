import json,re,collections
from lib import *
KW={('2020县级','问题一'):['社会治理'],('2020县级','问题二'):['市场主体','活力'],
('2021县级','问题一'):['数字政府'],('2021县级','问题二'):['质量变革','效率变革','动力变革','密码'],
('2022县级','问题一'):['软联通'],('2022县级','问题二'):['人文湾区','文化交流'],
('2023县级','问题一'):['金字招牌','打造品牌','追求质量'],('2023县级','问题二'):['青年人才','青年'],
('2024一卷','问题一'):['产业科技创新','新质生产力'],('2024二卷','问题一'):['产业科技创新','新质生产力'],
('2024一卷','问题二'):['高质量发展'],('2024二卷','问题二'):['百县千镇万村','百千万工程'],
('2025省市','问题一'):['主体','为主'],('2025省市','问题二'):['成果转化'],
('2025县镇','问题一'):['土特产'],('2025县镇','问题二'):['科技赋能'],
('2026省市','问题一'):['绿色工厂'],('2026县镇','问题一'):['绿色工厂'],
('2026省市','问题二'):['零碳园区'],('2026县镇','问题二'):['古树名木'],
('2024选调','问题一'):['下乡','返乡','新乡'],('2024选调','问题二'):['烦恼'],
('2025选调','问题一'):['金树林'],('2025选调','问题二'):['海洋牧场'],
('2023乡镇','问题一'):['人才'],('2023乡镇','问题二'):['文化'],('2023乡镇','问题三'):['积分制'],('2023乡镇','问题四'):['应急管理'],('2023乡镇','问题五'):['集体经济']}
tot=collections.Counter()
for q in qs:
    k=(q['set_id'],q['q'])
    if k not in KW: continue
    al,core,hit,sents=load_q(q)
    ids=json.load(open(f'{B}/_pool/{q["set_id"]}.json'))
    blocks=ids['blocks']
    kw=KW[k]; pat=re.compile('|'.join(map(re.escape,kw)))
    inblk=sum(len(pat.findall('\n'.join(blocks[b]))) for b in q['blocks'])
    Lin=sum(len(''.join(blocks[b])) for b in q['blocks'])
    Lout=sum(len(''.join(v)) for b,v in blocks.items() if b not in q['blocks'])
    outblk=sum(len(pat.findall('\n'.join(v))) for b,v in blocks.items() if b not in q['blocks'])
    dens_in=inblk/Lin*1000; dens_out=outblk/Lout*1000 if Lout else 0
    kc=[s for s,v in sents if s in core]; kn=[s for s,v in sents if s not in hit]
    sd=dict(sents)
    pc=sum(bool(pat.search(sd[s])) for s in kc); pn=sum(bool(pat.search(sd[s])) for s in kn)
    first=[s for s,v in sents if pat.search(v)]
    fs=first[0] if first else '-'
    # first sentence of the block
    lead=[s for s,v in sents if re.search(r'-p1-1$',s)]
    lead_has=[s for s in lead if pat.search(sd[s])]
    print(k[0],k[1],q['qtype'],kw,'则内%d次(%.1f/千字) 则外%d次(%.1f/千字)'%(inblk,dens_in,outblk,dens_out),
          '必答句含词 %d/%d  不得分句含词 %d/%d'%(pc,len(kc),pn,len(kn)),'首次',fs,'则首句含词' if lead_has else '')
    tot['cin']+=pc; tot['c']+=len(kc); tot['nin']+=pn; tot['n']+=len(kn)
    tot['ratio>3']+= (dens_in>3*dens_out); tot['q']+=1; tot['out0']+=(outblk==0)
    tot['lead']+=bool(lead_has)
print(dict(tot))
