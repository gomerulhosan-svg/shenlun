#!/usr/bin/env python3
"""把 select_pairs.py 的底表拆成盲表和答案：python3 10_选材因子/tools/select_blind.py <底表目录>

- <底表目录>/blind/<卷>.json：只有段 id、原文和本卷主题，给标注员；文章顺序按哈希打乱。
- <底表目录>/key/<卷>.json：每段的 标（选用/未选/部分）、用率、对应材料、快照、位置、字数，揭盲时用。
标注校验用 10_选材因子/tools/select_validate.py（放到底表目录下运行）。
"""
import hashlib
import json
import os
import sys

THEME = {'2022县级': '粤港澳大湾区建设的实效和经验', '2023县级': '广东制造业做优做强（质量品牌、青年人才）',
         '2024一卷': '产业科技创新、高水平科技自立自强', '2024二卷': '百县千镇万村高质量发展工程（另有一道产业科技创新小题）',
         '2024选调': '青年（下乡返乡、青年科技人才、时代新人）', '2025省市': '科技创新、新质生产力（企业创新主体、成果转化）',
         '2025县镇': '乡村产业振兴（土特产、科技赋能农业）', '2025选调': '海洋强省（红树林、海洋牧场、海洋经济）',
         '2026省市': '绿色发展是高质量发展的底色', '2026县镇': '绿美广东生态建设（绿色工厂、古树名木）'}


def main(d):
    os.makedirs(os.path.join(d, 'blind'), exist_ok=True)
    os.makedirs(os.path.join(d, 'key'), exist_ok=True)
    for pp, th in THEME.items():
        src = json.load(open(os.path.join(d, pp + '.json'), encoding='utf-8'))
        arts = sorted(src['文章'], key=lambda a: hashlib.md5((pp + a['快照']).encode()).hexdigest())
        blind, key = {'卷': pp, '主题': th, '文章': []}, {'卷': pp, '段': {}}
        for i, a in enumerate(arts, 1):
            aid, segs = 'A%02d' % i, []
            for n, s in enumerate(a['段']):
                pid = '%s-%03d' % (aid, s['序'])
                segs.append({'id': pid, '文': s['文']})
                key['段'][pid] = {'标': s['标'], '用率': s['用率'], '对应材料': s['对应材料'], '快照': a['快照'],
                                 '位置': round(n / max(1, len(a['段']) - 1), 2), '字数': len(s['文'])}
            blind['文章'].append({'编号': aid, '段': segs})
        json.dump(blind, open(os.path.join(d, 'blind', pp + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(key, open(os.path.join(d, 'key', pp + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main(sys.argv[1])
