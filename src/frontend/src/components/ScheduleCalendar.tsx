'use client'

import { useState, useCallback, useMemo, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Tooltip } from '@/components/ui/Tooltip'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import { 
  getScheduledPosts, 
  cancelScheduledPost, 
  publishScheduledPost,
  ScheduledPost,
  updateScheduledPost
} from '@/lib/api'
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon,
  Clock,
  Hash,
  MoreHorizontal,
  Edit3,
  Trash2,
  Play,
  AlertCircle,
  Grid3X3,
  List,
  CheckCircle2,
  XCircle,
  Loader2,
  GripVertical
} from 'lucide-react'
import { cn } from '@/lib/utils'
import ScheduleModal from './ScheduleModal'

interface ScheduleCalendarProps {
  onEditSchedule?: (schedule: ScheduledPost) => void
}

type CalendarView = 'month' | 'week' | 'day' | 'list'
type DragItem = { schedule: ScheduledPost; sourceDate: Date } | null

const PLATFORM_COLORS: Record<string, string> = {
  twitter: 'bg-gray-900 border-gray-900 text-white',
  linkedin: 'bg-blue-700 border-blue-700 text-white',
  facebook: 'bg-blue-600 border-blue-600 text-white',
  instagram: 'bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600 border-transparent text-white',
  threads: 'bg-black border-black text-white',
  tiktok: 'bg-black border-black text-white',
  youtube: 'bg-red-600 border-red-600 text-white',
  newsletter: 'bg-orange-500 border-orange-500 text-white',
  blog: 'bg-purple-600 border-purple-600 text-white',
}

const PLATFORM_ICONS: Record<string, string> = {
  twitter: '𝕏',
  linkedin: 'in',
  facebook: 'f',
  instagram: '📷',
  threads: '🧵',
  tiktok: '🎵',
  youtube: '▶',
  newsletter: '📧',
  blog: '📝',
}

