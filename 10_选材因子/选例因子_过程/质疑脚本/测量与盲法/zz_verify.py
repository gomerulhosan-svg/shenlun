from common import *
import copy
ONLY_UNUSED = ['2022县级-C105', '2022县级-C106', '2023县级-C033', '2023县级-C035', '2024一卷-C027', '2024一卷-C081', '2024一卷-C181', '2024二卷-C097', '2025县镇-C005', '2025选调-C005', '2025选调-C007', '2026省市-C066']
# which 10 have keywords only in unused segs (exclude 2 with none)
KW = re.compile(r'首个|首创|率先|第一|唯一|标杆|领先|首家|首次|首批|首台|首条|首座|首部|国家级|全国(?:文明|先进|示范|模范|百强|十佳|优秀)|国家(?:重点|示范)|全国[^，。；]{0,6}(?:奖|称号|冠军)')
ten=[]
for c in kept:
    if c['id'] in ONLY_UNUSED:
        t=''.join(TEXT[(c['paper'],s)] for s in c['segs'])
        if KW.search(t): ten.append(c['id'])
print('with kw in unused only', len(ten))
k2=copy.deepcopy(kept)
for c in k2:
    if c['id'] in ten:
        c['A']['出彩_显式']=0; c['B']['出彩_显式']=0
it=S.items_of(k2)
for who in 'AB':
    r=S.perm_test(it, S.fns_for(['出彩_显式'],who), 5000, 3, nboot=1000)
    print(who, fmt(r['出彩_显式']))
# B-A benefit count
sel=[c for c in kept if c['st']=='选用']; un=[c for c in kept if c['st']=='未选']
d=lambda c: c['B']['收益类数']-c['A']['收益类数']
print('B-A 收益 sel %.3f un %.3f'%(statistics.mean(map(d,sel)), statistics.mean(map(d,un))))
print('n kept', len(kept), 'sel', len(sel), 'un', len(un))
print('资源转化 A', sum(c['A']['资源转化'] for c in kept), '约束突破 A', sum(c['A']['约束突破'] for c in kept))
