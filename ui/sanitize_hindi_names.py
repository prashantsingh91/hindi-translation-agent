#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path


LATIN_PATTERN = re.compile(r"[A-Za-z]+(?:[\-\/'\.\(\)\s]*[A-Za-z]+)*")
MULTISPACE = re.compile(r"\s+")


def strip_latin(text: str) -> str:
    if text is None:
        return text
    # Remove latin sequences
    cleaned = LATIN_PATTERN.sub("", text)
    # Normalize various stray ascii commas/quotes around Hindi text
    cleaned = cleaned.replace("\"", "\"")
    cleaned = cleaned.replace(",", ",")
    # Collapse repeated commas and spaces
    cleaned = re.sub(r"\s*,\s*", ", ", cleaned)
    cleaned = re.sub(r"(\s*,\s*){2,}", ", ", cleaned)
    cleaned = MULTISPACE.sub(" ", cleaned).strip()
    # Remove accidental duplicate place names concatenated without separators like 'अलीगढ़अलीगढ़'
    cleaned = re.sub(r"(\S{2,})\1", r"\1", cleaned)
    return cleaned


def sanitize_csv(path: Path) -> None:
    tmp_path = path.with_suffix(path.suffix + ".sanitized.tmp")
    with path.open("r", newline="", encoding="utf-8") as f_in, tmp_path.open(
        "w", newline="", encoding="utf-8"
    ) as f_out:
        reader = csv.DictReader(f_in, restkey="_extra", restval="")
        fieldnames = reader.fieldnames
        if not fieldnames or "hindi_name" not in fieldnames:
            raise SystemExit("Expected column 'hindi_name' in CSV header")
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            # Fold any extra columns (caused by unquoted commas) into hindi_name
            extras = row.pop("_extra", None)
            if extras:
                tail = ",".join(extras)
                if row.get("hindi_name"):
                    row["hindi_name"] = f"{row['hindi_name']},{tail}"
                else:
                    row["hindi_name"] = tail
            original = row.get("hindi_name", "")
            row["hindi_name"] = strip_latin(original)
            writer.writerow(row)
    tmp_path.replace(path)


def sanitize_lines_as_fallback(path: Path) -> None:
    """
    Fallback pass for malformed rows: operate line-wise, preserving the first field
    verbatim and cleaning everything after the first comma as hindi_name.
    """
    tmp_path = path.with_suffix(path.suffix + ".fallback.tmp")
    with path.open("r", encoding="utf-8") as f_in, tmp_path.open(
        "w", encoding="utf-8"
    ) as f_out:
        header = f_in.readline()
        f_out.write(header)
        for line in f_in:
            if "," not in line:
                f_out.write(line)
                continue
            lab, rest = line.split(",", 1)
            # Remove any trailing newline to process cleanly
            rest_clean = strip_latin(rest.rstrip("\n\r"))
            f_out.write(f"{lab},{rest_clean}\n")


def enforce_two_columns(path: Path) -> None:
    """
    Rewrites the file to exactly two columns: lab_name,hindi_name
    - lab_name preserved verbatim (everything before first comma)
    - hindi_name is everything after the first comma with Latin removed
    - all rows are quoted to ensure embedded commas are safe
    """
    tmp_path = path.with_suffix(path.suffix + ".2cols.tmp")
    with path.open("r", encoding="utf-8", newline="") as f_in, tmp_path.open(
        "w", encoding="utf-8", newline=""
    ) as f_out:
        writer = csv.writer(
            f_out,
            quoting=csv.QUOTE_ALL,
            quotechar='"',
            lineterminator='\n',
        )
        # Read raw header line
        header_line = f_in.readline()
        # Always force canonical header
        writer.writerow(["lab_name", "hindi_name"])
        for raw in f_in:
            raw = raw.rstrip("\n\r")
            if not raw:
                continue
            if "," in raw:
                lab, rest = raw.split(",", 1)
            else:
                lab, rest = raw, ""
            hindi = strip_latin(rest)
            writer.writerow([lab, hindi])
    # Atomically replace original file
    tmp_path.replace(path)


def main():
    if len(sys.argv) != 2:
        print("Usage: sanitize_hindi_names.py /absolute/path/to/file.csv")
        sys.exit(1)
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"File not found: {target}")
        sys.exit(1)
    sanitize_csv(target)


if __name__ == "__main__":
    main()


