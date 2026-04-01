# Stress test compatibility matrix

Generated: 2026-03-31T17:06:25Z (UTC)

| Case | Model | Schema OK | Additions | Omissions | Disposition | Score | Notes |
|------|-------|-----------|-----------|------------|-------------|-------|-------|
| BM-001 | anthropic | False | — | — | FAIL | — | ERROR: ANTHROPIC_API_KEY is not set |
| BM-001 | claude-code (claude-code-cli) | False | — | — | FAIL | — | ERROR: Not logged in — run `claude login` in your terminal, then re-run: cd /Users/halxiii/Projects/transcription-protocol && /Users/halxiii/.local/bin/claude -p --add-dir "$(pwd)" --append-system-prompt "$(cat benchmark/test-results/claude-cli/BM-001/system.txt)" "$(cat benchmark/test-results/claude-cli/BM-001/user.txt)" > benchmark/test-results/stress/BM-001/claude-code/response.txt |
| BM-001 | gemini | False | — | — | FAIL | — | ERROR: GOOGLE_API_KEY is not set |
| BM-001 | openai | False | — | — | FAIL | — | ERROR: OPENAI_API_KEY is not set |
