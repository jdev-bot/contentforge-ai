'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Languages, 
  Plus, 
  X, 
  Check,
  Trash2,
  Download,
  ChevronDown,
  ChevronRight,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import { getTranslations, Translation, deleteTranslation } from '@/lib/api'
import TranslationPanel from './TranslationPanel'

interface TranslationSidebarProps {
  contentId: string
  originalText: string
  className?: string
}

// Language flags mapping
const LANGUAGE_FLAGS: Record<string, string> = {
  en: '🇺🇸', es: '🇪🇸', fr: '🇫🇷', de: '🇩🇪', it: '🇮🇹', pt: '🇵🇹',
  nl: '🇳🇱', ru: '🇷🇺', ja: '🇯🇵', ko: '🇰🇷', zh: '🇨🇳', ar: '🇸🇦',
  hi: '🇮🇳', pl: '🇵🇱', tr: '🇹🇷', sv: '🇸🇪', da: '🇩🇰', no: '🇳🇴',
  fi: '🇫🇮', cs: '🇨🇿', uk: '🇺🇦', th: '🇹🇭', vi: '🇻🇳', id: '🇮🇩',
  el: '🇬🇷'
}

// Language names mapping
const LANGUAGE_NAMES: Record<string, string> = {
  en: 'English', es: 'Spanish', fr: 'French', de: 'German', it: 'Italian',
  pt: 'Portuguese', nl: 'Dutch', ru: 'Russian', ja: 'Japanese', ko: 'Korean',
  zh: 'Chinese', ar: 'Arabic', hi: 'Hindi', pl: 'Polish', tr: 'Turkish',
  sv: 'Swedish', da: 'Danish', no: 'Norwegian', fi: 'Finnish', cs: 'Czech',
  uk: 'Ukrainian', th: 'Thai', vi: 'Vietnamese', id: 'Indonesian', el: 'Greek'
}

