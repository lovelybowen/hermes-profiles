# 委派上下文模板：产物金字塔要求

通过 `delegate_task` 向子 Agent 委派研究时，子 Agent 不会加载任何技能。必须在 `context` 字符串中明确包含目录结构、SOURCES 要求和输出格式。本模板提供应加入的准确文本。

## 最小模板

将下方区块原样复制到每个研究委派上下文中：

```
OUTPUT FORMAT: You MUST produce a compliant Artifact Pyramid, not flat files.

Create this directory structure at <your-output-path>/:
├── 00-index.md              ← entry point (mandatory)
├── 01-summary/findings.md   ← L1: one findings file
├── 02-analysis/             ← L2: one file per dimension/opportunity
└── 03-dossiers/             ← L3: raw scrape outputs, search results

Every file MUST end with a ## SOURCES section linking to deeper layers:
- L1 files link to L2 analysis files
- L2 files link to L3 dossiers
- Each SOURCES entry includes a description answering: "what will I find if I go deeper?"

When the output directory doesn't exist yet, create it with the full pyramid structure before writing any files.

Respond with ONLY the absolute path to the completed pyramid's 00-index.md.
Do NOT respond with natural language summaries or prose.
```

## 扩展模板（包含理由）

首次委派或子 Agent 需要更多上下文时使用：

```
OUTPUT FORMAT: You MUST produce a compliant Artifact Pyramid (https://www.groktop.us/artifact-pyramid-progressive-disclosure/).

The pyramid has three layers consumed top-down:
- L1 (01-summary/): Key findings, most important implications. One file only.
- L2 (02-analysis/): Per-dimension analysis files. One file per discovery. Self-contained.
- L3 (03-dossiers/): Raw source excerpts, scrape outputs, methodology notes.

Directory structure at <your-output-path>/:
├── 00-index.md              ← entry point (mandatory)
├── 01-summary/findings.md   ← L1: one findings file
├── 02-analysis/             ← L2: one file per promising result
└── 03-dossiers/             ← L3: raw outputs

Every file MUST end with a ## SOURCES section. SOURCES are navigation affordances
for downstream agents — each entry answers "what will I find if I go deeper?"
L1 SOURCES links to 02-analysis/ files. L2 SOURCES links to 03-dossiers/ files.

If the output directory doesn't exist, create it with mkdir -p before writing.

Respond with ONLY the absolute path to 00-index.md. No summary, no natural language.
```

## 为什么必须这样做

`delegate_task` 子 Agent 无法访问父 Agent 已加载的技能、记忆或对话历史，只会收到 `context` 字符串。如果该字符串没有包含产物金字塔目录结构，它们将在输出目录根部生成扁平文件。扁平文件可能内容良好，但缺少导航机制，使下游管线 Agent 无法使用。
