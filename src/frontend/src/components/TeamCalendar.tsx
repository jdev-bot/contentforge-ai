'use client'

import { useState, useMemo, useCallback } from 'react'
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
  MoreVertical,
  Edit3,
  Trash2,
  CheckCircle2,
  X,
  GripVertical,
  Calendar
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Avatar, AvatarGroup } from '@/components/ui/Avatar'
import { Tooltip } from '@/components/ui/Tooltip'
import { Input, Select } from '@/components/ui/Input'
import { cn } from '@/lib/utils'

// Types
export interface TeamMember {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'editor' | 'viewer'
  color: string
}

export interface ScheduledPost {
  id: string
  title: string
  content: string
  platform: 'linkedin' | 'twitter' | 'facebook' | 'instagram' | 'blog'
  scheduledDate: Date
  status: 'draft' | 'scheduled' | 'published' | 'failed'
  assignedTo: string[] // team member IDs
  timezone: string
  recurrence?: 'none' | 'daily' | 'weekly' | 'monthly'
  conflicts?: string[] // IDs of conflicting posts
}

// Mock data
const mockTeamMembers: TeamMember[] = [
  { id: '1', name: 'Sarah Johnson', email: 'sarah@company.com', role: 'admin', color: '#3B82F6' },
  { id: '2', name: 'Mike Chen', email: 'mike@company.com', role: 'editor', color: '#10B981' },
  { id: '3', name: 'Emily Davis', email: 'emily@company.com', role: 'editor', color: '#F59E0B' },
  { id: '4', name: 'Alex Wilson', email: 'alex@company.com', role: 'viewer', color: '#8B5CF6' },
]

