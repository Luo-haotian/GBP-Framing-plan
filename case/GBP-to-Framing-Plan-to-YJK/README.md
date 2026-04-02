# GBP -> Framing Plan -> YJK (Hong Kong)

## 项目目标

把建筑 GBP 与题目要求转化为可审阅、可追溯、可导入 YJK 的结构设计流程，分三步完成：

1. `01_GBP_Interpretation`
2. `02_Framing_Plan`
3. `03_YJK_Interface`

每一步都必须可独立审阅，不通过门槛不进入下一步。

## 代码与依据

本项目优先使用本地 `HK Code` 文件夹中的规范（若存在）：

- `CoP_SUC2013e.pdf`
- `DIL2011e.pdf`
- `FoundationCode2017.pdf`
- `SUOS2011.pdf`
- `WindEffects2019e.pdf`
- `fs_code2011.pdf`

原则：

- 关键参数必须可追溯到 `brief / drawing / code`。
- 不能只做几何布置，必须包含计算支撑。
- 若信息缺失，允许工程假定，但要显式标注。

## 三里程碑输出要求

## 1) `01_GBP_Interpretation`

目标：只保留“与结构有关、与要求有关”的信息。

最少输出：

- `M01_constraints.json`
- `M01_geometry.json`
- `M01_traceability.md`
- `M01_risks.md`

关键检查：

- 建筑外轮廓与轴网是否闭合、自洽；
- 核心筒、长跨区、停车约束区是否识别清楚；
- 题目硬约束是否全部入库（50车位、2.5x5.0、车道宽、转弯半径、450结构深度、内柱线限制等）。

## 2) `02_Framing_Plan`

目标：形成可用初步结构方案并附带可追溯简算。

最少输出：

- `M02_framing_*.dxf`
- `M02_member_schedule.csv`
- `M02_prelim_calc.csv`
- `M02_calc_notes.md`
- `M02_design_narrative.md`

关键检查：

- 竖向受力路径完整；
- 抗侧体系清晰（核心筒 + 必要翼墙/边墙）；
- 至少覆盖重力与水平工况的初步计算；
- 梁深不得超过 450mm；
- 停车与结构不冲突。

## 3) `03_YJK_Interface`

目标：一键进入 YJK 前的接口落地与自检。

最少输出：

- `M03_framing.json`
- `M03_yjk_import.dxf`
- `M03_import_checklist.md`

关键检查：

- 节点、梁、柱、墙拓扑一致；
- 图层映射符合 YJK 预处理规则；
- 与 `M02` 构件布置和假定一致。

## 当前开发策略（重要）

- 当前稳定路线：`DXF -> YJK`。
- `AIstructure JSON 导入` 暂时暂停（示例文件阶段性不可稳定导入）。
- 后续将以更高等级接口方案重启 JSON 方向（保留逻辑层 JSON，不影响当前 DXF 成果）。

## 识别策略（强制互证）

读取图纸/要求时，必须至少两条路径交叉验证：

1. PDF 文本和矢量几何提取（优先）  
2. OCR（如 Tesseract）兜底  

若两者冲突，先输出冲突项，不得静默覆盖。

## 目录建议

建议每次迭代单独建目录，例如：

- `record/20260402/01_GBP_Interpretation`
- `record/20260402/02_Framing_Plan`
- `record/20260402/03_YJK_Interface`

这样可以审阅每一步，也方便回溯比选。
