# Program Framework Plan

> Automation pipeline for dual-pass transcription, diffing, adjudication, validation, and export.

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          RUN CONFIGURATION                          │
│  targetLanguage, targetEra, diplomaticProfile, diplomaticToggles,   │
│  normalizationMode, sourcePageId, providerAdapter                   │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        1. INGEST & PREPROCESS                       │
│  Accept image files (TIFF, PNG, JPEG, PDF pages).                   │
│  Run resolution/orientation/boundary checks.                        │
│  Assign sourcePageId if not provided.                               │
│  Attach run configuration to job metadata.                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                        ┌────────┴────────┐
                        ▼                 ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  2a. TRANSCRIBER A│  │  2b. TRANSCRIBER B│
          │  (Provider X)     │  │  (Provider Y)     │
          │  Independent run  │  │  Independent run  │
          └────────┬─────────┘  └────────┬──────────┘
                   │                      │
                   └──────────┬───────────┘
                              ▼
          ┌────────────────────────────────────────┐
          │         3. COMPARE & DIFF              │
          │  Segment-level text diff.              │
          │  Flag conflicts (additions, omissions, │
          │  divergent uncertainty tokens).         │
          └────────────────┬───────────────────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
           No conflicts      Conflicts found
                  │                 │
                  ▼                 ▼
    ┌───────────────────┐  ┌────────────────────┐
    │ 4a. ACCEPT AS     │  │ 4b. ADJUDICATE     │
    │ CANONICAL         │  │ (Arbitrator prompt) │
    └────────┬──────────┘  └────────┬───────────┘
             │                      │
             └──────────┬───────────┘
                        ▼
          ┌──────────────────────────────┐
          │    5. VALIDATION GATE        │
          │  Schema check                │
          │  Addition detection          │
          │  Omission detection          │
          │  Uncertainty compliance      │
          │  Diplomatic compliance       │
          │  Language/era consistency     │
          │  Numeric scoring             │
          └──────────────┬───────────────┘
                         │
                ┌────────┴────────┐
                │                 │
             Pass/             Conditional
             Pass              Pass or Fail
                │                 │
                ▼                 ▼
    ┌───────────────────┐  ┌────────────────────┐
    │ 6a. EXPORT        │  │ 6b. HUMAN REVIEW   │
    │ Canonical          │  │ QUEUE              │
    │ transcript +       │  │ (low-confidence    │
    │ uncertainty ledger │  │  or failed checks) │
    └───────────────────┘  └────────────────────┘
```

---

## 2. Pipeline Stages

### 2.1 Ingest and Preprocess

**Inputs**: Image files (TIFF, PNG, JPEG) or PDF with page extraction.

**Operations**:
- Extract individual pages from multi-page documents.
- Run automated image quality checks (resolution DPI threshold, orientation detection, crop-boundary verification).
- Assign or validate `sourcePageId` for each page.
- Build job manifest binding each page to its run configuration.

**Job manifest structure**:
```yaml
job:
  jobId: "uuid"
  createdAt: "ISO-8601"
  configuration:
    targetLanguage: "eng-Latn"
    languageSet: []
    targetEra: "nineteenth_century"
    eraRange: "1840-1860"
    diplomaticProfile: "strict"
    diplomaticToggles:
      preserveLineBreaks: true
      preserveOriginalAbbreviations: true
      markExpansions: false
      captureDeletionsAndInsertions: false
      captureUnclearGlyphShape: true
    normalizationMode: "diplomatic"
    scriptNotes: null
    protocolVersion: "v1.0"
  pages:
    - sourcePageId: "MS-1234-folio-12r"
      filePath: "scans/folio-12r.tiff"
      preCheckResult: null  # populated after preprocess
  providerConfig:
    transcriberA: "claude"
    transcriberB: "openai"
    adjudicator: "claude"
