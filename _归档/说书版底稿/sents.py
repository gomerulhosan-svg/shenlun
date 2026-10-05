# 用法: python3 sents.py 起始行 结束行   —— 列出原文这几行里每段的句子编号（按"。"切）
import re, sys
SRC = "/home/user/shenlun/04_文件原文/01_2026广东省政府工作报告.md"
L = open(SRC, encoding='utf-8').read().split('\n')
a, b = int(sys.argv[1]), int(sys.argv[2])
for i in range(a, b + 1):
    t = L[i - 1]
    if not t.strip():
        continue
    s = re.findall(r'[^。]*。', t)
    if ''.join(s) != t:
        s = s + [t[len(''.join(s)):]]
    print(f'== 第 {i} 行，{len(s)} 句')
    for k, x in enumerate(s):
        print(f'  [{k}] {x}')
