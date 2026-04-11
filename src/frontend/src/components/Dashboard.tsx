'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { AuthUser } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Plus, FileText, Share2, BarChart3, Settings, Folder, Menu, X } from 'lucide-react'
import DistributionsTab from './DistributionsTab'
import ProjectsTab from './ProjectsTab'
import AnalyticsTab from './AnalyticsTab'
import SettingsTab from './SettingsTab'
import ContentTab from './ContentTab'

interface DashboardProps {
  user: AuthUser
}

export default function Dashboard({ user }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('content')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const router = useRouter()

  const tabs = [
    { id: 'content', name: 'Content', icon: FileText },
    { id: 'projects', name: 'Projects', icon: Folder },
    { id: 'distributions', name: 'Distributions', icon: Share2 },
    { id: 'analytics', name: 'Analytics', icon: BarChart3 },
    { id: 'settings', name: 'Settings', icon: Settings },
  ]

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
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
      // Escape to close mobile menu
      if (e.key === 'Escape') {
        setMobileMenuOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [router])

  const renderTabContent = () => {
    switch (activeTab) {
      case 'content':
        return <ContentTab />
      case 'projects':
        return <ProjectsTab />
      case 'distributions':
        return <DistributionsTab />
      case 'analytics':
        return <AnalyticsTab />
      case 'settings':
        return <SettingsTab user={user} />
      default:
        return <ContentTab />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Mobile Menu Button */}
            <div className="flex items-center gap-4">
              {/* Mobile Menu Button */}
              <button
                className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              >
                {mobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
              
              <div className="flex-shrink-0">
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  ContentForge
                </span>
              </div>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {user.email}
              </div>
              <Button variant="outline" size="sm">
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar - Desktop */}
          <aside className="hidden md:block w-64">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {tab.name}
                  </button>
                )
              })}
            </nav>
            
            {/* Keyboard Shortcuts Info */}
            <div className="mt-8 p-4 bg-gray-100 rounded-lg">
              <p className="text-xs font-medium text-gray-700 mb-2">Keyboard Shortcuts</p>
              <div className="space-y-1 text-xs text-gray-500">
                <div className="flex justify-between">
                  <span>New Content</span>
                  <kbd className="px-1.5 py-0.5 bg-white rounded border border-gray-300">Ctrl+N</kbd>
                </div>
                <div className="flex justify-between">
                  <span>New Project</span>
                  <kbd className="px-1.5 py-0.5 bg-white rounded border border-gray-300">Ctrl+P</kbd>
                </div>
              </div>
            </div>
          </aside>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <>
              {/* Backdrop */}
              <div 
                className="fixed inset-0 bg-black/50 z-40 md:hidden"
                onClick={() => setMobileMenuOpen(false)}
              />
              
              {/* Mobile Sidebar */}
              <aside className="fixed inset-y-0 left-0 w-64 bg-white z-50 md:hidden shadow-xl">
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    ContentForge
                  </span>
                  <button
                    onClick={() => setMobileMenuOpen(false)}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                
                <nav className="p-4 space-y-1">
                  {tabs.map((tab) => {
                    const Icon = tab.icon
                    return (
                      <button
                        key={tab.id}
                        onClick={() => {
                          setActiveTab(tab.id)
                          setMobileMenuOpen(false)
                        }}
                        className={`w-full flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors ${
                          activeTab === tab.id
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-700 hover:bg-gray-100'
                        }`}
                      >
                        <Icon className="mr-3 h-5 w-5" />
                        {tab.name}
                      </button>
                    )
                  })}
                </nav>
                
                <div className="p-4 border-t border-gray-200">
                  <div className="text-sm text-gray-600 mb-4">
                    {user.email}
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
            {renderTabContent()}
          </main>
        </div>
      </div>
    </div>
  )
}

