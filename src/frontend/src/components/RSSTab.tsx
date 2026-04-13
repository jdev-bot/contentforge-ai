'use client'

import { useState } from 'react'
import RSSFeedManager from './RSSFeedManager'
import RSSEntriesPanel from './RSSEntriesPanel'
import { Card, CardContent } from '@/components/ui/Card'
import { Rss } from 'lucide-react'

interface RSSTabProps {
  user?: {
    id: string
    email: string
  }
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default function RSSTab(props: RSSTabProps) {
  const [selectedFeedId, setSelectedFeedId] = useState<string | null>(null)

  const handleFeedSelect = (feedId: string | null) => {
    setSelectedFeedId(feedId)
  }

  const handleImportSuccess = () => {
    // Optionally refresh feeds to update counts
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
              <Rss className="w-5 h-5 text-white" />
            </div>
            RSS Feeds
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1 ml-13">
            Subscribe to RSS feeds and automatically import content from your favorite sources
          </p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Feed Manager */}
        <div className="lg:col-span-1">
          <RSSFeedManager
            onFeedSelect={handleFeedSelect}
            selectedFeedId={selectedFeedId}
          />
        </div>

        {/* Right Column: Entries Panel */}
        <div className="lg:col-span-2">
          <RSSEntriesPanel
            selectedFeedId={selectedFeedId}
            onImportSuccess={handleImportSuccess}
          />
        </div>
      </div>

      {/* RSS Settings Card */}
      <Card className="bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
              <Rss className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="font-medium text-slate-900 dark:text-slate-100">
                About RSS Feeds
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
                RSS (Really Simple Syndication) allows you to automatically import content from blogs, news sites, and other sources. 
                Configure your feeds to fetch at regular intervals, and import interesting articles directly into your ContentForge projects.
              </p>
              <ul className="text-sm text-slate-500 dark:text-slate-400 mt-3 space-y-1">
                <li>• Add any RSS feed URL (usually ends in /feed or /rss)</li>
                <li>• Set automatic fetch frequency or fetch manually</li>
                <li>• Preview entries before importing to your content library</li>
                <li>• Bulk import multiple entries at once</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