export default function TranslationSidebar({
  contentId,
  originalText,
  className
}: TranslationSidebarProps) {
  const [translations, setTranslations] = useState<Translation[]>([])
  const [loading, setLoading] = useState(true)
  const [showTranslationPanel, setShowTranslationPanel] = useState(false)
  const [expandedLanguages, setExpandedLanguages] = useState<Set<string>>(new Set())
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const { showToast } = useToast()

  // Load translations
  const loadTranslations = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getTranslations(contentId)
      setTranslations(data)
    } catch (error) {
      console.error('Failed to load translations:', error)
      // Don't show error toast - translations might not exist yet
      setTranslations([])
    } finally {
      setLoading(false)
    }
  }, [contentId])

  useEffect(() => {
    loadTranslations()
  }, [loadTranslations])

  // Group translations by language
  const translationsByLanguage = translations.reduce((acc, translation) => {
    if (!acc[translation.language_code]) {
      acc[translation.language_code] = []
    }
    acc[translation.language_code].push(translation)
    return acc
  }, {} as Record<string, Translation[]>)

  // Toggle language expansion
  const toggleLanguage = useCallback((langCode: string) => {
    setExpandedLanguages(prev => {
      const newSet = new Set(prev)
      if (newSet.has(langCode)) {
        newSet.delete(langCode)
      } else {
        newSet.add(langCode)
      }
      return newSet
    })
  }, [])

  // Handle translation complete
  const handleTranslationComplete = useCallback(() => {
    loadTranslations()
    setShowTranslationPanel(false)
  }, [loadTranslations])

  // Handle delete translation
  const handleDeleteTranslation = useCallback(async (translationId: string) => {
    if (!confirm('Are you sure you want to delete this translation?')) {
      return
    }

    try {
      setDeletingId(translationId)
      await deleteTranslation(translationId)
      setTranslations(prev => prev.filter(t => t.id !== translationId))
      showToast('Translation deleted successfully', 'success')
    } catch (error) {
      console.error('Failed to delete translation:', error)
      showToast('Failed to delete translation', 'error')
    } finally {
      setDeletingId(null)
    }
  }, [showToast])

  // Download translation
  const handleDownload = useCallback((translation: Translation) => {
    const blob = new Blob([translation.translated_text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${translation.content_id}_${translation.language_code}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    showToast('Translation downloaded', 'success')
  }, [showToast])

  // Get unique languages count
  const uniqueLanguages = Object.keys(translationsByLanguage).length

  return (
    <div className={cn("space-y-4", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Languages className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          <h3 className="font-semibold text-slate-900 dark:text-slate-100">
            Translations
          </h3>
          {uniqueLanguages > 0 && (
            <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
              {uniqueLanguages}
            </span>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowTranslationPanel(!showTranslationPanel)}
          leftIcon={showTranslationPanel ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
        >
          {showTranslationPanel ? 'Cancel' : 'Add'}
        </Button>
      </div>

      {/* Translation Panel */}
      <AnimatePresence>
        {showTranslationPanel && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <TranslationPanel
              contentId={contentId}
              originalText={originalText}
              onTranslationComplete={handleTranslationComplete}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Translation List */}
      <div className="space-y-2">
        {loading ? (
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-12 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : translations.length === 0 ? (
          <div className="text-center py-6 text-slate-500">
            <Languages className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No translations yet</p>
            <p className="text-xs mt-1">Click "Add" to translate this content</p>
          </div>
        ) : (
          <div className="space-y-2">
            {Object.entries(translationsByLanguage).map(([langCode, langTranslations]) => (
              <Card
                key={langCode}
                variant="default"
                className="overflow-hidden"
              >
                <button
                  onClick={() => toggleLanguage(langCode)}
                  className="w-full flex items-center gap-3 p-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                >
                  <span className="text-2xl">{LANGUAGE_FLAGS[langCode] || '🌐'}</span>
                  <div className="flex-1 text-left">
                    <span className="font-medium text-slate-900 dark:text-slate-100">
                      {LANGUAGE_NAMES[langCode] || langCode}
                    </span>
                    <span className="text-xs text-slate-400 ml-2">
                      ({langTranslations.length} version{langTranslations.length > 1 ? 's' : ''})
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">
                      Avg: {(langTranslations.reduce((acc, t) => acc + t.confidence_score, 0) / langTranslations.length * 100).toFixed(0)}%
                    </span>
                    {expandedLanguages.has(langCode) ? (
                      <ChevronDown className="h-4 w-4 text-slate-400" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-slate-400" />
                    )}
                  </div>
                </button>

                <AnimatePresence>
                  {expandedLanguages.has(langCode) && (
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: 'auto' }}
                      exit={{ height: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-3 pb-3 space-y-2">
                        {langTranslations.map((translation, index) => (
                          <div
                            key={translation.id}
                            className={cn(
                              "p-3 rounded-lg text-sm",
                              "bg-slate-50 dark:bg-slate-800/50",
                              "border border-slate-100 dark:border-slate-700"
                            )}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-slate-400">
                                  Version {index + 1}
                                </span>
                                <span className="text-xs text-slate-400">•</span>
                                <span className={cn(
                                  "text-xs",
                                  translation.confidence_score >= 0.9 ? "text-emerald-600 dark:text-emerald-400" :
                                  translation.confidence_score >= 0.7 ? "text-amber-600 dark:text-amber-400" :
                                  "text-rose-600 dark:text-rose-400"
                                )}>
                                  {(translation.confidence_score * 100).toFixed(0)}% confidence
                                </span>
                              </div>
                              <div className="flex items-center gap-1">
                                <button
                                  onClick={() => handleDownload(translation)}
                                  className="p-1.5 text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
                                  title="Download"
                                >
                                  <Download className="h-3.5 w-3.5" />
                                </button>
                                <button
                                  onClick={() => handleDeleteTranslation(translation.id)}
                                  disabled={deletingId === translation.id}
                                  className="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded transition-colors"
                                  title="Delete"
                                >
                                  {deletingId === translation.id ? (
                                    <div className="h-3.5 w-3.5 border-2 border-rose-500 border-t-transparent rounded-full animate-spin" />
                                  ) : (
                                    <Trash2 className="h-3.5 w-3.5" />
                                  )}
                                </button>
                              </div>
                            </div>
                            
                            <p className="text-slate-700 dark:text-slate-300 line-clamp-3">
                              {translation.translated_text.substring(0, 200)}
                              {translation.translated_text.length > 200 && '...'}
                            </p>
                            
                            <div className="mt-2 text-xs text-slate-400">
                              Created {new Date(translation.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
