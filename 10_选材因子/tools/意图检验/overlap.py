import json,re,itertools
d=json.load(open('blocks.json'))
def norm(t): return re.sub(r'[^一-鿿A-Za-z0-9]','',t)
def grams(t,k=10):
    t=norm(t); return {t[i:i+k] for i in range(len(t)-k+1)}
groups={'2020':['2020县级','2020乡镇'],'2021':['2021县级','2021乡镇'],'2022':['2022县级','2022乡镇'],'2023':['2023县级','2023乡镇'],'2024':['2024一卷','2024二卷','2024选调'],'2025':['2025省市','2025县镇','2025选调'],'2026':['2026省市','2026县镇']}
for y,ss in groups.items():
    for a,b in itertools.combinations(ss,2):
        for na,pa in d[a]:
            ga=grams(''.join(pa))
            if not ga: continue
            for nb,pb in d[b]:
                gb=grams(''.join(pb))
                if not gb: continue
                inter=len(ga&gb)
                if inter>=20:
                    print(y,f'{a}[{na}] vs {b}[{nb}]', f'共享10-gram {inter}; 占A {inter/len(ga):.2f} 占B {inter/len(gb):.2f}')
# also cross-year check for big overlaps
allb=[(s,n,grams(''.join(ps))) for s in d for n,ps in d[s]]
print('--- 跨年')
for (s1,n1,g1),(s2,n2,g2) in itertools.combinations(allb,2):
    if s1[:4]==s2[:4] or not g1 or not g2: continue
    i=len(g1&g2)
    if i>=30: print(f'{s1}[{n1}] vs {s2}[{n2}] {i} {i/len(g1):.2f} {i/len(g2):.2f}')
