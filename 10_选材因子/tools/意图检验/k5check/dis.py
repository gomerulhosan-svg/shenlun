import json,glob,re,collections,os,statistics as st
B='/home/user/shenlun/08_小题重写'
OUT='/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/k5check'
qs=json.load(open(B+'/questions.json'))
CORE={'必答','弱共识','有'}
HIT=CORE|{'可选','个案','单票'}
NUM=re.compile(r'\d|[一二三四五六七八九十百千万亿]+(?:个|家|项|人|户|亩|吨|元|亿|万|倍|%)|成以上')
EFF=re.compile(r'取得|成效|增长|提升了|提高了|达到|突破|位居|第一|累计|实现了|同比|占比|超过|带动|受益|效果|成为|迈上|居全国|首位|领先|显著|明显|大幅|已成|已有|已经')
BG=re.compile(r'习近平|总书记|指出|强调|意义|要求|必须|是.{0,12}(?:关键|基础|前提|保障|核心|根本|动力|必由之路)|近年来|随着|当前|新时代')
SPEECH=re.compile(r'说|表示|认为|介绍|坦言|感慨|直言|谈到|：“')
def han_bigrams(s):
    s=re.sub(r'[^一-鿿]','',s)
    return {s[i:i+2] for i in range(len(s)-1)}
BOIL='请根据材料给定概括分析说明主要做法举措谈谈体现在哪些方面假如你是如果工作人员梳理存在的问题并提出对策建议相应就进一步推进要求简述理解你对中提到草拟汇报内容调研组成员员拟写报告两部分所采取的为推动遇到的做好在的与了和对'
boil=han_bigrams(BOIL)
GENERIC={'广东','发展','工作','市场','建设','推进','推动','全市','方面','主要','进行','问题','提出','对策','建议'}
def stem_core(stem):
    s=stem.split('要求')[0]
    s=re.sub(r'（[^）]*分[^）]*）|\([^)]*分[^)]*\)','',s)
    g=han_bigrams(s)-boil-GENERIC
    # drop bigrams containing 材料 or pure numerals
    return {x for x in g if '材' not in x and '料' not in x}
res=[]
agg=collections.defaultdict(lambda:collections.Counter())
perq=[]
for q in qs:
    if not q['blocks']: continue
    sid=q['set_id']
    pool=json.load(open(f'{B}/_pool/{sid}.json'))
    ids=pool['ids']
    al=json.load(open(f'{B}/{sid}/对齐.json')).get(q['q'])
    if not isinstance(al,dict): continue
    core=set();hit=set()
    for p in al.get('points',[]):
        if not isinstance(p,dict): continue
        m=re.match(r'([一二三四五六七八九十导]+)-p(\d+)-(\d+)',p['pool_id'])
        key='%s-p%s-%s'%m.groups()
        c=p.get('class')
        if c in CORE: core.add(key)
        if c in HIT: hit.add(key)
    sk=stem_core(q['stem'])
    sents=[(k,v) for k,v in ids.items() if re.fullmatch(r'[一二三四五六七八九十导]+-p\d+-\d+',k) and k.split('-')[0] in q['blocks']]
    tot_chars=sum(len(v) for k,v in sents)
    cats=collections.Counter(); chars=collections.Counter()
    for k,v in sents:
        lab='core' if k in core else ('hit' if k in hit else 'none')
        cats[lab]+=1; chars[lab]+=len(v)
        f=dict(num=bool(NUM.search(v)),eff=bool(EFF.search(v)),bg=bool(BG.search(v)),speech=bool(SPEECH.search(v)),stem=len(han_bigrams(v)&sk)>0)
        a=agg[(lab)]
        a['n']+=1
        for kk,vv in f.items(): a[kk]+=vv
        qt='问对' if q['qtype'] in('T-问对','T-对策') else '提取'
        b=agg[(qt,lab)]; b['n']+=1
        for kk,vv in f.items(): b[kk]+=vv
    perq.append(dict(sid=sid,q=q['q'],pts=q['points'],qtype=q['qtype'],n=al.get('n'),sent=len(sents),core=cats['core'],hit=cats['hit'],none=cats['none'],none_char_share=round(chars['none']/tot_chars,2) if tot_chars else None,stemkeys=''.join(sorted(sk))[:40]))
for r in perq: print(r)
print()
for k in sorted(agg,key=str):
    a=agg[k]; n=a['n']
    print(k,'n=%d'%n,' '.join('%s=%.0f%%'%(x,100*a[x]/n) for x in['num','eff','bg','speech','stem']))
json.dump(perq,open(OUT+'/perq.json','w'),ensure_ascii=False)
