'use client'

import { useEffect, useState } from 'react'
import { listDistributions, Distribution } from '@/lib/api'
import { formatApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { Calendar, ExternalLink, Trash2 } from 'lucide-react'

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
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-4">
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
      cancelled: 'bg-gray-100 text-gray-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Distributions</h2>
        <Button variant="outline" onClick={loadDistributions}>
          Refresh
        </Button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {distributions.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Calendar className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No distributions yet</h3>
          <p className="mt-2 text-gray-500 max-w-sm mx-auto">
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
                    <span className="text-sm text-gray-600 capitalize">{dist.platform}</span>
                    {dist.scheduled_at && (
                      <span className="text-sm text-gray-500">
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
                      <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
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
