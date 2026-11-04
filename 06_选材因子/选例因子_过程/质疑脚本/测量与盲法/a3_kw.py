from common import *
KW = re.compile(r'首个|首创|率先|第一|唯一|标杆|领先|首家|首次|首批|首台|首条|首座|首部|国家级|全国(?:文明|先进|示范|模范|百强|十佳|优秀)|国家(?:重点|示范)|全国[^，。；]{0,6}(?:奖|称号|冠军)')
REP = re.compile(r'推广|可复制|典型案例|借鉴|学习.{0,4}经验|经验做法|写入|纳入.{0,6}(?:文件|规划)|示范')
NUM = re.compile(r'\d')
QUO = re.compile(r'“[^”]{8,}”')
def segtxt(c, s): return TEXT[(c['paper'], s)]
# (a) 出彩_显式 regex vs A label agreement
agree = Counter()
for c in kept:
    t = ''.join(segtxt(c, s) for s in c['segs'])
    agree[(c['A']['出彩_显式'], bool(KW.search(t)))] += 1
print('A 出彩_显式 vs 正则', dict(agree))
# (b) for selected multi-seg examples with A 出彩_显式=1: where is the keyword?
loc = Counter(); ex=[]
for c in kept:
    if c['st'] != '选用' or c['nseg'] == 1: continue
    sel = [s for s in c['segs'] if KEY[c['paper']][s]['标'] == '选用']
    uns = [s for s in c['segs'] if s not in sel]
    ks = any(KW.search(segtxt(c, s)) for s in sel)
    ku = any(KW.search(segtxt(c, s)) for s in uns)
    if c['A']['出彩_显式'] == 1:
        loc[('A=1', ks, ku)] += 1
        if not ks: ex.append(c['id'])
print('选用组多段例子 A出彩_显式=1: (关键词在选用段?, 在非选用段?)', dict(loc))
print('关键词只在非选用段的例子', ex)
# (c) annotator-free paragraph-level test within article: all paragraphs in PART articles (selected vs unselected), regex features
items=[]
for p in S.PAPERS:
    for a in BL[p]['文章']:
        u=(p,a['编号'])
        if u not in PART: continue
        for s in a['段']:
            t=KEY[p][s['id']]['标']
            if t=='部分': continue
            tx=s['文']
            items.append((u, t=='选用', {'kw':bool(KW.search(tx)),'rep':bool(REP.search(tx)),'num':bool(NUM.search(tx)),'quo':bool(QUO.search(tx)),'len':len(tx)}))
print('段层面(参加置换的 41 篇文章的全部段)')
for k in ['kw','rep','num','quo']:
    r,m=within(items, lambda o,k=k:o[k]); print('  ',k, fmt(r), m['选用'], m['未选'])
# length stratified
med = statistics.median(i[2]['len'] for i in items)
for lab, f in [('短段', lambda o:o['len']<=med), ('长段', lambda o:o['len']>med)]:
    sub=[i for i in items if f(i[2])]
    for k in ['kw','num','quo']:
        r,m=within(sub, lambda o,k=k:o[k]); print('  ',lab,k, fmt(r), m['选用'], m['未选'])
# (d) same at example level but only counting text in selected segments for selected examples vs all text for unselected (text actually used)
