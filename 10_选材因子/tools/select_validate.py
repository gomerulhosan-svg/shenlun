"""校验例子清单和标注：python3 validate.py <卷> cases|A|B"""
import json, sys, os
H = os.path.dirname(os.path.abspath(__file__))
paper, what = sys.argv[1], sys.argv[2]
blind = json.load(open(f'{H}/blind/{paper}.json'))
ids = {s['id'] for a in blind['文章'] for s in a['段']}
cases = json.load(open(f'{H}/out/cases_{paper}.json'))
err = []
cid = set()
for c in cases['例子']:
    for k in ('id', '段', '主体', '做法'):
        if k not in c: err.append(f'{c.get("id")}: 缺 {k}')
    if c['id'] in cid: err.append(f'{c["id"]}: id 重复')
    cid.add(c['id'])
    for p in c.get('段', []):
        if p not in ids: err.append(f'{c["id"]}: 段 {p} 不存在')
if what in ('A', 'B'):
    lab = json.load(open(f'{H}/out/labels{what}_{paper}.json'))
    SPEC = {'贴合度': {0, 1, 2}, '出彩_显式': {0, 1}, '出彩_实质': {0, 1, 2}, '可复制_显式': {0, 1},
            '可复制_实质': {0, 1, 2}, '独特禀赋': {0, 1}, '资源转化': {0, 1}, '约束突破': {0, 1},
            '量化成效': {0, 1}, '人物引语': {0, 1}, '讲难点': {0, 1}, '新事物': {0, 1}}
    KINDS = {'经济', '生态', '民生', '治理', '文化', '安全', '科技'}
    for i in cid:
        if i not in lab: err.append(f'{i}: 没标'); continue
        L = lab[i]
        for k, v in SPEC.items():
            if L.get(k) not in v: err.append(f'{i}: {k}={L.get(k)!r} 不合法')
        if not isinstance(L.get('收益类'), list) or not set(L['收益类']) <= KINDS:
            err.append(f'{i}: 收益类={L.get("收益类")!r} 不合法')
    for i in lab:
        if i not in cid: err.append(f'{i}: 标了不存在的例子')
print(f'{paper} {what}: 例子 {len(cid)}，问题 {len(err)}')
print('\n'.join(err[:30]))
sys.exit(1 if err else 0)
