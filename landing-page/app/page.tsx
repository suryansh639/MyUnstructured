'use client'

import { useState } from 'react'

const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT || ''
const USER_POOL_CLIENT_ID = process.env.NEXT_PUBLIC_USER_POOL_CLIENT_ID || ''

export default function Home() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [message, setMessage] = useState('')
  const [isLogin, setIsLogin] = useState(false)
  const [showVerification, setShowVerification] = useState(false)
  const [token, setToken] = useState('')
  const [credits, setCredits] = useState<number | null>(null)

  const handleRegister = async () => {
    try {
      const response = await fetch(`${API_ENDPOINT}/v1/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name }),
      })
      const data = await response.json()
      
      if (response.ok) {
        setMessage('✅ Registration successful! Check your email for verification code.')
        setShowVerification(true)
      } else {
        setMessage(JSON.stringify(data, null, 2))
      }
    } catch (error) {
      setMessage('Error: ' + error)
    }
  }

  const handleVerify = async () => {
    try {
      const response = await fetch('https://cognito-idp.us-east-1.amazonaws.com/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-amz-json-1.1',
          'X-Amz-Target': 'AWSCognitoIdentityProviderService.ConfirmSignUp',
        },
        body: JSON.stringify({
          ClientId: USER_POOL_CLIENT_ID,
          Username: email,
          ConfirmationCode: verificationCode,
        }),
      })
      
      if (response.ok) {
        setMessage('✅ Email verified successfully! Logging you in...')
        setTimeout(() => handleLogin(), 1000)
      } else {
        const data = await response.json()
        setMessage('❌ ' + (data.message || 'Invalid verification code'))
      }
    } catch (error) {
      setMessage('Error: ' + error)
    }
  }

  const handleLogin = async () => {
    try {
      const response = await fetch('https://cognito-idp.us-east-1.amazonaws.com/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-amz-json-1.1',
          'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
        },
        body: JSON.stringify({
          AuthFlow: 'USER_PASSWORD_AUTH',
          ClientId: USER_POOL_CLIENT_ID,
          AuthParameters: {
            USERNAME: email,
            PASSWORD: password,
          },
        }),
      })
      const data = await response.json()
      
      if (data.AuthenticationResult) {
        setToken(data.AuthenticationResult.IdToken)
        setMessage('✅ Login successful!')
        setIsLogin(true)
        setShowVerification(false)
        fetchCredits(data.AuthenticationResult.IdToken)
      } else if (data.message?.includes('not confirmed')) {
        setMessage('❌ Please verify your email first. Check your inbox for verification code.')
        setShowVerification(true)
      } else {
        setMessage('❌ ' + (data.message || 'Login failed'))
      }
    } catch (error) {
      setMessage('Error: ' + error)
    }
  }

  const fetchCredits = async (authToken: string) => {
    try {
      const response = await fetch(`${API_ENDPOINT}/v1/credits`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
      })
      const data = await response.json()
      setCredits(data.credits)
    } catch (error) {
      console.error('Error fetching credits:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {!isLogin ? (
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-5xl font-bold text-center mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              DocuAI
            </h1>
            <p className="text-center text-gray-600 mb-8">Transform Unstructured Documents to AI-Ready Data</p>

            <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
              {showVerification ? (
                <>
                  <h2 className="text-2xl font-bold mb-4">✉️ Verify Your Email</h2>
                  <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
                    <p className="text-sm text-blue-700">
                      📧 We sent a 6-digit verification code to:<br/>
                      <strong className="text-lg">{email}</strong>
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="000000"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      className="w-full px-4 py-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 outline-none text-center text-3xl tracking-widest font-bold"
                      maxLength={6}
                    />
                    
                    <button
                      onClick={handleVerify}
                      disabled={verificationCode.length !== 6}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50"
                    >
                      Verify & Login
                    </button>

                    <button
                      onClick={() => setShowVerification(false)}
                      className="w-full text-gray-600 py-2"
                    >
                      ← Back to Login
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <h2 className="text-2xl font-bold mb-6">Get Started</h2>
                  
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="Full Name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 outline-none"
                    />
                    <input
                      type="email"
                      placeholder="Email Address"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 outline-none"
                    />
                    <input
                      type="password"
                      placeholder="Password (min 8 chars, 1 uppercase, 1 number)"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 outline-none"
                    />
                    
                    <div className="flex gap-4">
                      <button
                        onClick={handleRegister}
                        className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition"
                      >
                        Register (5 Free Credits)
                      </button>
                      <button
                        onClick={handleLogin}
                        className="flex-1 border-2 border-blue-600 text-blue-600 py-3 rounded-lg font-semibold hover:bg-blue-50 transition"
                      >
                        Login
                      </button>
                    </div>

                    <div className="text-center">
                      <button
                        onClick={() => setShowVerification(true)}
                        className="text-sm text-blue-600 hover:underline"
                      >
                        Have a verification code? Click here
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>

            {message && (
              <div className="bg-gray-900 text-green-400 rounded-lg p-6 font-mono text-sm overflow-auto max-h-96">
                <pre>{message}</pre>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="h-screen flex flex-col">
          {/* Top Bar */}
          <div className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                DocuAI
              </h1>
              <span className="text-gray-600">|</span>
              <span className="text-gray-700">Document Processing Suite</span>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-right">
                <div className="text-xs text-gray-500">Credits</div>
                <div className="text-xl font-bold text-blue-600">{credits}</div>
              </div>
              <button
                onClick={() => {
                  setIsLogin(false)
                  setToken('')
                  setCredits(null)
                  setEmail('')
                  setPassword('')
                }}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
              >
                Logout
              </button>
            </div>
          </div>

          {/* Streamlit App in iframe */}
          <div className="flex-1">
            <iframe
              src="http://localhost:8501"
              className="w-full h-full border-0"
              title="Document Processing App"
            />
          </div>
        </div>
      )}
    </div>
  )
}
