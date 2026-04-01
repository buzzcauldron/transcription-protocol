# Red-team log: BM-001 × Claude Code CLI

See [`benchmark/RED_TEAM_NO_HALLUCINATION.md`](../RED_TEAM_NO_HALLUCINATION.md) for the zero-addition gate and attack patterns.

## Run metadata

- **case_id:** BM-001
- **model:** claude-code (local `claude` CLI)
- **schema_ok:** false (no successful model output in this environment — see below)
- **addition_count:** —
- **omission_count:** —
- **disposition:** FAIL (blocked before transcript)
- **evidence:** Claude Code reported not logged in; response file uses `ERROR:` prefix for `stress_replay`.
- **reviewer_note:** After `claude login`, re-run the flow in [`benchmark/CLAUDE_CLI.md`](../CLAUDE_CLI.md). Save raw assistant output to `benchmark/test-results/stress/BM-001/claude-code/response.txt`, then `python -m benchmark.stress_replay --cases BM-001`. Pass the red-team gate only if **addition_count = 0** vs the source image or ground truth.

## Commands executed (repo root)

1. `python -m benchmark.claude_cli --case BM-001` — wrote `benchmark/test-results/claude-cli/BM-001/system.txt` and `user.txt`; images at `benchmark/images/BM-001/page_*.jpg`.
2. Attempted `claude -p` with append-system-prompt + user text — failed: not logged in.
3. `python -m benchmark.stress_replay --cases BM-001` — refreshed `benchmark/test-results/stress/stress_report.md` and `stress_results.json`.

## Adoption gate (pending local auth)

- [ ] `claude login` on the machine that runs the CLI.
- [ ] Replace `response.txt` with the full assistant reply (valid YAML containing `transcriptionOutput`).
- [ ] Re-run `stress_replay`; require `schema_ok: true` and **addition_count: 0** for anti-fabrication sign-off.
