from .digital_id import extract_fayda_qr
from .mrz_parser import parse_mrz
from  .vision import extract_id_fields

def verify_identity(image_bytes: bytes) -> dict:
    """
    Priority chain:
    1. Fayda / MOSIP QR  → structured, confidence 1.0
    2. MRZ parse          → structured, confidence 0.95
    3. Google Vision OCR  → heuristic,  confidence 0.5–0.9
    :param image_bytes:
    :return:
    """

    result = extract_id_fields(image_bytes)
    if result: return result
    ocr_fields = extract_id_fields(image_bytes)
    if ocr_fields.get("mrz_line"):
        mrz = parse_mrz(ocr_fields["mrz_line"])
        if mrz:
            mrz["region_country"] = ocr_fields.get("region_country")
            mrz["region_state"] = ocr_fields.get("region_state")
            mrz["region_city"] = ocr_fields.get("region_city")
            mrz["address"] = ocr_fields.get("address")
            return mrz
    ocr_fields["source"]="ocr"
    return ocr_fields