'use client'

import { useState, useCallback, useEffect } from 'react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Input } from './ui/Input'
import { useToast } from '../hooks/useToast'
import { RefreshCw } from 'lucide-react'
import {
  createABExperiment,
  listABExperiments,
  updateABExperiment,
  deleteABExperiment,
  getABExperiment,
  type ABExperiment,
  type ABExperimentDetail,
} from '@/lib/api'

interface DisplayTest {
  id: string
  name: string
  contentId: string | null
  variantA: string
  variantB: string
  platform: string
  status: 'draft' | 'running' | 'paused' | 'completed' | 'stopped'
  startDate?: string
  endDate?: string
  duration: number
  results?: {
    variantA: { impressions: number; engagements: number; clicks: number; engagementRate: number; clickRate: number }
    variantB: { impressions: number; engagements: number; clicks: number; engagementRate: number; clickRate: number }
    winner: 'A' | 'B' | 'tie'
    confidence: number
  }
}

function mapExperimentToDisplay(exp: ABExperiment, detail?: ABExperimentDetail): DisplayTest {
  return {
    id: exp.id,
    name: exp.name,
    contentId: exp.content_id,
    variantA: exp.variant_a,
    variantB: exp.variant_b,
    platform: exp.platform,
    status: exp.status,
    startDate: exp.started_at || undefined,
    endDate: exp.ended_at || undefined,
    duration: exp.duration_days,
    results: detail?.winner
      ? {
          variantA: {
            impressions: detail.variant_a_results?.impressions ?? 0,
            engagements: detail.variant_a_results?.engagements ?? 0,
            clicks: detail.variant_a_results?.clicks ?? 0,
            engagementRate: detail.variant_a_results?.engagementRate ?? 0,
            clickRate: detail.variant_a_results?.clickRate ?? 0,
          },
          variantB: {
            impressions: detail.variant_b_results?.impressions ?? 0,
            engagements: detail.variant_b_results?.engagements ?? 0,
            clicks: detail.variant_b_results?.clicks ?? 0,
            engagementRate: detail.variant_b_results?.engagementRate ?? 0,
            clickRate: detail.variant_b_results?.clickRate ?? 0,
          },
          winner: (detail.winner === 'A' ? 'A' : detail.winner === 'B' ? 'B' : 'tie') as 'A' | 'B' | 'tie',
          confidence: detail.confidence ?? 0,
        }
      : undefined,
  }
}

