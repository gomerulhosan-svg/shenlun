# -*- coding: utf-8 -*-
# 第 1 套整卷自检：读 试卷.md、参考答案与解析.md、命题说明.md，算出版规范第六节自检表的每一项。
# 用法（仓库根目录）：python3 11_仿真卷/第1套_科技产业融合/_过程/自检_整卷.py [--md]
#   --md  最后多打印一张可以直接贴进 命题说明.md 的自检表。
# 字数口径：去掉〔段号〕和空白后的全部字符（含标点），同 10_选材因子/tools/意图检验/blocks.py 的 cc()；
#           脚本先用同一口径数 09_按年汇编 里 2025、2026 省市卷，应得 8297、8336，对不上就说明口径漂了。
# 另外做的事：
#   1 试卷.md 的材料和 _过程/材料_作文.md、材料_小题.md 逐段一字不差（三个核对脚本读的是过程稿，一致才能沿用它们的结论）；
#   2 试卷.md 里不出现过程信息（出处、合成说明、段落用途一类的词）；
#   3 答案里引用的「材料X〔n〕」「〔n〕」「材料X第 N 段」在 试卷.md 里都存在；
#   4 命题说明.md 的合成／示意逐条登记表：每条原文都在登记的那一段里；小题材料里的阿拉伯数字、数量词、时间词、字母化名、姓＋称谓都被某一条登记覆盖；
#   5 顺带跑三个既有核对脚本，摘出结论行。
import os
import re
import subprocess
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SET))
CN = '一二三四五六七八'
EXAM = date(2026, 12, 6)       # 考试日期按 12-06 推（蓝图第〇节；仓库只写"预计 12 月"，未证实）
TODAY_YEAR = 2026              # 材料里不带年份的日期、"今年"都指 2026 年
BLACK = ('广东 粤 深圳 广州 佛山 东莞 珠海 惠州 中山 江门 湛江 茂名 肇庆 清远 韶关 河源 梅州 汕头 汕尾 潮州 揭阳 云浮 阳江 '
         '南沙 前海 横琴 大湾区 香港 澳门 珠三角 顺德 宝安 番禺 天河 黄埔 光明 松山湖 北京 上海 亿航 大疆 美团 顺丰 丰翼 '
         '峰飞 小鹏 汇天 华为 腾讯 粤省事 粤医智影 开放广东 湾擎 全省 全国').split()   # 同 核查_事实核查.py D 部分
PROCESS_WORDS = ['_过程', '.md', 'grep', '考生不看', '示意', '命题', '采分', '零票', '过程文件', '审查意见', '蓝图',
                 '合成说明', '出处表', '用途', '对应程度', '候选池', '解析']
SURNAMES = set('王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤')
TITLES = '处长|医生|先生|女士|经理|秘书长|副局长|局长|警官|教授|科长|主任'


def cc(t):
    return len(re.sub(r'\s', '', t))


def parse(path):
    mats, cur = {}, None
    for line in open(path, encoding='utf-8').read().split('\n'):
        s = line.strip()
        m = re.match(r'^#*\s*【材料(.)】', s)
        if m:
            cur = m.group(1); mats[cur] = {}; continue
        if s.startswith('---') or s.startswith('# ') or (s.startswith('## ') and '【材料' not in s):
            cur = None; continue
        m = re.match(r'^〔(\d+)〕(.*)$', s)
        if m and cur:
            mats[cur][int(m.group(1))] = m.group(2).strip()
    return mats


def real_paper_totals():
    out = {}
    for y in ('2025', '2026'):
        t = open(os.path.join(ROOT, '09_按年汇编', f'{y}年广东申论_题干答案与逐句解析.md'), encoding='utf-8').read()
        for s in re.split(r'\n(?=## )', t):
            if '省市' in s.split('\n', 1)[0] and '### 给定材料' in s:
                g = s[s.index('### 给定材料'):s.index('### 题干')]
                out[y] = sum(cc(p) for p in re.findall(r'^〔\d+〕(.*)$', g, re.M))
    return out


