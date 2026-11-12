# PPT-ING · WorkBuddy 版

把 [`cchhm8888-ctrl/ppt-ing`](https://github.com/cchhm8888-ctrl/ppt-ing)（Codex Skill v5）
移植成 WorkBuddy 能真正执行的形态。

## 为什么要移植，而不是直接装

上游依赖三样这台机器没有的东西：

| 上游依赖 | 这里的情况 |
|---|---|
| `presentations:Presentations` MCP（生成原生 PPTX 对象） | 没有 |
| `figedit`（整页参考图分解） | 没有 |
| Codex CLI 的 `.codex/skills` 加载路径 | 没有 |

上游仓库里 **0 个 .pptx / .potx**，只有文字规范 + JSON Schema + 审查脚本。
所以原样装进去，得到的是一份"读得懂但跑不起来"的文档。

本版做的事是**换执行层**：

| 层 | 上游 | 本版 |
|---|---|---|
| 生成 | presentations MCP | `scripts/pptlib.py` 直接写 OOXML |
| 渲染 QA | 真 PowerPoint | `scripts/export_png.ps1` 调 PowerPoint COM（已实测可用） |
| 概念图 | imagegen | WorkBuddy 的 ImageGen |
| 视觉研究 | Pinterest | WebSearch / 用户给参考 |

设计契约（提案门、版式家族、字体六角色、动效时标、QA 硬门槛）**原样保留**。

## 安装

```
E:\.workbuddy\skills\ppt-ing\
├─ SKILL.md
├─ references\
│  ├─ design-system.md
│  ├─ build-recipes.md
│  └─ qa-checklist.md
├─ scripts\
│  ├─ pptlib.py
│  └─ export_png.ps1
└─ examples\valley-art-museum\
   ├─ build_deck.py
   └─ cover.jpg
```

装完**必须开新会话**才会被发现。

## 跑通验证

```bash
cd "E:\.workbuddy\skills\ppt-ing\examples\valley-art-museum"
python build_deck.py
powershell -ExecutionPolicy Bypass -File "..\..\scripts\export_png.ps1" `
  -Pptx "out\山谷美术馆_概念提案_v1.0.pptx" -OutDir "out\preview"
```

出来 2 页：封面（建筑即地形）+ 概念页（三条策略 + 原生剖面图）。
全部文字与图形可双击编辑。

## 环境要求

- Python + `python-pptx`（实测 1.0.2）
- 本机安装 PowerPoint（渲染 QA 用；没有就降级，不许假装查过）
- 字体：`Noto Serif SC` / `Noto Sans SC`。换机前先确认，否则掉版

## 已知限制

- 原生图表（`add_chart`）样式控制弱，数据可视化建议形状手绘 + 数字排版
- Morph 动效需要手写 `p:timing`，默认交付静态
- 无整页参考图分解能力，复刻截图只能人工量坐标

## 来源与授权

设计规范、流程契约来自上游仓库。**上游未声明开源许可证**，
按默认版权规则视为「保留所有权利」。因此：

- 本移植版**不声明任何许可证**；
- 若要公开分发，请先取得原作者授权，或仅作个人使用；
- 保留本文件与 SKILL.md 中的来源说明，不要抹掉出处。
