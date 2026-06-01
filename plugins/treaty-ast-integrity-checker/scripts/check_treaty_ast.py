from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TREE_REQUIRED_META = [
    "document_id",
    "doc_type",
    "title",
    "source_uri",
    "page_count",
]

TREE_RECOMMENDED_META = [
    "first_article_line_index",
    "instrument_profile",
    "split_routing",
    "page_line_spans",
]

BUNDLE_REQUIRED_TOP = ["schema_version", "document", "text_blocks"]
BUNDLE_REQUIRED_DOCUMENT = ["document_id", "doc_type", "title"]
BUNDLE_RECOMMENDED_DOCUMENT = [
    "source_uri",
    "page_count",
    "instrument_profile",
    "split_routing",
]
BUNDLE_REQUIRED_BLOCK = [
    "block_id",
    "sequence",
    "functional_block",
    "block_kind",
    "structure",
    "pages",
    "spans_pages",
    "text",
]
BUNDLE_REQUIRED_STRUCTURE = ["part", "chapter", "section", "article", "paragraph", "item"]
BUNDLE_RECOMMENDED_STRUCTURE = [
    "part_label_zh",
    "chapter_label_zh",
    "section_label_zh",
    "article_label_zh",
    "paragraph_label_zh",
    "item_label_zh",
]

TREE_NODE_REQUIRED_BY_TYPE = {
    "document": ["id", "type", "children", "meta"],
    "text": ["id", "type", "text", "line_start", "children"],
    "default": ["id", "type", "children", "line_start"],
}

LEGACY_TREE_ROOT_REQUIRED = ["id", "type", "source", "title", "children"]


@dataclass
class Finding:
    level: str
    code: str
    location: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "level": self.level,
            "code": self.code,
            "location": self.location,
            "message": self.message,
        }


class Reporter:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def error(self, code: str, location: str, message: str) -> None:
        self.findings.append(Finding("ERROR", code, location, message))

    def warning(self, code: str, location: str, message: str) -> None:
        self.findings.append(Finding("WARNING", code, location, message))

    def has_errors(self) -> bool:
        return any(f.level == "ERROR" for f in self.findings)


def load_json(path: Path) -> tuple[Any | None, list[Finding]]:
    findings: list[Finding] = []
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="gb18030")
    except FileNotFoundError:
        findings.append(Finding("ERROR", "FILE_NOT_FOUND", str(path), "文件不存在"))
        return None, findings

    try:
        return json.loads(raw), findings
    except json.JSONDecodeError as exc:
        findings.append(
            Finding(
                "ERROR",
                "JSON_SYNTAX_ERROR",
                f"{path}:{exc.lineno}:{exc.colno}",
                exc.msg,
            )
        )
        return None, findings


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def ensure_fields(
    rep: Reporter,
    obj: dict[str, Any],
    required: list[str],
    location: str,
    *,
    allow_blank: bool = False,
) -> None:
    for field in required:
        if field not in obj:
            rep.error("MISSING_FIELD", location, f"缺少字段 `{field}`")
            continue
        if not allow_blank and is_blank(obj.get(field)):
            rep.error("EMPTY_FIELD", f"{location}.{field}", "字段为空")


def warn_fields(rep: Reporter, obj: dict[str, Any], fields: list[str], location: str) -> None:
    for field in fields:
        if field not in obj or is_blank(obj.get(field)):
            rep.warning("MISSING_RECOMMENDED_FIELD", location, f"建议补充字段 `{field}`")


def validate_positive_int(rep: Reporter, value: Any, location: str) -> None:
    if not isinstance(value, int) or value < 1:
        rep.error("INVALID_INT", location, "应为大于等于 1 的整数")