```

**Outputs**: Validated job manifest with `preCheckResult` for each page.

**Abort conditions**: If a page fails resolution, orientation, or boundary checks, it is flagged and excluded from transcription (can be manually overridden).

### 2.2 Dual Transcription

Two independent transcription runs per page, using the Transcriber prompt template.

**Provider routing**: The framework selects which LLM provider to use for each pass from `providerConfig`. Passes must be independent — Transcriber B must not see Transcriber A's output.

**Per-pass output**: A complete transcription document conforming to OUTPUT_SCHEMA.

**Concurrency**: Passes A and B run in parallel. No information flows between them.

### 2.3 Compare and Diff

**Algorithm**:
1. Align segments between Output A and Output B by `segmentId` and `lineRange`.
2. For each aligned segment pair, compute character-level diff.
3. Classify differences:
   - **Text conflict**: Substantive word/character differences.
   - **Token conflict**: Different uncertainty tokens for the same region.
   - **Structural conflict**: Different segmentation or line breaks.
4. Generate a `conflictList` for adjudication.

**Conflict list structure**:
```yaml
conflictList:
  - conflictId: 1
    segmentId: 3
    type: "text_conflict"
    readingA: "proposed meeting"
    readingB: "[uncertain: proposed / postponed] meeting"
    location: "line 4, words 2-3"
  - conflictId: 2
    segmentId: 5
    type: "token_conflict"
    readingA: "[illegible: ~3 words]"
    readingB: "[illegible: ~2 words]"
    location: "line 12, end of line"
```

**No-conflict path**: If the diff produces zero conflicts, the output from Transcriber A is adopted as canonical (since both agree). Proceed directly to validation.

### 2.4 Adjudication

Triggered only when conflicts exist. Uses the Arbitrator prompt template.

**Inputs to Arbitrator**:
- Source image.
- Both transcription outputs.
- The `conflictList`.

**Output**: An `arbitrationReport` resolving each conflict with one of: `ADOPT_A`, `ADOPT_B`, `UNCERTAIN`, `ILLEGIBLE`, `REVISED`.

**Canonical assembly**: The framework merges the arbitrated resolutions into a single canonical transcript. Non-conflicting segments are carried forward unchanged.

### 2.5 Validation Gate

The canonical transcript is evaluated against the full Quality Rubric (see QUALITY_RUBRIC.md).

**Automated checks**:
1. Schema validation (all required fields, controlled vocabulary, format rules).
2. Addition detection (compare against source, flag ungrounded text).
3. Omission detection (segment coverage against image regions).
4. Uncertainty compliance (tokens present where needed, correct types).
5. Diplomatic profile compliance (profile-specific rule checks).
6. Language/era consistency (flag script or vocabulary inconsistent with configuration).
7. Numeric scoring.

**Dispositions**:
- `pass` — zero critical/major failures.
- `conditional_pass` — zero critical, one or more major failures. Routed to human review.
- `fail` — one or more critical failures. Requires re-run or manual correction.

### 2.6 Export

**Pass/conditional_pass outputs**:

```
export/
  {jobId}/
    {sourcePageId}/
      transcript.yaml          # canonical transcript (OUTPUT_SCHEMA format)
      transcript.txt           # plain text extract (diplomatic only)
      normalized.txt           # normalized text (if normalizationMode is "normalized")
      validation_report.yaml   # rubric results, score, disposition
      uncertainty_ledger.yaml  # all uncertainty tokens with locations
      provenance.yaml          # full run config, model IDs, timestamps
      arbitration_report.yaml  # if adjudication was triggered
      source_image_ref.txt     # path/hash of source image
```

**Uncertainty ledger** — a flat list of every uncertainty token in the canonical transcript:
```yaml
uncertaintyLedger:
  - tokenId: 1
    segmentId: 1
    lineNumber: 3
    tokenType: "uncertain"
    tokenText: "[uncertain: proposed / postponed]"
    resolved: false
  - tokenId: 2
    segmentId: 1
    lineNumber: 6
    tokenType: "illegible"
    tokenText: "[illegible: ~3 words]"
    resolved: false
