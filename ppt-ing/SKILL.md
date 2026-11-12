---
name: ppt-ing
description: 只在「可编辑原生 PPTX 的精细排版、视觉重设计、排版审查」时使用：坐标级控制、版式与字体契约、真实 PowerPoint 渲染 QA。触发词：重设计这份PPT、按提案级标准排版、审查PPT排版、可编辑PPTX、坐标级精修、提案deck。常规生成 PPT 请改用 workbuddy-pptx。
agent_created: true
---

# PPT-ING · WorkBuddy 版

`github.com/cchhm8888-ctrl/ppt-ing` v5 的移植版。**上游是 Codex Skill，依赖一个这里没有的 MCP；
本版把执行层换成 python-pptx + PowerPoint COM，设计契约原样保留。**

## 分工边界（先看这里）

同一台机器上还有 `workbuddy-pptx`、`ppt-two-step`、`guizang-ppt-skill`、`frontend-slides`。
**默认不要抢活：**

| 用户要什么 | 走哪个 |
|---|---|
| 常规做一份 PPT，内容为主 | `workbuddy-pptx` |
| 先理清说服逻辑再动手 | `ppt-two-step`（它最终会调 `workbuddy-pptx`） |
| 网页演示、横向翻页、要动效 | `guizang-ppt-skill` / `frontend-slides` |
| **已有版式要重设计、要坐标级精修、要审排版、要提案级视觉** | 本技能 |

判断口诀：**用户只要"一份 PPT"→ 让别人做；用户对"长什么样/能不能改"有具体要求 → 我来。**
拿不准就问一句，不要直接开工。

先明确一件事，别自我欺骗：
- 上游的 `presentations:Presentations` 能力这里没有 → 用 `scripts/pptlib.py` 手写原生对象替代。
- 上游的 `figedit`（整页图分解）这里没有 → **C 路径不可用**，只能用 A / B。
- 上游的 Pinterest 研究这里没有 → 用 `WebSearch` 或直接问用户要 1 个参考。
- 「通过 PowerPoint 渲染 QA」这句可以真说，因为 `scripts/export_png.ps1` 是真的调 PowerPoint。

## 路由

| 路线 | 触发 | 行为 |
|---|---|---|
| `proposal-first` | 新建、重设计、多页视觉改动 | 一次问清 → 出完整方案 → 等确认 → 制作 → 渲染 QA |
| `direct` | 用户明确说「直接做/别问了/赶时间」 | 内部推断全部参数，直接做，只在缺事实/缺文件时打断 |
| `lightweight` | 改错别字、改数字、导出、局部微调 | 跳过 intake 与方案，只动指定范围 |

「赶时间」不等于 `direct`，除非用户说别问。

## 一次问清（只用一轮）

八项，缺的用推荐值并在交付时**写明这是假设**。用户回「全部推荐」就全用默认。

1. 目标 / 场景 / 受众
2. 源内容、事实、已有文件
3. 页数 / 比例 / 语言 / 目标 PowerPoint 版本
4. 文案类型 / 语气 / 密度
5. 视觉语言：`商务克制` `编辑式平衡（默认）` `高表现艺术化`
6. 配色方向、品牌色、禁用色
7. 版式倾向、图数据比例
8. 动效：`A 静态` `B 克制讲述（默认）` `C 叙事 Morph` `D 背景视频`

附一行附件说明，不要当第九问：最多 1 个 pptx/potx、5 个图片/PDF/链接、1 个品牌包。
**未声明的模板只当风格参考，不继承母版。**

## 方案门（硬闸）

用户确认方案前，不要生成任何 pptx、不要出预览图。方案必须包含：
文案与叙事 / 视觉语言与模板包 / 配色与比例 / 页角色表与版式家族 / 组件与形状系统 /
动效配置 / 素材策略 / 字体六角色与预设 / 可编辑性边界。
**加一张完整逐页表。** 改方案只改方案，不重新问 intake。

