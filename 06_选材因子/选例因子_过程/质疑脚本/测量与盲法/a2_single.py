from common import *
feats = [f for f in S.FEATS]
def run(sub, label):
    it = S.items_of(sub)
    print('###', label)
    for who in 'AB':
        fns = S.fns_for([f[0] for f in S.FEATS], who)
        res = S.perm_test(it, fns, 5000, 7, nboot=1000)
        print(' ', who, res['_meta'])
        for name, fn, d in fns:
            r = res[name]
            print('   %-12s %s' % (name, fmt(r)))
run([c for c in kept if c['nseg'] == 1], '只看单段例子')
# length-matched: examples with len <= 300 chars
run([c for c in kept if c['nseg'] <= 2], '段数<=2')
