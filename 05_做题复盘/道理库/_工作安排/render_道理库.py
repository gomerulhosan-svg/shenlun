import json
import sys
from collections import OrderedDict

THEME_NAMES = {
    1: "走在前列", 2: "高质量发展", 3: "新质生产力·科技自立自强", 4: "现代化产业体系·制造业当家",
    5: "人工智能+·数字广东", 6: "扩大内需", 7: "改革·营商环境", 8: "对外开放·大湾区",
    9: "百千万·乡村振兴·县域", 10: "海洋强省", 11: "绿色发展·绿美广东", 12: "文化强省",
    13: "民生·共同富裕·公共服务", 14: "发展和安全·法治平安", 15: "城市高质量发展",
}
VERDICT = {"hit": "命中", "partial": "部分", "miss": "没有"}


def group_key(g):
    if g == "通用":
        return (0, 0)
    try:
        return (1, int(str(g).split("-")[0]))
    except ValueError:
        return (2, 0)


def id_key(e):
    i = e["id"]
    if i.startswith("T"):
        try:
            return (0, int(i[1:].split("-")[0]), i)
        except ValueError:
            return (0, 999, i)
    parts = i.split("-")
    try:
        return (1, int(parts[0]), int(parts[1]) if len(parts) > 1 else 0, i)
    except ValueError:
        return (2, 0, 0, i)


def themes_str(ts):
    return "、".join(f"{t} {THEME_NAMES.get(t, '')}".strip() for t in sorted(set(ts or [])))


def render_library(d):
    lib = sorted(d["library"], key=id_key)
    core = [e for e in lib if e.get("core")]
    out = []
    out.append("# 道理库：全库\n")
    out.append(f"共 {len(lib)} 条，其中核心 {len(core)} 条（打 ★ 的）。每条一句考场句，下面是钩子、信号词、为什么成立、别说过头的地方，以及支撑它的原文。\n")
    out.append("- **钩子**：大白话，用来记。考场上在材料页边写钩子，句子就跟着出来。")
    out.append("- **信号**：题干或材料里看到这些说法，就想到这一条。")
    out.append("- **原文**：「」里的字和出处文件逐字一致，可以当道理句直接用。没有原文的，用考场句。\n")

    out.append("## 按主题找\n")
    out.append("题干落在哪个主题，就先看那一行的条目。通用条目（T 开头）几乎每题都能挂。\n")
    out.append("| 主题 | 条目 |")
    out.append("|---|---|")
    for t in range(1, 16):
        ids = [e["id"] + ("★" if e.get("core") else "") for e in lib if t in (e.get("themes") or [])]
        out.append(f"| {t} {THEME_NAMES[t]} | {'、'.join(ids) if ids else '（无）'} |")
    out.append("")

    groups = OrderedDict()
    for e in sorted(lib, key=lambda x: (group_key(x.get("group", "")), id_key(x))):
        g = e.get("group", "")
        groups.setdefault(g, []).append(e)
    for g, es in groups.items():
        if g == "通用":
            out.append("## 通用\n")
        else:
            try:
                n = int(str(g).split("-")[0])
                out.append(f"## {n} {THEME_NAMES.get(n, '')}\n")
            except ValueError:
                out.append(f"## {g}\n")
        for e in es:
            star = "★ " if e.get("core") else ""
            out.append(f"**{star}{e['id']}　{e['reason']}**\n")
            meta = [f"钩子：{e.get('hook', '')}"]
            if e.get("signals"):
                meta.append("信号：" + "、".join(e["signals"]))
            if e.get("cost"):
                meta.append("讲代价")
            out.append("- " + "｜".join(meta))
            out.append(f"- 为什么：{e.get('mechanism', '')}")
            if e.get("limit"):
                out.append(f"- 别说过头：{e['limit']}")
            out.append(f"- 主题：{themes_str(e.get('themes'))}")
            if e.get("anchor"):
                out.append(f"- 原文：「{e['anchor']}」（{e.get('anchor_source', '')}）")
            out.append("")
    return "\n".join(out)


def render_core(d):
    lib = sorted([e for e in d["library"] if e.get("core")], key=id_key)
    out = ["# 道理库：核心一页\n", f"{len(lib)} 条。每天读一遍，三分钟。左边是考场句，右边是钩子。\n"]
    out.append("| 条目 | 考场句 | 钩子 |")
    out.append("|---|---|---|")
    for e in lib:
        out.append(f"| {e['id']} | {e['reason']} | {e.get('hook', '')} |")
    return "\n".join(out) + "\n"


def pct(a, b):
    return f"{(100.0 * a / b):.0f}%" if b else "—"