```

### 2.7 Human Review Queue

For `conditional_pass` outputs and `fail` outputs routed for manual recovery:

**Queue entry**:
```yaml
reviewItem:
  jobId: "uuid"
  sourcePageId: "MS-1234-folio-12r"
  disposition: "conditional_pass"
  issues:
    - category: "omission"
      severity: "major"
      segmentId: 4
      description: "possible missed word at line 8"
  assignedReviewer: null
  reviewStatus: "pending"  # pending, in_review, approved, rejected
  reviewNotes: null
  signoff:
    reviewer: null
    timestamp: null
```

**Sign-off**: A human reviewer must set `reviewStatus` to `approved` or `rejected` and populate `signoff` for the transcript to be marked as final. This metadata is included in the provenance record.

---

## 3. Execution Modes

### 3.1 Chat/Web Mode

For manual use through LLM chat interfaces:

1. User pastes the relevant prompt template (Transcriber, Verifier, or Arbitrator) into the chat.
2. User attaches the source image.
3. User fills in the configuration variables.
4. Model produces the output.
5. User manually runs a second pass (or uses a different chat session) for the verification step.
6. User compares outputs manually or pastes both into an Arbitrator session.

The protocol and templates are self-contained for this workflow. No software is required.

### 3.2 API Mode

For automated pipelines:

1. The framework reads a batch manifest of source images and configurations.
2. For each page, it dispatches two API calls (Transcriber A, Transcriber B) in parallel.
3. It parses the structured outputs, runs the diff algorithm, and dispatches Arbitrator calls for conflicts.
4. It runs the validation gate programmatically.
5. It exports the canonical package and routes failures to the review queue.

**API adapter interface** (see PROVIDER_ADAPTERS.md for vendor details):

```python
class TranscriptionAdapter:
    def transcribe(self, image_path: str, config: RunConfig) -> TranscriptionOutput:
        """Send image + transcriber prompt to LLM API, return parsed output."""

    def verify(self, image_path: str, transcription: TranscriptionOutput, config: RunConfig) -> VerificationReport:
        """Send image + transcription + verifier prompt, return report."""

    def adjudicate(self, image_path: str, output_a: TranscriptionOutput, output_b: TranscriptionOutput, conflicts: ConflictList, config: RunConfig) -> ArbitrationReport:
        """Send image + both outputs + conflict list + arbitrator prompt, return report."""
```

Each provider adapter implements this interface.

---

## 4. Data Flow Summary

```
Source Images
    │
    ▼
Job Manifest (config + pages)
    │
    ├──► Transcriber A ──► Output A ──┐
    │                                  ├──► Diff ──► Conflict List
    └──► Transcriber B ──► Output B ──┘         │
                                          ┌─────┴──────┐
                                     No conflicts    Conflicts
                                          │              │
                                     Adopt A        Arbitrate
                                          │              │
                                          └──────┬───────┘
                                                 │
                                          Canonical Transcript
                                                 │
                                          Validation Gate
                                                 │
                                     ┌───────────┼───────────┐
                                   Pass     Conditional    Fail
                                     │        Pass           │
                                   Export       │         Re-run or
                                     │      Human Review   Manual Fix
                                     │          │
                                     └──────────┘
                                          │
                                   Researcher-Ready Package
```

---

## 5. Configuration Reference

All configuration fields and their validation rules are defined in:
- [ACADEMIC_TRANSCRIPTION_PROTOCOL.md](../ACADEMIC_TRANSCRIPTION_PROTOCOL.md) — Section 2.
- [OUTPUT_SCHEMA.md](../OUTPUT_SCHEMA.md) — Section 2.
- [QUALITY_RUBRIC.md](../QUALITY_RUBRIC.md) — full rubric.
- [PROMPT_TEMPLATES.md](../PROMPT_TEMPLATES.md) — template variables.
- [skill/PROVIDER_ADAPTERS.md](../skill/PROVIDER_ADAPTERS.md) — API mappings.
