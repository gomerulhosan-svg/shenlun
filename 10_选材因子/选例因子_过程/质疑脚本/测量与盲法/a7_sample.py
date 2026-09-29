from common import *
seen = set('2022县级-C105 2022县级-C106 2023县级-C033 2023县级-C035 2024一卷-C027 2024一卷-C081 2024一卷-C181 2024二卷-C097 2025县镇-C005 2025选调-C005 2025选调-C007 2026省市-C066'.split())
pool = [c for c in kept if c['unit'] in PART and c['id'] not in seen]
rng = random.Random(20260929)
sel = [c for c in pool if c['st']=='选用']; un = [c for c in pool if c['st']=='未选']
# stratify: round-robin by paper
def strat(lst, n):
    byp = defaultdict(list)
    for c in lst: byp[c['paper']].append(c)
    for v in byp.values(): rng.shuffle(v)
    out=[]; ps=sorted(byp)
    while len(out)<n:
        for p in ps:
            if byp[p] and len(out)<n: out.append(byp[p].pop())
    return out
samp = strat(sel,15)+strat(un,15)
rng.shuffle(samp)
cs = {}
for p in S.PAPERS:
    for c in json.load(open(f'{SEL}/out/cases_{p}.json'))['例子']: cs[c['id']]=c
json.dump([c['id'] for c in samp], open('sample_ids.json','w'))
with open('sample_blind.txt','w') as f:
    for i,c in enumerate(samp,1):
        cc = cs[c['id']]
        t = ' ‖ '.join(TEXT[(c['paper'],s)] for s in c['segs'])
        f.write('#%02d 卷=%s 主题=%s\n 主体=%s 做法=%s 段数=%d 字数=%d\n %s\n\n' % (i, c['paper'], BL[c['paper']]['主题'], cc['主体'], cc['做法'], c['nseg'], c['len'], t[:1400] + ('…[截断]' if len(t)>1400 else '')))
print(len(samp))
