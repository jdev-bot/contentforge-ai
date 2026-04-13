'use client'

import { useState, useCallback, useMemo } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Tooltip } from '@/components/ui/Tooltip'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/hooks/useToast'
import { 
  schedulePost, 
  updateScheduledPost, 
  getScheduledPosts, 
  ScheduleRequest, 
  ScheduledPost,
  GeneratedAsset 
} from '@/lib/api'
import { 
  X, 
  Calendar, 
  Clock, 
  Globe, 
  Repeat, 
  AlertCircle,
  Check,
  ChevronDown,
  FileText,
  Image,
  Video,
  Hash,
  AlertTriangle,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface ScheduleModalProps {
  isOpen: boolean
  onClose: () => void
  asset?: GeneratedAsset
  contentTitle?: string
  existingSchedule?: ScheduledPost
  mode?: 'create' | 'edit'
  onSuccess?: () => void
}

const PLATFORMS = [
  { id: 'twitter', name: 'X (Twitter)', icon: '𝕏', color: 'bg-gray-900 text-white' },
  { id: 'linkedin', name: 'LinkedIn', icon: 'in', color: 'bg-blue-700 text-white' },
  { id: 'facebook', name: 'Facebook', icon: 'f', color: 'bg-blue-600 text-white' },
  { id: 'instagram', name: 'Instagram', icon: '📷', color: 'bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600 text-white' },
  { id: 'threads', name: 'Threads', icon: '🧵', color: 'bg-black text-white' },
  { id: 'tiktok', name: 'TikTok', icon: '🎵', color: 'bg-black text-white' },
  { id: 'youtube', name: 'YouTube', icon: '▶', color: 'bg-red-600 text-white' },
  { id: 'newsletter', name: 'Newsletter', icon: '📧', color: 'bg-orange-500 text-white' },
  { id: 'blog', name: 'Blog', icon: '📝', color: 'bg-purple-600 text-white' },
] as const

const TIMEZONES = [
  { id: 'UTC', name: 'UTC (Coordinated Universal Time)', offset: 'UTC+0' },
  { id: 'America/New_York', name: 'Eastern Time (ET)', offset: 'UTC-4/5' },
  { id: 'America/Chicago', name: 'Central Time (CT)', offset: 'UTC-5/6' },
  { id: 'America/Denver', name: 'Mountain Time (MT)', offset: 'UTC-6/7' },
  { id: 'America/Los_Angeles', name: 'Pacific Time (PT)', offset: 'UTC-7/8' },
  { id: 'Europe/London', name: 'London (GMT)', offset: 'UTC+0/1' },
  { id: 'Europe/Paris', name: 'Paris (CET)', offset: 'UTC+1/2' },
  { id: 'Europe/Berlin', name: 'Berlin (CET)', offset: 'UTC+1/2' },
  { id: 'Asia/Tokyo', name: 'Tokyo (JST)', offset: 'UTC+9' },
  { id: 'Asia/Shanghai', name: 'Shanghai (CST)', offset: 'UTC+8' },
  { id: 'Asia/Singapore', name: 'Singapore (SGT)', offset: 'UTC+8' },
  { id: 'Asia/Dubai', name: 'Dubai (GST)', offset: 'UTC+4' },
  { id: 'Australia/Sydney', name: 'Sydney (AEST)', offset: 'UTC+10/11' },
  { id: 'Pacific/Auckland', name: 'Auckland (NZST)', offset: 'UTC+12/13' },
]

const RECURRING_OPTIONS = [
  { id: 'none', name: 'One-time', description: 'Post only once' },
  { id: 'daily', name: 'Daily', description: 'Repeat every day' },
  { id: 'weekly', name: 'Weekly', description: 'Repeat every week' },
  { id: 'weekdays', name: 'Weekdays', description: 'Monday through Friday' },
  { id: 'custom', name: 'Custom', description: 'Set custom schedule' },
] as const

const QUICK_TEMPLATES = [
  { name: 'Morning Peak', hour: 9, minute: 0, description: 'Best for B2B content' },
  { name: 'Lunch Time', hour: 12, minute: 0, description: 'High engagement window' },
  { name: 'Afternoon Peak', hour: 15, minute: 0, description: 'Prime engagement time' },
  { name: 'Evening', hour: 18, minute: 0, description: 'After work browsing' },
  { name: 'Night Owl', hour: 21, minute: 0, description: 'Late night audience' },
]

export default function ScheduleModal({ 
  isOpen, 
  onClose, 
  asset, 
  contentTitle,
  existingSchedule,
  mode = 'create',
  onSuccess 
}: ScheduleModalProps) {
  const { showToast } = useToast()
  const [loading, setLoading] = useState(false)
  const [showTimezoneDropdown, setShowTimezoneDropdown] = useState(false)
  const [showRecurringDropdown, setShowRecurringDropdown] = useState(false)
  const [conflicts, setConflicts] = useState<ScheduledPost[]>([])
  
  // Form state
  const [selectedDate, setSelectedDate] = useState(() => {
    if (existingSchedule?.scheduled_at) {
      return new Date(existingSchedule.scheduled_at).toISOString().split('T')[0]
    }
    return new Date().toISOString().split('T')[0]
  })
  
  const [selectedTime, setSelectedTime] = useState(() => {
    if (existingSchedule?.scheduled_at) {
      const date = new Date(existingSchedule.scheduled_at)
      return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }
    return '09:00'
  })
  
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(() => {
    if (existingSchedule?.platforms) return existingSchedule.platforms
    return asset?.platform ? [asset.platform] : []
  })
  
  const [timezone, setTimezone] = useState(() => {
    return existingSchedule?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  })
  
  const [recurring, setRecurring] = useState(() => {
    return existingSchedule?.recurring_pattern || 'none'
  })
  
  const [showPreview, setShowPreview] = useState(true)

  // Check for scheduling conflicts
  const checkConflicts = useCallback(async (date: string, time: string, platforms: string[]) => {
    try {
      const scheduledPosts = await getScheduledPosts()
      const scheduledDate = new Date(`${date}T${time}`)
      
      const conflicts = scheduledPosts.filter(post => {
        if (mode === 'edit' && post.id === existingSchedule?.id) return false
        
        const postDate = new Date(post.scheduled_at)
        const isSameTime = Math.abs(postDate.getTime() - scheduledDate.getTime()) < 5 * 60 * 1000 // Within 5 minutes
        const hasSamePlatform = post.platforms.some(p => platforms.includes(p))
        return isSameTime && hasSamePlatform && post.status === 'scheduled'
      })
      
      setConflicts(conflicts)
    } catch {
      // Silently fail conflict check
    }
  }, [mode, existingSchedule])

  const handleDateChange = useCallback((date: string) => {
    setSelectedDate(date)
    if (selectedPlatforms.length > 0) {
      checkConflicts(date, selectedTime, selectedPlatforms)
    }
  }, [selectedTime, selectedPlatforms, checkConflicts])

  const handleTimeChange = useCallback((time: string) => {
    setSelectedTime(time)
    if (selectedPlatforms.length > 0) {
      checkConflicts(selectedDate, time, selectedPlatforms)
    }
  }, [selectedDate, selectedPlatforms, checkConflicts])

  const togglePlatform = useCallback((platformId: string) => {
    setSelectedPlatforms(prev => {
      const newPlatforms = prev.includes(platformId)
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
      checkConflicts(selectedDate, selectedTime, newPlatforms)
      return newPlatforms
    })
  }, [selectedDate, selectedTime, checkConflicts])

  const handleSubmit = useCallback(async () => {
    if (selectedPlatforms.length === 0) {
      showToast('Please select at least one platform', 'error')
      return
    }

    const scheduledAt = new Date(`${selectedDate}T${selectedTime}`)
    if (scheduledAt < new Date()) {
      showToast('Cannot schedule in the past', 'error')
      return
    }

    setLoading(true)
    try {
      const request: ScheduleRequest = {
        asset_id: asset?.id || existingSchedule?.asset_id || '',
        content: asset?.content || existingSchedule?.content || '',
        platforms: selectedPlatforms,
        scheduled_at: scheduledAt.toISOString(),
        timezone,
        recurring_pattern: recurring !== 'none' ? recurring : undefined,
      }

      if (mode === 'edit' && existingSchedule) {
        await updateScheduledPost(existingSchedule.id, request)
        showToast('Schedule updated successfully', 'success')
      } else {
        await schedulePost(request)
        showToast('Post scheduled successfully', 'success')
      }

      onSuccess?.()
      onClose()
    } catch (error) {
      console.error('Failed to schedule:', error)
      showToast('Failed to schedule post', 'error')
    } finally {
      setLoading(false)
    }
  }, [selectedDate, selectedTime, selectedPlatforms, timezone, recurring, asset, existingSchedule, mode, onSuccess, onClose, showToast])

  const applyTemplate = useCallback((template: typeof QUICK_TEMPLATES[0]) => {
    setSelectedTime(`${String(template.hour).padStart(2, '0')}:${String(template.minute).padStart(2, '0')}`)
  }, [])

  const getPlatformColor = useCallback((platformId: string) => {
    const platform = PLATFORMS.find(p => p.id === platformId)
    return platform?.color || 'bg-gray-500 text-white'
  }, [])

  const getPlatformName = useCallback((platformId: string) => {
    const platform = PLATFORMS.find(p => p.id === platformId)
    return platform?.name || platformId
  }, [])

  const previewDate = useMemo(() => {
    const date = new Date(`${selectedDate}T${selectedTime}`)
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      timeZone: timezone,
    })
  }, [selectedDate, selectedTime, timezone])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-hidden bg-white dark:bg-slate-900 rounded-2xl shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center">
              <Calendar className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                {mode === 'edit' ? 'Edit Schedule' : 'Schedule Post'}
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {contentTitle || 'Schedule your content'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Conflict Warnings */}
            {conflicts.length > 0 && (
              <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
                      Scheduling Conflicts Detected
                    </p>
                    <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                      You have {conflicts.length} other post(s) scheduled at the same time on overlapping platforms.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Templates */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                Quick Templates
              </label>
              <div className="flex flex-wrap gap-2">
                {QUICK_TEMPLATES.map(template => (
                  <button
                    key={template.name}
                    onClick={() => applyTemplate(template)}
                    className="px-3 py-2 text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-violet-100 dark:hover:bg-violet-900/30 hover:text-violet-700 dark:hover:text-violet-300 transition-colors"
                    title={template.description}
                  >
                    {template.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Date & Time */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  <Calendar className="inline h-4 w-4 mr-1.5" />
                  Date
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => handleDateChange(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition-all"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  <Clock className="inline h-4 w-4 mr-1.5" />
                  Time
                </label>
                <input
                  type="time"
                  value={selectedTime}
                  onChange={(e) => handleTimeChange(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition-all"
                />
              </div>
            </div>

            {/* Timezone Selector */}
            <div className="relative">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                <Globe className="inline h-4 w-4 mr-1.5" />
                Timezone
              </label>
              <button
                onClick={() => setShowTimezoneDropdown(!showTimezoneDropdown)}
                className="w-full flex items-center justify-between px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 hover:border-violet-400 dark:hover:border-violet-600 transition-colors"
              >
                <span>
                  {TIMEZONES.find(t => t.id === timezone)?.name || timezone}
                </span>
                <ChevronDown className={cn(
                  "h-4 w-4 transition-transform",
                  showTimezoneDropdown && "rotate-180"
                )} />
              </button>
              
              {showTimezoneDropdown && (
                <div className="absolute z-10 w-full mt-2 max-h-60 overflow-y-auto bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-xl">
                  {TIMEZONES.map(tz => (
                    <button
                      key={tz.id}
                      onClick={() => {
                        setTimezone(tz.id)
                        setShowTimezoneDropdown(false)
                      }}
                      className="w-full px-4 py-2.5 text-left hover:bg-violet-50 dark:hover:bg-violet-900/30 transition-colors"
                    >
                      <span className="text-sm text-slate-900 dark:text-slate-100">{tz.name}</span>
                      <span className="text-xs text-slate-500 dark:text-slate-400 ml-2">{tz.offset}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Platform Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                Platforms
                {selectedPlatforms.length > 0 && (
                  <span className="ml-2 text-xs text-violet-600 dark:text-violet-400">
                    ({selectedPlatforms.length} selected)
                  </span>
                )}
              </label>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                {PLATFORMS.map(platform => (
                  <button
                    key={platform.id}
                    onClick={() => togglePlatform(platform.id)}
                    className={cn(
                      "relative p-3 rounded-xl border-2 transition-all text-center",
                      selectedPlatforms.includes(platform.id)
                        ? "border-violet-500 bg-violet-50 dark:bg-violet-900/20"
                        : "border-slate-200 dark:border-slate-700 hover:border-violet-300 dark:hover:border-violet-700"
                    )}
                  >
                    <div className={cn(
                      "w-8 h-8 mx-auto rounded-lg flex items-center justify-center text-sm font-bold mb-2",
                      platform.color
                    )}>
                      {platform.icon}
                    </div>
                    <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
                      {platform.name}
                    </span>
                    {selectedPlatforms.includes(platform.id) && (
                      <div className="absolute top-1 right-1">
                        <Check className="h-3 w-3 text-violet-600 dark:text-violet-400" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Recurring Options */}
            <div className="relative">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                <Repeat className="inline h-4 w-4 mr-1.5" />
                Recurrence
              </label>
              <button
                onClick={() => setShowRecurringDropdown(!showRecurringDropdown)}
                className="w-full flex items-center justify-between px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 hover:border-violet-400 dark:hover:border-violet-600 transition-colors"
              >
                <span>
                  {RECURRING_OPTIONS.find(r => r.id === recurring)?.name || 'One-time'}
                </span>
                <ChevronDown className={cn(
                  "h-4 w-4 transition-transform",
                  showRecurringDropdown && "rotate-180"
                )} />
              </button>
              
              {showRecurringDropdown && (
                <div className="absolute z-10 w-full mt-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-xl">
                  {RECURRING_OPTIONS.map(option => (
                    <button
                      key={option.id}
                      onClick={() => {
                        setRecurring(option.id)
                        setShowRecurringDropdown(false)
                      }}
                      className="w-full px-4 py-3 text-left hover:bg-violet-50 dark:hover:bg-violet-900/30 transition-colors"
                    >
                      <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{option.name}</span>
                      <span className="text-xs text-slate-500 dark:text-slate-400 ml-2">— {option.description}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Preview */}
            {showPreview && (asset || existingSchedule) && (
              <Card className="border-dashed">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Content Preview
                    </h3>
                    <button
                      onClick={() => setShowPreview(false)}
                      className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                    >
                      Hide
                    </button>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-4">
                    {asset?.content || existingSchedule?.content}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Schedule Summary */}
            <div className="p-4 bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-800 rounded-xl">
              <h3 className="text-sm font-semibold text-violet-900 dark:text-violet-100 mb-2">
                Schedule Summary
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                  <span className="text-violet-800 dark:text-violet-200">{previewDate}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                  <span className="text-violet-800 dark:text-violet-200">
                    {TIMEZONES.find(t => t.id === timezone)?.name}
                  </span>
                </div>
                {selectedPlatforms.length > 0 && (
                  <div className="flex items-start gap-2">
                    <Hash className="h-4 w-4 text-violet-600 dark:text-violet-400 mt-0.5" />
                    <div className="flex flex-wrap gap-1">
                      {selectedPlatforms.map(platformId => (
                        <Badge 
                          key={platformId}
                          variant="primary" 
                          size="sm"
                          className="bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300"
                        >
                          {getPlatformName(platformId)}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {recurring !== 'none' && (
                  <div className="flex items-center gap-2">
                    <Repeat className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                    <span className="text-violet-800 dark:text-violet-200">
                      Repeats {RECURRING_OPTIONS.find(r => r.id === recurring)?.name?.toLowerCase()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50">
          <div className="flex items-center gap-2">
            {selectedPlatforms.length === 0 && (
              <span className="text-sm text-amber-600 dark:text-amber-400 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                Select at least one platform
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSubmit}
              loading={loading}
              disabled={selectedPlatforms.length === 0}
              leftIcon={<Calendar className="h-4 w-4" />}
            >
              {mode === 'edit' ? 'Update Schedule' : 'Schedule Post'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
