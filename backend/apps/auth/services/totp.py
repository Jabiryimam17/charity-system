import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer: str="Charity App")->str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(email, issuer_name=issuer)

def generate_qr_base64(uri: str)->str:

    """Returns base64 PNG to embed directly in HTML as <img src="data:image/png;base64,..." alt="QR Code">"""
    qr = qrcode.make(uri)
    img = qr.make_image(fill_color="black", back_color="white")
    output = BytesIO()
    img.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("utf-8")

def verify_totp_code(secret: str, code: str)->bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

