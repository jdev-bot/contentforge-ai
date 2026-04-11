import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/lib/supabase'
import Dashboard from '@/components/Dashboard'

export default async function Home() {
  const user = await getCurrentUser()
  
  if (!user) {
    redirect('/login')
  }
  
  return <Dashboard user={user} />
}
