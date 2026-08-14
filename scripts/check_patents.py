#!/usr/bin/env python3
"""Fail if bio.html's patent list and data.json disagree.

The patent count on this site drifted once already, because the same list was
maintained by hand in bio.html and in data.json. Run this after editing either.

    python3 scripts/check_patents.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GRANTED_RE = re.compile(r"US (\d{1,2},\d{3},\d{3})")
PENDING_RE = re.compile(r"US app\. (\d{2}/\d{3},\d{3})")


def main():
    bio = open(os.path.join(ROOT, "bio.html"), encoding="utf-8").read()
    section = bio.split("<h3>Patents</h3>", 1)
    if len(section) != 2:
        sys.exit("bio.html: no <h3>Patents</h3> section")
    section = section[1].split("<h3>", 1)[0]

    bio_granted = set(GRANTED_RE.findall(section))
    bio_pending = set(PENDING_RE.findall(section))

    data = json.load(open(os.path.join(ROOT, "data.json"), encoding="utf-8"))
    pubs = [p for p in data["publications"] if p.get("type") == "patent"]
    json_granted = set()
    json_pending = set()
    for p in pubs:
        venue = p.get("venue") or ""
        if "pending" in venue:
            json_pending |= set(PENDING_RE.findall(venue))
        elif "granted" in venue:
            json_granted |= set(GRANTED_RE.findall(venue))

    problems = []
    if bio_granted != json_granted:
        problems.append(f"granted only in bio.html:  {sorted(bio_granted - json_granted)}\n"
                        f"granted only in data.json: {sorted(json_granted - bio_granted)}")
    if bio_pending != json_pending:
        problems.append(f"pending only in bio.html:  {sorted(bio_pending - json_pending)}\n"
                        f"pending only in data.json: {sorted(json_pending - bio_pending)}")

    heading_granted = re.search(r"Granted US patents \((\d+)\)", bio)
    if heading_granted and int(heading_granted.group(1)) != len(bio_granted):
        problems.append(f"bio.html heading says {heading_granted.group(1)} granted patents "
                        f"but lists {len(bio_granted)}")
    heading_pending = re.search(r"Patent applications \((\d+), pending\)", bio)
    if heading_pending and int(heading_pending.group(1)) != len(bio_pending):
        problems.append(f"bio.html heading says {heading_pending.group(1)} pending applications "
                        f"but lists {len(bio_pending)}")

    if problems:
        print("PATENT DRIFT DETECTED\n")
        print("\n\n".join(problems))
        sys.exit(1)

    print(f"OK: {len(bio_granted)} granted, {len(bio_pending)} pending, "
          f"consistent between bio.html and data.json")


if __name__ == "__main__":
    main()
