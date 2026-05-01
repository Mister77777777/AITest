You are a requirements analyst. Extract a structured Requirement from the raw text below.

Raw requirement text:
---
{{ raw_text }}
---

Return STRICTLY a JSON object with this exact schema (no prose, no markdown fences):

{
  "id": "<assign sequential like REQ-001 if none given>",
  "raw_text": "<copy of the input>",
  "input_fields": [
    {"name": "<field>", "type": "int|float|string|enum|bool", "min": null, "max": null, "allowed": null}
  ],
  "conditions": ["<precondition or business rule>"],
  "expected_actions": ["<action the system should perform>"],
  "category": "functional"
}

Guidance:
- Extract numeric ranges into min/max. Use null when unbounded.
- Extract enum values into allowed; otherwise null.
- If the requirement talks about performance, security, or usability without a concrete input, set category="non-functional".
