'use client'

import { useState, useEffect, useMemo, Suspense, lazy } from 'react'
import { useRouter } from 'next/navigation'
import { AuthUser } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Avatar } from '@/components/ui/Avatar'
import { Tooltip } from '@/components/ui/Tooltip'
import { FileText, Share2, BarChart3, Settings, Folder, Menu, X, Users, Plus, Sparkles, Search, Trash2, Calendar, Rss, Leaf, TrendingUp, Bell, Users2, Target, Zap, Award, Activity, Lightbulb, Tag, Shield, MessageSquare, GitBranch, ScrollText, LayoutDashboard, Puzzle, Store, Filter, PieChart, Heart, Network, ChevronDown, ChevronRight, Pin, Home, MoreHorizontal } from 'lucide-react'
import { ErrorBoundary } from './ErrorBoundary'
import UsageCounter from './UsageCounter'
import UpgradeModal from './UpgradeModal'
import OfflineBanner from './OfflineBanner'
import Footer from './Footer'
import SearchModal from './SearchModal'
import { TrendingTopicsWidget } from './TrendingTopics'
import { AlertsBell } from './AlertsCenter'
import { cn, trackTabUsage, getPinnedTabs, savePinnedTabs, getMostUsedTabs } from '@/lib/utils'

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
const SuggestionPanel = lazy(() => import('./SuggestionPanel'))
const CategorizationPanel = lazy(() => import('./CategorizationPanel'))
const PerformanceAnalytics = lazy(() => import('./PerformanceAnalytics'))
const DataRetentionManager = lazy(() => import('./DataRetentionManager'))
const CommentsPanel = lazy(() => import('./CommentsPanel'))
const VersionHistory = lazy(() => import('./VersionHistory'))
const AuditLogs = lazy(() => import('./AuditLogs'))
const CustomDashboards = lazy(() => import('./CustomDashboards'))
const PluginManager = lazy(() => import('./PluginManager'))
const TemplateMarketplace = lazy(() => import('./TemplateMarketplace'))
const FunnelAnalytics = lazy(() => import('./FunnelAnalytics'))
const AttributionDashboard = lazy(() => import('./AttributionDashboard'))
const SLAMonitoring = lazy(() => import('./SLAMonitoring'))
const IntegrationHub = lazy(() => import('./IntegrationHub'))
const HomeTab = lazy(() => import('./HomeTab'))

interface DashboardProps {
  user: AuthUser
}

