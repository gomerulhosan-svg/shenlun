#!/usr/bin/env python3
"""打包：python3 09_按年汇编/tools/pack_zip.py

把 09_按年汇编/ 下的 README 和各年 .md、.pdf 打成一个压缩包，包里是一个文件夹。
用 Python 的 zipfile 写，中文文件名带 UTF-8 标记，Windows 和 macOS 解压不乱码。
"""
import os, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..'))
NAME = '广东申论2020-2026_按年汇编'


def main():
    files = ['README.md'] + sorted(f for f in os.listdir(OUT) if re.match(r'^\d{4}年.*\.(md|pdf)$', f))
    path = os.path.join(OUT, NAME + '.zip')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            z.write(os.path.join(OUT, f), NAME + '/' + f)
    print('写出 %s（%d 个文件，%.1f MB）' % (os.path.relpath(path, os.path.dirname(OUT)), len(files), os.path.getsize(path) / 1e6))


if __name__ == '__main__':
    main()
