# Stress test compatibility matrix

Generated: 2026-06-10T19:42:11Z (UTC)

| Case | Model | Schema OK | Accuracy% | Additions | Omissions | Disposition | Notes |
|------|-------|-----------|-----------|-----------|------------|-------------|-------|
| BM-001 | anthropic | False | — | — | — | FAIL | ERROR: ANTHROPIC_API_KEY is not set |
| BM-001 | claude-code (claude-code-cli) | False | — | — | — | FAIL | ERROR: Not logged in — run `claude login` in your terminal, then re-run: cd /Users/halxiii/Projects/transcription-protocol && /Users/halxiii/.local/bin/claude -p --add-dir "$(pwd)" --append-system-prompt "$(cat benchmark/test-results/claude-cli/BM-001/system.txt)" "$(cat benchmark/test-results/claude-cli/BM-001/user.txt)" > benchmark/test-results/stress/BM-001/claude-code/response.txt |
| BM-001 | gemini (gemini-2.5-flash) | True | 86.7% | 85 | 65 | FAIL | — |
| BM-001 | gemini-3.5-flash (gemini-3.5-flash) | False | 93.5% | 19 | 32 | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None |
| BM-001 | gemini-flash-lite (gemini-2.5-flash-lite) | False | 38.2% | 46 | 303 | FAIL | missing required field: confidence; missing required field: uncertaintyTokenCount; segment 0 confidence invalid: got None, expected one of ('high', 'medium', 'low'); mismatchReport is required when segments is non-empty (protocol 1.1.0 §5.2), unless pass2Summary is present with segmentsAltered: 0; hallucinationAudit is required (protocol §7.4 item 5; hard fail if absent) |
| BM-001 | gemini-pro (gemini-2.5-pro) | True | 95.1% | 31 | 24 | FAIL | — |
| BM-001 | openai | False | — | — | — | FAIL | ERROR: OPENAI_API_KEY is not set |
| BM-001 | shell-computus-gemini (gemini-2.5-pro) | False | — | — | — | FAIL | ERROR: while parsing a block mapping
  in "<unicode string>", line 40, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<scalar>'
  in "<unicode string>", line 46, column 9:
            Springfield Aug. 18th 1837
            ^ |
| BM-001 | shell-full-r5-gemini (gemini-2.5-pro) | True | 94.1% | 29 | 29 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-001 | shell-r2-gemini (gemini-2.5-pro) | False | — | — | — | FAIL | ERROR: while parsing a block mapping
  in "<unicode string>", line 38, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<scalar>'
  in "<unicode string>", line 44, column 9:
            Springfield Aug. 18[superscript: ... 
            ^ |
| BM-001 | shell-r5-gemini (gemini-2.5-pro) | True | 94.5% | 31 | 27 | FAIL | — |
| BM-MED-001 | gemini (gemini-2.5-flash) | True | 75.0% | 28 | 25 | FAIL | — |
| BM-MED-001 | gemini-pro (gemini-2.5-pro) | True | 86.0% | 16 | 14 | FAIL | — |
| BM-MED-001 | shell-computus-gemini (gemini-2.5-pro) | True | 72.0% | 31 | 28 | FAIL | — |
| BM-MED-001 | shell-gm-gemini (gemini-2.5-pro) | True | 85.0% | 18 | 15 | FAIL | — |
| BM-MED-001 | shell-r2-gemini (gemini-2.5-pro) | True | 69.0% | 37 | 31 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MED-001 | shell-r5-gemini (gemini-2.5-pro) | True | 88.0% | 14 | 12 | FAIL | — |
| BM-KB27 | gemini (gemini-2.5-flash) | False | 21.3% | 184 | 196 | FAIL | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-KB27 | gemini-pro (gemini-2.5-pro) | True | 31.7% | 165 | 170 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-KB27 | shell-computus-gemini (gemini-2.5-pro) | True | 22.5% | 140 | 193 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-KB27 | shell-full-r2-gemini (gemini-2.5-pro) | True | 23.3% | 185 | 191 | FAIL | — |
| BM-KB27 | shell-gm-gemini (gemini-2.5-pro) | True | 9.2% | 194 | 226 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-KB27 | shell-r2-gemini (gemini-2.5-pro) | True | 26.9% | 158 | 182 | FAIL | — |
| BM-KB27 | shell-r5-gemini (gemini-2.5-pro) | True | 20.5% | 180 | 198 | FAIL | — |
| BM-MOD-LOVEJOY | gemini (gemini-2.5-flash) | True | 81.1% | 2 | 14 | FAIL | — |
| BM-MOD-LOVEJOY | gemini-pro (gemini-2.5-pro) | False | — | — | — | FAIL | YAML parse error: while parsing a block mapping
  in "<unicode string>", line 38, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<block mapping start>'
  in "<unicode string>", line 45, column 9:
            Friend Nicolay:
            ^ |
| BM-MOD-LOVEJOY | shell-computus-gemini (gemini-2.5-pro) | False | 82.4% | 4 | 13 | FAIL | missing required field: confidence; missing required field: uncertaintyTokenCount; segment 0 confidence invalid: got None, expected one of ('high', 'medium', 'low') Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-LOVEJOY | shell-r2-gemini (gemini-2.5-pro) | False | — | — | — | FAIL | ERROR: while parsing a block mapping
  in "<unicode string>", line 38, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<block mapping start>'
  in "<unicode string>", line 46, column 9:
            Friend Nicolay:
            ^ |
| BM-MOD-LOVEJOY | shell-r5-gemini (gemini-2.5-pro) | True | 81.1% | 3 | 14 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-JOHNSON | gemini (gemini-2.5-flash) | True | 23.9% | 20 | 51 | FAIL | — |
| BM-MOD-JOHNSON | gemini-pro (gemini-2.5-pro) | True | 29.9% | 15 | 47 | FAIL | — |
| BM-MOD-JOHNSON | shell-computus-gemini (gemini-2.5-pro) | True | 26.9% | 22 | 49 | FAIL | — |
| BM-MOD-JOHNSON | shell-r2-gemini (gemini-2.5-pro) | True | 26.9% | 21 | 49 | FAIL | — |
| BM-MOD-JOHNSON | shell-r5-gemini (gemini-2.5-pro) | True | 31.3% | 19 | 46 | FAIL | — |
| BM-MOD-DEED | gemini (gemini-2.5-flash) | True | 94.9% | 7 | 4 | FAIL | — |
| BM-MOD-DEED | gemini-pro (gemini-2.5-pro) | True | 98.7% | 4 | 1 | FAIL | — |
| BM-MOD-DEED | shell-computus-gemini (gemini-2.5-pro) | True | 97.4% | 5 | 2 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-DEED | shell-full-computus-gemini (gemini-2.5-pro) | True | 96.2% | 5 | 3 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-DEED | shell-r2-gemini (gemini-2.5-pro) | True | 93.6% | 8 | 5 | FAIL | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-DEED | shell-r5-gemini (gemini-2.5-pro) | True | 92.3% | 7 | 6 | FAIL | — |
