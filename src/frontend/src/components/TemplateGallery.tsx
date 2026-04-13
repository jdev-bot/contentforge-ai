'use client'

import { useState, useCallback } from 'react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Input } from './ui/Input'
import { useToast } from '../hooks/useToast'

interface TemplateGalleryProps {
  isOpen: boolean
  onClose: () => void
  onSelectTemplate?: (template: Template) => void
}

interface Template {
  id: string
  name: string
  description: string
  category: 'blog' | 'social' | 'newsletter' | 'custom'
  platforms: string[]
  content: string
  tags: string[]
  author: string
  usageCount: number
  createdAt: string
  isCustom?: boolean
}

interface CustomTemplateForm {
  name: string
  description: string
  category: 'blog' | 'social' | 'newsletter'
  platforms: string[]
  content: string
  tags: string[]
}

const PRESET_TEMPLATES: Template[] = [
  // Blog Templates
  {
    id: 'blog-how-to',
    name: 'How-To Guide',
    description: 'Step-by-step tutorial format for educational content',
    category: 'blog',
    platforms: ['blog', 'medium', 'linkedin'],
    content: `# How to [Achieve Result] in [Timeframe]

## Introduction
Brief intro to the problem and why this guide matters.

## Prerequisites
- Item 1
- Item 2
- Item 3

## Step 1: [First Action]
Detailed explanation...

## Step 2: [Second Action]
Detailed explanation...

## Step 3: [Third Action]
Detailed explanation...

## Common Mistakes to Avoid
- Mistake 1
- Mistake 2

## Conclusion
Summary and next steps...

## FAQ
**Q: Question 1?**
A: Answer...

**Q: Question 2?**
A: Answer...`,
    tags: ['tutorial', 'education', 'how-to'],
    author: 'ContentForge AI',
    usageCount: 15420,
    createdAt: '2026-01-15',
  },
  {
    id: 'blog-listicle',
    name: 'Listicle Post',
    description: 'Numbered list format for easy scanning and sharing',
    category: 'blog',
    platforms: ['blog', 'medium', 'linkedin'],
    content: `# [Number] [Topic] That Will [Benefit]

## Introduction
Hook readers with why this list matters.

## 1. [First Item]
Description and explanation...

## 2. [Second Item]
Description and explanation...

## 3. [Third Item]
Description and explanation...

## 4. [Fourth Item]
Description and explanation...

## 5. [Fifth Item]
Description and explanation...

## Bonus Tip
Extra value for readers...

## Conclusion
Wrap up with key takeaways...`,
    tags: ['listicle', 'engagement', 'shareable'],
    author: 'ContentForge AI',
    usageCount: 23100,
    createdAt: '2026-01-15',
  },
  {
    id: 'blog-case-study',
    name: 'Case Study',
    description: 'Results-focused format for showcasing success stories',
    category: 'blog',
    platforms: ['blog', 'linkedin'],
    content: `# How [Company] [Achieved Result] in [Timeframe]

## Background
Context about the company and situation...

## The Challenge
What problem needed solving...

## The Solution
How they approached it...

## Implementation
Step-by-step execution...

## Results
- Metric 1: X% improvement
- Metric 2: Y% increase
- Metric 3: Z% reduction

## Key Takeaways
1. Lesson 1
2. Lesson 2
3. Lesson 3

## Conclusion
Final thoughts and next steps...`,
    tags: ['case-study', 'results', 'b2b'],
    author: 'ContentForge AI',
    usageCount: 8900,
    createdAt: '2026-01-20',
  },
  // Social Templates
  {
    id: 'social-thread',
    name: 'Viral Thread',
    description: 'Multi-post Twitter/X thread for maximum engagement',
    category: 'social',
    platforms: ['twitter'],
    content: `🧵 [Number] [Topic] that will [benefit]:

1/ [Hook statement]

2/ [Point 1 with value]

3/ [Point 2 with value]

4/ [Point 3 with value]

5/ [Point 4 with value]

6/ [Point 5 with value]

7/ [Summary + CTA]

Like this thread? Follow @[handle] for more.`,
    tags: ['twitter', 'thread', 'viral'],
    author: 'ContentForge AI',
    usageCount: 45600,
    createdAt: '2026-01-10',
  },
  {
    id: 'social-linkedin',
    name: 'LinkedIn Professional Post',
    description: 'Professional narrative format for LinkedIn',
    category: 'social',
    platforms: ['linkedin'],
    content: `[Opening hook - personal story or bold statement]

[Context and background]

[The challenge or situation]

[The solution or insight]

[Results or outcome]

[Key lessons learned]

[Call to action or question for engagement]

[Relevant hashtags]`,
    tags: ['linkedin', 'professional', 'storytelling'],
    author: 'ContentForge AI',
    usageCount: 32100,
    createdAt: '2026-01-12',
  },
  {
    id: 'social-carousel',
    name: 'Instagram Carousel',
    description: 'Swipe-through educational carousel format',
    category: 'social',
    platforms: ['instagram'],
    content: `Slide 1 (Cover): Eye-catching headline with bold design

Slide 2: Problem statement
"Are you struggling with..."

Slide 3: Agitate the problem
"This leads to..."

Slide 4: Introduce solution
"Here's how to fix it:"

Slide 5: Step 1
"First, do this..."

Slide 6: Step 2
"Next, do this..."

Slide 7: Step 3
"Finally, do this..."

Slide 8: Results/Proof
"Here's what happened..."

Slide 9: CTA
"Save this post and follow for more!"`,
    tags: ['instagram', 'carousel', 'visual'],
    author: 'ContentForge AI',
    usageCount: 28700,
    createdAt: '2026-01-18',
  },
  // Newsletter Templates
  {
    id: 'newsletter-weekly',
    name: 'Weekly Digest',
    description: 'Curated news and updates format for regular newsletters',
    category: 'newsletter',
    platforms: ['email'],
    content: `Subject: [Company] Weekly Digest - [Week of Date]

Hi [First Name],

Welcome to this week's edition of [Newsletter Name]!

## 🚀 This Week's Highlights

### [Story 1 Title]
[Brief summary]
[Read more →]

### [Story 2 Title]
[Brief summary]
[Read more →]

### [Story 3 Title]
[Brief summary]
[Read more →]

## 📊 Quick Stats
- Metric 1: Value
- Metric 2: Value
- Metric 3: Value

## 🔗 Worth Your Time
- [Link 1 description]
- [Link 2 description]
- [Link 3 description]

## 💡 Pro Tip
[Short actionable tip]

## What's Coming Next Week
[Teaser for next week's content]

See you then!

[Your Name]

P.S. [Personal note or additional CTA]`,
    tags: ['newsletter', 'weekly', 'digest'],
    author: 'ContentForge AI',
    usageCount: 18900,
    createdAt: '2026-01-25',
  },
  {
    id: 'newsletter-product-launch',
    name: 'Product Launch Announcement',
    description: 'Announcement format for new product or feature launches',
    category: 'newsletter',
    platforms: ['email'],
    content: `Subject: 🎉 Introducing [Product Name] - [Key Benefit]

Hi [First Name],

Big news! Today we're thrilled to announce [Product Name]...

## What is [Product Name]?
[Product description and positioning]

## Why We Built This
[Origin story and motivation]

## Key Features
✨ Feature 1 - Description
✨ Feature 2 - Description
✨ Feature 3 - Description

## How It Works
[Simple explanation]

## Who It's For
[Target audience description]

## Special Launch Offer
🎁 [Discount/Offer details]

[Get Early Access Button]

## Questions?
Reply to this email or [contact method].

Excited to hear what you think!

[Your Name]
[Title]

P.S. [Additional incentive or urgency]`,
    tags: ['newsletter', 'product-launch', 'announcement'],
    author: 'ContentForge AI',
    usageCount: 12400,
    createdAt: '2026-02-01',
  },
]

