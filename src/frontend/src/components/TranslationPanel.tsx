'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Languages, 
  Copy, 
  Check, 
  X, 
  RefreshCw, 
  Globe,
  Sparkles,
  BarChart3,
  ArrowRightLeft,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Tooltip } from '@/components/ui/Tooltip'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import { translateContent, getSupportedLanguages, Language } from '@/lib/api'

// Language data with flags (using emoji flags)
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

interface TranslationPanelProps {
  contentId: string
  originalText: string
  originalLanguage?: string
  onTranslationComplete?: (translation: TranslationResult) => void
  className?: string
}

export interface TranslationResult {
  contentId: string
  targetLanguage: string
  translatedText: string
  confidenceScore: number
  tokensUsed: number
}

export default function TranslationPanel({
  contentId,
  originalText,
  originalLanguage = 'en',
  onTranslationComplete,
  className
}: TranslationPanelProps) {
  const [selectedLanguage, setSelectedLanguage] = useState<string>('')
  const [isTranslating, setIsTranslating] = useState(false)
  const [translatedText, setTranslatedText] = useState<string>('')
  const [confidenceScore, setConfidenceScore] = useState<number>(0)
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [languages, setLanguages] = useState<Language[]>(LANGUAGES)
  const { showToast } = useToast()

  // Load supported languages from API
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const supported = await getSupportedLanguages()
        if (supported && supported.length > 0) {
          setLanguages(supported)
        }
      } catch {
        // Fallback to default languages
        setLanguages(LANGUAGES)
      }
    }
    loadLanguages()
  }, [])

  // Filter languages based on search
  const filteredLanguages = languages.filter(
    lang => 
      lang.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lang.nativeName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lang.code.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Get selected language details
  const selectedLang = languages.find(l => l.code === selectedLanguage)

  const handleTranslate = useCallback(async () => {
    if (!selectedLanguage) {
      showToast('Please select a target language', 'error')
      return
    }

    setIsTranslating(true)
    setError(null)

    try {
      const result = await translateContent(contentId, selectedLanguage)
      setTranslatedText(result.translatedText)
      setConfidenceScore(result.confidenceScore)
      
      onTranslationComplete?.(result)
      showToast(`Translated to ${selectedLang?.name || selectedLanguage}`, 'success')
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Translation failed'
      setError(errorMsg)
      showToast(errorMsg, 'error')
    } finally {
      setIsTranslating(false)
    }
  }, [contentId, selectedLanguage, selectedLang, onTranslationComplete, showToast])

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(translatedText)
      setCopied(true)
      showToast('Copied to clipboard', 'success')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      showToast('Failed to copy', 'error')
    }
  }, [translatedText, showToast])

  const handleSwapLanguages = useCallback(() => {
    if (translatedText) {
      // In a real implementation, this would swap source/target
      showToast('Languages swapped', 'info')
    }
  }, [translatedText, showToast])

  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return 'text-emerald-600 dark:text-emerald-400'
    if (score >= 0.7) return 'text-amber-600 dark:text-amber-400'
    return 'text-rose-600 dark:text-rose-400'
  }

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.9) return 'Excellent'
    if (score >= 0.7) return 'Good'
    if (score >= 0.5) return 'Fair'
    return 'Low'
  }

  return (
    <Card variant="glass" className={cn("overflow-visible", className)}>
      <CardHeader className="pb-4">
        <CardTitle className="text-lg flex items-center gap-2">
          <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/20 to-violet-500/20">
            <Languages className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          Translate Content
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Language Selector */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Target Language
          </label>
          <div className="relative">
            <button
              onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
              className={cn(
                "w-full flex items-center justify-between p-3 rounded-xl",
                "border-2 transition-all",
                showLanguageDropdown 
                  ? "border-blue-500 ring-4 ring-blue-500/10" 
                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
              )}
            >
              <div className="flex items-center gap-3">
                {selectedLang ? (
                  <>
                    <span className="text-2xl">{selectedLang.flag}</span>
                    <div className="text-left">
                      <span className="font-medium">{selectedLang.name}</span>
                      {selectedLang.nativeName && selectedLang.nativeName !== selectedLang.name && (
                        <span className="text-sm text-slate-500 ml-2">({selectedLang.nativeName})</span>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <Globe className="h-5 w-5 text-slate-400" />
                    <span className="text-slate-500">Select a language...</span>
                  </>
                )}
              </div>
              <ArrowRightLeft 
                className={cn(
                  "h-4 w-4 text-slate-400 transition-transform",
                  showLanguageDropdown && "rotate-180"
                )} 
              />
            </button>

            {/* Language Dropdown */}
            <AnimatePresence>
              {showLanguageDropdown && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className={cn(
                    "absolute z-50 w-full mt-2",
                    "bg-white dark:bg-slate-800",
                    "border border-slate-200 dark:border-slate-700",
                    "rounded-xl shadow-xl",
                    "max-h-80 overflow-hidden"
                  )}
                >
                  {/* Search */}
                  <div className="p-3 border-b border-slate-100 dark:border-slate-700">
                    <input
                      type="text"
                      placeholder="Search languages..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className={cn(
                        "w-full px-3 py-2 rounded-lg",
                        "bg-slate-50 dark:bg-slate-900",
                        "border border-slate-200 dark:border-slate-700",
                        "text-sm",
                        "focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10"
                      )}
                      autoFocus
                    />
                  </div>
                  
                  {/* Language List */}
                  <div className="overflow-y-auto max-h-60">
                    {filteredLanguages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setSelectedLanguage(lang.code)
                          setShowLanguageDropdown(false)
                          setSearchQuery('')
                        }}
                        className={cn(
                          "w-full flex items-center gap-3 px-4 py-3",
                          "hover:bg-slate-50 dark:hover:bg-slate-700/50",
                          "transition-colors",
                          selectedLanguage === lang.code && "bg-blue-50 dark:bg-blue-900/20"
                        )}
                      >
                        <span className="text-2xl">{lang.flag}</span>
                        <div className="flex-1 text-left">
                          <span className={cn(
                            "font-medium",
                            selectedLanguage === lang.code && "text-blue-600 dark:text-blue-400"
                          )}>
                            {lang.name}
                          </span>
                          {lang.nativeName && lang.nativeName !== lang.name && (
                            <span className="text-sm text-slate-500 ml-2">{lang.nativeName}</span>
                          )}
                        </div>
                        {selectedLanguage === lang.code && (
                          <Check className="h-4 w-4 text-blue-500" />
                        )}
                      </button>
                    ))}
                    {filteredLanguages.length === 0 && (
                      <div className="p-4 text-center text-slate-500">
                        No languages found
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Original Text Preview */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Original ({languages.find(l => l.code === originalLanguage)?.name || 'English'})
            </label>
            <span className="text-xs text-slate-400">
              {originalText.length} characters
            </span>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-4">
              {originalText}
            </p>
          </div>
        </div>

        {/* Translate Button */}
        <Button
          onClick={handleTranslate}
          disabled={isTranslating || !selectedLanguage}
          loading={isTranslating}
          className="w-full"
          leftIcon={<Sparkles className="h-4 w-4" />}
        >
          {isTranslating ? 'Translating...' : `Translate to ${selectedLang?.name || 'Selected Language'}`}
        </Button>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3 rounded-lg bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 flex items-center gap-2"
          >
            <AlertCircle className="h-4 w-4 text-rose-500 flex-shrink-0" />
            <p className="text-sm text-rose-600 dark:text-rose-400">{error}</p>
          </motion.div>
        )}

        {/* Translation Result */}
        <AnimatePresence>
          {translatedText && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              <div className="h-px bg-slate-200 dark:bg-slate-700" />
              
              {/* Side-by-side comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Original */}
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{languages.find(l => l.code === originalLanguage)?.flag}</span>
                    <span className="text-xs font-medium text-slate-500 uppercase">Original</span>
                  </div>
                  <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                    {originalText}
                  </p>
                </div>

                {/* Translated */}
                <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{selectedLang?.flag}</span>
                    <span className="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase">Translation</span>
                  </div>
                  <p className="text-sm text-slate-900 dark:text-slate-100 whitespace-pre-wrap">
                    {translatedText}
                  </p>
                </div>
              </div>

              {/* Confidence Score */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-slate-400" />
                  <span className="text-sm text-slate-600 dark:text-slate-400">Translation Quality</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className={cn(
                          "h-full rounded-full transition-all duration-500",
                          confidenceScore >= 0.9 ? "bg-emerald-500" :
                          confidenceScore >= 0.7 ? "bg-amber-500" : "bg-rose-500"
                        )}
                        style={{ width: `${confidenceScore * 100}%` }}
                      />
                    </div>
                    <span className={cn("text-sm font-medium", getConfidenceColor(confidenceScore))}>
                      {getConfidenceLabel(confidenceScore)}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">
                    {(confidenceScore * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3">
                <Button
                  variant="secondary"
                  onClick={handleCopy}
                  className="flex-1"
                  leftIcon={copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                >
                  {copied ? 'Copied!' : 'Copy Translation'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setTranslatedText('')
                    setConfidenceScore(0)
                  }}
                  leftIcon={<RefreshCw className="h-4 w-4" />}
                >
                  New Translation
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}
