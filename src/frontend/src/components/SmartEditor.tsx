'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Wand2, 
  Expand, 
  Minimize2, 
  Share2, 
  Check, 
  X, 
  ChevronDown,
  Loader2,
  Type,
  Sparkles,
  AlignLeft,
  MessageSquare,
  Zap,
  ArrowRightLeft,
  RefreshCw,
  Keyboard,
  Info
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Tooltip, TooltipButton } from '@/components/ui/Tooltip'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import {
  rewriteContent,
  expandContent,
  condenseContent,
  optimizeContent,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'

// Animation variants
const panelVariants = {
  hidden: { 
    opacity: 0, 
    y: 20, 
    scale: 0.95,
    filter: 'blur(10px)'
  },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    filter: 'blur(0px)',
    transition: {
      duration: 0.3,
      ease: [0.16, 1, 0.3, 1] as const
    }
  },
  exit: { 
    opacity: 0, 
    y: 10, 
    scale: 0.98,
    filter: 'blur(5px)',
    transition: { duration: 0.2 }
  }
}

const slideVariants = {
  hidden: { opacity: 0, x: 20 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { duration: 0.2, ease: 'easeOut' as const }
  },
  exit: { 
    opacity: 0, 
    x: -20,
    transition: { duration: 0.15 }
  }
}

// Types
type EditMode = 'rewrite' | 'expand' | 'condense' | 'optimize' | null

interface ToneOption {
  value: string
  label: string
  icon: React.ReactNode
  description: string
}

interface StyleOption {
  value: string
  label: string
}

interface PlatformOption {
  value: string
  label: string
  icon: React.ReactNode
}

const toneOptions: ToneOption[] = [
  { value: 'professional', label: 'Professional', icon: <Type className="h-4 w-4" />, description: 'Formal and business-like' },
  { value: 'casual', label: 'Casual', icon: <MessageSquare className="h-4 w-4" />, description: 'Relaxed and conversational' },
  { value: 'humorous', label: 'Humorous', icon: <Sparkles className="h-4 w-4" />, description: 'Funny and entertaining' },
  { value: 'formal', label: 'Formal', icon: <AlignLeft className="h-4 w-4" />, description: 'Academic and serious' },
  { value: 'friendly', label: 'Friendly', icon: <Zap className="h-4 w-4" />, description: 'Warm and approachable' },
  { value: 'authoritative', label: 'Authoritative', icon: <Zap className="h-4 w-4" />, description: 'Expert and confident' },
]

const styleOptions: StyleOption[] = [
  { value: 'engaging', label: 'More Engaging' },
  { value: 'concise', label: 'More Concise' },
  { value: 'descriptive', label: 'More Descriptive' },
  { value: 'persuasive', label: 'More Persuasive' },
  { value: 'storytelling', label: 'Storytelling' },
  { value: 'technical', label: 'Technical' },
]

const platformOptions: PlatformOption[] = [
  { value: 'twitter', label: 'Twitter/X', icon: <Share2 className="h-4 w-4" /> },
  { value: 'linkedin', label: 'LinkedIn', icon: <Share2 className="h-4 w-4" /> },
  { value: 'instagram', label: 'Instagram', icon: <Share2 className="h-4 w-4" /> },
  { value: 'facebook', label: 'Facebook', icon: <Share2 className="h-4 w-4" /> },
  { value: 'tiktok', label: 'TikTok', icon: <Share2 className="h-4 w-4" /> },
  { value: 'youtube', label: 'YouTube', icon: <Share2 className="h-4 w-4" /> },
  { value: 'blog', label: 'Blog Post', icon: <AlignLeft className="h-4 w-4" /> },
  { value: 'newsletter', label: 'Newsletter', icon: <MessageSquare className="h-4 w-4" /> },
]

interface SmartEditorProps {
  content: string
  contentId: string
  onContentChange?: (newContent: string) => void
  onSave?: (newContent: string) => Promise<void>
  className?: string
}

