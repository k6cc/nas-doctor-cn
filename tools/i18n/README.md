# i18n 工具集

本目录包含 nas-doctor 国际化开发中使用的可复用工具脚本。

## 工具列表

### `verify_keys.py` — 键值对齐校验

```bash
python tools/i18n/verify_keys.py
```

校验 `en.json` 和 `zh.json` 的键对齐情况：
- 两文件键数是否一致
- 是否存在单边缺失的键
- 是否有空值
- 按命名空间统计键数

**使用场景**：每次添加新键后运行，确保中英文翻译完整对齐。

---

### `add_keys.py` — 批量添加翻译键

```bash
# 1. 编辑脚本中的 KEYS_EN 和 KEYS_ZH 字典
# 2. 运行
python tools/i18n/add_keys.py
```

向 `en.json` 和 `zh.json` 批量添加翻译键。已存在的键自动跳过，添加后按键名字母排序。

**使用场景**：新增页面或功能时，批量添加一组翻译键。

---

### `gen_finding_keys.py` — 诊断发现翻译键生成

```bash
python tools/i18n/gen_finding_keys.py
```

为 `internal/analyzer/` 中的所有诊断发现类型生成 i18n 键（`finding.<type>.<field>`）。

覆盖 4 个字段：`title`、`description`、`action`、`impact`。

**使用场景**：在 analyzer 中新增 FindingType 后，运行此脚本生成对应的翻译键。
脚本内的 `FINDINGS` 列表需要手动同步新增的类型定义。

## i18n 架构概览

```
internal/api/i18n/
├── i18n.go          # Go 后端：go:embed JSON 字典，注入到 HTML
└── locales/
    ├── en.json      # 英文字典（基准语言，1560+ keys）
    └── zh.json      # 中文字典（1560+ keys，与 en.json 完全对齐）
```

### 翻译流程

1. **后端**：`Finding` 结构体通过 `FindingType` 字段标识发现类型
2. **前端**：`translateFinding()` 函数从 `dictionaries['en']` 获取英文模板，构建正则提取参数，替换到翻译模板
3. **降级**：无 `FindingType` 或无翻译键时，返回原始英文文本

### Key 命名规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `dashboard.*` | 仪表盘 | `dashboard.ups.title` |
| `finding.*` | 诊断发现 | `finding.sata_cable.title` |
| `planner.*` | 更换计划 | `planner.reason.healthy` |
| `alerts.*` | 告警页 | `alerts.enum.severity.critical` |
| `settings.*` | 设置页 | `settings.severity.warning` |
| `nav.*` | 导航 | `nav.alerts` |
| `trend.*` | 趋势预测 | `trend.recommendation.monitor` |

### 添加新语言

1. 复制 `en.json` 为 `<lang>.json`（如 `ja.json`）
2. 翻译所有值（保留 `{{param}}` 占位符不变）
3. 在 `i18n.go` 的 `IsValid()` 函数中添加语言代码
4. 在设置页语言下拉中添加选项
5. 运行 `verify_keys.py` 确认对齐
