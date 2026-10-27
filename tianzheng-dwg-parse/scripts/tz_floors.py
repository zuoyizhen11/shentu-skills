# -*- coding: utf-8 -*-
"""tz_floors.py — 天正 DXF 逐层统计（y 聚类）。

模型空间多图框竖列堆叠时，用实体 y 值聚类近似切层：
  --block 块名片段 -> 统计插入点数量，逐层给出计数与属性值分布
  --text  关键词   -> 逐层统计含关键词的 TEXT/MTEXT
  --labels 把 y 范围映射成楼层名，便于出表

用法:
    python tz_floors.py plan.dxf --block 00000240 \
        --xband 300000,470000 --gap 40000 \
        --labels "3F=156395-240495,35F=895137-979237" -o report.txt

两遍定位法: 先不带 --labels 跑一遍，从报告抄各簇 y 范围，
回填成 --labels 再跑一遍，即得带楼层名的成品表。
gap 取楼层间距的 1/3 左右（毫米图常用 30000~50000）。

注意: 100MB 级 DXF readfile 约 1~2 分钟；结果写文件，控制台只打印摘要。
"""
import argparse
import sys
from collections import Counter

import ezdxf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_labels(s):
    """'3F=156395-240495,35F=895137-979237' -> [('3F',156395.0,240495.0), ...]"""
    out = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        name, rng = part.split("=", 1)
        y0, y1 = rng.split("-", 1)
        out.append((name.strip(), float(y0), float(y1)))
    return out


def cluster_pts(pts, gap):
    """pts=[(x, y, extra), ...] 按 y 升序，相邻差 > gap 切簇。"""
    pts = sorted(pts, key=lambda p: p[1])
    clusters, cur = [], [pts[0]]
    for p in pts[1:]:
        if p[1] - cur[-1][1] > gap:
            clusters.append(cur)
            cur = [p]
        else:
            cur.append(p)
    clusters.append(cur)
    return clusters


def floor_name(cy, ylo, yhi, labels):
    """质心落在哪个 label 区间就用哪个名字，否则显示 y 范围。"""
    for name, a, b in labels:
        if a <= cy <= b:
            return name
    return "y%.0f~%.0f" % (ylo, yhi)


def fmt_dist(counter, limit=10):
    """Counter -> 紧凑字符串，种类过多截断。"""
    items = counter.most_common()
    s = ", ".join("%r x%d" % (v, n) for v, n in items[:limit])
    if len(items) > limit:
        s += ", ...(%d 种)" % len(items)
    return s


def main():
    ap = argparse.ArgumentParser(description="天正 DXF 逐层统计（y 聚类）")
    ap.add_argument("dxf", help="DXF 文件路径")
    ap.add_argument("-o", "--out", help="输出报告路径（默认 <dxf>_floors.txt）")
    ap.add_argument("--block", action="append", default=[], metavar="FRAG",
                    help="块名片段（可多次），统计插入点数量与属性分布")
    ap.add_argument("--text", action="append", default=[], metavar="KW",
                    help="文字关键词（可多次），逐层计数并列明细")
    ap.add_argument("--xband", metavar="X0,X1",
                    help="只统计 x0<=x<=x1 带内实体（多图框横排/双列时限定一列）")
    ap.add_argument("--gap", type=float, default=40000.0,
                    help="聚类间距阈值（默认 40000，约取楼层间距 1/3）")
    ap.add_argument("--labels",
                    help='楼层名映射: "名=y0-y1[,名=y0-y1...]"（质心落区间即命名）')
    a = ap.parse_args()

    doc = ezdxf.readfile(a.dxf)
    msp = doc.modelspace()
    labels = parse_labels(a.labels) if a.labels else []
    x0 = x1 = None
    if a.xband:
        x0, x1 = (float(v) for v in a.xband.split(",", 1))

    def in_band(x):
        return x0 is None or (x0 <= x <= x1)

    lines = []
    w = lines.append
    w("=" * 72)
    w("tz_floors 逐层统计报告")
    w("DXF   : %s" % a.dxf)
    w("gap=%.0f  xband=%s  blocks=%s  text=%s" %
      (a.gap, a.xband or "全图", ",".join(a.block) or "-", ",".join(a.text) or "-"))
    w("=" * 72)

    # ---------- 块插入点逐层统计 ----------
    for frag in a.block:
        pts = []  # (x, y, attribs)
        for ins in msp.query("INSERT"):
            if frag not in ins.dxf.name:
                continue
            x, y = ins.dxf.insert.x, ins.dxf.insert.y
            if not in_band(x):
                continue
            attribs = {at.dxf.tag: at.dxf.text for at in ins.attribs}
            pts.append((x, y, attribs))
        w("")
        w("-" * 72)
        w("块片段 [%s]  总计 %d 个插入点" % (frag, len(pts)))
        if not pts:
            continue
        for cl in cluster_pts(pts, a.gap):
            ys = [p[1] for p in cl]
            cy = sum(ys) / len(ys)
            name = floor_name(cy, min(ys), max(ys), labels)
            w("  %-16s n=%-5d y %.0f ~ %.0f" % (name, len(cl), min(ys), max(ys)))
            dist = {}  # tag -> Counter(值)
            for _, _, attribs in cl:
                for tag, val in attribs.items():
                    dist.setdefault(tag, Counter())[val] += 1
            for tag in sorted(dist):
                w("      attr %-14s %s" % (tag, fmt_dist(dist[tag])))

    # ---------- 文字关键词逐层统计 ----------
    if a.text:
        tpts = []  # (x, y, 文本)
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
            x, y = e.dxf.insert.x, e.dxf.insert.y
            if not in_band(x):
                continue
            tpts.append((x, y, s))
        w("")
        w("-" * 72)
        w("文字关键词逐层统计（带内文字实体共 %d 条）" % len(tpts))
        for kw in a.text:
            hits = [p for p in tpts if kw in p[2]]
            w("")
            w("关键词 [%s]  总计 %d 处" % (kw, len(hits)))
            if not hits:
                continue
            for cl in cluster_pts(hits, a.gap):
                ys = [p[1] for p in cl]
                cy = sum(ys) / len(ys)
                name = floor_name(cy, min(ys), max(ys), labels)
                w("  %-16s n=%-5d y %.0f ~ %.0f" % (name, len(cl), min(ys), max(ys)))
                texts = Counter(p[2] for p in cl)
                for s, n in texts.most_common(8):
                    w("      %3d x %s" % (n, s[:60]))

    out = a.out or (a.dxf.rsplit(".", 1)[0] + "_floors.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # 控制台摘要：只回显各簇楼层行
    print("报告: %s" % out)
    for ln in lines:
        if "n=" in ln and (ln.startswith("  ") or ln.startswith("关键词")):
            print(ln)


if __name__ == "__main__":
    main()