12 页以上的文档语法：`封面 → 目录 → 分章 → 内容 → 总结 → 收尾`；
15 页以上至少 8 个不同 `layout_variant_id`（差在构图几何，不是换图换色）。

## 设计契约（不可协商的部分）

- 默认强度 D3–D4（编辑式平衡）。
- 10 页以上 5–7 个版式家族；同一家族不连续超过 3 页；完全相同的构图不连续超过 2 页。
- 卡片式页面 ≤35%；重复的标题几何 ≤40%。
- 字体六角色：`Display / Section / Title / Body / Caption / Numeral`。
- 每页最多一个主效果 + 一个辅助效果；正文与数据标签禁用粗描边、3D、全篇发光、艺术字。
- 形状必须能做到以下之一：聚焦、承载文案、组织信息、表达关系、制造节奏。
  **空白线、空环、胶囊、纯装饰框、阴影、光晕，一律判不合格。**
- 图片是独立素材；文字、数据、图表、遮罩、标签、语义形状必须是原生可编辑对象。
- 用户批准过的构图（`design_commitments`）不得擅自简化成卡片、等分栏或"标题左图右"。

详见 `references/design-system.md`。

## 制作

```python
import sys; sys.path.insert(0, r"E:\.workbuddy\skills\ppt-ing\scripts")
from pptlib import *
prs = new_deck()                      # 13.3333 x 7.5 in
s = prs.slides.add_slide(blank_layout(prs))
txt(s, 0.95, 1.10, 5.2, 0.75, "只做三个动作", size=40, spc=60)
```

**开做前先查字体**（`ls /c/Windows/Fonts | grep -iE "noto|simsun|msyh|deng"`），
写一个本机不存在的字体名 = 交付即掉版。

坐标系单位一律英寸。四边出血、基线对齐、光标尺寸都要落到小数第二位，不要用 `center` 蒙。

坑与配方见 `references/build-recipes.md`（自由多边形、中文字体、字距、渐变、阴影）。

## 渲染 QA（硬闸）

```powershell
powershell -ExecutionPolicy Bypass -File scripts\export_png.ps1 `
  -Pptx "D:\out\deck.pptx" -OutDir "D:\out\preview"
```

然后**逐页看图**，不是看代码。以下任一条即判失败，回去改对象再渲染：

- 缺页角色、版式家族、字体预设或视觉锚点；
- 承诺过的构图特征或预期对象不存在；
- 标题几何雷同、层级平庸；
- 渲染结果与批准的方案/参考不一致；
- 主体被裁、文字压到不安全区、遮罩挡住语义；
- 用整页截图代替可编辑结构；
- 无意义装饰、重复卡片、过量阴影/发光、假 Morph；
- 中文变成方块或回落到默认字体。

最终预览必须来自**交付的那一版 pptx**，不能是上一版。

## 已知限制（说清楚，别装）

- 没有 `presentations` MCP：复杂图表（原生 chart）只能走 python-pptx 的 `add_chart`，样式控制弱于上游；数据可视化优先用形状手绘 + 数字排版。
- 没有 `figedit`：整页参考图分解不可用。要复刻某张截图，只能人工量取坐标。
- 没有 Pinterest：视觉研究退化为 WebSearch + 用户直接给参考。
- 渲染 QA 依赖本机装了 PowerPoint（COM）。没装就如实说明只能做静态自查，**不许声称已通过动画 QA**。
- 动效：python-pptx 只支持基础 timing 注入，Morph 需要手写 `p:timing`。默认交付静态 + 建议动效参数，不默认写动画。

## 文件

- `scripts/pptlib.py` — 原生对象工具库（文字/形/自由多边形/渐变/图片填充）
- `scripts/export_png.ps1` — PowerPoint COM 导出逐页 PNG
- `references/design-system.md` — 字体角色、字体预设、颜色、栅格、动效时标
- `references/build-recipes.md` — python-pptx 实操配方与踩坑记录
- `references/qa-checklist.md` — 交付前逐项核对
- `examples/valley-art-museum/` — 2 页建筑概念提案，可直接跑通全链路
