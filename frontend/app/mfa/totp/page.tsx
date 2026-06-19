'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { KeyRound, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { getAccessToken, getApiBaseUrl } from '@/lib/auth';

export default function TotpSetupPage() {
  const router = useRouter();
  const [secret, setSecret] = useState('');
  const [qr, setQr] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  const setupTotp = async () => {
    setLoading(true);
    setError('');
    setStatus('Generating TOTP secret...');

    try {
      const token = getAccessToken();
      if (!token) {
        throw new Error('Please login first.');
      }

      const response = await fetch(`${getApiBaseUrl()}/mfs/setup/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || result.message || 'Failed to setup TOTP');
      }

      setSecret(result.secret || '');
      setQr(result.qr || '');
      setStatus('Scan the QR code and enter your first OTP code below.');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not setup TOTP';
      setError(message);
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  const confirmTotp = async () => {
    setLoading(true);
    setError('');
    setStatus('Verifying code...');

    try {
      const token = getAccessToken();
      if (!token) {
        throw new Error('Please login first.');
      }

      const response = await fetch(`${getApiBaseUrl()}/mfs/confirm/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ code }),
      });

      const result = await response.json();
      if (!response.ok || !result.success) {
        throw new Error(result.error || result.message || 'Failed to confirm TOTP');
      }

      setStatus('TOTP setup completed successfully.');
      setTimeout(() => router.push('/mfa'), 1200);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not confirm TOTP';
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
            <KeyRound className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900">TOTP Setup</h1>
          <p className="text-gray-500 mt-2">Use your authenticator app to scan and verify.</p>
        </div>

        {!secret && (
          <button
            onClick={setupTotp}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl disabled:opacity-70"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin mx-auto" /> : 'Generate TOTP QR'}
          </button>
        )}

        {qr && (
          <div className="space-y-4">
            <Image src={qr} alt="TOTP QR" width={192} height={192} className="w-48 h-48 mx-auto rounded-xl border border-blue-100" />
            <p className="text-xs text-gray-500 break-all">Manual secret: <span className="font-semibold text-gray-700">{secret}</span></p>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="Enter 6-digit code"
              className="w-full px-4 py-3 rounded-xl border border-blue-100 outline-none focus:ring-2 focus:ring-blue-500/40"
            />
            <button
              onClick={confirmTotp}
              disabled={loading || code.length < 6}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl disabled:opacity-70"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin mx-auto" /> : 'Confirm TOTP'}
            </button>
          </div>
        )}

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
