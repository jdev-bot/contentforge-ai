'use client'

import { useState, useCallback } from 'react'
import ScheduleCalendar from './ScheduleCalendar'
import UpcomingPostsWidget from './UpcomingPostsWidget'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/hooks/useToast'
import { ScheduledPost } from '@/lib/api'
import ScheduleModal from './ScheduleModal'
import { 
  Calendar, 
  Plus, 
  Clock,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  BarChart3
} from 'lucide-react'

export default function ScheduleTab() {
  const { showToast } = useToast()
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduledPost | null>(null)

  const handleEditSchedule = useCallback((schedule: ScheduledPost) => {
    setSelectedSchedule(schedule)
    setShowScheduleModal(true)
  }, [])

  const handleNewSchedule = useCallback(() => {
    setSelectedSchedule(null)
    setShowScheduleModal(true)
  }, [])

  const handleScheduleSuccess = useCallback(() => {
    setShowScheduleModal(false)
    showToast('Schedule updated successfully', 'success')
  }, [showToast])

  // Stats for the header
  const stats = [
    { 
      label: 'Scheduled', 
      value: '0', 
      icon: Clock, 
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/30'
    },
    { 
      label: 'Published', 
      value: '0', 
      icon: CheckCircle2, 
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-100 dark:bg-emerald-900/30'
    },
    { 
      label: 'Success Rate', 
      value: '0%', 
      icon: TrendingUp, 
      color: 'text-violet-600 dark:text-violet-400',
      bg: 'bg-violet-100 dark:bg-violet-900/30'
    },
  ]

  return (
    <div className="space-y-6">
      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {stats.map(stat => (
          <Card key={stat.label} className="border border-slate-200 dark:border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", stat.bg)}>
                  <stat.icon className={cn("h-5 w-5", stat.color)} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {stat.value}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {stat.label}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Calendar */}
        <div className="lg:col-span-3">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-violet-600" />
                    Publishing Calendar
                  </h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    Manage and schedule your content publishing
                  </p>
                </div>
                
                <Button
                  variant="primary"
                  onClick={handleNewSchedule}
                  leftIcon={<Plus className="h-4 w-4" />}
                >
                  New Schedule
                </Button>
              </div>
            </div>
            
            <ScheduleCalendar 
              onEditSchedule={handleEditSchedule}
            />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <UpcomingPostsWidget 
            onViewAll={() => {}}
            onEditPost={handleEditSchedule}
          />
          
          {/* Quick Tips */}
          <Card className="border border-slate-200 dark:border-slate-700">
            <CardContent className="p-4">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-3">
                <AlertCircle className="h-4 w-4 text-amber-500" />
                Best Practices
              </h3>
              
              <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                <li className="flex items-start gap-2">
                  <span className="text-violet-500 mt-0.5">•</span>
                  Schedule posts 1-2 weeks ahead for optimal planning
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-violet-500 mt-0.5">•</span>
                  Use recurring schedules for consistent content
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-violet-500 mt-0.5">•</span>
                  Post during peak engagement hours (9 AM - 3 PM)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-violet-500 mt-0.5">•</span>
                  Spread posts across different timezones for global reach
                </li>
              </ul>
            </CardContent>
          </Card>
          
          {/* Templates Card */}
          <Card className="border border-slate-200 dark:border-slate-700">
            <CardContent className="p-4">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-3">
                <BarChart3 className="h-4 w-4 text-violet-500" />
                Schedule Templates
              </h3>
              
              <div className="space-y-2">
                {[
                  { name: 'Morning Blast', time: '9:00 AM', desc: 'Best for B2B' },
                  { name: 'Lunch Hour', time: '12:00 PM', desc: 'High engagement' },
                  { name: 'Evening Wind', time: '6:00 PM', desc: 'After work' },
                ].map(template => (
                  <button
                    key={template.name}
                    className="w-full text-left p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        {template.name}
                      </span>
                      <span className="text-xs text-violet-600">{template.time}</span>
                    </div>
                    <p className="text-xs text-slate-500">{template.desc}</p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <ScheduleModal
        isOpen={showScheduleModal}
        onClose={() => {
          setShowScheduleModal(false)
          setSelectedSchedule(null)
        }}
        existingSchedule={selectedSchedule || undefined}
        mode={selectedSchedule ? 'edit' : 'create'}
        onSuccess={handleScheduleSuccess}
      />
    </div>
  )
}

// Helper function
function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ')
}
