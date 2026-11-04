import json,sys
sys.path.insert(0,'/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/kwseed_mine')
D='/tmp/claude-0/-home-user-shenlun/176c3aa6-8759-55ba-8781-1d2ff4e9649d/scratchpad/intent/kwseed_mine/'
R={ '%s|%s'%(r['sid'],r['q']):r for r in json.load(open(D+'result.json'))}
M=json.load(open(D+'dims.json'))
V=json.load(open(D+'verdict.json'))
Q={ '%s|%s'%(x['set_id'],x['q']):x for x in json.load(open('/home/user/shenlun/08_小题重写/questions.json'))}
for sid,q,n,ba,bt,bp in V:
    key='%s|%s'%(sid,q); r=R[key]; m=M[key]
    t=ba or bt
    k,(ver,cov,nat)=t[0],t[1]
    v=r['perk'][k]; d=m[k]
    print('|%s %s|%s|n=%s|%s|%s|%s/%s|%d/%d vs %d/%d (×%s)|%d/%d|句%d/期%.1f；邻%d/%d|%s|'%(sid,q[-1],Q[key]['qtype'][2:],n,r['des'],k,v['din'],v['dout'],v['a'],r['nS'],v['b'],r['nNS'],v['enr'],v['pts'],r['npts'],d['s'],d['exp'],d['w'],d['nd'],ver))
