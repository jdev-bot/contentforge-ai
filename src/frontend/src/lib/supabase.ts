import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

// Client-side Supabase client with cookie-based session persistence
// This ensures the middleware can read auth state from cookies
export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    storage: {
      getItem: (key: string) => {
        if (typeof window === 'undefined') return null
        // Try cookie first, fallback to localStorage
        const cookieMatch = document.cookie.match(new RegExp(`(^| )${key}=([^;]+)`))
        if (cookieMatch) return decodeURIComponent(cookieMatch[2])
        return localStorage.getItem(key)
      },
      setItem: (key: string, value: string) => {
        if (typeof window === 'undefined') return
        // Store in both localStorage and cookie so middleware can read it
        localStorage.setItem(key, value)
        document.cookie = `${key}=${encodeURIComponent(value)}; path=/; max-age=${60 * 60 * 24 * 365}; SameSite=Lax`
      },
      removeItem: (key: string) => {
        if (typeof window === 'undefined') return
        localStorage.removeItem(key)
        document.cookie = `${key}=; path=/; max-age=0`
      },
    },
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
})

export type AuthUser = {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) return null
  
  return {
    id: user.id,
    email: user.email || '',
    full_name: user.user_metadata?.full_name || '',
    avatar_url: user.user_metadata?.avatar_url || '',
  }
}

export async function signUp(email: string, password: string, fullName: string) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        full_name: fullName,
      },
    },
  })
  
  return { data, error }
}

export async function signIn(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  
  return { data, error }
}

export async function signOut() {
  const { error } = await supabase.auth.signOut()
  return { error }
}