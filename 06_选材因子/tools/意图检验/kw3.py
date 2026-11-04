import json, re, sys
sys.path.insert(0, '.')
from kw import BASE, BIG
# 每题：关键词组 [(名, 正则)]，第一组为主关键词；core = 全部组的并集
CFG = [
 ('2024一卷','问题一','二',[('产业科技(创新)',r'产业科技'),('新质生产力',r'新质生产力')]),
 ('2024一卷','问题二','八',[('高质量发展',r'高质量发展')]),
 ('2024二卷','问题一','二',[('产业科技(创新)',r'产业科技'),('新质生产力',r'新质生产力')]),
 ('2024二卷','问题二','五',[('百千万工程',r'百千万工程|百县千镇万村')]),
 ('2024选调','问题一','三',[('下乡/返乡/兴乡',r'下乡|返乡|兴乡|返家乡'),('青年',r'青年')]),
 ('2024选调','问题二','四',[('青年科技人才',r'青年(科技人才|科研人员|教师|人才)'),('烦恼/压力',r'烦恼|压力')]),
 ('2025省市','问题一','四',[('主体/为主',r'主体|为主|主力军'),('企业',r'企业')]),
 ('2025省市','问题二','五',[('(成果)转化',r'转化'),('科研成果',r'科研成果|研究成果|科技成果')]),
 ('2025县镇','问题一','三',[('土特产/特色',r'土特产|特产|特色'),('产业',r'产业')]),
 ('2025县镇','问题二','四',[('科技/技术',r'科技|科研|技术'),('赋能',r'赋能')]),
 ('2025选调','问题一','三',[('金树林/转变',r'金树林|转变'),('价值/效益',r'价值|效益|回报|变现|经济')]),
 ('2025选调','问题二','四',[('海洋牧场',r'海洋牧场|海上牧场')]),
 ('2026省市','问题一','三',[('绿',r'绿'),('绿色工厂',r'绿色工厂')]),
 ('2026省市','问题二','五',[('零碳',r'零碳'),('园区',r'园区')]),
 ('2026县镇','问题一','五',[('绿',r'绿'),('绿色工厂',r'绿色工厂')]),
 ('2026县镇','问题二','七',[('古树',r'古树'),('保护',r'保护')]),
]
PROB = r'但|然而|却|缺乏|不足|不够|难以|困难|问题|不高|偏低|制约|影响|短板|不畅|压力|烦恼|过短|过大|过低|不愿|不便|难度|缺口|薄弱|较少|不了解|没有|未能|不强|有限|太麻烦|错过'
ORDER = 'BOCN?'
def nch(t): return len(re.sub(r'\s','',t))
def best(a,b): return a if ORDER.index(a)<=ORDER.index(b) else b
out=[]
for sid,q,blk,kws in CFG:
    pool=json.load(open(f'{BASE}/_pool/{sid}.json',encoding='utf-8'))
    ali=json.load(open(f'{BASE}/{sid}/对齐.json',encoding='utf-8'))[q]
    blocks=pool['blocks']; ids=pool['ids']
    core=kws[0][1]  # 句层检验只用主关键词
    union='|'.join(r for _,r in kws)
    row=dict(sid=sid,q=q,blk=blk,n=ali.get('n'),kws=[])
    for name,rx in kws+([('并集',union)] if len(kws)>1 else []):
        kin=len(re.findall(rx,''.join(blocks[blk]))); cin=nch(''.join(blocks[blk]))
        kout=sum(len(re.findall(rx,''.join(v))) for b,v in blocks.items() if b!=blk)
        cout=sum(nch(''.join(v)) for b,v in blocks.items() if b!=blk)
        dall={b:len(re.findall(rx,''.join(v)))/nch(''.join(v))*1000 for b,v in blocks.items()}
        rank=sorted(dall,key=lambda b:-dall[b]).index(blk)+1
        row['kws'].append(dict(name=name,rx=rx,kin=kin,din=round(kin/cin*1000,1),kout=kout,dout=round(kout/cout*1000,1),
            ratio=(round(kin/cin/(kout/cout),1) if kout else None),rank=f'{rank}/{len(blocks)}'))
    sents={k:v for k,v in ids.items() if re.fullmatch(re.escape(blk)+r'-p\d+-\d+',k)}
    scls={}
    clause_of={}
    for p in ali['points']:
        if not isinstance(p,dict) or not isinstance(p.get('pool_id'),str): continue
        pid=p['pool_id']; c=BIG.get(p.get('class'),'?'); s=re.sub(r'[a-z]$','',pid)
        scls[s]=best(c,scls.get(s,'?'))
        clause_of.setdefault(s,[]).append((pid,c))
    has_B = any(v=='B' for v in scls.values())
    top = 'B' if (has_B and sid!='2024选调') else 'O'   # 2025选调问题二没有必答层，用单票
    def isS(s): return scls.get(s,'?') in ('B',) if top=='B' else scls.get(s,'?') in ('B','O')
    S=[s for s in sents if isS(s)]
    K=[s for s in sents if re.search(core,sents[s])]
    P=[s for s in sents if re.search(PROB,sents[s])]
    SK=[s for s in S if s in K]
    # 分句层：采分分句本身含词
    Scl=[pid for s in S for pid,c in clause_of[s] if (c=='B' if top=='B' else c in 'BO')]
    Scl=list(dict.fromkeys(Scl))
    Sclk=[pid for pid in Scl if re.search(core,ids.get(pid,''))]
    # 段层
    def para(s): return s.rsplit('-',1)[0]
    Sp={para(s) for s in S}; Kp={para(s) for s in K}
    row.update(top=top,nsent=len(sents),nS=len(S),nK=len(K),nSK=len(SK),
      p_kw_given_S=round(len(SK)/len(S),2) if S else None,
      p_kw_base=round(len(K)/len(sents),2),
      p_S_given_K=round(len(SK)/len(K),2) if K else None,
      p_S_given_notK=round((len(S)-len(SK))/(len(sents)-len(K)),2) if len(sents)>len(K) else None,
      ncl=len(Scl),nclk=len(Sclk),
      nSp=len(Sp),nSpk=len(Sp&Kp),
      nP=len(P),nSP=len([s for s in S if s in P]),
      p_prob_given_S=round(len([s for s in S if s in P])/len(S),2) if S else None,
      p_prob_base=round(len(P)/len(sents),2))
    KU=[s for s in sents if re.search(union,sents[s])]
    row.update(nKU=len(KU),nSKU=len([s for s in S if s in KU]))
    row['K_detail']=[(s,scls.get(s,'-'),sents[s]) for s in K]
    row['S_detail']=[(s,scls.get(s,'-'),s in K,sents[s]) for s in S]
    out.append(row)
json.dump(out,open('kw3_result.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for r in out:
    k=r['kws']
    print(f"{r['sid']}{r['q']} 材料{r['blk']} n={r['n']} 层={r['top']}")
    for x in k: print(f"   {x['name']}: 指定 {x['kin']}次 {x['din']}/千字 | 其他 {x['kout']}次 {x['dout']}/千字 | x{x['ratio']} | 名次{x['rank']}")
    print(f"   句: 全{r['nsent']} 采分句{r['nS']} 含词句{r['nK']} 采分且含词{r['nSK']} | P(词|采分)={r['p_kw_given_S']} 基线P(词)={r['p_kw_base']} | P(采分|词)={r['p_S_given_K']} P(采分|无词)={r['p_S_given_notK']}")
    print(f"   并集句: 含词句{r['nKU']} 采分且含词{r['nSKU']}/{r['nS']}")
    print(f"   分句: 采分分句{r['ncl']} 含词{r['nclk']} | 段: 采分段{r['nSp']} 含词{r['nSpk']} | 问题标记: P(标记|采分)={r['p_prob_given_S']} 基线={r['p_prob_base']}")
