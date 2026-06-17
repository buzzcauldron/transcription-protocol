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

# Expanded Vulgate reference (abbreviations resolved); scored expansion-to-expansion.
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

# ── KB27.335 AALT 0235 (King's Bench plea roll, c.1340 legal anglicana) ──
# Expanded PAGE XML (nw-page-editor): abbreviations resolved, scribal spellings preserved.
# Firewalled: used only by the legal evaluator, never supplied to the model.
KB27_GT = (
    "Londinia Dominus Rex per Johannem de Lincoln qui sequitur pro eo optulit se quarto die versus Magistrum Robertum de Thresk "
    "de placito quare cum de iure et sedem legem et consuetudinem regni Regis nunc Anglie omnia terras et tenementibus et redditus ac "
    "advocationes ecclesticarum et aliorum beneficiorum ecclesiasticarum quoruscumque que de domino Rege tenentur in capite sine licencia "
    "Regis alienata in manum Regis capi et penes Rege remanere debeant predictus Robertus ius corone et Regie "
    "dignitatus Regis iniens enervare se in ecclesiam de Northflete vacantem et ad Regis donacionem spectantem ratione "
    "alienacionis advocationis ecclesie illius que quidem advocato de domino Rege tenetur in capite sine licencia Regis "
    "per Johannem Archiepiscopum Cantuarie facte et quam etiam advocationem ea de causa in manum suam capi fecit Rex "
    "vi et armis est ingressus et sic in eadem ad huc se tenet et quam pluries bullas et brevas domino Regi "
    "et regno Regis preiudicialies infra idem regnum detulit et in dies deferre fecit et diversos processus super "
    "eiusdem bullis et lettris per callidas machinationes infra idem regnum prosequitur sum effectum in Regis contempto "
    "et iacitiram multiplice ac iurium corone et Regie dignitatis Regis predictorum exheredationem manifestam et contra "
    "pacem Regis Et ipse non venit et preceptum fuit vicecomiti sicut pluries quod caperet eum etc Et vicecomites "
    "retornavit quod non est inventus etc ideo preceptum est vicecomiti sicut pluries quod capiat eum si inventus etc Et "
    "salvo etc Ita quod habeant corporus eius coram domino Rege a die Pasche in xv dies ubicumque etc"
)

# ── Donne → Egerton (early modern secretary hand, 1602), Folger MS L.b.534, leaf 1 recto ──
# Ground truth: EMMO diplomatic transcription (CC BY-SA 4.0), letter body only.
# Firewalled: used only by the early-modern evaluator, never supplied to the model.
# ── LOC By the People transcripts (firewalled; modern English, minimal damage) ──

# mal.3010000 — Owen Lovejoy to John G. Nicolay, 2 Feb 1864 (Joliet postmaster)
LOVEJOY_GT = (
    "Washington D.C. February 2nd 1864 Friend Nicolay: I understand the President "
    "has removed the Post Master at Joliet, Ill. Will you ask him if he can "
    "consistently suspend the matter for a few days till I can see him? "
    "I hope to be on my pegs again shortly. Yours Truly Owen Lovejoy pv H. C. V. "
    "Col. Nicolay Executive Mansion Washington D.C. Hon. O. Lovejoy About Joliet "
    "Post Office Feb 2 1864"
)

# mal.3030000 — Reverdy Johnson to Abraham Lincoln, 8 Feb 1864 (Waring pardon inquiry)
JOHNSON_GT = (
    "Senate Chamber 8 Feby '64 My dear Sir, Do me the favor to let me know by return "
    "of the messenger whether the pardon of J S Waring of Md has issued? His members "
    "of our Legislature who petition you on the subject, are very desirous of knowing. "
    "Yrs trule repy Reverdy Johnson The President. Reverdy Johnson Washington Feb. 8, 1864 "
    "Inquiries about the case of Waring"
)

