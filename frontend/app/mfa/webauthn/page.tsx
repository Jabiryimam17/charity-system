'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Fingerprint, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { getAccessToken } from '@/lib/auth';
import { createWebAuthnCredential, isWebAuthnSupported } from '@/lib/webauthn';

export default function WebAuthnSetupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  const setupWebAuthn = async () => {
    setLoading(true);
    setError('');
    setStatus('Starting WebAuthn registration...');

    try {
      if (!isWebAuthnSupported()) {
        throw new Error('This browser does not support WebAuthn/passkeys.');
      }

      const token = getAccessToken();
      if (!token) {
        throw new Error('Please login first.');
      }

      await createWebAuthnCredential();

      setStatus('WebAuthn setup completed successfully.');
      setTimeout(() => router.push('/mfa'), 1200);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not setup WebAuthn';
      setError(message);
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#e0f7fa] bg-gradient-to-br from-cyan-100 via-blue-100 to-indigo-200 flex items-center justify-center p-4">
      <div className="max-w-lg w-full bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl border border-white/50 p-8">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-2xl shadow-lg mb-4">
            <Fingerprint className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900">WebAuthn Setup</h1>
          <p className="text-gray-500 mt-2">Register your biometric authenticator or security key.</p>
        </div>

        <button
          onClick={setupWebAuthn}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl disabled:opacity-70"
        >
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <Loader2 className="h-5 w-5 animate-spin" />
              Waiting for browser popup...
            </span>
          ) : (
            'Start WebAuthn Setup'
          )}
        </button>

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
