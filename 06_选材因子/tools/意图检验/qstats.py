import json,re
d=json.load(open('blocks.json'))
qs=json.load(open('/home/user/shenlun/08_小题重写/questions.json'))
def cc(t): return len(re.sub(r'\s','',t))
dom={('2020乡镇','问题一'):['二'],('2020乡镇','问题二'):['三'],('2020乡镇','问题三'):['四'],('2020乡镇','问题四'):['五'],('2020乡镇','问题五'):['六'],
('2021乡镇','问题一'):['三'],('2021乡镇','问题二'):['五'],('2021乡镇','问题三'):['四'],('2021乡镇','问题四'):['六','七','八'],('2021乡镇','问题五'):['九'],
('2022乡镇','问题一'):['一'],('2022乡镇','问题二'):['二'],('2022乡镇','问题三'):['三'],('2022乡镇','问题四'):['四'],('2022乡镇','问题五'):['五']}
CN='一二三四五六七八九十'
for q in qs:
    s=q['set_id']; bl=q['blocks'] or dom.get((s,q['q']),[])
    B=dict(d[s]); names=[n for n,_ in d[s] if n!='导']; tot=sum(cc(p) for n,ps in d[s] for p in ps)
    qc=sum(cc(p) for b in bl for p in B[b])
    ps=[p for b in bl for p in B[b]]
    speak=sum(1 for p in ps if re.match(r'^[^，。“”：]{2,20}：',p) and not re.match(r'^(时间|地点)',p))
    quotes=sum(p.count('“') for p in ps)
    said=sum(len(re.findall(r'(说|表示|指出|介绍|反映|认为|坦言|直言)',p)) for p in ps)
    wen=len(re.findall(r'(问题|难|困|不足|短板|缺|瓶颈|制约|烦恼|滞后|不够)',''.join(ps)))
    pos=[names.index(b)+1 for b in bl]
    print(s,q['q'],bl,'位置',pos,'/',len(names),f'字数{qc} 占{qc/tot:.0%}','发言段',speak,'引号',quotes,'说类动词',said,'负面词',wen, f'负面词/千字 {wen*1000/max(qc,1):.1f}')
