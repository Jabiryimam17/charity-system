from enum import IntFlag

class IdentityStep(IntFlag):
    NONE = 0
    GOVERNMENT_ID = 1 << 1
    TAX_DOCUMENT = 1 << 2
    RELIGIOUS_CERTIFICATE = 1 << 3
class AuthSteps(IntFlag):
    NONE = 0
    EMAIL = 1 << 0
    WALLET = 1 << 1
    TOTP = 1 << 2
    SMS = 1 << 3
    HARDWARE_KEY = 1 << 4

class Roles(IntFlag):
    NONE = 0
    DONATOR = 1 << 0
    BENEFICIARY = 1 << 1
    RELIGIOUS_LEADER = 1 << 2
    PLANNER = 1 << 3
    EXECUTOR = 1 << 4
    AUDITOR = 1 << 5
    VERIFIER = 1 << 6