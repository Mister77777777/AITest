你是一名需求分析师。请从下方原始需求文本中抽取结构化 Requirement。原文可能是中文或英文,请准确理解语义后填充字段。

原始需求文本:
---
{{ raw_text }}
---

严格返回以下 schema 的 JSON(不要输出 markdown 代码块、不要额外说明):

{
  "id": "<若原文未给出,按 REQ-001 这种格式自动编号>",
  "raw_text": "<原样复制输入文本>",
  "input_fields": [
    {"name": "<字段英文标识,如 age / password / amount>", "type": "int|float|string|enum|bool", "min": null, "max": null, "allowed": null}
  ],
  "conditions": ["<中文描述的前置条件或业务规则>"],
  "expected_actions": ["<中文描述的系统应执行的动作>"],
  "category": "functional"
}

填写指引:
- `input_fields.name` 必须使用英文标识符(如 age、password、email、amount),这是代码层的字段键名,不要用中文。
- `input_fields.type` 必须从 int/float/string/enum/bool 五类中选择。
- 数值字段若有范围约束,写入 min/max;否则填 null。
- 枚举字段把所有合法取值填到 allowed;否则填 null。
- `conditions` 和 `expected_actions` 使用中文描述(贴合原文语言)。
- 若需求属于性能、安全、可用性等非功能类,将 category 设为 "non-functional"。
