# Stress test compatibility matrix

Generated: 2026-06-09T14:05:05Z (UTC)

| Case | Model | Schema OK | Additions | Omissions | Disposition | Score | Notes |
|------|-------|-----------|-----------|------------|-------------|-------|-------|
| BM-001 | gemini (gemini-2.5-flash) | True | 85 | 65 | FAIL | 0.0 | — |
| BM-001 | gemini-pro (gemini-2.5-pro) | True | 59 | 57 | FAIL | 0.0 | — |
| BM-001 | gemini-3.5-flash (gemini-3.5-flash) | False | 19 | 32 | FAIL | 0.0 | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None |
| BM-001 | gemini-flash-lite (gemini-2.5-flash-lite) | False | 46 | 303 | FAIL | 0.0 | missing required field: confidence; missing required field: uncertaintyTokenCount; segment 0 confidence invalid: got None, expected one of ('high', 'medium', 'low'); mismatchReport is required when segments is non-empty (protocol 1.1.0 §5.2), unless pass2Summary is present with segmentsAltered: 0; hallucinationAudit is required (protocol §7.4 item 5; hard fail if absent) |
