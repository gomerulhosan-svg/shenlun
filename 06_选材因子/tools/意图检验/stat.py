import json,collections
r=json.load(open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/result.json'))
SKIP=('背景','其他材料')
for k,v in r.items():
    items={i:c for i,c in v['items'].items() if not (i.startswith('总观点') or '标题' in i)}
    single=0; multi=[]; feed=collections.Counter(); narr_dom=0
    for it,c in items.items():
        cc={p:n for p,n in c.items() if not p.startswith(SKIP)}
        tot=sum(cc.values()) or 1
        top=max(cc.items(),key=lambda x:x[1]) if cc else ('-',0)
        if top[1]/tot>=0.6: single+=1
        else: multi.append(it[:8])
        if top[0].startswith('叙述'): narr_dom+=1
        for p in cc: feed[p]+=1
    persons=[p for p in v['order'] if not p.startswith(SKIP)]
    withpts=[p for p in persons if any(x for x in v['cnt'].get(p,{}).values())]
    nobi=[p.split('|')[0] for p in persons if not any(kk.endswith('必') for kk in v['cnt'].get(p,{}))]
    zero=[p.split('|')[0] for p in persons if not v['cnt'].get(p)]
    many=[f"{p.split('|')[0]}{n}" for p,n in feed.items() if n>=3]
    print(k, f"条{len(items)} 单源条{single} 多源{multi} 叙述主导条{narr_dom} | 人{len(persons)} 有点{len(withpts)} 无必答{nobi} 零点{zero} 喂≥3条{many}")
    # bi totals by side
    tot=collections.Counter()
    for p,c in v['cnt'].items():
        for kk,n in c.items(): tot[kk]+=n
    print('   totals',dict(tot))
