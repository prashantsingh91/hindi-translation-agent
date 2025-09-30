#!/usr/bin/env python3
import csv
import sys
import re
from pathlib import Path


OVERRIDES = {
    # Exact lab_name → corrected hindi_name
    "CHC HARAIYA  (AZAMGARH)": "सामुदायिक स्वास्थ्य केंद्र, हरैया, आजमगढ़",
    "chc-hariya": "सामुदायिक स्वास्थ्य केंद्र, हरिया",
    "chc-parshurampur": "सामुदायिक स्वास्थ्य केंद्र, परशुरामपुर",
    "CHC Martinganj  (Azamgarh)": "सामुदायिक स्वास्थ्य केंद्र, मार्टिंगंज, आजमगढ़",
    "CHC Kushalgaon (Azamgarh)": "सामुदायिक स्वास्थ्य केंद्र, कुशलगांव, आजमगढ़",
    "CHC Sahaswan (BADAUN)": "सामुदायिक स्वास्थ्य केंद्र, सहसवान, बदायूं",
    "CHC UJHANI  (BADAUN)": "सामुदायिक स्वास्थ्य केंद्र, उझानी, बदायूं",
    "CHA BARSANA (MATHURA)": "सामुदायिक स्वास्थ्य केंद्र, बरसाना, मथुरा",
    "CHC MEERGANJ (BAREILLY)": "सामुदायिक स्वास्थ्य केंद्र, मीरगंज, बरेली",
    "CHC BHAMORA (BAREILLY)": "सामुदायिक स्वास्थ्य केंद्र, भमोरा, बरेली",
    "CHC PHOOL BEHAD (LAKHIMPUR KHEERI)": "सामुदायिक स्वास्थ्य केंद्र, फूल बेहड़, लखीमपुर खीरी",
    "CHC MIRZAPUR (AZAMGARH)": "सामुदायिक स्वास्थ्य केंद्र, मिर्ज़ापुर, आजमगढ़",
}

# Flexible pattern overrides: (compiled_pattern, replacement)
PATTERN_OVERRIDES = [
    (
        re.compile(r"^\s*CHC\s+HARAIYA\s*\(\s*AZAMGARH\s*\)\s*$", re.IGNORECASE),
        "सामुदायिक स्वास्थ्य केंद्र, हरैया, आजमगढ़",
    ),
]


def apply_overrides(path: Path) -> int:
    tmp = path.with_suffix(path.suffix + ".over.tmp")
    changed = 0
    with path.open("r", encoding="utf-8", newline="") as f_in, tmp.open(
        "w", encoding="utf-8", newline=""
    ) as f_out:
        r = csv.DictReader(f_in)
        fieldnames = r.fieldnames
        if not fieldnames or "lab_name" not in fieldnames or "hindi_name" not in fieldnames:
            raise SystemExit("CSV must have lab_name and hindi_name columns")
        w = csv.DictWriter(f_out, fieldnames=fieldnames)
        w.writeheader()
        for row in r:
            lab = row.get("lab_name", "")
            if lab in OVERRIDES:
                row["hindi_name"] = OVERRIDES[lab]
                changed += 1
            else:
                for pat, repl in PATTERN_OVERRIDES:
                    if pat.match(lab or ""):
                        row["hindi_name"] = repl
                        changed += 1
                        break
            w.writerow(row)
    tmp.replace(path)
    return changed


def main():
    if len(sys.argv) != 2:
        print("Usage: set_hindi_from_labname_overrides.py /absolute/path/to/file.csv")
        sys.exit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)
    n = apply_overrides(p)
    print(f"Updated {n} rows")


if __name__ == "__main__":
    main()


