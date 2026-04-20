'use client'

import { useEffect, useState } from 'react'
import { listDistributions, Distribution } from '@/lib/api'
import { formatApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { Calendar, ExternalLink, Trash2, Share2 } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'

export default function DistributionsTab() {
  const [distributions, setDistributions] = useState<Distribution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDistributions()
  }, [])

  async function loadDistributions() {
    try {
      const data = await listDistributions()
      setDistributions(data)
    } catch (err: unknown) {
      setError(formatApiError(err, 'Failed to load distributions'))
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-10 w-24" />
        </div>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
              <div className="flex items-center gap-4">
                <Skeleton className="h-6 w-20 rounded-full" />
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-32" />
                <div className="ml-auto">
                  <Skeleton className="h-8 w-8 rounded-lg" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-700',
      scheduled: 'bg-blue-100 text-blue-700',
      publishing: 'bg-purple-100 text-purple-700',
      published: 'bg-green-100 text-green-700',
      failed: 'bg-red-100 text-red-700',
      cancelled: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
    }
    return colors[status] || 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Distributions"
        description="Publish and distribute content across platforms"
        icon={<Share2 className="w-5 h-5 text-blue-600" />}
        actions={
          <Button variant="outline" onClick={loadDistributions}>
            Refresh
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-red-500/10 dark:bg-red-500/20 border border-red-500/50 dark:border-red-500/50 rounded-lg">
          <p className="text-sm text-red-500 dark:text-red-400">{error}</p>
        </div>
      )}

      {distributions.length === 0 ? (
        <div className="bg-slate-50 dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-12 text-center">
          <Calendar className="mx-auto h-12 w-12 text-slate-400 dark:text-slate-500" />
          <h3 className="mt-4 text-lg font-medium text-slate-900 dark:text-slate-100">No distributions yet</h3>
          <p className="mt-2 text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            Generated assets can be scheduled for publishing here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {distributions.map((dist) => (
            <Card key={dist.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(dist.status)}`}>
                      {dist.status}
                    </span>
                    <span className="text-sm text-slate-600 dark:text-slate-400 capitalize">{dist.platform}</span>
                    {dist.scheduled_at && (
                      <span className="text-sm text-slate-500 dark:text-slate-400">
                        Scheduled: {new Date(dist.scheduled_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {dist.published_url && (
                      <a
                        href={dist.published_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                    {dist.status !== 'published' && (
                      <button className="p-2 text-red-500 dark:text-red-400 hover:bg-red-50 rounded-lg">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
