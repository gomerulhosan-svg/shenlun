"""维度层检验：按 08_小题重写/<套>/Qn.md 每个要点的「来源」句，看是否含主关键词；并按超几何算随机期望。"""
import re, json
from math import comb
BASE='/home/user/shenlun/08_小题重写'
src=open('kw2.py',encoding='utf-8').read().split('PROB =')[0].replace('from kw import BASE, BIG',"BASE='%s';BIG={}"%BASE).replace('import json, re, sys\nsys.path.insert(0, \'.\')','')
exec(src)
for sid,q,blk,kws in CFG:
    rx=kws[0][1]
    ids=json.load(open(f'{BASE}/_pool/{sid}.json',encoding='utf-8'))['ids']
    sents={k:v for k,v in ids.items() if re.fullmatch(re.escape(blk)+r'-p\d+-\d+',k)}
    N=len(sents); K=sum(1 for v in sents.values() if re.search(rx,v))
    txt=open(f'{BASE}/{sid}/{"Q1" if q=="问题一" else "Q2"}.md',encoding='utf-8').read()
    obs=exp=nd=0
    for sec in re.split(r'(?m)^### ',txt)[1:]:
        if sec.startswith('总句'): continue
        got=set()
        for line in sec.split('\n'):
            if '来源：' not in line: continue
            cb=cp=None
            for m in re.finditer(r'(?:材料([一二三四五六七八九十]+))?(?:第 ?(\d+) ?段)?第 ?(\d+) ?句',line):
                cb=m.group(1) or cb; cp=m.group(2) or cp
                if cp and f'{cb or blk}-p{cp}-{m.group(3)}' in sents: got.add(f'{cb or blk}-p{cp}-{m.group(3)}')
        nd+=1; k=len(got)
        obs+=any(re.search(rx,sents[i]) for i in got)
        exp+=(1-comb(N-K,k)/comb(N,k)) if k and N-K>=k else (1 if k else 0)
    print(f'{sid}{q} 维度含词 {obs}/{nd} 随机期望 {exp:.1f}')
