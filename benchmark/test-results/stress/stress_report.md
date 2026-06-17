# Stress test compatibility matrix

Generated: 2026-06-17T14:37:21Z (UTC)

| Case | Model | Schema OK | Accuracy% | Additions | Omissions | Disposition | Notes |
|------|-------|-----------|-----------|-----------|------------|-------------|-------|
| BM-001 | gemini (gemini-2.5-flash) | False | 69.8% | 204 | 148 | FAIL | missing required field: confidence; missing required field: uncertaintyTokenCount; segment 1 confidence invalid: got None, expected one of ('high', 'medium', 'low'); mismatchReport is required when segments is non-empty (protocol 1.1.0 §5.2), unless pass2Summary is present with segmentsAltered: 0; hallucinationAudit is required (protocol §7.4 item 5; hard fail if absent) |
| BM-001 | gemini-3.5-flash (gemini-3.5-flash) | False | 94.7% | 13 | 26 | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None |
| BM-001 | gemini-flash-lite (gemini-2.5-flash-lite) | False | — | — | — | FAIL | API error: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}} |
| BM-MOD-LOVEJOY | gemini (gemini-2.5-flash) | True | 81.1% | 3 | 14 | FAIL | — |
| BM-MOD-LOVEJOY | gemini-3.5-flash (gemini-3.5-flash) | False | — | — | — | FAIL | YAML parse error: while parsing a block mapping
  in "<unicode string>", line 1, column 3:
    - Wait, let's look at the signatur ... 
      ^
expected <block end>, but found '<scalar>'
  in "<unicode string>", line 1, column 65:
     ... ure: "Owen Lovejoy / pr H.E.D." or "pr H.E.H." or "pr H.E.N." or ... 
                                         ^ |
| BM-MOD-LOVEJOY | gemini-flash-lite (gemini-2.5-flash-lite) | True | 79.7% | 6 | 15 | FAIL | — |
| BM-MOD-1854 | gemini (gemini-2.5-flash) | True | 94.7% | 11 | 19 | FAIL | — |
| BM-MOD-1854 | gemini-3.5-flash (gemini-3.5-flash) | False | 97.2% | 11 | 10 | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-1854 | gemini-flash-lite (gemini-2.5-flash-lite) | True | 93.2% | 20 | 24 | FAIL | — |
