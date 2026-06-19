'use client';

import React, { useState } from 'react';
import { ShieldCheck, Fingerprint, KeyRound, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { getAccessToken, getApiBaseUrl } from '@/lib/auth';
import { fetchWithWebAuthn } from '@/lib/webauthn';

export default function MfaSetupPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  const runProtectedRequest = async () => {
    setLoading(true);
    setError('');
    setStatus('Triggering WebAuthn popup...');

    try {
      const token = getAccessToken();
      if (!token) {
        throw new Error('Login first to run protected requests.');
      }

      const response = await fetchWithWebAuthn(`${getApiBaseUrl()}/identity/verify-id/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ document_type: 'passport', document_number: 'A1234567' }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Protected request failed');
      }

      setStatus('Protected request completed after WebAuthn verification.');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to complete protected request';
      setError(message);
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#e0f7fa] bg-gradient-to-br from-cyan-100 via-blue-100 to-indigo-200 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl border border-white/50 p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-2xl shadow-lg mb-4">
            <ShieldCheck className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900">Set up Multi-Factor Security</h1>
          <p className="text-gray-500 mt-2">Enable TOTP or WebAuthn to secure your account.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <a href="/mfa/totp" className="p-5 rounded-2xl border border-blue-100 bg-white hover:border-blue-300 transition-colors">
            <div className="flex items-center gap-3 mb-2">
              <KeyRound className="h-5 w-5 text-blue-600" />
              <h2 className="font-bold text-gray-900">Set up TOTP</h2>
            </div>
            <p className="text-sm text-gray-600">Scan QR with Google Authenticator/Authy and verify your first code.</p>
          </a>

          <a href="/mfa/webauthn" className="p-5 rounded-2xl border border-blue-100 bg-white hover:border-blue-300 transition-colors">
            <div className="flex items-center gap-3 mb-2">
              <Fingerprint className="h-5 w-5 text-blue-600" />
              <h2 className="font-bold text-gray-900">Set up WebAuthn</h2>
            </div>
            <p className="text-sm text-gray-600">Register your device biometrics/security key for popup-based verification.</p>
          </a>
        </div>

        <div className="mt-8 p-5 rounded-2xl border border-indigo-100 bg-indigo-50/50">
          <h3 className="font-semibold text-gray-900 mb-2">Test request-time WebAuthn popup</h3>
          <p className="text-sm text-gray-600 mb-4">When you click this, a WebAuthn popup appears before the protected request is sent.</p>
          <button
            onClick={runProtectedRequest}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 px-4 rounded-xl disabled:opacity-70"
          >
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Verifying...
              </span>
            ) : (
              'Run Protected Request'
            )}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-100 text-red-700 rounded-xl flex items-start gap-2 text-sm">
            <AlertCircle className="h-4 w-4 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {status && !error && (
          <div className="mt-4 p-3 bg-green-50 border border-green-100 text-green-700 rounded-xl flex items-start gap-2 text-sm">
            <CheckCircle2 className="h-4 w-4 mt-0.5" />
            <span>{status}</span>
          </div>
        )}
      </div>
    </div>
  );
}
