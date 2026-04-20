import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Get status color classes for a given status string.
 * Centralized to avoid duplicate color logic across components.
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-300',
    processing: 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300',
    completed: 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300',
    failed: 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300',
    published: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
    scheduled: 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300',
    cancelled: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
    approved: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
    rejected: 'bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300',
    generated: 'bg-violet-100 text-violet-700 dark:bg-violet-500/20 dark:text-violet-300',
    active: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
    inactive: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  }
  return colors[status] || 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
}

/**
 * Get a status dot color class (small colored circle indicator).
 */
export function getStatusDotColor(status: string): string {
  const dots: Record<string, string> = {
    pending: 'bg-yellow-500',
    processing: 'bg-blue-500 animate-pulse',
    completed: 'bg-emerald-500',
    failed: 'bg-red-500',
    published: 'bg-emerald-500',
    scheduled: 'bg-blue-500',
    cancelled: 'bg-slate-400',
    approved: 'bg-emerald-500',
    rejected: 'bg-rose-500',
    generated: 'bg-violet-500',
    active: 'bg-emerald-500',
    inactive: 'bg-slate-400',
  }
  return dots[status] || 'bg-slate-400'
}

/**
 * Format a date string into a human-readable format.
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Format a date string with relative time (e.g., "2 hours ago").
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  if (diffHour < 24) return `${diffHour}h ago`
  if (diffDay < 7) return `${diffDay}d ago`
  return formatDate(dateString)
}

/**
 * Simple fuzzy search: returns true if all characters in the query
 * appear in the target in order (not necessarily contiguous).
 */
export function fuzzyMatch(query: string, target: string): boolean {
  const q = query.toLowerCase()
  const t = target.toLowerCase()
  let qi = 0
  for (let ti = 0; ti < t.length && qi < q.length; ti++) {
    if (t[ti] === q[qi]) qi++
  }
  return qi === q.length
}

/**
 * Pinned tabs localStorage key.
 */
export const PINNED_TABS_KEY = 'contentforge-pinned-tabs'
export const RECENT_SEARCHES_KEY = 'contentforge-recent-searches'

/**
 * Get pinned tabs from localStorage.
 */
export function getPinnedTabs(): string[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem(PINNED_TABS_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

/**
 * Save pinned tabs to localStorage.
 */
export function savePinnedTabs(tabs: string[]): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(PINNED_TABS_KEY, JSON.stringify(tabs))
  }
  catch {
    // Ignore storage errors
  }
}

/**
 * Track tab usage — increment a counter stored in localStorage.
 */
export function trackTabUsage(tabId: string): void {
  if (typeof window === 'undefined') return
  try {
    const stored = localStorage.getItem('contentforge-tab-usage')
    const usage: Record<string, number> = stored ? JSON.parse(stored) : {}
    usage[tabId] = (usage[tabId] || 0) + 1
    localStorage.setItem('contentforge-tab-usage', JSON.stringify(usage))
  } catch {
    // Ignore
  }
}

/**
 * Get most-used tabs sorted by usage count.
 */
export function getMostUsedTabs(limit = 5): string[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem('contentforge-tab-usage')
    const usage: Record<string, number> = stored ? JSON.parse(stored) : {}
    return Object.entries(usage)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([id]) => id)
  } catch {
    return []
  }
}

/**
 * Get recent searches from localStorage.
 */
export function getRecentSearches(): string[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

/**
 * Save a recent search to localStorage (deduped, max 10).
 */
export function saveRecentSearch(query: string): void {
  if (typeof window === 'undefined' || !query.trim()) return
  try {
    const searches = getRecentSearches().filter(s => s !== query)
    searches.unshift(query)
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(searches.slice(0, 10)))
  } catch {
    // Ignore
  }
}