def run(script):
    r = subprocess.run([sys.executable, os.path.join(HERE, script)], capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout


def main():
    md = '--md' in sys.argv
    fails = []
    paper_path = os.path.join(SET, '试卷.md')
    paper = open(paper_path, encoding='utf-8').read()
    M = parse(paper_path)
    ans = open(os.path.join(SET, '参考答案与解析.md'), encoding='utf-8').read()
    R = {}   # 自检表的值

    # ---------- 0 口径校准 ----------
    real = real_paper_totals()
    print('口径校准（09_按年汇编 省市卷）：', real, '（应为 2025=8297、2026=8336）')
    if real != {'2025': 8297, '2026': 8336}:
        fails.append('字数口径和真卷算法对不上')

    # ---------- 1 则数、字数 ----------
    order = [k for k in CN if k in M]
    per = {k: sum(cc(p) for p in M[k].values()) for k in order}
    total = sum(per.values())
    print('\n一、则数、字数')
    print(f'  则数 {len(order)}；总字数 {total}')
    for k in order:
        print(f'  材料{k}：{len(M[k])} 段，{per[k]} 字，段长 {min(cc(p) for p in M[k].values())}–{max(cc(p) for p in M[k].values())}')
    R['则数'] = len(order); R['总字数'] = total; R['各则'] = per
    if len(order) != 8 or not (7800 <= total <= 8900):
        fails.append('则数或总字数不在规范区间')

    # ---------- 2 试卷与过程稿一致；试卷里无过程信息 ----------
    P = {}
    P.update(parse(os.path.join(HERE, '材料_作文.md')))
    P.update(parse(os.path.join(HERE, '材料_小题.md')))
    diff = [(k, n) for k in CN for n in set(M.get(k, {})) | set(P.get(k, {})) if M.get(k, {}).get(n) != P.get(k, {}).get(n)]
    print('\n二、试卷.md 与过程稿逐段比对：', '一字不差' if not diff else f'不一致 {diff}')
    if diff: fails.append('试卷与过程稿不一致')
    head = paper[:paper.index('## 给定材料')]
    tail = paper[paper.index('## 作答要求'):]
    body = ''.join(p for v in M.values() for p in v.values())
    leak = [w for w in PROCESS_WORDS if w in head or w in tail or w in body]
    print('  试卷.md 里的过程信息用词：', leak or '无')
    if leak: fails.append(f'试卷里有过程信息 {leak}')
    other = [l for l in paper.split('\n') if l.strip() and not re.match(r'^(#|〔\d+〕|\*\*问题|要求|（\d）|\d\. )', l.strip())]
    print('  试卷.md 里既不是标题、段落、题干、要求、注意事项的行：', other or '无')
    if other: fails.append('试卷里有多余的行')

    # ---------- 3 材料一 ----------
    m1 = M['一']
    xi = [n for n, p in m1.items() if '习近平' in p and '摘自' not in p]
    print('\n三、材料一：含"习近平"的段', xi, '；出处注段', [n for n, p in m1.items() if '摘自' in p])
    R['材料一'] = f'是：〔{"〕〔".join(map(str, xi))}〕为习近平总书记讲话原话（《求是》2025 年第 22 期三段＋2025-11 新华社通稿），〔{len(m1)}〕为出处注'

    # ---------- 4 题干：问题一、问题二指定材料 ----------
    stem = tail
    q1 = re.search(r'\*\*问题一\*\*(.+)', stem).group(1)
    q2 = re.search(r'\*\*问题二\*\*(.+)', stem).group(1)
    q3 = re.search(r'\*\*问题三\*\*(.+)', stem).group(1)
    n1 = int(re.search(r'根据材料\s*(\d)', q1).group(1)); n2 = int(re.search(r'根据材料\s*(\d)', q2).group(1))
    k1, k2 = CN[n1 - 1], CN[n2 - 1]
    print('\n四、小题指定材料')
    print(f'  问题一 → 第 {n1} 则（材料{k1}），{per[k1]} 字，{len(M[k1])} 段；规范：第 2–5 则、1200–2000 字 →',
          '合格' if 2 <= n1 <= 5 and 1200 <= per[k1] <= 2000 else '不合格')
    print(f'  问题二 → 第 {n2} 则（材料{k2}），{per[k2]} 字，{len(M[k2])} 段；规范：第 4–8 则、1200–2000 字 →',
          '合格' if 4 <= n2 <= 8 and 1200 <= per[k2] <= 2000 else '不合格')
    print(f'  问题一在问题二之前：{n1 < n2}；两则合计 {per[k1] + per[k2]} 字，占全卷 {100 * (per[k1] + per[k2]) / total:.1f}%')
    if not (2 <= n1 <= 5 and 4 <= n2 <= 8 and n1 < n2 and 1200 <= per[k1] <= 2000 and 1200 <= per[k2] <= 2000):
        fails.append('小题材料位置或字数不合规范')
    R['q1'] = (n1, k1, per[k1], len(M[k1])); R['q2'] = (n2, k2, per[k2], len(M[k2]))
    R['小题占比'] = 100 * (per[k1] + per[k2]) / total

    # 组织方与身份
    ident = re.search(r'假如你是(.+?)工作人员', q2).group(1)
    org = re.search(r'([A-Z]市[^，。]{2,12}?)召开', M[k2][1])
    orgname = org.group(1) if org else None
    ok = orgname is not None and orgname == ident
    print(f'  问题二身份「{ident}工作人员」；材料{k2}〔1〕组织方「{orgname}」召开 → {"对应" if ok else "不对应"}')
    if not ok: fails.append('问题二组织方与身份不对应')
    R['组织方'] = (orgname, ident, ok)
    # 城市代号：题干和材料一致
    c1 = re.search(r'概括([A-Z])市', q1).group(1); c2 = re.findall(r'([A-Z])市', q2)
    print(f'  城市代号：问题一 {c1} 市（材料{k1}里 {c1}市 出现 {"".join(M[k1].values()).count(c1 + "市")} 次）；'
          f'问题二 {set(c2)} 市（材料{k2}里 {c2[0]}市 出现 {"".join(M[k2].values()).count(c2[0] + "市")} 次）')

    # 真实地名
    print('  小题材料真实地名／企业名（黑名单扫描）：')
    R['地名'] = {}
    for k in (k1, k2):
        t = ''.join(M[k].values())
        hit = [(w, t.count(w)) for w in BLACK if w in t]
        R['地名'][k] = hit
        print(f'    材料{k}：', hit or 0)
        if hit: fails.append(f'材料{k} 有真实地名 {hit}')

    # 对象词位置与密度
    print('  问题一对象词（每千字）：')
    for w in ('人工智能+', '公共服务领域'):   # 问题一题干「在公共服务领域深化拓展“人工智能+”」的两个对象词（定稿核查时题干改用 R26 原话）
        dens = {k: 1000 * ''.join(M[k].values()).count(w) / per[k] for k in order}
        first3 = [n for n in (1, 2, 3) if w in M[k1].get(n, '')]
        top = max(dens, key=dens.get)
        print(f'    「{w}」 材料{k1} {dens[k1]:.2f}，其他各则最高 {max(v for k, v in dens.items() if k != k1):.2f}；'
              f'出现在材料{k1}前三段的 {first3}；最密的一则：材料{top}')
        R.setdefault('对象词', []).append((w, dens[k1], max(v for k, v in dens.items() if k != k1), first3, top))

    # ---------- 5 答案：首段、整段零票 ----------
    print('\n五、首段与整段零票（按答案解析「来源：」行算：每行第一个段号是采分分句的出处，同一行后面的段号是借词或佐证）')
    secs = {'三': ans[ans.index('## 问题一'):ans.index('## 问题二')], '五': ans[ans.index('## 问题二'):ans.index('## 问题三')]}
    R['零票'] = {}
    for k, sec in secs.items():
        cited, aux = set(), set()
        for line in sec.split('\n'):
            if '来源：' not in line: continue
            last = None; first = True
            for mm in re.finditer(r'(材料([一二三四五六七八]))?〔(\d+)〕', line):
                mat = mm.group(2) or last or k
                if mm.group(2): last = mm.group(2)
                if mat == k: (cited if first else aux).add(int(mm.group(3)))
                first = False
        zero = [n for n in M[k] if n not in cited]
        zc = sum(cc(M[k][n]) for n in zero)
        aux_only = sorted(n for n in aux if n not in cited)
        print(f'  材料{k}：采分分句出处段 {sorted(cited)}；整段零票 {zero}，{zc} 字，占本则 {100 * zc / per[k]:.1f}%；首段〔1〕零票：{1 in zero}；'
              f'只被借词、佐证引到的段 {aux_only or "无"}')
        R['零票'][k] = (zero, zc, 100 * zc / per[k], 1 in zero, aux_only)
        if 1 not in zero: fails.append(f'材料{k} 首段有采分')

    # ---------- 6 答案字数 ----------
    print('\n六、答案字数（含标点，不含空白）')
    def ans_lines(sec):
        a0 = sec.index('### 答案'); a1 = sec.index('\n（', a0)
        return [l[1:].strip() for l in sec[a0:a1].split('\n') if l.startswith('>') and l[1:].strip()]
    a1 = ans_lines(secs['三']); a2 = ans_lines(secs['五'])
    n_a1 = sum(cc(x) for x in a1); n_a2 = sum(cc(x) for x in a2)
    i2 = a2.index('对策：')
    p_col = sum(cc(x) for x in a2[:i2]); d_col = sum(cc(x) for x in a2[i2:])
    items1 = [x for x in a1 if re.match(r'^[一二三四五六七八九十]、', x)]
    items2p = [x for x in a2[:i2] if re.match(r'^[一二三四五六七八九十]、', x)]
    items2d = [x for x in a2[i2:] if re.match(r'^[一二三四五六七八九十]、', x)]
    e0 = ans.index('### 作文'); e1 = ans.index('### 逐句解析', e0)
    el = [l[1:].strip().replace('*', '') for l in ans[e0:e1].split('\n') if l.startswith('>') and l[1:].strip()]
    n_e = sum(cc(x) for x in el); n_et = sum(cc(x) for x in el[:2])
    print(f'  问题一：{n_a1} 字 / 上限 200；{len(items1)} 条')
    print(f'  问题二：{n_a2} 字 / 上限 300（问题栏 {p_col}，对策栏 {d_col}）；问题 {len(items2p)} 条、对策 {len(items2d)} 条')
    print(f'  作文：含标题 {n_e} 字（标题 {n_et}，正文 {n_e - n_et}）/ 1000 字左右')
    if n_a1 > 200 or n_a2 > 300 or not (900 <= n_e <= 1100): fails.append('答案字数超限')
    R['答案'] = (n_a1, len(items1), n_a2, p_col, d_col, len(items2p), len(items2d), n_e, n_et)

    # ---------- 7 答案里的段号都在试卷里 ----------
    print('\n七、答案里引用的段号在试卷.md 里是否存在')
    qpat = re.compile(r'(材料([一二三四五六七八]))?〔(\d+)〕')
    dpat = re.compile(r'(材料([一二三四五六七八]))?第\s*(\d+)\s*段')
    refs, missing, ambiguous, byctx = set(), [], [], []
    sec = None; ctx = None   # ctx：上文最近一次写明的材料名（遇到标题或范文句行清空），给作文解析里只写「第 N 段」的行定则号
    for ln, line in enumerate(ans.split('\n'), 1):
        if line.startswith('## 问题一'): sec = '三'
        elif line.startswith('## 问题二'): sec = '五'
        elif line.startswith('## 问题三'): sec = None
        if line.startswith('#') or line.startswith('**'): ctx = None
        last = None
        for mm in qpat.finditer(line):
            mat = mm.group(2) or last or sec
            if mm.group(2): last = mm.group(2)
            if not mat: ambiguous.append((ln, mm.group(0))); continue
            refs.add((mat, int(mm.group(3))))
            if int(mm.group(3)) not in M.get(mat, {}): missing.append((ln, f'材料{mat}〔{mm.group(3)}〕'))
        for mm in dpat.finditer(line):
            mat = mm.group(2)
            if not mat:
                ms = re.findall(r'材料([一二三四五六七八])', line[:mm.start()])
                mat = ms[-1] if ms else sec
            if not mat and ctx:
                mat = ctx; byctx.append((ln, f'{mm.group(0)}→材料{ctx}'))
            if not mat: ambiguous.append((ln, mm.group(0))); continue
            refs.add((mat, int(mm.group(3))))
            if int(mm.group(3)) not in M.get(mat, {}): missing.append((ln, f'材料{mat}第{mm.group(3)}段'))
        ms = re.findall(r'材料([一二三四五六七八])', line)
        if ms: ctx = ms[-1]
    by = {}
    for m_, n_ in refs: by.setdefault(m_, set()).add(n_)
    print(f'  引到的不同段 {len(refs)} 个：', {k: sorted(v) for k, v in sorted(by.items(), key=lambda x: CN.index(x[0]))})
    print(f'  试卷里不存在的 {len(missing)} 个', missing[:10], f'；认不出是哪则的 {len(ambiguous)} 个', ambiguous[:10])
    print(f'  本行没写材料名、按上文定则号的 {len(byctx)} 个：', byctx)
    if missing or ambiguous: fails.append('答案段号有对不上的')
    R['段号'] = (len(refs), len(missing), len(ambiguous))

    # ---------- 8 作文题干逐字片段 ----------
    print('\n八、作文题干与材料的逐字片段')
    quote = re.search(r'围绕“(.+?)”', q3).group(1)
    loc = [(k, n) for k in order for n, p in M[k].items() if quote in p]
    stem_txt = re.sub(r'（\d+分）', '', q3)
    best = ''
    for i in range(len(stem_txt)):
        for j in range(len(stem_txt), i + len(best), -1):
            if stem_txt[i:j] in body:
                best = stem_txt[i:j]; break
    print(f'  题干引语「{quote}」{cc(quote)} 字，逐字所在段：', [f'材料{k}〔{n}〕' for k, n in loc])
    print(f'  题干里能逐字贴回材料的最长片段：「{best}」{cc(best)} 字')
    if cc(best) < 10 or not loc: fails.append('作文题干没有 10 字以上逐字片段')
    R['题干'] = (quote, cc(quote), loc, best)

    # ---------- 9 最晚的事 ----------
    print('\n九、作文材料里最晚的事')
    ESSAY = [k for k in order if k not in (k1, k2)]
    dates = []
    for k in ESSAY:
        for n, p in M[k].items():
            for mm in re.finditer(r'(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日', p):
                y = int(mm.group(1)) if mm.group(1) else TODAY_YEAR
                dates.append((date(y, int(mm.group(2)), int(mm.group(3))), f'材料{k}〔{n}〕', mm.group(0)))
    dates.sort()
    last_ev = dates[-1]
    src = open(os.path.join(HERE, '作文材料_出处.md'), encoding='utf-8').read()
    tbl = src[src.index('## 二、总表'):src.index('## 三、逐段对照')]
    rep = []
    for line in tbl.split('\n'):
        m = re.match(r'^\| (材料.) \|', line)
        if m:
            for d in re.findall(r'(20\d\d)-(\d\d)-(\d\d)', line.split('|')[-2]):
                rep.append((date(*map(int, d)), m.group(1)))
    rep.sort()
    last_rep = rep[-1]
    wk = lambda d: (EXAM - d).days / 7
    print(f'  材料正文里写明日期的最晚一件：{last_ev[0]}（{last_ev[1]}「{last_ev[2]}」），距 {EXAM} 考试 {(EXAM - last_ev[0]).days} 天，约 {wk(last_ev[0]):.1f} 周')
    print(f'  出处表里最晚的报道：{last_rep[0]}（{"、".join(sorted(set(k for d, k in rep if d == last_rep[0]), key=lambda x: CN.index(x[-1])))}），距考试 {(EXAM - last_rep[0]).days} 天，约 {wk(last_rep[0]):.1f} 周')
    print('  真卷 3.5–6 周 →', '达标' if wk(last_rep[0]) <= 6 else '不达标（出卷日 2026-09-28 所限）')
    rep_mats = sorted(set(k for d, k in rep if d == last_rep[0]), key=lambda x: CN.index(x[-1]))
    R['时效'] = (last_ev, last_rep, wk(last_ev[0]), wk(last_rep[0]), rep_mats)

    # ---------- 10 合成／示意逐条登记 ----------
    print('\n十、命题说明.md 合成／示意逐条登记')
    note_path = os.path.join(SET, '命题说明.md')
    R['登记'] = None
    if os.path.exists(note_path):
        note = open(note_path, encoding='utf-8').read()
        rows = re.findall(r'^\| (M[35]-\d+) \| 材料(.)〔(\d+)〕 \| (.+?) \| (合成|示意|真实原句|真实文件用语)（?[^|]*?\|', note, re.M)
        notin, cover = [], {}
        cnt = {}
        for rid, k, n, frag, cat in rows:
            frag = frag.strip().strip('「」')
            cnt[cat] = cnt.get(cat, 0) + 1
            parts = [x for x in frag.split('……') if x]
            if not all(x in M[k].get(int(n), '') for x in parts):
                notin.append((rid, k, n, frag[:20]))
            cover.setdefault((k, int(n)), []).extend(parts)
        dual = re.findall(r'^\| (M[35]-\d+) \|[^|]*\|[^|]*\| [^|]*；示意', note, re.M)   # 双标注（合成；示意），上面按第一个标注计
        print(f'  登记 {len(rows)} 条，按类别 {cnt}（按第一个标注计；另有双标注 {dual}）；原文不在登记段里的 {len(notin)} 条', notin)
        # 覆盖检查：数字、数量词、时间词按段查（登记在同一段才算）；字母化名、姓＋称谓按则查（同一则登记过一次即可）
        num_pat = re.compile(r'[0-9]+(?:\.[0-9]+)?%?|[几上两三十百千万]+(?:多|余)?(?:个|家|批|张|秒钟|分钟|小时|天|成|架次|岁|部门|件|栋)|'
                             r'超过千万|大半天|一个多月|今年以来|今年汛期|今年\d+月|一年前|这两年|去年|近日|年初')
        name_pat = re.compile(r'[A-Z](?:市|区|街道)|[A-Z][\u4e00-\u9fff]{0,4}?公司|'
                              r'[' + ''.join(sorted(SURNAMES)) + r'](?:' + TITLES + r')|小[\u4e00-\u9fff](?=[：“，的自])|老[\u4e00-\u9fff](?=[：“，不])')
        uncovered = []
        ntok = 0
        for k in (k1, k2):
            whole_k = [f for (kk, _), fs in cover.items() if kk == k for f in fs]
            for n, p in M[k].items():
                for mm in num_pat.finditer(p):
                    tok = mm.group(0); ntok += 1
                    if not any(tok in f for f in cover.get((k, n), [])):
                        uncovered.append(f'材料{k}〔{n}〕{tok}')
                for mm in name_pat.finditer(p):
                    tok = mm.group(0); ntok += 1
                    if not any(tok in f for f in whole_k):
                        uncovered.append(f'材料{k}〔{n}〕{tok}')
        print(f'  小题材料里抽出的数字、数量词、时间词、化名、人物 {ntok} 处；没有被登记覆盖的 {len(uncovered)} 处', uncovered)
        if notin or uncovered: fails.append('合成登记不全或原文对不上')
        R['登记'] = (len(rows), cnt, len(notin), ntok, len(uncovered), dual)
    else:
        print('  命题说明.md 还没有，跳过')

    # ---------- 11 三个既有核对脚本 ----------
    print('\n十一、三个既有核对脚本（读过程稿；第二项已证明试卷与过程稿逐段一致）')
    rc, out = run('核对_作文材料出处.py')
    s1 = [l for l in out.split('\n') if l.startswith('键 ') or l.startswith('题干引语')]
    print('  核对_作文材料出处.py：', s1, '退出码', rc)
    rc2, out2 = run('核查_事实核查.py')
    s2 = [l.strip() for l in out2.split('\n') if l.startswith('数字 ') or l.startswith('引语 ') or '黑名单命中' in l or l.startswith('带引文') or l.startswith('范文字数')]
    unreg = [l for l in out2.split('\n') if '清单未登记：' in l and not l.rstrip().endswith('[]')]
    print('  核查_事实核查.py：', s2, '；数量词、时间词未登记的段', unreg or '无')
    rc3, out3 = run('核对_答案引文.py')
    s3 = [l.strip() for l in out3.split('\n') if l.startswith('材料来源') or l.startswith('段号') or l.startswith('「来源：」') or l.startswith('问题') or l.startswith('作文')]
    print('  核对_答案引文.py：', s3, '退出码', rc3)
    if rc3 != 0 or '问题 0 个' not in out: fails.append('既有核对脚本报了问题')
    nums = re.search(r'数字 (\d+) 个；来源里带 6 字以上上下文命中的 (\d+) 个', out2)
    R['脚本'] = (re.search(r'键 (\d+) 条；问题 (\d+) 个', out).groups(), nums.groups() if nums else None,
                 re.search(r'引语 (\d+) 处', out2).group(1), re.search(r'段号、句号引用 (\d+) 处；带引文 (\d+) 条；对不上 (\d+) 条', out3).groups(),
                 re.search(r'「来源：」行里的引文片段 (\d+) 个；贴不回材料的 (\d+) 个', out3).groups())

    print('\n结论：', '除时效一项外均通过（时效不达标，是出卷日所限，按已知缺口单列）' if not fails else f'有 {len(fails)} 项不通过：{fails}；另时效一项不达标，按已知缺口单列')
    if md:
        print_md(R)
    return 1 if fails else 0


def print_md(R):
    n1, k1, c1, p1 = R['q1']; n2, k2, c2, p2 = R['q2']
    a = R['答案']; z = R['零票']; t = R['时效']; s = R['脚本']; o = R['对象词']
    quote, ql, loc, best = R['题干']
    print('\n| 项 | 真卷参照 | 本卷（`_过程/自检_整卷.py` 算） |')
    print('|---|---|---|')
    print(f"| 材料则数、总字数 | 8 则，7850–8894 字 | {R['则数']} 则，{R['总字数']} 字（" + '、'.join(f'材料{k} {v}' for k, v in R['各则'].items()) + '）；同一口径数 2025、2026 省市卷得 8297、8336 |')
    print(f"| 材料一是否习近平讲话或中央理论 | 6/6 | {R['材料一']} |")
    print(f'| 问题一材料位置、字数 | 第 2–5 则，1200–2000 字 | 第 {n1} 则（材料{k1}），{c1} 字，{p1} 段 |')
    print(f'| 问题二材料位置、字数 | 第 4–8 则，1200–2000 字 | 第 {n2} 则（材料{k2}），{c2} 字，{p2} 段；问题一在前；两则合计占全卷 {R["小题占比"]:.1f}% |')
    org, ident, ok = R['组织方']
    print(f'| 问题二材料是否写明组织方、身份是否对应 | 8/8（仿真度审查第五节：应为 7/8 明写、1/8 靠发文单位推出） | 是：材料{k2}〔1〕"{org}召开"；题干"假如你是{ident}工作人员"，{"对应" if ok else "不对应"} |')
    g = R['地名']
    print(f"| 小题材料真实地名数 | 问题一平均 0.4、问题二 0.0 | 材料{k1} {len(g[k1])}、材料{k2} {len(g[k2])}（按 `核查_事实核查.py` 的 50 余词黑名单扫描） |")
    print(f"| 作文题干有 10 字以上片段逐字出自材料 | 8/8 | 是：「{quote}」{ql} 字，逐字见" + '、'.join(f'材料{k}〔{n}〕' for k, n in loc) + ' |')
    aux = '；'.join(f'材料{k}〔{"〕〔".join(map(str, z[k][4]))}〕只被借词、佐证引到' for k in (k1, k2) if z[k][4])
    print(f"| 首段是否背景 | 24/30 整段零票 | 是：材料{k1}〔1〕、材料{k2}〔1〕都没有采分分句。整段零票：材料{k1} 〔{'〕〔'.join(map(str, z[k1][0]))}〕{z[k1][1]} 字（{z[k1][2]:.1f}%），材料{k2} 〔{'〕〔'.join(map(str, z[k2][0]))}〕{z[k2][1]} 字（{z[k2][2]:.1f}%）；真卷中位数 19.2%" + (f'（{aux}）' if aux else '') + ' |')
    print(f"| 材料里最晚的事离考试多久 | 3.5–6 周，放在作文材料里 | 约 {t[3]:.0f} 周，**不达标**：最晚的报道 {t[1][0]}（南方日报，用在{'、'.join(t[4])}），正文写明日期的最晚一件 {t[0][0]}（{t[0][1]}「{t[0][2]}」，约 {t[2]:.1f} 周）；按 {EXAM} 考试推算；都在作文材料里 |")
    print(f"| 作文材料的每个数字是否有出处 | — | 是：`核对_作文材料出处.py` 键 {s[0][0]} 条、问题 {s[0][1]} 个；`核查_事实核查.py` 数字 {s[1][0]} 个（{s[1][1]} 个带 6 字以上上下文命中，其余是日期，说话人和场合已人工核）、引语 {s[2]} 处全部逐字命中 |")
    print(f'| 问题一参考答案条数、字数 | 约 5 条，≤200 字 | {a[1]} 条，{a[0]} 字 |')
    print(f'| 问题二参考答案条数、字数 | 问题 5–6 条＋同数对策，≤300 字 | 问题 {a[5]} 条＋对策 {a[6]} 条，{a[2]} 字（问题栏 {a[3]}、对策栏 {a[4]}） |')
    print(f'| 作文范文字数 | 1000 字左右 | 含标题 {a[7]} 字（标题 {a[8]}、正文 {a[7] - a[8]}） |')
    print(f'| 问题一对象词在前三段出现、本则最密 | 规范第四节 | ' + '；'.join(f'「{w}」本则每千字 {d:.2f}、其他各则最高 {mx:.2f}，前三段出现在〔{"〕〔".join(map(str, f3))}〕' for w, d, mx, f3, top in o) + ' |')
    r = R['段号']
    print(f'| 答案引用的段号在试卷里都存在 | — | 引到不同的段 {r[0]} 个，不存在 {r[1]} 个，认不出则号 {r[2]} 个；`核对_答案引文.py` 段号句号引用 {s[3][0]} 处、带引文 {s[3][1]} 条、对不上 {s[3][2]} 条，「来源」片段 {s[4][0]} 个、贴不回 {s[4][1]} 个 |')
    if R['登记']:
        n, cnt, bad, ntok, unc, dual = R['登记']
        dn = f'；{"、".join(dual)} 双标注"合成；示意"，按第一个标注计入合成，按标注计示意共 {cnt.get("示意", 0) + len(dual)} 条' if dual else ''
        print(f'| 小题材料合成／示意逐条登记 | 规范第二节 | 登记 {n} 条（' + '、'.join(f'{k} {v}' for k, v in cnt.items()) + f'{dn}）；原文对不上 {bad} 条；材料里抽出的数字、时间词、化名、人物 {ntok} 处，未登记 {unc} 处 |')


if __name__ == '__main__':
    sys.exit(main())
