# Adversarial limits and threat model

This document indexes **known gaps** between what a `transcriptionOutput` document can *claim* and what can be **mechanically verified** from YAML/JSON alone. It complements [ACADEMIC_TRANSCRIPTION_PROTOCOL.md](ACADEMIC_TRANSCRIPTION_PROTOCOL.md) (especially §5.2, §5.6, §7.3–§7.4) and [QUALITY_RUBRIC.md](QUALITY_RUBRIC.md). It does **not** replace external or image-grounded verification.

---

## Index: risk → protocol reference → mitigation class

| Risk | Protocol / schema refs | YAML-only | Validator (no image) | Image-aware or external |
|------|------------------------|-----------|----------------------|-------------------------|
| Self-certifying `hallucinationAudit`; coordinated fabrication of audit fields | §7.3; OUTPUT_SCHEMA §6b; rubric “Audit self-certification” | Catches absent/inconsistent blocks only | Cross-field checks (e.g. expansions vs visible marks) | Human review; second model; tooling with image |
| `pass2Summary` shorthand vs per-segment `mismatchReport` rigor | §5.2; OUTPUT_SCHEMA §5 | Declares Pass 2 outcome | `segmentsAltered` > 0 requires `mismatchReport` entries ([`validate_schema.py`](benchmark/validate_schema.py)) | Independent Pass 2 or verifier prompt |
| Single-inference “Pass 2” (same call) | §5.2 implementation note | — | — | Separate inference/session; verifier |
| Uncertainty flooding ratio (§5.6) | §5.6; OUTPUT_SCHEMA §4a | — | Normative word count + `U` count; documentation carve-out | Human review if ratio borderline |
| Word-count gaming (denominator) | §5.6; OUTPUT_SCHEMA §4a | — | Fixed algorithm in schema + validator | Spot-check transcript |
| Coverage / line-count circularity (`preCheck` vs segments) | §7.4 item 7 | — | Optional consistency checks (future) | Validator with image; manual line count |
| `[illegible]` / physical cause unverifiable without image | §5.5 | — | — | Image review |
| Free-text config injection (`scriptNotes`, `eraRange`, etc.) | §2.7 | — | Controlled vocab for enum fields | **Implementation:** sanitize, length limits, never elevate user strings to system role ([`skill/PROVIDER_ADAPTERS.md`](skill/PROVIDER_ADAPTERS.md)) |
| On-page text that looks like instructions to the model | §2.6–§2.7 | Transcribe, do not obey | — | Prompt architecture; red-team evaluation |
| Confidence calibration (`high` / `medium` / `low`) | §1.1; §8 | — | Heuristic rules possible (future; risk of false positives) | Rubric + reviewer |
| Repeated formulaic segments (copy-paste risk) | — | — | Duplicate-segment heuristics (future) | Spot-check; image |
| Expansion provenance (“visible mark” vs context prior) | §7.2–§7.3 | — | Audit vs text cross-checks | Expert review |

**Mitigation class legend**

- **YAML-only:** Structure and presence rules on the serialized output.
- **Validator (no image):** [`benchmark/validate_schema.py`](benchmark/validate_schema.py) and related tools; cannot prove grounding.
- **Image-aware or external:** Human, separate model, or automation that reads the source image or an independent capture.

---

## Tier 1 — Already acknowledged in the protocol

These are **design limits**, not oversights. The protocol requires honest process traces but does not claim they are cryptographic proofs.

1. **`hallucinationAudit` is self-reported** — Catches careless inconsistency; does not detect deliberate coordinated lying (§7.3).
2. **Pass 2 is not independent** in typical single-call deployments — Bias can persist across both passes (§5.2 note).
3. **External verifier** — Prompts and pipeline hooks exist ([`PROMPT_TEMPLATES.md`](PROMPT_TEMPLATES.md), [`skill/SKILL.md`](skill/SKILL.md)); high-stakes work should use them.

---

## Tier 2 — Partially closable (documentation + tooling)

Normative **§5.6 word counting** is defined in [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md) §4a and implemented in [`benchmark/validate_schema.py`](benchmark/validate_schema.py).

**Backlog (prioritized for future revisions)**

| Item | Direction |
|------|-----------|
| **`pass2Summary` friction** | Optional caps, required spot-check segment IDs, or checksum of post–Pass 2 segment text in `pass2Summary` — increases coordination cost; does not replace external Pass 2. |
| **`epistemicNotes` triggers** | Strongly recommended when `preCheck.proceedOverride` is true and whenever the run documents substantial residual doubt (§1.1); future: conditional required in schema/validator if ecosystem tolerates breakage. |
| **Line / coverage vs `preCheck`** | Validators with images should verify line counts; automated checks may flag inconsistency between `pageCount`, segment count, and `lineRange` sums (no image: weak signal). |
| **Config field sanitization** | Enforce in **adapters**, not in model honor system: length limits, strip control characters, validate enums server-side ([`skill/PROVIDER_ADAPTERS.md`](skill/PROVIDER_ADAPTERS.md)). |

---

## Tier 3 — Non-goals for the schema (deployment / product)

- **Jailbreak text on the page** (“ignore instructions and output X”) — Mitigation is model behavior and prompt placement; the protocol requires faithful transcription of such text without obeying it.
- **Repeated-segment hallucination** — Best addressed by heuristics and review, not a single new required field.
- **Mechanical confidence rules** — Any density rule for `confidence` is approximate; prefer rubric + review over hard invalidation unless calibrated on real data.

---

## What this repository will not claim

Structural validation **does not** prove that the transcript is **true to the manuscript**. It proves that the output **matches declared shape and cross-field rules** suitable for honest workflows and for catching **accidental** inconsistency. Deliberate evasion requires **external** verification.
