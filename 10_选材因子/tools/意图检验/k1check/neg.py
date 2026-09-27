import json,re,collections
d=json.load(open('blocks.json'))
qs=json.load(open('/home/user/shenlun/08_小题重写/questions.json'))
def cc(t): return len(re.sub(r'\s','',t))
L0=r'(问题|难|困|不足|短板|缺|瓶颈|制约|烦恼|滞后|不够)'
L1=r'(难|困|不足|短板|缺|瓶颈|制约|烦恼|滞后|不够)'   # drop 问题
L2=r'(但是|然而|却|仍|尚未|还没|没有|不能|无法|难以|匮乏|薄弱|不强|不高|不畅|不到位|不完善|不健全|压力|风险|隐患|矛盾|担心|苦恼|头疼)'  # independent list
sets=['2020县级','2021县级','2022县级','2023县级','2024一卷','2024二卷','2025省市','2025县镇','2026省市','2026县镇','2024选调','2025选调']
for s in sets:
    B=dict(d[s]); row=[s]
    allq=set()
    for q in qs:
        if q['set_id']!=s: continue
        allq|=set(q['blocks'])
        t=''.join(p for b in q['blocks'] for p in B[b]); n=cc(t)
        hits=collections.Counter(re.findall(L0,t))
        row.append(f"{q['q'][-1]}:L0 {len(re.findall(L0,t))*1000/n:.1f} L1 {len(re.findall(L1,t))*1000/n:.1f} L2 {len(re.findall(L2,t))*1000/n:.1f} 问题={hits.get('问题',0)} 缺={hits.get('缺',0)}")
    rest=''.join(p for b,ps in d[s] if b not in allq and b!='导' for p in ps); n=cc(rest)
    row.append(f"作文用则:L0 {len(re.findall(L0,rest))*1000/n:.1f} L1 {len(re.findall(L1,rest))*1000/n:.1f} L2 {len(re.findall(L2,rest))*1000/n:.1f}")
    print(' | '.join(row))
# 不可或缺 etc
for s in sets:
    B=dict(d[s])
    for q in qs:
        if q['set_id']!=s or q['q']!='问题一': continue
        t=''.join(p for b in q['blocks'] for p in B[b])
        ctx=[t[max(0,m.start()-6):m.end()+6] for m in re.finditer(L0,t)]
        print(s,'Q1 命中上下文:',ctx)
