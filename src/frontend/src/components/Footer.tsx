'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Cookie } from 'lucide-react'

export default function Footer() {
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  const currentYear = new Date().getFullYear()
  
  if (!mounted) return null
  
  return (
    <footer className="border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Copyright */}
          <p className="text-sm text-slate-500 dark:text-slate-400">
            © {currentYear} ContentForge AI. All rights reserved.
          </p>
          
          {/* Legal Links */}
          <nav className="flex flex-wrap items-center justify-center gap-6 text-sm">
            <Link 
              href="/legal/terms" 
              className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 transition-colors"
            >
              Terms of Service
            </Link>
            <Link 
              href="/legal/privacy" 
              className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 transition-colors"
            >
              Privacy Policy
            </Link>
            <Link 
              href="/legal/cookies" 
              className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 transition-colors flex items-center gap-1"
            >
              <Cookie className="h-3 w-3" />
              Cookie Policy
            </Link>
            <Link 
              href="/legal/dmca" 
              className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 transition-colors"
            >
              DMCA Notice
            </Link>
          </nav>
        </div>
      </div>
    </footer>
  )
}
