'use client'

import { useState, useCallback } from 'react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Input } from './ui/Input'
import { useToast } from '../hooks/useToast'

interface BulkOperationsModalProps {
  isOpen: boolean
  onClose: () => void
  projectId?: string
  onOperationComplete?: () => void
}

type BulkOperationType = 'import' | 'generate' | 'schedule'
type ImportFormat = 'csv' | 'json'
type SchedulePlatform = 'twitter' | 'linkedin' | 'facebook' | 'instagram' | 'tiktok'

interface ImportPreview {
  total: number
  valid: number
  invalid: number
  sample: Array<{
    title: string
    source_type: string
    source_url?: string
  }>
}

interface ScheduledItem {
  id: string
  title: string
  platform: string
  scheduledFor: string
  status: 'pending' | 'scheduled' | 'processing' | 'published'
}

export default function BulkOperationsModal({
  isOpen,
  onClose,
  projectId,
  onOperationComplete,
}: BulkOperationsModalProps) {
  const { showToast } = useToast()
  const [activeTab, setActiveTab] = useState<BulkOperationType>('import')
  
  // Import states
  const [importFormat, setImportFormat] = useState<ImportFormat>('csv')
  const [importData, setImportData] = useState('')
  const [importFile, setImportFile] = useState<File | null>(null)
  const [isParsing, setIsParsing] = useState(false)
  const [importPreview, setImportPreview] = useState<ImportPreview | null>(null)
  const [isImporting, setIsImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  
  // Generate states
  const [selectedContentIds, setSelectedContentIds] = useState<string[]>([])
  const [generatePlatforms, setGeneratePlatforms] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  
  // Schedule states
  const [scheduleContentIds, setScheduleContentIds] = useState<string[]>([])
  const [schedulePlatform, setSchedulePlatform] = useState<SchedulePlatform>('twitter')
  const [scheduleStartTime, setScheduleStartTime] = useState('')
  const [scheduleInterval, setScheduleInterval] = useState(60)
  const [isScheduling, setIsScheduling] = useState(false)
  const [scheduleProgress, setScheduleProgress] = useState(0)
  const [scheduledItems, setScheduledItems] = useState<ScheduledItem[]>([])

  // Sample data for demo
  const sampleContent = [
    { id: '1', title: 'Blog Post About AI', status: 'completed' },
    { id: '2', title: 'Video Script Ideas', status: 'completed' },
    { id: '3', title: 'Marketing Campaign', status: 'completed' },
    { id: '4', title: 'Product Launch', status: 'completed' },
    { id: '5', title: 'Weekly Newsletter', status: 'completed' },
  ]

  const platforms = [
    { id: 'twitter', name: 'Twitter/X', icon: '𝕏' },
    { id: 'linkedin', name: 'LinkedIn', icon: 'in' },
    { id: 'facebook', name: 'Facebook', icon: 'f' },
    { id: 'instagram', name: 'Instagram', icon: '📷' },
    { id: 'tiktok', name: 'TikTok', icon: '🎵' },
  ]

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setImportFile(file)
    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result as string
      setImportData(content)
      parseImportData(content, file.name.endsWith('.json') ? 'json' : 'csv')
    }
    reader.readAsText(file)
  }, [])

  const parseImportData = useCallback((data: string, format: ImportFormat) => {
    setIsParsing(true)
    
    setTimeout(() => {
      try {
        let preview: ImportPreview = { total: 0, valid: 0, invalid: 0, sample: [] }
        
        if (format === 'json') {
          const parsed = JSON.parse(data)
          const items = Array.isArray(parsed) ? parsed : [parsed]
          preview = {
            total: items.length,
            valid: items.filter(item => item.title && item.source_type).length,
            invalid: items.filter(item => !item.title || !item.source_type).length,
            sample: items.slice(0, 3).map(item => ({
              title: item.title || 'Untitled',
              source_type: item.source_type || 'text',
              source_url: item.source_url,
            })),
          }
        } else {
          // Parse CSV
          const lines = data.split('\n').filter(line => line.trim())
          const headers = lines[0]?.split(',').map(h => h.trim()) || []
          const rows = lines.slice(1)
          
          preview = {
            total: rows.length,
            valid: rows.filter(row => row.includes(',')).length,
            invalid: rows.filter(row => !row.includes(',')).length,
            sample: rows.slice(0, 3).map(row => {
              const cols = row.split(',')
              return {
                title: cols[0]?.trim() || 'Untitled',
                source_type: cols[1]?.trim() || 'text',
                source_url: cols[2]?.trim(),
              }
            }),
          }
        }
        
        setImportPreview(preview)
      } catch (error) {
        showToast('Failed to parse import data', 'error')
      } finally {
        setIsParsing(false)
      }
    }, 500)
  }, [showToast])

  const handleImport = useCallback(async () => {
    if (!importPreview || importPreview.valid === 0) return
    
    setIsImporting(true)
    setImportProgress(0)
    
    // Simulate import progress
    const interval = setInterval(() => {
      setImportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 10
      })
    }, 200)
    
    // Simulate API call
    setTimeout(() => {
      clearInterval(interval)
      setImportProgress(100)
      setIsImporting(false)
      showToast(`Successfully imported ${importPreview.valid} items`, 'success')
      onOperationComplete?.()
      setTimeout(onClose, 1000)
    }, 2500)
  }, [importPreview, showToast, onClose, onOperationComplete])

  const handleBulkGenerate = useCallback(async () => {
    if (selectedContentIds.length === 0) {
      showToast('Please select content to generate', 'error')
      return
    }
    if (generatePlatforms.length === 0) {
      showToast('Please select at least one platform', 'error')
      return
    }
    
    setIsGenerating(true)
    setGenerationProgress(0)
    
    // Simulate generation progress
    const interval = setInterval(() => {
      setGenerationProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 5
      })
    }, 300)
    
    // Simulate API call
    setTimeout(() => {
      clearInterval(interval)
      setGenerationProgress(100)
      setIsGenerating(false)
      showToast(`Generated assets for ${selectedContentIds.length} items`, 'success')
      onOperationComplete?.()
      setTimeout(onClose, 1000)
    }, 3000)
  }, [selectedContentIds, generatePlatforms, showToast, onClose, onOperationComplete])

  const handleBulkSchedule = useCallback(async () => {
    if (scheduleContentIds.length === 0) {
      showToast('Please select content to schedule', 'error')
      return
    }
    if (!scheduleStartTime) {
      showToast('Please select a start time', 'error')
      return
    }
    
    setIsScheduling(true)
    setScheduleProgress(0)
    
    // Generate scheduled items
    const startDate = new Date(scheduleStartTime)
    const newItems: ScheduledItem[] = scheduleContentIds.map((id, index) => {
      const scheduledDate = new Date(startDate.getTime() + index * scheduleInterval * 60000)
      const content = sampleContent.find(c => c.id === id)
      return {
        id: `schedule-${id}`,
        title: content?.title || `Content ${id}`,
        platform: schedulePlatform,
        scheduledFor: scheduledDate.toISOString(),
        status: 'scheduled',
      }
    })
    
    // Simulate scheduling progress
    const interval = setInterval(() => {
      setScheduleProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 10
      })
    }, 200)
    
    setTimeout(() => {
      clearInterval(interval)
      setScheduleProgress(100)
      setScheduledItems(newItems)
      setIsScheduling(false)
      showToast(`Scheduled ${newItems.length} items for ${schedulePlatform}`, 'success')
      onOperationComplete?.()
    }, 1500)
  }, [scheduleContentIds, scheduleStartTime, schedulePlatform, scheduleInterval, showToast, onOperationComplete])

  const toggleContentSelection = (id: string, setter: React.Dispatch<React.SetStateAction<string[]>>) => {
    setter(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const togglePlatform = (platformId: string) => {
    setGeneratePlatforms(prev =>
      prev.includes(platformId) ? prev.filter(p => p !== platformId) : [...prev, platformId]
    )
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b border-slate-200 dark:border-slate-700 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 dark:text-white">Bulk Operations</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
          
          {/* Tabs */}
          <div className="flex gap-2 mt-6">
            {[
              { id: 'import', label: '📥 Import Content', desc: 'Bulk import from CSV/JSON' },
              { id: 'generate', label: '✨ Generate Assets', desc: 'Bulk AI content generation' },
              { id: 'schedule', label: '📅 Schedule Posts', desc: 'Bulk scheduling with intervals' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as BulkOperationType)}
                className={`flex-1 p-3 rounded-lg text-left transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-500'
                    : 'bg-slate-50 dark:bg-slate-900 dark:bg-gray-800 border-2 border-transparent hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-gray-700'
                }`}
              >
                <div className="font-semibold text-slate-900 dark:text-slate-100 dark:text-white">{tab.label}</div>
                <div className="text-sm text-slate-500 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500">{tab.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {/* Import Tab */}
          {activeTab === 'import' && (
            <div className="space-y-6">
              <div className="flex gap-4">
                <button
                  onClick={() => setImportFormat('csv')}
                  className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                    importFormat === 'csv'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-slate-200 dark:border-slate-700 dark:border-gray-700 hover:border-slate-300 dark:border-slate-600'
                  }`}
                >
                  <div className="text-2xl mb-2">📄</div>
                  <div className="font-semibold">CSV Import</div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">Comma-separated values</div>
                </button>
                <button
                  onClick={() => setImportFormat('json')}
                  className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                    importFormat === 'json'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-slate-200 dark:border-slate-700 dark:border-gray-700 hover:border-slate-300 dark:border-slate-600'
                  }`}
                >
                  <div className="text-2xl mb-2">🗂️</div>
                  <div className="font-semibold">JSON Import</div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">JSON array format</div>
                </button>
              </div>

              <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 dark:border-gray-600 rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept={importFormat === 'csv' ? '.csv' : '.json'}
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer block"
                >
                  <div className="text-4xl mb-4">📁</div>
                  <div className="text-lg font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-2">
                    Drop your {importFormat.toUpperCase()} file here or click to browse
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    Supports {importFormat === 'csv' ? '.csv' : '.json'} files up to 10MB
                  </div>
                </label>
                
                {importFile && (
                  <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="text-green-700 dark:text-green-300 font-medium">
                      ✓ {importFile.name} ({(importFile.size / 1024).toFixed(1)} KB)
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-slate-50 dark:bg-slate-900 dark:bg-gray-800 rounded-lg p-4">
                <div className="font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-2">
                  {importFormat === 'csv' ? 'CSV Format Example:' : 'JSON Format Example:'}
                </div>
                <pre className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500 overflow-x-auto bg-slate-100 dark:bg-slate-800 dark:bg-gray-900 p-3 rounded">
                  {importFormat === 'csv' 
                    ? `title,source_type,source_url
"My Blog Post",url,https://example.com/post
"Direct Content",text,
"YouTube Video",youtube,https://youtube.com/watch?v=...`
                    : `[
  {
    "title": "My Blog Post",
    "source_type": "url",
    "source_url": "https://example.com/post"
  },
  {
    "title": "Direct Content",
    "source_type": "text"
  }
]`}
                </pre>
              </div>

              {isParsing && (
                <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <span>Parsing file...</span>
                </div>
              )}

              {importPreview && (
                <Card className="p-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                    <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{importPreview.total}</div>
                      <div className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500">Total Items</div>
                    </div>
                    <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{importPreview.valid}</div>
                      <div className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500">Valid</div>
                    </div>
                    <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">{importPreview.invalid}</div>
                      <div className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-400 dark:text-slate-500">Invalid</div>
                    </div>
                  </div>
                  
                  <div className="font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-2">Preview:</div>
                  <div className="space-y-2">
                    {importPreview.sample.map((item, idx) => (
                      <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-900 dark:bg-gray-800 rounded flex justify-between">
                        <span className="font-medium">{item.title}</span>
                        <span className="text-sm text-slate-500 dark:text-slate-400 capitalize">{item.source_type}</span>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {isImporting && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Importing content...</span>
                    <span>{importProgress}%</span>
                  </div>
                  <div className="h-2 bg-slate-200 dark:bg-slate-700 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 transition-all duration-300"
                      style={{ width: `${importProgress}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <Button onClick={onClose} variant="secondary" className="flex-1">
                  Cancel
                </Button>
                <Button 
                  onClick={handleImport} 
                  className="flex-1"
                  disabled={!importPreview || importPreview.valid === 0 || isImporting}
                >
                  {isImporting ? 'Importing...' : `Import ${importPreview?.valid || 0} Items`}
                </Button>
              </div>
            </div>
          )}

          {/* Generate Tab */}
          {activeTab === 'generate' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-3">Select Content</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {sampleContent.map(content => (
                    <label
                      key={content.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        selectedContentIds.includes(content.id)
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-slate-200 dark:border-slate-700 dark:border-gray-700 hover:border-slate-300 dark:border-slate-600'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedContentIds.includes(content.id)}
                        onChange={() => toggleContentSelection(content.id, setSelectedContentIds)}
                        className="w-5 h-5 text-blue-600 rounded"
                      />
                      <span className="flex-1 font-medium">{content.title}</span>
                      <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded">
                        {content.status}
                      </span>
                    </label>
                  ))}
                </div>
                <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {selectedContentIds.length} items selected
                </div>
              </div>

              <div>
                <h3 className="font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-3">Select Platforms</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {platforms.map(platform => (
                    <button
                      key={platform.id}
                      onClick={() => togglePlatform(platform.id)}
                      className={`p-4 rounded-lg border-2 transition-all flex items-center gap-3 ${
                        generatePlatforms.includes(platform.id)
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-slate-200 dark:border-slate-700 dark:border-gray-700 hover:border-slate-300 dark:border-slate-600'
                      }`}
                    >
                      <span className="text-2xl">{platform.icon}</span>
                      <div className="text-left">
                        <div className="font-medium">{platform.name}</div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">AI-generated content</div>
                      </div>
                    </button>
                  ))}
                </div>
                <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {generatePlatforms.length} platforms selected
                </div>
              </div>

              {isGenerating && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Generating assets...</span>
                    <span>{generationProgress}%</span>
                  </div>
                  <div className="h-2 bg-slate-200 dark:bg-slate-700 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-500 transition-all duration-300"
                      style={{ width: `${generationProgress}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <Button onClick={onClose} variant="secondary" className="flex-1">
                  Cancel
                </Button>
                <Button 
                  onClick={handleBulkGenerate}
                  className="flex-1"
                  disabled={selectedContentIds.length === 0 || generatePlatforms.length === 0 || isGenerating}
                >
                  {isGenerating ? 'Generating...' : `Generate ${selectedContentIds.length * generatePlatforms.length} Assets`}
                </Button>
              </div>
            </div>
          )}

          {/* Schedule Tab */}
          {activeTab === 'schedule' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-3">Select Content to Schedule</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {sampleContent.map(content => (
                    <label
                      key={content.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        scheduleContentIds.includes(content.id)
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-slate-200 dark:border-slate-700 dark:border-gray-700 hover:border-slate-300 dark:border-slate-600'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={scheduleContentIds.includes(content.id)}
                        onChange={() => toggleContentSelection(content.id, setScheduleContentIds)}
                        className="w-5 h-5 text-blue-600 rounded"
                      />
                      <span className="flex-1 font-medium">{content.title}</span>
                    </label>
                  ))}
                </div>
                <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {scheduleContentIds.length} items selected
                </div>
              </div>

              <div>
                <h3 className="font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-3">Platform</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {platforms.map(platform => (
                    <button
                      key={platform.id}
                      onClick={() => setSchedulePlatform(platform.id as SchedulePlatform)}
                      className={`p-3 rounded-lg border-2 transition-all flex items-center gap-2 ${
                        schedulePlatform === platform.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-slate-200 dark:border-slate-700 dark:border-gray-700 hover:border-slate-300 dark:border-slate-600'
                      }`}
                    >
                      <span className="text-xl">{platform.icon}</span>
                      <span className="font-medium">{platform.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-300 dark:text-slate-600 mb-2">
                    Start Time
                  </label>
                  <Input
                    type="datetime-local"
                    value={scheduleStartTime}
                    onChange={(e) => setScheduleStartTime(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 dark:text-slate-300 dark:text-slate-600 mb-2">
                    Interval Between Posts (minutes)
                  </label>
                  <Input
                    type="number"
                    min="15"
                    max="1440"
                    value={scheduleInterval}
                    onChange={(e) => setScheduleInterval(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>

              {scheduledItems.length > 0 && (
                <Card className="p-4">
                  <h4 className="font-medium text-slate-900 dark:text-slate-100 dark:text-white mb-3">
                    Scheduled Items Preview
                  </h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {scheduledItems.map((item, idx) => (
                      <div key={item.id} className="flex items-center gap-3 p-2 bg-slate-50 dark:bg-slate-900 dark:bg-gray-800 rounded">
                        <span className="text-sm font-mono text-slate-500 dark:text-slate-400">#{idx + 1}</span>
                        <span className="flex-1 font-medium text-sm truncate">{item.title}</span>
                        <span className="text-xs text-slate-500 dark:text-slate-400">
                          {new Date(item.scheduledFor).toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {isScheduling && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Scheduling posts...</span>
                    <span>{scheduleProgress}%</span>
                  </div>
                  <div className="h-2 bg-slate-200 dark:bg-slate-700 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 transition-all duration-300"
                      style={{ width: `${scheduleProgress}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <Button onClick={onClose} variant="secondary" className="flex-1">
                  Cancel
                </Button>
                <Button 
                  onClick={handleBulkSchedule}
                  className="flex-1"
                  disabled={scheduleContentIds.length === 0 || !scheduleStartTime || isScheduling}
                >
                  {isScheduling ? 'Scheduling...' : `Schedule ${scheduleContentIds.length} Posts`}
                </Button>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}