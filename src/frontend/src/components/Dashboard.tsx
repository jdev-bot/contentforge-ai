'use client'

import { useState } from 'react'
import { AuthUser } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Plus, FileText, Share2, BarChart3, Settings } from 'lucide-react'

interface DashboardProps {
  user: AuthUser
}

export default function Dashboard({ user }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('content')

  const tabs = [
    { id: 'content', name: 'Content', icon: FileText },
    { id: 'projects', name: 'Projects', icon: Plus },
    { id: 'distributions', name: 'Distributions', icon: Share2 },
    { id: 'analytics', name: 'Analytics', icon: BarChart3 },
    { id: 'settings', name: 'Settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  ContentForge
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
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
          {/* Sidebar */}
          <aside className="w-full md:w-64">
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
            
            {/* Quick Stats */}
            <div className="mt-8 bg-white rounded-lg p-4 shadow-sm border border-gray-100">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Content Pieces</span>
                  <span className="font-medium">0</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Assets Generated</span>
                  <span className="font-medium">0</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Published</span>
                  <span className="font-medium">0</span>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            {activeTab === 'content' && <ContentTab />}
            {activeTab === 'projects' && <ProjectsTab />}
            {activeTab === 'distributions' && <DistributionsTab />}
            {activeTab === 'analytics' && <AnalyticsTab />}
            {activeTab === 'settings' && <SettingsTab user={user} />}
          </main>
        </div>
      </div>
    </div>
  )
}

function ContentTab() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Your Content</h2>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Content
        </Button>
      </div>

      {/* Empty State */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
        <div className="mx-auto h-12 w-12 text-gray-400">
          <FileText className="h-12 w-12" />
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900">No content yet</h3>
        <p className="mt-2 text-gray-500 max-w-sm mx-auto">
          Get started by adding your first piece of content. We'll transform it into multiple formats.
        </p>
        
        <div className="mt-6">
          <Button className="flex items-center gap-2 mx-auto">
            <Plus className="h-4 w-4" />
            Add Content
          </Button>
        </div>
      </div>
    </div>
  )
}

function ProjectsTab() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Projects</h2>
      <p className="text-gray-500">Organize your content by brand, campaign, or client.</p>
    </div>
  )
}

function DistributionsTab() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Distributions</h2>
      <p className="text-gray-500">Manage your scheduled and published content across platforms.</p>
    </div>
  )
}

function AnalyticsTab() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Analytics</h2>
      <p className="text-gray-500">Track your content performance and engagement metrics.</p>
    </div>
  )
}

function SettingsTab({ user }: { user: AuthUser }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Profile</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <div className="mt-1 text-gray-900">{user.email}</div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Full Name</label>
            <div className="mt-1 text-gray-900">{user.full_name || 'Not set'}</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Subscription</h3>
        
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Current Plan</p>
            <p className="text-lg font-medium text-gray-900">Free</p>
          </div>
          
          <Button variant="outline">Upgrade</Button>
        </div>
      </div>
    </div>
  )
}
