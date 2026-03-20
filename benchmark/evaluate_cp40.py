#!/usr/bin/env python3
"""
Evaluate CP40.355 AALT 4070 transcription against PAGE XML ground truth.
Computes Character Error Rate (CER) and Word Error Rate (WER).
"""
import re
import sys
import xml.etree.ElementTree as ET


TOKEN_PATTERN = re.compile(
    r'\[(?:illegible|uncertain|gap|damaged|glyph-uncertain|'
    r'deletion|insertion|marginalia|superscript|exp|wrap-join)[^]]*\]'
)


def strip_tokens(text):
    def replace_token(m):
        tok = m.group(0)
        if tok.startswith("[uncertain:"):
            inner = tok[len("[uncertain:"):].rstrip("]").strip()
            return inner.split("/")[0].strip()
        if tok.startswith("[insertion:"):
            inner = tok[len("[insertion:"):].rstrip("]").strip()
            for prefix in ["interlinear: ", 'interlinear: "', "above line: "]:
                if inner.startswith(prefix):
                    inner = inner[len(prefix):]
            return inner.strip('"').strip()
        if tok.startswith("[deletion:"):
            return ""
        if tok.startswith("[marginalia:"):
            return ""
        return ""
    return TOKEN_PATTERN.sub(replace_token, text)


def normalize(text):
    text = strip_tokens(text)
    text = text.replace("=\n", "")
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (c1 != c2)
            ))
        prev = curr
    return prev[-1]


def word_levenshtein(s1_words, s2_words):
    if len(s1_words) < len(s2_words):
        return word_levenshtein(s2_words, s1_words)
    if len(s2_words) == 0:
        return len(s1_words)
    prev = list(range(len(s2_words) + 1))
    for i, w1 in enumerate(s1_words):
        curr = [i + 1]
        for j, w2 in enumerate(s2_words):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (w1 != w2)
            ))
        prev = curr
    return prev[-1]


