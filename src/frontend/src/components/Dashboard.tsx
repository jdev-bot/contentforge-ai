'use client'

import { useState, useEffect, useMemo, Suspense, lazy } from 'react'
import { useRouter } from 'next/navigation'
import { AuthUser } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Avatar } from '@/components/ui/Avatar'
import { Tooltip } from '@/components/ui/Tooltip'
import { FileText, Share2, BarChart3, Settings, Folder, Menu, X, Users, Plus, Sparkles, Search, Trash2, Calendar, Rss, Leaf, TrendingUp, Bell, Users2, Target, Zap, Award, Activity } from 'lucide-react'
import { ErrorBoundary } from './ErrorBoundary'
import UsageCounter from './UsageCounter'
import UpgradeModal from './UpgradeModal'
import OfflineBanner from './OfflineBanner'
import Footer from './Footer'
import SearchModal from './SearchModal'
import { TrendingTopicsWidget } from './TrendingTopics'
import { AlertsBell } from './AlertsCenter'
import { cn } from '@/lib/utils'

// Dynamic imports for code splitting
const ContentTab = lazy(() => import('./ContentTab'))
const ProjectsTab = lazy(() => import('./ProjectsTab'))
const DistributionsTab = lazy(() => import('./DistributionsTab'))
const AnalyticsTab = lazy(() => import('./AnalyticsTab'))
const SettingsTab = lazy(() => import('./SettingsTab'))
const TeamTab = lazy(() => import('./TeamTab'))
const TrashTab = lazy(() => import('./TrashTab'))
const ScheduleTab = lazy(() => import('./ScheduleTab'))
const RSSTab = lazy(() => import('./RSSTab'))
const FreshnessDashboard = lazy(() => import('./FreshnessDashboard'))
const TrendingTopics = lazy(() => import('./TrendingTopics'))
const AlertsCenter = lazy(() => import('./AlertsCenter'))
const TeamCalendar = lazy(() => import('./TeamCalendar'))
const CompetitorAnalysis = lazy(() => import('./CompetitorAnalysis'))
const IntegrationsPanel = lazy(() => import('./IntegrationsPanel'))
const QualityDashboard = lazy(() => import('./QualityDashboard'))
const SentimentDashboard = lazy(() => import('./SentimentDashboard'))

interface DashboardProps {
  user: AuthUser
}

