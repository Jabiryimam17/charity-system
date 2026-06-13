from apps.auth.views.webauthn import webauthn_register_begin, webauthn_register_complete, webauthn_auth_begin, webauthn_auth_complete
from apps.auth.views.identity import verify_id
from apps.auth.views.documents import submit_document, document_status
from apps.auth.views.totp import totp_setup, totp_verify, totp_confirm