def extract_ground_truth_from_xml(xml_path):
    ns = {'page': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    lines = []
    for text_line in root.findall('.//page:TextLine', ns):
        text_equiv = text_line.find('page:TextEquiv/page:Unicode', ns)
        if text_equiv is not None and text_equiv.text:
            lines.append(text_equiv.text.strip())
    return lines


def main():
    xml_path = sys.argv[1] if len(sys.argv) > 1 else \
        "/Users/halxiii/Library/CloudStorage/Dropbox/Transcriptions/Done lines/CP40.355.AALT.4070.xml"

    gt_lines = extract_ground_truth_from_xml(xml_path)
    gt_full = ' '.join(gt_lines)
    gt_norm = normalize(gt_full)

    # Transcription from protocol run (segments concatenated)
    tr_segments = [
        'Cornubie  ¶Radulphus Baro Stafford summonitus fuit ad respondendum domino Regi de placito quod permittat ipsum presentare',
        '[insertion: interlinear: "de"]',
        'idoneam personam ad ecclesiam de Suthill que vacat et ad suam spectat donacionem etc Et unde',
        'Johannes de Clone qui sequitur pro domino Rege dicit quod quidam Thomas Corbet fuit seisitus de manerio de Calyngton',
        'cum pertinenenciis ad quod advocatio ecclisie predicte pertinet tempore pacis tempore Henrici Regis proavi domini Regis nunc et eandem ecclesiam presen',
        '[insertion: interlinear: "ad"]',
        'tavit quendam Johannem de Bradelegh clericum suum qui ad presentationem suam fuit admissus et institutus tempore pacis',
        'tempore eiusdem domini Regis [uncertain: henricum / Henrici] etc et de ipse Thoma descendit manerium predictum ad quod etc cuidam Petro ut filio et heredi etc',
        'Qui quidem Petrus manerium predictum ad quod etc dedit cuidam Roberto de Stafford in liberum maritagium cum Amicia sorore',
        'eiusdem Petri per quod donum iidem Robertus et Amicia fuerunt seisiti de manerio etc ad quod etc per formam etc tempore pacis',
        'tempore Edwardi Regis avi domini Regis nunc et de ipsis Roberto et Amicia descendit manerium ad quod etc cuidam Nicholao ut',
        'filio et heredi etc qui quidem Nicholaus tunc infra etatem fuit et quia predictus Robertus pater tenuit manerium de Stafford',
        'cum pertinenciis de ipso Rege avo etc per baroniam etc idem Rex avus etc post mortem predictorum Roberti et Amicie seisivit in',
        '[insertion: interlinear: "et aliis advocationibus etc ratione minoris etatis euisdem Nicholai una cum custodia euisdem Nicholai"]',
        'manuum suam predictum manerium de Stafford una cum advocatione predicta  post quam quidem seisinam ipso Nicholao filio',
        '[insertion: interlinear: "presentandi"]',
        'Roberti infra etatem existente predicta ecclesia vacavit per mortem predicti Johannis de Bradelegh per quod ius accrevit',
        'ipsi Regi avo etc ut in iure ipsius Nicholai ratione minoris etatis eiusdem Nicholai etc et de ipso Rege avo etc',
        'descendit ius etc cuidam Edwardo ut filio et heredi etc Et de ipso Edwardo ipsi domino Regi nunc ut filium',
        'et hereditum etc Et ea ratione pertinent ad ipsum dominum Regem nunc ad ecclesiam predictam ad presens presentare predictus',
        'Radulphus ipsum inuste impedit ad dampnum ipsius Radulphi mille Librarum Et hoc offert verificare pro domino Rege etc',
        'Et Radulphus per Gilbertum de [uncertain: Berdefeld / Berdesfeld] attornatum suum venit et defendit vim et iniuriam quando etc Et dicit quod',
        'ipse non potest dedicere [uncertain: quim / quin] ad predictum dominum Regem nunc hac sola vice pertineat ad ecclesiam predictam',
        'presentare prout predictus Johannes qui sequitur etc superius versus eum pro domino Rege narravit set dicit quod ipse',
        'non impedivit ipsum dominum Regem presentare ad ecclesiam predictam Et de hoc ponit se super patriam Et Johannes',
        'qui sequitur etc Similiter Ideo consideratum est quod dominus Rex recuperet versus eum presentationem suam ad ecclesiam predictam',
        'et habeat breve Episcopo Exonie loci Diocesano quod non obstante reclamatione ipsius Radulphi ad presentationem ipsius domini',
        'Regis ad ecclesiam predictam idoneam personam admittat Nihil de misericordia ipsius Radulphi quia venit primo die etc Et',
        'preceptum est [uncertain: vicecomites / vicecomiti] quod venire faciat hic in Octabis Sancti Michaelis XII etc per quos etc Et qui predictum Radulphum',
        'nulla etc ad recognoscendum etc Quia tam etc',
    ]

    tr_full = ' '.join(tr_segments)
    tr_norm = normalize(tr_full)

    gt_chars = gt_norm
    tr_chars = tr_norm
    gt_words = gt_norm.split()
    tr_words = tr_norm.split()

    char_edit = levenshtein(gt_chars, tr_chars)
    word_edit = word_levenshtein(gt_words, tr_words)

    cer = char_edit / len(gt_chars) * 100 if gt_chars else 0
    wer = word_edit / len(gt_words) * 100 if gt_words else 0

    print("=" * 72)
    print("BENCHMARK: BM-MED-002 — CP40.355 AALT 4070 (Plea Roll)")
    print("14th-century English legal hand | lat-Latn | medieval")
    print("=" * 72)
    print()
    print("--- CHARACTER ERROR RATE (CER) ---")
    print(f"Ground truth chars:    {len(gt_chars)}")
    print(f"Transcription chars:   {len(tr_chars)}")
    print(f"Edit distance (chars): {char_edit}")
    print(f"CER:                   {cer:.2f}%")
    print()
    print("--- WORD ERROR RATE (WER) ---")
    print(f"Ground truth words:    {len(gt_words)}")
    print(f"Transcription words:   {len(tr_words)}")
    print(f"Edit distance (words): {word_edit}")
    print(f"WER:                   {wer:.2f}%")
    print()

    # Find word-level differences
    from difflib import SequenceMatcher
    sm = SequenceMatcher(None, gt_words, tr_words)
    additions, omissions, substitutions = [], [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'insert':
            additions.extend(tr_words[j1:j2])
        elif op == 'delete':
            omissions.extend(gt_words[i1:i2])
        elif op == 'replace':
            for k in range(max(i2 - i1, j2 - j1)):
                gt_w = gt_words[i1 + k] if i1 + k < i2 else ""
                tr_w = tr_words[j1 + k] if j1 + k < j2 else ""
                if gt_w and tr_w:
                    substitutions.append((gt_w, tr_w))
                elif gt_w:
                    omissions.append(gt_w)
                else:
                    additions.append(tr_w)

    print("--- WORD-LEVEL DIFFERENCES ---")
    print(f"Substitutions:         {len(substitutions)}")
    for gt_w, tr_w in substitutions:
        print(f"  '{gt_w}' → '{tr_w}'")
    print(f"Additions:             {len(additions)}")
    for w in additions:
        print(f"  + '{w}'")
    print(f"Omissions:             {len(omissions)}")
    for w in omissions:
        print(f"  - '{w}'")
    print()

    # Fabricated content check
    fabricated = [w for w in additions if w.lower() not in
                  {'et', 'de', 'ad', 'in', 'etc', 'quod', 'qui', 'per'}]
    print("--- ZERO-ADDITION CHECK ---")
    if not fabricated and not additions:
        print("  PASS — no fabricated content")
    elif additions:
        print(f"  {len(additions)} word(s) added (check if structural, not fabricated)")
        for w in additions:
            print(f"    + '{w}'")
    print()

    # Disposition
    if cer < 1.0 and wer < 2.0:
        disposition = "PASS"
    elif cer < 3.0 and wer < 5.0:
        disposition = "CONDITIONAL_PASS"
    else:
        disposition = "FAIL"

    print(f"DISPOSITION:           {disposition}")
    print()
    print("=" * 72)

    return 0 if disposition != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
