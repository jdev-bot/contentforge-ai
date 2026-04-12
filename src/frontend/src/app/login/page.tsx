'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { signIn, signUp } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Sparkles, Zap, Shield, CheckCircle, Github, Twitter, Mail } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const router = useRouter()

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
      router.push('/')
      router.refresh()
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
                  : 'Start transforming your content with AI'
                }
              </CardDescription>
            </CardHeader>
            
            <CardContent className="pt-6">
              {/* Social Login */}
              <div className="grid grid-cols-3 gap-3 mb-6">
                {[
                  { icon: Github, label: 'GitHub' },
                  { icon: Twitter, label: 'Twitter' },
                  { icon: Mail, label: 'Email' },
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
                    <provider.icon className="w-5 h-5" />
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
                {!isLogin && (
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