export default function Dashboard({ user }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('content')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [showSearchModal, setShowSearchModal] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const router = useRouter()

  // Handle scroll for glass effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Memoize tabs array to prevent unnecessary re-renders
  const tabs = useMemo(() => [
    { id: 'content', name: 'Content', icon: FileText, badge: null },
    { id: 'projects', name: 'Projects', icon: Folder, badge: null },
    { id: 'schedule', name: 'Schedule', icon: Calendar, badge: null },
    { id: 'team-calendar', name: 'Team Calendar', icon: Users2, badge: 'New' },
    { id: 'rss', name: 'RSS Feeds', icon: Rss, badge: null },
    { id: 'freshness', name: 'Freshness', icon: Leaf, badge: null },
    { id: 'trends', name: 'Trends', icon: TrendingUp, badge: null },
    { id: 'distributions', name: 'Distributions', icon: Share2, badge: null },
    { id: 'analytics', name: 'Analytics', icon: BarChart3, badge: null },
    { id: 'competitors', name: 'Competitors', icon: Target, badge: 'New' },
    { id: 'team', name: 'Team', icon: Users, badge: null },
    { id: 'alerts', name: 'Alerts', icon: Bell, badge: null },
    { id: 'integrations', name: 'Integrations', icon: Zap, badge: 'New' },
    { id: 'quality', name: 'Quality', icon: Award, badge: null },
    { id: 'sentiment', name: 'Sentiment', icon: Activity, badge: null },
    { id: 'settings', name: 'Settings', icon: Settings, badge: null },
    { id: 'trash', name: 'Trash', icon: Trash2, badge: null },
  ], [])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setShowSearchModal(true)
      }
      // Ctrl/Cmd + N for new content
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault()
        router.push('/content/new')
      }
      // Ctrl/Cmd + P for new project
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault()
        router.push('/projects/new')
      }
      // Number keys for tab switching
      if (e.altKey && e.key >= '1' && e.key <= '9') {
        e.preventDefault()
        const tabIndex = parseInt(e.key) - 1
        if (tabs[tabIndex]) {
          setActiveTab(tabs[tabIndex].id)
        }
      }
      // Escape to close mobile menu
      if (e.key === 'Escape') {
        setMobileMenuOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [router, tabs])

  // Wrap tab content with ErrorBoundary and Suspense
  const renderTabContent = () => {
    const fallback = (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-slate-500">Loading...</p>
        </div>
      </div>
    )

    switch (activeTab) {
      case 'content':
        return (
          <ErrorBoundary onReset={() => setActiveTab('content')}>
            <Suspense fallback={fallback}>
              <ContentTab />
            </Suspense>
          </ErrorBoundary>
        )
      case 'projects':
        return (
          <ErrorBoundary onReset={() => setActiveTab('projects')}>
            <Suspense fallback={fallback}>
              <ProjectsTab />
            </Suspense>
          </ErrorBoundary>
        )
      case 'distributions':
        return (
          <ErrorBoundary onReset={() => setActiveTab('distributions')}>
            <Suspense fallback={fallback}>
              <DistributionsTab />
            </Suspense>
          </ErrorBoundary>
        )
      case 'schedule':
        return (
          <ErrorBoundary onReset={() => setActiveTab('schedule')}>
            <Suspense fallback={fallback}>
              <ScheduleTab />
            </Suspense>
          </ErrorBoundary>
        )
      case 'rss':
        return (
          <ErrorBoundary onReset={() => setActiveTab('rss')}>
            <Suspense fallback={fallback}>
              <RSSTab user={user} />
            </Suspense>
          </ErrorBoundary>
        )
      case 'freshness':
        return (
          <ErrorBoundary onReset={() => setActiveTab('freshness')}>
            <Suspense fallback={fallback}>
              <FreshnessDashboard />
            </Suspense>
          </ErrorBoundary>
        )
      case 'trends':
        return (
          <ErrorBoundary onReset={() => setActiveTab('trends')}>
            <Suspense fallback={fallback}>
              <TrendingTopics />
            </Suspense>
          </ErrorBoundary>
        )
      case 'analytics':
        return (
          <ErrorBoundary onReset={() => setActiveTab('analytics')}>
            <Suspense fallback={fallback}>
              <AnalyticsTab />
            </Suspense>
          </ErrorBoundary>
        )
      case 'competitors':
        return (
          <ErrorBoundary onReset={() => setActiveTab('competitors')}>
            <Suspense fallback={fallback}>
              <CompetitorAnalysis />
            </Suspense>
          </ErrorBoundary>
        )
      case 'team':
        return (
          <ErrorBoundary onReset={() => setActiveTab('team')}>
            <Suspense fallback={fallback}>
              <TeamTab user={user} />
            </Suspense>
          </ErrorBoundary>
        )
      case 'team-calendar':
        return (
          <ErrorBoundary onReset={() => setActiveTab('team-calendar')}>
            <Suspense fallback={fallback}>
              <TeamCalendar />
            </Suspense>
          </ErrorBoundary>
        )
      case 'alerts':
        return (
          <ErrorBoundary onReset={() => setActiveTab('alerts')}>
            <Suspense fallback={fallback}>
              <AlertsCenter />
            </Suspense>
          </ErrorBoundary>
        )
      case 'integrations':
        return (
          <ErrorBoundary onReset={() => setActiveTab('integrations')}>
            <Suspense fallback={fallback}>
              <IntegrationsPanel />
            </Suspense>
          </ErrorBoundary>
        )
      case 'quality':
        return (
          <ErrorBoundary onReset={() => setActiveTab('quality')}>
            <Suspense fallback={fallback}>
              <QualityDashboard />
            </Suspense>
          </ErrorBoundary>
        )
      case 'sentiment':
        return (
          <ErrorBoundary onReset={() => setActiveTab('sentiment')}>
            <Suspense fallback={fallback}>
              <SentimentDashboard />
            </Suspense>
          </ErrorBoundary>
        )
      case 'settings':
        return (
          <ErrorBoundary onReset={() => setActiveTab('settings')}>
            <Suspense fallback={fallback}>
              <SettingsTab user={user} />
            </Suspense>
          </ErrorBoundary>
        )
      case 'trash':
        return (
          <ErrorBoundary onReset={() => setActiveTab('trash')}>
            <Suspense fallback={fallback}>
              <TrashTab onItemRestored={() => setActiveTab('content')} />
            </Suspense>
          </ErrorBoundary>
        )
      default:
        return (
          <ErrorBoundary onReset={() => setActiveTab('content')}>
            <Suspense fallback={fallback}>
              <ContentTab />
            </Suspense>
          </ErrorBoundary>
        )
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Offline Banner */}
      <OfflineBanner />

      {/* Header */}
      <header className={cn(
        'sticky top-0 z-50 transition-all duration-300',
        isScrolled 
          ? 'bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl shadow-sm border-b border-slate-200/50 dark:border-slate-700/50'
          : 'bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700'
      )}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Mobile Menu Button */}
            <div className="flex items-center gap-4">
              {/* Mobile Menu Button */}
              <button
                className="md:hidden p-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-all"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
                aria-expanded={mobileMenuOpen}
              >
                {mobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
              
              <div className="flex-shrink-0 flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
                  ContentForge
                </span>
              </div>
            </div>
            
            {/* Desktop Navigation - Right Side */}
            <div className="hidden md:flex items-center gap-4">
              <Tooltip content="Search (Ctrl+K)" position="bottom">
                <Button
                  variant="ghost"
                  size="sm"
                  leftIcon={<Search className="h-4 w-4" />}
                  onClick={() => setShowSearchModal(true)}
                >
                  Search
                </Button>
              </Tooltip>
              
              <Tooltip content="Create new content (Ctrl+N)" position="bottom">
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Plus className="h-4 w-4" />}
                  onClick={() => router.push('/content/new')}
                >
                  New Content
                </Button>
              </Tooltip>
              
              <div className="h-8 w-px bg-slate-200 dark:bg-slate-700" />
              
              <AlertsBell onClick={() => setActiveTab('alerts')} />
              
              <Tooltip content="View profile" position="bottom">
                <button
                  onClick={() => setActiveTab('settings')}
                  className="flex items-center gap-3 p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <Avatar
                    name={user.email?.split('@')[0] || 'User'}
                    size="sm"
                    status="online"
                  />
                  <div className="text-left hidden lg:block">
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                      {user.email?.split('@')[0] || 'User'}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {user.email}
                    </p>
                  </div>
                </button>
              </Tooltip>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar - Desktop */}
          <aside className="hidden md:block w-64 flex-shrink-0">
            <nav className="sticky top-24 space-y-1">
              {tabs.map((tab, index) => {
                const Icon = tab.icon
                const isActive = activeTab === tab.id
                
                return (
                  <Tooltip key={tab.id} content={`Alt+${index + 1}`} position="right" delay={1000}>
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={cn(
                        'w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200',
                        'group relative overflow-hidden',
                        isActive
                          ? 'bg-gradient-to-r from-blue-500 to-violet-600 text-white shadow-lg shadow-blue-500/25'
                          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100'
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={cn(
                          'h-5 w-5 transition-colors',
                          isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300'
                        )} />
                        <span>{tab.name}</span>
                      </div>
                      
                      {tab.badge && (
                        <Badge 
                          variant={isActive ? 'default' : 'primary'} 
                          size="sm"
                          className={cn(
                            'ml-2',
                            isActive && 'bg-white/20 text-white border-white/30'
                          )}
                        >
                          {tab.badge}
                        </Badge>
                      )}
                      
                      {/* Active indicator */}
                      {isActive && (
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-violet-600/20 animate-pulse" />
                      )}
                    </button>
                  </Tooltip>
                )
              })}
            </nav>
            
            {/* Glass Card - Usage Stats */}
            <div className="mt-6 p-4 rounded-2xl bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl border border-slate-200/50 dark:border-slate-700/50 shadow-lg">
              <UsageCounter onUpgrade={() => setShowUpgradeModal(true)} />
            </div>
            
            {/* Trending Topics Widget */}
            <div className="mt-6 p-4 rounded-2xl bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl border border-slate-200/50 dark:border-slate-700/50 shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  Trending Now
                </h3>
                <button
                  onClick={() => setActiveTab('trends')}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                >
                  View all
                </button>
              </div>
              <TrendingTopicsWidget />
            </div>
            
            {/* Keyboard Shortcuts Info */}
            <div className="mt-6 p-4 rounded-2xl bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">
                Keyboard Shortcuts
              </p>
              <div className="space-y-2 text-xs text-slate-500 dark:text-slate-400">
                <div className="flex justify-between items-center">
                  <span>New Content</span>
                  <kbd className="px-2 py-1 bg-white dark:bg-slate-700 rounded-md border border-slate-300 dark:border-slate-600 font-mono">
                    Ctrl+N
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span>New Project</span>
                  <kbd className="px-2 py-1 bg-white dark:bg-slate-700 rounded-md border border-slate-300 dark:border-slate-600 font-mono">
                    Ctrl+P
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span>Search</span>
                  <kbd className="px-2 py-1 bg-white dark:bg-slate-700 rounded-md border border-slate-300 dark:border-slate-600 font-mono">
                    Ctrl+K
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span>Switch Tab</span>
                  <kbd className="px-2 py-1 bg-white dark:bg-slate-700 rounded-md border border-slate-300 dark:border-slate-600 font-mono">
                    Alt+1-8
                  </kbd>
                </div>
              </div>
            </div>
          </aside>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <>
              {/* Backdrop */}
              <div 
                className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 md:hidden"
                onClick={() => setMobileMenuOpen(false)}
                aria-hidden="true"
              />
              
              {/* Mobile Sidebar */}
              <aside className="fixed inset-y-0 left-0 w-72 bg-white dark:bg-slate-900 z-50 md:hidden shadow-2xl">
                <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
                      ContentForge
                    </span>
                  </div>
                  <button
                    onClick={() => setMobileMenuOpen(false)}
                    className="p-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-all"
                    aria-label="Close menu"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                
                {/* User Info in Mobile Menu */}
                <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                  <div className="flex items-center gap-3">
                    <Avatar
                      name={user.email?.split('@')[0] || 'User'}
                      size="md"
                      status="online"
                    />
                    <div>
                      <p className="font-medium text-slate-900 dark:text-slate-100">
                        {user.email?.split('@')[0] || 'User'}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </div>
                
                <nav className="p-4 space-y-1">
                  {tabs.map((tab) => {
                    const Icon = tab.icon
                    const isActive = activeTab === tab.id
                    
                    return (
                      <button
                        key={tab.id}
                        onClick={() => {
                          setActiveTab(tab.id)
                          setMobileMenuOpen(false)
                        }}
                        className={cn(
                          'w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200',
                          isActive
                            ? 'bg-gradient-to-r from-blue-500 to-violet-600 text-white shadow-lg shadow-blue-500/25'
                            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                        )}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className={cn(
                            'h-5 w-5',
                            isActive ? 'text-white' : 'text-slate-400'
                          )} />
                          <span>{tab.name}</span>
                        </div>
                        
                        {tab.badge && (
                          <Badge 
                            variant={isActive ? 'default' : 'primary'} 
                            size="sm"
                            className={cn(
                              isActive && 'bg-white/20 text-white border-white/30'
                            )}
                          >
                            {tab.badge}
                          </Badge>
                        )}
                      </button>
                    )
                  })}
                </nav>
                
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="mb-4">
                    <UsageCounter onUpgrade={() => {
                      setShowUpgradeModal(true)
                      setMobileMenuOpen(false)
                    }} />
                  </div>
                  
                  <Button variant="outline" className="w-full">
                    Sign Out
                  </Button>
                </div>
              </aside>
            </>
          )}

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            {/* Tab Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {tabs.find(t => t.id === activeTab)?.name}
                  </h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    Manage your {activeTab.toLowerCase()} and settings
                  </p>
                </div>
                
                {/* Contextual Actions */}
                {activeTab === 'content' && (
                  <Button
                    variant="primary"
                    size="sm"
                    leftIcon={<Plus className="h-4 w-4" />}
                    onClick={() => router.push('/content/new')}
                  >
                    New Content
                  </Button>
                )}
                {activeTab === 'projects' && (
                  <Button
                    variant="primary"
                    size="sm"
                    leftIcon={<Plus className="h-4 w-4" />}
                    onClick={() => router.push('/projects/new')}
                  >
                    New Project
                  </Button>
                )}
                {activeTab === 'schedule' && (
                  <Button
                    variant="primary"
                    size="sm"
                    leftIcon={<Plus className="h-4 w-4" />}
                    onClick={() => {
                      // Trigger new schedule via the ScheduleTab component
                      window.dispatchEvent(new CustomEvent('triggerNewSchedule'))
                    }}
                  >
                    New Schedule
                  </Button>
                )}
              </div>
            </div>
            
            {/* Tab Content */}
            <div className="animate-fadeIn">
              {renderTabContent()}
            </div>
          </main>
        </div>
      </div>

      {/* Footer */}
      <Footer />

      {/* Search Modal */}
      <SearchModal
        isOpen={showSearchModal}
        onClose={() => setShowSearchModal(false)}
      />

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        currentTier="free"
      />
    </div>
  )
}
