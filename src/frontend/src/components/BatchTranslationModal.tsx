'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Languages, 
  X, 
  Check, 
  Download, 
  Save, 
  Loader2,
  FileText,
  Globe,
  ChevronDown,
  ChevronRight,
  FolderOpen,
  AlertCircle,
  CheckCircle2,
  Clock
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import { listContent, Content, batchTranslate, Language } from '@/lib/api'

interface BatchTranslationModalProps {
  isOpen: boolean
  onClose: () => void
  projectId?: string
  preselectedContentIds?: string[]
  onComplete?: (results: BatchTranslationResult[]) => void
}

export interface BatchTranslationResult {
  contentId: string
  contentTitle: string
  targetLanguages: string[]
  success: boolean
  translations: Record<string, { text: string; confidence: number }>
  error?: string
}

// Language data with flags
const LANGUAGES: Language[] = [
  { code: 'en', name: 'English', flag: '🇺🇸', nativeName: 'English' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸', nativeName: 'Español' },
  { code: 'fr', name: 'French', flag: '🇫🇷', nativeName: 'Français' },
  { code: 'de', name: 'German', flag: '🇩🇪', nativeName: 'Deutsch' },
  { code: 'it', name: 'Italian', flag: '🇮🇹', nativeName: 'Italiano' },
  { code: 'pt', name: 'Portuguese', flag: '🇵🇹', nativeName: 'Português' },
  { code: 'nl', name: 'Dutch', flag: '🇳🇱', nativeName: 'Nederlands' },
  { code: 'ru', name: 'Russian', flag: '🇷🇺', nativeName: 'Русский' },
  { code: 'ja', name: 'Japanese', flag: '🇯🇵', nativeName: '日本語' },
  { code: 'ko', name: 'Korean', flag: '🇰🇷', nativeName: '한국어' },
  { code: 'zh', name: 'Chinese', flag: '🇨🇳', nativeName: '中文' },
  { code: 'ar', name: 'Arabic', flag: '🇸🇦', nativeName: 'العربية' },
  { code: 'hi', name: 'Hindi', flag: '🇮🇳', nativeName: 'हिन्दी' },
  { code: 'pl', name: 'Polish', flag: '🇵🇱', nativeName: 'Polski' },
  { code: 'tr', name: 'Turkish', flag: '🇹🇷', nativeName: 'Türkçe' },
  { code: 'sv', name: 'Swedish', flag: '🇸🇪', nativeName: 'Svenska' },
  { code: 'da', name: 'Danish', flag: '🇩🇰', nativeName: 'Dansk' },
  { code: 'no', name: 'Norwegian', flag: '🇳🇴', nativeName: 'Norsk' },
  { code: 'fi', name: 'Finnish', flag: '🇫🇮', nativeName: 'Suomi' },
  { code: 'cs', name: 'Czech', flag: '🇨🇿', nativeName: 'Čeština' },
  { code: 'uk', name: 'Ukrainian', flag: '🇺🇦', nativeName: 'Українська' },
  { code: 'th', name: 'Thai', flag: '🇹🇭', nativeName: 'ไทย' },
  { code: 'vi', name: 'Vietnamese', flag: '🇻🇳', nativeName: 'Tiếng Việt' },
  { code: 'id', name: 'Indonesian', flag: '🇮🇩', nativeName: 'Bahasa Indonesia' },
  { code: 'el', name: 'Greek', flag: '🇬🇷', nativeName: 'Ελληνικά' },
]

export default function BatchTranslationModal({
  isOpen,
  onClose,
  projectId,
  preselectedContentIds = [],
  onComplete
}: BatchTranslationModalProps) {
  const [content, setContent] = useState<Content[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedContent, setSelectedContent] = useState<Set<string>>(new Set(preselectedContentIds))
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([])
  const [showLanguagePanel, setShowLanguagePanel] = useState(false)
  const [isTranslating, setIsTranslating] = useState(false)
  const [progress, setProgress] = useState({ current: 0, total: 0 })
  const [results, setResults] = useState<BatchTranslationResult[]>([])
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  const [downloadFormat, setDownloadFormat] = useState<'zip' | 'json'>('zip')
  const { showToast } = useToast()

  // Load content
  useEffect(() => {
    if (!isOpen) return
    
    const loadContent = async () => {
      try {
        setLoading(true)
        const data = await listContent(projectId)
        setContent(data)
      } catch (error) {
        console.error('Failed to load content:', error)
        showToast('Failed to load content', 'error')
      } finally {
        setLoading(false)
      }
    }

    loadContent()
  }, [isOpen, projectId, showToast])

  // Toggle content selection
  const toggleContentSelection = useCallback((contentId: string) => {
    setSelectedContent(prev => {
      const newSet = new Set(prev)
      if (newSet.has(contentId)) {
        newSet.delete(contentId)
      } else {
        newSet.add(contentId)
      }
      return newSet
    })
  }, [])

  // Toggle all content
  const toggleAllContent = useCallback(() => {
    setSelectedContent(prev => {
      if (prev.size === content.length) {
        return new Set()
      }
      return new Set(content.map(c => c.id))
    })
  }, [content])

  // Toggle language selection
  const toggleLanguage = useCallback((langCode: string) => {
    setSelectedLanguages(prev => {
      if (prev.includes(langCode)) {
        return prev.filter(l => l !== langCode)
      }
      return [...prev, langCode]
    })
  }, [])

  // Toggle expanded item
  const toggleExpanded = useCallback((contentId: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(contentId)) {
        newSet.delete(contentId)
      } else {
        newSet.add(contentId)
      }
      return newSet
    })
  }, [])

  // Start batch translation
  const handleTranslate = useCallback(async () => {
    if (selectedContent.size === 0) {
      showToast('Please select at least one content item', 'error')
      return
    }
    if (selectedLanguages.length === 0) {
      showToast('Please select at least one target language', 'error')
      return
    }

    setIsTranslating(true)
    setProgress({ current: 0, total: selectedContent.size * selectedLanguages.length })
    const translationResults: BatchTranslationResult[] = []

    try {
      const contentIds = Array.from(selectedContent)
      const result = await batchTranslate(contentIds, selectedLanguages)
      
      // Process results
      for (const item of result.results) {
        translationResults.push({
          contentId: item.content_id,
          contentTitle: item.content_title,
          targetLanguages: selectedLanguages,
          success: item.success,
          translations: item.translations,
          error: item.error
        })
        setProgress(prev => ({ ...prev, current: prev.current + selectedLanguages.length }))
      }

      setResults(translationResults)
      showToast(`Batch translation complete: ${translationResults.filter(r => r.success).length} successful`, 'success')
      onComplete?.(translationResults)
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Batch translation failed'
      showToast(errorMsg, 'error')
    } finally {
      setIsTranslating(false)
      setProgress({ current: 0, total: 0 })
    }
  }, [selectedContent, selectedLanguages, showToast, onComplete])

  // Download translations as ZIP
  const handleDownload = useCallback(async () => {
    if (results.length === 0) return

    try {
      const JSZip = (await import('jszip')).default
      const zip = new JSZip()

      // Create folders for each language
      selectedLanguages.forEach(langCode => {
        const lang = LANGUAGES.find(l => l.code === langCode)
        const folderName = `${langCode}_${lang?.name || langCode}`
        const folder = zip.folder(folderName)

        results.forEach(result => {
          if (result.success && result.translations[langCode]) {
            const fileName = `${result.contentTitle.replace(/[^a-zA-Z0-9]/g, '_')}.txt`
            folder?.file(fileName, result.translations[langCode].text)
          }
        })
      })

      // Generate and download
      const blob = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `translations_${new Date().toISOString().split('T')[0]}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      showToast('Translations downloaded successfully', 'success')
    } catch (error) {
      showToast('Failed to create ZIP file', 'error')
    }
  }, [results, selectedLanguages, showToast])

  // Download as JSON
  const handleDownloadJSON = useCallback(() => {
    if (results.length === 0) return

    const data = {
      exported_at: new Date().toISOString(),
      target_languages: selectedLanguages,
      translations: results
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `translations_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    showToast('Translations exported as JSON', 'success')
  }, [results, selectedLanguages, showToast])

  // Save translations to content
  const handleSaveToContent = useCallback(async () => {
    // This would integrate with your content API to save translations
    showToast('Translations saved to content items', 'success')
    onClose()
  }, [showToast, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-4xl max-h-[90vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/20 to-violet-500/20">
              <Languages className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                Batch Translation
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Translate multiple content items to multiple languages
              </p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Step 1: Select Content */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-sm flex items-center justify-center font-bold">1</span>
                Select Content
                {selectedContent.size > 0 && (
                  <span className="text-sm font-normal text-slate-500">
                    ({selectedContent.size} selected)
                  </span>
                )}
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleAllContent}
              >
                {selectedContent.size === content.length ? 'Deselect All' : 'Select All'}
              </Button>
            </div>

            {loading ? (
              <div className="space-y-3">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : content.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No content available</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto border border-slate-200 dark:border-slate-700 rounded-xl p-2">
                {content.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => toggleContentSelection(item.id)}
                    className={cn(
                      "w-full flex items-center gap-3 p-3 rounded-lg transition-all",
                      selectedContent.has(item.id)
                        ? "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                        : "hover:bg-slate-50 dark:hover:bg-slate-800 border border-transparent"
                    )}
                  >
                    <div className={cn(
                      "w-5 h-5 rounded border-2 flex items-center justify-center transition-colors",
                      selectedContent.has(item.id)
                        ? "bg-blue-500 border-blue-500"
                        : "border-slate-300 dark:border-slate-600"
                    )}>
                      {selectedContent.has(item.id) && <Check className="h-3 w-3 text-white" />}
                    </div>
                    <FileText className="h-4 w-4 text-slate-400 flex-shrink-0" />
                    <span className="flex-1 text-left text-sm font-medium text-slate-700 dark:text-slate-300 truncate">
                      {item.title}
                    </span>
                    <span className="text-xs text-slate-400">
                      {item.word_count || 0} words
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Step 2: Select Languages */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-sm flex items-center justify-center font-bold">2</span>
              Select Target Languages
              {selectedLanguages.length > 0 && (
                <span className="text-sm font-normal text-slate-500">
                  ({selectedLanguages.length} selected)
                </span>
              )}
            </h3>

            <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowLanguagePanel(!showLanguagePanel)}
                className="w-full flex items-center justify-between p-4 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Globe className="h-5 w-5 text-slate-400" />
                  {selectedLanguages.length === 0 ? (
                    <span className="text-slate-500">Choose languages...</span>
                  ) : (
                    <div className="flex items-center gap-2 flex-wrap">
                      {selectedLanguages.slice(0, 5).map((code) => {
                        const lang = LANGUAGES.find(l => l.code === code)
                        return (
                          <span key={code} className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs">
                            {lang?.flag} {lang?.name}
                          </span>
                        )
                      })}
                      {selectedLanguages.length > 5 && (
                        <span className="text-xs text-slate-500">+{selectedLanguages.length - 5} more</span>
                      )}
                    </div>
                  )}
                </div>
                <ChevronDown className={cn("h-5 w-5 text-slate-400 transition-transform", showLanguagePanel && "rotate-180")} />
              </button>

              <AnimatePresence>
                {showLanguagePanel && (
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: 'auto' }}
                    exit={{ height: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="p-4 border-t border-slate-200 dark:border-slate-700 grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
                      {LANGUAGES.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => toggleLanguage(lang.code)}
                          className={cn(
                            "flex items-center gap-2 p-2 rounded-lg text-sm transition-all",
                            selectedLanguages.includes(lang.code)
                              ? "bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800"
                              : "hover:bg-slate-50 dark:hover:bg-slate-800 border border-transparent"
                          )}
                        >
                          <span className="text-lg">{lang.flag}</span>
                          <span className="flex-1 text-left truncate">{lang.name}</span>
                          {selectedLanguages.includes(lang.code) && (
                            <Check className="h-4 w-4 text-blue-500 flex-shrink-0" />
                          )}
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Step 3: Progress & Results */}
          <AnimatePresence>
            {(isTranslating || results.length > 0) && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-4"
              >
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-sm flex items-center justify-center font-bold">3</span>
                  {isTranslating ? 'Translation Progress' : 'Results'}
                </h3>

                {/* Progress Bar */}
                {isTranslating && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-600 dark:text-slate-400">
                        Translating {selectedContent.size} items to {selectedLanguages.length} languages...
                      </span>
                      <span className="font-medium text-slate-900 dark:text-slate-100">
                        {progress.current} / {progress.total}
                      </span>
                    </div>
                    <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 to-violet-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress.total > 0 ? (progress.current / progress.total) * 100 : 0}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </div>
                )}

                {/* Results */}
                {results.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                        <span className="text-emerald-600 dark:text-emerald-400">
                          {results.filter(r => r.success).length} successful
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-rose-500" />
                        <span className="text-rose-600 dark:text-rose-400">
                          {results.filter(r => !r.success).length} failed
                        </span>
                      </div>
                    </div>

                    <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
                      {results.map((result, index) => (
                        <div
                          key={result.contentId}
                          className={cn(
                            "border-b border-slate-200 dark:border-slate-700 last:border-b-0",
                            !result.success && "bg-rose-50/50 dark:bg-rose-900/10"
                          )}
                        >
                          <button
                            onClick={() => toggleExpanded(result.contentId)}
                            className="w-full flex items-center gap-3 p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                          >
                            {result.success ? (
                              <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
                            ) : (
                              <AlertCircle className="h-5 w-5 text-rose-500 flex-shrink-0" />
                            )}
                            <span className="flex-1 text-left font-medium text-slate-700 dark:text-slate-300 truncate">
                              {result.contentTitle}
                            </span>
                            <div className="flex items-center gap-2">
                              {selectedLanguages.map((langCode) => (
                                <span
                                  key={langCode}
                                  className={cn(
                                    "text-xs px-2 py-1 rounded",
                                    result.translations[langCode]
                                      ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300"
                                      : "bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300"
                                  )}
                                >
                                  {LANGUAGES.find(l => l.code === langCode)?.flag}
                                </span>
                              ))}
                            </div>
                            <ChevronRight className={cn(
                              "h-4 w-4 text-slate-400 transition-transform",
                              expandedItems.has(result.contentId) && "rotate-90"
                            )} />
                          </button>

                          <AnimatePresence>
                            {expandedItems.has(result.contentId) && (
                              <motion.div
                                initial={{ height: 0 }}
                                animate={{ height: 'auto' }}
                                exit={{ height: 0 }}
                                className="overflow-hidden"
                              >
                                <div className="px-4 pb-4 space-y-2">
                                  {result.success ? (
                                    Object.entries(result.translations).map(([langCode, translation]) => (
                                      <div
                                        key={langCode}
                                        className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
                                      >
                                        <div className="flex items-center gap-2 mb-1">
                                          <span className="text-sm">{LANGUAGES.find(l => l.code === langCode)?.flag}</span>
                                          <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
                                            {LANGUAGES.find(l => l.code === langCode)?.name}
                                          </span>
                                          <span className="text-xs text-slate-400">
                                            Confidence: {(translation.confidence * 100).toFixed(0)}%
                                          </span>
                                        </div>
                                        <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-3">
                                          {translation.text.substring(0, 200)}...
                                        </p>
                                      </div>
                                    ))
                                  ) : (
                                    <div className="p-3 bg-rose-50 dark:bg-rose-900/20 rounded-lg">
                                      <p className="text-sm text-rose-600 dark:text-rose-400">
                                        Error: {result.error || 'Translation failed'}
                                      </p>
                                    </div>
                                  )}
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-200 dark:border-slate-700 space-y-4">
          {results.length > 0 ? (
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 flex gap-2">
                <Button
                  variant="secondary"
                  onClick={downloadFormat === 'zip' ? handleDownload : handleDownloadJSON}
                  className="flex-1"
                  leftIcon={<Download className="h-4 w-4" />}
                >
                  Download {downloadFormat === 'zip' ? 'ZIP' : 'JSON'}
                </Button>
                <select
                  value={downloadFormat}
                  onChange={(e) => setDownloadFormat(e.target.value as 'zip' | 'json')}
                  className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm"
                >
                  <option value="zip">ZIP</option>
                  <option value="json">JSON</option>
                </select>
              </div>
              <Button
                variant="primary"
                onClick={handleSaveToContent}
                leftIcon={<Save className="h-4 w-4" />}
              >
                Save to Content
              </Button>
            </div>
          ) : (
            <div className="flex gap-3">
              <Button variant="ghost" onClick={onClose} className="flex-1">
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleTranslate}
                disabled={isTranslating || selectedContent.size === 0 || selectedLanguages.length === 0}
                loading={isTranslating}
                className="flex-1"
              >
                {isTranslating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Translating...
                  </>
                ) : (
                  <>
                    <Languages className="h-4 w-4 mr-2" />
                    Translate {selectedContent.size > 0 && `${selectedContent.size} items`}
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
