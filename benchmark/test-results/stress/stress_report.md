# Stress test compatibility matrix

Generated: 2026-06-16T18:59:04Z (UTC)

| Case | Model | Schema OK | Accuracy% | Additions | Omissions | Disposition | Notes |
|------|-------|-----------|-----------|-----------|------------|-------------|-------|
| BM-OCR-001 | gemini-3-pro (gemini-3.1-pro-preview) | True | — |  |  | FAIL | expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
| BM-OCR-001 | gemini-3.5-flash (gemini-3.5-flash) | False | — |  |  | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
| BM-LAT-001 | gemini-3-pro (gemini-3.1-pro-preview) | True | — |  |  | FAIL | expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
| BM-LAT-001 | gemini-3.5-flash (gemini-3.5-flash) | False | — |  |  | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
| BM-LAT-002 | gemini-3-pro (gemini-3.1-pro-preview) | True | — |  |  | FAIL | expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
| BM-LAT-002 | gemini-3.5-flash (gemini-3.5-flash) | False | — |  |  | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None expansion firewall (protocol §2.4.1): diplomatic output (preserveOriginalAbbreviations: true) cannot be scored against expanded GT |
