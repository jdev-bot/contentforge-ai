'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Star,
  Download,
  Eye,
  Tag,
  ChevronRight,
  ChevronLeft,
  Filter,
  TrendingUp,
  Award,
  Heart,
  MessageSquare,
  Clock,
  User,
  Plus,
  X,
  Send,
  Loader2,
  Sparkles,
  Package,
  ExternalLink,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/hooks/useToast'
import {
  listMarketplaceTemplates,
  getMarketplaceCategories,
  getMarketplaceTags,
  getFeaturedTemplates,
  getTrendingTemplates,
  getMarketplaceTemplate,
  installMarketplaceTemplate,
  rateMarketplaceTemplate,
  getTemplateRatings,
  createMarketplaceTemplate,
  publishMarketplaceTemplate,
  type MarketplaceTemplate,
  type MarketplaceCategory,
  type MarketplaceTag,
  type MarketplaceRating,
} from '@/lib/api'

type ViewMode = 'gallery' | 'detail' | 'publish'

interface TemplateMarketplaceProps {
  isOpen: boolean
  onClose: () => void
  onUseTemplate?: (template: MarketplaceTemplate) => void
}

export default function TemplateMarketplace({ isOpen, onClose, onUseTemplate }: TemplateMarketplaceProps) {
  const { showToast } = useToast()

  // Navigation state
  const [viewMode, setViewMode] = useState<ViewMode>('gallery')
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null)

  // Gallery state
  const [templates, setTemplates] = useState<MarketplaceTemplate[]>([])
  const [categories, setCategories] = useState<MarketplaceCategory[]>([])
  const [popularTags, setPopularTags] = useState<MarketplaceTag[]>([])
  const [totalTemplates, setTotalTemplates] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  // Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'newest' | 'popular' | 'rating'>('newest')
  const [offset, setOffset] = useState(0)
  const limit = 12

  // Detail view state
  const [detailTemplate, setDetailTemplate] = useState<MarketplaceTemplate | null>(null)
  const [ratings, setRatings] = useState<MarketplaceRating[]>([])
  const [isLoadingDetail, setIsLoadingDetail] = useState(false)
  const [userRating, setUserRating] = useState(0)
  const [userReview, setUserReview] = useState('')
  const [isSubmittingRating, setIsSubmittingRating] = useState(false)
  const [isInstalling, setIsInstalling] = useState(false)

  // Publish form state
  const [publishForm, setPublishForm] = useState({
    name: '',
    description: '',
    category: 'blog',
    content: '',
    tags: '',
    platforms: '',
    version: '1.0.0',
  })
  const [isPublishing, setIsPublishing] = useState(false)

  // Featured & Trending
  const [featuredTemplates, setFeaturedTemplates] = useState<MarketplaceTemplate[]>([])
  const [trendingTemplates, setTrendingTemplates] = useState<MarketplaceTemplate[]>([])

  // Load initial data
  useEffect(() => {
    if (isOpen) {
      loadInitialData()
    }
  }, [isOpen])

  // Reload templates when filters change
  useEffect(() => {
    if (isOpen && viewMode === 'gallery') {
      loadTemplates()
    }
  }, [searchQuery, selectedCategory, selectedTags, sortBy, offset])

  const loadInitialData = async () => {
    setIsLoading(true)
    try {
      const [cats, tags, featured, trending] = await Promise.all([
        getMarketplaceCategories().catch(() => []),
        getMarketplaceTags(15).catch(() => []),
        getFeaturedTemplates(6).catch(() => []),
        getTrendingTemplates(6).catch(() => []),
      ])
      setCategories(cats)
      setPopularTags(tags)
      setFeaturedTemplates(featured)
      setTrendingTemplates(trending)
    } catch (error: unknown) {
      // Categories/tags are non-critical
    }
  }

  const loadTemplates = async () => {
    setIsLoading(true)
    try {
      const result = await listMarketplaceTemplates({
        category: selectedCategory !== 'all' ? selectedCategory : undefined,
        search: searchQuery || undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        sort: sortBy,
        limit,
        offset,
      })
      setTemplates(result.templates)
      setTotalTemplates(result.total)
    } catch (error: unknown) {
      showToast('Failed to load templates', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const loadTemplateDetail = async (templateId: string) => {
    setIsLoadingDetail(true)
    try {
      const [template, ratingsResult] = await Promise.all([
        getMarketplaceTemplate(templateId),
        getTemplateRatings(templateId, 10, 0).catch(() => ({ ratings: [], total: 0 })),
      ])
      setDetailTemplate(template)
      setRatings(ratingsResult.ratings || [])
      setSelectedTemplateId(templateId)
      setViewMode('detail')
    } catch (error: unknown) {
      showToast('Failed to load template details', 'error')
    } finally {
      setIsLoadingDetail(false)
    }
  }

  const handleInstall = useCallback(async () => {
    if (!selectedTemplateId) return
    setIsInstalling(true)
    try {
      const result = await installMarketplaceTemplate(selectedTemplateId)
      if (result.already_installed) {
        showToast('Template already installed', 'info')
      } else {
        showToast('Template installed successfully!', 'success')
      }
      // Refresh detail
      loadTemplateDetail(selectedTemplateId)
    } catch (error: unknown) {
      showToast(error instanceof Error ? error.message : 'Failed to install template', 'error')
    } finally {
      setIsInstalling(false)
    }
  }, [selectedTemplateId, showToast])

  const handleSubmitRating = useCallback(async () => {
    if (!selectedTemplateId || userRating === 0) return
    setIsSubmittingRating(true)
    try {
      await rateMarketplaceTemplate(selectedTemplateId, {
        rating: userRating,
        review: userReview || undefined,
      })
      showToast('Rating submitted!', 'success')
      setUserRating(0)
      setUserReview('')
      // Refresh ratings
      const result = await getTemplateRatings(selectedTemplateId, 10, 0)
      setRatings(result.ratings || [])
      loadTemplateDetail(selectedTemplateId)
    } catch (error: unknown) {
      showToast(error instanceof Error ? error.message : 'Failed to submit rating', 'error')
    } finally {
      setIsSubmittingRating(false)
    }
  }, [selectedTemplateId, userRating, userReview, showToast])

  const handlePublish = useCallback(async () => {
    if (!publishForm.name || !publishForm.description || !publishForm.content) {
      showToast('Please fill in all required fields', 'error')
      return
    }
    setIsPublishing(true)
    try {
      const template = await createMarketplaceTemplate({
        name: publishForm.name,
        description: publishForm.description,
        category: publishForm.category,
        content: publishForm.content,
        tags: publishForm.tags.split(',').map(t => t.trim()).filter(Boolean),
        platforms: publishForm.platforms.split(',').map(p => p.trim()).filter(Boolean),
        version: publishForm.version,
        is_published: true,
      })
      showToast('Template published to marketplace!', 'success')
      setPublishForm({ name: '', description: '', category: 'blog', content: '', tags: '', platforms: '', version: '1.0.0' })
      setViewMode('gallery')
      loadTemplates()
    } catch (error: unknown) {
      showToast(error instanceof Error ? error.message : 'Failed to publish template', 'error')
    } finally {
      setIsPublishing(false)
    }
  }, [publishForm, showToast])

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    )
    setOffset(0)
  }

  const renderStars = (rating: number, size: 'sm' | 'md' = 'sm') => {
    const sizeClass = size === 'sm' ? 'w-3.5 h-3.5' : 'w-5 h-5'
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`${sizeClass} ${
              star <= Math.round(rating)
                ? 'text-amber-400 fill-amber-400'
                : 'text-slate-300 dark:text-slate-600'
            }`}
          />
        ))}
      </div>
    )
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', duration: 0.5 }}
          className="w-full max-w-6xl"
          onClick={(e) => e.stopPropagation()}
        >
          <Card variant="glass" padding="none" className="overflow-hidden max-h-[90vh] flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-white/10 dark:border-white/5 shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-emerald-500/20">
                    <Package className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                      Template Marketplace
                    </h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {totalTemplates} templates available
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setViewMode('publish')}
                  >
                    <Plus className="w-3.5 h-3.5 mr-1.5" /> Publish
                  </Button>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors text-slate-500"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden flex">
              <AnimatePresence mode="wait">
                {/* === GALLERY VIEW === */}
                {viewMode === 'gallery' && (
                  <motion.div
                    key="gallery"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex-1 flex"
                  >
                    {/* Sidebar: Categories + Tags */}
                    <div className="w-56 border-r border-white/10 dark:border-white/5 p-4 bg-slate-50/50 dark:bg-slate-900/50 overflow-y-auto shrink-0">
                      {/* Search */}
                      <div className="relative mb-4">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <Input
                          value={searchQuery}
                          onChange={(e) => { setSearchQuery(e.target.value); setOffset(0) }}
                          placeholder="Search templates..."
                          className="pl-9 text-sm"
                        />
                      </div>

                      {/* Categories */}
                      <div className="mb-6">
                        <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                          Categories
                        </h4>
                        <div className="space-y-0.5">
                          <button
                            onClick={() => { setSelectedCategory('all'); setOffset(0) }}
                            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
                              selectedCategory === 'all'
                                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
                                : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400'
                            }`}
                          >
                            <span>📚 All</span>
                          </button>
                          {categories.map((cat) => (
                            <button
                              key={cat.id}
                              onClick={() => { setSelectedCategory(cat.id); setOffset(0) }}
                              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
                                selectedCategory === cat.id
                                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
                                  : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400'
                              }`}
                            >
                              <span>{cat.icon} {cat.name}</span>
                              <span className="text-xs opacity-60">{cat.template_count}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Popular Tags */}
                      <div className="mb-6">
                        <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                          Popular Tags
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {popularTags.map((tag) => (
                            <button
                              key={tag.name}
                              onClick={() => toggleTag(tag.name)}
                              className={`px-2 py-1 rounded-md text-xs transition-colors ${
                                selectedTags.includes(tag.name)
                                  ? 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300'
                                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
                              }`}
                            >
                              #{tag.name}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Sort */}
                      <div>
                        <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                          Sort By
                        </h4>
                        <div className="space-y-0.5">
                          {[
                            { id: 'newest', label: 'Newest', icon: Clock },
                            { id: 'popular', label: 'Most Popular', icon: TrendingUp },
                            { id: 'rating', label: 'Highest Rated', icon: Award },
                          ].map((option) => (
                            <button
                              key={option.id}
                              onClick={() => { setSortBy(option.id as 'newest' | 'popular' | 'rating'); setOffset(0) }}
                              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                                sortBy === option.id
                                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
                                  : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400'
                              }`}
                            >
                              <option.icon className="w-3.5 h-3.5" />
                              {option.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Main Content */}
                    <div className="flex-1 overflow-y-auto p-4">
                      {/* Featured Banner */}
                      {featuredTemplates.length > 0 && !searchQuery && selectedCategory === 'all' && (
                        <div className="mb-6">
                          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2 mb-3">
                            <Award className="w-4 h-4 text-amber-500" /> Featured Templates
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            {featuredTemplates.slice(0, 3).map((template) => (
                              <motion.div
                                key={template.id}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                              >
                                <Card
                                  variant="glass"
                                  interactive
                                  padding="sm"
                                  onClick={() => loadTemplateDetail(template.id)}
                                  className="border-amber-200/50 dark:border-amber-500/20"
                                >
                                  <div className="flex items-start justify-between mb-2">
                                    <h4 className="font-semibold text-sm text-slate-900 dark:text-slate-100 line-clamp-1">
                                      {template.name}
                                    </h4>
                                    <Badge className="text-xs bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 shrink-0 ml-2">
                                      ⭐
                                    </Badge>
                                  </div>
                                  <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 mb-2">
                                    {template.description}
                                  </p>
                                  <div className="flex items-center justify-between text-xs text-slate-400">
                                    <div className="flex items-center gap-2">
                                      {renderStars(template.avg_rating)}
                                    </div>
                                    <span>{template.install_count} installs</span>
                                  </div>
                                </Card>
                              </motion.div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Template Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {templates.map((template) => (
                          <motion.div
                            key={template.id}
                            whileHover={{ scale: 1.02, y: -2 }}
                            whileTap={{ scale: 0.98 }}
                            layout
                          >
                            <Card
                              variant="glass"
                              interactive
                              padding="sm"
                              onClick={() => loadTemplateDetail(template.id)}
                            >
                              <div className="flex items-start justify-between mb-2">
                                <h4 className="font-semibold text-sm text-slate-900 dark:text-slate-100 line-clamp-1">
                                  {template.name}
                                </h4>
                                <Badge variant="outline" className="text-xs shrink-0 ml-2">
                                  {template.category}
                                </Badge>
                              </div>
                              <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 mb-3">
                                {template.description}
                              </p>
                              {template.tags && template.tags.length > 0 && (
                                <div className="flex flex-wrap gap-1 mb-3">
                                  {template.tags.slice(0, 3).map((tag) => (
                                    <span key={tag} className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-xs text-slate-500">
                                      #{tag}
                                    </span>
                                  ))}
                                  {template.tags.length > 3 && (
                                    <span className="text-xs text-slate-400">+{template.tags.length - 3}</span>
                                  )}
                                </div>
                              )}
                              <div className="flex items-center justify-between text-xs text-slate-400">
                                <div className="flex items-center gap-1">
                                  {renderStars(template.avg_rating)}
                                  <span className="ml-1">({template.rating_count})</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className="flex items-center gap-0.5">
                                    <Download className="w-3 h-3" /> {template.install_count}
                                  </span>
                                </div>
                              </div>
                              {template.author && (
                                <div className="mt-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-400 flex items-center gap-1">
                                  <User className="w-3 h-3" />
                                  {template.author.full_name || template.author.email}
                                </div>
                              )}
                            </Card>
                          </motion.div>
                        ))}
                      </div>

                      {/* Loading / Empty State */}
                      {isLoading && (
                        <div className="flex items-center justify-center py-12">
                          <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                        </div>
                      )}
                      {!isLoading && templates.length === 0 && (
                        <div className="text-center py-12">
                          <div className="text-4xl mb-3">🔍</div>
                          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">No templates found</h3>
                          <p className="text-sm text-slate-500 mt-1">Try adjusting your search or filters</p>
                        </div>
                      )}

                      {/* Pagination */}
                      {totalTemplates > limit && (
                        <div className="flex items-center justify-center gap-2 mt-6">
                          <Button
                            variant="secondary"
                            size="sm"
                            disabled={offset === 0}
                            onClick={() => setOffset(Math.max(0, offset - limit))}
                          >
                            <ChevronLeft className="w-4 h-4" />
                          </Button>
                          <span className="text-sm text-slate-500">
                            {Math.floor(offset / limit) + 1} / {Math.ceil(totalTemplates / limit)}
                          </span>
                          <Button
                            variant="secondary"
                            size="sm"
                            disabled={offset + limit >= totalTemplates}
                            onClick={() => setOffset(offset + limit)}
                          >
                            <ChevronRight className="w-4 h-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}

                {/* === DETAIL VIEW === */}
                {viewMode === 'detail' && detailTemplate && (
                  <motion.div
                    key="detail"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="flex-1 overflow-y-auto p-6"
                  >
                    {isLoadingDetail ? (
                      <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {/* Back button */}
                        <button
                          onClick={() => { setViewMode('gallery'); setDetailTemplate(null) }}
                          className="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                        >
                          <ChevronLeft className="w-4 h-4" /> Back to marketplace
                        </button>

                        {/* Template Header */}
                        <div>
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                                {detailTemplate.name}
                              </h2>
                              <p className="text-slate-600 dark:text-slate-400 mt-1">
                                {detailTemplate.description}
                              </p>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                              <Button onClick={handleInstall} disabled={isInstalling}>
                                {isInstalling ? (
                                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                  <Download className="w-4 h-4 mr-2" />
                                )}
                                {isInstalling ? 'Installing...' : 'Install Template'}
                              </Button>
                              <Button
                                variant="secondary"
                                onClick={() => onUseTemplate?.(detailTemplate)}
                              >
                                <Sparkles className="w-4 h-4 mr-2" /> Use Template
                              </Button>
                            </div>
                          </div>
                        </div>

                        {/* Stats Bar */}
                        <div className="flex items-center gap-6 text-sm text-slate-500 dark:text-slate-400">
                          <div className="flex items-center gap-1">
                            {renderStars(detailTemplate.avg_rating, 'md')}
                            <span className="ml-1 font-medium text-slate-700 dark:text-slate-300">
                              {detailTemplate.avg_rating.toFixed(1)}
                            </span>
                            <span>({detailTemplate.rating_count} ratings)</span>
                          </div>
                          <span className="flex items-center gap-1">
                            <Download className="w-4 h-4" /> {detailTemplate.install_count} installs
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageSquare className="w-4 h-4" /> {detailTemplate.review_count} reviews
                          </span>
                          <Badge variant="outline">v{detailTemplate.version}</Badge>
                          {detailTemplate.is_featured && (
                            <Badge className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300">
                              <Award className="w-3 h-3 mr-1" /> Featured
                            </Badge>
                          )}
                        </div>

                        {/* Author */}
                        {detailTemplate.author && (
                          <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/10 to-violet-500/10">
                              <User className="w-5 h-5 text-blue-500" />
                            </div>
                            <div>
                              <p className="font-medium text-sm text-slate-900 dark:text-slate-100">
                                {detailTemplate.author.full_name || detailTemplate.author.email}
                              </p>
                              <p className="text-xs text-slate-500">Template Author</p>
                            </div>
                          </div>
                        )}

                        {/* Tags & Platforms */}
                        <div className="flex flex-wrap gap-2">
                          {detailTemplate.tags?.map((tag: string) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              #{tag}
                            </Badge>
                          ))}
                          {detailTemplate.platforms?.map((platform: string) => (
                            <Badge key={platform} className="text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                              {platform}
                            </Badge>
                          ))}
                        </div>

                        {/* Content Preview */}
                        <Card variant="glass" padding="md">
                          <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">
                            Template Preview
                          </h4>
                          <pre className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap font-mono overflow-x-auto max-h-96 overflow-y-auto p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                            {detailTemplate.content}
                          </pre>
                        </Card>

                        {/* Rating Section */}
                        <div className="space-y-4">
                          <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                            <Star className="w-4 h-4 text-amber-500" /> Rate this template
                          </h4>

                          {/* Rating Input */}
                          <div className="flex items-center gap-4">
                            <div className="flex gap-1">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <motion.button
                                  key={star}
                                  whileHover={{ scale: 1.2 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => setUserRating(star)}
                                >
                                  <Star
                                    className={`w-6 h-6 transition-colors ${
                                      star <= userRating
                                        ? 'text-amber-400 fill-amber-400'
                                        : 'text-slate-300 dark:text-slate-600 hover:text-amber-300'
                                    }`}
                                  />
                                </motion.button>
                              ))}
                            </div>
                            <span className="text-sm text-slate-500">
                              {userRating > 0 ? `${userRating}/5` : 'Select rating'}
                            </span>
                          </div>

                          <textarea
                            value={userReview}
                            onChange={(e) => setUserReview(e.target.value)}
                            placeholder="Write a review (optional)..."
                            className="w-full h-20 px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none"
                          />

                          <Button
                            size="sm"
                            disabled={userRating === 0 || isSubmittingRating}
                            onClick={handleSubmitRating}
                          >
                            {isSubmittingRating ? (
                              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                            ) : (
                              <Send className="w-4 h-4 mr-1" />
                            )}
                            Submit Rating
                          </Button>

                          {/* Reviews List */}
                          {ratings.length > 0 && (
                            <div className="space-y-3 mt-4">
                              <h5 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                                Recent Reviews
                              </h5>
                              {ratings.map((rating) => (
                                <Card key={rating.id} variant="outline" padding="sm">
                                  <div className="flex items-center justify-between mb-1">
                                    <div className="flex items-center gap-2">
                                      {renderStars(rating.rating)}
                                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                        {rating.user?.full_name || 'Anonymous'}
                                      </span>
                                    </div>
                                    <span className="text-xs text-slate-400">
                                      {new Date(rating.created_at).toLocaleDateString()}
                                    </span>
                                  </div>
                                  {rating.review && (
                                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                                      {rating.review}
                                    </p>
                                  )}
                                </Card>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* === PUBLISH VIEW === */}
                {viewMode === 'publish' && (
                  <motion.div
                    key="publish"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="flex-1 overflow-y-auto p-6"
                  >
                    <div className="max-w-2xl mx-auto space-y-5">
                      <button
                        onClick={() => setViewMode('gallery')}
                        className="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                      >
                        <ChevronLeft className="w-4 h-4" /> Back to marketplace
                      </button>

                      <div>
                        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                          <Sparkles className="w-5 h-5 text-blue-500" />
                          Publish a Template
                        </h2>
                        <p className="text-sm text-slate-500 mt-1">
                          Share your template with the community
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                          Template Name *
                        </label>
                        <Input
                          value={publishForm.name}
                          onChange={(e) => setPublishForm(prev => ({ ...prev, name: e.target.value }))}
                          placeholder="e.g., Professional Blog Template"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                          Description *
                        </label>
                        <textarea
                          value={publishForm.description}
                          onChange={(e) => setPublishForm(prev => ({ ...prev, description: e.target.value }))}
                          placeholder="Describe what this template is for..."
                          className="w-full h-20 px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                          Category
                        </label>
                        <select
                          value={publishForm.category}
                          onChange={(e) => setPublishForm(prev => ({ ...prev, category: e.target.value }))}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm"
                        >
                          {categories.map((cat) => (
                            <option key={cat.id} value={cat.id}>
                              {cat.icon} {cat.name}
                            </option>
                          ))}
                          {categories.length === 0 && (
                            <>
                              <option value="blog">📝 Blog Posts</option>
                              <option value="social">📱 Social Media</option>
                              <option value="newsletter">📧 Newsletters</option>
                              <option value="marketing">🎯 Marketing</option>
                              <option value="seo">🔍 SEO Content</option>
                              <option value="ecommerce">🛒 E-Commerce</option>
                              <option value="technical">⚙️ Technical Writing</option>
                              <option value="creative">🎨 Creative Writing</option>
                            </>
                          )}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                          Template Content *
                        </label>
                        <textarea
                          value={publishForm.content}
                          onChange={(e) => setPublishForm(prev => ({ ...prev, content: e.target.value }))}
                          placeholder="Enter your template structure... Use [brackets] for variables"
                          className="w-full h-48 px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 font-mono resize-none"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                            Tags (comma separated)
                          </label>
                          <Input
                            value={publishForm.tags}
                            onChange={(e) => setPublishForm(prev => ({ ...prev, tags: e.target.value }))}
                            placeholder="e.g., tutorial, marketing, b2b"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                            Platforms (comma separated)
                          </label>
                          <Input
                            value={publishForm.platforms}
                            onChange={(e) => setPublishForm(prev => ({ ...prev, platforms: e.target.value }))}
                            placeholder="e.g., blog, twitter, linkedin"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                          Version
                        </label>
                        <Input
                          value={publishForm.version}
                          onChange={(e) => setPublishForm(prev => ({ ...prev, version: e.target.value }))}
                          placeholder="1.0.0"
                        />
                      </div>

                      <div className="flex gap-3 pt-2">
                        <Button variant="secondary" onClick={() => setViewMode('gallery')} className="flex-1">
                          Cancel
                        </Button>
                        <Button onClick={handlePublish} disabled={isPublishing} className="flex-1">
                          {isPublishing ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <ExternalLink className="w-4 h-4 mr-2" />
                          )}
                          {isPublishing ? 'Publishing...' : 'Publish Template'}
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}