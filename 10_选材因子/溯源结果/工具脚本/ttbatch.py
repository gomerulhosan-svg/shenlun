#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量跑头条搜索，结果另存文本，避免一次刷屏。
用法: python3 ttbatch.py out.txt "词1" "词2" ...
"""
import sys, time
sys.path.insert(0, "/Users/jianguolingyun/公考/07_申论/申论/溯源结果/_tools")
import tt2


def main():
    out = sys.argv[1]
    qs = sys.argv[2:]
    with open(out, "w", encoding="utf-8") as f:
        for q in qs:
            f.write("\n\n================ %s ================\n" % q)
            f.flush()
            import io, contextlib
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    tt2.search(q, 0, tries=4)
            except Exception as e:
                buf.write("ERR %s\n" % e)
            f.write(buf.getvalue())
            f.flush()
            time.sleep(1)
    print("WROTE", out)


if __name__ == "__main__":
    main()