def render_coverage(d):
    st = d["stats"]
    out = ["# 道理库：覆盖测试\n"]
    out.append("每道题先由一个没见过道理库的人，只看题干和材料（预测题只看文件），列出写好这篇要用到的道理：开头立什么理、每段第二句放什么道理、哪里写代价。再由另一个人拿道理库逐条判：命中（直接能用，最多改几个字）、部分（要明显改写或两条拼）、没有。首轮判完，把没有的补进库，再判一遍。\n")
    out.append("## 总数\n")
    out.append("| 题组 | 需要的道理 | 首轮 命中/部分/没有 | 补后 命中/部分/没有 | 补后 命中率 | 补后 命中＋部分 |")
    out.append("|---|---|---|---|---|---|")
    order = ["真题", "选调", "仿真", "预测"]
    tot_b = {"hit": 0, "partial": 0, "miss": 0, "none": 0, "total": 0}
    tot_a = dict(tot_b)
    for s in order:
        b = st["before"].get(s)
        a = st["after"].get(s)
        if not b:
            continue
        for k in tot_b:
            tot_b[k] += b.get(k, 0)
            tot_a[k] += a.get(k, 0)
        out.append(f"| {s} | {b['total']} | {b['hit']}/{b['partial']}/{b['miss']} | {a['hit']}/{a['partial']}/{a['miss']} | {pct(a['hit'], a['total'])} | {pct(a['hit'] + a['partial'], a['total'])} |")
    out.append(f"| 合计 | {tot_b['total']} | {tot_b['hit']}/{tot_b['partial']}/{tot_b['miss']} | {tot_a['hit']}/{tot_a['partial']}/{tot_a['miss']} | {pct(tot_a['hit'], tot_a['total'])} | {pct(tot_a['hit'] + tot_a['partial'], tot_a['total'])} |")
    if tot_b.get("none") or tot_a.get("none"):
        out.append(f"\n另有 {tot_b['none']} 条首轮没判到、{tot_a['none']} 条补后没判到（判题的代理出错），不算进命中。")
    out.append("")

    cue_total = cue_ok = 0
    for t in d["coverage"]:
        for n in t["needs"]:
            f = n.get("first")
            if f and f.get("verdict") in ("hit", "partial"):
                cue_total += 1
                if f.get("cue_ok"):
                    cue_ok += 1
    out.append(f"**想不想得起来**：首轮命中或部分命中的 {cue_total} 条里，有 {cue_ok} 条（{pct(cue_ok, cue_total)}）在那道题的题干或需要里能找到对应条目的信号词。\n")

    out.append("## 逐题\n")
    for s in order:
        ts = [t for t in d["coverage"] if t["set"] == s]
        if not ts:
            continue
        out.append(f"### {s}\n")
        for t in ts:
            out.append(f"**{t['key']}　{t['title']}**\n")
            for n in t["needs"]:
                f = n.get("first") or {}
                fi = n.get("final") or {}
                fv = VERDICT.get(f.get("verdict"), "未判")
                av = VERDICT.get(fi.get("verdict"), "未判")
                fids = "、".join(f.get("ids") or [])
                aids = "、".join(fi.get("ids") or [])
                change = f"{fv}{('（' + fids + '）') if fids else ''}"
                if (fi.get("verdict") != f.get("verdict")) or (aids != fids):
                    change += f" → {av}{('（' + aids + '）') if aids else ''}"
                note = fi.get("note") or f.get("note") or ""
                out.append(f"- 【{n['role']}】{n['point']}：{n['reason']}｜{change}{('｜' + note) if note else ''}")
            out.append("")

    out.append("## 预测题\n")
    for f in d.get("forecast", []):
        out.append(f"**{f['key']}　{f['title']}**（{f.get('level', '')}，{f.get('type', '')}）\n")
        out.append(f"- 为什么可能考：{f.get('why', '')}")
        if f.get("docs"):
            out.append("- 取材文件：" + "、".join(x.replace('/home/user/shenlun/', '') for x in f["docs"]))
        out.append("")

    if d.get("dropped"):
        out.append("## 复核时删掉的条目\n")
        for x in d["dropped"]:
            out.append(f"- {x.get('id', '')}　{x.get('reason', '')}：{x.get('why', '')}")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    src, outdir = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(f"{outdir}/道理库.md", "w", encoding="utf-8") as fh:
        fh.write(render_library(data))
    with open(f"{outdir}/核心一页.md", "w", encoding="utf-8") as fh:
        fh.write(render_core(data))
    with open(f"{outdir}/覆盖测试.md", "w", encoding="utf-8") as fh:
        fh.write(render_coverage(data))
    print("ok", len(data["library"]))
