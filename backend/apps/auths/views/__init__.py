from apps.auths.views.webauthn import webauthn_register_begin, webauthn_register_complete, webauthn_auth_begin, webauthn_auth_complete
from apps.auths.views.identity import verify_id
from apps.auths.views.documents import submit_document, document_status
from apps.auths.views.totp import totp_setup, totp_verify, totp_confirm