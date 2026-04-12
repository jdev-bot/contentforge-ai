'use client'

import { useState, useCallback } from 'react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Input } from './ui/Input'
import { useToast } from '../hooks/useToast'

interface EngagementPredictionProps {
  contentId?: string
  contentText?: string
  platform?: string
}

interface PredictionResult {
  score: number
  confidence: number
  factors: {
    readability: number
    emotionalImpact: number
    hashtagUsage: number
    optimalLength: number
    callToAction: number
  }
  suggestions: string[]
  predictedEngagement: {
    likes: number
    comments: number
    shares: number
    impressions: number
  }
  bestPostingTime: string
}

const MOCK_PREDICTION: PredictionResult = {
  score: 78,
  confidence: 0.82,
  factors: {
    readability: 85,
    emotionalImpact: 75,
    hashtagUsage: 60,
    optimalLength: 90,
    callToAction: 80,
  },
  suggestions: [
    'Add 2-3 more relevant hashtags to increase discoverability',
    'Include a clear call-to-action to boost engagement',
    'Consider posting between 9-11 AM for maximum reach',
    'Your hook is strong - keep it up!',
  ],
  predictedEngagement: {
    likes: 245,
    comments: 32,
    shares: 18,
    impressions: 3200,
  },
  bestPostingTime: '09:30 AM EST',
}

export default function EngagementPrediction({
  contentId,
  contentText,
  platform = 'twitter',
}: EngagementPredictionProps) {
  const { showToast } = useToast()
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [content, setContent] = useState(contentText || '')

  const analyzeContent = useCallback(async () => {
    if (!content.trim()) {
      showToast('Please enter content to analyze', 'error')
      return
    }

    setIsAnalyzing(true)
    
    // Simulate API call
    setTimeout(() => {
      setPrediction(MOCK_PREDICTION)
      setIsAnalyzing(false)
      showToast('Engagement prediction complete!', 'success')
    }, 2000)
  }, [content, showToast])

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            🔮 Engagement Prediction
          </h3>
          <p className="text-sm text-gray-500">
            AI-powered prediction of content performance
          </p>
        </div>
      </div>

      {!prediction ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Content to Analyze
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your content here to predict engagement..."
              className="w-full h-32 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
            />
          </div>

          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Platform:
            </label>
            <select
              value={platform}
              onChange={(e) => {}}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
            >
              <option value="twitter">Twitter/X</option>
              <option value="linkedin">LinkedIn</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
            </select>
          </div>

          <Button
            onClick={analyzeContent}
            disabled={isAnalyzing}
            className="w-full"
          >
            {isAnalyzing ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </span>
            ) : (
              'Predict Engagement'
            )}
          </Button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="flex items-center gap-6">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="none"
                  className="text-gray-200 dark:text-gray-700"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="none"
                  strokeDasharray={`${(prediction.score / 100) * 351.86} 351.86`}
                  className={getScoreColor(prediction.score)}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className={`text-3xl font-bold ${getScoreColor(prediction.score)}`}>
                  {prediction.score}
                </span>
                <span className="text-xs text-gray-500">Score</span>
              </div>
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Confidence:
                </span>
                <span className="text-sm font-bold text-blue-600">
                  {(prediction.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-sm text-gray-500">
                {prediction.score >= 80
                  ? 'Great! This content is likely to perform well.'
                  : prediction.score >= 60
                  ? 'Good potential with some improvements needed.'
                  : 'Consider revising to improve engagement potential.'}
              </p>
            </div>
          </div>

          {/* Factor Breakdown */}
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">
              Factor Analysis
            </h4>
            <div className="space-y-3">
              {Object.entries(prediction.factors).map(([factor, score]) => (
                <div key={factor}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="capitalize text-gray-700 dark:text-gray-300">
                      {factor.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                    <span className="font-medium">{score}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getScoreBg(score)} transition-all duration-500`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Predicted Engagement */}
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">
              Predicted Engagement
            </h4>
            <div className="grid grid-cols-4 gap-3">
              {Object.entries(prediction.predictedEngagement).map(([metric, value]) => (
                <div
                  key={metric}
                  className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div className="text-2xl font-bold text-blue-600">
                    {value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value}
                  </div>
                  <div className="text-xs text-gray-500 capitalize">
                    {metric.replace(/([A-Z])/g, ' $1').trim()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Suggestions */}
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">
              💡 Improvement Suggestions
            </h4>
            <ul className="space-y-2">
              {prediction.suggestions.map((suggestion, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
                >
                  <span className="text-blue-500 mt-0.5">•</span>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>

          {/* Best Time */}
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-xl">🕐</span>
              <div>
                <span className="font-medium text-gray-900 dark:text-white">
                  Optimal Posting Time:{' '}
                </span>
                <span className="text-blue-600 font-bold">
                  {prediction.bestPostingTime}
                </span>
              </div>
            </div>
          </div>

          <Button
            onClick={() => {
              setPrediction(null)
              setContent('')
            }}
            variant="secondary"
            className="w-full"
          >
            Analyze New Content
          </Button>
        </div>
      )}
    </Card>
  )
}
