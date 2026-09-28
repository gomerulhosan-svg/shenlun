# -*- coding: utf-8 -*-
# 组装 试卷.md：注意事项 + 给定材料（材料一至八，按则号合并 _过程/材料_作文.md 和 _过程/材料_小题.md）+ 作答要求。
# 用法（仓库根目录）：python3 11_仿真卷/第1套_科技产业融合/_过程/组装_试卷.py
# 只拷"【材料X】"下面的〔段号〕正文，过程稿的文件头、说明、分隔线一律不拷；
# 作答要求照抄 参考答案与解析.md 的"## 题干"一节（两处保持一字不差）。
# 改了过程稿里的材料或答案里的题干，重跑本脚本，再跑 _过程/自检_整卷.py。
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
CN = '一二三四五六七八'

NOTICE = """## 注意事项

1. 本题本由给定材料与作答要求两部分构成。满分 100 分，考试时限 150 分钟。
2. 请在答题卡指定位置填写姓名、准考证号。
3. 请用黑色字迹的钢笔或签字笔在答题卡指定区域内作答，超出答题区域的作答无效。
4. 所有题目一律使用现代汉语作答，未按要求作答的不得分。
"""


def parse(path):
    mats, cur = {}, None
    for line in open(path, encoding='utf-8').read().split('\n'):
        s = line.strip()
        m = re.match(r'^#*\s*【材料(.)】', s)
        if m:
            cur = m.group(1); mats[cur] = []; continue
        if s.startswith('---') or s.startswith('# ') or (s.startswith('## ') and '【材料' not in s):
            cur = None; continue
        m = re.match(r'^〔(\d+)〕(.*)$', s)
        if m and cur:
            mats[cur].append((int(m.group(1)), m.group(2).strip()))
    return mats


def stems():
    ans = open(os.path.join(SET, '参考答案与解析.md'), encoding='utf-8').read()
    i = ans.index('\n## 题干\n') + len('\n## 题干\n')
    j = ans.index('\n## ', i)
    return ans[i:j].strip('\n')


def main():
    mats = {}
    mats.update(parse(os.path.join(HERE, '材料_作文.md')))
    mats.update(parse(os.path.join(HERE, '材料_小题.md')))
    assert sorted(mats, key=CN.index) == list(CN), f'则号不全：{sorted(mats)}'
    out = ['# 2027 年广东省考《申论》仿真卷（省市卷）·第 1 套', '', NOTICE, '## 给定材料', '']
    for k in CN:
        paras = mats[k]
        nums = [n for n, _ in paras]
        assert nums == list(range(1, len(nums) + 1)), f'材料{k} 段号不连续：{nums}'
        out += [f'### 【材料{k}】', '']
        for n, t in paras:
            out += [f'〔{n}〕{t}', '']
    out += ['## 作答要求', '', stems(), '']
    path = os.path.join(SET, '试卷.md')
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    print('写出', path, '；各则段数', {k: len(v) for k, v in mats.items()})


if __name__ == '__main__':
    main()
