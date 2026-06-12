import re
from google.cloud import vision
from pycparser import parse_file

client = vision.ImageAnnotatorClient()


def extract_id_fields(image_bytes: bytes) -> dict:
    """
    :param image_bytes:
    :return:
    Send image to Google Cloud Vision, parse the raw OCR text
    into structured identity fields. Returns a dict ready to
    save into VerifiedIdentity.
    """

    image = vision.Image(content=image_bytes)
    response = client.document_text_detection(image=image)
    if response.error.message:
        raise ValueError(response.error.message)

    raw = response.full_text_annotation.text if response.full_text_annotation else ""

    fields = parse_fields(raw)

    fields["raw_text"] = raw
    fields["confidence"] = score_confidece(fields)
    fields["status"] = "verified" if fields["confidence"] >= 0.75 else "review"
    return fields


def parse_fields(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return {
        "full_name": find_name(lines),
        "date_of_birth": find_date(text, ["birth", "dob", "born", "የተወለዱበት"]),
        "id_number": find_id_number(text),
        "nationality": find_keyword_next(lines, ["nationality", "ዜግነት"]),
        "issuing_country": find_keyword_next(lines, ["country", "issued by"]),
        "region_country": find_region_country(text),
        "region_state": find_keyword_next(lines, ["region", "state", "ክልል", "province"]),
        "region_city": find_keyword_next(lines, ["city", "district", "woreda", "ወረዳ", "kebele", "ቀበሌ", "zone"]),
    }


def find_name(lines: list) -> str | None:
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in ["name", "full name", "ስም", "surname"]):
            if i + 1 < len(lines):
                candidate = lines[i + 1]
                if len(candidate) > 3 and candidate[0].isupper():
                    return candidate
    for line in lines[:8]:
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
            return line
    return None


def find_date(text, keywords):
    pattern = r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{2}[\/\-\.]\d{2})\b'
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            snippet = text[idx: idx + 60]
            m = re.search(pattern, snippet)
            if m:
                return normalize_date(m.group())
    return None


def normalize_date(raw: str) -> str:
    """Try to return YYYY-MM-DD, pass through if unparseable."""
    from datetime import datetime
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    return raw


def find_id_number(text: str) -> str | None:
    # Common ID number patterns: 6-12 alphanumeric, often labelled
    m = re.search(r'(?:no|number|id|passport)[^\w]*([A-Z0-9]{6,12})', text, re.IGNORECASE)
    if m:
        return m.group(1)
    # fallback: standalone alphanumeric block
    m = re.search(r'\b([A-Z]{1,3}[0-9]{6,9})\b', text)
    return m.group(1) if m else None


def find_keyword_next(lines: list, keywords: list) -> str | None:
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in keywords):
            # value might be on same line after a colon
            if ':' in line:
                val = line.split(':', 1)[1].strip()
                if val:
                    return val
            if i + 1 < len(lines):
                return lines[i + 1]
    return None


def find_region_country(text: str) -> str | None:
    countries = ["ethiopia", "kenya", "uganda", "tanzania", "somalia",
                 "eritrea", "sudan", "south sudan", "djibouti"]
    lower = text.lower()
    for c in countries:
        if c in lower:
            return c.title()
    return None


def score_confidence(fields: dict) -> float:
    """Simple heuristic: ratio of non-null core fields."""
    core = ["full_name", "date_of_birth", "id_number", "nationality"]
    filled = sum(1 for k in core if fields.get(k))
    return round(filled / len(core), 2)
