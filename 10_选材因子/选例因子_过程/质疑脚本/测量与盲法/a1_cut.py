from common import *
# 1. paragraph coverage by tag, in articles that have >=1 example
cov = defaultdict(set)  # (p,seg) -> set of case ids (all cases, pre-dedup)
for c in cases:
    for s in c['segs']:
        cov[(c['paper'], s)].add(c['id'])
arts_with_ex = {(c['paper'], c['art']) for c in cases}
tot = Counter(); covered = Counter(); nper = defaultdict(list); lens=defaultdict(list)
for p in S.PAPERS:
    for a in BL[p]['文章']:
        if (p, a['编号']) not in arts_with_ex: continue
        for s in a['段']:
            t = KEY[p][s['id']]['标']
            tot[t] += 1
            k = len(cov.get((p, s['id']), ()))
            if k:
                covered[t] += 1; nper[t].append(k)
            lens[(t, bool(k))].append(KEY[p][s['id']]['字数'])
print('段覆盖率（有例子的文章内）')
for t in ['选用', '部分', '未选']:
    print(t, tot[t], covered[t], '%.1f%%' % (100*covered[t]/tot[t]), '每个被覆盖段的例子数均值 %.2f' % statistics.mean(nper[t]), '>1例子的段占 %.1f%%' % (100*sum(1 for x in nper[t] if x>1)/len(nper[t])))
for k,v in sorted(lens.items()): print(k, 'n=%d 中位字数 %d' % (len(v), statistics.median(v)))
# within-article paragraph-level: covered or not, selected vs unselected paragraphs, in PART articles
items = []
for p in S.PAPERS:
    for a in BL[p]['文章']:
        u = (p, a['编号'])
        if u not in PART: continue
        for s in a['段']:
            t = KEY[p][s['id']]['标']
            if t == '部分': continue
            items.append((u, t == '选用', {'cov': len(cov.get((p, s['id']), ())), 'len': KEY[p][s['id']]['字数']}))
r, m = within(items, lambda o: o['cov'] > 0)
print('段层面·文章内 被覆盖率 选用段 vs 未选段:', fmt(r), m)
r, m = within([i for i in items if i[2]['cov']>0], lambda o: o['cov'] > 1)
print('被覆盖段里 一段>1个例子:', fmt(r), m)
r, m = within([i for i in items if i[2]['cov']>0], lambda o: o['cov'], d=+1)
print('被覆盖段 每段例子数:', fmtm(r))
# 2. case granularity: nseg, len, chars per seg, by status, within-article
it = S.items_of(kept)
for name, fn in [('nseg', lambda c: c['nseg']), ('nseg>=3', lambda c: c['nseg']>=3), ('len', lambda c: c['len']), ('nseg==1', lambda c: c['nseg']==1)]:
    r, m = within(it, fn)
    print(name, fmtm(r) if name in ('nseg','len') else fmt(r))
# among selected multi-seg examples: what share of their segs are actually selected?
ms = [c for c in kept if c['st']=='选用' and c['nseg']>1]
fr = [sum(1 for s in c['segs'] if KEY[c['paper']][s]['标']=='选用')/c['nseg'] for c in ms]
print('选用组多段例子 n=%d；其中选用段占比 均值 %.2f；只有一段是选用的 %d 个' % (len(ms), statistics.mean(fr), sum(1 for c in ms if sum(1 for s in c['segs'] if KEY[c['paper']][s]['标']=='选用')==1)))
chars_sel = sum(KEY[c['paper']][s]['字数'] for c in ms for s in c['segs'] if KEY[c['paper']][s]['标']=='选用')
chars_all = sum(c['len'] for c in ms)
print('多段选用例子的字数里 选用段字数占 %.1f%%' % (100*chars_sel/chars_all))
allsel = [c for c in kept if c['st']=='选用']
cs = sum(KEY[c['paper']][s]['字数']*KEY[c['paper']][s]['用率'] for c in allsel for s in c['segs'])
print('全部选用例子：按用率×字数估算，被命题人实际用到的文字占例子总字数 %.1f%%' % (100*cs/sum(c['len'] for c in allsel)))
print('例子最大段数分布 选用', Counter(min(c['nseg'],6) for c in kept if c['st']=='选用'), '未选', Counter(min(c['nseg'],6) for c in kept if c['st']=='未选'))
