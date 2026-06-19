import { getAccessToken, getApiBaseUrl } from './auth';

const toBase64Url = (buffer: ArrayBuffer) => {
  const bytes = new Uint8Array(buffer);
  const binary = bytes.reduce((acc, b) => acc + String.fromCharCode(b), '');
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
};

const fromBase64Url = (input: string) => {
  const padded = input.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(input.length / 4) * 4, '=');
  const binary = atob(padded);
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
};

const authHeaders = () => {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export const isWebAuthnSupported = () =>
  typeof window !== 'undefined' && typeof window.PublicKeyCredential !== 'undefined';

export const createWebAuthnCredential = async () => {
  const beginRes = await fetch(`${getApiBaseUrl()}/webauthn/register/begin`, {
    method: 'GET',
    headers: authHeaders(),
  });

  const begin = await beginRes.json();
  if (!beginRes.ok) {
    throw new Error(begin.error || begin.message || 'Failed to start WebAuthn setup');
  }

  const publicKey: PublicKeyCredentialCreationOptions = {
    ...begin,
    challenge: fromBase64Url(begin.challenge),
    user: {
      ...begin.user,
      id: fromBase64Url(begin.user.id),
    },
    excludeCredentials: (begin.excludeCredentials || []).map(
      (credential: { id: string; type: PublicKeyCredentialType }) => ({
        ...credential,
        id: fromBase64Url(credential.id),
      }),
    ),
  };

  const credential = (await navigator.credentials.create({
    publicKey,
  })) as PublicKeyCredential | null;

  if (!credential) {
    throw new Error('WebAuthn setup was cancelled');
  }

  const response = credential.response as AuthenticatorAttestationResponse;
  const payload = {
    id: credential.id,
    rawId: toBase64Url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: toBase64Url(response.clientDataJSON),
      attestationObject: toBase64Url(response.attestationObject),
    },
  };

  const completeRes = await fetch(`${getApiBaseUrl()}/webauthn/register/complete/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  const complete = await completeRes.json();
  if (!completeRes.ok || !complete.success) {
    throw new Error(complete.error || complete.message || 'WebAuthn setup failed');
  }

  return complete;
};

export const completeWebAuthnAssertion = async () => {
  const beginRes = await fetch(`${getApiBaseUrl()}/webauthn/auth/begin/`, {
    method: 'GET',
    headers: authHeaders(),
  });

  const begin = await beginRes.json();
  if (!beginRes.ok) {
    throw new Error(begin.error || begin.message || 'Failed to start WebAuthn verification');
  }

  const publicKey: PublicKeyCredentialRequestOptions = {
    ...begin,
    challenge: fromBase64Url(begin.challenge),
    allowCredentials: (begin.allowCredentials || []).map((credential: { id: string; type: PublicKeyCredentialType }) => ({
      ...credential,
      id: fromBase64Url(credential.id),
    })),
  };

  const credential = (await navigator.credentials.get({
    publicKey,
  })) as PublicKeyCredential | null;

  if (!credential) {
    throw new Error('WebAuthn request was cancelled');
  }

  const response = credential.response as AuthenticatorAssertionResponse;

  const payload = {
    id: credential.id,
    rawId: toBase64Url(credential.rawId),
    type: credential.type,
    response: {
      authenticatorData: toBase64Url(response.authenticatorData),
      clientDataJSON: toBase64Url(response.clientDataJSON),
      signature: toBase64Url(response.signature),
      userHandle: response.userHandle ? toBase64Url(response.userHandle) : null,
    },
  };

  const completeRes = await fetch(`${getApiBaseUrl()}/webauthn/auth/complete/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  const complete = await completeRes.json();
  if (!completeRes.ok || !complete.success) {
    throw new Error(complete.error || complete.message || 'WebAuthn verification failed');
  }

  return complete;
};

export const fetchWithWebAuthn = async (input: RequestInfo | URL, init?: RequestInit) => {
  await completeWebAuthnAssertion();
  return fetch(input, init);
};
