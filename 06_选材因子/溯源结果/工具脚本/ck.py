import sys, re
sys.path.insert(0,"/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
from fetch import norm
f = sys.argv[1]; t = norm(open(f,encoding="utf-8").read())
for q in sys.argv[2:]:
    n = t.count(norm(q))
    print(("FOUND  " if n else "NOTFOUND"), n, q)
