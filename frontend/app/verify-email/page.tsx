'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Mail, Loader2, AlertCircle, CheckCircle2, ArrowRight } from 'lucide-react';

export default function VerifyEmailPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    const storedEmail = sessionStorage.getItem('verify_email');
    if (storedEmail) {
      setEmail(storedEmail);
    } else {
      // If no email in session, fallback for demo
      setEmail('your email');
    }
  }, []);

  const handleCodeChange = (index: number, value: string) => {
    if (value.length > 1) value = value.slice(-1);
    if (!/^\d*$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    // Auto-focus next input
    if (value && index < 5) {
      const nextInput = document.getElementById(`code-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      const prevInput = document.getElementById(`code-${index - 1}`);
      prevInput?.focus();
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    const verificationCode = code.join('');
    if (verificationCode.length !== 6) {
      setError('Please enter the full 6-digit code');
      return;
    }

    setLoading(true);
    setError('');
    setStatus('Verifying...');

    try {
      const response = await fetch('http://localhost:8000/api/auths/email-otp/verify-email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          code: verificationCode,
        }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || 'Verification failed');
      }

      setStatus('Email verified successfully!');
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);

    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setStatus('Sending new code...');
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/auths/email-otp/send-email-code/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      const result = await response.json();
      if (result.success) {
        setStatus('New code sent to your email');
      } else {
        setError(result.message || 'Failed to resend code');
      }
    } catch (err) {
      setError('Failed to resend code');
    }
  };

  return (
    <div className="min-h-screen bg-[#e0f7fa] bg-gradient-to-br from-cyan-100 via-blue-100 to-indigo-200 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative water bubbles */}
      <div className="absolute top-[-10%] left-[-5%] w-64 h-64 bg-white/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-[-10%] right-[-5%] w-80 h-80 bg-blue-300/20 rounded-full blur-3xl animate-pulse delay-700"></div>

      <div className="max-w-md w-full bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl overflow-hidden border border-white/50 relative z-10">
        <div className="px-8 pt-10 pb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl shadow-lg mb-6 transform rotate-6 hover:rotate-0 transition-transform duration-300">
            <Mail className="h-8 w-8 text-white" />
          </div>
          
          <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Check your email</h1>
          <p className="text-gray-500 mb-8">
            We've sent a 6-digit code to <span className="text-blue-600 font-semibold">{email}</span>
          </p>

          <form onSubmit={handleVerify} className="space-y-8">
            <div className="flex justify-center gap-2 sm:gap-4">
              {code.map((digit, index) => (
                <input
                  key={index}
                  id={`code-${index}`}
                  type="text"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleCodeChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  className="w-10 h-12 sm:w-12 sm:h-14 text-center text-2xl font-bold text-gray-900 caret-blue-600 bg-white/80 border-2 border-blue-100 rounded-xl shadow-sm shadow-blue-100/40 focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all"
                />
              ))}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed shadow-lg shadow-blue-200"
            >
              {loading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <span>Verify Email</span>
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8">
            <p className="text-sm text-gray-600">
              Didn't receive the code?{' '}
              <button 
                onClick={handleResend}
                className="text-blue-600 font-bold hover:text-blue-700 hover:underline transition-colors"
              >
                Resend Code
              </button>
            </p>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-50/50 border border-red-100 text-red-700 rounded-xl flex items-start gap-3 text-sm animate-in fade-in slide-in-from-top-2 duration-300">
              <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {status && !error && !status.includes('successfully') && (
            <div className="mt-6 p-4 bg-blue-50/50 border border-blue-100 text-blue-700 rounded-xl flex items-center gap-3 text-sm animate-pulse">
              <Loader2 className="h-5 w-5 shrink-0 animate-spin" />
              <span>{status}</span>
            </div>
          )}

          {status.includes('successfully') && (
            <div className="mt-6 p-4 bg-green-50/50 border border-green-100 text-green-700 rounded-xl flex items-center gap-3 text-sm">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <span>{status}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
