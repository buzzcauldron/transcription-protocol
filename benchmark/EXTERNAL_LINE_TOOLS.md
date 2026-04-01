# External line tools and `lineRange`

This protocol expects each segment to declare **`lineRange`** (e.g. `"3-8"`) and **`pageNumber`** on [`transcriptionOutput`](../transcription-output-schema-v1.1.0.md). Researchers sometimes use **third-party line detectors** to propose line boundaries before transcribing under the protocol. This note clarifies what is compatible and what is not.

## Compatible use: line structure only

Tools that output **line geometry**, **line order**, or **line IDs** (often after cropping a page image) can inform how you **split segments** and **number lines** in YAML. Workflow sketch:

1. Run the external tool through **line identification** (and manual **line editing** if needed).
2. Optionally **export** a lines file if the tool offers one (e.g. PageXML-oriented download/upload).
3. Transcribe the **same crop or page** using this protocol ([`prompt-templates-v1.1.0.md`](../prompt-templates-v1.1.0.md)); produce **`segments[].text`** only from that process.
4. Set **`lineRange`** (and segment boundaries) to **match** the line groups you are accounting for, consistent with the tool’s line count and reading order where you rely on it.

The [schema validator](validate_schema.py) does **not** ingest PageXML or vendor line files; `lineRange` remains a **string convention** you maintain.

**Optional XML check:** [`validate_lines_xml.py`](validate_lines_xml.py) verifies that a downloaded file is **well-formed XML** and counts **PAGE-style** `TextLine` (and `TextRegion` / `Line`) elements using **namespace-agnostic** tags — useful before you rely on line counts for `lineRange`. It does **not** run full PAGE XML **XSD** validation. For transcript YAML, still use `validate_schema.py`.

## Incompatible use: vendor text as ground truth

Do **not** treat machine **extracted**, **spell-checked**, **corrected**, or **translated** text from an external line/OCR pipeline as the **canonical** diplomatic transcript for this protocol unless you **re-derive** that text under [`diplomatic-transcription-protocol-v1.1.0.md`](../diplomatic-transcription-protocol-v1.1.0.md) (no silent additions, explicit uncertainty, etc.).

If a tool’s default output uses **silent abbreviation expansion**, **readable normalization**, or steps that **do not refer back to the manuscript**, that output is **not** interchangeable with protocol-compliant `segments[].text` without a full rework.

## Example: [Glyph Machina](https://glyphmachina.com/)

Glyph Machina is a **Latin**-oriented workflow with **Identify Lines**, **Edit Lines**, and **Download Lines File** / **Upload Lines File** (PageXML-oriented). **Extract Text** is the step that **refers directly to the manuscript**; optional later steps described on their site (**spell and grammar check**, **Modern English**) **do not** refer back to the manuscript.

**Lineation-only use (recommended if you use it at all):** complete line detection (and export lines if useful), then transcribe under this protocol elsewhere; **skip** or **ignore** Glyph Machina’s extracted text for your authoritative YAML. Their line model is aimed at the hands and period they describe—**quality still depends on crop and image quality**, like any detector.

## Summary

| Artifact | Role in this protocol |
| -------- | --------------------- |
| Line boundaries, counts, order, optional lines export | **OK** as **prior structure** for `lineRange` / segmentation |
| Vendor OCR / “readable” / spell-checked / translated text | **Not** canonical `segments[].text` without full protocol re-transcription |
