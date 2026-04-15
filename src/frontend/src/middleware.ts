import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

const APP_ENV = process.env.NEXT_PUBLIC_APP_ENV || 'production'
const isStaging = APP_ENV === 'staging'

const PUBLIC_ROUTES = ['/login', '/sso', '/api/auth', '/api/health', '/api/v1', '/legal', '/onboarding']
const STATIC_PREFIXES = ['/_next', '/static', '/favicon', '/robots', '/sitemap', '/opengraph-image']

function isPublicRoute(pathname: string): boolean {
  if (PUBLIC_ROUTES.some(route => pathname.startsWith(route))) return true
  if (STATIC_PREFIXES.some(prefix => pathname.startsWith(prefix))) return true
  if (pathname === '/' && !isStaging) return true
  if (!isStaging) {
    if (['/', '/pricing', '/about', '/contact'].includes(pathname)) return true
  }
  return false
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  let response = NextResponse.next()

  if (isStaging) {
    response.headers.set('X-Robots-Tag', 'noindex, nofollow, nosnippet, noarchive')

    if (!isPublicRoute(pathname)) {
      // Log all cookies for debugging
      const allCookies = request.cookies.getAll()
      const cookieNames = allCookies.map(c => c.name)
      console.log(`[MW] ${pathname} | cookies: ${cookieNames.join(', ') || 'NONE'}`)

      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

      if (!supabaseUrl || !supabaseKey) {
        console.log(`[MW] Missing env vars: URL=${!!supabaseUrl} KEY=${!!supabaseKey}`)
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set('redirectTo', pathname)
        return NextResponse.redirect(loginUrl)
      }

      try {
        const supabase = createServerClient(supabaseUrl, supabaseKey, {
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
        })

        const { data, error } = await supabase.auth.getUser()
        console.log(`[MW] getUser result: user=${!!data.user} error=${error?.message || 'none'}`)

        if (!data.user) {
          const loginUrl = new URL('/login', request.url)
          loginUrl.searchParams.set('redirectTo', pathname)
          return NextResponse.redirect(loginUrl)
        }
      } catch (err) {
        console.log(`[MW] Exception: ${err}`)
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