export default function ABTestingFramework() {
  const { showToast } = useToast()
  const [tests, setTests] = useState<DisplayTest[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [selectedTest, setSelectedTest] = useState<DisplayTest | null>(null)
  const [newTest, setNewTest] = useState({
    name: '',
    variantA: '',
    variantB: '',
    platform: 'twitter',
    duration: 7,
  })
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  // Fetch experiments from API
  const fetchExperiments = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await listABExperiments()
      const mapped: DisplayTest[] = data.experiments.map((exp) => mapExperimentToDisplay(exp))
      setTests(mapped)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load experiments')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchExperiments()
  }, [fetchExperiments])

  const createTest = useCallback(async () => {
    if (!newTest.name || !newTest.variantA || !newTest.variantB) {
      showToast('Please fill in all fields', 'error')
      return
    }

    try {
      const exp = await createABExperiment({
        name: newTest.name,
        variant_a: newTest.variantA,
        variant_b: newTest.variantB,
        platform: newTest.platform,
        duration_days: newTest.duration,
      })
      setTests((prev) => [...prev, mapExperimentToDisplay(exp)])
      setIsCreating(false)
      setNewTest({ name: '', variantA: '', variantB: '', platform: 'twitter', duration: 7 })
      showToast('A/B test created successfully', 'success')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to create test', 'error')
    }
  }, [newTest, showToast])

  const startTest = useCallback(async (testId: string) => {
    try {
      setActionLoading(testId)
      const exp = await updateABExperiment(testId, { status: 'running' })
      setTests((prev) =>
        prev.map((t) =>
          t.id === testId ? mapExperimentToDisplay(exp) : t
        )
      )
      if (selectedTest?.id === testId) {
        setSelectedTest(mapExperimentToDisplay(exp))
      }
      showToast('Test started', 'success')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to start test', 'error')
    } finally {
      setActionLoading(null)
    }
  }, [showToast, selectedTest])

  const pauseTest = useCallback(async (testId: string) => {
    try {
      setActionLoading(testId)
      const exp = await updateABExperiment(testId, { status: 'paused' })
      setTests((prev) =>
        prev.map((t) =>
          t.id === testId ? { ...t, status: 'paused' as const } : t
        )
      )
      if (selectedTest?.id === testId) {
        setSelectedTest((prev) => prev ? { ...prev, status: 'paused' as const } : null)
      }
      showToast('Test paused', 'info')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to pause test', 'error')
    } finally {
      setActionLoading(null)
    }
  }, [showToast, selectedTest])

  const stopTest = useCallback(async (testId: string) => {
    try {
      setActionLoading(testId)
      const exp = await updateABExperiment(testId, { status: 'stopped' })
      setTests((prev) =>
        prev.map((t) =>
          t.id === testId ? { ...t, status: 'stopped' as const } : t
        )
      )
      if (selectedTest?.id === testId) {
        setSelectedTest((prev) => prev ? { ...prev, status: 'stopped' as const } : null)
      }
      showToast('Test stopped', 'info')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to stop test', 'error')
    } finally {
      setActionLoading(null)
    }
  }, [showToast, selectedTest])

  const handleDeleteTest = useCallback(async (testId: string) => {
    try {
      await deleteABExperiment(testId)
      setTests((prev) => prev.filter((t) => t.id !== testId))
      if (selectedTest?.id === testId) setSelectedTest(null)
      showToast('Test deleted', 'success')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to delete test', 'error')
    }
  }, [showToast, selectedTest])

  const handleSelectTest = useCallback(async (test: DisplayTest) => {
    setSelectedTest(test)
    // Fetch full details including results
    try {
      const detail = await getABExperiment(test.id)
      const full = mapExperimentToDisplay(detail, detail)
      setSelectedTest(full)
    } catch {
      // Keep the basic view
    }
  }, [])

  const getStatusBadge = (status: DisplayTest['status']) => {
    const styles: Record<string, string> = {
      draft: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
      running: 'bg-green-100 text-green-700',
      paused: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-blue-100 text-blue-700',
      stopped: 'bg-rose-100 text-rose-700',
    }
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status] || styles.draft}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 dark:text-white">
            🧪 A/B Testing Framework
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">Test content variations to optimize performance</p>
        </div>
        <Button onClick={() => setIsCreating(true)} size="sm" disabled={isLoading}>
          + New Test
        </Button>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-6 w-6 text-slate-400 animate-spin" />
          <span className="ml-3 text-slate-500">Loading experiments...</span>
        </div>
      )}

      {error && !isLoading && (
        <div className="p-4 bg-rose-50 dark:bg-rose-900/20 rounded-lg mb-4">
          <p className="text-sm text-rose-700 dark:text-rose-300">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchExperiments} className="mt-2">Retry</Button>
        </div>
      )}

      {!isLoading && !error && isCreating ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">Create New A/B Test</h4>
            <button
              onClick={() => setIsCreating(false)}
              className="text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
            >
              Cancel
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-600 mb-2">
              Test Name
            </label>
            <Input
              value={newTest.name}
              onChange={(e) => setNewTest((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Headline Test April 2026"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-600 mb-2">
                Variant A
              </label>
              <textarea
                value={newTest.variantA}
                onChange={(e) => setNewTest((prev) => ({ ...prev, variantA: e.target.value }))}
                placeholder="Control version..."
                className="w-full h-32 px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-600 mb-2">
                Variant B
              </label>
              <textarea
                value={newTest.variantB}
                onChange={(e) => setNewTest((prev) => ({ ...prev, variantB: e.target.value }))}
                placeholder="Test version..."
                className="w-full h-32 px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
              />
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-600 mb-2">
                Platform
              </label>
              <select
                value={newTest.platform}
                onChange={(e) => setNewTest((prev) => ({ ...prev, platform: e.target.value }))}
                className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 dark:border-gray-600 bg-white dark:bg-gray-800"
              >
                <option value="twitter">Twitter/X</option>
                <option value="linkedin">LinkedIn</option>
                <option value="facebook">Facebook</option>
                <option value="email">Email</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-600 mb-2">
                Duration (days)
              </label>
              <Input
                type="number"
                min={1}
                max={90}
                value={newTest.duration}
                onChange={(e) =>
                  setNewTest((prev) => ({ ...prev, duration: parseInt(e.target.value) || 7 }))
                }
              />
            </div>
          </div>

          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setIsCreating(false)} className="flex-1">
              Cancel
            </Button>
            <Button onClick={createTest} className="flex-1">
              Create Test
            </Button>
          </div>
        </div>
      ) : !isLoading && !error && selectedTest ? (
        <div className="space-y-6">
          <button
            onClick={() => setSelectedTest(null)}
            className="text-blue-600 hover:underline text-sm"
          >
            ← Back to tests
          </button>

          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-xl font-bold mb-2">{selectedTest.name}</h4>
              <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
                <span>{getStatusBadge(selectedTest.status)}</span>
                <span>Platform: {selectedTest.platform}</span>
                <span>Duration: {selectedTest.duration} days</span>
              </div>
            </div>
            <div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDeleteTest(selectedTest.id)}
                className="text-rose-600 hover:text-rose-700"
                disabled={!!actionLoading}
              >
                Delete
              </Button>
            </div>
          </div>

          {/* Variants Comparison */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card className={`p-4 ${selectedTest.results?.winner === 'A' ? 'border-green-500 border-2' : ''}`}>
              <div className="flex items-center justify-between mb-3">
                <span className="font-bold">Variant A</span>
                {selectedTest.results?.winner === 'A' && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-bold">
                    🏆 Winner
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-500 mb-4 p-3 bg-slate-50 dark:bg-gray-800 rounded">
                {selectedTest.variantA}
              </p>

              {selectedTest.results ? (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Impressions</span>
                    <span className="font-medium">
                      {selectedTest.results.variantA.impressions.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Engagements</span>
                    <span className="font-medium">
                      {selectedTest.results.variantA.engagements.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Engagement Rate</span>
                    <span className="font-medium text-blue-600">
                      {selectedTest.results.variantA.engagementRate}%
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500 dark:text-slate-400 italic">Waiting for results...</p>
              )}
            </Card>

            <Card className={`p-4 ${selectedTest.results?.winner === 'B' ? 'border-green-500 border-2' : ''}`}>
              <div className="flex items-center justify-between mb-3">
                <span className="font-bold">Variant B</span>
                {selectedTest.results?.winner === 'B' && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-bold">
                    🏆 Winner
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-500 mb-4 p-3 bg-slate-50 dark:bg-gray-800 rounded">
                {selectedTest.variantB}
              </p>

              {selectedTest.results ? (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Impressions</span>
                    <span className="font-medium">
                      {selectedTest.results.variantB.impressions.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Engagements</span>
                    <span className="font-medium">
                      {selectedTest.results.variantB.engagements.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Engagement Rate</span>
                    <span className="font-medium text-blue-600">
                      {selectedTest.results.variantB.engagementRate}%
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500 dark:text-slate-400 italic">Waiting for results...</p>
              )}
            </Card>
          </div>

          {selectedTest.results && (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">📊</span>
                <span className="font-medium">
                  Statistical Confidence: {(selectedTest.results.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-500">
                {selectedTest.results.winner === 'A'
                  ? 'Variant A performed significantly better than Variant B.'
                  : selectedTest.results.winner === 'B'
                  ? 'Variant B performed significantly better than Variant A.'
                  : 'Both variants performed similarly. Consider running a longer test.'}
              </p>
            </div>
          )}

          {/* Test Controls */}
          <div className="flex gap-3">
            {selectedTest.status === 'draft' && (
              <Button
                onClick={() => startTest(selectedTest.id)}
                className="flex-1"
                disabled={!!actionLoading}
              >
                {actionLoading === selectedTest.id ? 'Starting...' : 'Start Test'}
              </Button>
            )}
            {selectedTest.status === 'running' && (
              <Button
                onClick={() => pauseTest(selectedTest.id)}
                variant="secondary"
                className="flex-1"
                disabled={!!actionLoading}
              >
                {actionLoading === selectedTest.id ? 'Pausing...' : 'Pause Test'}
              </Button>
            )}
            {selectedTest.status === 'paused' && (
              <Button
                onClick={() => startTest(selectedTest.id)}
                className="flex-1"
                disabled={!!actionLoading}
              >
                {actionLoading === selectedTest.id ? 'Resuming...' : 'Resume Test'}
              </Button>
            )}
            {(selectedTest.status === 'running' || selectedTest.status === 'paused') && (
              <Button
                onClick={() => stopTest(selectedTest.id)}
                variant="outline"
                className="flex-1"
                disabled={!!actionLoading}
              >
                Stop Test
              </Button>
            )}
            <Button variant="secondary" onClick={() => setSelectedTest(null)} className="flex-1">
              Close
            </Button>
          </div>
        </div>
      ) : !isLoading && !error && (
        <div className="space-y-4">
          {tests.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">🧪</div>
              <p className="text-slate-500 dark:text-slate-400">No tests yet. Create your first A/B test to optimize content performance.</p>
            </div>
          ) : (
            tests.map((test) => (
              <Card
                key={test.id}
                onClick={() => handleSelectTest(test)}
                className="p-4 cursor-pointer hover:border-blue-500 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold">{test.name}</span>
                      {getStatusBadge(test.status)}
                    </div>
                    <div className="text-sm text-slate-500 dark:text-slate-400">
                      Platform: {test.platform} • Duration: {test.duration} days
                      {test.startDate && ` • Started: ${test.startDate}`}
                    </div>
                  </div>
                  <div className="text-right">
                    {test.results ? (
                      <div className="text-sm">
                        <span className="text-slate-500 dark:text-slate-400">Winner: </span>
                        <span
                          className={`font-bold ${
                            test.results.winner === 'A'
                              ? 'text-blue-600'
                              : test.results.winner === 'B'
                              ? 'text-purple-600'
                              : 'text-slate-600 dark:text-slate-400'
                          }`}
                        >
                          Variant {test.results.winner}
                        </span>
                      </div>
                    ) : (
                      <div className="text-sm text-slate-500 dark:text-slate-400">In Progress</div>
                    )}
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </Card>
  )
}