export default function SmartEditor({ 
  content, 
  contentId,
  onContentChange, 
  onSave,
  className 
}: SmartEditorProps) {
  // State
  const [originalContent, setOriginalContent] = useState(content)
  const [editedContent, setEditedContent] = useState(content)
  const [previewContent, setPreviewContent] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [activeMode, setActiveMode] = useState<EditMode>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const [showDiff, setShowDiff] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showShortcuts, setShowShortcuts] = useState(false)
  
  // Mode-specific state
  const [selectedTone, setSelectedTone] = useState('professional')
  const [selectedStyle, setSelectedStyle] = useState('engaging')
  const [targetLength, setTargetLength] = useState(500)
  const [condensePercentage, setCondensePercentage] = useState(50)
  const [selectedPlatform, setSelectedPlatform] = useState('twitter')
  
  const { showToast } = useToast()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Update content when prop changes
  useEffect(() => {
    setOriginalContent(content)
    setEditedContent(content)
    setPreviewContent(null)
    setHasChanges(false)
  }, [content])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + R - Rewrite
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault()
        setActiveMode('rewrite')
      }
      // Ctrl/Cmd + E - Expand
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault()
        setActiveMode('expand')
      }
      // Ctrl/Cmd + Shift + C - Condense
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
        e.preventDefault()
        setActiveMode('condense')
      }
      // Ctrl/Cmd + O - Optimize
      if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
        e.preventDefault()
        setActiveMode('optimize')
      }
      // Escape - Close panel
      if (e.key === 'Escape') {
        setActiveMode(null)
        setShowPreview(false)
      }
      // Ctrl/Cmd + Enter - Accept changes
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && previewContent) {
        e.preventDefault()
        handleAccept()
      }
      // Ctrl/Cmd + Backspace - Reject changes
      if ((e.ctrlKey || e.metaKey) && e.key === 'Backspace' && previewContent) {
        e.preventDefault()
        handleReject()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [previewContent])

  // Process content based on active mode
  const handleProcess = async () => {
    if (!editedContent.trim()) return
    
    setIsProcessing(true)
    setError(null)
    
    try {
      let result: string
      
      switch (activeMode) {
        case 'rewrite':
          result = await rewriteContent(editedContent, selectedTone, selectedStyle)
          break
        case 'expand':
          result = await expandContent(editedContent, targetLength)
          break
        case 'condense':
          result = await condenseContent(editedContent, condensePercentage)
          break
        case 'optimize':
          result = await optimizeContent(editedContent, selectedPlatform)
          break
        default:
          return
      }
      
      setPreviewContent(result)
      setShowPreview(true)
      showToast(`${activeMode?.charAt(0).toUpperCase()}${activeMode?.slice(1)} complete!`, 'success')
    } catch (err) {
      const errorMsg = formatApiError(err, 'Processing failed')
      setError(errorMsg)
      showToast(errorMsg, 'error')
    } finally {
      setIsProcessing(false)
    }
  }

  // Accept changes
  const handleAccept = useCallback(async () => {
    if (previewContent) {
      setEditedContent(previewContent)
      setHasChanges(true)
      onContentChange?.(previewContent)
      setPreviewContent(null)
      setShowPreview(false)
      setActiveMode(null)
      showToast('Changes accepted', 'success')
    }
  }, [previewContent, onContentChange, showToast])

  // Reject changes
  const handleReject = useCallback(() => {
    setPreviewContent(null)
    setShowPreview(false)
    setActiveMode(null)
    showToast('Changes rejected', 'info')
  }, [showToast])

  // Save content
  const handleSave = async () => {
    if (!hasChanges) return
    
    try {
      await onSave?.(editedContent)
      setOriginalContent(editedContent)
      setHasChanges(false)
      showToast('Content saved successfully', 'success')
    } catch (err) {
      const errorMsg = formatApiError(err, 'Failed to save')
      showToast(errorMsg, 'error')
    }
  }

  // Handle manual edit
  const handleManualEdit = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value
    setEditedContent(newContent)
    setHasChanges(newContent !== originalContent)
    onContentChange?.(newContent)
  }

  // Render diff view
  const renderDiff = () => {
    if (!previewContent) return null
    
    // Simple word-based diff
    const originalWords = editedContent.split(/\s+/)
    const previewWords = previewContent.split(/\s+/)
    
    return (
      <div className="space-y-4">
        {/* Before/After labels */}
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-500 dark:text-slate-400">Current</span>
          <ArrowRightLeft className="h-4 w-4 text-slate-400" />
          <span className="text-blue-600 dark:text-blue-400 font-medium">AI Suggestion</span>
        </div>
        
        {/* Comparison view */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Current */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">Current</p>
            <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
              {editedContent}
            </p>
          </div>
          
          {/* Preview */}
          <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
            <p className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-2">AI Suggestion</p>
            <p className="text-sm text-slate-900 dark:text-slate-100 whitespace-pre-wrap">
              {previewContent}
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Toolbar buttons
  const toolbarButtons = [
    { 
      mode: 'rewrite' as const, 
      icon: <Wand2 className="h-4 w-4" />, 
      label: 'Rewrite',
      shortcut: 'Ctrl+R',
      description: 'Rewrite with different tone and style'
    },
    { 
      mode: 'expand' as const, 
      icon: <Expand className="h-4 w-4" />, 
      label: 'Expand',
      shortcut: 'Ctrl+E',
      description: 'Make content longer and more detailed'
    },
    { 
      mode: 'condense' as const, 
      icon: <Minimize2 className="h-4 w-4" />, 
      label: 'Condense',
      shortcut: 'Ctrl+Shift+C',
      description: 'Make content shorter and punchier'
    },
    { 
      mode: 'optimize' as const, 
      icon: <Share2 className="h-4 w-4" />, 
      label: 'Optimize',
      shortcut: 'Ctrl+O',
      description: 'Optimize for specific platform'
    },
  ]

  return (
    <div className={cn("space-y-4", className)}>
      {/* Floating Toolbar */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sticky top-4 z-30"
      >
        <Card variant="glass" className="p-2">
          <div className="flex items-center gap-2 flex-wrap">
            {/* Edit mode buttons */}
            {toolbarButtons.map((btn) => (
              <Tooltip key={btn.mode} content={
                <div className="text-center">
                  <p className="font-medium">{btn.label}</p>
                  <p className="text-xs text-slate-400">{btn.description}</p>
                  <p className="text-xs text-slate-500 mt-1">{btn.shortcut}</p>
                </div>
              }>
                <Button
                  variant={activeMode === btn.mode ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveMode(activeMode === btn.mode ? null : btn.mode)}
                  className="flex items-center gap-2"
                >
                  {btn.icon}
                  <span className="hidden sm:inline">{btn.label}</span>
                </Button>
              </Tooltip>
            ))}
            
            <div className="h-6 w-px bg-slate-200 dark:bg-slate-700 mx-2" />
            
            {/* Diff toggle */}
            <Tooltip content="Show/hide comparison view">
              <Button
                variant={showDiff ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setShowDiff(!showDiff)}
                className="flex items-center gap-2"
              >
                <ArrowRightLeft className="h-4 w-4" />
                <span className="hidden sm:inline">Compare</span>
              </Button>
            </Tooltip>
            
            {/* Keyboard shortcuts */}
            <Tooltip content="View keyboard shortcuts">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowShortcuts(!showShortcuts)}
                className="flex items-center gap-2"
              >
                <Keyboard className="h-4 w-4" />
              </Button>
            </Tooltip>
            
            {/* Save button */}
            {hasChanges && (
              <Button
                variant="success"
                size="sm"
                onClick={handleSave}
                className="flex items-center gap-2 ml-auto"
              >
                <Check className="h-4 w-4" />
                Save Changes
              </Button>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Keyboard Shortcuts Panel */}
      <AnimatePresence>
        {showShortcuts && (
          <motion.div
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <Card variant="glass" className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <Keyboard className="h-4 w-4" />
                  Keyboard Shortcuts
                </h3>
                <Button variant="ghost" size="sm" onClick={() => setShowShortcuts(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                {toolbarButtons.map((btn) => (
                  <div key={btn.mode} className="flex items-center gap-2">
                    <kbd className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs font-mono">
                      {btn.shortcut}
                    </kbd>
                    <span className="text-slate-600 dark:text-slate-400">{btn.label}</span>
                  </div>
                ))}
                <div className="flex items-center gap-2">
                  <kbd className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs font-mono">
                    Ctrl+Enter
                  </kbd>
                  <span className="text-slate-600 dark:text-slate-400">Accept</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs font-mono">
                    Esc
                  </kbd>
                  <span className="text-slate-600 dark:text-slate-400">Close Panel</span>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mode-specific panels */}
      <AnimatePresence mode="wait">
        {activeMode && !showPreview && (
          <motion.div
            key={activeMode}
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <Card variant="glass" className="p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/20 to-violet-500/20">
                    {activeMode === 'rewrite' && <Wand2 className="h-5 w-5 text-blue-600 dark:text-blue-400" />}
                    {activeMode === 'expand' && <Expand className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />}
                    {activeMode === 'condense' && <Minimize2 className="h-5 w-5 text-amber-600 dark:text-amber-400" />}
                    {activeMode === 'optimize' && <Share2 className="h-5 w-5 text-violet-600 dark:text-violet-400" />}
                  </div>
                  <div>
                    <h3 className="font-semibold capitalize">{activeMode}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {activeMode === 'rewrite' && 'Transform your content with AI'}
                      {activeMode === 'expand' && 'Make your content more detailed'}
                      {activeMode === 'condense' && 'Create a shorter version'}
                      {activeMode === 'optimize' && 'Perfect for your target platform'}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setActiveMode(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Mode-specific controls */}
              <AnimatePresence mode="wait">
                {activeMode === 'rewrite' && (
                  <motion.div
                    key="rewrite-controls"
                    variants={slideVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="space-y-4"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">
                          Tone
                        </label>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {toneOptions.map((tone) => (
                            <button
                              key={tone.value}
                              onClick={() => setSelectedTone(tone.value)}
                              className={cn(
                                "flex items-center gap-2 p-3 rounded-xl border-2 text-left transition-all",
                                selectedTone === tone.value
                                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                              )}
                            >
                              <span className="text-slate-500">{tone.icon}</span>
                              <div>
                                <p className="text-sm font-medium">{tone.label}</p>
                                <p className="text-xs text-slate-500">{tone.description}</p>
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">
                          Style
                        </label>
                        <div className="space-y-2">
                          {styleOptions.map((style) => (
                            <button
                              key={style.value}
                              onClick={() => setSelectedStyle(style.value)}
                              className={cn(
                                "w-full flex items-center justify-between p-3 rounded-xl border-2 transition-all",
                                selectedStyle === style.value
                                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                              )}
                            >
                              <span className="text-sm font-medium">{style.label}</span>
                              {selectedStyle === style.value && (
                                <Check className="h-4 w-4 text-blue-500" />
                              )}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeMode === 'expand' && (
                  <motion.div
                    key="expand-controls"
                    variants={slideVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="space-y-4"
                  >
                    <div>
                      <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">
                        Target Length: {targetLength} words
                      </label>
                      <input
                        type="range"
                        min={editedContent.split(/\s+/).length * 1.2}
                        max={2000}
                        step={50}
                        value={targetLength}
                        onChange={(e) => setTargetLength(Number(e.target.value))}
                        className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                      />
                      <div className="flex justify-between text-xs text-slate-500 mt-1">
                        <span>Current: {editedContent.split(/\s+/).length} words</span>
                        <span>Max: 2000 words</span>
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeMode === 'condense' && (
                  <motion.div
                    key="condense-controls"
                    variants={slideVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="space-y-4"
                  >
                    <div>
                      <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">
                        Condense by: {condensePercentage}%
                      </label>
                      <input
                        type="range"
                        min={10}
                        max={80}
                        step={5}
                        value={condensePercentage}
                        onChange={(e) => setCondensePercentage(Number(e.target.value))}
                        className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
                      />
                      <div className="flex justify-between text-xs text-slate-500 mt-1">
                        <span>Slight reduction</span>
                        <span>Heavy reduction</span>
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeMode === 'optimize' && (
                  <motion.div
                    key="optimize-controls"
                    variants={slideVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="space-y-4"
                  >
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">
                      Select Platform
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {platformOptions.map((platform) => (
                        <button
                          key={platform.value}
                          onClick={() => setSelectedPlatform(platform.value)}
                          className={cn(
                            "flex items-center gap-2 p-3 rounded-xl border-2 transition-all",
                            selectedPlatform === platform.value
                              ? "border-violet-500 bg-violet-50 dark:bg-violet-900/20"
                              : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                          )}
                        >
                          <span className="text-slate-500">{platform.icon}</span>
                          <span className="text-sm font-medium">{platform.label}</span>
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Error display */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-3 bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 rounded-lg"
                >
                  <p className="text-sm text-rose-600 dark:text-rose-400">{error}</p>
                </motion.div>
              )}

              {/* Action buttons */}
              <div className="flex items-center justify-end gap-3 mt-6">
                <Button variant="ghost" onClick={() => setActiveMode(null)}>
                  Cancel
                </Button>
                <Button 
                  onClick={handleProcess}
                  disabled={isProcessing || !editedContent.trim()}
                  loading={isProcessing}
                >
                  {isProcessing ? (
                    <>Processing...</>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Apply {activeMode.charAt(0).toUpperCase() + activeMode.slice(1)}
                    </>
                  )}
                </Button>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Preview Panel */}
      <AnimatePresence>
        {showPreview && previewContent && (
          <motion.div
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <Card variant="glass" className="p-4 border-l-4 border-l-blue-500">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Sparkles className="h-5 w-5 text-blue-500" />
                  <h3 className="font-semibold">AI Suggestion</h3>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowDiff(!showDiff)}
                  >
                    {showDiff ? 'Hide Diff' : 'Show Diff'}
                  </Button>
                </div>
              </div>

              {showDiff ? (
                renderDiff()
              ) : (
                <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-900/20">
                  <p className="text-sm text-slate-900 dark:text-slate-100 whitespace-pre-wrap">
                    {previewContent}
                  </p>
                </div>
              )}

              {/* Stats */}
              <div className="flex items-center gap-6 mt-4 text-sm text-slate-500">
                <span>Original: {editedContent.split(/\s+/).length} words</span>
                <ArrowRightLeft className="h-4 w-4" />
                <span className="text-blue-600 dark:text-blue-400">
                  New: {previewContent.split(/\s+/).length} words
                </span>
                <span className={cn(
                  "ml-auto",
                  previewContent.split(/\s+/).length > editedContent.split(/\s+/).length
                    ? "text-emerald-600"
                    : "text-amber-600"
                )}>
                  {((previewContent.split(/\s+/).length - editedContent.split(/\s+/).length) / editedContent.split(/\s+/).length * 100).toFixed(0)}%
                  {previewContent.split(/\s+/).length > editedContent.split(/\s+/).length ? ' longer' : ' shorter'}
                </span>
              </div>

              {/* Accept/Reject */}
              <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
                <Tooltip content="Ctrl+Backspace">
                  <Button variant="outline" onClick={handleReject}>
                    <X className="h-4 w-4 mr-2" />
                    Reject
                  </Button>
                </Tooltip>
                <Tooltip content="Ctrl+Enter">
                  <Button variant="success" onClick={handleAccept}>
                    <Check className="h-4 w-4 mr-2" />
                    Accept Changes
                  </Button>
                </Tooltip>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Editor */}
      <Card variant={hasChanges ? 'elevated' : 'default'} className="relative">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              Content Editor
              {hasChanges && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400">
                  Unsaved
                </span>
              )}
            </CardTitle>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Info className="h-4 w-4" />
              <span>{editedContent.split(/\s+/).length} words</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <textarea
            ref={textareaRef}
            value={editedContent}
            onChange={handleManualEdit}
            className={cn(
              "w-full min-h-[300px] p-4 rounded-xl",
              "bg-slate-50 dark:bg-slate-800/50",
              "border-2 border-slate-200 dark:border-slate-700",
              "text-slate-900 dark:text-slate-100",
              "placeholder:text-slate-400",
              "focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10",
              "transition-all duration-200",
              "resize-y",
              "font-mono text-sm leading-relaxed"
            )}
            placeholder="Start writing or paste your content here..."
            spellCheck={false}
          />
        </CardContent>
      </Card>
    </div>
  )
}

// Export types for consumers
export type { SmartEditorProps, EditMode }
