'use client'

import { AuthUser } from '@/lib/supabase'
import ContentDetailPanel from '@/components/ContentDetailPanel'
import { useRouter } from 'next/navigation'

export default function ContentDetailClient({ id, user }: { id: string; user: AuthUser }) {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ContentDetailPanel
          id={id}
          user={user}
          onBack={() => router.back()}
        />
      </main>
    </div>
  )
}