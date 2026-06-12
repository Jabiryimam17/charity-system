#
# from webauthn.helpers.structs import (
#     AuthenticatorSelectionCriteria,
#     UserVerificationRequirement,
#     ResidentKeyRequirement,
# )
# from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options,verify_authentication_response
# from webauthn.helpers import bytes_to_base64url, base64url_to_bytes
# from django.conf import settings
# from .models import WebAuthnCredential
#
# RP_ID = settings.WEBAUTHN_RP_ID
# RP_NAME = settings.WEBAUTHN_RP_NAME
# RP_ORIGIN = settings.WEBAUTHN_RP_ORIGIN
#
# def begin_registration(user):
#     # exclude credentials user already registered
#     existing = [
#         {"id":bytes(c.credential_id).hex(), "transports":[]}
#         for c in user.webauthn_credential_set.all()
#     ]
#
#     options = generate_registration_options(
#         rp_id=RP_ID,
#         rp_name = RP_NAME,
#         user_id=str(user.id).encode(),
#         user_name=user.email,
#         user_display_name=user.get_full_name(),
#         exclude_credentials=existing,
#         authenticator_selection = AuthenticatorSelectionCriteria(
#             user_verification=UserVerificationRequirement.PREFERRED,
#             resident_key = ResidentKeyRequirement.DISCOURAGED
#         ),
#     )
#     return options
#
# def complete_registration(user, credential_data, challenge):
#     verification=verify_registration_response(
#         credential=credential_data,
#         expected_challenge=challenge,
#         expected_rp_id=RP_ID,
#         expected_origin=RP_ORIGIN,
#         require_user_verification=False,
#     )
#
#     cred = WebAuthnCredential(
#         user=user,
#         credential_id=verification.credential_id,
#         public_key=verification.credential_public_key,
#         sign_count=verification.sign_count,
#     )
#     return cred
#
#
# def begin_authentication(user):
#     credentials = [
#         {"id":bytes(c.credential_id).hex(), "transports":[]}
#         for c in user.webauthn_credential_set.all()
#     ]
#
#     options = generate_authentication_options(
#         rp_id=RP_ID,
#         allow_credentials=credentials,
#         user_verification=UserVerificationRequirement.PREFERRED,
#     )
#     return options
#
# def complete_authentication(user, credential_data, challenge):
#     cred_id = base64url_to_bytes(credential_data["id"])
#     stored = user.webauthn_credentials.get(credential_id=cred_id)
#
#     verification = verify_authentication_response(
#         credential=credential_data,
#         expected_challenge=challenge,
#         expected_rp_id=RP_ID,
#         expected_origin=RP_ORIGIN,
#         credential_public_key=bytes(stored.public_key),
#         credential_current_sign_count=stored.sign_count,
#         require_user_verification=False
#     )
#     stored.sign_count = verification.new_sign_count
#     stored.save()
#     return verification