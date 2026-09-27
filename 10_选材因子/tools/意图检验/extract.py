import re,json,glob
base='/home/user/shenlun/09_按年汇编/'
setmap={'县级卷':'县级','乡镇卷':'乡镇','一卷':'一卷','二卷':'二卷','省市卷':'省市','县镇卷':'县镇'}
out={}
for f in sorted(glob.glob(base+'20*.md')):
    lines=open(f,encoding='utf-8').read().split('\n')
    cur=None; mat=None; inmat=False
    for ln in lines:
        m=re.match(r'^## (\d{4}) 年广东(省考《申论》·(.+)|选调生《申论》)',ln)
        if m:
            y=m.group(1)
            if m.group(3): cur=y+setmap.get(m.group(3).strip(),m.group(3))
            else: cur=y+'选调'
            if '三卷' in ln: cur=None
            out.setdefault(cur,{}) if cur else None
            inmat=False; mat=None; continue
        if cur is None: continue
        if ln.startswith('### '):
            inmat = ln.strip()=='### 给定材料'; mat=None; continue
        if inmat:
            m=re.match(r'^#### 材料(.+)',ln)
            if m: mat=m.group(1).strip(); out[cur][mat]=[]; continue
            if mat and ln.strip():
                out[cur][mat].append(ln.strip())
json.dump(out,open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/mats.json','w'),ensure_ascii=False,indent=1)
for s,v in out.items(): print(s, {k:len(x) for k,x in v.items()})
