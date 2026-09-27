import json,re,sys
BASE='/home/user/shenlun/08_小题重写'
src=open('/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/kw3.py').read()
CFG=eval(src.split('CFG =')[1].split('\nPROB')[0])
PROB=re.compile(src.split("PROB = r'")[1].split("'")[0])
ACT=re.compile(r'通过|推动|推进|建立|建设|实施|开展|打造|出台|制定|加强|完善|搭建|引导|支持|鼓励|设立|组建|创新|推行|探索|强化|实行|落实|提供|引进|培育|组织')
BIG={'必答':'B','弱共识':'B','有':'B','可选':'O','单票':'O','个案':'C'}
tot=dict(sc=0,sck=0,nc=0,nck=0)
print('题 | 采分分句含词 | 不给分分句含词 | 采分句含问题词/非采分句 | 采分句含动作词/非采分句')
for sid,q,blk,kws in CFG:
    pool=json.load(open(f'{BASE}/_pool/{sid}.json')); ids=pool['ids']
    ali=json.load(open(f'{BASE}/{sid}/对齐.json'))[q]
    rx=re.compile(kws[0][1])
    cls={}
    for p in ali['points']:
        if isinstance(p,dict) and isinstance(p.get('pool_id'),str): cls[p['pool_id']]=BIG.get(p.get('class'),'?')
    top='O' if (sid=='2024选调' or not any(v=='B' for v in cls.values())) else 'B'
    good=('B',) if top=='B' else ('B','O')
    clauses={k:v for k,v in ids.items() if re.fullmatch(re.escape(blk)+r'-p\d+-\d+[a-z]+',k)}
    sentences={k:v for k,v in ids.items() if re.fullmatch(re.escape(blk)+r'-p\d+-\d+',k)}
    # clause ids with class
    Sc=[c for c in clauses if cls.get(c,'?') in good]
    hitc=set(c for c in cls if cls[c] in 'BOC')
    # non-scoring clauses: clause not hit and its sentence has no hit clause either? use clause-level
    Nc=[c for c in clauses if c not in hitc]
    sck=sum(bool(rx.search(clauses[c])) for c in Sc); nck=sum(bool(rx.search(clauses[c])) for c in Nc)
    # sentence level S vs non-S (non-hit sentences)
    def sent_of(c): return re.sub(r'[a-z]+$','',c)
    Ss=set(sent_of(c) for c in Sc); Hs=set(sent_of(c) for c in hitc)
    Ns=[s for s in sentences if s not in Hs]
    pS=sum(bool(PROB.search(sentences[s])) for s in Ss if s in sentences); pN=sum(bool(PROB.search(sentences[s])) for s in Ns)
    aS=sum(bool(ACT.search(sentences[s])) for s in Ss if s in sentences); aN=sum(bool(ACT.search(sentences[s])) for s in Ns)
    nS=len([s for s in Ss if s in sentences])
    print(f"{sid}{q} n={ali.get('n')} 层{top} | {sck}/{len(Sc)}={sck/max(1,len(Sc)):.0%} | {nck}/{len(Nc)}={nck/max(1,len(Nc)):.0%} | 问题词 {pS}/{nS}={pS/max(1,nS):.0%} vs {pN}/{len(Ns)}={pN/max(1,len(Ns)):.0%} | 动作词 {aS}/{nS}={aS/max(1,nS):.0%} vs {aN}/{len(Ns)}={aN/max(1,len(Ns)):.0%}")
    tot['sc']+=len(Sc); tot['sck']+=sck; tot['nc']+=len(Nc); tot['nck']+=nck
print(tot, 'sc rate %.1f%% nc rate %.1f%%'%(100*tot['sck']/tot['sc'],100*tot['nck']/tot['nc']))