# mal.4095900 — A. S. H. White to John G. Nicolay, 27 Feb 1865 (Indian deeds for approval)
DEED_WHITE_GT = (
    "Department of the Interior, Washington, Feby 27, 1865 Jno. G. Nicolay Esq Dear Sir, "
    "Herewith please find two Indian Deeds for the President's approval. The Secretary "
    "directs me to inquire if the two deeds sent up on the 17th ultimo have been "
    "approved by the president? If so, that they be returned. They are deeds of "
    "Virginia Grignon, and of Geo. Culver guardian for minor heirs of Antoine Grignon; "
    "Winnebago Indians. Respectfully yours A. S. H. White"
)

# ── London, Canada West, 3 Sep 1854 (Scottish emigrant letter) ──────────────
# Human GT (researcher's transcription, page 1 only).
# Uncertain readings: "Bessie's" or "Jessie's" (name); "Grey" at end (user marked [Grey?]).
# Confirmed: "orry" (Scottish dialect, quoted in letter).
# Confirmed: "Fenton Barns, viz the Whiteheads" (plural); "settle at Detroit";
# "introductory letters" (model reading accepted; image too low-res to adjudicate
# vs "introductions, letters").
LONDON_CW_1854_GT = (
    "London C.W. 3 September 1854 "
    "My Dear George, I suppose I should begin this letter in the usual way by making an apology "
    "for delaying so long in writing you. Your letter of 19 June was duly received and today we had "
    "the pleasure of receiving your letter of the 14th ult by which we are glad to see that Isabella "
    "the children and yourself are in the enjoyment of good health and that things are all prospering "
    "at Fenton Barns. We were glad to receive Bessie's letter for Jane and I am happy to hear that "
    "my Dear Sister continues well and seems to enjoy herself. We have had a great time here with the "
    "arrival of the immigrants, from Fenton Barns, viz the Whiteheads. Andrew made his appearance first, "
    "having left his Father and Mother & sister along with Jack at some outlandish French settlement in "
    "Lower Canada. We told him he had better get his folks out of there; but before Andrew's letter "
    "reach'd Lower Canada the family had left for Upper Canada. Andrew is engaged as a Porter in our "
    "Hardware Store and seems to do well and is considered a good specimen of Fenton Barn raising. "
    "One of the girls Helen has been engaged by my wife for the kitchen and the other is with Jane. "
    "They appear to be good active girls and please well. The old man is working \"orry\" in this Town. "
    "The old woman regrets that she ever left Fenton Barns, but will get over it. Of course the young "
    "people have a far better chance to improve their circumstances in Canada than in Scotland. "
    "Mr. Falkner was here. He stayed over Saturday and Sunday and he spent the Sunday evening at our "
    "house. I would take him to be, as you remark, changeable. He had made up his mind to settle at "
    "Detroit amongst the Yankees, altho' I told him I thought he would be more comfortable amongst his "
    "own people in Canada. He was well fortified with all sorts of introductory letters, amongst "
    "others, one from Sir Geo. Grey to"
)

DONNE_GT = (
    "The honorable fauor that yr lp hath afforded me, in allowinge me the liberty of myne own Chamber, "
    "hath giuen me leaue so much to respect and loue my self, that now I can desire to be well. And "
    "therfore, for health, not pleasure, (of wch yr lps displeasure hath dulld in me all tast and ap=prehension) "
    "I humbly beseeche yr lp, so much more to slacken my fetters, that as I ame by yr lps fa=uor, myne own "
    "keeper, and Surety, so I may be myne owne phisician and Apothecary: wch yr lp shall worke, yf yow graunt me "
    "Liberty to take the Ayre, about this Towne. The whole world ys a streight Imprisonmt to me, whilst I ame barrd "
    "yr lps sight. But this fauor may lengthen and better my lyfe, wch I desire to prserve, onely in hope to "
    "redeeme by my sorrowe, and desire to do yr lp Seruice, my Offence past. Allmighty godd well euer in yr ls "
    "hart, and fill yt wth good desires, and graunt them. Yor lps poorest seruant I: Donne"
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
