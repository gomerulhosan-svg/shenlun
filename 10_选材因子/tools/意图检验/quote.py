import re
from parse import load,norm,SETS
from difflib import SequenceMatcher
def lcs(a,b):
    m=SequenceMatcher(None,a,b,autojunk=False).find_longest_match(0,len(a),0,len(b))
    return m.size
def segs(stem):
    q3=stem[stem.find('**问题三**'):]
    q3=q3.split('要求')[0].replace('**问题三**','').strip()
    parts=re.findall(r'[“"]([^”"]+)[”"]',q3)
    # also leading sentences before 请
    lead=q3.split('请')[0]
    for sent in re.split(r'[。；]',lead):
        sent=re.sub(r'习近平总书记(指出|强调)?[：:，]?','',sent).strip('，： ')
        if len(norm(sent))>=8 and not any(norm(p) in norm(sent) for p in parts): parts.append(sent)
    return q3,parts
for s in SETS:
    mats,stem=load(s)
    q3,parts=segs(stem)
    print('=====',s); print('Q3:',q3[:160])
    for p in parts:
        np_=norm(p); best=[]
        for m,ps in mats.items():
            for i,t in ps.items():
                L=lcs(np_,norm(t))
                best.append((L,m,i))
        best.sort(reverse=True)
        top=[f'材料{m}〔{i}〕{L}/{len(np_)}' for L,m,i in best[:3]]
        print(f'  「{p}」 ->',' | '.join(top), '逐字' if best[0][0]==len(np_) else '')
