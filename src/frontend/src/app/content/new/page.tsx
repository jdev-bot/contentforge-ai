import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import ContentNewClient from './ContentNewClient'

export type AuthUser = {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
}

async function getServerUser(): Promise<AuthUser | null> {
  const cookieStore = await cookies()
  
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => cookieStore.set(name, value))
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) return null
  
  return {
    id: user.id,
    email: user.email || '',
    full_name: user.user_metadata?.full_name || '',
    avatar_url: user.user_metadata?.avatar_url || '',
  }
}

export default async function NewContentPage() {
  const user = await getServerUser()
  
  if (!user) {
    redirect('/login')
  }
  
  return <ContentNewClient user={user} />
}