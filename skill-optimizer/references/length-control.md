# 长度控制 — 拆分策略

通过结构化拆分和渐进式披露保持 `SKILL.md` 在 500 行以内的详细方案。

> 本文件不足 300 行，因此不需要目录。

## 何时拆分

当以下**任一**条件满足时拆分 `SKILL.md`：

- 行数 ≥ 400（主动）或 > 500（硬限制）。
- 任何单个 `##` 段落超过约 100 行。
- 内容仅在特定子工作流中需要（非每次调用都需要）。
- 用户反馈技能感觉冗长或难以浏览。

当技能较短（< 300 行）时**不要**拆分，即使主题感觉很深 — 内联比跳转更快。

## 保留内联 vs 提取

| 保留在 `SKILL.md` 中 | 提取到 `references/<topic>.md` |
|----------------------|-------------------------------|
| 触发描述 | 完整 API 文档 |
| 工作流概览/检查清单 | 边缘情况表 |
| 核心决策点 | 长示例序列 |
| 每个主题 3–6 行摘要 | 深度技术背景 |
| 指向引用文件的直接指针 | 替代方案与权衡 |

经验法则：如果智能体不是在**每次**调用时都需要该内容，就提取它。

## 拆分步骤

1. **盘点** — 列出每个 `##` 段落及其行数。
2. **排序** — 按大小排序；候选对象是最重的 2–3 个段落。
3. **提取** — 将重度内容移入 `references/<kebab-case-topic>.md`。
4. **摘要** — 在 `SKILL.md` 中用 3–6 行摘要替换已提取内容。
5. **链接** — 添加"何时阅读"指针（见 [reference-linking.md](reference-linking.md)）。
6. **目录** — 如果新引用文件超过 300 行，添加目录（见 [toc-patterns.md](toc-patterns.md)）。

## 层次设计

保持引用**只深一层**：

```
好：
SKILL.md → references/foo.md
SKILL.md → references/bar.md

坏：
SKILL.md → references/foo.md → references/foo-details.md
```

深层嵌套引用有部分读取和上下文混淆的风险。如果引用文件本身需要拆分，考虑父主题是否应成为独立技能。

## 前后对比示例

### 前（620 行，违反长度限制）

```markdown
---
name: pdf-processing
description: ...
---

# PDF Processing

## Extracting Text
[80 行 pdfplumber 细节、边缘情况、OCR 后备方案]

## Filling Forms
[120 行字段类型表、验证、示例]

## Merging Documents
[90 行合并策略、页码范围语法、错误情况]

## Signatures
[70 行签名字段细节]

## Common Errors
[60 行错误表]
...
```

### 后（280 行，合规）

```markdown
---
name: pdf-processing
description: ...
---

# PDF Processing

## Quick Start
[20 行常见工作流]

## Extracting Text
Use pdfplumber. For scanned PDFs needing OCR, read
[references/text-extraction.md](references/text-extraction.md).

[15 行摘要 + 基本代码示例]

## Filling Forms
Three field types: text, checkbox, dropdown. For the full field-type matrix
and validation rules, read [references/form-filling.md](references/form-filling.md).

[20 行摘要]

## Merging Documents
Use pypdf for basic merges. For page-range syntax and ordering strategies,
read [references/merging.md](references/merging.md).

[15 行摘要]

## Additional Resources
- [references/text-extraction.md](references/text-extraction.md) — OCR 后备方案、表格抽取。
- [references/form-filling.md](references/form-filling.md) — 字段类型、验证。
- [references/merging.md](references/merging.md) — 页码范围、元数据处理。
- [references/errors.md](references/errors.md) — 完整错误查找表。
```

## 决策树

```
SKILL.md 是否 > 500 行？
├── 是 → 必须拆分。从最大的段落开始。
└── 否
    ├── 是否 > 400 行？
    │   ├── 是 → 建议主动拆分。
    │   └── 否
    │       ├── 任何单个段落 > 100 行？
    │       │   ├── 是 → 仅拆分该段落。
    │       │   └── 否 → 保持原样。
```

## 反模式

1. **过度提取** — 仅留下指针的 `SKILL.md` 没有独立使用价值。智能体应能不打开任何引用文件就处理常见情况。

2. **按文件类型而非任务拆分** — 创建 `all-examples.md` 和 `all-tables.md` 迫使智能体阅读无关内容。按**主题/任务**拆分，使每个引用文件对一个工作流自包含。

3. **孤立引用** — 创建了 `SKILL.md` 从未链接的引用文件。审计脚本会标记这些；要么添加指针，要么删除文件。

4. **重复内容** — 在 `SKILL.md` 中保留旧内容的同时又提取它。始终替换，绝不重复。
