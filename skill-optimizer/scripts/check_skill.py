#!/usr/bin/env python3
"""针对六个优化模式审计 Qoder 技能。

用法：
    python check_skill.py <技能目录路径>

检查项：
    1. 长度控制   - SKILL.md 正文 <= 500 行（>= 400 行时警告）。
    2. 引用链接   - SKILL.md 中的每个 markdown 链接都有
                     "何时阅读"上下文。
    3. 大文件目录 - 超过 300 行的引用文件包含
                     "## Table of Contents" 或 "## 目录" 段落。
    4. 流程描述   - 含执行流程的 SKILL.md 覆盖五要素
                    （触发条件、主流程、分支决策、异常处理、输出副作用）。
    5. 描述语言   - SKILL.md 正文避免模糊词和内部实现细节。
    6. 异常处理   - 流程描述中的错误码携带语义。

所有检查通过时退出码为 0，否则为 1。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 阈值
HARD_LIMIT = 500
SOFT_LIMIT = 400
TOC_THRESHOLD = 300

# 指示链接带有"何时阅读"上下文的关键词。
# 不区分大小写。英文和中文线索。
WHEN_KEYWORDS = [
    "when ", "if ", "for ", "to ",
    "read ", "see ", "refer",
    "use when", "use for",
    "当 ", "若 ", "如果", "对于", "用于", "参阅", "参考", "详见",
]

# 模式5：流程描述中不应出现的模糊词。
VAGUE_WORDS_CN = ["可能", "大概", "有时候", "尽量", "也许", "似乎", "差不多"]
VAGUE_WORDS_EN = ["maybe ", "probably ", "sometimes ", "roughly ", "perhaps ", "might "]

# 模式5：不应出现在流程描述中的内部实现模式。
IMPL_PATTERNS = [
    r"SELECT\s.+\sFROM",
    r"INSERT\s.+\sINTO",
    r"UPDATE\s.+\sSET",
    r"DELETE\s.+\sFROM",
    r"\.(execute|fetchone|fetchall)\(",
    r"requests\.(get|post|put|delete)\(",
    r"os\.environ",
]

# 流程段落指示词 — 如果 SKILL.md 包含这些，则检查模式4-6。
FLOW_INDICATORS = ["执行流程", "步骤", "工作流", "workflow", "step"]

# 模式4：流程描述五要素及其关键词。
FLOW_ELEMENTS = {
    "触发条件": ["触发", "前提", "前置", "前置检查", "必填", "权限要求", "trigger"],
    "主流程": ["主流程", "happy path", "步骤1", "step 1", "正常流程", "编号步骤"],
    "分支决策": ["IF", "分支", "决策", "判断", "条件", "ELSE", "ELSE IF", "否则"],
    "异常处理": ["异常", "容错", "错误", "失败", "超时", "重试", "降级", "error", "timeout", "fallback"],
    "输出副作用": ["输出", "返回", "副作用", "返回结构", "side effect", "output"],
}

# Markdown 链接正则，排除图片链接。
LINK_RE = re.compile(r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)')
H1_RE = re.compile(r"^#\s+", re.MULTILINE)


def strip_frontmatter(text: str) -> str:
    """如果存在则移除 YAML frontmatter。"""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :]
    return text


def count_body_lines(path: Path) -> int:
    """统计正文行数（不含 frontmatter）。"""
    text = path.read_text(encoding="utf-8")
    body = strip_frontmatter(text)
    return body.count("\n") + (0 if body.endswith("\n") else 1)


def has_toc(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return bool(
        re.search(r"^##\s+(Table of Contents|目录)\s*$", text, re.MULTILINE)
    )


def strip_code_blocks(text: str) -> str:
    """移除围栏代码块内容，避免对示例代码误报。"""
    return re.sub(r"```[^`]*```", "", text, flags=re.DOTALL)


def strip_inline_code(text: str) -> str:
    """移除行内代码内容，避免对反引号包裹的示例词误报。"""
    return re.sub(r"`[^`]+`", "", text)


def find_links(text: str) -> list[tuple[int, str, str, str]]:
    """返回每个链接的 (行号, 标签, URL, 所在行)。"""
    results = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in LINK_RE.finditer(line):
            label, url = m.group(1), m.group(2)
            # 跳过锚点和外部 URL；仅审计文件引用。
            if url.startswith(("http://", "https://", "#", "mailto:")):
                continue
            results.append((lineno, label, url, line))
    return results


def has_when_context(label: str, line: str) -> bool:
    """启发式判断：该行或链接标签是否带有'何时阅读'线索？"""
    haystack = (line + " " + label).lower()
    return any(kw in haystack for kw in WHEN_KEYWORDS)


def has_flow_section(text: str) -> bool:
    """判断文本是否包含流程/工作流指示词。"""
    lower = text.lower()
    return any(kw in lower for kw in FLOW_INDICATORS)


def check_flow_elements(text: str) -> list[str]:
    """返回缺失的流程要素列表（模式4）。"""
    missing = []
    for element, keywords in FLOW_ELEMENTS.items():
        if not any(kw in text for kw in keywords):
            missing.append(element)
    return missing


def find_vague_words(text: str) -> list[tuple[int, str]]:
    """返回 (行号, 模糊词) 列表（模式5）。跳过代码块和行内代码。"""
    clean = strip_code_blocks(text)
    clean = strip_inline_code(clean)
    results = []
    all_vague = VAGUE_WORDS_CN + VAGUE_WORDS_EN
    for lineno, line in enumerate(clean.splitlines(), start=1):
        lower = line.lower()
        for word in all_vague:
            if word in lower:
                results.append((lineno, word.strip()))
    return results


def find_impl_patterns(text: str) -> list[tuple[int, str]]:
    """返回 (行号, 匹配模式) 列表（模式5）。"""
    results = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pat in IMPL_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                results.append((lineno, pat))
    return results


def audit(skill_dir: Path) -> int:
    issues = 0
    warnings = 0
    print(f"Auditing skill: {skill_dir}")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"  [FAIL] SKILL.md not found in {skill_dir}")
        return 1

    # --- 检查1：SKILL.md 长度 ---
    lines = count_body_lines(skill_md)
    if lines > HARD_LIMIT:
        print(f"  [FAIL] SKILL.md: {lines} lines (> {HARD_LIMIT} hard limit)")
        issues += 1
    elif lines >= SOFT_LIMIT:
        print(f"  [WARN] SKILL.md: {lines} lines (>= {SOFT_LIMIT} soft limit)")
    else:
        print(f"  [OK]   SKILL.md: {lines} lines (< {HARD_LIMIT})")

    # --- 检查2：引用链接上下文 ---
    skill_text = skill_md.read_text(encoding="utf-8")
    body = strip_frontmatter(skill_text)
    # 跳过代码块内的链接（示例代码不是真实引用）
    body_no_codeblocks = strip_code_blocks(body)
    links = find_links(body_no_codeblocks)
    # 但行号需在原始 body 中查找，所以重新扫描原始文本获取行号
    all_links = find_links(body)
    # 过滤掉代码块内的链接
    codeblock_links = find_links(body_no_codeblocks)
    codeblock_urls = {(ln, url) for ln, label, url, line in codeblock_links}
    links = [
        (ln, label, url, line) for ln, label, url, line in all_links
        if (ln, url) in {(l[0], l[2]) for l in codeblock_links}
    ]
    bad_links = [
        (ln, label, url) for ln, label, url, line in links
        if not has_when_context(label, line)
    ]
    if links:
        if bad_links:
            print(
                f"  [FAIL] {len(bad_links)}/{len(links)} reference link(s) "
                f"lack 'when to read' context:"
            )
            for ln, label, url in bad_links:
                print(f"           line {ln}: [{label}]({url})")
            issues += 1
        else:
            print(
                f"  [OK]   All {len(links)} reference link(s) have "
                f"'when to read' context"
            )
    else:
        print("  [OK]   No reference links in SKILL.md")

    # --- 检查3：大型引用文件目录 ---
    ref_files = [
        p for p in skill_dir.rglob("*.md")
        if p.resolve() != skill_md.resolve()
    ]
    big_without_toc = []
    big_with_toc = []
    for ref in ref_files:
        rlines = count_body_lines(ref)
        if rlines > TOC_THRESHOLD:
            rel = ref.relative_to(skill_dir).as_posix()
            if has_toc(ref):
                big_with_toc.append((rel, rlines))
            else:
                big_without_toc.append((rel, rlines))

    if big_without_toc:
        print(
            f"  [FAIL] {len(big_without_toc)} reference file(s) > "
            f"{TOC_THRESHOLD} lines lack a TOC:"
        )
        for rel, rlines in big_without_toc:
            print(f"           {rel} ({rlines} lines)")
        issues += 1
    if big_with_toc:
        print(
            f"  [OK]   All {len(big_with_toc)} reference file(s) > "
            f"{TOC_THRESHOLD} lines have a TOC"
        )
    if not big_without_toc and not big_with_toc:
        print(
            f"  [OK]   No reference files exceed {TOC_THRESHOLD} lines"
        )

    # --- 检查4-6：内容质量（仅当存在流程段落时） ---
    if has_flow_section(body):
        # 检查4：流程描述完备性
        missing_elements = check_flow_elements(body)
        if missing_elements:
            print(
                f"  [WARN] 流程描述可能缺少: {', '.join(missing_elements)}"
            )
            warnings += 1
        else:
            print("  [OK]   流程描述覆盖所有五要素")

        # 检查5：描述语言 — 模糊词
        vague = find_vague_words(body)
        if vague:
            print(
                f"  [WARN] SKILL.md 中发现 {len(vague)} 个模糊词:"
            )
            for ln, word in vague[:5]:
                print(f"           line {ln}: '{word}'")
            if len(vague) > 5:
                print(f"           ... 还有 {len(vague) - 5} 个")
            warnings += 1
        else:
            print("  [OK]   SKILL.md 中未检测到模糊词")

        # 检查5：描述语言 — 内部实现细节
        impl = find_impl_patterns(body)
        if impl:
            print(
                f"  [WARN] 发现 {len(impl)} 处内部实现模式:"
            )
            for ln, pat in impl[:5]:
                print(f"           line {ln}: 匹配 '{pat}'")
            warnings += 1
        else:
            print("  [OK]   未检测到内部实现模式")

        # 检查6：错误码语义
        error_code_re = re.compile(r"`([A-Z][A-Z0-9_]{2,})`")
        non_error_words = {
            "IF", "ELSE", "THEN", "AND", "OR", "NOT", "JSON",
            "API", "SQL", "HTTP", "URL", "ID", "UUID", "MCP",
            "HAPPY", "PATH", "YAML", "SKILL", "OPENAPI", "PDF",
        }
        error_codes = []
        for m in error_code_re.finditer(body):
            code = m.group(1)
            if code not in non_error_words:
                error_codes.append(code)
        if error_codes:
            unique = sorted(set(error_codes))
            print(f"  [INFO]  发现 {len(unique)} 个错误码: {', '.join(unique[:10])}")
            print("         请确认是否遵循 'CODE | 消息 | 建议' 格式。")
        else:
            print("  [INFO]  未检测到错误码（建议人工审查）")
    else:
        print("  [SKIP]  未检测到流程段落，跳过内容质量检查（模式4-6）")

    # --- 汇总 ---
    print()
    if issues == 0 and warnings == 0:
        print("所有检查通过。")
        return 0
    if issues > 0:
        print(f"{issues} 项失败, {warnings} 项警告。")
        return 1
    print(f"所有检查通过，{warnings} 项警告。")
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.is_dir():
        print(f"Not a directory: {skill_dir}")
        return 2
    return audit(skill_dir)


if __name__ == "__main__":
    sys.exit(main())
