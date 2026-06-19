from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from pathlib import Path


def send_email(code: str, to_email: str) -> bool:
    html = _render_verify_template(code, to_email)

    plain = f"Your verification code is {code}\n\n Expires in 10 minutes"

    msg = EmailMultiAlternatives(
        subject=f"{code} is your verification code",
        body=plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html, "text/html")
    try:
        msg.send()
        return True
    except Exception as e:
        return False


def _render_verify_template(code: str, email: str) -> str:
    verify_template_path = Path(__file__).parent.parent.parent/ "templates" / "verification_email.html"
    html = verify_template_path.read_text()
    digits_html = "\n".join(
        f'<span class="digit">{d}</span>' for d in code
    )
    html = html.replace(
        '\n'.join(f'<span class="digit">{d}</span>' for d in "483912"),
        digits_html
    )
    html = html.replace("user@example.com", email)
    return html
