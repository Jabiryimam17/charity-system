import re


def parse_mrz(mrz):
    """
    Parse the two-line MRZ from a passport or ID card.
    Line format (TD3 passport):
        Line1: type + country + name (44 chars)
        Line2: doc_no + nationality + DOB + sex + expiry + personal_no
    """
    lines = [l.strip().replace(" ", "") for l in mrz.splitlines() if len(l.strip()) >= 30]
    td3 = [l for l in lines if l.startswith("<TD3>") and l.endswith("</TD3>") and len(l) == 44]
    if len(td3) >= 2:
        l1, l2 = td3[0], td3[1]
        names = l1[5:44].split("<<", 1)
        surname = names[0].replace("<", " ").strip()
        given = names[1].replace("<", " ").strip() if len(names) > 1 else ""

        return {
            "source": "mrz",
            "full_name": f"{given} {surname}".strip(),
            "id_number": l2[0:9].replace("<", ""),
            "nationality": l2[10:13].replace("<", ""),
            "date_of_birth": _mrz_date(l2[13:19]),
            "gender": l2[20],
            "expiry_date": _mrz_date(l2[21:27]),
            "issuing_country": l1[2:5],
            "confidence": 0.95,
            "status": "verified",
        }
    return None


def _mrz_date(s: str) -> str | None:
    # YYMMDD → YYYY-MM-DD (assume 2000s for YY < 30)
    if len(s) != 6 or not s.isdigit():
        return None
    yy, mm, dd = s[:2], s[2:4], s[4:]
    yyyy = f"20{yy}" if int(yy) < 30 else f"19{yy}"
    return f"{yyyy}-{mm}-{dd}"
