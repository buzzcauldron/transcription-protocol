# Stress test compatibility matrix

Generated: 2026-06-10T16:02:56Z (UTC)

| Case | Model | Schema OK | Additions | Omissions | Disposition | Score | Notes |
|------|-------|-----------|-----------|------------|-------------|-------|-------|
| BM-001 | anthropic | False | — | — | FAIL | — | ERROR: ANTHROPIC_API_KEY is not set |
| BM-001 | claude-code (claude-code-cli) | False | — | — | FAIL | — | ERROR: Not logged in — run `claude login` in your terminal, then re-run: cd /Users/halxiii/Projects/transcription-protocol && /Users/halxiii/.local/bin/claude -p --add-dir "$(pwd)" --append-system-prompt "$(cat benchmark/test-results/claude-cli/BM-001/system.txt)" "$(cat benchmark/test-results/claude-cli/BM-001/user.txt)" > benchmark/test-results/stress/BM-001/claude-code/response.txt |
| BM-001 | gemini (gemini-2.5-flash) | True | 85 | 65 | FAIL | 0.0 | — |
| BM-001 | gemini-3.5-flash (gemini-3.5-flash) | False | 19 | 32 | FAIL | 0.0 | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None |
| BM-001 | gemini-flash-lite (gemini-2.5-flash-lite) | False | 46 | 303 | FAIL | 0.0 | missing required field: confidence; missing required field: uncertaintyTokenCount; segment 0 confidence invalid: got None, expected one of ('high', 'medium', 'low'); mismatchReport is required when segments is non-empty (protocol 1.1.0 §5.2), unless pass2Summary is present with segmentsAltered: 0; hallucinationAudit is required (protocol §7.4 item 5; hard fail if absent) |
| BM-001 | gemini-pro (gemini-2.5-pro) | True | 31 | 24 | FAIL | 0.0 | — |
| BM-001 | openai | False | — | — | FAIL | — | ERROR: OPENAI_API_KEY is not set |
| BM-001 | shell-computus-gemini (gemini-2.5-pro) | False | — | — | FAIL | — | ERROR: while parsing a block mapping
  in "<unicode string>", line 40, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<scalar>'
  in "<unicode string>", line 46, column 9:
            Springfield Aug. 18th 1837
            ^ |
| BM-001 | shell-full-r5-gemini (gemini-2.5-pro) | False | 29 | 29 | FAIL | 0.0 | segment 1 position invalid: got 'top', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-001 | shell-r2-gemini (gemini-2.5-pro) | False | — | — | FAIL | — | ERROR: while parsing a block mapping
  in "<unicode string>", line 38, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<scalar>'
  in "<unicode string>", line 44, column 9:
            Springfield Aug. 18[superscript: ... 
            ^ |
| BM-001 | shell-r5-gemini (gemini-2.5-pro) | False | 31 | 27 | FAIL | 0.0 | segment 1 position invalid: got 'top-center', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MED-001 | gemini (gemini-2.5-flash) | True | 28 | 25 | FAIL | 0.0 | — |
| BM-MED-001 | gemini-pro (gemini-2.5-pro) | True | 16 | 14 | FAIL | 0.0 | — |
| BM-MED-001 | shell-computus-gemini (gemini-2.5-pro) | True | 31 | 28 | FAIL | 0.0 | — |
| BM-MED-001 | shell-r2-gemini (gemini-2.5-pro) | True | 37 | 31 | FAIL | 0.0 | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MED-001 | shell-r5-gemini (gemini-2.5-pro) | True | 14 | 12 | FAIL | 0.0 | — |
| BM-KB27 | gemini (gemini-2.5-flash) | False | 184 | 196 | FAIL | 0.0 | missing required field: protocolVersion; metadata.protocolVersion must be one of ['1.0.0', '1.1.0', 'v1.0', 'v1.1'], got None Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-KB27 | gemini-pro (gemini-2.5-pro) | True | 165 | 170 | FAIL | 0.0 | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-KB27 | shell-computus-gemini (gemini-2.5-pro) | True | 140 | 193 | FAIL | 0.0 | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-KB27 | shell-full-r2-gemini (gemini-2.5-pro) | True | 185 | 191 | FAIL | 0.0 | — |
| BM-KB27 | shell-r2-gemini (gemini-2.5-pro) | True | 158 | 182 | FAIL | 0.0 | — |
| BM-KB27 | shell-r5-gemini (gemini-2.5-pro) | True | 180 | 198 | FAIL | 0.0 | — |
| BM-MOD-LOVEJOY | gemini (gemini-2.5-flash) | False | 2 | 14 | FAIL | 0.0 | segment 1 position invalid: got 'address', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MOD-LOVEJOY | gemini-pro (gemini-2.5-pro) | False | — | — | FAIL | — | YAML parse error: while parsing a block mapping
  in "<unicode string>", line 38, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<block mapping start>'
  in "<unicode string>", line 45, column 9:
            Friend Nicolay:
            ^ |
| BM-MOD-LOVEJOY | shell-computus-gemini (gemini-2.5-pro) | False | 4 | 13 | FAIL | 0.0 | missing required field: confidence; missing required field: uncertaintyTokenCount; segment 0 confidence invalid: got None, expected one of ('high', 'medium', 'low') Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-LOVEJOY | shell-r2-gemini (gemini-2.5-pro) | False | — | — | FAIL | — | ERROR: while parsing a block mapping
  in "<unicode string>", line 38, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<block mapping start>'
  in "<unicode string>", line 46, column 9:
            Friend Nicolay:
            ^ |
| BM-MOD-LOVEJOY | shell-r5-gemini (gemini-2.5-pro) | True | 3 | 14 | FAIL | 0.0 | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-JOHNSON | gemini (gemini-2.5-flash) | False | 20 | 51 | FAIL | 0.0 | segment 1 position invalid: got 'marginalia', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MOD-JOHNSON | gemini-pro (gemini-2.5-pro) | True | 15 | 47 | FAIL | 0.0 | — |
| BM-MOD-JOHNSON | shell-computus-gemini (gemini-2.5-pro) | True | 22 | 49 | FAIL | 0.0 | — |
| BM-MOD-JOHNSON | shell-r2-gemini (gemini-2.5-pro) | True | 21 | 49 | FAIL | 0.0 | — |
| BM-MOD-JOHNSON | shell-r5-gemini (gemini-2.5-pro) | True | 19 | 46 | FAIL | 0.0 | — |
| BM-MOD-DEED | gemini (gemini-2.5-flash) | False | 7 | 4 | FAIL | 0.0 | segment 1 position invalid: got 'marginalia', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MOD-DEED | gemini-pro (gemini-2.5-pro) | False | 4 | 1 | FAIL | 0.05 | segment 1 position invalid: got 'bottom_left_corner', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MOD-DEED | shell-computus-gemini (gemini-2.5-pro) | True | 5 | 2 | FAIL | 0.0 | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-DEED | shell-full-computus-gemini (gemini-2.5-pro) | True | 5 | 3 | FAIL | 0.0 | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-DEED | shell-r2-gemini (gemini-2.5-pro) | True | 8 | 5 | FAIL | 0.0 | Warnings: suspected overconfidence (soft escalation §7.3–§7.4): multiline body text, conditionNotes suggest damage/abbreviation/difficulty, but zero [uncertain] / [illegible] / [glyph-uncertain] tokens — flag for human review |
| BM-MOD-DEED | shell-r5-gemini (gemini-2.5-pro) | True | 7 | 6 | FAIL | 0.0 | — |
