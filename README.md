# ITRAP 国际条约结构化数据集

本仓库收录一批国际条约、协定、议定书、联合声明等法律文件的结构化 JSON 数据。数据主要面向国际法检索、条约条款解析、法律知识库构建、RAG 检索增强、法律文本可视化和自然语言处理实验。

当前数据文件位于 `json/`，每个 JSON 文件对应一份法律文件。文件采用统一的文档树结构，包含 `meta` 元数据和 `children` 正文结构节点。

## 数据概览

- 数据规模：24 份 JSON 文件
- 主要语种：中文，含个别英文文本
- 文件类型：条约、协定、议定书、谅解备忘录、联合声明、公报、附件等
- 结构形式：`document -> preamble/article/annex -> text`
- 元数据索引：见 `metadata/catalog.csv`
- 结构说明：见 `metadata/schema.md`

## 目录结构

```text
data/
  json/                # 已整理的条约 JSON 数据
metadata/
  catalog.csv          # 数据目录索引
  schema.md            # JSON 结构和字段说明
plugins/
  treaty-ast-integrity-checker/
                      # 条约 AST 完整性检查工具
```

## 快速使用

可以直接读取单个 JSON 文件：

```python
import json
from pathlib import Path

path = Path("json/巴黎协定.json")
data = json.loads(path.read_text(encoding="utf-8"))

print(data["meta"]["title"])
print(data["children"][0]["type"])
```

也可以先读取 `metadata/catalog.csv` 进行筛选，再打开对应的 JSON 文件。

## 字段说明

每份 JSON 顶层通常包含：

- `meta`：文件标题、类型、缔约方、关键词、签署日期、生效日期、来源 URL 等元数据
- `type`：顶层节点类型，通常为 `document`
- `title`：文档标题
- `children`：文档正文结构，通常包括序言、条、附件等节点

详细字段含义请参见 `metadata/schema.md`。

## 数据来源与准确性

数据中的 `source`、`source_url`、`source_file_url` 字段记录了整理时使用的来源信息。部分文本来源包括中华人民共和国条约数据库、中国自由贸易区服务网、中华人民共和国外交部等公开页面。

本数据集是结构化整理结果，不构成法律意见。用于法律研究、正式引用或合规判断时，请以官方公布文本和现行有效法律文件为准。

## 校验

仓库中包含一个基础完整性检查工具：

```powershell
python plugins/treaty-ast-integrity-checker/scripts/check_treaty_ast.py "json/巴黎协定.json"
```

该工具主要检查 JSON 语法、必需字段、节点结构等工程完整性问题，不验证法律内容本身的准确性。

## 引用建议

如需引用本数据集，建议注明：

```text
ITRAP 国际条约结构化数据集，JSON 结构化整理版本，访问日期：YYYY-MM-DD。
```

引用具体条约文本时，请同时引用对应 JSON 中的官方来源链接。
