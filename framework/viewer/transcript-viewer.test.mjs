import assert from "node:assert/strict";
import test from "node:test";
import {
  linesFromSegment,
  normalizeConfidence,
} from "./transcript-viewer.js";

test("normalizeConfidence maps schema values and unknown", () => {
  assert.equal(normalizeConfidence("high"), "high");
  assert.equal(normalizeConfidence("MEDIUM"), "medium");
  assert.equal(normalizeConfidence(" low "), "low");
  assert.equal(normalizeConfidence(""), "unknown");
  assert.equal(normalizeConfidence(null), "unknown");
  assert.equal(normalizeConfidence("bogus"), "unknown");
});

test("linesFromSegment uses segment confidence for each split line", () => {
  const rows = linesFromSegment({
    text: "a\nb\n",
    confidence: "low",
  });
  assert.equal(rows.length, 3);
  assert.deepEqual(
    rows.map((r) => r.confidence),
    ["low", "low", "low"]
  );
});

test("linesFromSegment uses lineConfidences when lengths match", () => {
  const rows = linesFromSegment({
    text: "one\ntwo",
    confidence: "high",
    lineConfidences: ["medium", "low"],
  });
  assert.equal(rows.length, 2);
  assert.equal(rows[0].confidence, "medium");
  assert.equal(rows[1].confidence, "low");
});

test("lineConfidences ignored when length mismatch", () => {
  const rows = linesFromSegment({
    text: "a\nb",
    confidence: "high",
    lineConfidences: ["low"],
  });
  assert.equal(rows[0].confidence, "high");
  assert.equal(rows[1].confidence, "high");
});

test("long single line preserves text and confidence", () => {
  const long = "word ".repeat(500).trim();
  const rows = linesFromSegment({
    text: long,
    confidence: "medium",
  });
  assert.equal(rows.length, 1);
  assert.equal(rows[0].text, long);
  assert.equal(rows[0].confidence, "medium");
});
