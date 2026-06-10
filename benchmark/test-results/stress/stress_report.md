# Stress test compatibility matrix

Generated: 2026-06-10T14:28:33Z (UTC)

| Case | Model | Schema OK | Additions | Omissions | Disposition | Score | Notes |
|------|-------|-----------|-----------|------------|-------------|-------|-------|
| BM-MOD-LOVEJOY | gemini (gemini-2.5-flash) | False | 2 | 14 | FAIL | 0.0 | segment 1 position invalid: got 'address', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MOD-LOVEJOY | gemini-pro (gemini-2.5-pro) | False | — | — | FAIL | — | YAML parse error: while parsing a block mapping
  in "<unicode string>", line 38, column 7:
        - segmentId: 1
          ^
expected <block end>, but found '<block mapping start>'
  in "<unicode string>", line 45, column 9:
            Friend Nicolay:
            ^ |
| BM-MOD-JOHNSON | gemini (gemini-2.5-flash) | False | 20 | 51 | FAIL | 0.0 | segment 1 position invalid: got 'marginalia', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MOD-JOHNSON | gemini-pro (gemini-2.5-pro) | True | 15 | 47 | FAIL | 0.0 | — |
| BM-MOD-DEED | gemini (gemini-2.5-flash) | False | 7 | 4 | FAIL | 0.0 | segment 1 position invalid: got 'marginalia', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
| BM-MOD-DEED | gemini-pro (gemini-2.5-pro) | False | 4 | 1 | FAIL | 0.05 | segment 1 position invalid: got 'bottom_left_corner', expected one of ('body', 'header', 'footer', 'margin_left', 'margin_right', 'margin_top', 'margin_bottom', 'interlinear', 'footnote', 'table_row', 'table_header') |
