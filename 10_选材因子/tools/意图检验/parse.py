import re,sys,json,os
D='/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent'
SETS=['2020县级','2021县级','2022县级','2023县级','2024一卷','2024二卷','2024选调','2025省市','2025县镇','2025选调','2026省市','2026县镇']
CN='一二三四五六七八九十'
def load(s):
    t=open(f'{D}/mat_{s}.md',encoding='utf-8').read()
    mats={}; cur=None
    body,stem=t.split('### 题干')
    for line in body.split('\n'):
        m=re.match(r'#### 材料(.+)',line)
        if m: cur=m.group(1).strip(); mats[cur]={}; continue
        m=re.match(r'〔(\d+)〕(.*)',line)
        if m and cur: mats[cur][int(m.group(1))]=m.group(2)
    return mats,stem
def norm(x): return re.sub(r'[\s，。、；：“”‘’「」『』"\'（）()《》！？…·—\-,.;:!?]','',x)
if __name__=='__main__':
    out={}
    for s in SETS:
        mats,stem=load(s)
        out[s]={'n_mat':len(mats),'paras':{k:len(v) for k,v in mats.items()}}
    print(json.dumps(out,ensure_ascii=False))
