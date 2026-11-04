"""查道理卡里卷面句子（论点、道理、总论点）的几类毛病，只列出来给人看，不自动改：
1. 固定提法：只能给指定主语的说法，出现了就列出来，人看主语对不对；
2. 说重了的词：根本、决定性、唯一、首要、最；
3. 操作层面的词和口语，出现在卷面句子里就列出来（"例子要证"那行是白话，不查）。
用法：python3 查提法.py [卡片.md ...]"""
import re, sys, glob, os
here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
files = sys.argv[1:] or sorted(glob.glob(os.path.join(here, '[0-9]*.md')))
fixed = {'第一生产力': '科技', '第一资源': '人才', '第一动力': '创新', '首要任务': '高质量发展', '头号工程': '百千万工程',
         '关键一招': '改革开放', '根本保证': '党的领导', '本质特征': '共同富裕（对中国式现代化）', '本质要求': '看原文',
         '战略支点': '看原文', '牛鼻子': '只表示重要，不进论点后半句', '重中之重': '只表示重要，不进论点后半句'}
heavy = ['根本', '决定性', '唯一', '最']
ops = ['编制', '常住人口', '补贴', '审批', '指标', '考核', '经费', '财政', '学校', '医院', '千条线', '一根针', '饿肚子', '老规矩', '便宜']
for f in files:
    name = os.path.basename(f)
    for i, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'\s*- (论点|道理|总论点)[^：]*：(.*)$', line)
        if not m: continue
        s = re.split(r'〔', m.group(2))[0]
        notes = [f'{k}→{v}' for k, v in fixed.items() if k in s]
        notes += [f'重:{k}' for k in heavy if k in s and not any(k in x for x in fixed)]
        notes += [f'操作/口语:{k}' for k in ops if k in s]
        if notes:
            print(f'{name}:{i} [{m.group(1)}] {s.strip()[:40]}  ← ' + '；'.join(notes))
