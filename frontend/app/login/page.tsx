'use client'

import React, { useState, FormEvent } from 'react';
import Image from 'next/image';

const Login: React.FC = () => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showError, setShowError] = useState<boolean>(false);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setShowError(false);

    try {
      const response = await fetch('http://localhost:8008/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        document.cookie = `access_token=${data.access_token}; path=/;`;
        window.location.href = '/account/1'; // or homepage
      }else {
        setShowError(true);
        setTimeout(() => setShowError(false), 3000); // auto-hide after 3s
      }
    } catch (err) {
      console.error(err);
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
    }
  };

  return (
    <div className="min-h-screen flex relative">
      {/* Toast Notification */}
      {showError && (
        <div className="absolute top-4 right-4 z-50 bg-red-500 text-white px-4 py-2 rounded shadow-lg animate-fade-in-down">
          Incorrect username or password
        </div>
      )}

      {/* Left Panel */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-indigo-600 to-purple-700 text-white items-center justify-center p-10">
        <div className="max-w-md">
          <h1 className="text-4xl font-bold mb-4">Welcome to SmartSpendAI</h1>
          <p className="text-lg">
            Take control of your finances. Track expenses, set budgets, manage subscriptions and get AI-powered savings tips — all in one place.
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex flex-col items-center mb-6">
            <Image
              src="logo.svg"
              alt="SmartSpendAI Logo"
              width={100}
              height={100}
            />
            <h2 className="text-2xl font-semibold mt-4">Login to SmartSpendAI</h2>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition duration-200"
            >
              Sign In
            </button>

            <div className="flex justify-between items-center text-sm mt-2">
              <a href="#" className="hover:underline">Forgot password?</a>
              <a href="#" className="hover:underline">Don't have an account?</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
