# -*- coding: utf-8 -*-
"""天正 DXF 全图普查：实体统计 / 代理分布 / 图层清单 / 顶层块引用 / 按图层文字清单 / 关键词命中。

用法:
    python tz_survey.py 图纸.dxf [-o survey.txt] [--keywords 无线AP,ONU,支架] [--top 40]

产出定位: 图纸目录图层(CATALOG)、图例图层、楼层块名、设备块名清单。
注意: 100MB 级 DXF readfile 约 1~2 分钟；结果写文件，控制台只打印摘要。
"""
import argparse
import sys
from collections import Counter

import ezdxf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description="天正 DXF 全图普查")
    ap.add_argument("dxf")
    ap.add_argument("-o", "--out", help="输出报告路径（默认 <dxf>_survey.txt）")
    ap.add_argument("--keywords", default="", help="逗号分隔关键词，输出命中文字明细")
    ap.add_argument("--top", type=int, default=40, help="每个图层文字清单最多展示条数")
    a = ap.parse_args()

    doc = ezdxf.readfile(a.dxf)
    msp = doc.modelspace()
    kws = [k.strip() for k in a.keywords.split(",") if k.strip()]

    types = Counter(e.dxftype() for e in msp)
    proxy_layer = Counter(e.dxf.layer for e in msp if e.dxftype() == "ACAD_PROXY_ENTITY")
    layers_defined = [l.dxf.name for l in doc.layers]   # LayerTable 定义全表(含未使用)
    layer_used = Counter(e.dxf.layer for e in msp)      # 模型空间实际引用
    blocks = Counter(e.dxf.name for e in msp if e.dxftype() == "INSERT")

    text_by_layer = {}
    kw_hits = []
    for e in msp:
        t = e.dxftype()
        if t == "TEXT":
            s = e.dxf.text.strip()
        elif t == "MTEXT":
            s = e.plain_text().strip()
        else:
            continue
        if not s:
            continue
        text_by_layer.setdefault(e.dxf.layer, Counter())[s] += 1
        if kws and any(k in s for k in kws):
            x, y = e.dxf.insert.x, e.dxf.insert.y
            kw_hits.append((e.dxf.layer, f"{x:.0f},{y:.0f}", s))

    out = a.out or (a.dxf.rsplit(".", 1)[0] + "_survey.txt")
    with open(out, "w", encoding="utf-8") as f:
        W = f.write
        W("=" * 70 + "\n【实体类型统计】\n")
        for t, n in types.most_common():
            W(f"  {t:24s} {n}\n")
        W("\n【代理对象按图层】(天正未炸对象, 集中在建筑层属正常)\n")
        for l, n in proxy_layer.most_common():
            W(f"  {l:32s} {n}\n")
        W(f"  合计 {sum(proxy_layer.values())}\n")
        W(f"\n【图层清单】定义 {len(layers_defined)} 个 / 模型空间实际使用 {len(layer_used)} 个\n")
        for l, n in layer_used.most_common():
            W(f"  {l:32s} {n}\n")
        unused = set(layers_defined) - set(layer_used)
        if unused:
            W(f"  （定义但未使用 {len(unused)} 个，略）\n")
        W(f"\n【顶层块引用 TOP{a.top}】(块全名, 括号内原名无语义)\n")
        for b, n in blocks.most_common(a.top):
            W(f"  x{n:<5} {b}\n")
        W("\n【按图层文字清单】(实例数/去重数)\n")
        for lay, cnt in sorted(text_by_layer.items()):
            W(f"\n=== 图层 [{lay}]  文字 {sum(cnt.values())} 条, 去重 {len(cnt)} ===\n")
            for s, n in cnt.most_common(a.top):
                W(f"  x{n:<5} {s}\n")
        if kws:
            W(f"\n【关键词命中明细】{kws}  共 {len(kw_hits)} 条\n")
            for lay, xy, s in kw_hits:
                W(f"  [{lay}] ({xy}) {s}\n")

    print(f"实体 {sum(types.values()):,} | 代理 {sum(proxy_layer.values())} | "
          f"图层 定义{len(layers_defined)}/使用{len(layer_used)} | "
          f"块引用 {sum(blocks.values()):,} | 关键词命中 {len(kw_hits)}")
    print(f"报告: {out}")


if __name__ == "__main__":
    main()
