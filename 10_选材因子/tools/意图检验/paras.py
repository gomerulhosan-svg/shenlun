import json,sys
d=json.load(open('blocks.json'))
for arg in sys.argv[1:]:
    s,b=arg.split(':')
    for n,ps in d[s]:
        if n==b:
            print('=====',s,b)
            for i,p in enumerate(ps,1): print(f' p{i}:',p[:70])
