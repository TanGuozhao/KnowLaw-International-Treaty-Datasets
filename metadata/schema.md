# JSON Schema 说明

本文档说明 `data/json/` 中条约结构化 JSON 的约定结构。该说明是数据集文档，不是严格的 JSON Schema 校验文件。

## 顶层结构

每个 JSON 文件通常采用以下结构：

```json
{
  "meta": {},
  "type": "document",
  "title": "文件标题",
  "children": []
}
```

## 顶层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `meta` | object | 文档元数据，包括标题、类型、日期、来源等信息 |
| `type` | string | 顶层节点类型，通常为 `document` |
| `title` | string | 文档标题，通常与 `meta.title` 一致 |
| `children` | array | 文档正文结构节点列表 |

## `meta` 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `title` | string | 文件正式标题 |
| `doc_type` | string | 文件类型，如 `agreement`、`convention`、`protocol`、`mou`、`joint declaration`、`joint statement`、`appendix` |
| `law_type` | string | 法律关系类型，如 `bilateral`、`multilateral` |
| `summary` | string | 内容摘要，部分文件可能为空 |
| `country` | array/string | 缔约方、参与方或相关主体 |
| `keyword` | array/string | 主题关键词 |
| `sign_date` | string/array | 签署日期或通过日期 |
| `sign_place` | string/array | 签署地点 |
| `publication_date` | string/array | 发布日期 |
| `effective_date` | string/array | 生效日期 |
| `expiry_date` | string/array | 失效日期或状态说明 |
| `amendment_date` | string/array | 修订日期或修订说明 |
| `status` | string | 效力状态，如 `active`、`revised`、`abolished`、`Not_yet_in_effect` |
| `page_count` | number | 来源文件页数或整理时记录的页数 |
| `source` | string | 来源名称 |
| `source_url` | string | 来源页面 URL |
| `source_file_url` | string | 来源文件 URL，通常为 PDF |
| `split_routing` | string | 切分策略，如 `preamble_then_body`、`body_only`、`unknown` |
| `instrument_profile` | string | 文书完整度，如 `full`、`summary`、`unknown` |
| `graph_short_name` | string | 用于图谱或界面展示的短名，部分文件为空 |

## 正文节点结构

`children` 中的节点通常采用递归树结构：

```json
{
  "type": "article",
  "label": "第一条",
  "title": "定义",
  "text": "",
  "children": []
}
```

## 正文节点字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 节点类型 |
| `label` | string | 节点编号或标签，如 `第一条`、`序言` |
| `title` | string | 节点标题 |
| `text` | string | 文本内容，通常出现在 `text` 类型节点中 |
| `children` | array/string | 子节点列表。少量历史数据中可能为空字符串 |

## 常见节点类型

| 类型 | 说明 |
| --- | --- |
| `document` | 文档根节点 |
| `preamble` | 序言或前言 |
| `article` | 条款 |
| `annex` | 附件 |
| `text` | 具体文本段落 |

## 数据规范建议

- 日期优先使用 `YYYY-MM-DD`，历史数据中保留了部分中文日期或多日期写法。
- 多值字段在 JSON 中优先使用数组，在 `metadata/catalog.csv` 中使用分号 `;` 拼接。
- 正文结构应尽量保持 `children` 为数组；若出现空字符串，表示该节点无进一步子节点。
- `source_url` 和 `source_file_url` 应尽量保留官方来源，便于核验。

## 注意事项

本数据集的结构化结果用于工程检索和研究分析。法律效力、正式译文、缔约状态和后续修订情况，应以官方公布文本及主管机关说明为准。
