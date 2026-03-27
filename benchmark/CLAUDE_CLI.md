# Testing with Claude Code CLI (`claude`)

Use this when you want to exercise the **same manifest + system/user zones** as [`stress_run.py`](stress_run.py), but through **Claude Code** on your machine (`claude` in the terminal — typically `~/.local/bin/claude`).

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated (`claude auth` or subscription).
- Repository root as working directory.
- **PyYAML** for the helper (`pip install pyyaml` or your env).

## 1. Build prompts and resolve images

From the repository root:

```bash
python -m benchmark.claude_cli --case BM-001
```

This:

1. Downloads or reuses BM-001 images under `benchmark/images/BM-001/` (same as the API stress harness).
2. Writes `benchmark/test-results/claude-cli/BM-001/system.txt` and `user.txt` (system rules + configuration + OUTPUT FORMAT + image `@` paths).

## 2. Run Claude (non-interactive)

**Option A — helper:**

```bash
python -m benchmark.claude_cli --case BM-001 --exec
```

**Option B — shell (avoids huge argv on some systems by using `cat`):**

```bash
claude -p --add-dir "$(pwd)" \
  --append-system-prompt "$(cat benchmark/test-results/claude-cli/BM-001/system.txt)" \
  "$(cat benchmark/test-results/claude-cli/BM-001/user.txt)"
```

`--add-dir` lets the CLI read project files; the user prompt includes `@/absolute/path/to/page_*.jpg` lines for Claude Code file references (behavior depends on your Claude Code version).

## 3. Score the output

Save the assistant reply to:

`benchmark/test-results/stress/BM-001/claude-code/response.txt`

(You can rename the folder; see [`CURSOR_STRESS.md`](CURSOR_STRESS.md).)

Then:

```bash
python -m benchmark.stress_replay
# or
python -m benchmark.stress_run --replay
```

Same schema gate + ground-truth metrics as other stress runs.

## Notes

- `--exec` passes large strings on the command line; if your OS limits argument length, use **Option B** with `cat` instead.
- Interactive `claude` (no `-p`) also works: start in the repo, paste `user.txt` after attaching the same images from `benchmark/images/...`.
- Optional cases (e.g. BM-MED-001) need local images per [`benchmark/images/README.md`](images/README.md).
