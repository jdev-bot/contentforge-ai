import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Next.js middleware for environment-driven behavior.
 * 
 * When NEXT_PUBLIC_APP_ENV=staging:
 * - Redirects unauthenticated users to /login (except auth pages and static assets)
 * - Blocks search engine indexing via X-Robots-Tag header
 * 
 * When NEXT_PUBLIC_APP_ENV=production (or unset):
 * - Allows public access to landing, pricing, and login pages
 * - No auth gate on public routes
 */

const APP_ENV = process.env.NEXT_PUBLIC_APP_ENV || 'production'
const isStaging = APP_ENV === 'staging'

// Routes that are always accessible without authentication
const PUBLIC_ROUTES = [
  '/login',
  '/sso',
  '/api/auth',
  '/api/health',
]

// Static asset prefixes that bypass auth
const STATIC_PREFIXES = [
  '/_next',
  '/static',
  '/favicon',
  '/robots',
  '/sitemap',
]

function isPublicRoute(pathname: string): boolean {
  // Check exact public routes
  if (PUBLIC_ROUTES.some(route => pathname.startsWith(route))) {
    return true
  }

  // Check static assets
  if (STATIC_PREFIXES.some(prefix => pathname.startsWith(prefix))) {
    return true
  }

  // Root path - public in production, gated in staging
  if (pathname === '/' && !isStaging) {
    return true
  }

  // In production, these pages are public
  if (!isStaging) {
    const productionPublicRoutes = ['/', '/pricing', '/about', '/contact']
    if (productionPublicRoutes.includes(pathname)) {
      return true
    }
  }

  return false
}

export function middleware(request: NextRequest) {
  const response = NextResponse.next()
  const { pathname } = request.nextUrl

  // Add staging-specific headers
  if (isStaging) {
    // Prevent search engine indexing
    response.headers.set('X-Robots-Tag', 'noindex, nofollow, nosnippet, noarchive')
  }

  // In staging, require authentication for all non-public routes
  if (isStaging && !isPublicRoute(pathname)) {
    // Check for Supabase auth cookie
    const authCookie = request.cookies.getAll().find(
      cookie => cookie.name.startsWith('sb-') && cookie.name.includes('-auth-token')
    )

    if (!authCookie) {
      // Redirect to login with return URL
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirectTo', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}