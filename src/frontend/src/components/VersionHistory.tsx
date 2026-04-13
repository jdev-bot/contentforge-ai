'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import DOMPurify from 'dompurify'
import {
  Clock,
  RotateCcw,
  GitCompare,
  History,
  ChevronRight,
  Sparkles,
  FileText,
  AlertTriangle,
  Plus,
  Minus,
  ArrowLeft,
  Check,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { EmptyState } from '@/components/ui/EmptyState'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import {
  getContentVersions,
  compareVersions,
  restoreContentVersion,
  ContentVersion,
  VersionComparison,
  VersionHistoryResponse,
} from '@/lib/api'

interface VersionHistoryProps {
  contentId: string
}

export default function VersionHistory({ contentId }: VersionHistoryProps) {
  const [history, setHistory] = useState<VersionHistoryResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedVersion, setSelectedVersion] = useState<ContentVersion | null>(null)
  const [compareMode, setCompareMode] = useState(false)
  const [compareOld, setCompareOld] = useState<ContentVersion | null>(null)
  const [compareNew, setCompareNew] = useState<ContentVersion | null>(null)
  const [comparison, setComparison] = useState<VersionComparison | null>(null)
  const [isComparing, setIsComparing] = useState(false)
  const [restoreTarget, setRestoreTarget] = useState<ContentVersion | null>(null)
  const [isRestoring, setIsRestoring] = useState(false)
  const { showToast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await getContentVersions(contentId)
      setHistory(data)
      if (data.versions.length > 0 && !selectedVersion) {
        setSelectedVersion(data.versions[0])
      }
    } catch {
      showToast('Failed to load version history', 'error')
    } finally {
      setIsLoading(false)
    }
  }, [contentId, showToast, selectedVersion])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleCompare = useCallback(async () => {
    if (!compareOld || !compareNew) return
    try {
      setIsComparing(true)
      const result = await compareVersions(
        contentId,
        compareOld.id,
        compareNew.id
      )
      setComparison(result)
    } catch {
      showToast('Failed to compare versions', 'error')
    } finally {
      setIsComparing(false)
    }
  }, [contentId, compareOld, compareNew, showToast])

  const handleRestore = useCallback(async () => {
    if (!restoreTarget) return
    try {
      setIsRestoring(true)
      await restoreContentVersion(contentId, restoreTarget.id)
      showToast(`Restored version ${restoreTarget.version_number}`, 'success')
      fetchData()
    } catch {
      showToast('Failed to restore version', 'error')
    } finally {
      setIsRestoring(false)
      setRestoreTarget(null)
    }
  }, [contentId, restoreTarget, fetchData, showToast])

  const toggleCompareVersion = useCallback(
    (version: ContentVersion) => {
      if (compareOld?.id === version.id) {
        setCompareOld(null)
      } else if (compareNew?.id === version.id) {
        setCompareNew(null)
      } else if (!compareOld) {
        setCompareOld(version)
      } else if (!compareNew) {
        setCompareNew(version)
      }
    },
    [compareOld, compareNew]
  )

  const exitCompareMode = useCallback(() => {
    setCompareMode(false)
    setCompareOld(null)
    setCompareNew(null)
    setComparison(null)
  }, [])

  const sortedVersions = useMemo(() => {
    if (!history?.versions) return []
    return [...history.versions].sort(
      (a, b) => b.version_number - a.version_number
    )
  }, [history])

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-24 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800"
            />
          ))}
        </div>
        <div className="lg:col-span-2 h-96 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800" />
      </div>
    )
  }

  if (!history || history.versions.length === 0) {
    return (
      <EmptyState
        title="No versions yet"
        description="Version history will appear here as you edit content. Auto-versioning is enabled."
        icon="file"
      />
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Version History
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            {history.total_versions} version{history.total_versions !== 1 ? 's' : ''} recorded
          </p>
        </div>
        <div className="flex items-center gap-3">
          {compareMode ? (
            <>
              <Button
                variant="primary"
                size="sm"
                leftIcon={<GitCompare className="w-4 h-4" />}
                onClick={handleCompare}
                disabled={!compareOld || !compareNew || isComparing}
                loading={isComparing}
              >
                Compare
              </Button>
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<ArrowLeft className="w-4 h-4" />}
                onClick={exitCompareMode}
              >
                Exit Compare
              </Button>
            </>
          ) : (
            <>
              <Badge variant="success" size="sm" dot>
                Auto-versioning on
              </Badge>
              <Button
                variant="outline"
                size="sm"
                leftIcon={<GitCompare className="w-4 h-4" />}
                onClick={() => setCompareMode(true)}
              >
                Compare Versions
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Version List */}
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {sortedVersions.map((version, idx) => {
              const isSelected = selectedVersion?.id === version.id
              const isCompareOld = compareOld?.id === version.id
              const isCompareNew = compareNew?.id === version.id

              return (
                <motion.div
                  key={version.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  onClick={() => {
                    if (compareMode) {
                      toggleCompareVersion(version)
                    } else {
                      setSelectedVersion(version)
                    }
                  }}
                  className={cn(
                    'relative p-4 rounded-xl cursor-pointer transition-all duration-200',
                    'border',
                    isSelected && !compareMode && [
                      'bg-blue-50 dark:bg-blue-900/20',
                      'border-blue-200 dark:border-blue-500/30',
                      'shadow-md',
                    ],
                    isCompareOld && [
                      'bg-emerald-50 dark:bg-emerald-900/20',
                      'border-emerald-200 dark:border-emerald-500/30',
                    ],
                    isCompareNew && [
                      'bg-violet-50 dark:bg-violet-900/20',
                      'border-violet-200 dark:border-violet-500/30',
                    ],
                    !isSelected && !isCompareOld && !isCompareNew && [
                      'bg-white/50 dark:bg-slate-800/50',
                      'border-slate-200 dark:border-slate-700',
                      'hover:border-slate-300 dark:hover:border-slate-600',
                    ]
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                          v{version.version_number}
                        </span>
                        {version.is_auto_version && (
                          <Badge variant="info" size="sm">
                            <Sparkles className="w-3 h-3 mr-1" />
                            Auto
                          </Badge>
                        )}
                        {isCompareOld && (
                          <Badge variant="success" size="sm">Old</Badge>
                        )}
                        {isCompareNew && (
                          <Badge variant="purple" size="sm">New</Badge>
                        )}
                      </div>
                      <p className="text-sm text-slate-700 dark:text-slate-300 truncate">
                        {version.change_summary || 'No summary'}
                      </p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-slate-500 dark:text-slate-400">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(version.created_at).toLocaleString()}
                        </span>
                        <span>{version.word_count} words</span>
                      </div>
                    </div>
                    <ChevronRight
                      className={cn(
                        'w-4 h-4 text-slate-400 transition-transform',
                        isSelected && 'rotate-90'
                      )}
                    />
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>

        {/* Content Preview / Comparison */}
        <div className="lg:col-span-2">
          {comparison ? (
            /* Side-by-side comparison view */
            <Card variant="glass" className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <GitCompare className="w-5 h-5 text-violet-500" />
                      Version Comparison
                    </CardTitle>
                    <CardDescription>
                      v{comparison.old_version.version_number} → v{comparison.new_version.version_number}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                      <Plus className="w-4 h-4" />
                      {comparison.diff.additions} additions
                    </span>
                    <span className="flex items-center gap-1 text-rose-600 dark:text-rose-400">
                      <Minus className="w-4 h-4" />
                      {comparison.diff.deletions} deletions
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Old Version */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Badge variant="outline" size="sm">
                        v{comparison.old_version.version_number}
                      </Badge>
                      <span className="text-sm text-slate-500 dark:text-slate-400">
                        {new Date(comparison.old_version.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 max-h-[500px] overflow-y-auto">
                      <div
                        className="prose prose-sm dark:prose-invert max-w-none text-sm"
                        dangerouslySetInnerHTML={{
                          __html: DOMPurify.sanitize(comparison.old_version.content_text),
                        }}
                      />
                    </div>
                  </div>
                  {/* New Version */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Badge variant="primary" size="sm">
                        v{comparison.new_version.version_number}
                      </Badge>
                      <span className="text-sm text-slate-500 dark:text-slate-400">
                        {new Date(comparison.new_version.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 max-h-[500px] overflow-y-auto">
                      <div
                        className="prose prose-sm dark:prose-invert max-w-none text-sm"
                        dangerouslySetInnerHTML={{
                          __html: DOMPurify.sanitize(comparison.new_version.content_text),
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Diff View */}
                {comparison.diff.diff_html && (
                  <div className="mt-6">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">
                      Changes
                    </h4>
                    <div
                      className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 max-h-[300px] overflow-y-auto text-sm [&_.diff-add]:bg-emerald-100 dark:[&_.diff-add]:bg-emerald-900/30 [&_.diff-add]:text-emerald-800 dark:[&_.diff-add]:text-emerald-300 [&_.diff-remove]:bg-rose-100 dark:[&_.diff-remove]:bg-rose-900/30 [&_.diff-remove]:text-rose-800 dark:[&_.diff-remove]:text-rose-300"
                      dangerouslySetInnerHTML={{
                        __html: DOMPurify.sanitize(comparison.diff.diff_html),
                      }}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          ) : selectedVersion ? (
            /* Single version preview */
            <Card variant="glass" className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-blue-500" />
                      v{selectedVersion.version_number} — {selectedVersion.title}
                    </CardTitle>
                    <CardDescription>
                      {selectedVersion.change_summary || 'No change summary'}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-3">
                    {selectedVersion.is_auto_version && (
                      <Badge variant="info" size="sm" dot>
                        Auto-saved
                      </Badge>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      leftIcon={<RotateCcw className="w-4 h-4" />}
                      onClick={() => setRestoreTarget(selectedVersion)}
                    >
                      Restore
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Version meta */}
                <div className="flex items-center gap-4 mb-4 text-sm text-slate-500 dark:text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {new Date(selectedVersion.created_at).toLocaleString()}
                  </span>
                  <span>By {selectedVersion.created_by}</span>
                  <span>{selectedVersion.word_count} words</span>
                </div>

                {/* Content preview */}
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 max-h-[500px] overflow-y-auto">
                  <div
                    className="prose prose-sm dark:prose-invert max-w-none"
                    dangerouslySetInnerHTML={{
                      __html: DOMPurify.sanitize(selectedVersion.content_text),
                    }}
                  />
                </div>

                {/* Diff summary from previous */}
                {selectedVersion.diff_from_previous && (
                  <div className="mt-4 flex items-center gap-4">
                    <div className="flex items-center gap-1 text-sm text-emerald-600 dark:text-emerald-400">
                      <Plus className="w-4 h-4" />
                      {selectedVersion.diff_from_previous.additions} added
                    </div>
                    <div className="flex items-center gap-1 text-sm text-rose-600 dark:text-rose-400">
                      <Minus className="w-4 h-4" />
                      {selectedVersion.diff_from_previous.deletions} removed
                    </div>
                    <div className="flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400">
                      <Check className="w-4 h-4" />
                      {selectedVersion.diff_from_previous.unchanged} unchanged
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card variant="glass" className="h-full flex items-center justify-center">
              <div className="text-center p-8">
                <History className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-500 dark:text-slate-400">
                  Select a version to preview
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Restore Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!restoreTarget}
        onClose={() => setRestoreTarget(null)}
        onConfirm={handleRestore}
        title="Restore Version"
        message={
          restoreTarget
            ? `Are you sure you want to restore version ${restoreTarget.version_number}? This will create a new version with the content from v${restoreTarget.version_number}.`
            : ''
        }
        confirmText="Restore Version"
        cancelText="Cancel"
        variant="warning"
        loading={isRestoring}
      />
    </div>
  )
}