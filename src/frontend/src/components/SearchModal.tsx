'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { searchContent, getSearchSuggestions, SearchResult, SearchSuggestion } from '@/lib/api'
import { useToast } from '@/hooks/useToast'
import { getRecentSearches, saveRecentSearch, fuzzyMatch, cn } from '@/lib/utils'
import { 
  Search, 
  X, 
  FileText, 
  FolderOpen, 
  Loader2,
  ArrowRight,
  Clock,
  BarChart3,
  Trash2,
} from 'lucide-react'
import Link from 'next/link'

type SearchCategory = 'all' | 'content' | 'projects' | 'analytics'

interface SearchModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const { showToast } = useToast()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [recentSearches, setRecentSearches] = useState<string[]>([])
  const [category, setCategory] = useState<SearchCategory>('all')
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  // Load recent searches on open
  useEffect(() => {
    if (isOpen) {
      setRecentSearches(getRecentSearches())
      setTimeout(() => inputRef.current?.focus(), 100)
      setSelectedIndex(-1)
    }
  }, [isOpen])

  // Handle keyboard shortcuts within modal
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
        return
      }

      // Arrow key navigation
      const allItems = getVisibleItems()
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(prev => Math.min(prev + 1, allItems.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(prev => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter' && selectedIndex >= 0 && allItems[selectedIndex]) {
        e.preventDefault()
        const item = allItems[selectedIndex]
        if (item.type === 'recent') {
          setQuery(item.text)
        } else if (item.result) {
          saveRecentSearch(query)
          onClose()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose, selectedIndex, query])

  // Get all visible items for keyboard navigation
  const getVisibleItems = useCallback(() => {
    const items: Array<{ type: 'recent' | 'suggestion' | 'result'; text: string; result?: SearchResult }> = []
    
    if (!query && recentSearches.length > 0) {
      recentSearches.forEach(s => items.push({ type: 'recent', text: s }))
    }
    
    if (suggestions.length > 0 && results.length === 0 && !loading) {
      suggestions.forEach(s => items.push({ type: 'suggestion', text: s.text }))
    }
    
    if (results.length > 0) {
      results.forEach(r => items.push({ type: 'result', text: r.title, result: r }))
    }
    
    return items
  }, [query, recentSearches, suggestions, results, loading])

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) {
      setSuggestions([])
      return
    }

    try {
      const data = await getSearchSuggestions(q)
      setSuggestions(data.suggestions)
    } catch (error) {
      console.error('Failed to get suggestions:', error)
    }
  }, [])

  const performSearch = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([])
      setTotal(0)
      return
    }

    setLoading(true)
    try {
      const data = await searchContent(q, { limit: 20 })
      let filtered = data.results
      
      // Client-side category filter
      if (category !== 'all') {
        filtered = filtered.filter(r => r.type === category.slice(0, -1)) // 'content' -> 'content', 'projects' -> 'project'
      }

      // Apply fuzzy search enhancement
      if (q.length >= 2) {
        filtered = filtered.filter(r =>
          fuzzyMatch(q, r.title) || (r.matched_text && fuzzyMatch(q, r.matched_text))
        )
      }

      setResults(filtered)
      setTotal(data.total)
      setSuggestions([])
    } catch (error) {
      console.error('Search failed:', error)
      showToast('Search failed', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast, category])

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    if (query.length >= 2) {
      debounceRef.current = setTimeout(() => {
        performSearch(query)
      }, 300)
    } else {
      setResults([])
      setTotal(0)
    }

    fetchSuggestions(query)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query, performSearch, fetchSuggestions])

  const clearRecentSearches = () => {
    localStorage.removeItem('contentforge-recent-searches')
    setRecentSearches([])
  }

  const getItemIcon = (type: string) => {
    switch (type) {
      case 'content':
        return <FileText className="h-5 w-5 text-blue-500" />
      case 'project':
        return <FolderOpen className="h-5 w-5 text-purple-500" />
      case 'analytics':
        return <BarChart3 className="h-5 w-5 text-emerald-500" />
      default:
        return <FileText className="h-5 w-5 text-slate-500 dark:text-slate-400" />
    }
  }

  const getItemLink = (result: SearchResult) => {
    switch (result.type) {
      case 'content':
        return `/content/${result.id}`
      case 'project':
        return `/projects/${result.id}`
      default:
        return '#'
    }
  }

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text
    const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'))
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200 dark:bg-yellow-500/30 text-slate-900 dark:text-slate-100 rounded px-0.5">{part}</mark>
      ) : (
        part
      )
    )
  }

  const CATEGORIES: { value: SearchCategory; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'content', label: 'Content' },
    { value: 'projects', label: 'Projects' },
    { value: 'analytics', label: 'Analytics' },
  ]

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-start justify-center z-50 pt-[10vh]">
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden border border-slate-200 dark:border-slate-700">
        {/* Search Input */}
        <div className="border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3 px-4 py-4">
            <Search className="h-5 w-5 text-slate-400 dark:text-slate-500 flex-shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setSelectedIndex(-1)
              }}
              placeholder="Search content, projects, analytics..."
              className="flex-1 text-lg outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 bg-transparent"
            />
            {loading && <Loader2 className="h-5 w-5 text-slate-400 dark:text-slate-500 animate-spin flex-shrink-0" />}
            {!loading && query && (
              <button
                onClick={() => { setQuery(''); setResults([]); setTotal(0); }}
                className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors"
              >
                <X className="h-5 w-5 text-slate-400 dark:text-slate-500" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-slate-400 dark:text-slate-500" />
            </button>
          </div>

          {/* Category filters */}
          <div className="flex items-center gap-1 px-4 pb-3">
            {CATEGORIES.map(cat => (
              <button
                key={cat.value}
                onClick={() => { setCategory(cat.value); setSelectedIndex(-1) }}
                className={cn(
                  'px-3 py-1.5 text-xs font-medium rounded-full transition-all',
                  category === cat.value
                    ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300'
                    : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                )}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto">
          {/* Recent Searches (show when no query) */}
          {!query && recentSearches.length > 0 && (
            <div className="py-2">
              <div className="flex items-center justify-between px-4 py-2">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  Recent searches
                </span>
                <button
                  onClick={clearRecentSearches}
                  className="text-xs text-slate-400 dark:text-slate-500 hover:text-red-500 dark:hover:text-red-400 flex items-center gap-1"
                >
                  <Trash2 className="w-3 h-3" />
                  Clear
                </button>
              </div>
              {recentSearches.map((search, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(search)}
                  className={cn(
                    'w-full px-4 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors',
                    selectedIndex === index && 'bg-slate-50 dark:bg-slate-800'
                  )}
                >
                  <Clock className="h-4 w-4 text-slate-300 dark:text-slate-600" />
                  <span className="text-slate-700 dark:text-slate-300">{search}</span>
                </button>
              ))}
            </div>
          )}

          {/* Suggestions */}
          {suggestions.length > 0 && results.length === 0 && !loading && (
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">
                Suggestions
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion.text)}
                  className={cn(
                    'w-full px-4 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors',
                    selectedIndex === (recentSearches.length > 0 ? -1 : index) + index && 'bg-slate-50 dark:bg-slate-800'
                  )}
                >
                  <Search className="h-4 w-4 text-slate-400 dark:text-slate-500" />
                  <span className="text-slate-700 dark:text-slate-300">{highlightMatch(suggestion.text, query)}</span>
                  <span className="text-xs text-slate-400 dark:text-slate-500 capitalize ml-auto">{suggestion.type}</span>
                </button>
              ))}
            </div>
          )}

          {/* No Results */}
          {query.length >= 2 && !loading && results.length === 0 && suggestions.length === 0 && (
            <div className="py-12 text-center">
              <div className="mx-auto w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-3">
                <Search className="h-6 w-6 text-slate-400 dark:text-slate-500" />
              </div>
              <p className="text-slate-600 dark:text-slate-400">No results found for &quot;{query}&quot;</p>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Try different keywords or check your spelling</p>
            </div>
          )}

          {/* Search Results */}
          {results.length > 0 && (
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">
                {total} result{total !== 1 ? 's' : ''} found
                {category !== 'all' && <span className="ml-1 normal-case">in {category}</span>}
              </div>
              
              {results.map((result, index) => (
                <Link
                  key={result.id}
                  href={getItemLink(result)}
                  onClick={() => {
                    saveRecentSearch(query)
                    onClose()
                  }}
                  className={cn(
                    'flex items-start gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group',
                    selectedIndex === index && 'bg-slate-50 dark:bg-slate-800'
                  )}
                >
                  <div className="flex-shrink-0 mt-0.5">
                    {getItemIcon(result.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-slate-900 dark:text-slate-100 truncate">
                        {highlightMatch(result.title, query)}
                      </h4>
                      <span className="text-xs text-slate-400 dark:text-slate-500 capitalize">
                        {result.type}
                      </span>
                    </div>
                    
                    {result.matched_text && (
                      <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5 line-clamp-2">
                        {highlightMatch(result.matched_text, query)}
                      </p>
                    )}
                    
                    {result.project_name && (
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        in {result.project_name}
                      </p>
                    )}
                  </div>
                  
                  <ArrowRight className="h-4 w-4 text-slate-300 dark:text-slate-600 group-hover:text-slate-500 dark:group-hover:text-slate-400 flex-shrink-0" />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 dark:border-slate-700 px-4 py-3 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-4">
            <span>Use <kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded text-slate-600 dark:text-slate-300">↑</kbd> <kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded text-slate-600 dark:text-slate-300">↓</kbd> to navigate</span>
            <span><kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded text-slate-600 dark:text-slate-300">Enter</kbd> to select</span>
          </div>
          <span><kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded text-slate-600 dark:text-slate-300">Esc</kbd> to close</span>
        </div>
      </div>
    </div>
  )
}