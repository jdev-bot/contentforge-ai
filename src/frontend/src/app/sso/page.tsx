'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  ChevronRight,
  Link2,
  Unlink,
  AlertCircle,
  CheckCircle,
  Loader2,
  ArrowLeft,
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  getAvailableSSOProviders,
  initiateSSOLogin,
  handleSSOCallback,
  getUserSSOIdentities,
  unlinkSSOIdentity,
  type AvailableSSOProvider,
  type SSOIdentity,
} from '@/lib/api'

// Provider icon mapping
const PROVIDER_ICONS: Record<string, React.ReactNode> = {
  google: (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  ),
  microsoft: (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path fill="#F25022" d="M1 1h10v10H1z" />
      <path fill="#00A4EF" d="M1 13h10v10H1z" />
      <path fill="#7FBA00" d="M13 1h10v10H13z" />
      <path fill="#FFB900" d="M13 13h10v10H13z" />
    </svg>
  ),
  okta: (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="#007DC1" strokeWidth="2.5" fill="none" />
      <circle cx="12" cy="12" r="5" fill="#007DC1" />
    </svg>
  ),
  custom: <Shield className="w-5 h-5 text-slate-400" />,
}

const PROVIDER_COLORS: Record<string, string> = {
  google: 'from-blue-500 to-red-500',
  microsoft: 'from-blue-600 to-green-500',
  okta: 'from-cyan-500 to-blue-600',
  custom: 'from-purple-500 to-indigo-600',
}

type ViewState = 'select' | 'callback' | 'identities' | 'link-success'

