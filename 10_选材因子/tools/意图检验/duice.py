import json,re,sys,collections
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent')
from maps import M
from analyze import label,pid_parse,CN,qs,R
for (s,q),m in M.items():
    qt=qs[(s,q)]['qtype']
    if qt not in ('T-问对','T-对策'): continue
    d=json.load(open(R+f'{s}/对齐.json'))[q]; ids=json.load(open(R+f'_pool/{s}.json'))['ids']
    print('=====',s,q)
    for p in d['points']:
        note=str(p.get('note',''))
        if 'side' in p: side=p['side']
        elif qt=='T-问对': side='对策' if note.startswith('对策') else '问题'
        else: side='对策'
        if side!='对策': continue
        blk,pp,ss,cl=pid_parse(p['pool_id'])
        sent=ids.get(f'{blk}-p{pp}-{ss}','')
        print(f"{p['pool_id']:11s} {CN.get(p['class'])} {p['kind']:4s} {label(m,blk,pp,ss,cl)[:10]:10s} | {sent[:60]} || {note[:30]}")
