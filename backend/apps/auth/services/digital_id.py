from pyzbar.pyzbar import decode
from PIL import Image
import json, base64, io


def extract_fayda_qr(image_bytes: bytes) -> dict | None:
    """
    Decode the QR code from a Fayda card image.
    Returns structured fields or None if no QR f
    :param image_bytes:
    :return:
    """
    image = Image.open(io.BytesIO(image_bytes))
    codes = decode(image)
    for code in codes:
        try:
            raw = code.data.decode('utf-8')
            payload = json.loads(raw)
            # MOSIP QR payload structure
            return {
                "source": "fayda_qr",
                "full_name": payload.get("name") or _join(payload, ["firstName", "lastName"]),
                "date_of_birth": payload.get("dateOfBirth") or payload.get("dob"),
                "id_number": payload.get("uin") or payload.get("vid"),
                "gender": payload.get("gender"),
                "nationality": "Ethiopian",
                "issuing_country": "Ethiopia",
                "region_country": "Ethiopia",
                "region_state": payload.get("region"),
                "region_city": payload.get("city") or payload.get("zone"),
                "address": payload.get("addressLine1"),
                "confidence": 1.0,  # QR = structured signed data, max confidence
                "status": "verified",
                "raw_payload": payload,
            }
        except (json.JSONDecodeError, KeyError):
            continue
    return None

def _join(d: dict, keys: list) -> str | None:
    return " ".join(d.get(k) for k in keys if d.get(k)) or None

