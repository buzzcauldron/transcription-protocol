# Stress test compatibility matrix

Generated: 2026-03-26T19:22:49Z (UTC)

| Case | Model | Schema OK | Additions | Omissions | Disposition | Score | Notes |
|------|-------|-----------|-----------|------------|-------------|-------|-------|
| BM-001 | anthropic (claude-sonnet-4-20250514) | False | — | — | FAIL | — | API error: ANTHROPIC_API_KEY is not set |
| BM-001 | openai (gpt-4o) | False | — | — | FAIL | — | API error: OPENAI_API_KEY is not set |
| BM-001 | gemini (gemini-2.0-flash) | False | — | — | FAIL | — | API error: GOOGLE_API_KEY is not set |
