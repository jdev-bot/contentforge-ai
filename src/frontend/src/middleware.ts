import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

const APP_ENV = process.env.NEXT_PUBLIC_APP_ENV || 'production'
const isStaging = APP_ENV === 'staging'

// Routes that are always accessible without authentication
const PUBLIC_ROUTES = [
  '/login',
  '/sso',
  '/api/auth',
  '/api/health',
  '/api/v1',
  '/legal',
  '/onboarding',
]

// Static asset prefixes that bypass auth
const STATIC_PREFIXES = [
  '/_next',
  '/static',
  '/favicon',
  '/robots',
  '/sitemap',
  '/opengraph-image',
]

function isPublicRoute(pathname: string): boolean {
  if (PUBLIC_ROUTES.some(route => pathname.startsWith(route))) return true
  if (STATIC_PREFIXES.some(prefix => pathname.startsWith(prefix))) return true
  if (pathname === '/' && !isStaging) return true
  if (!isStaging) {
    const productionPublicRoutes = ['/', '/pricing', '/about', '/contact']
    if (productionPublicRoutes.includes(pathname)) return true
  }
  return false
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  let response = NextResponse.next()

  // In staging, add noindex headers and check auth
  if (isStaging) {
    response.headers.set('X-Robots-Tag', 'noindex, nofollow, nosnippet, noarchive')

    if (!isPublicRoute(pathname)) {
      // Create a Supabase server client that reads cookies from the request
      const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
          cookies: {
            getAll() {
              return request.cookies.getAll()
            },
            setAll(cookiesToSet) {
              cookiesToSet.forEach(({ name, value, options }) => {
                request.cookies.set(name, value)
                response.cookies.set(name, value, options)
              })
            },
          },
        }
      )

      // Check if user is authenticated
      const { data: { user } } = await supabase.auth.getUser()

      if (!user) {
        // Redirect to login with return URL
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set('redirectTo', pathname)
        return NextResponse.redirect(loginUrl)
      }
    }
  }

  return response
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}