def validate_tree_ast(data: dict[str, Any], rep: Reporter) -> None:
    ensure_fields(rep, data, TREE_NODE_REQUIRED_BY_TYPE["document"], "root")
    if data.get("type") != "document":
        rep.error("INVALID_ROOT_TYPE", "root.type", "根节点 type 必须为 `document`")

    meta = data.get("meta")
    if not isinstance(meta, dict):
        rep.error("INVALID_META", "root.meta", "`meta` 必须是对象")
    else:
        ensure_fields(rep, meta, TREE_REQUIRED_META, "root.meta")
        warn_fields(rep, meta, TREE_RECOMMENDED_META, "root.meta")
        page_count = meta.get("page_count")
        if not is_blank(page_count) and (not isinstance(page_count, int) or page_count < 0):
            rep.error("INVALID_PAGE_COUNT", "root.meta.page_count", "page_count 应为大于等于 0 的整数")
        spans = meta.get("page_line_spans")
        if spans is not None and not isinstance(spans, list):
            rep.error("INVALID_PAGE_LINE_SPANS", "root.meta.page_line_spans", "page_line_spans 必须是数组")

    seen_ids: set[str] = set()

    def walk(node: Any, location: str) -> None:
        if not isinstance(node, dict):
            rep.error("INVALID_NODE", location, "节点必须是对象")
            return

        node_type = str(node.get("type") or "").strip()
        required = TREE_NODE_REQUIRED_BY_TYPE.get(node_type, TREE_NODE_REQUIRED_BY_TYPE["default"])
        ensure_fields(rep, node, required, location)

        node_id = str(node.get("id") or "").strip()
        if node_id:
            if node_id in seen_ids:
                rep.error("DUPLICATE_NODE_ID", f"{location}.id", f"重复的节点 id: `{node_id}`")
            seen_ids.add(node_id)

        if "line_start" in node and not is_blank(node.get("line_start")):
            validate_positive_int(rep, node.get("line_start"), f"{location}.line_start")

        if node_type == "text" and is_blank(node.get("text")):
            rep.error("EMPTY_TEXT", f"{location}.text", "文本节点缺少正文")

        if node_type in {"article", "chapter", "section", "part", "annex", "preamble", "paragraph"}:
            if "label" not in node:
                rep.warning("MISSING_LABEL", location, f"`{node_type}` 节点缺少 `label`")
            if "title" not in node:
                rep.warning("MISSING_TITLE", location, f"`{node_type}` 节点缺少 `title`")

        children = node.get("children")
        if not isinstance(children, list):
            rep.error("INVALID_CHILDREN", f"{location}.children", "`children` 必须是数组")
            return

        for idx, child in enumerate(children):
            child_id = ""
            if isinstance(child, dict):
                child_id = str(child.get("id") or "").strip()
            child_location = f"{location}.children[{idx}]"
            if child_id:
                child_location = f"{child_location}<{child_id}>"
            walk(child, child_location)

    walk(data, "root")


def validate_legacy_tree_ast(data: dict[str, Any], rep: Reporter) -> None:
    ensure_fields(rep, data, LEGACY_TREE_ROOT_REQUIRED, "root")
    if data.get("type") != "document":
        rep.error("INVALID_ROOT_TYPE", "root.type", "根节点 type 必须为 `document`")

    rep.warning("MISSING_META", "root", "缺少 `meta`；这是旧版树形 AST，无法检查文书元数据完整性")
    warn_fields(
        rep,
        data,
        ["source"],
        "root",
    )

    seen_ids: set[str] = set()

    def walk(node: Any, location: str) -> None:
        if not isinstance(node, dict):
            rep.error("INVALID_NODE", location, "节点必须是对象")
            return

        node_type = str(node.get("type") or "").strip()
        required = TREE_NODE_REQUIRED_BY_TYPE.get(node_type, TREE_NODE_REQUIRED_BY_TYPE["default"])
        required = [field for field in required if field != "meta"]
        ensure_fields(rep, node, required, location)

        node_id = str(node.get("id") or "").strip()
        if node_id:
            if node_id in seen_ids:
                rep.error("DUPLICATE_NODE_ID", f"{location}.id", f"重复的节点 id: `{node_id}`")
            seen_ids.add(node_id)

        if "line_start" in node and not is_blank(node.get("line_start")):
            validate_positive_int(rep, node.get("line_start"), f"{location}.line_start")

        if node_type == "text":
            if is_blank(node.get("text")):
                rep.error("EMPTY_TEXT", f"{location}.text", "文本节点缺少正文")
        elif node_type != "document" and "text" not in node:
            rep.warning("MISSING_TEXT_FIELD", location, f"`{node_type}` 节点缺少 `text` 字段")

        if node_type in {"article", "chapter", "section", "part", "annex", "preamble", "paragraph"}:
            if "label" not in node:
                rep.warning("MISSING_LABEL", location, f"`{node_type}` 节点缺少 `label`")
            if "title" not in node:
                rep.warning("MISSING_TITLE", location, f"`{node_type}` 节点缺少 `title`")

        children = node.get("children")
        if not isinstance(children, list):
            rep.error("INVALID_CHILDREN", f"{location}.children", "`children` 必须是数组")
            return

        for idx, child in enumerate(children):
            child_id = ""
            if isinstance(child, dict):
                child_id = str(child.get("id") or "").strip()
            child_location = f"{location}.children[{idx}]"
            if child_id:
                child_location = f"{child_location}<{child_id}>"
            walk(child, child_location)

    walk(data, "root")


