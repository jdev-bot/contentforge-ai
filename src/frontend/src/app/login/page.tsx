'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { signIn, signUp } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Sparkles, Zap, Shield, CheckCircle, Mail, Lock } from 'lucide-react'
import { cn } from '@/lib/utils'

const APP_ENV = process.env.NEXT_PUBLIC_APP_ENV || 'production'
const isStaging = APP_ENV === 'staging'
const SIGNUP_ENABLED = process.env.NEXT_PUBLIC_SIGNUP_ENABLED !== 'false'

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900"><div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full" /></div>}>
      <LoginContent />
    </Suspense>
  )
}

function LoginContent() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()
  const redirectTo = searchParams.get('redirectTo') || '/'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (isLogin) {
        const { error } = await signIn(email, password)
        if (error) throw error
      } else {
        const { error } = await signUp(email, password, fullName)
        if (error) throw error
      }
      // Full page reload to ensure middleware reads the new auth cookies
      const destination = redirectTo || '/'
      window.location.href = destination
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const features = [
    { icon: Sparkles, text: 'AI-powered content transformation' },
    { icon: Zap, text: '20+ content formats supported' },
    { icon: Shield, text: 'Enterprise-grade security' },
  ]

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Decorative */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-violet-600 to-fuchsia-600">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30">
          </div>
          
          {/* Floating Elements */}
          <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full blur-xl animate-float" />
          <div className="absolute bottom-40 right-20 w-48 h-48 bg-violet-500/20 rounded-full blur-2xl animate-float" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/3 w-24 h-24 bg-fuchsia-500/20 rounded-full blur-xl animate-float" style={{ animationDelay: '2s' }} />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-16 text-white">
          <div className="mb-8">
            <Badge variant="default" className="bg-white/20 text-white border-white/30 mb-6">
              <Sparkles className="w-3 h-3 mr-1" />
              New: AI Content Generation
            </Badge>
            <h1 className="text-5xl font-bold mb-6 leading-tight">
              Transform Your Content
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-pink-300">
                With AI Power
              </span>
            </h1>
            <p className="text-xl text-blue-100 mb-10 max-w-md">
              Create, repurpose, and distribute content across 20+ formats in minutes, not hours.
            </p>
          </div>

          <div className="space-y-4">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="flex items-center gap-4 p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20"
              >
                <div className="p-2 bg-white/20 rounded-lg">
                  <feature.icon className="w-5 h-5" />
                </div>
                <span className="font-medium">{feature.text}</span>
              </div>
            ))}
          </div>

          {/* Trust Badges */}
          <div className="mt-12 pt-8 border-t border-white/20">
            <p className="text-sm text-blue-200 mb-4">Trusted by teams at</p>
            <div className="flex items-center gap-6 opacity-70">
              {['Google', 'Meta', 'Netflix', 'Spotify'].map((company) => (
                <span key={company} className="text-sm font-semibold">{company}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-8 bg-slate-50 dark:bg-slate-900">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
              ContentForge
            </span>
            <p className="text-slate-500 dark:text-slate-400 mt-2">
              AI-powered content transformation
            </p>
          </div>

          <Card variant="elevated" className="border-0 shadow-2xl">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {isLogin ? 'Welcome Back' : 'Create Account'}
              </CardTitle>
              <CardDescription className="mt-2">
                {isLogin 
                  ? 'Sign in to access your content workspace'
                  : isStaging 
                    ? 'Join the ContentForge staging environment'
                    : 'Start transforming your content with AI'
                }
              </CardDescription>
              {isStaging && (
                <div className="mt-3 p-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex items-center gap-2 text-sm text-amber-700 dark:text-amber-400">
                  <Lock className="w-4 h-4 flex-shrink-0" />
                  <span>Invite-only access — Contact an admin for an account.</span>
                </div>
              )}
            </CardHeader>
            
            <CardContent className="pt-6">
              {/* Social Login */}
              <div className="grid grid-cols-3 gap-3 mb-6">
                {[
                  { icon: 'github', label: 'GitHub' },
                  { icon: 'twitter', label: 'Twitter' },
                  { icon: 'mail', label: 'Email' },
                ].map((provider) => (
                  <button
                    key={provider.label}
                    type="button"
                    className={cn(
                      'flex items-center justify-center p-3',
                      'rounded-xl border border-slate-200 dark:border-slate-700',
                      'bg-white dark:bg-slate-800',
                      'text-slate-600 dark:text-slate-400',
                      'hover:bg-slate-50 dark:hover:bg-slate-700',
                      'hover:border-slate-300 dark:hover:border-slate-600',
                      'transition-all duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                    )}
                    aria-label={`Sign in with ${provider.label}`}
                  >
                    {provider.icon === 'github' && (
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                      </svg>
                    )}
                    {provider.icon === 'twitter' && (
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                      </svg>
                    )}
                    {provider.icon === 'mail' && (
                      <Mail className="w-5 h-5" />
                    )}
                  </button>
                ))}
              </div>

              <div className="relative mb-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200 dark:border-slate-700" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                    Or continue with email
                  </span>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && !SIGNUP_ENABLED && !isStaging && (
                  <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-400">
                    Self-registration is currently disabled. Please contact an administrator for an invite.
                  </div>
                )}
                {!isLogin && SIGNUP_ENABLED && (
                  <Input
                    type="text"
                    label="Full Name"
                    placeholder="John Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required={!isLogin}
                    autoComplete="name"
                  />
                )}
                
                <Input
                  type="email"
                  label="Email Address"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
                
                <Input
                  type="password"
                  label="Password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                />
                
                {!isLogin && (
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      id="terms"
                      checked={agreedToTerms}
                      onChange={(e) => setAgreedToTerms(e.target.checked)}
                      className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      required={!isLogin}
                    />
                    <label htmlFor="terms" className="text-sm text-slate-600 dark:text-slate-400">
                      I agree to the{' '}
                      <a href="#" className="text-blue-600 hover:text-blue-500 font-medium">Terms of Service</a>
                      {' '}and{' '}
                      <a href="#" className="text-blue-600 hover:text-blue-500 font-medium">Privacy Policy</a>
                    </label>
                  </div>
                )}
                
                {error && (
                  <div className="p-3 rounded-lg bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800">
                    <p className="text-sm text-rose-600 dark:text-rose-400 flex items-center gap-2">
                      <span className="text-lg">⚠</span> {error}
                    </p>
                  </div>
                )}
                
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full"
                  loading={loading}
                  disabled={!isLogin && !agreedToTerms}
                >
                  {isLogin ? 'Sign In' : 'Create Account'}
                </Button>
              </form>
              
              <div className="mt-6 text-center">
                {SIGNUP_ENABLED || isStaging ? (
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button
                      type="button"
                      onClick={() => {
                        setIsLogin(!isLogin)
                        setError('')
                      }}
                      className="text-blue-600 hover:text-blue-500 font-medium transition-colors"
                    >
                      {isLogin ? 'Sign Up' : 'Sign In'}
                    </button>
                  </p>
                ) : (
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Registration is invite-only. Contact an administrator.
                  </p>
                )}
              </div>

              {/* Feature list for mobile */}
              <div className="lg:hidden mt-8 pt-8 border-t border-slate-200 dark:border-slate-700">
                <div className="space-y-3">
                  {features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-3 text-sm text-slate-600 dark:text-slate-400">
                      <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                      <span>{feature.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <p className="text-center text-xs text-slate-400 mt-6">
            © 2024 ContentForge AI. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  )
}
