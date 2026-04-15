'use client'

import { useState, useCallback } from 'react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Input } from './ui/Input'
import { useToast } from '../hooks/useToast'

interface ABTest {
  id: string
  name: string
  contentId: string
  variantA: string
  variantB: string
  platform: string
  status: 'draft' | 'running' | 'paused' | 'completed'
  startDate?: string
  endDate?: string
  duration: number // days
  results?: {
    variantA: TestResults
    variantB: TestResults
    winner: 'A' | 'B' | 'tie'
    confidence: number
  }
}

interface TestResults {
  impressions: number
  engagements: number
  clicks: number
  engagementRate: number
  clickRate: number
}

const MOCK_TESTS: ABTest[] = [
  {
    id: '1',
    name: 'Hook Variation Test',
    contentId: 'content-1',
    variantA: 'Discover the secret to...',
    variantB: 'Learn how to...',
    platform: 'twitter',
    status: 'completed',
    startDate: '2026-04-01',
    endDate: '2026-04-08',
    duration: 7,
    results: {
      variantA: {
        impressions: 12450,
        engagements: 892,
        clicks: 156,
        engagementRate: 7.16,
        clickRate: 1.25,
      },
      variantB: {
        impressions: 12380,
        engagements: 745,
        clicks: 124,
        engagementRate: 6.02,
        clickRate: 1.0,
      },
      winner: 'A',
      confidence: 0.94,
    },
  },
  {
    id: '2',
    name: 'CTA Button Test',
    contentId: 'content-2',
    variantA: 'Get Started Now',
    variantB: 'Start Your Free Trial',
    platform: 'linkedin',
    status: 'running',
    duration: 14,
  },
]

export default function ABTestingFramework() {
  const { showToast } = useToast()
  const [tests, setTests] = useState<ABTest[]>(MOCK_TESTS)
  const [isCreating, setIsCreating] = useState(false)
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null)
  const [newTest, setNewTest] = useState({
    name: '',
    variantA: '',
    variantB: '',
    platform: 'twitter',
    duration: 7,
  })

  const createTest = useCallback(() => {
    if (!newTest.name || !newTest.variantA || !newTest.variantB) {
      showToast('Please fill in all fields', 'error')
      return
    }

    const test: ABTest = {
      id: `test-${Date.now()}`,
      name: newTest.name,
      contentId: `content-${Date.now()}`,
      variantA: newTest.variantA,
      variantB: newTest.variantB,
      platform: newTest.platform,
      status: 'draft',
      duration: newTest.duration,
    }

    setTests((prev) => [...prev, test])
    setIsCreating(false)
    setNewTest({ name: '', variantA: '', variantB: '', platform: 'twitter', duration: 7 })
    showToast('A/B test created successfully', 'success')
  }, [newTest, showToast])

  const startTest = useCallback((testId: string) => {
    setTests((prev) =>
      prev.map((test) =>
        test.id === testId
          ? {
              ...test,
              status: 'running' as const,
              startDate: new Date().toISOString().split('T')[0],
            }
          : test
      )
    )
    showToast('Test started', 'success')
  }, [showToast])

  const pauseTest = useCallback((testId: string) => {
    setTests((prev) =>
      prev.map((test) =>
        test.id === testId ? { ...test, status: 'paused' as const } : test
      )
    )
    showToast('Test paused', 'info')
  }, [showToast])

  const getStatusBadge = (status: ABTest['status']) => {
    const styles = {
      draft: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
      running: 'bg-green-100 text-green-700',
      paused: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-blue-100 text-blue-700',
    }
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status]}`}>
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
        <Button onClick={() => setIsCreating(true)} size="sm">
          + New Test
        </Button>
      </div>

      {isCreating ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">Create New A/B Test</h4>
            <button
              onClick={() => setIsCreating(false)}
              className="text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:text-slate-300"
            >
              Cancel
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-300 dark:text-slate-600 mb-2">
              Test Name
            </label>
            <Input
              value={newTest.name}
              onChange={(e) => setNewTest((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Headline Test April 2026"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-300 dark:text-slate-600 mb-2">
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
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-300 dark:text-slate-600 mb-2">
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
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-300 dark:text-slate-600 mb-2">
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
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-300 dark:text-slate-600 mb-2">
                Duration (days)
              </label>
              <Input
                type="number"
                min={1}
                max={30}
                value={newTest.duration}
                onChange={(e) =>
                  setNewTest((prev) => ({ ...prev, duration: parseInt(e.target.value) }))
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
      ) : selectedTest ? (
        <div className="space-y-6">
          <button
            onClick={() => setSelectedTest(null)}
            className="text-blue-600 hover:underline text-sm"
          >
            ← Back to tests
          </button>

          <div>
            <h4 className="text-xl font-bold mb-2">{selectedTest.name}</h4>
            <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
              <span>{getStatusBadge(selectedTest.status)}</span>
              <span>Platform: {selectedTest.platform}</span>
              <span>Duration: {selectedTest.duration} days</span>
            </div>
          </div>

          {/* Variants Comparison */}
          <div className="grid grid-cols-2 gap-4">
            <Card className={`p-4 ${selectedTest.results?.winner === 'A' ? 'border-green-500 border-2' : ''}`}>
              <div className="flex items-center justify-between mb-3">
                <span className="font-bold">Variant A</span>
                {selectedTest.results?.winner === 'A' && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-bold">
                    🏆 Winner
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500 mb-4 p-3 bg-slate-50 dark:bg-slate-900 dark:bg-gray-800 rounded">
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
              <p className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500 mb-4 p-3 bg-slate-50 dark:bg-slate-900 dark:bg-gray-800 rounded">
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
              <p className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500">
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
              <Button onClick={() => startTest(selectedTest.id)} className="flex-1">
                Start Test
              </Button>
            )}
            {selectedTest.status === 'running' && (
              <Button onClick={() => pauseTest(selectedTest.id)} variant="secondary" className="flex-1">
                Pause Test
              </Button>
            )}
            {selectedTest.status === 'paused' && (
              <Button onClick={() => startTest(selectedTest.id)} className="flex-1">
                Resume Test
              </Button>
            )}
            <Button variant="secondary" onClick={() => setSelectedTest(null)} className="flex-1">
              Close
            </Button>
          </div>
        </div>
      ) : (
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
                onClick={() => setSelectedTest(test)}
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
