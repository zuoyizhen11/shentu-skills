# 审图技能合集

建筑与施工图审查场景的 Agent Skills 合集，遵循 `SKILL.md` 规范，可在 WorkBuddy、Claude Code 等支持该规范的智能体中使用。

## 技能清单

| 技能 | 用途 | 典型产出 |
|---|---|---|
| `building-review` | 建筑施工图技术审查（总图、单体、专项） | 正式格式《施工图审查意见》DOCX |
| `review-opinion-delivery` | 把已有审查意见整理为规范交付件 | 证据齐全的 Word 交付稿 |
| `drawing-review-cn` | 图纸会审（全专业自审） | 9 列问题清单 + 会审记录表 |
| `tianzheng-dwg-parse` | 天正 T20/T8、T3 DWG 解析与图面审计 | 逐层设备统计、图面审计报告 |
| `ppt-ing` | 可编辑 PPTX 制作、重设计、排版审查 | 原生对象 PPTX + 逐页渲染预览 |

## 各技能说明

### building-review

证据驱动的建筑专业施工图审查技能。核心是**不允许 AI 凭空下结论**：每条意见必须挂上图纸事实、规范原文、截图证据，并通过完整性审计才能出报告。

- 覆盖：总图、建筑单体、防火、无障碍、节能、绿建、防水、人防、幕墙、装饰等建筑归口专业
- 边界：不技术审查结构、给排水、电气、暖通图纸
- 机制：规则库展开 → 原子化核查 → 证据链闭环 → 完整性审计 → 报告生成
- 校验：内置 13 组回归测试与多重门禁脚本

### review-opinion-delivery

面向"意见已存在、只差交付"的场景。把审查人手写的意见、标注位置、截图，按交付契约整理成 Word，不改动结论。

### drawing-review-cn

图纸会审（施工前各专业碰头）技能，与 `building-review` 的"施工图审查"是不同业务阶段。

- 覆盖：建筑、结构、给排水、电气、暖通、智能化、室内装修、景观园林、海绵、基坑支护、亮化
- 工具链：DWG 文字提取、PDF 渲染与文字抽取、图像裁剪、像素比对、重复图扫描
- 产出：统一 9 列问题清单、各专业明细、会审记录表（Word / Excel）

### tianzheng-dwg-parse

把天正（T20/T8）与 T3 导出的 DWG 变成可统计、可审计的数据。链路为：DWG → `accoreconsole` 转 DXF → `ezdxf` 解析 → 逐层聚类统计。**全程只读，不改动原图。**

## 环境要求

- Python 3.11+
- `pymupdf`、`python-docx`、`ezdxf`、`openpyxl`、`pillow`
- 部分 DWG 功能需要 AutoCAD（含 `accoreconsole.exe`）与 PowerShell 7

```bash
pip install pymupdf python-docx ezdxf openpyxl pillow
```

## 目录约定

每个技能目录结构一致：

```
<skill>/
├── SKILL.md          # 技能定义与工作流
├── references/       # 规则、格式、边界说明
├── scripts/          # 可执行脚本
└── evals/            # 回归测试用例（部分技能提供）
```

## 许可证

各技能分别遵循其原始许可证。除 `ppt-ing` 外均为 MIT：

| 技能 | 版权 |
|---|---|
| `building-review`、`review-opinion-delivery` | Copyright (c) 2026 kangmaojian |
| `drawing-review-cn` | Copyright (c) 2025 drawing-review-cn contributors |
| `tianzheng-dwg-parse` | Copyright (c) 2026 hwdemtv |
| `ppt-ing` | 移植版，**混合授权**：代码部分 MIT；规范文本源自上游，不随本仓授权，见 `ppt-ing/NOTICE.md` |

各技能目录下的 `LICENSE` 文件为对应原始许可证全文。
