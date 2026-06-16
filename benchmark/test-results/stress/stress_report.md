# Stress test compatibility matrix

Generated: 2026-06-16T17:21:47Z (UTC)

| Case | Model | Schema OK | Accuracy% | Additions | Omissions | Disposition | Notes |
|------|-------|-----------|-----------|-----------|------------|-------------|-------|
| BM-OCR-001 | gemini-3.5-flash (gemini-3.5-flash) | False | — |  |  | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None; mismatchReport must not be empty when segments is non-empty (protocol 1.1.0 §5.2) unless pass2Summary is present with segmentsAltered: 0 expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
| BM-OCR-001 | gemini-3-pro (gemini-3.1-pro-preview) | True | — |  |  | FAIL | expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
| BM-KB27 | gemini-3.5-flash (gemini-3.5-flash) | False | 56.2% | 111 | 109 | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None |
| BM-KB27 | gemini-3-pro (gemini-3.1-pro-preview) | True | 53.8% | 110 | 115 | FAIL | — |