const STATUS_COLORS: Record<string, { bg: string; text: string; icon: typeof CheckCircle2 }> = {
  scheduled: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-300', icon: Clock },
  published: { bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-300', icon: CheckCircle2 },
  failed: { bg: 'bg-rose-100 dark:bg-rose-900/30', text: 'text-rose-700 dark:text-rose-300', icon: XCircle },
  cancelled: { bg: 'bg-slate-100 dark:bg-slate-800', text: 'text-slate-600 dark:text-slate-400', icon: XCircle },
  processing: { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-300', icon: Loader2 },
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

export default function ScheduleCalendar({ onEditSchedule }: ScheduleCalendarProps) {
  const { showToast } = useToast()
  const [schedules, setSchedules] = useState<ScheduledPost[]>([])
  const [loading, setLoading] = useState(true)
  const [currentDate, setCurrentDate] = useState(new Date())
  const [view, setView] = useState<CalendarView>('month')
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduledPost | null>(null)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [showMenu, setShowMenu] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [dragItem, setDragItem] = useState<DragItem>(null)

  // Load scheduled posts
  useEffect(() => {
    loadSchedules()
  }, [])

  const loadSchedules = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getScheduledPosts()
      setSchedules(data)
    } catch (error) {
      console.error('Failed to load schedules:', error)
      showToast('Failed to load scheduled posts', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  // Close menu on outside click
  useEffect(() => {
    const handleClickOutside = () => setShowMenu(null)
    if (showMenu) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showMenu])

  // Calendar navigation
  const goToToday = useCallback(() => {
    setCurrentDate(new Date())
  }, [])

  const goToPrevious = useCallback(() => {
    setCurrentDate(prev => {
      const newDate = new Date(prev)
      if (view === 'month') {
        newDate.setMonth(prev.getMonth() - 1)
      } else if (view === 'week') {
        newDate.setDate(prev.getDate() - 7)
      } else if (view === 'day') {
        newDate.setDate(prev.getDate() - 1)
      }
      return newDate
    })
  }, [view])

  const goToNext = useCallback(() => {
    setCurrentDate(prev => {
      const newDate = new Date(prev)
      if (view === 'month') {
        newDate.setMonth(prev.getMonth() + 1)
      } else if (view === 'week') {
        newDate.setDate(prev.getDate() + 7)
      } else if (view === 'day') {
        newDate.setDate(prev.getDate() + 1)
      }
      return newDate
    })
  }, [view])

  // Get schedules for a specific date
  const getSchedulesForDate = useCallback((date: Date) => {
    return schedules.filter(schedule => {
      const scheduleDate = new Date(schedule.scheduled_at)
      return (
        scheduleDate.getFullYear() === date.getFullYear() &&
        scheduleDate.getMonth() === date.getMonth() &&
        scheduleDate.getDate() === date.getDate()
      )
    })
  }, [schedules])

  // Calendar grid generation
  const calendarDays = useMemo(() => {
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()
    
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const startPadding = firstDay.getDay()
    const daysInMonth = lastDay.getDate()
    
    const days: { date: Date | null; schedules: ScheduledPost[] }[] = []
    
    // Previous month padding
    for (let i = 0; i < startPadding; i++) {
      const prevDate = new Date(year, month, -i)
      days.unshift({ date: prevDate, schedules: [] })
    }
    
    // Current month
    for (let i = 1; i <= daysInMonth; i++) {
      const date = new Date(year, month, i)
      days.push({ date, schedules: getSchedulesForDate(date) })
    }
    
    // Next month padding (fill to 42 cells for 6 rows)
    const remainingCells = 42 - days.length
    for (let i = 1; i <= remainingCells; i++) {
      const nextDate = new Date(year, month + 1, i)
      days.push({ date: nextDate, schedules: [] })
    }
    
    return days
  }, [currentDate, getSchedulesForDate])

  // Week view
  const weekDays = useMemo(() => {
    const startOfWeek = new Date(currentDate)
    startOfWeek.setDate(currentDate.getDate() - currentDate.getDay())
    
    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(startOfWeek)
      date.setDate(startOfWeek.getDate() + i)
      return { date, schedules: getSchedulesForDate(date) }
    })
  }, [currentDate, getSchedulesForDate])

  // Actions
  const handlePublishNow = useCallback(async (schedule: ScheduledPost) => {
    if (!confirm('Are you sure you want to publish this post now?')) return
    
    setActionLoading(schedule.id)
    try {
      await publishScheduledPost(schedule.id)
      showToast('Post published successfully', 'success')
      await loadSchedules()
    } catch (error) {
      showToast('Failed to publish post', 'error')
    } finally {
      setActionLoading(null)
      setShowMenu(null)
    }
  }, [loadSchedules, showToast])

  const handleCancel = useCallback(async (schedule: ScheduledPost) => {
    if (!confirm('Are you sure you want to cancel this scheduled post?')) return
    
    setActionLoading(schedule.id)
    try {
      await cancelScheduledPost(schedule.id)
      showToast('Schedule cancelled', 'success')
      await loadSchedules()
    } catch (error) {
      showToast('Failed to cancel schedule', 'error')
    } finally {
      setActionLoading(null)
      setShowMenu(null)
    }
  }, [loadSchedules, showToast])

  const handleEdit = useCallback((schedule: ScheduledPost) => {
    setSelectedSchedule(schedule)
    setShowScheduleModal(true)
    setShowMenu(null)
    onEditSchedule?.(schedule)
  }, [onEditSchedule])

  // Drag and drop
  const handleDragStart = useCallback((schedule: ScheduledPost, date: Date) => {
    setDragItem({ schedule, sourceDate: date })
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent, targetDate: Date) => {
    e.preventDefault()
    if (!dragItem) return

    const { schedule } = dragItem
    const newDate = new Date(targetDate)
    const oldDate = new Date(schedule.scheduled_at)
    
    // Keep the same time
    newDate.setHours(oldDate.getHours(), oldDate.getMinutes())
    
    try {
      await updateScheduledPost(schedule.id, {
        scheduled_at: newDate.toISOString()
      })
      showToast('Schedule updated', 'success')
      await loadSchedules()
    } catch {
      showToast('Failed to reschedule', 'error')
    } finally {
      setDragItem(null)
    }
  }, [dragItem, loadSchedules, showToast])

  const renderHeader = () => (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border-b border-slate-200 dark:border-slate-700">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={goToPrevious}
            leftIcon={<ChevronLeft className="h-4 w-4" />}
          >
            Prev
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={goToToday}
          >
            Today
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={goToNext}
            rightIcon={<ChevronRight className="h-4 w-4" />}
          >
            Next
          </Button>
        </div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          {view === 'month' && `${MONTHS[currentDate.getMonth()]} ${currentDate.getFullYear()}`}
          {view === 'week' && `Week of ${currentDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`}
          {view === 'day' && currentDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
          {view === 'list' && 'All Scheduled Posts'}
        </h2>
      </div>
      
      <div className="flex items-center gap-2">
        {(['month', 'week', 'day', 'list'] as CalendarView[]).map((v) => (
          <Button
            key={v}
            variant={view === v ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setView(v)}
            leftIcon={
              v === 'month' ? <CalendarIcon className="h-4 w-4" /> :
              v === 'week' ? <Grid3X3 className="h-4 w-4" /> :
              v === 'day' ? <Clock className="h-4 w-4" /> :
              <List className="h-4 w-4" />
            }
          >
            {v.charAt(0).toUpperCase() + v.slice(1)}
          </Button>
        ))}
      </div>
    </div>
  )

  const renderMonthView = () => (
    <div className="flex-1 overflow-auto">
      {/* Day headers */}
      <div className="grid grid-cols-7 border-b border-slate-200 dark:border-slate-700">
        {DAYS.map(day => (
          <div 
            key={day} 
            className="px-4 py-3 text-center text-sm font-semibold text-slate-700 dark:text-slate-300"
          >
            {day}
          </div>
        ))}
      </div>
      
      {/* Calendar grid */}
      <div className="grid grid-cols-7">
        {calendarDays.map(({ date, schedules }, index) => {
          if (!date) return null
          
          const isToday = new Date().toDateString() === date.toDateString()
          const isCurrentMonth = date.getMonth() === currentDate.getMonth()
          const isDragTarget = dragItem && date.toDateString() !== dragItem.sourceDate.toDateString()
          
          return (
            <div
              key={index}
              className={cn(
                "min-h-[120px] p-2 border-b border-r border-slate-200 dark:border-slate-700 transition-colors",
                !isCurrentMonth && "bg-slate-50 dark:bg-slate-900/50",
                isDragTarget && "bg-violet-50 dark:bg-violet-900/20"
              )}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, date)}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={cn(
                    "w-7 h-7 flex items-center justify-center text-sm font-medium rounded-full",
                    isToday && "bg-violet-600 text-white",
                    !isToday && isCurrentMonth && "text-slate-900 dark:text-slate-100",
                    !isCurrentMonth && "text-slate-400 dark:text-slate-600"
                  )}
                >
                  {date.getDate()}
                </span>
                {schedules.length > 0 && (
                  <span className="text-xs text-violet-600 dark:text-violet-400 font-medium">
                    {schedules.length}
                  </span>
                )}
              </div>
              
              <div className="space-y-1">
                {schedules.map(schedule => (
                  <div
                    key={schedule.id}
                    draggable
                    onDragStart={() => handleDragStart(schedule, date)}
                    className="group relative"
                  >
                    <div
                      className={cn(
                        "px-2 py-1.5 rounded-lg text-xs cursor-grab active:cursor-grabbing transition-all hover:shadow-md",
                        schedule.status === 'scheduled' && "bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-200",
                        schedule.status === 'published' && "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-200",
                        schedule.status === 'failed' && "bg-rose-100 dark:bg-rose-900/40 text-rose-800 dark:text-rose-200",
                        schedule.status === 'cancelled' && "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                      )}
                    >
                      <div className="flex items-center gap-1.5">
                        <GripVertical className="h-3 w-3 opacity-0 group-hover:opacity-50" />
                        <span className="font-medium truncate">
                          {new Date(schedule.scheduled_at).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 mt-1">
                        {schedule.platforms.slice(0, 3).map(platform => (
                          <span key={platform} className="text-[10px]">
                            {PLATFORM_ICONS[platform] || '📄'}
                          </span>
                        ))}
                        {schedule.platforms.length > 3 && (
                          <span className="text-[10px]">+{schedule.platforms.length - 3}</span>
                        )}
                      </div>
                    </div>
                    
                    {/* Hover menu */}
                    <div className="absolute right-1 top-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowMenu(showMenu === schedule.id ? null : schedule.id)
                        }}
                        className="p-1 rounded bg-white dark:bg-slate-700 shadow-sm"
                      >
                        <MoreHorizontal className="h-3 w-3" />
                      </button>
                      
                      {showMenu === schedule.id && schedule.status === 'scheduled' && (
                        <div className="absolute right-0 mt-1 w-32 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 py-1 z-10"
                        >
                          <button
                            onClick={() => handleEdit(schedule)}
                            className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                          >
                            <Edit3 className="h-3 w-3" />
                            Edit
                          </button>
                          <button
                            onClick={() => handlePublishNow(schedule)}
                            disabled={actionLoading === schedule.id}
                            className="w-full flex items-center gap-2 px-3 py-2 text-xs text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20"
                          >
                            {actionLoading === schedule.id ? (
                              <Loader2 className="h-3 w-3 animate-spin" />
                            ) : (
                              <>
                                <Play className="h-3 w-3" />
                                Publish Now
                              </>
                            )}
                          </button>
                          <button
                            onClick={() => handleCancel(schedule)}
                            disabled={actionLoading === schedule.id}
                            className="w-full flex items-center gap-2 px-3 py-2 text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/20"
                          >
                            <Trash2 className="h-3 w-3" />
                            Cancel
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )

  const renderWeekView = () => (
    <div className="flex-1 overflow-auto">
      <div className="grid grid-cols-7 min-w-[800px]">
        {weekDays.map(({ date, schedules }) => {
          const isToday = new Date().toDateString() === date.toDateString()
          
          return (
            <div 
              key={date.toISOString()} 
              className={cn(
                "border-r border-slate-200 dark:border-slate-700 min-h-[400px]",
                isToday && "bg-violet-50/50 dark:bg-violet-900/10"
              )}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, date)}
            >
              <div className={cn(
                "p-4 text-center border-b border-slate-200 dark:border-slate-700",
                isToday && "bg-violet-100 dark:bg-violet-900/30"
              )}>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                  {DAYS[date.getDay()]}
                </p>
                <p className={cn(
                  "text-lg font-bold",
                  isToday ? "text-violet-700 dark:text-violet-300" : "text-slate-900 dark:text-slate-100"
                )}>
                  {date.getDate()}
                </p>
              </div>
              
              <div className="p-2 space-y-2">
                {schedules.length === 0 && (
                  <p className="text-xs text-slate-400 dark:text-slate-600 text-center py-4">
                    No scheduled posts
                  </p>
                )}
                {schedules.map(schedule => (
                  <Card 
                    key={schedule.id}
                    draggable
                    onDragStart={() => handleDragStart(schedule, date)}
                    className="cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow"
                  >
                    <CardContent className="p-3">
                      <div className="flex items-start gap-2">
                        <div className="flex-1">
                          <p className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                            {new Date(schedule.scheduled_at).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 mt-1">
                            {schedule.content.substring(0, 60)}...
                          </p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {schedule.platforms.map(platform => (
                              <Badge 
                                key={platform}
                                size="sm"
                                className={cn(
                                  "text-[10px] px-1.5 py-0.5",
                                  PLATFORM_COLORS[platform] || "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                                )}
                              >
                                {PLATFORM_ICONS[platform] || platform}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )

  const renderDayView = () => {
    const daySchedules = getSchedulesForDate(currentDate)
    const hours = Array.from({ length: 24 }, (_, i) => i)
    
    return (
      <div className="flex-1 overflow-auto">
        <div className="space-y-1 p-4">
          {hours.map(hour => {
            const hourSchedules = daySchedules.filter(s => {
              const scheduleHour = new Date(s.scheduled_at).getHours()
              return scheduleHour === hour
            })
            
            const isCurrentHour = new Date().getHours() === hour && 
                                  new Date().toDateString() === currentDate.toDateString()
            
            return (
              <div 
                key={hour}
                className={cn(
                  "flex gap-4 p-3 rounded-lg transition-colors",
                  isCurrentHour && "bg-violet-50 dark:bg-violet-900/20"
                )}
                onDragOver={handleDragOver}
                onDrop={(e) => {
                  const targetDate = new Date(currentDate)
                  targetDate.setHours(hour)
                  handleDrop(e, targetDate)
                }}
              >
                <div className="w-16 text-right">
                  <span className={cn(
                    "text-sm font-medium",
                    isCurrentHour ? "text-violet-700 dark:text-violet-300" : "text-slate-500 dark:text-slate-400"
                  )}>
                    {hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}
                  </span>
                </div>
                
                <div className="flex-1 min-h-[60px] border-l-2 border-slate-200 dark:border-slate-700 pl-4">
                  <div className="space-y-2">
                    {hourSchedules.map(schedule => (
                      <Card 
                        key={schedule.id}
                        draggable
                        onDragStart={() => handleDragStart(schedule, new Date(schedule.scheduled_at))}
                        className="cursor-grab active:cursor-grabbing"
                      >
                        <CardContent className="p-3">
                          <div className="flex items-center gap-3">
                            <GripVertical className="h-4 w-4 text-slate-400" />
                            
                            <div className="flex-1">
                              <p className="text-sm text-slate-900 dark:text-slate-100 line-clamp-2">
                                {schedule.content}
                              </p>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {schedule.platforms.map(platform => (
                                  <Badge 
                                    key={platform}
                                    size="sm"
                                    className={cn(
                                      "text-xs",
                                      PLATFORM_COLORS[platform] || "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                                    )}
                                  >
                                    {PLATFORM_ICONS[platform] || platform}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            
                            {schedule.status === 'scheduled' && (
                              <div className="flex items-center gap-1">
                                <button
                                  onClick={() => handleEdit(schedule)}
                                  className="p-2 text-slate-400 hover:text-blue-600 rounded-lg hover:bg-blue-50"
                                >
                                  <Edit3 className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() => handleCancel(schedule)}
                                  className="p-2 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  const renderListView = () => (
    <div className="flex-1 overflow-auto p-6">
      {schedules.length === 0 ? (
        <div className="text-center py-12">
          <CalendarIcon className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">No scheduled posts</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">Schedule your first post to see it here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {schedules
            .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime())
            .map(schedule => {
              const statusConfig = STATUS_COLORS[schedule.status] || STATUS_COLORS.scheduled
              const StatusIcon = statusConfig.icon
              
              return (
                <Card key={schedule.id} className="group hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className={cn(
                        "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0",
                        statusConfig.bg
                      )}>
                        <StatusIcon className={cn("h-5 w-5", statusConfig.text)} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                            {new Date(schedule.scheduled_at).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: 'numeric',
                              minute: '2-digit',
                            })}
                          </span>
                          <Badge variant={schedule.status === 'scheduled' ? 'primary' : 'secondary'} size="sm">
                            {schedule.status}
                          </Badge>
                          
                          {schedule.recurring_pattern && schedule.recurring_pattern !== 'none' && (
                            <Badge variant="secondary" size="sm" className="bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
                              🔄 {schedule.recurring_pattern}
                            </Badge>
                          )}
                        </div>
                        
                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 line-clamp-2">
                          {schedule.content}
                        </p>
                        
                        <div className="flex flex-wrap gap-2 mt-3">
                          {schedule.platforms.map(platform => (
                            <Badge 
                              key={platform}
                              size="sm"
                              className={cn(
                                "text-xs",
                                PLATFORM_COLORS[platform] || "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                              )}
                            >
                              {PLATFORM_ICONS[platform] || platform}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      {schedule.status === 'scheduled' && (
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Tooltip content="Edit" position="left">
                            <button
                              onClick={() => handleEdit(schedule)}
                              className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            >
                              <Edit3 className="h-4 w-4" />
                            </button>
                          </Tooltip>
                          
                          <Tooltip content="Publish Now" position="left">
                            <button
                              onClick={() => handlePublishNow(schedule)}
                              disabled={actionLoading === schedule.id}
                              className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                            >
                              {actionLoading === schedule.id ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Play className="h-4 w-4" />
                              )}
                            </button>
                          </Tooltip>
                          
                          <Tooltip content="Cancel" position="left">
                            <button
                              onClick={() => handleCancel(schedule)}
                              disabled={actionLoading === schedule.id}
                              className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </Tooltip>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
        </div>
      )}
    </div>
  )

  if (loading) {
    return (
      <div className="h-full">
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <Skeleton className="h-6 w-48" />
          <div className="flex gap-2">
            <Skeleton className="h-9 w-20" />
            <Skeleton className="h-9 w-20" />
            <Skeleton className="h-9 w-20" />
            <Skeleton className="h-9 w-20" />
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-7 gap-2">
            {[...Array(35)].map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="h-full flex flex-col bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        {renderHeader()}
        
        {view === 'month' && renderMonthView()}
        {view === 'week' && renderWeekView()}
        {view === 'day' && renderDayView()}
        {view === 'list' && renderListView()}
      </div>

      <ScheduleModal
        isOpen={showScheduleModal}
        onClose={() => {
          setShowScheduleModal(false)
          setSelectedSchedule(null)
        }}
        existingSchedule={selectedSchedule || undefined}
        mode="edit"
        onSuccess={loadSchedules}
      />
    </>
  )
}