export default function TemplateGallery({
  isOpen,
  onClose,
  onSelectTemplate,
}: TemplateGalleryProps) {
  const { showToast } = useToast()
  const [activeTab, setActiveTab] = useState<'browse' | 'custom' | 'marketplace'>('browse')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [customTemplates, setCustomTemplates] = useState<Template[]>([])
  const [isCreatingTemplate, setIsCreatingTemplate] = useState(false)
  const [customForm, setCustomForm] = useState<CustomTemplateForm>({
    name: '',
    description: '',
    category: 'blog',
    platforms: [],
    content: '',
    tags: [],
  })

  const categories = [
    { id: 'all', name: 'All Templates', icon: '📚' },
    { id: 'blog', name: 'Blog Posts', icon: '📝' },
    { id: 'social', name: 'Social Media', icon: '📱' },
    { id: 'newsletter', name: 'Newsletters', icon: '📧' },
    { id: 'custom', name: 'My Templates', icon: '⭐' },
  ]

  const platforms = [
    { id: 'blog', name: 'Blog', icon: '📝' },
    { id: 'medium', name: 'Medium', icon: '📖' },
    { id: 'twitter', name: 'Twitter/X', icon: '𝕏' },
    { id: 'linkedin', name: 'LinkedIn', icon: 'in' },
    { id: 'facebook', name: 'Facebook', icon: 'f' },
    { id: 'instagram', name: 'Instagram', icon: '📷' },
    { id: 'tiktok', name: 'TikTok', icon: '🎵' },
    { id: 'email', name: 'Email', icon: '📧' },
  ]

  const filteredTemplates = useCallback(() => {
    let templates = [...PRESET_TEMPLATES, ...customTemplates]
    
    if (selectedCategory !== 'all') {
      templates = templates.filter(t => t.category === selectedCategory || (selectedCategory === 'custom' && t.isCustom))
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      templates = templates.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.tags.some(tag => tag.toLowerCase().includes(query))
      )
    }
    
    return templates.sort((a, b) => b.usageCount - a.usageCount)
  }, [selectedCategory, searchQuery, customTemplates])

  const handleSelectTemplate = useCallback((template: Template) => {
    setSelectedTemplate(template)
  }, [])

  const handleUseTemplate = useCallback(() => {
    if (!selectedTemplate) return
    
    onSelectTemplate?.(selectedTemplate)
    showToast(`Template "${selectedTemplate.name}" selected!`, 'success')
    onClose()
  }, [selectedTemplate, onSelectTemplate, onClose, showToast])

  const handleCreateCustomTemplate = useCallback(() => {
    if (!customForm.name || !customForm.content) {
      showToast('Please fill in all required fields', 'error')
      return
    }

    const newTemplate: Template = {
      id: `custom-${Date.now()}`,
      name: customForm.name,
      description: customForm.description,
      category: customForm.category,
      platforms: customForm.platforms,
      content: customForm.content,
      tags: customForm.tags,
      author: 'You',
      usageCount: 0,
      createdAt: new Date().toISOString().split('T')[0],
      isCustom: true,
    }

    setCustomTemplates(prev => [...prev, newTemplate])
    setIsCreatingTemplate(false)
    setCustomForm({
      name: '',
      description: '',
      category: 'blog',
      platforms: [],
      content: '',
      tags: [],
    })
    showToast('Custom template created!', 'success')
  }, [customForm, showToast])

  const handleDeleteCustomTemplate = useCallback((id: string) => {
    setCustomTemplates(prev => prev.filter(t => t.id !== id))
    if (selectedTemplate?.id === id) {
      setSelectedTemplate(null)
    }
    showToast('Template deleted', 'info')
  }, [selectedTemplate, showToast])

  const togglePlatform = (platformId: string, isCustom: boolean = false) => {
    if (isCustom) {
      setCustomForm(prev => ({
        ...prev,
        platforms: prev.platforms.includes(platformId)
          ? prev.platforms.filter(p => p !== platformId)
          : [...prev.platforms, platformId]
      }))
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <Card className="w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Template Gallery</h2>
              <p className="text-gray-500 dark:text-gray-400">Choose from pre-built templates or create your own</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
          
          {/* Tabs */}
          <div className="flex gap-2 mt-6">
            {[
              { id: 'browse', label: 'Browse Templates', icon: '📚' },
              { id: 'custom', label: 'Create Custom', icon: '✨' },
              { id: 'marketplace', label: 'Marketplace', icon: '🏪' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Browse Templates */}
          {activeTab === 'browse' && (
            <>
              {/* Sidebar */}
              <div className="w-64 border-r border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900">
                <Input
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="mb-4"
                />
                
                <div className="space-y-1">
                  {categories.map(category => (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                        selectedCategory === category.id
                          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                    >
                      <span>{category.icon}</span>
                      <span className="font-medium">{category.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Template Grid / Preview */}
              <div className="flex-1 overflow-y-auto p-4">
                {selectedTemplate ? (
                  <div className="space-y-4">
                    <button
                      onClick={() => setSelectedTemplate(null)}
                      className="text-blue-600 hover:underline"
                    >
                      ← Back to templates
                    </button>
                    
                    <Card className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                            {selectedTemplate.name}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-400 mt-1">
                            {selectedTemplate.description}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {selectedTemplate.tags.map(tag => (
                            <span key={tag} className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                        <span>👤 {selectedTemplate.author}</span>
                        <span>📊 {selectedTemplate.usageCount.toLocaleString()} uses</span>
                        <span>📅 {selectedTemplate.createdAt}</span>
                      </div>
                      
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Compatible Platforms:</h4>
                        <div className="flex gap-2">
                          {selectedTemplate.platforms.map(platform => (
                            <span key={platform} className="px-3 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-full text-sm">
                              {platform}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Template Preview:</h4>
                        <pre className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap font-mono overflow-x-auto max-h-96 overflow-y-auto">
                          {selectedTemplate.content}
                        </pre>
                      </div>
                      
                      <div className="flex gap-3">
                        <Button onClick={handleUseTemplate} className="flex-1">
                          Use This Template
                        </Button>
                        {selectedTemplate.isCustom && (
                          <Button 
                            variant="secondary" 
                            onClick={() => handleDeleteCustomTemplate(selectedTemplate.id)}
                            className="text-red-600"
                          >
                            Delete
                          </Button>
                        )}
                      </div>
                    </Card>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {filteredTemplates().map(template => (
                      <Card
                        key={template.id}
                        onClick={() => handleSelectTemplate(template)}
                        className="p-4 cursor-pointer hover:border-blue-500 transition-colors"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-bold text-gray-900 dark:text-white">{template.name}</h3>
                          <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                            {template.category}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                          {template.description}
                        </p>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>👤 {template.author}</span>
                          <span>📊 {template.usageCount.toLocaleString()} uses</span>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
                
                {!selectedTemplate && filteredTemplates().length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-4">🔍</div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">No templates found</h3>
                    <p className="text-gray-500">Try adjusting your search or category filter</p>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Create Custom Template */}
          {activeTab === 'custom' && (
            <div className="flex-1 overflow-y-auto p-6">
              {isCreatingTemplate ? (
                <div className="max-w-2xl mx-auto space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-bold">Create Custom Template</h3>
                    <button
                      onClick={() => setIsCreatingTemplate(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Template Name *
                    </label>
                    <Input
                      value={customForm.name}
                      onChange={(e) => setCustomForm(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., My Blog Template"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description
                    </label>
                    <Input
                      value={customForm.description}
                      onChange={(e) => setCustomForm(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Brief description of this template"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Category
                    </label>
                    <select
                      value={customForm.category}
                      onChange={(e) => setCustomForm(prev => ({ ...prev, category: e.target.value as 'blog' | 'social' | 'newsletter' }))}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
                    >
                      <option value="blog">Blog Post</option>
                      <option value="social">Social Media</option>
                      <option value="newsletter">Newsletter</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Compatible Platforms
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {platforms.map(platform => (
                        <button
                          key={platform.id}
                          onClick={() => togglePlatform(platform.id, true)}
                          className={`px-3 py-2 rounded-lg border transition-colors ${
                            customForm.platforms.includes(platform.id)
                              ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500'
                              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
                          }`}
                        >
                          {platform.icon} {platform.name}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Template Content *
                    </label>
                    <textarea
                      value={customForm.content}
                      onChange={(e) => setCustomForm(prev => ({ ...prev, content: e.target.value }))}
                      placeholder="Enter your template structure... Use [brackets] for variables"
                      className="w-full h-64 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 font-mono text-sm"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tags (comma separated)
                    </label>
                    <Input
                      value={customForm.tags.join(', ')}
                      onChange={(e) => setCustomForm(prev => ({ 
                        ...prev, 
                        tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                      }))}
                      placeholder="e.g., tutorial, educational, how-to"
                    />
                  </div>
                  
                  <div className="flex gap-3">
                    <Button onClick={() => setIsCreatingTemplate(false)} variant="secondary" className="flex-1">
                      Cancel
                    </Button>
                    <Button onClick={handleCreateCustomTemplate} className="flex-1">
                      Create Template
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">✨</div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Create Your Own Template</h3>
                  <p className="text-gray-500 mb-6 max-w-md mx-auto">
                    Build a custom template with your brand voice and specific requirements. Reuse it for consistent content creation.
                  </p>
                  <Button onClick={() => setIsCreatingTemplate(true)}>
                    Start Creating
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* Marketplace */}
          {activeTab === 'marketplace' && (
            <div className="flex-1 overflow-y-auto p-6">
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🏪</div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Template Marketplace</h3>
                <p className="text-gray-500 mb-6 max-w-md mx-auto">
                  Coming soon! Browse templates created by the community and share your own.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                  <Card className="p-4 text-center opacity-50">
                    <div className="text-2xl mb-2">📊</div>
                    <h4 className="font-medium">Analytics Templates</h4>
                    <p className="text-xs text-gray-500">Coming soon</p>
                  </Card>
                  <Card className="p-4 text-center opacity-50">
                    <div className="text-2xl mb-2">🎯</div>
                    <h4 className="font-medium">Marketing Templates</h4>
                    <p className="text-xs text-gray-500">Coming soon</p>
                  </Card>
                  <Card className="p-4 text-center opacity-50">
                    <div className="text-2xl mb-2">🏢</div>
                    <h4 className="font-medium">Business Templates</h4>
                    <p className="text-xs text-gray-500">Coming soon</p>
                  </Card>
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}