export default function SSOLoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()

  const [providers, setProviders] = useState<AvailableSSOProvider[]>([])
  const [identities, setIdentities] = useState<SSOIdentity[]>([])
  const [loading, setLoading] = useState(true)
  const [initiatingProvider, setInitiatingProvider] = useState<string | null>(null)
  const [view, setView] = useState<ViewState>('select')
  const [linkMode, setLinkMode] = useState(false)
  const [callbackResult, setCallbackResult] = useState<{
    action: string
    email: string
    full_name: string | null
    is_new_user: boolean
  } | null>(null)

  // Handle SSO callback from URL params
  const callbackState = searchParams.get('state')
  const callbackCode = searchParams.get('code')
  const callbackError = searchParams.get('error')

  useEffect(() => {
    loadProviders()
  }, [])

  useEffect(() => {
    if (callbackState && callbackCode && !callbackResult) {
      handleCallback(callbackState, callbackCode)
    }
    if (callbackError) {
      toast({
        title: 'SSO Login Failed',
        description: searchParams.get('error_description') || callbackError,
        variant: 'error',
      })
    }
  }, [callbackState, callbackCode, callbackError])

  const loadProviders = async () => {
    try {
      setLoading(true)
      const result = await getAvailableSSOProviders()
      setProviders(result)
    } catch {
      toast({ title: 'Failed to load SSO providers', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const loadIdentities = async () => {
    try {
      const result = await getUserSSOIdentities()
      setIdentities(result)
      setView('identities')
    } catch {
      toast({ title: 'Failed to load SSO identities', variant: 'error' })
    }
  }

  const handleSSOInitiate = async (providerName: string) => {
    setInitiatingProvider(providerName)
    try {
      const redirectUri = `${window.location.origin}/sso`
      const result = await initiateSSOLogin({
        provider: providerName,
        redirect_uri: redirectUri,
        link_user: linkMode,
      })
      // Redirect the user to the IdP
      window.location.href = result.authorization_url
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to initiate SSO login'
      toast({ title: 'SSO Login Failed', description: message, variant: 'error' })
      setInitiatingProvider(null)
    }
  }

  const handleCallback = async (state: string, code: string) => {
    setLoading(true)
    setView('callback')
    try {
      const result = await handleSSOCallback({ state, code })
      setCallbackResult(result)

      if (result.action === 'register' || result.action === 'login') {
        toast({
          title: result.is_new_user ? 'Account Created' : 'Login Successful',
          description: `Welcome${result.full_name ? `, ${result.full_name}` : ''}!`,
          variant: 'success',
        })
        // Redirect to dashboard after short delay
        setTimeout(() => {
          router.push('/dashboard')
          router.refresh()
        }, 1500)
      } else if (result.action === 'linked') {
        setView('link-success')
        toast({
          title: 'SSO Account Linked',
          description: 'Your SSO identity has been linked to your account.',
          variant: 'success',
        })
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'SSO callback failed'
      toast({ title: 'SSO Login Failed', description: message, variant: 'error' })
      setView('select')
    } finally {
      setLoading(false)
    }
  }

  const handleUnlink = async (identityId: string) => {
    try {
      await unlinkSSOIdentity(identityId)
      toast({ title: 'SSO Identity Unlinked', variant: 'success' })
      loadIdentities()
    } catch {
      toast({ title: 'Failed to unlink identity', variant: 'error' })
    }
  }

  // ── Render: Callback Processing ─────────────────────────────────
  if (view === 'callback') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <Loader2 className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Processing SSO Login</h2>
          <p className="text-slate-400">Verifying your identity...</p>
        </motion.div>
      </div>
    )
  }

  // ── Render: Link Success ────────────────────────────────────────
  if (view === 'link-success' && callbackResult) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <Card className="bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 shadow-2xl">
            <CardContent className="pt-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
                className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <CheckCircle className="w-8 h-8 text-emerald-400" />
              </motion.div>
              <h2 className="text-2xl font-bold text-white mb-2">SSO Account Linked</h2>
              <p className="text-slate-400 mb-6">
                {callbackResult.email} has been linked to your account.
              </p>
              <Button
                variant="primary"
                className="w-full"
                onClick={() => router.push('/settings')}
              >
                Back to Settings
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    )
  }

  // ── Render: Identities Management ────────────────────────────────
  if (view === 'identities') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-lg"
        >
          <Card className="bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 shadow-2xl">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <button
                  onClick={() => setView('select')}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <CardTitle className="text-xl text-white">Linked SSO Accounts</CardTitle>
              </div>
              <CardDescription>Manage your connected SSO identities</CardDescription>
            </CardHeader>
            <CardContent>
              <AnimatePresence>
                {identities.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-8"
                  >
                    <Link2 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400">No SSO identities linked yet</p>
                  </motion.div>
                ) : (
                  <div className="space-y-3">
                    {identities.map((identity, idx) => (
                      <motion.div
                        key={identity.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="flex items-center justify-between p-4 rounded-xl bg-slate-800/60 border border-slate-700/40"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center">
                            {PROVIDER_ICONS[identity.provider] || PROVIDER_ICONS.custom}
                          </div>
                          <div>
                            <p className="font-medium text-white">{identity.provider}</p>
                            <p className="text-sm text-slate-400">{identity.email || 'No email'}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => handleUnlink(identity.id)}
                          className="p-2 rounded-lg hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors"
                          title="Unlink identity"
                        >
                          <Unlink className="w-4 h-4" />
                        </button>
                      </motion.div>
                    ))}
                  </div>
                )}
              </AnimatePresence>

              <div className="mt-6 pt-6 border-t border-slate-700/50">
                <Button
                  variant="secondary"
                  className="w-full"
                  onClick={() => {
                    setLinkMode(true)
                    setView('select')
                  }}
                >
                  <Link2 className="w-4 h-4 mr-2" />
                  Link Another Provider
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    )
  }

  // ── Render: Provider Selection (default) ────────────────────────
  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Decorative */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-violet-600 to-fuchsia-600">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
          <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full blur-xl animate-float" />
          <div className="absolute bottom-40 right-20 w-48 h-48 bg-violet-500/20 rounded-full blur-2xl animate-float" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/3 w-24 h-24 bg-fuchsia-500/20 rounded-full blur-xl animate-float" style={{ animationDelay: '2s' }} />
        </div>

        <div className="relative z-10 flex flex-col justify-center px-16 text-white">
          <Badge variant="default" className="bg-white/20 text-white border-white/30 mb-6 w-fit">
            <Shield className="w-3 h-3 mr-1" />
            Enterprise SSO
          </Badge>
          <h1 className="text-5xl font-bold mb-6 leading-tight">
            Single Sign-On
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-pink-300">
              Authentication
            </span>
          </h1>
          <p className="text-xl text-blue-100 mb-10 max-w-md">
            Sign in securely with your organization&apos;s identity provider. No new passwords to remember.
          </p>

          <div className="space-y-4">
            {[
              { icon: Shield, text: 'Enterprise-grade OIDC security' },
              { icon: Link2, text: 'Link multiple SSO providers' },
              { icon: CheckCircle, text: 'Automatic account provisioning' },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-center gap-4 p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20"
              >
                <div className="p-2 bg-white/20 rounded-lg">
                  <feature.icon className="w-5 h-5" />
                </div>
                <span className="font-medium">{feature.text}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Panel - SSO Selection */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-8 bg-slate-950">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
              ContentForge
            </span>
            <p className="text-slate-400 mt-2">SSO Authentication</p>
          </div>

          <Card className="bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 shadow-2xl">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl font-bold text-white">
                {linkMode ? 'Link SSO Provider' : 'Sign in with SSO'}
              </CardTitle>
              <CardDescription className="text-slate-400 mt-2">
                {linkMode
                  ? 'Connect an SSO identity to your existing account'
                  : 'Choose your identity provider to continue'}
              </CardDescription>
            </CardHeader>

            <CardContent className="pt-6">
              {loading ? (
                <div className="flex flex-col items-center py-8">
                  <Loader2 className="w-8 h-8 text-blue-400 animate-spin mb-3" />
                  <p className="text-slate-400">Loading providers...</p>
                </div>
              ) : providers.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-8"
                >
                  <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                  <p className="text-slate-400 mb-2">No SSO providers configured</p>
                  <p className="text-sm text-slate-500">
                    Contact your administrator to set up SSO authentication.
                  </p>
                </motion.div>
              ) : (
                <div className="space-y-3">
                  <AnimatePresence>
                    {providers.map((provider, idx) => (
                      <motion.button
                        key={provider.name}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        onClick={() => handleSSOInitiate(provider.name)}
                        disabled={initiatingProvider !== null}
                        className={cn(
                          'w-full flex items-center gap-4 p-4 rounded-xl',
                          'border border-slate-700/50',
                          'bg-slate-800/60 hover:bg-slate-800',
                          'hover:border-slate-600/60',
                          'transition-all duration-200',
                          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900',
                          'disabled:opacity-50 disabled:cursor-not-allowed',
                          'group'
                        )}
                      >
                        <div className={cn(
                          'w-10 h-10 rounded-lg flex items-center justify-center',
                          'bg-gradient-to-br',
                          PROVIDER_COLORS[provider.name] || PROVIDER_COLORS.custom,
                          'opacity-80 group-hover:opacity-100 transition-opacity'
                        )}>
                          {PROVIDER_ICONS[provider.name] || PROVIDER_ICONS.custom}
                        </div>
                        <div className="flex-1 text-left">
                          <p className="font-semibold text-white">
                            {provider.display_name}
                          </p>
                          <p className="text-sm text-slate-400">
                            Continue with {provider.display_name}
                          </p>
                        </div>
                        {initiatingProvider === provider.name ? (
                          <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-slate-300 transition-colors" />
                        )}
                      </motion.button>
                    ))}
                  </AnimatePresence>
                </div>
              )}

              <div className="mt-6 pt-6 border-t border-slate-700/50">
                {linkMode ? (
                  <Button
                    variant="ghost"
                    className="w-full text-slate-400"
                    onClick={() => setLinkMode(false)}
                  >
                    Cancel
                  </Button>
                ) : (
                  <div className="space-y-3">
                    <Button
                      variant="secondary"
                      className="w-full"
                      onClick={loadIdentities}
                    >
                      <Link2 className="w-4 h-4 mr-2" />
                      Manage Linked Providers
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full text-slate-400"
                      onClick={() => router.push('/login')}
                    >
                      <ArrowLeft className="w-4 h-4 mr-2" />
                      Back to Email Login
                    </Button>
                  </div>
                )}
              </div>

              {/* Footer */}
              <p className="text-center text-xs text-slate-600 mt-6">
                Secured with OpenID Connect · PKCE enabled
              </p>
            </CardContent>
          </Card>

          <p className="text-center text-xs text-slate-600 mt-6">
            © 2024 ContentForge AI. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  )
}