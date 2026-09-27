import json,sys,re
d=json.load(open('blocks.json'))
KW=['习近平','总书记','讲话','座谈','发言','调研','走访','记者','采访','日记','报告','意见','方案','问题','难','困','不足','说：','表示','采访','论坛','会议','专家','记录']
for s in sys.argv[1:]:
    print('=====',s)
    for n,ps in d[s]:
        t=''.join(ps)
        kw={k:t.count(k) for k in KW if t.count(k)}
        print(f'--[{n}] {len(ps)}段 kw={kw}')
        print('  首:',ps[0][:160])
        if len(ps)>1: print('  二:',ps[1][:100])
        print('  尾:',ps[-1][-80:])
