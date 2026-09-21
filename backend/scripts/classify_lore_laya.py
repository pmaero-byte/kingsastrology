#!/usr/bin/env python3
"""
classify_lore_laya.py — classify the practitioner-lore corpus with Laya
(BUILD-TIME ONLY; docs/17 protocol).

The corpus (backend/data/practitioner_lore/corpus.jsonl) holds what practicing
astrologers suggest on forums and remedy portals — harvested from open web
search 2026-09-22. This is LIVING TRADITION, firewalled from the Brihat Jataka
verse store: it is never served as doctrine and never mixed into rule
citations. It is classified here so the court can SEE the living tradition,
organised, with its classical agreement checked.

Protocol (docs/17 §3, adapted for lore):
  Q1  noul x9   "Does this advice concern {graha}?"        -> graha set
  Q2  choice    "What kind of advice is it?" (8 options)   -> kind
  Q3  noul      "Does the advice promise a health/wealth/outcome
                 verdict?"                                 -> ethics flag
  Q4  rule      classical-agreement check against the court's verified
                conventions (day/gem/colour/metal per graha, from Brihat
                Jataka Ch 2 v 5 + Āśvalāyana materials + the Elgods god-planet
                mapping) — deterministic, labelled as such.

Thresholds (calibrated-probability semantics, docs/17 §3.3):
  p >= 0.85 (+ margin >= 0.25 for choice)  -> auto-draft
  0.50 <= p < 0.85                         -> scholar-assist
  p < 0.50                                 -> escalated
  ethics p >= 0.30                         -> always human-reviewed

Engine: tries the real Laya checkpoint (pip install laya). Laya is near-chance
zero-shot on typed decisions until fine-tuned (model card), and this host may
not carry the 421M weights — so a deterministic lexicon engine implements the
identical battery and thresholds, and the manifest records which engine ran.
Nothing is ever auto-verified: these are drafts for the Scholar Reviewer.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LORE_VERSION = "lore-1.0.0"

GRAHAS = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
KINDS = ["mantra", "charity", "gemstone", "behavioral", "ritual", "worship", "technique", "caution"]

# ---- the court's verified conventions (classical layer, not forum lore) ----
# day: weekday of worship convention; gem/metal/colour: Brihat Jataka Ch 2 v 5
# colour words + Āśvalāyanagṛhyapariśiṣṭa 2.3 materials + god-planet mapping.
CONVENTIONS = {
    "Surya":   {"day": ["sunday"], "gem": ["ruby", "manikya"],
                "colour": ["copper", "red", "saffron"], "metal": ["gold", "copper"]},
    "Chandra": {"day": ["monday"], "gem": ["pearl", "moti"],
                "colour": ["white", "silver"], "metal": ["silver"]},
    "Mangala": {"day": ["tuesday"], "gem": ["red coral", "moonga", "coral"],
                "colour": ["red"], "metal": ["copper"]},
    "Budha":   {"day": ["wednesday"], "gem": ["emerald", "panna"],
                "colour": ["green"], "metal": ["gold", "brass"]},
    "Guru":    {"day": ["thursday"], "gem": ["yellow sapphire", "pusparaga", "topaz"],
                "colour": ["yellow"], "metal": ["gold"]},
    "Shukra":  {"day": ["friday"], "gem": ["diamond", "opal", "white sapphire"],
                "colour": ["white", "silver", "variegated"], "metal": ["silver"]},
    "Shani":   {"day": ["saturday"], "gem": ["blue sapphire", "neelam"],
                "colour": ["black", "dark blue"], "metal": ["iron"]},
    "Rahu":    {"day": ["saturday"], "gem": ["hessonite", "gomed"],
                "colour": ["smoky"], "metal": ["iron", "lead"]},
    "Ketu":    {"day": ["tuesday"], "gem": ["cat's eye", "lehsunia", "cats eye"],
                "colour": ["smoky"], "metal": ["iron"]},
}

GRAHA_TOKENS = {
    "Surya": ["sun", "surya", "suryaya", "aditya"], "Chandra": ["moon", "chandra", "chandraya", "soma"],
    "Mangala": ["mars", "mangal", "mangala", "bhaumaya", "kuja"],
    "Budha": ["mercury", "budh", "budha"], "Guru": ["jupiter", "guru", "brihaspati", "gurve"],
    "Shukra": ["venus", "shukra", "shukraya"], "Shani": ["saturn", "shani", "shanaishcharaya"],
    "Rahu": ["rahu", "rahavay"], "Ketu": ["ketu", "ketav"],
}
GRAHA_TOKEN_RE = {g: [re.compile(rf"\b{re.escape(t)}\b", re.I) for t in toks]
                  for g, toks in GRAHA_TOKENS.items()}
KIND_TOKENS = {
    "mantra": ["mantra", "chant", "recite", "stotra", "beej", "gayatri", "jap", "108 times", "hanuman chalisa", "namaha", "namah"],
    "charity": ["donate", "donation", "daan", "dan ", "charity", "feed", "feeding", "give"],
    "gemstone": ["wear", "gemstone", "gem ", "sapphire", "emerald", "pearl", "ruby", "coral", "diamond", "opal", "hessonite", "gomed", "cat's eye", "lehsunia", "moonga", "moti", "panna", "manikya", "stone"],
    "behavioral": ["avoid", "respect", "discipline", "honesty", "humility", "cleanliness",
                   "wake up early", "control anger", "routines", "consistent effort",
                   "keep the teeth", "serve", "service", "seva", "selfless"],
    "ritual": ["fast", "lamp", "light a", "homa", "yagna", "yagya", "puja", "pooja", "arghya", "offer water", "tilak", "moonlight", "silver glass"],
    "worship": ["worship", "lord", "deity", "ganesha", "saraswati", "hanuman", "vishnu", "idol", "blessings", "temple"],
    "technique": ["whose house", "occupies", "dasha", "transit", "strong in the chart", "upaya of the planet"],
    "caution": ["backfire", "without careful testing", "only after consult", "after consulting", "qualified astrologer", "can cause", "widely advised against", "precaution"],
}
ETHICS_TOKENS = ["can cause", "will get", "guarantee", "cure", "job losses", "will become rich",
                 "best way", "will fully", "never fail", "surely"]


def low(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


# ---------------------------------------------------------------- engines
class LexiconEngine:
    """Deterministic typed-decision engine implementing the Laya battery.
    Probabilities are normalised keyword scores; margins follow the same
    accept/assist/escalate contract as docs/17 §3.3."""

    name = "fallback-lexicon-v1"

    def noul(self, text: str, tokens: list[str]) -> float:
        t = low(text)
        hits = sum(1 for k in tokens if k in t)
        if not tokens:
            return 0.0
        return min(0.97, 0.9 if hits else 0.06 * (1 if any(w in t for w in tokens[0]) else 0))

    def noul_contains(self, text: str, tokens) -> float:
        rxs = [t if hasattr(t, "search") else re.compile(rf"\b{re.escape(t)}\b", re.I)
               for t in tokens]
        return 0.95 if any(rx.search(text) for rx in rxs) else 0.04

    def choice(self, text: str, option_tokens: dict[str, list[str]]) -> tuple[str, float, float]:
        t = low(text)
        scores = {opt: sum(t.count(k) for k in toks) for opt, toks in option_tokens.items()}
        best = max(scores.values())
        if best == 0:
            return ("", 0.0, 0.0)
        ordered = sorted(scores.items(), key=lambda kv: -kv[1])
        top, second = ordered[0], ordered[1]
        p = top[1] / (top[1] + 1.0)
        p = min(0.95, 0.55 + 0.4 * (top[1] - 1) / top[1]) if top[1] > 1 else 0.6
        margin = (top[1] - second[1]) / max(1, top[1])
        return (top[0], round(p, 3), round(margin, 3))


class LayaEngine(LexiconEngine):
    """The real checkpoint (convaiinnovations/laya) answering the same typed
    questions. Loaded only if the `laya` package is importable; any failure
    falls back to the lexicon engine (recorded in the manifest)."""

    name = "convaiinnovations/laya"

    def __init__(self):
        import laya  # noqa: F401  (pip install laya)
        self.agent = laya.load("convaiinnovations/laya")

    def _ask(self, question_type: str, text: str, options: list[str] | None):
        q = {"question": text, "answer_type": question_type}
        if options:
            q["options"] = options
        return self.agent.predict({"state": {"text": text}, "questions": [q]})

    def noul_contains(self, text: str, tokens: list[str]) -> float:
        label = " | ".join(tokens[:6])
        res = self._ask("noul", text, None)
        # the Router returns typed answers; we treat the affirmative probability
        p = float(res.get("probability", res.get("p", 0.0)))
        return p if label else p

    def choice(self, text: str, option_tokens: dict[str, list[str]]):
        res = self._ask("choice", text, list(option_tokens.keys()))
        probs = res.get("probabilities", res) if isinstance(res, dict) else {}
        if not isinstance(probs, dict) or not probs:
            return ("", 0.0, 0.0)
        ordered = sorted(probs.items(), key=lambda kv: -float(kv[1]))
        return (ordered[0][0], round(float(ordered[0][1]), 3),
                round(float(ordered[0][1]) - float(ordered[1][1]), 3)
                if len(ordered) > 1 else 1.0)


def load_engine():
    if "--laya" in sys.argv:
        try:
            eng = LayaEngine()
            print("[engine] real Laya checkpoint loaded")
            return eng
        except Exception as e:  # noqa: BLE001 — recorded honestly, not silent
            print(f"[engine] Laya unavailable ({type(e).__name__}: {e}) — "
                  f"falling back to the deterministic lexicon engine")
    return LexiconEngine()


# ---------------------------------------------------------------- agreement
def convention_check(text: str, grahas: list[str]) -> dict:
    """Deterministic cross-check of a lore entry against the court's verified
    conventions. Verdicts: consistent | partial | contradicts | no-basis."""
    t = low(text)
    hits, misses = [], []
    for g in grahas:
        conv = CONVENTIONS.get(g)
        if not conv:
            continue
        for axis, words in conv.items():
            present = [w for w in words if w in t]
            if present:
                hits.append({"graha": g, "axis": axis, "matched": present})
    # contradictions: a gem/colour/day named in the text but belonging to a
    # DIFFERENT graha than the entry's grahas
    for g, conv in CONVENTIONS.items():
        if g in grahas:
            continue
        for axis in ("gem", "day"):
            if any(w in t for w in conv[axis]) and axis in ("gem",):
                misses.append({"axis": axis, "belongs_to": g})
    verdict = "no-basis"
    if misses:
        verdict = "contradicts"
    elif hits:
        verdict = "consistent" if len(hits) >= 1 else "partial"
    return {"verdict": verdict, "hits": hits, "misses": misses,
            "method": "deterministic rule over verified conventions "
                      "(BJ Ch 2 v 5 colour verse + Āśvalāyana materials + "
                      "god-planet mapping)"}


# ---------------------------------------------------------------- classify
def status_of(p: float, margin: float | None) -> str:
    if p >= 0.85 and (margin is None or margin >= 0.25):
        return "auto-draft"
    if p >= 0.50:
        return "scholar-assist"
    return "escalated"


def classify(entry: dict, eng) -> dict:
    text = entry["text"]
    # Q1 — graha battery (noul per graha)
    grahas = []
    for g in GRAHAS:
        p = eng.noul_contains(text, GRAHA_TOKEN_RE[g])
        if p >= 0.50:
            grahas.append({"graha": g, "p": round(p, 3)})
    graha_names = [x["graha"] for x in grahas] or ["general"]
    # Q2 — kind (choice, with margin)
    kind, p_kind, margin = eng.choice(text, KIND_TOKENS)
    kind_status = status_of(p_kind, margin) if kind else "escalated"
    if not kind:
        kind = "unclassified"
    # Q3 — ethics (noul, conservative threshold)
    p_ethics = eng.noul_contains(text, ETHICS_TOKENS)
    ethics = {"p": round(p_ethics, 3),
              "flag": p_ethics >= 0.30,
              "basis": "outcome/health/wealth guarantee language"}
    # Q4 — classical agreement (deterministic)
    agreement = convention_check(text, graha_names)
    return {
        **entry,
        "classification": {
            "grahas": grahas if grahas else [{"graha": "general", "p": 0.0}],
            "kind": kind, "kind_p": p_kind, "kind_margin": margin,
            "kind_status": kind_status,
            "ethics": ethics,
            "classical_agreement": agreement,
            "status": "scholar-assist" if (ethics["flag"] or kind_status == "escalated")
                      else kind_status,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(ROOT / "backend/data/practitioner_lore/corpus.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "backend/data/practitioner_lore"))
    ap.add_argument("--laya", action="store_true",
                    help="attempt the real convaiinnovations/laya checkpoint")
    args = ap.parse_args()

    entries = [json.loads(line) for line in Path(args.corpus).read_text().splitlines() if line.strip()]
    eng = load_engine()
    classified = [classify(e, eng) for e in entries]

    by_graha: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    by_agreement: dict[str, int] = {}
    flagged = escalated = 0
    for c in classified:
        cl = c["classification"]
        for g in cl["grahas"]:
            by_graha[g["graha"]] = by_graha.get(g["graha"], 0) + 1
        by_kind[cl["kind"]] = by_kind.get(cl["kind"], 0) + 1
        v = cl["classical_agreement"]["verdict"]
        by_agreement[v] = by_agreement.get(v, 0) + 1
        flagged += 1 if cl["ethics"]["flag"] else 0
        escalated += 1 if cl["status"] == "escalated" else 0

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "classified.json").write_text(
        json.dumps({"version": LORE_VERSION, "entries": classified}, ensure_ascii=False, indent=1) + "\n")
    manifest = {
        "lore_version": LORE_VERSION,
        "corpus": "open-forum / practitioner harvest, 2026-09-22 (Reddit consensus, "
                  "Quora-equivalent answer pages, astrologer sites, remedy portals; "
                  "see per-entry sources)",
        "engine": eng.name,
        "engine_note": "the real Laya checkpoint is near-chance zero-shot until fine-tuned "
                       "(model card); the lexicon engine implements the identical typed battery "
                       "and thresholds deterministically",
        "counts": {"entries": len(classified), "ethics_flagged": flagged, "escalated": escalated},
        "by_graha": by_graha, "by_kind": by_kind, "by_agreement": by_agreement,
        "firewall": "practitioner lore is LIVING TRADITION: it never enters the verse store, "
                    "never cites as doctrine, never renders in readings. Classification exists "
                    "so the court can see the tradition organised and its classical agreement "
                    "checked. All entries await Scholar Reviewer triage.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")

    print(f"engine: {eng.name}")
    print(f"entries: {len(classified)}  flagged: {flagged}  escalated: {escalated}")
    print("by graha:", json.dumps(by_graha, ensure_ascii=False))
    print("by kind:", json.dumps(by_kind, ensure_ascii=False))
    print("classical agreement:", json.dumps(by_agreement, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
