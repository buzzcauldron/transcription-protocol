"""Ground-truth strings for automated gate checks (same sources as evaluate.py / evaluate_all.py)."""

from __future__ import annotations

import re

from ._eval_core import strip_tokens

LINCOLN_GT_P1 = """Springfield Aug. 16th 1837
Friend Mary.

You will, no doubt, think it rather strange, that I should write you a letter on the same day on which we parted; and I can only account for it by supposing, that seeing you lately makes me think you of you more than usual, while at our late meeting we had but few expressions of thoughts. You must know that I can not see you, or think of you, with entire indifference; and yet it may be, that you, are mistaken in regard to what my real feelings towards you are. If I knew you were not, I should not trouble you with this letter. Perhaps any other man would know enough without further information; but I consider it my peculiar right to plead ignorance, and your bounden duty to allow the plea. I want in all cases to do right; and most particularly so, in all cases with women. I want, at this particular time, more than any thing else, to do right with you, and if I knew it would be doing right, as I rather suspect it would, to let you alone, I would do it. And for the purpose of making the matter as plain as possible, I now say, that you can now drop the subject, dismiss your thoughts (if you ever had any) from me forever, and leave this letter unanswered, without calling forth one accusing murmer from me. And I will even go further, and say,"""

LINCOLN_GT_P2 = """that if it will add any thing to your comfort, or peace of mind, to do so, it is my sincere wish that you should. Do not understand by this, that I wish to cut your acquaintance. I mean no such thing. What I do wish is, that our further acquaintance shall depend upon yourself. If such further acquaintance would contribute nothing to your happiness, I am sure it would not to mine. If you feel yourself in any degree bound to me, I am now willing to release you, provided you wish it; while, on the other hand, I am willing, and even anxious to bind you faster, if I can be convinced that it will, in any considerable degree, add to your happiness. This, indeed, is the whole question with me. Nothing would make me more miserable than to believe you miserable\u2014 nothing more happy, than to know you were so.

In what I have now said, I think I can not be misunderstood; and to make myself understood, is the only object of this letter.

If it suits you best to not answer this\u2014 farewell\u2014 a long life and a merry one attend you. But if you conclude to write back, speak as plainly as I do. There can be neither harm nor danger, in saying, to me, any thing you think, just in the manner you think it.

My respects to your sister.

Your friend Lincoln"""

MEDIEVAL_GT = (
    "et peperit iniquitatem. Lacum "
    "aperuit et effodit eum. et incidit "
    "in foveam quam fecit. Convertetur "
    "dolor eius in caput eius. et in verticem "
    "ipsius iniquitas eius descendet. Confitebor "
    "Domino secundum iustitiam eius. "
    "et psallam nomini Domini altissimi "
    "Iuste iudex cui cor et renes scrutans Deus. "
    "supra senes te invenit mundo "
    "corde: inpolluta omni sorde. "
    "Domine Dominus noster. quam "
    "admirabile est nomen "
    "tuum in universa terra. Quoniam "
    "elevata est magnificentia tua super "
    "caelos. Ex ore infantium et "
    "lactentium perfecisti laudem. propter "
    "inimicos tuos. ut destruas "
    "inimicum et ultorem. Quoniam videbo "
    "caelos tuos opera digitorum tuorum. "
    "lunam et stellas quae tu fundasti."
)

ABBREV_MAP = {
    "&": "et",
    "eu": "eum",
    "ei": "eius",
    "dno": "Domino",
    "dns": "Dominus",
    "nr": "noster",
    "dni": "Domini",
    "Dne": "Domine",
    "scdm": "secundum",
    "ds": "Deus",
    "iniqtatem": "iniquitatem",
    "fouea": "foveam",
    "qua": "quam",
    "Conuertet": "Convertetur",
    "ipsi": "ipsius",
    "iniqtas": "iniquitas",
    "iusticia": "iustitiam",
    "psalla": "psallam",
    "tuu": "tuum",
    "uniuisa": "universa",
    "tra": "terra",
    "eleuata": "elevata",
    "e": "est",
    "magnificecia": "magnificentia",
    "infantiu": "infantium",
    "lactenciu": "lactentium",
    "pfecisti": "perfecisti",
    "laude": "laudem",
    "ppter": "propter",
    "imicu": "inimicum",
    "inimicu": "inimicum",
    "ultore": "ultorem",
    "opa": "opera",
    "digitor": "digitorum",
    "tuo": "tuorum",
    "luna": "lunam",
    "inuent": "invenit",
    "uerti": "verti",
    "Co": "Con",
    "uertice": "verticem",
    "Cofitebor": "Confitebor",
}


def normalize_medieval_latin(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = text.replace("ae", "e").replace("oe", "e")
    text = re.sub(r"(?<![a-z])u(?=[aeiou])", "v", text)
    text = text.replace("j", "i")
    return text


def expand_medieval(text: str) -> str:
    text = strip_tokens(text)
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    expanded = []
    skip_next = False
    for i, w in enumerate(words):
        if skip_next:
            skip_next = False
            continue
        clean = w.rstrip(".,:;")
        punct = w[len(clean) :]
        if clean == "Q" and i + 1 < len(words) and words[i + 1].startswith("m"):
            expanded.append("Quoniam" + punct)
            skip_next = True
        elif clean == "su" and i + 1 < len(words) and words[i + 1].startswith("per"):
            expanded.append("super" + punct)
            skip_next = True
        elif clean == "in" and i + 1 < len(words) and words[i + 1].startswith("imicu"):
            expanded.append("inimicum" + punct)
            skip_next = True
        elif clean == "Co" and i + 1 < len(words):
            next_w = words[i + 1]
            expanded.append("Con" + next_w + punct)
            skip_next = True
        elif clean == "uerti" and i + 1 < len(words) and words[i + 1].startswith("ce"):
            expanded.append("verticem" + punct)
            skip_next = True
        elif clean in ("ps", "d", "v", "viii"):
            continue
        elif clean in ABBREV_MAP:
            expanded.append(ABBREV_MAP[clean] + punct)
        else:
            expanded.append(w)
    return " ".join(expanded)
