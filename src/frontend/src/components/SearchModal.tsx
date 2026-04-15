'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { searchContent, getSearchSuggestions, SearchResult, SearchSuggestion } from '@/lib/api'
import { useToast } from '@/hooks/useToast'
import { 
  Search, 
  X, 
  FileText, 
  FolderOpen, 
  Loader2,
  ArrowRight
} from 'lucide-react'
import Link from 'next/link'

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
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        if (!isOpen) {
          // This would need to be passed from parent
        }
      }
      // Escape to close
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

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
      setResults(data.results)
      setTotal(data.total)
      setSuggestions([])
    } catch (error) {
      console.error('Search failed:', error)
      showToast('Search failed', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

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

    // Fetch suggestions immediately
    fetchSuggestions(query)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query, performSearch, fetchSuggestions])

  const getItemIcon = (type: string) => {
    switch (type) {
      case 'content':
        return <FileText className="h-5 w-5 text-blue-500" />
      case 'project':
        return <FolderOpen className="h-5 w-5 text-purple-500" />
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
    const parts = text.split(new RegExp(`(${query})`, 'gi'))
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200 text-slate-900 dark:text-slate-100 rounded px-0.5">{part}</mark>
      ) : (
        part
      )
    )
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center z-50 pt-[10vh]">
      <div className="bg-slate-50 dark:bg-slate-900 rounded-xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden">
        {/* Search Input */}
        <div className="border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3 px-4 py-4">
            <Search className="h-5 w-5 text-slate-400 dark:text-slate-500 flex-shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search content, projects..."
              className="flex-1 text-lg outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:text-slate-500"
            />
            {loading && <Loader2 className="h-5 w-5 text-slate-400 dark:text-slate-500 animate-spin flex-shrink-0" />}
            {!loading && query && (
              <button
                onClick={() => setQuery('')}
                className="p-1 hover:bg-slate-100 dark:bg-slate-800 rounded-full"
              >
                <X className="h-5 w-5 text-slate-400 dark:text-slate-500" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 hover:bg-slate-100 dark:bg-slate-800 rounded-full"
            >
              <X className="h-5 w-5 text-slate-400 dark:text-slate-500" />
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto">
          {/* Suggestions */}
          {suggestions.length > 0 && results.length === 0 && !loading && (
            <div className="py-2">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion.text)}
                  className="w-full px-4 py-2 text-left hover:bg-slate-50 dark:bg-slate-900 flex items-center gap-3"
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
              <p className="text-slate-600 dark:text-slate-400">No results found for {query}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Try different keywords or check your spelling</p>
            </div>
          )}

          {/* Search Results */}
          {results.length > 0 && (
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">
                {total} result{total !== 1 ? 's' : ''} found
              </div>
              
              {results.map((result) => (
                <Link
                  key={result.id}
                  href={getItemLink(result)}
                  onClick={onClose}
                  className="flex items-start gap-3 px-4 py-3 hover:bg-slate-50 dark:bg-slate-900 transition-colors group"
                
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
                  
                  <ArrowRight className="h-4 w-4 text-slate-300 dark:text-slate-600 group-hover:text-slate-500 dark:text-slate-400 flex-shrink-0" />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 dark:border-slate-700 px-4 py-3 bg-slate-50 dark:bg-slate-900 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-4">
            <span>Use <kbd className="px-1.5 py-0.5 bg-white border rounded text-slate-600 dark:text-slate-400">↑</kbd> <kbd className="px-1.5 py-0.5 bg-white border rounded text-slate-600 dark:text-slate-400">↓</kbd> to navigate</span>
            <span><kbd className="px-1.5 py-0.5 bg-white border rounded text-slate-600 dark:text-slate-400">Enter</kbd> to select</span>
          </div>
          <span><kbd className="px-1.5 py-0.5 bg-white border rounded text-slate-600 dark:text-slate-400">Esc</kbd> to close</span>
        </div>
      </div>
    </div>
  )
}
