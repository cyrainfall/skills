# 引用链接 — 指针措辞方案

关于如何从 `SKILL.md` 向引用文件编写清晰的"何时阅读"指针的详细指引。

> 本文件不足 300 行，因此不需要目录。

## 核心规则

`SKILL.md` 到支撑文件的每个链接都必须回答：**在什么条件下智能体应该打开这个文件？**

如果答案是"总是" — 内容应该内联，而不是提取。
如果答案是"没有特别情况" — 链接应该被删除。

## 三种可接受的形式

### 形式1：条件式

当引用仅在特定输入条件下相关时使用。

```markdown
当 PDF 是扫描件且需要 OCR 时，阅读
[references/ocr-fallback.md](references/ocr-fallback.md)。
```

模式：`当 <条件> 时，阅读 [文件](路径)。`

### 形式2：任务导向式

当引用支持特定子任务时使用。

```markdown
要生成多包 monorepo 的提交信息，阅读
[references/monorepo.md](references/monorepo.md)。
```

模式：`要 <做某任务>，阅读 [文件](路径)。`

### 形式3：后备/深度转义式

当内联摘要通常够用但有深度内容可用时使用。

```markdown
以上摘要覆盖了标准字段。对于包含签名和计算字段的完整字段类型
矩阵，阅读 [references/field-types.md](references/field-types.md)。
```

模式：`... 对于 <更深层细节>，阅读 [文件](路径)。`

## 放置规则

- 将指针放在相关段落**内部**，而不仅仅是最后的"附加资源"列表中。
- 内联指针在需要的时刻到达智能体；文件底部的列表经常被跳过。
- 末尾的汇总列表作为*补充*是可以的，但不能作为*替代*。

## 反模式与重写

### 反模式：裸链接

```markdown
# 坏
见 [examples.md](examples.md)。
```

```markdown
# 好
对于多文件重构提交的前后对比示例，阅读
[examples.md](examples.md)。
```

### 反模式："更多信息"

```markdown
# 坏
更多信息，见 [reference.md](reference.md)。
```

"更多信息"没有告诉智能体打开文件是否与当前任务相关。

```markdown
# 好
当验证错误提到"循环字段依赖"时，阅读
[reference.md](reference.md) 获取诊断步骤。
```

### 反模式：底部堆砌链接

```markdown
# 坏
## 附加资源
- [a.md](a.md)
- [b.md](b.md)
- [c.md](c.md)
```

每个链接都需要一行"何时阅读"注释，即使在汇总列表中也是如此。

```markdown
# 好
## 附加资源
- [a.md](a.md) — 扫描 PDF 的 OCR 后备方案。
- [b.md](b.md) — 完整字段类型矩阵和验证规则。
- [c.md](c.md) — 带页码范围语法的合并策略。
```

### 反模式：过度链接

不要将每个概念都链接到引用文件。如果概念能在 5 行内写完，就内联它并跳过链接。

### 反模式：深层嵌套引用

```markdown
# 坏（在 references/a.md 中）
详情见 [references/a-details.md](a-details.md)。
```

保持引用只深一层。如果 `a.md` 需要指向更深层，考虑深层内容是否应直接放在 `SKILL.md` 的主资源列表中。

## 重写方案

优化现有技能的链接时：

1. 在 `SKILL.md` 中搜索 `](` 找到所有 markdown 链接。
2. 对每个链接，检查：周围文本是否解释了**何时**打开它？
3. 如果没有，使用上述形式1、2或3重写。
4. 如果链接完全没有明确的"何时"，要么：
   - 删除链接和引用文件（如果确实未使用），或者
   - 内联引用内容（如果总是需要）。

## 完整示例

### 前

```markdown
## Commit Messages

Generate descriptive commit messages from git diffs.

See [format.md](format.md) and [examples.md](examples.md) for more details.

## Additional Resources
- [format.md](format.md)
- [examples.md](examples.md)
- [conventions.md](conventions.md)
```

### 后

```markdown
## Commit Messages

Generate descriptive commit messages from git diffs. The default format is
Conventional Commits: `<type>(<scope>): <subject>`.

When the diff spans multiple packages in a monorepo, read
[conventions.md](conventions.md) for scope-selection rules.

For the exact subject/body character limits and footer conventions, read
[format.md](format.md).

## Additional Resources
- [format.md](format.md) — character limits, body wrapping, footer conventions.
- [examples.md](examples.md) — before/after samples for refactors, fixes, and features.
- [conventions.md](conventions.md) — monorepo scope rules, co-authored-by handling.
```

## 检查清单

在最终确定技能前，验证 `SKILL.md` 中的每个 `](` 链接：

- [ ] 位于相关段落内（而非仅底部列表中）。
- [ ] 附近有"何时阅读"子句。
- [ ] 指向一层深度（到文件，而非经由另一个文件）。
- [ ] 路径使用正斜杠。
- [ ] 目标文件存在且仍然相关。
