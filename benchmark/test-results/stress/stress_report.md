# Stress test compatibility matrix

Generated: 2026-06-17T13:26:19Z (UTC)

| Case | Model | Schema OK | Accuracy% | Additions | Omissions | Disposition | Notes |
|------|-------|-----------|-----------|-----------|------------|-------------|-------|
| BM-MOD-1854 | gemini-3-pro (gemini-3.1-pro-preview) | True | 97.2% | 11 | 10 | FAIL | — |
| BM-MOD-1854 | gemini-3.5-flash (gemini-3.5-flash) | False | — | — | — | FAIL | YAML parse error: while scanning for the next token
found character '`' that cannot start any token
  in "<unicode string>", line 1, column 26:
    - Let's look at line 20: `to do well & is considered a go ... 
                             ^ |
