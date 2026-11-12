# -*- coding: utf-8 -*-
"""
pptlib - native object toolkit for PPT-ING (WorkBuddy port)

python-pptx 在中文排版、字距、渐变、自由多边形上有几个坑，
这里一次性封装掉，避免每次重建时重新踩。

Usage:
    import sys; sys.path.insert(0, r"E:\\.workbuddy\\skills\\ppt-ing\\scripts")
    from pptlib import *
    prs = new_deck()
    s = prs.slides.add_slide(blank_layout(prs))
    txt(s, 0.95, 1.2, 6, 0.8, "山谷美术馆", size=72, spc=120)
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement

EMU = 914400

# ---- 常用色（宣纸/墨/矿物，TP-ORIENTAL-EDITORIAL） -------------------------
INK      = RGBColor(0x1C, 0x1C, 0x1A)
PAPER    = RGBColor(0xF4, 0xF0, 0xE8)
EARTH    = RGBColor(0xEF, 0xE9, 0xDC)
RULE     = RGBColor(0xDE, 0xD7, 0xC8)
MUTED    = RGBColor(0x8B, 0x83, 0x77)
BODY     = RGBColor(0x33, 0x32, 0x2E)
OCHRE    = RGBColor(0x96, 0x71, 0x4A)

SERIF = "Noto Serif SC"   # 本机已装；换机前先确认，否则掉字体
SANS  = "Noto Sans SC"


def hexc(s):
    s = s.strip().lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


# ---- 字体 -----------------------------------------------------------------
def _set_fonts(run, name):
    """python-pptx 的 font.name 只写 latin，中文会回落到默认字体。
    必须同时写 a:ea，否则 PPT 里中文和英文是两套字形。"""
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    latin = rPr.find(qn("a:latin"))
    if rPr.find(qn("a:ea")) is None:
        ea = OxmlElement("a:ea")
        if latin is not None:
            latin.addnext(ea)
        else:
            rPr.append(ea)
        ea.set("typeface", name)


def txt(slide, x, y, w, h, content, font=SERIF, size=12, color=INK, spc=0,
        align=PP_ALIGN.LEFT, ls=None, anchor=MSO_ANCHOR.TOP, wrap=False,
        bold=False, italic=False):
    """content 里的 \\n 拆成段落。spc 单位 1/100 pt（240 = 2.4pt 字距）。"""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    tf.vertical_anchor = anchor
    tf.auto_size = None
    for i, line in enumerate(content.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if ls:
            p.line_spacing = ls
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        _set_fonts(r, font)
        if spc:
            r._r.get_or_add_rPr().set("spc", str(int(spc)))
    return box


# ---- 基本形 ---------------------------------------------------------------
def _finish(s, fill, line, lw):
    s.shadow.inherit = False          # 不关掉会带 PowerPoint 默认阴影
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    s.text_frame.word_wrap = False
    return s


def rect(slide, x, y, w, h, fill=None, line=None, lw=0.75):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    return _finish(s, fill, line, lw)


def hline(slide, x1, y, x2, color=RULE, lw=0.5, dash=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y), Inches(x2), Inches(y))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    if dash:
        c.line.dash_style = dash
    return c


def vline(slide, x, y1, y2, color=RULE, lw=0.5, dash=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    if dash:
        c.line.dash_style = dash
    return c


def poly(slide, pts, fill=None, line=None, lw=1.0, close=True):
    """自由多边形，坐标单位=英寸。

    注意：不要用 pptx 自带的 build_freeform(scale=...)。
    它的 start_x/start_y 已经是 EMU，再乘 scale 会溢出成 1e12 级坐标，
    PowerPoint 直接报 "could not open the file"，且 python-pptx 重开不报错。
    这里直接写 custGeom 路径，绝对可控。
    """
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    w, h = max(xs) - x0, max(ys) - y0
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x0), Inches(y0), Inches(w), Inches(h))
    s.shadow.inherit = False
    spPr = s._element.spPr
    prst = spPr.find(qn("a:prstGeom"))
    idx = list(spPr).index(prst)
    spPr.remove(prst)

    cx, cy = int(round(w * EMU)), int(round(h * EMU))
    cg = OxmlElement("a:custGeom")
    for tag in ("a:avLst", "a:gdLst", "a:ahLst", "a:cxnLst"):
        cg.append(OxmlElement(tag))
    rc = OxmlElement("a:rect")
    for k, v in (("l", "0"), ("t", "0"), ("r", "r"), ("b", "b")):
        rc.set(k, v)
    cg.append(rc)

    plst = OxmlElement("a:pathLst")
    path = OxmlElement("a:path")
    path.set("w", str(cx))
    path.set("h", str(cy))

    def _pt(p):
        e = OxmlElement("a:pt")
        e.set("x", str(int(round((p[0] - x0) * EMU))))
        e.set("y", str(int(round((p[1] - y0) * EMU))))
        return e

    mv = OxmlElement("a:moveTo")
    mv.append(_pt(pts[0]))
    path.append(mv)
    for p in pts[1:]:
        ln = OxmlElement("a:lnTo")
        ln.append(_pt(p))
        path.append(ln)
    if close:
        path.append(OxmlElement("a:close"))
    plst.append(path)
    cg.append(plst)
    spPr.insert(idx, cg)

    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    s.text_frame.word_wrap = False
    return s


def grad_x(shape, stops, ang=0):
    """水平线性渐变。stops = [(pos0_1000, (r,g,b)), ...]
    用途之一：让大色块在贴边处淡入纸色，消掉裁切硬边。"""
    spPr = shape._element.spPr
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:grpFill"):
        e = spPr.find(qn(tag))
        if e is not None:
            spPr.remove(e)
    gf = OxmlElement("a:gradFill")
    gf.set("rotWithShape", "1")
    lst = OxmlElement("a:gsLst")
    for pos, col in stops:
        gs = OxmlElement("a:gs")
        gs.set("pos", str(int(pos)))
        clr = OxmlElement("a:srgbClr")
        clr.set("val", "%02X%02X%02X" % (col[0], col[1], col[2]))
        gs.append(clr)
        lst.append(gs)
    gf.append(lst)
    ln = OxmlElement("a:lin")
    ln.set("ang", str(int(ang)))
    ln.set("scaled", "0")
    gf.append(ln)
    anchor = spPr.find(qn("a:ln"))
    if anchor is not None:
        anchor.addprevious(gf)
    else:
        spPr.append(gf)


def picture_fill(slide, path, x, y, w, h, crop=None):
    """铺满指定框并按比例裁切（crop 可显式传 l,r,t,b 比例）。"""
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    if crop:
        pic.crop_left, pic.crop_right, pic.crop_top, pic.crop_bottom = crop
    return pic


# ---- 文档 -----------------------------------------------------------------
def new_deck(w=13.3333, h=7.5):
    prs = Presentation()
    prs.slide_width = Inches(w)
    prs.slide_height = Inches(h)
    return prs


def blank_layout(prs):
    return prs.slide_layouts[6]


def save(prs, path):
    prs.save(path)
    return path
