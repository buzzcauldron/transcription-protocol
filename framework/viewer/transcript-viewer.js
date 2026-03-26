/**
 * Per-line confidence from OUTPUT_SCHEMA segments:
 * - Default: each line (split of segment.text on newlines) uses segment.confidence.
 * - Optional: segment.lineConfidences (same length as lines) overrides per line
 *   when present (forward-compatible if the schema gains per-line scores later).
 */

const VALID_BUCKETS = new Set(["high", "medium", "low"]);

/**
 * @param {unknown} raw
 * @returns {"high"|"medium"|"low"|"unknown"}
 */
export function normalizeConfidence(raw) {
  if (typeof raw !== "string") return "unknown";
  const k = raw.trim().toLowerCase();
  if (VALID_BUCKETS.has(k)) return /** @type {"high"|"medium"|"low"} */ (k);
  return "unknown";
}

/**
 * @param {{ text?: string, confidence?: string, lineConfidences?: unknown }} segment
 * @returns {Array<{ text: string, confidence: "high"|"medium"|"low"|"unknown" }>}
 */
export function linesFromSegment(segment) {
  const text = typeof segment.text === "string" ? segment.text : "";
  const lines = text.split("\n");
  const segBucket = normalizeConfidence(segment.confidence);
  const perLine = segment.lineConfidences;

  if (Array.isArray(perLine) && perLine.length === lines.length) {
    return lines.map((line, i) => ({
      text: line,
      confidence: normalizeConfidence(perLine[i]),
    }));
  }

  return lines.map((line) => ({
    text: line,
    confidence: segBucket,
  }));
}

/**
 * @param {unknown} data
 * @returns {{ segments: Array<Record<string, unknown>> } | null}
 */
function getRoot(data) {
  if (!data || typeof data !== "object") return null;
  const o = /** @type {Record<string, unknown>} */ (data);
  if (o.transcriptionOutput && typeof o.transcriptionOutput === "object") {
    const inner = /** @type {Record<string, unknown>} */ (o.transcriptionOutput);
    if (Array.isArray(inner.segments)) return { segments: /** @type {Array<Record<string, unknown>>} */ (inner.segments) };
  }
  if (Array.isArray(o.segments)) return { segments: /** @type {Array<Record<string, unknown>>} */ (o.segments) };
  return null;
}

/**
 * @param {unknown} data
 * @returns {DocumentFragment}
 */
export function renderTranscriptionView(data) {
  const frag = document.createDocumentFragment();
  const root = getRoot(data);
  if (!root) {
    const p = document.createElement("p");
    p.className = "tv-error";
    p.textContent =
      "Could not find transcription data: expected transcriptionOutput.segments or top-level segments.";
    frag.appendChild(p);
    return frag;
  }

  const segments = root.segments;
  if (segments.length === 0) {
    const p = document.createElement("p");
    p.className = "tv-empty";
    p.textContent = "No segments to display.";
    frag.appendChild(p);
    return frag;
  }

  let globalLine = 0;
  for (let s = 0; s < segments.length; s++) {
    const seg = segments[s];
    if (!seg || typeof seg !== "object") continue;

    const section = document.createElement("section");
    section.className = "tv-segment";

    const sid = seg.segmentId != null ? String(seg.segmentId) : String(s + 1);
    const pos = typeof seg.position === "string" ? seg.position : "";
    const lr = typeof seg.lineRange === "string" ? seg.lineRange : "";
    const meta = document.createElement("div");
    meta.className = "tv-segment-meta";
    meta.textContent = [lr && `MS lines ${lr}`, pos && `· ${pos}`, `segment ${sid}`]
      .filter(Boolean)
      .join(" ");
    section.appendChild(meta);

    const lineRows = linesFromSegment(seg);
    const ul = document.createElement("ul");
    ul.className = "tv-lines";
    ul.setAttribute("role", "list");

    for (let i = 0; i < lineRows.length; i++) {
      globalLine += 1;
      const { text, confidence } = lineRows[i];
      const li = document.createElement("li");
      li.className = "tv-line";
      li.setAttribute("dir", "auto");
      li.setAttribute("role", "listitem");
      li.dataset.confidence = confidence;
      const label = `Transcript line ${globalLine}, ${confidence} confidence`;
      li.setAttribute("aria-label", label);
      li.title = `${confidence.charAt(0).toUpperCase() + confidence.slice(1)} confidence`;
      li.tabIndex = 0;
      li.textContent = text.length === 0 ? "\u00a0" : text;
      ul.appendChild(li);
    }

    section.appendChild(ul);
    frag.appendChild(section);
  }

  return frag;
}

/**
 * @param {string} jsonText
 * @returns {{ ok: true, data: unknown } | { ok: false, error: string }}
 */
export function parseJson(jsonText) {
  try {
    const data = JSON.parse(jsonText);
    return { ok: true, data };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { ok: false, error: msg };
  }
}