const mockScheduledPosts: ScheduledPost[] = [
  {
    id: '1',
    title: 'Weekly Product Update',
    content: 'Excited to share our latest features...',
    platform: 'linkedin',
    scheduledDate: new Date(new Date().setHours(10, 0, 0, 0)),
    status: 'scheduled',
    assignedTo: ['1', '2'],
    timezone: 'America/New_York',
  },
  {
    id: '2',
    title: 'Industry Trends Thread',
    content: '5 trends shaping our industry in 2025...',
    platform: 'twitter',
    scheduledDate: new Date(new Date().setHours(14, 30, 0, 0)),
    status: 'scheduled',
    assignedTo: ['2'],
    timezone: 'America/Los_Angeles',
    conflicts: ['3'],
  },
  {
    id: '3',
    title: 'Customer Success Story',
    content: 'How Company X achieved 200% growth...',
    platform: 'linkedin',
    scheduledDate: new Date(new Date().setHours(14, 0, 0, 0)),
    status: 'draft',
    assignedTo: ['3'],
    timezone: 'America/New_York',
    conflicts: ['2'],
  },
  {
    id: '4',
    title: 'Monday Motivation',
    content: 'Start your week with these productivity tips...',
    platform: 'instagram',
    scheduledDate: new Date(new Date().setDate(new Date().getDate() + 1)),
    status: 'scheduled',
    assignedTo: ['1', '3', '4'],
    timezone: 'America/New_York',
    recurrence: 'weekly',
  },
]

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
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month')
  const [filterMember, setFilterMember] = useState<string | 'all'>('all')
  const [draggedPost, setDraggedPost] = useState<ScheduledPost | null>(null)
  const [posts, setPosts] = useState(mockScheduledPosts)
  const [showConflictModal, setShowConflictModal] = useState(false)
  const [conflicts, setConflicts] = useState<ScheduledPost[]>([])

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  const daysInMonth = getDaysInMonth(year, month)
  const firstDayOfMonth = getFirstDayOfMonth(year, month)

  const filteredPosts = useMemo(() => {
    return posts.filter(post => 
      filterMember === 'all' || post.assignedTo.includes(filterMember)
    )
  }, [posts, filterMember])

  const postsForDate = useCallback((date: Date) => {
    return filteredPosts.filter(post => {
      const postDate = new Date(post.scheduledDate)
      return postDate.toDateString() === date.toDateString()
    }).sort((a, b) => a.scheduledDate.getTime() - b.scheduledDate.getTime())
  }, [filteredPosts])

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
  }

  const navigateToday = () => {
    setCurrentDate(new Date())
  }

  const handleDragStart = (post: ScheduledPost) => {
    setDraggedPost(post)
  }

  const handleDrop = (date: Date) => {
    if (!draggedPost) return

    // Check for conflicts
    const dayPosts = postsForDate(date)
    const conflicts = dayPosts.filter(p => p.id !== draggedPost.id)

    const updatedPost = { ...draggedPost, scheduledDate: date }
    
    setPosts(prev => prev.map(p => 
      p.id === draggedPost.id ? updatedPost : p
    ))

    if (conflicts.length > 0) {
      setConflicts(conflicts)
      setShowConflictModal(true)
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
      case 'draft': return 'bg-slate-400'
      case 'failed': return 'bg-rose-500'
      default: return 'bg-slate-400'
    }
  }

  const getAssignedMembers = (ids: string[]) => {
    return mockTeamMembers.filter(m => ids.includes(m.id))
  }

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const days = []
    const prevMonthDays = getDaysInMonth(year, month - 1)
    
    // Previous month padding
    for (let i = firstDayOfMonth - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, prevMonthDays - i),
        isCurrentMonth: false,
      })
    }
    
    // Current month
    for (let i = 1; i <= daysInMonth; i++) {
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
  }, [year, month, daysInMonth, firstDayOfMonth])

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Team Calendar"
        description="Schedule and manage content across your team"
        icon={<Calendar className="w-5 h-5 text-blue-600" />}
        badge={<span className="text-xs bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 px-2 py-0.5 rounded-full">Demo Data</span>}
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
                  {mockTeamMembers.map(member => (
                    <option key={member.id} value={member.id}>
                      {member.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />
              
              <AvatarGroup 
                avatars={mockTeamMembers.slice(0, 4).map(m => ({ 
                  name: m.name, 
                  src: m.avatar 
                }))} 
                size="sm" 
                max={4}
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Calendar Grid */}
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
              {calendarDays.map(({ date, isCurrentMonth }, index) => {
                const dayPosts = postsForDate(date)
                const isToday = date.toDateString() === new Date().toDateString()
                const isSelected = selectedDate?.toDateString() === date.toDateString()
                const hasConflicts = dayPosts.some(p => (p.conflicts?.length ?? 0) > 0)
                
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
                    onDragOver={(e) => {
                      e.preventDefault()
                    }}
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
                      
                      {hasConflicts && (
                        <Tooltip content="Scheduling conflicts detected" position="top">
                          <AlertTriangle className="h-4 w-4 text-amber-500" />
                        </Tooltip>
                      )}
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
                            onDragStart={() => handleDragStart(post)}
                            className={cn(
                              'text-xs p-1.5 rounded-lg cursor-move group relative',
                              'bg-slate-100 dark:bg-slate-700/50',
                              'hover:bg-slate-200 dark:hover:bg-slate-700',
                              post.conflicts?.length && 'border border-amber-500/50'
                            )}
                          >
                            <div className="flex items-center gap-1.5">
                              <span>{getPlatformIcon(post.platform)}</span>
                              <span className="truncate flex-1 text-slate-700 dark:text-slate-300">
                                {post.title}
                              </span>
                            </div>
                            
                            <div className="flex items-center gap-1 mt-1">
                              <Clock className="h-3 w-3 text-slate-400" />
                              <span className="text-slate-400">
                                {post.scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
          </div>
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
                    {postsForDate(selectedDate).length} scheduled posts
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
              <div className="space-y-3">
                {postsForDate(selectedDate).map((post) => {
                  const members = getAssignedMembers(post.assignedTo)
                  const hasConflict = post.conflicts && post.conflicts.length > 0
                  
                  return (
                    <Card 
                      key={post.id} 
                      className={cn(
                        'border-l-4',
                        hasConflict ? 'border-l-amber-500' : 'border-l-blue-500'
                      )}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-lg">{getPlatformIcon(post.platform)}</span>
                              <h4 className="font-medium text-slate-900 dark:text-slate-100">
                                {post.title}
                              </h4>
                              <Badge 
                                variant={post.status === 'scheduled' ? 'primary' : 'default'} 
                                size="sm"
                              >
                                {post.status}
                              </Badge>
                              {post.recurrence && post.recurrence !== 'none' && (
                                <Badge variant="outline" size="sm">
                                  ↻ {post.recurrence}
                                </Badge>
                              )}
                            </div>
                            
                            <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                              {post.content}
                            </p>
                            
                            <div className="flex items-center gap-4">
                              <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4 text-slate-400" />
                                <span className="text-sm text-slate-600 dark:text-slate-400">
                                  {post.scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                  {' · '}
                                  {post.timezone}
                                </span>
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <Users className="h-4 w-4 text-slate-400" />
                                <AvatarGroup 
                                  avatars={members.map(m => ({ name: m.name, src: m.avatar }))}
                                  size="xs"
                                  max={3}
                                />
                              </div>
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
                        
                        {hasConflict && (
                          <div className="mt-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 flex-shrink-0" />
                            <span className="text-sm text-amber-700 dark:text-amber-300">
                              Scheduling conflict with another post at the same time
                            </span>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )
                })}
                
                {postsForDate(selectedDate).length === 0 && (
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
                  {conflicts.map((post) => (
                    <Card key={post.id} variant="outline">
                      <CardContent className="p-3">
                        <div className="flex items-center gap-3">
                          <span className="text-lg">{getPlatformIcon(post.platform)}</span>
                          <div className="flex-1">
                            <p className="font-medium text-slate-900 dark:text-slate-100">
                              {post.title}
                            </p>
                            <p className="text-sm text-slate-500">
                              {post.scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
