#!/usr/bin/env python3
"""
Blind evaluation: KB27.335 AALT 0235 (King's Bench plea roll).
Transcription produced from image alone, compared against PAGE XML ground truth.
"""
import re
import sys
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher


TOKEN_RE = re.compile(
    r'\[(?:illegible|uncertain|gap|damaged|glyph-uncertain|'
    r'deletion|insertion|marginalia|superscript|exp|wrap-join)[^]]*\]'
)


def strip_tokens(text):
    def repl(m):
        tok = m.group(0)
        if tok.startswith("[uncertain:"):
            inner = tok[len("[uncertain:"):].rstrip("]").strip()
            return inner.split("/")[0].strip()
        return ""
    return TOKEN_RE.sub(repl, text)


def normalize(text):
    text = strip_tokens(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for c1 in s1:
        curr = [prev[0] + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def word_lev(a, b):
    if len(a) < len(b):
        return word_lev(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for w1 in a:
        curr = [prev[0] + 1]
        for j, w2 in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (w1 != w2)))
        prev = curr
    return prev[-1]


def extract_gt(xml_path):
    ns = {'p': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
    tree = ET.parse(xml_path)
    lines = []
    for tl in tree.getroot().findall('.//p:TextLine', ns):
        u = tl.find('p:TextEquiv/p:Unicode', ns)
        if u is not None and u.text:
            lines.append(u.text.strip())
    return lines


# ── BLIND TRANSCRIPTION (from image only, before seeing XML) ──────────
BLIND = [
    "Londonia ¶ Dominus Rex per Johannem de Lincolnia qui sequitur pro eo optulit se quarto die versus Magistrum Robertum de Thresk",
    "de placito quare cum de iure et secundum legem et consuetudinem regni Regis nunc Anglie omnia terras et tenementa et redditus ac",
    "advocationes ecclesiasticarum et aliorum beneficiorum ecclesiasticarum quorumcumque que de domino Rege tenentur in capite sine licencia",
    "Regis alienata in manum Regis capi et penes Regem remanere debeant predictus Robertus ius corone et Regie",
    "dignitatis Regis iniens enervare se in ecclesiam de Northflete vacantem et ad Regis donacionem spectantem ratione",
    "alienacionis advocationis ecclesie illius que quidem advocacio de domino Rege tenetur in capite sine licencia Regis",
    "per Johannem Archiepiscopum Cantuarie facte et quam etiam advocationem ea de causa in manum suam capi fecit Rex",
    "vi et armis est ingressus et sic in eadem ad huc se tenet et quam pluries bullas et [uncertain: brevia / brevas] domino Regi",
    "et regno Regis preiudiciales infra idem regnum detulit et in dies deferre fecit et diversos processus super",
    "eiusdem bullis et [uncertain: litteris / lettris] per callidas machinationes infra idem regnum prosequitur sum effectum in Regis contempto",
    "et [uncertain: iacturam / iacitiram] [uncertain: multiplicem / multiplice] ac iurium corone et Regie dignitatis Regis predictorum exheredationem manifestam et contra",
    "pacem Regis Et ipse non venit et preceptum fuit vicecomiti sicut pluries quod caperet eum etc Et vicecomites",
    "retornavit quod non est inventus etc ideo preceptum est vicecomiti sicut pluries quod capiat eum si inventus etc Et",
    "salvo etc Ita quod habeant corpus eius coram domino Rege a die Pasche in xv dies ubicumque etc",
]


def main():
    xml_path = (sys.argv[1] if len(sys.argv) > 1 else
                "/Users/halxiii/Library/CloudStorage/Dropbox/Transcriptions/Done lines/KB27.335.AALT.0235.xml")

    gt_lines = extract_gt(xml_path)
    gt_full = normalize(' '.join(gt_lines))
    tr_full = normalize(' '.join(BLIND))

    gt_w = gt_full.split()
    tr_w = tr_full.split()

    ced = levenshtein(gt_full, tr_full)
    wed = word_lev(gt_w, tr_w)
    cer = ced / len(gt_full) * 100
    wer = wed / len(gt_w) * 100

    print("=" * 72)
    print("BLIND BENCHMARK: KB27.335 AALT 0235 (King's Bench plea roll)")
    print("14th-century legal hand | lat-Latn | medieval")
    print("=" * 72)
    print()
    print(f"CER:  {cer:.2f}%  ({ced} edits / {len(gt_full)} chars)")
    print(f"WER:  {wer:.2f}%  ({wed} edits / {len(gt_w)} words)")
    print()

    sm = SequenceMatcher(None, gt_w, tr_w)
    subs, adds, omits = [], [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'replace':
            for k in range(max(i2 - i1, j2 - j1)):
                gw = gt_w[i1 + k] if i1 + k < i2 else ""
                tw = tr_w[j1 + k] if j1 + k < j2 else ""
                if gw and tw:
                    subs.append((gw, tw))
                elif gw:
                    omits.append(gw)
                else:
                    adds.append(tw)
        elif op == 'insert':
            adds.extend(tr_w[j1:j2])
        elif op == 'delete':
            omits.extend(gt_w[i1:i2])

    print("--- WORD-LEVEL DIFFERENCES ---")
    print(f"Substitutions: {len(subs)}")
    for g, t in subs:
        print(f"  GT '{g}' → TR '{t}'")
    print(f"Additions:     {len(adds)}")
    for w in adds:
        print(f"  + '{w}'")
    print(f"Omissions:     {len(omits)}")
    for w in omits:
        print(f"  - '{w}'")
    print()

    # Classify errors
    normalization_errors = []
    expansion_errors = []
    other_errors = []
    for g, t in subs:
        if g.lower().replace("ti", "ci") == t.lower().replace("ti", "ci"):
            normalization_errors.append((g, t))
        elif len(g) != len(t) and (g[:3] == t[:3] or g[-3:] == t[-3:]):
            expansion_errors.append((g, t))
        else:
            other_errors.append((g, t))

    print("--- ERROR CLASSIFICATION ---")
    print(f"Spelling normalization (LLM corrected scribal Latin): {len(normalization_errors)}")
    for g, t in normalization_errors:
        print(f"  '{g}' → '{t}'")
    print(f"Abbreviation expansion errors: {len(expansion_errors)}")
    for g, t in expansion_errors:
        print(f"  '{g}' → '{t}'")
    print(f"Other: {len(other_errors)}")
    for g, t in other_errors:
        print(f"  '{g}' → '{t}'")

    dispo = "PASS" if cer < 1 and wer < 2 else "CONDITIONAL_PASS" if cer < 3 and wer < 5 else "FAIL"
    print(f"\nDISPOSITION: {dispo}")
    print("=" * 72)
    return 0 if dispo != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
