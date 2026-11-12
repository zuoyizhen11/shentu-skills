# 构建配方与踩坑记录

全部结论都来自实际跑通/失败过的案例，不是推测。

## 1. 自由多边形：不要用 build_freeform

**症状**：生成的 pptx 用 python-pptx 能正常重开，但 PowerPoint 报
「PowerPoint could not open the file」，且没有任何细节。

**原因**：`shapes.build_freeform(start_x, start_y, scale)` 的 `start_x/start_y` 已经是
EMU 数值，若你按文档传 `Inches(6.2)` 再给 `scale=914400`，坐标会被乘第二次，
得到 1e12 量级的值，超出 OOXML 允许范围。

**正确做法**：直接写 `<a:custGeom>` 路径，坐标用「英寸 × 914400」自己换算。
现成实现见 `scripts/pptlib.py::poly()`。要点：

- `a:path` 的 `w/h` 必须等于形状 ext 的 EMU 整数；
- 每个 `a:pt` 用相对 bbox 的 EMU 整数；
- 开放折线用 `close=False` + `fill=None`，否则会连回起点；
- 曲线要平滑就在点集上加密（每 0.4–0.6in 一个点足够），比贝塞尔好控。

## 2. 中文字体：只设 font.name 会分裂

`run.font.name = "Noto Serif SC"` 只写 `<a:latin>`。中文走 `<a:ea>`，
不写就会回落到宋体/等线，标题的衬线感当场消失。

```python
rPr = run._r.get_or_add_rPr()
ea = OxmlElement("a:ea")
rPr.find(qn("a:latin")).addnext(ea)   # 必须在 latin 之后，顺序错了 PowerPoint 不认
ea.set("typeface", name)
```

**开做前查字体是否真的装了**。写了不存在的字体名不会报错，只会静默掉版。

## 3. 字距

`<a:rPr spc="240">` = 2.4pt。中文大标题 60–120，英文小字 300–430。
Captions 不加字距会糊成一团；但正文加超过 60 会读起来散。

## 4. 默认阴影

`add_shape` 出来的形状带主题阴影。必须 `shape.shadow.inherit = False`，
否则每个色块下面都有一层灰边，直接违反"禁用默认阴影"。

## 5. 渐变填充：让大色块在贴边处淡出

python-pptx 的高层 API 只有双色渐变的粗控制。要三档色标就手写 `<a:gradFill>`：

```xml
<a:gradFill rotWithShape="1">
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="F4F0E8"/></a:gs>
    <a:gs pos="15000"><a:srgbClr val="EFE9DC"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="EFE9DC"/></a:gs>
  </a:gsLst>
  <a:lin ang="0" scaled="0"/>
</a:gradFill>
```

插入位置：`spPr` 里几何之后、`a:ln` 之前。`ang=0` 是左→右。

**典型用途**：剖面/地形/大色块从画布边缘切入时，最外 15% 淡到纸色，
硬边就消失了——比加白框自然得多。

## 6. PowerPoint COM 渲染

- `Open()` 的 ReadOnly/Untitled/WithWindow 要传 **msoTriState 整数**（`-1` / `0`），
  传 `$true/$false` 会抛「无法将值转换为 MsoTriState」。
- `$app.Visible = $true` 同样要 `-1`，且很多环境不需要也不允许设。
- **含中文的路径打不开**（实测）。必须先把 pptx 复制到纯英文临时目录再 Open。
- 导出后一定要真的看图。文字压边、行距崩塌这类问题在代码里完全看不出来。

现成脚本：`scripts/export_png.ps1`。

## 7. 图片水印

AI 生成的图常在右下角带水印（`AI生成 / WORKBUDDY`）。三种处理，按优先级：

1. 裁掉：水印一般占右下 5.5% × 5.4%，裁完正好还是 16:9；
2. 用压暗渐变盖住；
3. 实在去不掉，就在页面角落标注来源，不要假装是自己的实景。

## 8. 竖排与旋转

`text_frame` 不支持竖排。做法：文本框旋转 `-90`（`shape.rotation = -90`），
再按旋转后的 bbox 反算位置。中文竖排要每字一段，别指望 word_wrap。

## 9. 尺寸自检

做完用代码核一遍再渲染，比肉眼快：

```python
for sh in slide.shapes:
    assert sh.left >= 0 and sh.top >= 0
    assert sh.left + sh.width <= prs.slide_width + 1000
    assert sh.top + sh.height <= prs.slide_height + 1000
```

但**这查不出文字溢出**——文字溢出只能看图或按「字数 × 字号」估算：
汉字宽度 ≈ 字号(pt)，4.3in 宽 ≈ 309pt ≈ 26 个 11pt 汉字。
