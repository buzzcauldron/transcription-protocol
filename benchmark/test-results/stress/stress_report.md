# Stress test — image-only results

Generated: 2026-06-10T19:42:11Z (UTC)

Image-only baseline (no HTR pipeline). For transcriber-shell pipeline results see
[transcription-shell/benchmark/results/stress/](https://github.com/buzzcauldron/transcription-shell/tree/main/benchmark/results/stress/).

| Case | Model | Schema OK | Accuracy% | Additions | Omissions | Disposition | Notes |
|------|-------|-----------|-----------|-----------|------------|-------------|-------|
| BM-001 | anthropic | False | — | — | — | FAIL | ERROR: ANTHROPIC_API_KEY is not set |
| BM-001 | claude-code (claude-code-cli) | False | — | — | — | FAIL | ERROR: Not logged in — run `claude login` in your terminal, then re-run: cd /Users/halxiii/Projects/transcription-protoc |
| BM-001 | gemini (gemini-2.5-flash) | True | — | 85 | 65 | FAIL | — |
| BM-001 | gemini-3.5-flash (gemini-3.5-flash) | False | — | 19 | 32 | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got |
| BM-001 | gemini-flash-lite (gemini-2.5-flash-lite) | False | — | 46 | 303 | FAIL | missing required field: confidence; missing required field: uncertaintyTokenCount; segment 0 confidence invalid: got Non |
| BM-001 | gemini-pro (gemini-2.5-pro) | True | — | 31 | 24 | FAIL | — |
| BM-001 | openai | False | — | — | — | FAIL | ERROR: OPENAI_API_KEY is not set |
| BM-MED-001 | gemini (gemini-2.5-flash) | True | — | 28 | 25 | FAIL | — |
| BM-MED-001 | gemini-pro (gemini-2.5-pro) | True | — | 16 | 14 | FAIL | — |
| BM-KB27 | gemini (gemini-2.5-flash) | False | — | 184 | 196 | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got |
| BM-KB27 | gemini-pro (gemini-2.5-pro) | True | — | 165 | 170 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbre |
| BM-MOD-LOVEJOY | gemini (gemini-2.5-flash) | True | — | 2 | 14 | FAIL | — |
| BM-MOD-LOVEJOY | gemini-pro (gemini-2.5-pro) | False | — | — | — | FAIL | YAML parse error: while parsing a block mapping   in "<unicode string>", line 38, column 7:         - segmentId: 1       |
| BM-MOD-JOHNSON | gemini (gemini-2.5-flash) | True | — | 20 | 51 | FAIL | — |
| BM-MOD-JOHNSON | gemini-pro (gemini-2.5-pro) | True | — | 15 | 47 | FAIL | — |
| BM-MOD-DEED | gemini (gemini-2.5-flash) | True | — | 7 | 4 | FAIL | — |
| BM-MOD-DEED | gemini-pro (gemini-2.5-pro) | True | — | 4 | 1 | FAIL | — |
