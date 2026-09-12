# 生成来源

本技能由 researcher 角色的工作流需求整理而成，方法论来自仓库共享技能池中的其他技能：

- `research-methodology` 技能及其参考资料（来源评估、结构化分析技术、综合模式、技术验证）
- `artifact-pyramids` 技能（渐进披露的三层产物结构与 `SOURCES` 导航）
- `orchestration-methodology` 技能（编排者如何分配研究简报、如何接收研究结论）

## 工具依赖

本技能**不依赖任何外部私有工具**：默认使用 Hermes 原生研究工具（`web_search`、`web_extract`、browser）。
`groktocrawl` 是可选的增强路径，仅在 `command -v groktocrawl` 确认可用且任务需要其独有能力时启用。
完整选择表见 `references/tool-governance.md`。

## 结构说明

Hermes 只索引名为 `SKILL.md` 的文件，且 `skill_view` 不支持 `父/子` 形式的技能名。
因此五个阶段以 `references/<phase>.md` 交付，通过
`skill_view('researcher-workflow', file_path='references/<phase>.md')` 加载，
而不是作为独立「子技能」按名字加载。
