import json,re,sys,collections
sys.path.insert(0,'.')
from maps import M
from analyze import label,pid_parse,CN,qs,R
RANK={'必':3,'可':2,'个':1}
# manual 对策 source type for 必 points: Y=应当/诉求句, F=反写/自造, Z=做法/现状句
TYPE={'八-p4-2b':'Y','八-p5-3c':'F','八-p5-4a':'F','八-p6-1g':'F','八-p7-2e':'F','八-p7-1f':'Z','八-p9-3a':'Y','八-p10-3d':'Z',
'2024二卷:五-p2-3d':'F','五-p3-1e':'F','五-p3-1h':'F','2024二卷:五-p4-3f':'F','五-p7-3b':'F','五-p7-3d':'Y','五-p8-2a':'F','五-p10-1b':'F',
'五-p6-4b':'Y','五-p7-5b':'Y','五-p6-3b':'Y','五-p3-3d':'F','五-p4-7c':'Y','五-p7-2b':'Y',
'四-p7-3d':'Y','四-p4-2c':'F','四-p9-2b':'F','四-p13-4e':'Y','四-p14-1b':'F','四-p14-3b':'F',
'五-p5-2b':'F','五-p6-1d':'F','五-p7-2d':'F','五-p7-2h':'Y','五-p11-2b':'F','五-p11-1c':'Y','五-p12-4a':'F','五-p12-3d':'F','五-p16-1c':'Y','五-p16-1b':'Y','五-p18-1c':'Y','五-p18-1a':'Y',
'七-p6-5a':'F','七-p10-2b':'Y','七-p13-1d':'Y','七-p13-2a':'Y','七-p13-2b':'Y','七-p12-4a':'Y',
'2020乡镇:五-p2-3a':'Y','2020乡镇:五-p2-3c':'Y','五-p7-1a':'Y','五-p7-2a':'F','五-p7-1b':'Y','三-p1-4c':'Z','四-p15-1b':'Z','四-p12-2b':'Z',
'2021乡镇:*':'F',
'五-p4-2b':'Y','五-p4-1d':'F','五-p7-3d':'Y','五-p7-2d':'F','五-p10-1i':'Y','五-p11-2e':'Z','五-p10-3d':'Y','五-p10-5e':'Y','五-p11-8b':'Z'}
GOV=('政府','镇干部','镇领导','林业站','街道干部')
res={}
for (s,q),m in M.items():
    qt=qs[(s,q)]['qtype']; d=json.load(open(R+f'{s}/对齐.json'))[q]
    best={}
    for p in d['points']:
        if not isinstance(p,dict): continue
        note=str(p.get('note',''))
        if 'side' in p: side=p['side']
        elif qt=='T-问对': side='对策' if note.startswith('对策') else '问题'
        elif qt=='T-对策': side='对策'
        else: side='点'
        key=(p['pool_id'],side); c=CN.get(p['class'],p['class'])
        if key not in best or RANK[c]>RANK[best[key]]: best[key]=c
    cnt=collections.defaultdict(collections.Counter); dstat=collections.Counter()
    for (pid,side),c in best.items():
        blk,pp,ss,cl=pid_parse(pid); lab=label(m,blk,pp,ss,cl)
        cnt[lab][side+c]+=1
        if side=='对策' and c=='必':
            t=TYPE.get(f'{s}:{pid}') or TYPE.get(f'{s}:*') or TYPE.get(pid,'?')
            g='gov' if lab.split('|')[1] in GOV else ('exp' if lab.split('|')[1] in ('专家',) else 'oth')
            dstat[t]+=1; dstat[g]+=1; dstat['n']+=1
    res[f'{s}|{q}']=({k:dict(v) for k,v in cnt.items()},dict(dstat))
    print('=====',s,q,qt,'对策必统计',dict(dstat))
    order=[]
    for pnum in sorted(m['paras']):
        labs=[m['paras'][pnum]]+[v for k,v in list(m.get('sents',{}).items())+list(m.get('clauses',{}).items()) if int(k.split('-')[0])==pnum]
        for l in labs:
            if l not in order: order.append(l)
    for l in list(cnt): 
        if l not in order: order.append(l)
    for l in order:
        c=cnt.get(l,{})
        if l.startswith('背景') and not c: continue
        if qt in ('T-问对',):
            s1='/'.join(str(c.get('问题'+x,0)) for x in '必可个'); s2='/'.join(str(c.get('对策'+x,0)) for x in '必可个')
            print(f'  {l:24s} 问{s1}  策{s2}')
        else:
            side='对策' if qt=='T-对策' else '点'
            print(f'  {l:24s} '+'/'.join(str(c.get(side+x,0)) for x in '必可个'))
pass
