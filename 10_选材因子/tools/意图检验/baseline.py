import re, json, sys
sys.path.insert(0, '09_按年汇编/tools'); sys.path.insert(0, '08_小题重写/tools')
import build
MU = open('10_选材因子/溯源结果/母文件_2025.md', encoding='utf-8').read()
REP = MU[MU.index('### 2.2'):MU.index('## 3 ')]           # 2025 政府工作报告：当年工作安排
def norm(s): return re.sub(r'[\s“”"‘’「」《》（）()、，。；：！？,.;:!?—…·\-]', '', s)
R = norm(REP)
# 通用词：题干套话和泛用政策词，命中不算
STOP = set('''根据给定材料 概括 主要做法 对策建议 存在问题 提出 分析 说明 结合 联系实际 自拟题目 撰写 议论文 深入思考 高质量发展 推动 推进 广东 加快 建设 发展 工作 问题 材料 全面 实施 深入 提升 加强'''.split())
def phrases(stem):
    s = norm(stem); out = set()
    for L in range(12, 3, -1):
        for i in range(len(s) - L + 1):
            p = s[i:i+L]
            if p in R and not any(p in q for q in out):
                if p not in STOP and not all(w in STOP for w in [p]) and not re.fullmatch(r'[\d]+', p):
                    out.add(p)
    # 去掉只由通用词拼成的短语
    return sorted(q for q in out if not any(q == w for w in STOP) and len(q) >= 4)
rows = []
for year, papers in build.YEARS:
    for sid, name, _ in papers:
        items = build.stem_items(sid)
        for label, text, req in items:
            ps = phrases(text)
            rows.append((sid, label, ps, text[:40]))
# 输出
import collections
by = collections.OrderedDict()
for sid, label, ps, t in rows:
    by.setdefault(sid, []).append((label, ps))
for sid, qs in by.items():
    print('==', sid)
    for label, ps in qs:
        print('  ', label, '｜', '、'.join(ps) if ps else '—')
