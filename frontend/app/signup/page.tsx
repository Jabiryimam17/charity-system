'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ethers } from 'ethers';
import { Mail, User, Lock, Phone, Wallet, Loader2, AlertCircle, CheckCircle2, Droplets, ArrowRight } from 'lucide-react';

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setStatus('Connecting to wallet...');

    try {
      if (!window.ethereum) {
        throw new Error('MetaMask or another Ethereum wallet is required');
      }

      // 1. Request wallet connection
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      setStatus('Signing message...');
      
      // 2. Generate message and timestamp
      const message = "Register to Charity System: ";
      const timestamp = Math.floor(Date.now() / 1000).toString();
      const fullMessage = `${message}${timestamp}`;
      
      // 3. Sign message
      const signature = await signer.signMessage(fullMessage);

      setStatus('Creating account...');

      // 4. Send to backend
      const response = await fetch('http://localhost:8000/api/auths/email-otp/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user: {
            user_address: address,
            message: message,
            timestamp: timestamp,
            signature: signature,
            email: formData.email,
            first_name: formData.firstName,
            last_name: formData.lastName,
            password: formData.password,
            phone_number: formData.phone,
          },
        }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || result.error || 'Registration failed');
      }

      setStatus('Success! Redirecting...');
      // Store email in session storage for the verify page
      sessionStorage.setItem('verify_email', formData.email);
      
      setTimeout(() => {
        router.push('/verify-email');
      }, 1500);

    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An unexpected error occurred');
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#e0f7fa] bg-gradient-to-br from-cyan-100 via-blue-100 to-indigo-200 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative water bubbles */}
      <div className="absolute top-[-10%] left-[-5%] w-64 h-64 bg-white/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-[-10%] right-[-5%] w-80 h-80 bg-blue-300/20 rounded-full blur-3xl animate-pulse delay-700"></div>
      <div className="absolute top-1/4 right-1/4 w-32 h-32 bg-cyan-200/30 rounded-full blur-2xl animate-bounce duration-[10s]"></div>

      <div className="max-w-md w-full bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl overflow-hidden border border-white/50 relative z-10">
        <div className="px-8 pt-10 pb-8">
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl shadow-lg mb-4 transform -rotate-3 hover:rotate-0 transition-transform duration-300">
              <Droplets className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Create Account</h1>
            <p className="text-gray-500 mt-2">Join our community and make a splash</p>
          </div>

          <form onSubmit={handleSignup} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-700 ml-1">First Name</label>
                <div className="relative group">
                  <User className="absolute left-3 top-3 h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                  <input
                    type="text"
                    name="firstName"
                    placeholder="John"
                    required
                    className="w-full pl-10 pr-4 py-2.5 bg-white/70 text-gray-900 caret-blue-600 border border-blue-100 rounded-xl shadow-sm shadow-blue-100/40 focus:bg-white focus:ring-2 focus:ring-blue-500/40 focus:border-blue-300 outline-none transition-all duration-200 placeholder:text-gray-500"
                    value={formData.firstName}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-700 ml-1">Last Name</label>
                <div className="relative group">
                  <User className="absolute left-3 top-3 h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                  <input
                    type="text"
                    name="lastName"
                    placeholder="Doe"
                    required
                    className="w-full pl-10 pr-4 py-2.5 bg-white/70 text-gray-900 caret-blue-600 border border-blue-100 rounded-xl shadow-sm shadow-blue-100/40 focus:bg-white focus:ring-2 focus:ring-blue-500/40 focus:border-blue-300 outline-none transition-all duration-200 placeholder:text-gray-500"
                    value={formData.lastName}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-700 ml-1">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                <input
                  type="email"
                  name="email"
                  placeholder="john@example.com"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-white/70 text-gray-900 caret-blue-600 border border-blue-100 rounded-xl shadow-sm shadow-blue-100/40 focus:bg-white focus:ring-2 focus:ring-blue-500/40 focus:border-blue-300 outline-none transition-all duration-200 placeholder:text-gray-500"
                  value={formData.email}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-700 ml-1">Phone Number</label>
              <div className="relative group">
                <Phone className="absolute left-3 top-3 h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                <input
                  type="tel"
                  name="phone"
                  placeholder="+251..."
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-white/70 text-gray-900 caret-blue-600 border border-blue-100 rounded-xl shadow-sm shadow-blue-100/40 focus:bg-white focus:ring-2 focus:ring-blue-500/40 focus:border-blue-300 outline-none transition-all duration-200 placeholder:text-gray-500"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-700 ml-1">Password</label>
              <div className="relative group">
                <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                <input
                  type="password"
                  name="password"
                  placeholder="••••••••"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-white/70 text-gray-900 caret-blue-600 border border-blue-100 rounded-xl shadow-sm shadow-blue-100/40 focus:bg-white focus:ring-2 focus:ring-blue-500/40 focus:border-blue-300 outline-none transition-all duration-200 placeholder:text-gray-500"
                  value={formData.password}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed shadow-lg shadow-blue-200 active:scale-[0.98]"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    {status || 'Processing...'}
                  </>
                ) : (
                  <>
                    <Wallet className="h-5 w-5" />
                    <span>Sign & Sign Up</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-6 p-4 bg-red-50/50 border border-red-100 text-red-700 rounded-xl flex items-start gap-3 text-sm animate-in fade-in slide-in-from-top-2 duration-300">
              <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {status && !error && !status.includes('Success') && (
             <div className="mt-6 p-4 bg-blue-50/50 border border-blue-100 text-blue-700 rounded-xl flex items-center gap-3 text-sm animate-pulse">
                <Loader2 className="h-5 w-5 shrink-0 animate-spin" />
                <span>{status}</span>
             </div>
          )}

          {status.includes('Success') && (
            <div className="mt-6 p-4 bg-green-50/50 border border-green-100 text-green-700 rounded-xl flex items-center gap-3 text-sm animate-in zoom-in duration-300">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <span>{status}</span>
            </div>
          )}
        </div>

        <div className="px-8 py-6 bg-gray-50/50 border-t border-gray-100 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="text-blue-600 font-bold hover:text-blue-700 hover:underline transition-colors">
              Log In
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
