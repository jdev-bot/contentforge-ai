'use client'

import { useState, useMemo, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  Clock,
  Users,
  Filter,
  Plus,
  AlertTriangle,
  Edit3,
  Trash2,
  CheckCircle2,
  X,
  Calendar
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Avatar, AvatarGroup } from '@/components/ui/Avatar'
import { Tooltip } from '@/components/ui/Tooltip'
import { cn } from '@/lib/utils'
import {
  getTeamCalendarMonth,
  getTeamCalendarDay,
  checkTeamCalendarConflicts,
  listOrganizations,
  type TeamCalendarMember,
  type TeamCalendarPost,
  type TeamCalendarDay,
  type TeamConflictDetail,
} from '@/lib/api'

// Types
interface CalendarDayEntry {
  date: Date
  isCurrentMonth: boolean
}

// Calendar utilities
const getDaysInMonth = (year: number, month: number) => {
  return new Date(year, month + 1, 0).getDate()
}

const getFirstDayOfMonth = (year: number, month: number) => {
  return new Date(year, month, 1).getDay()
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const getMonthYear = (date: Date) => {
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
}

export default function TeamCalendar() {
  // Core state
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month')
  const [filterMember, setFilterMember] = useState<string | 'all'>('all')

  // API data state
  const [members, setMembers] = useState<TeamCalendarMember[]>([])
  const [calendarDays, setCalendarDays] = useState<TeamCalendarDay[]>([])
  const [stats, setStats] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Selected day detail
  const [selectedDayPosts, setSelectedDayPosts] = useState<TeamCalendarPost[]>([])
  const [selectedDayLoading, setSelectedDayLoading] = useState(false)

  // Drag & drop
  const [draggedPost, setDraggedPost] = useState<TeamCalendarPost | null>(null)

  // Conflict modal
  const [showConflictModal, setShowConflictModal] = useState(false)
  const [conflicts, setConflicts] = useState<TeamConflictDetail[]>([])

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()
  const monthNum = month + 1 // 1-indexed for API

  // Org ID — resolved from user's first org
  const [orgId, setOrgId] = useState<string>('')

  // Fetch org membership on mount
  useEffect(() => {
    async function fetchOrgId() {
      try {
        const orgs = await listOrganizations()
        if (orgs.length > 0) {
          setOrgId(orgs[0].id)
        }
      } catch {
        // User may not have an org yet — component works without one
      }
    }
    fetchOrgId()
  }, [])

  // Fetch calendar data when month/org changes
  useEffect(() => {
    if (!orgId) {
      setLoading(false)
      return
    }

    async function fetchCalendarData() {
      setLoading(true)
      setError(null)
      try {
        const data = await getTeamCalendarMonth(
          orgId,
          year,
          monthNum,
          filterMember !== 'all' ? filterMember : undefined,
        )
        setMembers(data.members)
        setCalendarDays(data.days)
        setStats(data.stats)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load calendar')
      } finally {
        setLoading(false)
      }
    }

    fetchCalendarData()
  }, [orgId, year, monthNum, filterMember])

  // Fetch selected day detail
  useEffect(() => {
    if (!selectedDate || !orgId) return

    async function fetchDayDetail() {
      setSelectedDayLoading(true)
      try {
        const dateStr = selectedDate!.toISOString().slice(0, 10)
        const data = await getTeamCalendarDay(
          orgId,
          dateStr,
          filterMember !== 'all' ? filterMember : undefined,
        )
        setSelectedDayPosts(data.posts)
      } catch {
        setSelectedDayPosts([])
      } finally {
        setSelectedDayLoading(false)
      }
    }

    fetchDayDetail()
  }, [selectedDate, orgId, filterMember])

  // Build posts lookup from calendarDays for the grid view
  const postsByDate = useMemo(() => {
    const map = new Map<string, TeamCalendarPost[]>()
    for (const day of calendarDays) {
      map.set(day.date, day.posts)
    }
    return map
  }, [calendarDays])

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev)
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1)
      } else {
        newDate.setMonth(prev.getMonth() + 1)
      }
      return newDate
    })
    setSelectedDate(null)
  }

  const navigateToday = () => {
    setCurrentDate(new Date())
    setSelectedDate(null)
  }

  const handleDrop = async (date: Date) => {
    if (!draggedPost || !orgId) return

    // Check for conflicts via API
    try {
      const newTime = new Date(date)
      newTime.setHours(new Date(draggedPost.scheduled_at).getHours(), new Date(draggedPost.scheduled_at).getMinutes())
      const conflictResult = await checkTeamCalendarConflicts(
        orgId,
        newTime.toISOString(),
        draggedPost.platform,
        draggedPost.id,
      )
      if (conflictResult.has_conflicts) {
        setConflicts(conflictResult.conflicts)
        setShowConflictModal(true)
      }
    } catch {
      // Silently handle conflict check failure
    }
    setDraggedPost(null)
  }

  const getPlatformIcon = (platform: string) => {
    const icons: Record<string, string> = {
      linkedin: '🔗',
      twitter: '🐦',
      facebook: '📘',
      instagram: '📷',
      blog: '📝',
    }
    return icons[platform] || '📄'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-emerald-500'
      case 'scheduled': return 'bg-blue-500'
      case 'pending': return 'bg-blue-400'
      case 'processing': return 'bg-indigo-500'
      case 'draft': return 'bg-slate-400'
      case 'failed': return 'bg-rose-500'
      default: return 'bg-slate-400'
    }
  }

  const getAssignedMembers = (ids: string[]) => {
    return members.filter(m => ids.includes(m.id))
  }

  // Generate calendar grid days
  const gridDays = useMemo(() => {
    const days: CalendarDayEntry[] = []
    const daysInMonthVal = getDaysInMonth(year, month)
    const firstDay = getFirstDayOfMonth(year, month)
    const prevMonthDays = getDaysInMonth(year, month - 1)

    // Previous month padding
    for (let i = firstDay - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, prevMonthDays - i),
        isCurrentMonth: false,
      })
    }

    // Current month
    for (let i = 1; i <= daysInMonthVal; i++) {
      days.push({
        date: new Date(year, month, i),
        isCurrentMonth: true,
      })
    }

    // Next month padding
    const remainingDays = 42 - days.length
    for (let i = 1; i <= remainingDays; i++) {
      days.push({
        date: new Date(year, month + 1, i),
        isCurrentMonth: false,
      })
    }

    return days
  }, [year, month])

  // No org state
  if (!loading && !orgId) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Team Calendar"
          description="Schedule and manage content across your team"
          icon={<Calendar className="w-5 h-5 text-blue-600" />}
        />
        <Card>
          <CardContent className="p-12 text-center">
            <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="h-8 w-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
              No Organization Found
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-4">
              Create or join an organization to use the team calendar.
            </p>
            <Button variant="primary" leftIcon={<Plus className="h-4 w-4" />}>
              Create Organization
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Team Calendar"
        description="Schedule and manage content across your team"
        icon={<Calendar className="w-5 h-5 text-blue-600" />}
        actions={
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={navigateToday}
            >
              Today
            </Button>
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
              {(['month', 'week', 'day'] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={cn(
                    'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                    viewMode === mode
                      ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  )}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="h-4 w-4" />}
            >
              New Schedule
            </Button>
          </div>
        }
      />

      {/* Calendar Navigation & Filter */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigateMonth('prev')}
                className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-400" />
              </button>

              <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 min-w-[200px] text-center">
                {getMonthYear(currentDate)}
              </h3>

              <button
                onClick={() => navigateMonth('next')}
                className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                <ChevronRight className="h-5 w-5 text-slate-600 dark:text-slate-400" />
              </button>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-slate-400" />
                <select
                  value={filterMember}
                  onChange={(e) => setFilterMember(e.target.value)}
                  className="text-sm bg-transparent border-none focus:ring-0 text-slate-700 dark:text-slate-300 cursor-pointer"
                >
                  <option value="all">All Members</option>
                  {members.map(member => (
                    <option key={member.id} value={member.id}>
                      {member.name}
                    </option>
                  ))}
                </select>
              </div>

              {members.length > 0 && (
                <>
                  <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />
                  <AvatarGroup
                    avatars={members.slice(0, 4).map(m => ({
                      name: m.name,
                      src: m.avatar_url || undefined
                    }))}
                    size="sm"
                    max={4}
                  />
                </>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
          ) : error ? (
            <div className="text-center py-12 text-rose-500">{error}</div>
          ) : (
            /* Calendar Grid */
            <div className="space-y-2">
              {/* Day headers */}
              <div className="grid grid-cols-7 gap-1">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div
                    key={day}
                    className="text-center text-sm font-medium text-slate-500 dark:text-slate-400 py-2"
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar days */}
              <div className="grid grid-cols-7 gap-1">
                {gridDays.map(({ date, isCurrentMonth }, index) => {
                  const dateKey = date.toISOString().slice(0, 10)
                  const dayPosts = postsByDate.get(dateKey) || []
                  const isToday = date.toDateString() === new Date().toDateString()
                  const isSelected = selectedDate?.toDateString() === date.toDateString()

                  return (
                    <motion.div
                      key={index}
                      className={cn(
                        'min-h-[100px] p-2 rounded-xl border-2 transition-all cursor-pointer',
                        'flex flex-col gap-1',
                        isCurrentMonth
                          ? 'bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-700'
                          : 'bg-slate-50 dark:bg-slate-900/50 border-transparent',
                        isToday && 'border-blue-500 dark:border-blue-400',
                        isSelected && 'ring-2 ring-blue-500 ring-offset-2 dark:ring-offset-slate-900',
                        draggedPost && 'hover:border-blue-300 dark:hover:border-blue-600'
                      )}
                      onClick={() => setSelectedDate(date)}
                      onDragOver={(e) => e.preventDefault()}
                      onDrop={(e) => {
                        e.preventDefault()
                        handleDrop(date)
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <span className={cn(
                          'text-sm font-medium',
                          isCurrentMonth
                            ? 'text-slate-700 dark:text-slate-300'
                            : 'text-slate-400 dark:text-slate-600',
                          isToday && 'text-blue-600 dark:text-blue-400'
                        )}>
                          {date.getDate()}
                        </span>
                      </div>

                      <div className="flex-1 space-y-1 overflow-hidden">
                        <AnimatePresence>
                          {dayPosts.slice(0, 3).map((post) => (
                            <motion.div
                              key={post.id}
                              layout
                              initial={{ opacity: 0, scale: 0.9 }}
                              animate={{ opacity: 1, scale: 1 }}
                              exit={{ opacity: 0, scale: 0.9 }}
                              draggable
                              onDragStart={() => setDraggedPost(post)}
                              className={cn(
                                'text-xs p-1.5 rounded-lg cursor-move group relative',
                                'bg-slate-100 dark:bg-slate-700/50',
                                'hover:bg-slate-200 dark:hover:bg-slate-700'
                              )}
                            >
                              <div className="flex items-center gap-1.5">
                                <span>{getPlatformIcon(post.platform)}</span>
                                <span className="truncate flex-1 text-slate-700 dark:text-slate-300">
                                  {post.content?.slice(0, 40) || post.platform}
                                </span>
                              </div>

                              <div className="flex items-center gap-1 mt-1">
                                <Clock className="h-3 w-3 text-slate-400" />
                                <span className="text-slate-400">
                                  {new Date(post.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                              </div>

                              <div className="absolute right-1 top-1 flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button className="p-0.5 hover:bg-white dark:hover:bg-slate-600 rounded">
                                  <Edit3 className="h-3 w-3 text-slate-500" />
                                </button>
                                <button className="p-0.5 hover:bg-white dark:hover:bg-slate-600 rounded">
                                  <Trash2 className="h-3 w-3 text-rose-500" />
                                </button>
                              </div>
                            </motion.div>
                          ))}
                        </AnimatePresence>

                        {dayPosts.length > 3 && (
                          <div className="text-xs text-slate-500 dark:text-slate-400 text-center py-1">
                            +{dayPosts.length - 3} more
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>

              {/* Stats bar */}
              {Object.keys(stats).length > 0 && (
                <div className="flex items-center gap-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {stats.total || 0} posts this month
                  </span>
                  <span className="text-xs text-blue-600 dark:text-blue-400">{stats.scheduled || 0} scheduled</span>
                  <span className="text-xs text-emerald-600 dark:text-emerald-400">{stats.published || 0} published</span>
                  {stats.failed > 0 && (
                    <span className="text-xs text-rose-600 dark:text-rose-400">{stats.failed} failed</span>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selected Day Detail */}
      {selectedDate && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{formatDate(selectedDate)}</CardTitle>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    {selectedDayPosts.length} scheduled posts
                  </p>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<Plus className="h-4 w-4" />}
                >
                  Add Post
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {selectedDayLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
                </div>
              ) : (
                <div className="space-y-3">
                  {selectedDayPosts.map((post) => {
                    const postMembers = getAssignedMembers(post.assigned_to)

                    return (
                      <Card
                        key={post.id}
                        className="border-l-4 border-l-blue-500"
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg">{getPlatformIcon(post.platform)}</span>
                                <h4 className="font-medium text-slate-900 dark:text-slate-100">
                                  {post.content?.slice(0, 60) || `Post for ${post.platform}`}
                                </h4>
                                <Badge
                                  variant={post.status === 'scheduled' || post.status === 'pending' ? 'primary' : 'default'}
                                  size="sm"
                                >
                                  {post.status}
                                </Badge>
                                {post.recurrence && (
                                  <Badge variant="outline" size="sm">
                                    ↻ {post.recurrence}
                                  </Badge>
                                )}
                              </div>

                              {post.content && post.content.length > 60 && (
                                <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                                  {post.content.slice(60, 160)}
                                </p>
                              )}

                              <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2">
                                  <Clock className="h-4 w-4 text-slate-400" />
                                  <span className="text-sm text-slate-600 dark:text-slate-400">
                                    {new Date(post.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    {' · '}
                                    {post.timezone}
                                  </span>
                                </div>

                                {postMembers.length > 0 && (
                                  <div className="flex items-center gap-2">
                                    <Users className="h-4 w-4 text-slate-400" />
                                    <AvatarGroup
                                      avatars={postMembers.map(m => ({ name: m.name, src: m.avatar_url || undefined }))}
                                      size="xs"
                                      max={3}
                                    />
                                  </div>
                                )}

                                {post.author_name && (
                                  <span className="text-xs text-slate-500">by {post.author_name}</span>
                                )}
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              <Tooltip content="Edit" position="top">
                                <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
                                  <Edit3 className="h-4 w-4 text-slate-500" />
                                </button>
                              </Tooltip>

                              <Tooltip content="Delete" position="top">
                                <button className="p-2 hover:bg-rose-100 dark:hover:bg-rose-900/30 rounded-lg transition-colors">
                                  <Trash2 className="h-4 w-4 text-rose-500" />
                                </button>
                              </Tooltip>
                            </div>
                          </div>

                          {post.error_message && (
                            <div className="mt-3 p-3 bg-rose-50 dark:bg-rose-900/20 rounded-lg flex items-center gap-2">
                              <AlertTriangle className="h-4 w-4 text-rose-600 dark:text-rose-400 flex-shrink-0" />
                              <span className="text-sm text-rose-700 dark:text-rose-300">
                                {post.error_message}
                              </span>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )
                  })}

                  {selectedDayPosts.length === 0 && (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CalendarIcon className="h-8 w-8 text-slate-400" />
                      </div>
                      <p className="text-slate-500 dark:text-slate-400">
                        No posts scheduled for this day
                      </p>
                      <Button
                        variant="outline"
                        className="mt-4"
                        leftIcon={<Plus className="h-4 w-4" />}
                      >
                        Schedule a Post
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Conflict Modal */}
      <AnimatePresence>
        {showConflictModal && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
              onClick={() => setShowConflictModal(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-0 m-auto w-full max-w-lg h-fit max-h-[80vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              <div className="p-6 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                      Scheduling Conflict
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      This time slot has existing posts
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setShowConflictModal(false)}
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="h-5 w-5 text-slate-500" />
                </button>
              </div>

              <div className="p-6 overflow-y-auto">
                <p className="text-slate-600 dark:text-slate-400 mb-4">
                  The following posts are scheduled at the same time:
                </p>

                <div className="space-y-3">
                  {conflicts.map((conflict) => (
                    <Card key={conflict.post_id} variant="outline">
                      <CardContent className="p-3">
                        <div className="flex items-center gap-3">
                          <span className="text-lg">{getPlatformIcon(conflict.platform)}</span>
                          <div className="flex-1">
                            <p className="font-medium text-slate-900 dark:text-slate-100">
                              {conflict.title || `Post on ${conflict.platform}`}
                            </p>
                            <p className="text-sm text-slate-500">
                              {new Date(conflict.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                          <Badge variant="warning" size="sm">
                            Conflict
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <div className="p-6 border-t border-slate-200 dark:border-slate-700 flex gap-3">
                <Button
                  variant="primary"
                  className="flex-1"
                  leftIcon={<CheckCircle2 className="h-4 w-4" />}
                  onClick={() => setShowConflictModal(false)}
                >
                  Keep Both
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowConflictModal(false)}
                >
                  Reschedule
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}