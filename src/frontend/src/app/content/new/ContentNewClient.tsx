'use client'

import { AuthUser } from '@/lib/supabase'
import ContentCreatePanel from '@/components/ContentCreatePanel'
import { ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function ContentNewClient({ user }: { user: AuthUser }) {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => router.back()}
              className="mr-4 p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <span className="text-xl font-bold">New Content</span>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ContentCreatePanel
          user={user}
          onBack={() => router.back()}
          onContentCreated={(id) => router.push(`/content/${id}`)}
        />
      </main>
    </div>
  )
}