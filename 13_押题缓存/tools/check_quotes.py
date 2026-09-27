"""核对母料里的引文是否真在出处文件里。

引文格式：「原句」〔相对路径｜日期〕
- 相对路径从仓库根算起；
- 原句里可以用"……"表示省略，省略前后的每一段（去掉空白后 ≥4 字）都要按顺序出现在出处里；
- 比对前去掉空白和 markdown 的 * 号。

用法：python3 13_押题缓存/tools/check_quotes.py <母料.md> [...]
退出码：有不合格引文时为 1。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAT = re.compile(r'「([^」]{2,}?)」\s*〔([^｜〕]+)｜([^〕]*)〕')
_cache = {}


def norm(s):
    return re.sub(r'[\s*]', '', s)


def load(rel):
    if rel not in _cache:
        p = ROOT / rel.strip()
        _cache[rel] = norm(p.read_text(encoding='utf-8')) if p.is_file() else None
    return _cache[rel]


def found(quote, text):
    parts = [norm(x) for x in re.split(r'…+|\.{3,}', quote)]
    parts = [x for x in parts if len(x) >= 4] or [norm(quote)]
    pos = 0
    for x in parts:
        i = text.find(x, pos)
        if i < 0:
            return False
        pos = i + len(x)
    return True


def check(md):
    t = Path(md).read_text(encoding='utf-8')
    ok = bad = 0
    for m in PAT.finditer(t):
        q, rel, date = m.group(1), m.group(2), m.group(3)
        line = t.count('\n', 0, m.start()) + 1
        text = load(rel)
        if text is None:
            bad += 1
            print(f'{md}:{line}: 找不到文件 {rel}')
        elif not found(q, text):
            bad += 1
            print(f'{md}:{line}: 原句不在 {rel}：「{q[:40]}」')
        else:
            ok += 1
    print(f'{md}: 合格 {ok}，不合格 {bad}')
    return bad


if __name__ == '__main__':
    sys.exit(1 if sum(check(f) for f in sys.argv[1:]) else 0)
