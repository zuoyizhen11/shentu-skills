# 天正 DWG 图纸解析 · Tianzheng DWG Parse

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20WorkBuddy-lightgrey)](#环境要求)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](#环境要求)
[![AutoCAD](https://img.shields.io/badge/Tool-AutoCAD%20accoreconsole-orange)](#环境要求)

**A WorkBuddy agent skill for parsing Tianzheng (T20/T8) and T3-exported DWG construction drawings — read-only surveying, per-floor device counts, and drawing auditing via `accoreconsole` + `ezdxf`.**

一个 [WorkBuddy](https://www.workbuddy.cn) 智能体技能：把天正（T20/T8）与 T3 导出的 DWG 施工图变成**可统计、可审计、可比对**的数据。链路：**天正 T3 导出 → accoreconsole `_.DXFOUT`(R2018) → ezdxf 解析 → 逐层聚类统计**。全程只读，不改动原图。

## 特性 / Features

- **判格式先行**：读 DWG 文件头（`AC1018` = T3/2004，`AC1021+` = T20 2007+），据此判断是否该请设计方转 T3，而不是盲目开图
- **全图普查**：实体类型统计、天正代理对象按图层分布、图层清单（定义数 / 实际使用数双口径）、顶层块引用 TOP N、按图层文字清单、关键词命中明细
- **逐层统计（y 聚类）**：多张图框在模型空间竖列堆叠时，靠实体 y 值相邻差自动切层，无需硬编码窗户坐标；`--xband` 限定竖列排除图例区干扰，`--labels` 用已知楼层反查校验
- **块名 → 图例名称映射**：天正设备块 = 符号图形 + ATTDEF，**设备名藏在 `tag=A` 的默认值里**；块名 `$equip_U$00000240(WIN-3PDLNMTE0GS)` 括号内容无语义，同 handle 前缀还可能有多个不同设备变体
- **计数防坑三律**：杜绝"递归父块展开 + 窗口中心收录"两头收导致的双重计数（实测同一对象真值 77 被数成 208）
- **审计报告框架**：问题按四级分类（图纸内部矛盾 / 图面缺漏 / 制图错误 / 图纸-清单矛盾），每条附图纸原文证据

## 实测数据（真实项目：某科研设计中心弱电施工图 15 张）

| 指标 | 数值 |
|---|---|
| 原图（天正 T20） | 10.6 MB |
| T3 导出后 | 8.66 MB（`AC1018` / 2004 格式） |
| 转 R2018 DXF | 99.7 MB，耗时 1~3 min |
| 模型空间实体 | 18,609 |
| 天正代理对象 | 4,552（集中在建筑图层，不影响弱电统计） |
| 图层 | 定义 150 个 / 实际使用 76 个 |
| 顶层块引用 | 5,088 |
| 无线 AP 逐层核查 | 9 层共 84 点（7/11/9/9/9/11/11/7/10），与逐点文字标注三重吻合 |
| ONU 支架 | 77 处逐点标注，与块插入点聚类一致 |

## 环境要求

- **Windows** + 已安装 AutoCAD（含 `accoreconsole.exe`；2022~2024 常见路径已内置自动探测，也可用 `--acad` 显式指定）
- **Python 3.10+** + `ezdxf`（脚本仅依赖标准库与 ezdxf；注意 ezdxf 装在哪个解释器里需先探测）
- **可选**：天正软件（用于把 T20 原图导出为 T3 格式）

## 快速开始 / Quick Start

### 1. 安装技能（三选一）

**方式 A · 一行命令安装（推荐）**

Windows（PowerShell）：

```powershell
irm https://raw.githubusercontent.com/hwdemtv/tianzheng-dwg-parse/main/install.ps1 | iex
```

macOS / Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/hwdemtv/tianzheng-dwg-parse/main/install.sh | bash
```

**方式 B · 直接把仓库地址丢给 WorkBuddy**

在 WorkBuddy 对话中发送：

> 安装技能：https://github.com/hwdemtv/tianzheng-dwg-parse

**方式 C · 手动复制**

把本仓库的 `SKILL.md`、`references/`、`scripts/` 复制到 `~/.workbuddy/skills/tianzheng-dwg-parse/`（Windows 为 `%USERPROFILE%\.workbuddy\skills\tianzheng-dwg-parse\`）。

### 2. 五步工作流

```bash
# ① 判格式：读 DWG 头 6 字节，AC1018=T3 / AC1021+=T20
# ② DWG → R2018 DXF（先 --dry-run 看生成的 SCR 是否正确）
python scripts/dxfout.py 图纸.dwg -o 图纸.dxf --dry-run
python scripts/dxfout.py 图纸.dwg -o 图纸.dxf

# ③ 全图普查：定位图层/图例/楼层块名/设备块名
python scripts/tz_survey.py 图纸.dxf -o survey.txt --keywords 无线AP,ONU,支架,光分路器,配线架,机柜

# ④ 逐层统计：按块名片段聚类计数 + 属性分布
python scripts/tz_floors.py 图纸.dxf --block 00000240 --xband 300000,470000 --gap 40000 -o ap.txt

# ⑤ 文字口径复核（设备本体是代理时的可靠替代）
python scripts/tz_floors.py 图纸.dxf --text 支架 --xband 300000,470000 --gap 40000 \
    --labels "3F=182111-215070,24F=331350-372621" -o onu.txt
```

**两遍定位法**：先不带 `--labels` 跑一遍，从报告抄下各簇 y 范围；再回填成 `--labels` 跑第二遍，即得带楼层名的成品统计表。

### 3. 出报告

每个数字落到证据文件（`*.txt`）并在报告中注明来源；**块插入聚类数、顶层文字计数、图例数三方交叉验证一致**后才写入结论。

## FAQ

**Q: 必须让设计院把图转成 T3 吗？**
不必须，但强烈建议。T3 的价值：楼层块名（`3F`/`35F`…）、`CATALOG` 图纸目录、房间名、弱电逐点标注文字全部可读；设备本体多数仍是代理对象，但**不影响工程量统计与图面审计**。

**Q: ezdxf 能直接读 DWG 吗？**
不能，任何版本的 DWG 二进制都报 `OSError: is not a DXF file`，必须先经 accoreconsole 转 DXF。

**Q: 为什么不用 `-EXPORTTOAUTOCAD` 把天正代理对象彻底炸开？**
实测对 10MB 级天正图 >5 分钟无产出，性价比极低，本技能放弃该路线。

**Q: 统计数字怎么保证不是错的？**
靠"计数三律"（不许两头收、以块定义解剖+插入点聚类为金标准、三方交叉验证）+ 逐点文字计数复核；真实项目中曾纠正过 208 vs 77 的双重计数错误。

**Q: 会改动我的图纸吗？**
不会。本技能全链路只读。需要往图纸写标记、写回 DWG 或批量出图 PDF，请用姊妹技能 [`autocad-dwg-headless`](https://github.com/hwdemtv/dwg-block-compare)。

## 目录结构

```
tianzheng-dwg-parse/
├── SKILL.md                  # 技能清单（5 步工作流 + 4 条核心规则）
├── references/
│   └── pitfalls.md           # 详解：DXFOUT 序列、计数三律、块名变体表、rot270 提取、环境坑表、审计框架
├── scripts/
│   ├── dxfout.py             # DWG → R2018 DXF（accoreconsole _.DXFOUT 包装，支持 --dry-run）
│   ├── tz_survey.py          # 全图普查（实体/代理/图层/块引用/文字/关键词）
│   └── tz_floors.py          # 逐层统计（y 聚类计数 + 属性分布 + 关键词文字）
├── install.ps1               # Windows 一行安装
└── install.sh                # macOS / Linux 一行安装
```

## 关键词

`天正` `T20` `T3` `DWG` `DXF` `ezdxf` `accoreconsole` `AutoCAD` `弱电` `智能化` `工程量统计` `施工图审核` `设备点位` `drawing audit` `quantity takeoff` `agent skill` `WorkBuddy`

## License

[MIT](LICENSE)
