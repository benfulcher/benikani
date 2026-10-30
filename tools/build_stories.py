"""Build stories.json (bundled stories) from tools/stories_src.txt, checking every kanji against a known-kanji list.

Usage:  python3 tools/build_stories.py [known_kanji.txt]
The known list defaults to tools/known_kanji.txt (one string of kanji, a snapshot of the WaniKani sync).
Fails loudly on any kanji outside the list, an unannotated token containing kanji, or a wrong reading equal to the right one.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "stories_src.txt"
KNOWN = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tools" / "known_kanji.txt"
OUT = ROOT / "stories.json"

KANJI = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
TOKEN = re.compile(r"^(?P<t>[^\[\]]+)\[(?P<r>[^|\]]+)\|(?P<d>[^\]]*)\]$")

known = set(KNOWN.read_text(encoding="utf-8").strip())

# surface -> (meaning, [wrong, wrong]) for the meaning quiz
MEANINGS = ROOT / "tools" / "meanings.txt"
meanings = {}
for raw in MEANINGS.read_text(encoding="utf-8").splitlines():
    if not raw.strip() or raw.startswith("#"):
        continue
    surface, meaning, wrong = [x.strip() for x in raw.split("\t")]
    meanings[surface] = (meaning, [w.strip() for w in wrong.split(";")])

stories, errors = [], []
story = None
new_para = False

for n, raw in enumerate(SRC.read_text(encoding="utf-8").splitlines(), 1):
    line = raw.strip()
    if not line or (line.startswith("#") and not line.startswith("# b")):
        continue
    if line.startswith("# "):
        sid, jp, en, length = [x.strip() for x in line[2:].split("|")]
        story = {"id": sid, "title": {"jp": jp, "en": en}, "length": length, "sentences": []}
        stories.append(story)
        for c in KANJI.findall(jp):
            if c not in known:
                errors.append(f"line {n}: title kanji {c} not known")
        new_para = False
        continue
    if line == "¶":
        new_para = True
        continue
    if " // " not in line:
        errors.append(f"line {n}: missing ' // ' English")
        continue
    jp_part, en = line.split(" // ", 1)
    tokens = []
    for tok in jp_part.split(" "):
        if not tok:
            continue
        m = TOKEN.match(tok)
        if m:
            t, r, d = m.group("t"), m.group("r"), [x for x in m.group("d").split(",") if x]
            if not KANJI.search(t):
                errors.append(f"line {n}: annotated token {t} has no kanji")
            if len(d) != 2 or r in d or len(set(d)) != 2:
                errors.append(f"line {n}: token {t} needs two distinct wrong readings different from {r} (got {d})")
            for c in KANJI.findall(t):
                if c not in known:
                    errors.append(f"line {n}: kanji {c} in {t} not known")
            if t in meanings:
                m, md = meanings[t]
                if len(md) != 2 or m in md:
                    errors.append(f"line {n}: meanings for {t} need two distinct wrong meanings (got {md})")
                tokens.append({"t": t, "r": r, "d": d, "m": m, "md": md})
            else:
                errors.append(f"line {n}: no meaning for {t} in tools/meanings.txt")
                tokens.append({"t": t, "r": r, "d": d})
        else:
            if KANJI.search(tok):
                errors.append(f"line {n}: token {tok} has kanji but no reading")
            if "[" in tok or "]" in tok:
                errors.append(f"line {n}: malformed token {tok}")
            tokens.append({"t": tok, "r": "", "d": []})
    story["sentences"].append({"tokens": tokens, "en": en.strip(), "np": new_para})
    new_para = False

if errors:
    print("\n".join(errors))
    sys.exit(1)

LEVEL, MIN_STAGE = 17, 5  # the WaniKani level and SRS stage the known-kanji snapshot was taken at (2026-10-30)

for s in stories:
    s["bundled"] = True
    s["model"] = "Claude (bundled)"
    s["createdAt"] = "2026-10-30T12:00:00+11:00"
    s["level"], s["minStage"] = LEVEL, MIN_STAGE
    kanji = {c for sent in s["sentences"] for tok in sent["tokens"] for c in KANJI.findall(tok["t"])}
    s["unknown"] = sorted(c for c in kanji if c not in known)
    s["usage"] = None
    s["quiz"] = None
    targets = sum(1 for sent in s["sentences"] for tok in sent["tokens"] if tok["r"])
    print(f"{s['id']}  {s['title']['jp']}  {len(s['sentences'])} sentences, {len(kanji)} kanji, {targets} quiz words")

OUT.write_text(json.dumps({"stories": stories}, ensure_ascii=False, indent=0), encoding="utf-8")
print("wrote", OUT, f"({OUT.stat().st_size // 1024} KB)")
