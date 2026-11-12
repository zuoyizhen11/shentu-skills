# -*- coding: utf-8 -*-
"""
示例：境象建筑 / 山谷美术馆 · 2 页概念提案
演示 ppt-ing(WorkBuddy 版) 的完整链路：
    new_deck -> 原生文字/形/剖面 -> save -> export_png -> 看图复核
所有文字与图形均为可编辑原生对象，无整页贴图。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))

from pptlib import (new_deck, blank_layout, txt, rect, hline, poly, grad_x,
                    picture_fill, save, INK, PAPER, EARTH, RULE, MUTED,
                    BODY, OCHRE, SERIF, SANS, RGBColor, PP_ALIGN, MSO_ANCHOR,
                    MSO_LINE_DASH_STYLE)

W, H = 13.3333, 7.5
COVER_TXT = RGBColor(0xF3, 0xEE, 0xE4)
COVER_MUT = RGBColor(0x9C, 0x95, 0x8A)
COVER_DIM = RGBColor(0x6E, 0x69, 0x60)

prs = new_deck(W, H)
blank = blank_layout(prs)

# ---------------------------------------------------------------- P1 封面
s1 = prs.slides.add_slide(blank)
picture_fill(s1, os.path.join(HERE, "cover.jpg"), 0, 0, W, H)

hline(s1, 0.95, 1.02, 1.62, RGBColor(0x8E, 0x88, 0x7C), 0.75)
txt(s1, 0.95, 1.13, 6.2, 0.22, "境象建筑 / JINGXIANG ARCHITECTS",
    font=SANS, size=8, color=COVER_MUT, spc=250)
txt(s1, 0.95, 1.90, 6.4, 1.15, "山谷美术馆", size=72, color=COVER_TXT, spc=120)
txt(s1, 0.95, 3.10, 6.0, 0.22, "VALLEY ART MUSEUM",
    font=SANS, size=8.5, color=COVER_MUT, spc=430)
hline(s1, 0.95, 3.52, 2.35, RGBColor(0x6F, 0x6A, 0x60), 0.5)
txt(s1, 0.95, 3.80, 4.05, 1.0, "建筑不立于地形之上。\n它成为地形的一部分。",
    size=16.5, color=RGBColor(0xDE, 0xD7, 0xC8), ls=1.75, wrap=True)
txt(s1, 0.95, 6.42, 6.4, 0.2, "中国 · 皖南　　2026　　4,200 ㎡",
    font=SANS, size=8, color=COVER_MUT, spc=110)
hline(s1, 0.95, 6.72, 12.38, RGBColor(0x50, 0x4C, 0x44), 0.5)
txt(s1, 8.60, 6.91, 3.78, 0.2, "概念提案 · 虚构项目 · AI 概念图",
    font=SANS, size=7, color=COVER_DIM, spc=40, align=PP_ALIGN.RIGHT)

# ---------------------------------------------------------------- P2 概念
s2 = prs.slides.add_slide(blank)
rect(s2, 0, 0, W, H, fill=PAPER)

GROUND = [(6.16, 2.10), (6.85, 2.55), (7.55, 3.05), (8.25, 3.55),
          (8.85, 4.05), (9.25, 4.35), (9.85, 4.35), (10.35, 4.05),
          (10.95, 3.55), (11.65, 3.05), (12.40, 2.52), (13.34, 1.95)]
earth = poly(s2, GROUND + [(13.34, 7.5), (6.16, 7.5)], fill=EARTH, close=True)
grad_x(earth, [(0, (0xF4, 0xF0, 0xE8)), (15000, (0xEF, 0xE9, 0xDC)),
               (100000, (0xEF, 0xE9, 0xDC))])
poly(s2, [(p[0], p[1] + 0.17) for p in GROUND], line=RGBColor(0xD8, 0xCF, 0xBB),
     lw=0.5, close=False)
poly(s2, GROUND, line=RGBColor(0x3A, 0x3A, 0x34), lw=1.1, close=False)
hline(s2, 9.50, 1.55, 9.50, RGBColor(0xD2, 0xCA, 0xB8), 0.5, MSO_LINE_DASH_STYLE.DASH)

rect(s2, 8.83, 4.49, 1.34, 1.37, fill=INK)      # 沉入谷底的体块（剖切）
rect(s2, 8.48, 4.34, 2.04, 0.15, fill=INK)      # 屋顶板
rect(s2, 9.00, 4.49, 1.00, 0.055, fill=PAPER)   # 采光缝
rect(s2, 9.97, 5.20, 0.20, 0.30, fill=PAPER)    # 框景洞口

txt(s2, 8.85, 5.92, 0.4, 0.2, "01", font=SANS, size=7.5, color=OCHRE, spc=120)
txt(s2, 8.50, 4.08, 0.4, 0.2, "02", font=SANS, size=7.5, color=OCHRE, spc=120)
txt(s2, 10.26, 5.23, 0.4, 0.2, "03", font=SANS, size=7.5, color=OCHRE, spc=120)
txt(s2, 10.60, 7.06, 2.00, 0.2, "纵剖面 · 示意", font=SANS, size=7,
    color=MUTED, spc=40, align=PP_ALIGN.RIGHT)

txt(s2, 0.95, 0.62, 3.0, 0.2, "02 — 概念", font=SANS, size=8, color=MUTED, spc=220)
hline(s2, 0.95, 0.98, 12.38, RULE, 0.5)
txt(s2, 0.95, 1.10, 5.2, 0.75, "只做三个动作", size=40, color=INK, spc=60)
txt(s2, 0.95, 2.00, 4.6, 0.24, "其余交给地形、光线和时间。",
    font=SANS, size=11.5, color=RGBColor(0x6B, 0x65, 0x5C), spc=40)

rows = [
    ("01", "下沉", "展厅退到谷底，屋面交还给步道。", "覆土屋面 / 侧高窗 / 展厅净高 6.4m"),
    ("02", "折", "一条坡道折三次，从谷口走到屋面。", "坡道兼作结构 / 全长 210m / 坡度 1:12"),
    ("03", "借", "只开三个洞：远山、谷雾、树冠。", "三个框景洞口 / 东南向 / 无人工照明"),
]
y0 = 2.94
for num, word, line, meta in rows:
    hline(s2, 0.95, y0 - 0.14, 4.30, RULE, 0.5)
    txt(s2, 0.95, y0, 0.6, 0.18, num, font=SANS, size=8, color=OCHRE, spc=200)
    txt(s2, 0.95, y0 + 0.10, 3.0, 0.45, word, size=23, color=INK, spc=140)
    txt(s2, 0.95, y0 + 0.60, 4.3, 0.24, line, font=SANS, size=11, color=BODY, spc=30)
    txt(s2, 0.95, y0 + 0.88, 4.3, 0.2, meta, font=SANS, size=7.5, color=MUTED, spc=50)
    y0 += 1.36

txt(s2, 0.95, 7.08, 6.0, 0.2, "境象建筑 · 山谷美术馆 · 概念提案 v1.0",
    font=SANS, size=7, color=MUTED, spc=40)

prs.core_properties.title = "山谷美术馆 / Valley Art Museum — 概念提案"
prs.core_properties.author = "境象建筑 JINGXIANG ARCHITECTS"
save(prs, os.path.join(HERE, "out", "山谷美术馆_概念提案_v1.0.pptx"))
print("saved")
