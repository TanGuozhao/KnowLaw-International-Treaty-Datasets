# Treaty AST Integrity Checker

用于检查国际条约结构化 JSON 的：

- JSON 语法错误
- 缺失字段
- 缺失元数据
- 重复节点 ID / block_id
- `attached_after_block_id` 断链
- 基本页码、序号、节点结构异常

当前支持两种输入结构：

- 树形 AST：根节点类似 `type=document`，含 `children` 与 `meta`
- 历史 bundle JSON：顶层含 `schema_version`、`document`、`text_blocks`

## 用法

```powershell
python plugins/treaty-ast-integrity-checker/scripts/check_treaty_ast.py "data/ready/上海合作组织反恐怖主义公约.json"
```

输出 JSON：

```powershell
python plugins/treaty-ast-integrity-checker/scripts/check_treaty_ast.py "path/to/file.json" --format json
```

## 返回规则

- 发现 `ERROR` 时退出码为 `1`
- 只有 `WARNING` 或完全通过时退出码为 `0`

## 说明

这个检查器偏“工程完整性校验”，不是法律内容正确性校验。
