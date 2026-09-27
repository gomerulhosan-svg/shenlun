import sys,re,json
sys.path.insert(0,'/home/user/shenlun/08_小题重写/tools')
from common import split_blocks
SETS=['2020县级','2020乡镇','2021县级','2021乡镇','2022县级','2022乡镇','2023县级','2023乡镇','2024一卷','2024二卷','2024选调','2025省市','2025县镇','2025选调','2026省市','2026县镇']
def cc(t): return len(re.sub(r'\s','',t))
def han(t): return len(re.findall(r'[一-鿿]',t))
out={}
for s in SETS:
    b=split_blocks(s)
    tot=sum(cc(p) for n,ps in b for p in ps)
    print(s, len([x for x in b if x[0]!='导']), '导' if any(x[0]=='导' for x in b) else '', tot, [(n,len(ps),sum(cc(p) for p in ps)) for n,ps in b])
    out[s]=[(n,ps) for n,ps in b]
json.dump(out,open('blocks.json','w'),ensure_ascii=False)
