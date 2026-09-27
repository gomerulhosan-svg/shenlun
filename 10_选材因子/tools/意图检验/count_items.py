import json,re,os,collections,statistics
B='/home/user/shenlun/08_小题重写'
OUT=os.path.dirname(os.path.abspath(__file__))
qs=json.load(open(B+'/questions.json'))
qidx={'问题一':1,'问题二':2,'问题三':3,'问题四':4,'问题五':5}
PRE=r'(?:^|(?<=[。；;\s：:\n]))'
def cnt(s):
    a=len(re.findall(PRE+r'[一二三四五六七八九十]{1,2}(?:、|是)',s,re.M))
    b=len(re.findall(PRE+r'\d{1,2}[\.、．](?!\d)',s,re.M))
    return max(a,b)
def items(t):
    t=t.split('\n---')[0]
    m=re.search(r'(?:对策建议|对策|建议)[：:]\s*\n?\s*(?:一|1)[、\.是．]',t)
    if m:
        P=cnt(t[:m.start()]); C=cnt(t[m.start():])
        if P>0 and C>0: return P+C,P,C
    n=cnt(t)
    both=len(re.findall(r'(?:对策|建议)[：:]',t))
    if both>=2 and abs(both-n)<=1: return n*2,n,n
    return n,None,None
def answer_section(f):
    s=open(f,encoding='utf-8').read()
    m=re.search(r'## 答案\n(.*?)\n## ',s,re.S)
    return m.group(1) if m else ''
rows=[]
for q in qs:
    sid=q['set_id']; k=qidx[q['q']]
    fin=answer_section(f'{B}/{sid}/Q{k}.md')
    ref=open(f'{B}/{sid}/参照_上一版/Q{k}.txt',encoding='utf-8').read()
    a=items(fin); b=items(ref)
    rows.append(dict(sid=sid,q=q['q'],pts=q['points'],limit=q['limit'],qtype=q['qtype'],fin=a,ref=b))
    print(sid,q['q'],q['points'],q['limit'],q['qtype'],'final',a,'ref',b)
json.dump(rows,open(OUT+'/items.json','w'),ensure_ascii=False)