export default function Dashboard({ user }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('home')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [showSearchModal, setShowSearchModal] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>({
    insights: false,
    system: true,
    extensions: true,
  })
  const [pinnedTabIds, setPinnedTabIds] = useState<string[]>([])
  const [mobileMoreOpen, setMobileMoreOpen] = useState(false)
  const router = useRouter()

  // Initialize pinned tabs from localStorage
  useEffect(() => {
    const stored = getPinnedTabs()
    if (stored.length > 0) {
      setPinnedTabIds(stored)
    } else {
      // Auto-populate from most-used tabs
      const mostUsed = getMostUsedTabs(5)
      const defaults = mostUsed.length > 0 ? mostUsed : ['content', 'analytics', 'schedule']
      setPinnedTabIds(defaults)
      savePinnedTabs(defaults)
    }
  }, [])

  // Handle scroll for glass effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Memoize section groups for organized sidebar navigation
  const sidebarSections = useMemo(() => [
    {
      id: 'content',
      label: 'Content',
      tabs: [
        { id: 'content', name: 'Content', icon: FileText, badge: null },
        { id: 'projects', name: 'Projects', icon: Folder, badge: null },
        { id: 'schedule', name: 'Schedule', icon: Calendar, badge: null },
        { id: 'rss', name: 'RSS Feeds', icon: Rss, badge: null },
        { id: 'freshness', name: 'Freshness', icon: Leaf, badge: null },
      ]
    },
    {
      id: 'analytics',
      label: 'Analytics',
      tabs: [
        { id: 'analytics', name: 'Analytics', icon: BarChart3, badge: null },
        { id: 'trends', name: 'Trends', icon: TrendingUp, badge: null },
        { id: 'distributions', name: 'Distributions', icon: Share2, badge: null },
        { id: 'performance', name: 'Performance', icon: BarChart3, badge: null },
        { id: 'funnels', name: 'Funnels', icon: Filter, badge: 'New' },
        { id: 'attribution', name: 'Attribution', icon: PieChart, badge: 'New' },
        { id: 'competitors', name: 'Competitors', icon: Target, badge: 'New' },
      ]
    },
    {
      id: 'insights',
      label: 'Insights',
      tabs: [
        { id: 'quality', name: 'Quality', icon: Award, badge: null },
        { id: 'sentiment', name: 'Sentiment', icon: Activity, badge: null },
        { id: 'categorization', name: 'Categories', icon: Tag, badge: 'New' },
        { id: 'suggestions', name: 'Suggestions', icon: Lightbulb, badge: 'New' },
      ]
    },
    {
      id: 'team',
      label: 'Team',
      tabs: [
        { id: 'team', name: 'Team', icon: Users, badge: null },
        { id: 'team-calendar', name: 'Team Calendar', icon: Users2, badge: 'New' },
        { id: 'comments', name: 'Comments', icon: MessageSquare, badge: null },
        { id: 'version-history', name: 'History', icon: GitBranch, badge: 'New' },
      ]
    },
    {
      id: 'system',
      label: 'System',
      tabs: [
        { id: 'alerts', name: 'Alerts', icon: Bell, badge: null },
        { id: 'audit-logs', name: 'Audit', icon: ScrollText, badge: 'New' },
        { id: 'custom-dashboards', name: 'Dashboards', icon: LayoutDashboard, badge: 'New' },
        { id: 'sla', name: 'SLA', icon: Heart, badge: 'New' },
        { id: 'retention', name: 'Retention', icon: Shield, badge: null },
      ]
    },
    {
      id: 'extensions',
      label: 'Extensions',
      tabs: [
        { id: 'integrations', name: 'Integrations', icon: Zap, badge: 'New' },
        { id: 'integration-hub', name: 'Integrations Hub', icon: Network, badge: 'New' },
        { id: 'plugins', name: 'Plugins', icon: Puzzle, badge: 'New' },
        { id: 'marketplace', name: 'Marketplace', icon: Store, badge: 'New' },
      ]
    },
    {
      id: 'account',
      label: null,
      tabs: [
        { id: 'settings', name: 'Settings', icon: Settings, badge: null },
        { id: 'trash', name: 'Trash', icon: Trash2, badge: null },
      ]
    },
  ], [])

  // Flat tabs array for keyboard shortcuts (backward compat)
  const tabs = useMemo(() => sidebarSections.flatMap(s => s.tabs), [sidebarSections])

  // Pinned tabs (resolved to full tab objects)
  const pinnedTabs = useMemo(() => {
    return pinnedTabIds
      .map(id => tabs.find(t => t.id === id))
      .filter((t): t is NonNullable<typeof t> => t != null)
  }, [pinnedTabIds, tabs])

  // Toggle pin on a tab
  const togglePin = (tabId: string) => {
    setPinnedTabIds(prev => {
      const next = prev.includes(tabId)
        ? prev.filter(id => id !== tabId)
        : [...prev, tabId].slice(0, 7) // Max 7 pinned tabs
      savePinnedTabs(next)
      return next
    })
  }

  // Enhanced setActiveTab that tracks usage
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId)
    trackTabUsage(tabId)
    setMobileMenuOpen(false)
    setMobileMoreOpen(false)
  }

  // Toggle section collapse
  const toggleSection = (sectionId: string) => {
    setCollapsedSections(prev => ({ ...prev, [sectionId]: !prev[sectionId] }))
  }

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
      // Number keys for tab switching (1-9)
      if (e.altKey && e.key >= '1' && e.key <= '9') {
        e.preventDefault()
        const tabIndex = parseInt(e.key) - 1
        if (tabs[tabIndex]) {
          handleTabChange(tabs[tabIndex].id)
        }
      }
      // Alt+0 for home
      if (e.altKey && e.key === '0') {
        e.preventDefault()
        handleTabChange('home')
      }
      // Escape to close mobile menu
      if (e.key === 'Escape') {
        setMobileMenuOpen(false)
        setMobileMoreOpen(false)
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
          <div className="w-12 h-12 border-4 border-blue-200 dark:border-slate-700 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin" />
          <p className="text-slate-500 dark:text-slate-400 text-sm">Loading...</p>
        </div>
      </div>
    )

    switch (activeTab) {
      case 'home':
        return (
          <ErrorBoundary onReset={() => setActiveTab('home')}>
            <Suspense fallback={fallback}>
              <HomeTab onTabChange={handleTabChange} />
            </Suspense>
          </ErrorBoundary>
        )
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
      case 'suggestions':
        return (
          <ErrorBoundary onReset={() => setActiveTab('suggestions')}>
            <Suspense fallback={fallback}>
              <SuggestionPanel />
            </Suspense>
          </ErrorBoundary>
        )
      case 'categorization':
        return (
          <ErrorBoundary onReset={() => setActiveTab('categorization')}>
            <Suspense fallback={fallback}>
              <CategorizationPanel />
            </Suspense>
          </ErrorBoundary>
        )
      case 'performance':
        return (
          <ErrorBoundary onReset={() => setActiveTab('performance')}>
            <Suspense fallback={fallback}>
              <PerformanceAnalytics />
            </Suspense>
          </ErrorBoundary>
        )
      case 'retention':
        return (
          <ErrorBoundary onReset={() => setActiveTab('retention')}>
            <Suspense fallback={fallback}>
              <DataRetentionManager />
            </Suspense>
          </ErrorBoundary>
        )
      case 'comments':
        return (
          <ErrorBoundary onReset={() => setActiveTab('comments')}>
            <Suspense fallback={fallback}>
              <CommentsPanel />
            </Suspense>
          </ErrorBoundary>
        )
      case 'version-history':
        return (
          <ErrorBoundary onReset={() => setActiveTab('version-history')}>
            <Suspense fallback={fallback}>
              <VersionHistory />
            </Suspense>
          </ErrorBoundary>
        )
      case 'audit-logs':
        return (
          <ErrorBoundary onReset={() => setActiveTab('audit-logs')}>
            <Suspense fallback={fallback}>
              <AuditLogs />
            </Suspense>
          </ErrorBoundary>
        )
      case 'custom-dashboards':
        return (
          <ErrorBoundary onReset={() => setActiveTab('custom-dashboards')}>
            <Suspense fallback={fallback}>
              <CustomDashboards />
            </Suspense>
          </ErrorBoundary>
        )
      case 'plugins':
        return (
          <ErrorBoundary onReset={() => setActiveTab('plugins')}>
            <Suspense fallback={fallback}>
              <PluginManager organizationId="default" />
            </Suspense>
          </ErrorBoundary>
        )
      case 'marketplace':
        return (
          <ErrorBoundary onReset={() => setActiveTab('marketplace')}>
            <Suspense fallback={fallback}>
              <TemplateMarketplace isOpen={true} onClose={() => setActiveTab('content')} />
            </Suspense>
          </ErrorBoundary>
        )
      case 'funnels':
        return (
          <ErrorBoundary onReset={() => setActiveTab('funnels')}>
            <Suspense fallback={fallback}>
              <FunnelAnalytics />
            </Suspense>
          </ErrorBoundary>
        )
      case 'attribution':
        return (
          <ErrorBoundary onReset={() => setActiveTab('attribution')}>
            <Suspense fallback={fallback}>
              <AttributionDashboard />
            </Suspense>
          </ErrorBoundary>
        )
      case 'sla':
        return (
          <ErrorBoundary onReset={() => setActiveTab('sla')}>
            <Suspense fallback={fallback}>
              <SLAMonitoring />
            </Suspense>
          </ErrorBoundary>
        )
      case 'integration-hub':
        return (
          <ErrorBoundary onReset={() => setActiveTab('integration-hub')}>
            <Suspense fallback={fallback}>
              <IntegrationHub />
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
          <ErrorBoundary onReset={() => setActiveTab('home')}>
            <Suspense fallback={fallback}>
              <HomeTab onTabChange={handleTabChange} />
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
              
              <AlertsBell onClick={() => handleTabChange('alerts')} />
              
              <Tooltip content="View profile" position="bottom">
                <button
                  onClick={() => handleTabChange('settings')}
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

            {/* Mobile: minimal header actions */}
            <div className="flex md:hidden items-center gap-2">
              <button
                onClick={() => setShowSearchModal(true)}
                className="p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                aria-label="Search"
              >
                <Search className="h-5 w-5" />
              </button>
              <button
                onClick={() => router.push('/content/new')}
                className="p-2 bg-gradient-to-r from-blue-600 to-violet-600 text-white rounded-xl"
                aria-label="New content"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar - Desktop */}
          <aside className="hidden md:block w-56 flex-shrink-0">
            <nav className="sticky top-24 space-y-1 max-h-[calc(100vh-8rem)] overflow-y-auto scrollbar-thin">
              {/* Pinned Section */}
              {pinnedTabs.length > 0 && (
                <div className="mb-2">
                  <div className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                    <Pin className="w-3 h-3" />
                    Pinned
                  </div>
                  {pinnedTabs.map((tab) => {
                    const Icon = tab.icon
                    const isActive = activeTab === tab.id
                    return (
                      <SidebarTab
                        key={tab.id}
                        tab={tab}
                        isActive={isActive}
                        isPinned={true}
                        onTogglePin={() => togglePin(tab.id)}
                        onClick={() => handleTabChange(tab.id)}
                        shortcutIndex={undefined}
                      />
                    )
                  })}
                  <div className="my-2 border-t border-slate-200 dark:border-slate-700/50" />
                </div>
              )}

              {/* Home tab at top */}
              <SidebarTab
                tab={{ id: 'home', name: 'Home', icon: Home, badge: null }}
                isActive={activeTab === 'home'}
                isPinned={false}
                onClick={() => handleTabChange('home')}
                shortcutHint="Alt+0"
              />

              {/* Sections */}
              {sidebarSections.map((section) => {
                const isCollapsed = collapsedSections[section.id] ?? false
                const hasActiveTab = section.tabs.some(t => t.id === activeTab)
                const shouldShow = !isCollapsed || hasActiveTab
                const tabCount = section.tabs.length
                
                return (
                  <div key={section.id}>
                    {/* Section Header (collapsible) */}
                    {section.label ? (
                      <button
                        onClick={() => toggleSection(section.id)}
                        className={cn(
                          'w-full flex items-center justify-between px-3 py-2 text-xs font-semibold uppercase tracking-wider transition-colors rounded-lg',
                          'text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                        )}
                      >
                        <span className="flex items-center gap-1.5">
                          <span>{section.label}</span>
                          <span className="text-slate-300 dark:text-slate-600 font-normal normal-case tracking-normal">
                            {tabCount}
                          </span>
                        </span>
                        {isCollapsed && !hasActiveTab ? (
                          <ChevronRight className="w-3 h-3" />
                        ) : (
                          <ChevronDown className="w-3 h-3" />
                        )}
                      </button>
                    ) : (
                      <div className="mt-3 border-t border-slate-200 dark:border-slate-700/50 pt-1" />
                    )}
                    
                    {/* Section Tabs */}
                    {shouldShow && section.tabs.map((tab) => {
                      const Icon = tab.icon
                      const isActive = activeTab === tab.id
                      const isPinned = pinnedTabIds.includes(tab.id)
                      const tabIndex = tabs.indexOf(tab)
                      
                      return (
                        <SidebarTab
                          key={tab.id}
                          tab={tab}
                          isActive={isActive}
                          isPinned={isPinned}
                          onTogglePin={() => togglePin(tab.id)}
                          onClick={() => handleTabChange(tab.id)}
                          shortcutIndex={tabIndex >= 0 && tabIndex < 9 ? tabIndex + 1 : undefined}
                        />
                      )
                    })}
                  </div>
                )
              })}
            </nav>
            
            {/* Usage Stats (condensed) */}
            <div className="mt-4 p-3 rounded-2xl bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl border border-slate-200/50 dark:border-slate-700/50 shadow-lg">
              <UsageCounter onUpgrade={() => setShowUpgradeModal(true)} />
            </div>
            
            {/* Quick Tip */}
            <div className="mt-4 p-3 rounded-2xl bg-slate-100/80 dark:bg-slate-800/50 border border-slate-200/50 dark:border-slate-700/50">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Press <kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-700 rounded border border-slate-300 dark:border-slate-600 font-mono text-xs">Ctrl+K</kbd> to search · <kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-700 rounded border border-slate-300 dark:border-slate-600 font-mono text-xs">Alt+N</kbd> switch tabs
              </p>
            </div>
          </aside>

          {/* Mobile Menu - Full overlay */}
          {mobileMenuOpen && (
            <>
              <div 
                className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 md:hidden"
                onClick={() => setMobileMenuOpen(false)}
                aria-hidden="true"
              />
              
              <aside className="fixed inset-y-0 left-0 w-72 bg-white dark:bg-slate-900 z-50 md:hidden shadow-2xl overflow-y-auto">
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
                  {/* Home in mobile */}
                  <MobileTabButton
                    tab={{ id: 'home', name: 'Home', icon: Home, badge: null }}
                    isActive={activeTab === 'home'}
                    onClick={() => handleTabChange('home')}
                  />

                  {sidebarSections.map((section) => {
                    const isCollapsed = collapsedSections[section.id] ?? true // Collapsed by default on mobile
                    const hasActiveTab = section.tabs.some(t => t.id === activeTab)
                    const shouldShow = !isCollapsed || hasActiveTab
                    
                    return (
                      <div key={section.id}>
                        {section.label ? (
                          <button
                            onClick={() => toggleSection(section.id)}
                            className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider"
                          >
                            <span>{section.label}</span>
                            {isCollapsed && !hasActiveTab ? (
                              <ChevronRight className="w-3 h-3" />
                            ) : (
                              <ChevronDown className="w-3 h-3" />
                            )}
                          </button>
                        ) : (
                          <div className="mt-2 border-t border-slate-200 dark:border-slate-700/50 pt-2" />
                        )}
                        
                        {shouldShow && section.tabs.map((tab) => (
                          <MobileTabButton
                            key={tab.id}
                            tab={tab}
                            isActive={activeTab === tab.id}
                            onClick={() => handleTabChange(tab.id)}
                          />
                        ))}
                      </div>
                    )
                  })}
                </nav>
                
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
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

          {/* Mobile Bottom Navigation */}
          <div className="fixed bottom-0 left-0 right-0 z-40 md:hidden bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border-t border-slate-200 dark:border-slate-700 safe-area-bottom">
            <div className="flex items-center justify-around h-16 px-2">
              <MobileBottomTab
                icon={<Home className="h-5 w-5" />}
                label="Home"
                isActive={activeTab === 'home'}
                onClick={() => handleTabChange('home')}
              />
              <MobileBottomTab
                icon={<FileText className="h-5 w-5" />}
                label="Content"
                isActive={activeTab === 'content'}
                onClick={() => handleTabChange('content')}
              />
              <MobileBottomTab
                icon={<BarChart3 className="h-5 w-5" />}
                label="Analytics"
                isActive={activeTab === 'analytics'}
                onClick={() => handleTabChange('analytics')}
              />
              <MobileBottomTab
                icon={<Calendar className="h-5 w-5" />}
                label="Schedule"
                isActive={activeTab === 'schedule'}
                onClick={() => handleTabChange('schedule')}
              />
              <MobileBottomTab
                icon={<MoreHorizontal className="h-5 w-5" />}
                label="More"
                isActive={mobileMoreOpen}
                onClick={() => setMobileMoreOpen(!mobileMoreOpen)}
              />
            </div>
          </div>

          {/* Mobile "More" Drawer */}
          {mobileMoreOpen && (
            <>
              <div
                className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden"
                onClick={() => setMobileMoreOpen(false)}
              />
              <div className="fixed bottom-16 left-0 right-0 z-50 md:hidden bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700 rounded-t-2xl shadow-2xl max-h-[60vh] overflow-y-auto">
                <div className="p-4 space-y-1">
                  <p className="px-3 py-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">More tabs</p>
                  {sidebarSections.flatMap(s => s.tabs)
                    .filter(t => !['content', 'analytics', 'schedule'].includes(t.id))
                    .map((tab) => (
                      <MobileTabButton
                        key={tab.id}
                        tab={tab}
                        isActive={activeTab === tab.id}
                        onClick={() => handleTabChange(tab.id)}
                      />
                    ))}
                  <MobileTabButton
                    tab={{ id: 'settings', name: 'Settings', icon: Settings, badge: null }}
                    isActive={activeTab === 'settings'}
                    onClick={() => handleTabChange('settings')}
                  />
                  <MobileTabButton
                    tab={{ id: 'trash', name: 'Trash', icon: Trash2, badge: null }}
                    isActive={activeTab === 'trash'}
                    onClick={() => handleTabChange('trash')}
                  />
                </div>
              </div>
            </>
          )}

          {/* Main Content */}
          <main className="flex-1 min-w-0 pb-20 md:pb-0">
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

/* ──────────────────────────────────────────
   Sub-components for the sidebar
   ────────────────────────────────────────── */

interface SidebarTabItem {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string }>
  badge: string | null
}

function SidebarTab({
  tab,
  isActive,
  isPinned,
  onTogglePin,
  onClick,
  shortcutIndex,
  shortcutHint,
}: {
  tab: SidebarTabItem
  isActive: boolean
  isPinned: boolean
  onTogglePin?: () => void
  onClick: () => void
  shortcutIndex?: number
  shortcutHint?: string
}) {
  const Icon = tab.icon
  const shortcut = shortcutHint || (shortcutIndex ? `Alt+${shortcutIndex}` : undefined)

  return (
    <div className="group/sidebar relative">
      <button
        onClick={onClick}
        className={cn(
          'w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium rounded-lg transition-all duration-150',
          isActive
            ? 'bg-gradient-to-r from-blue-500 to-violet-600 text-white shadow-lg shadow-blue-500/25'
            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100'
        )}
      >
        <Icon className={cn(
          'h-4 w-4 flex-shrink-0 transition-colors',
          isActive ? 'text-white' : 'text-slate-400 group-hover/sidebar:text-slate-600 dark:group-hover/sidebar:text-slate-300'
        )} />
        <span className="truncate">{tab.name}</span>
        {tab.badge && (
          <Badge 
            variant={isActive ? 'default' : 'primary'} 
            size="sm"
            className={cn(
              'ml-auto',
              isActive && 'bg-white/20 text-white border-white/30'
            )}
          >
            {tab.badge}
          </Badge>
        )}
        {isPinned && !tab.badge && (
          <Pin className="w-3 h-3 ml-auto text-slate-300 dark:text-slate-600 opacity-0 group-hover/sidebar:opacity-100 transition-opacity" />
        )}
        {shortcut && !tab.badge && (
          <span className={cn(
            'ml-auto text-[10px] font-mono px-1.5 py-0.5 rounded transition-opacity',
            isActive
              ? 'text-white/50'
              : 'text-slate-400 dark:text-slate-600 opacity-0 group-hover/sidebar:opacity-100'
          )}>
            {shortcut}
          </span>
        )}
      </button>

      {/* Pin/unpin on right-click area (hover overlay) */}
      {onTogglePin && (
        <button
          onClick={(e) => { e.stopPropagation(); onTogglePin() }}
          className={cn(
            'absolute right-1 top-1/2 -translate-y-1/2',
            'p-1 rounded opacity-0 group-hover/sidebar:opacity-100 transition-opacity',
            'hover:bg-slate-200 dark:hover:bg-slate-700',
            isActive && 'hover:bg-white/20'
          )}
          aria-label={isPinned ? 'Unpin tab' : 'Pin tab'}
        >
          <Pin className={cn(
            'w-3 h-3',
            isPinned ? 'text-blue-500' : 'text-slate-400 dark:text-slate-500'
          )} />
        </button>
      )}
    </div>
  )
}

function MobileTabButton({
  tab,
  isActive,
  onClick,
}: {
  tab: SidebarTabItem
  isActive: boolean
  onClick: () => void
}) {
  const Icon = tab.icon
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-200',
        isActive
          ? 'bg-gradient-to-r from-blue-500 to-violet-600 text-white shadow-lg shadow-blue-500/25'
          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
      )}
    >
      <div className="flex items-center gap-3">
        <Icon className={cn(
          'h-4 w-4',
          isActive ? 'text-white' : 'text-slate-400'
        )} />
        <span>{tab.name}</span>
      </div>
      {tab.badge && (
        <Badge 
          variant={isActive ? 'default' : 'primary'} 
          size="sm"
          className={cn(isActive && 'bg-white/20 text-white border-white/30')}
        >
          {tab.badge}
        </Badge>
      )}
    </button>
  )
}

function MobileBottomTab({
  icon,
  label,
  isActive,
  onClick,
}: {
  icon: React.ReactNode
  label: string
  isActive: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex flex-col items-center justify-center gap-0.5 flex-1 py-1 transition-colors',
        isActive
          ? 'text-blue-600 dark:text-blue-400'
          : 'text-slate-400 dark:text-slate-500'
      )}
    >
      {icon}
      <span className="text-[10px] font-medium">{label}</span>
    </button>
  )
}