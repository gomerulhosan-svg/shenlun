import json,re,sys
d=json.load(open('blocks.json'))
def norm(t): return re.sub(r'[^一-鿿A-Za-z0-9]','',t)
def B(s,n): return norm(''.join(dict(d[s])[n]))
def common_spans(a,b,k=10):
    out=[];i=0
    gb={b[j:j+k] for j in range(len(b)-k+1)}
    while i<len(a)-k+1:
        if a[i:i+k] in gb:
            j=i
            while j<len(a)-k+1 and a[j:j+k] in gb: j+=1
            out.append(a[i:j+k-1]); i=j+k
        else: i+=1
    return out
for arg in sys.argv[1:]:
    x,y=arg.split('|'); s1,n1=x.split(':'); s2,n2=y.split(':')
    print('==',arg)
    for sp in common_spans(B(s1,n1),B(s2,n2)): print('  ',len(sp),sp[:120])