def validate_bundle(data: dict[str, Any], rep: Reporter) -> None:
    ensure_fields(rep, data, BUNDLE_REQUIRED_TOP, "root")

    doc = data.get("document")
    if not isinstance(doc, dict):
        rep.error("INVALID_DOCUMENT", "root.document", "`document` 必须是对象")
    else:
        ensure_fields(rep, doc, BUNDLE_REQUIRED_DOCUMENT, "root.document")
        warn_fields(rep, doc, BUNDLE_RECOMMENDED_DOCUMENT, "root.document")

    blocks = data.get("text_blocks")
    if not isinstance(blocks, list):
        rep.error("INVALID_TEXT_BLOCKS", "root.text_blocks", "`text_blocks` 必须是数组")
        return

    if not blocks:
        rep.warning("EMPTY_TEXT_BLOCKS", "root.text_blocks", "`text_blocks` 为空")

    seen_block_ids: set[str] = set()
    seen_sequences: set[int] = set()

    for idx, block in enumerate(blocks):
        location = f"root.text_blocks[{idx}]"
        if not isinstance(block, dict):
            rep.error("INVALID_BLOCK", location, "文本块必须是对象")
            continue

        ensure_fields(rep, block, BUNDLE_REQUIRED_BLOCK, location)

        block_id = str(block.get("block_id") or "").strip()
        if block_id:
            if block_id in seen_block_ids:
                rep.error("DUPLICATE_BLOCK_ID", f"{location}.block_id", f"重复的 block_id: `{block_id}`")
            seen_block_ids.add(block_id)

        seq = block.get("sequence")
        if not isinstance(seq, int) or seq < 1:
            rep.error("INVALID_SEQUENCE", f"{location}.sequence", "sequence 应为大于等于 1 的整数")
        elif seq in seen_sequences:
            rep.warning("DUPLICATE_SEQUENCE", f"{location}.sequence", f"重复的 sequence: {seq}")
        else:
            seen_sequences.add(seq)

        structure = block.get("structure")
        if not isinstance(structure, dict):
            rep.error("INVALID_STRUCTURE", f"{location}.structure", "`structure` 必须是对象")
        else:
            ensure_fields(rep, structure, BUNDLE_REQUIRED_STRUCTURE, f"{location}.structure", allow_blank=True)
            warn_fields(rep, structure, BUNDLE_RECOMMENDED_STRUCTURE, f"{location}.structure")

        pages = block.get("pages")
        if not isinstance(pages, dict):
            rep.error("INVALID_PAGES", f"{location}.pages", "`pages` 必须是对象")
        else:
            ensure_fields(rep, pages, ["start", "end"], f"{location}.pages", allow_blank=True)
            start = pages.get("start")
            end = pages.get("end")
            if not isinstance(start, int) or start < 1:
                rep.error("INVALID_PAGE_START", f"{location}.pages.start", "页码起始值应为大于等于 1 的整数")
            if not isinstance(end, int) or end < 1:
                rep.error("INVALID_PAGE_END", f"{location}.pages.end", "页码结束值应为大于等于 1 的整数")
            if isinstance(start, int) and isinstance(end, int) and start > end:
                rep.error("INVALID_PAGE_RANGE", f"{location}.pages", "pages.start 不能大于 pages.end")

    for idx, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        attached = block.get("attached_after_block_id")
        if attached and attached not in seen_block_ids:
            rep.error(
                "BROKEN_ATTACHMENT_REF",
                f"root.text_blocks[{idx}].attached_after_block_id",
                f"引用了不存在的 block_id: `{attached}`",
            )


def detect_format(data: Any) -> str:
    if not isinstance(data, dict):
        return "unknown"
    if "schema_version" in data and "document" in data and "text_blocks" in data:
        return "bundle"
    if data.get("type") == "document" and "children" in data and "meta" in data:
        return "tree"
    if data.get("type") == "document" and "children" in data and "title" in data:
        return "legacy_tree"
    return "unknown"


def build_output(path: Path, fmt: str, data: Any, rep: Reporter) -> str:
    detected = detect_format(data)
    payload = {
        "path": str(path),
        "format": detected,
        "ok": not rep.has_errors(),
        "summary": {
            "errors": sum(1 for f in rep.findings if f.level == "ERROR"),
            "warnings": sum(1 for f in rep.findings if f.level == "WARNING"),
        },
        "findings": [f.to_dict() for f in rep.findings],
    }
    if fmt == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2)

    lines = [
        f"文件: {payload['path']}",
        f"识别格式: {detected}",
        f"结果: {'通过' if payload['ok'] else '未通过'}",
        f"错误: {payload['summary']['errors']}  警告: {payload['summary']['warnings']}",
    ]
    if not rep.findings:
        lines.append("未发现语法或完整性问题。")
        return "\n".join(lines)

    lines.append("")
    for i, finding in enumerate(rep.findings, start=1):
        lines.append(
            f"{i}. [{finding.level}] {finding.code} @ {finding.location} - {finding.message}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check treaty AST JSON syntax and completeness.")
    parser.add_argument("json_path", help="待检查 JSON 文件路径")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    args = parser.parse_args()

    path = Path(args.json_path)
    data, load_findings = load_json(path)
    rep = Reporter()
    rep.findings.extend(load_findings)

    if data is None:
        print(build_output(path, args.format, {}, rep))
        return 1

    detected = detect_format(data)
    if detected == "tree":
        validate_tree_ast(data, rep)
    elif detected == "legacy_tree":
        validate_legacy_tree_ast(data, rep)
    elif detected == "bundle":
        validate_bundle(data, rep)
    else:
        rep.error(
            "UNKNOWN_FORMAT",
            "root",
            "无法识别 JSON 结构；当前仅支持树形 treaty AST 与 ?? bundle JSON",
        )

    print(build_output(path, args.format, data, rep))
    return 1 if rep.has_errors() else 0


if __name__ == "__main__":
    raise SystemExit(main())
