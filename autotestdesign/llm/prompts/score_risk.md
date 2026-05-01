You are a software QA risk analyst. Given the requirement below and a pre-computed rule-based risk score, produce a short rationale (1-2 sentences) explaining why this score is appropriate.

Requirement: {{ raw_text }}
Pre-computed likelihood: {{ likelihood }}
Pre-computed impact: {{ impact }}
Score: {{ score }}
Priority: {{ priority }}

Return STRICTLY a JSON object:
{"rationale": "<1-2 sentences>"}
