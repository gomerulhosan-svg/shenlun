import json,re,os,collections
B='/home/user/shenlun/08_小题重写'
qs=json.load(open(B+'/questions.json'))
CORE={'必答','弱共识','有'}
HIT=CORE|{'可选','个案','单票'}
def load_q(q):
    sid=q['set_id']
    ids=json.load(open(f'{B}/_pool/{sid}.json'))['ids']
    al=json.load(open(f'{B}/{sid}/对齐.json')).get(q['q'])
    core=set();hit=set()
    if isinstance(al,dict):
        for p in al.get('points',[]):
            if not isinstance(p,dict): continue
            m=re.match(r'([一二三四五六七八九十导]+)-p(\d+)-(\d+)',p['pool_id'])
            key='%s-p%s-%s'%m.groups()
            c=p.get('class')
            if c in CORE: core.add(key)
            if c in HIT: hit.add(key)
    sents=[(k,v) for k,v in ids.items() if re.fullmatch(r'[一二三四五六七八九十导]+-p\d+-\d+',k) and k.split('-')[0] in q['blocks']]
    return al,core,hit,sents
