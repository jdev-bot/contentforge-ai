import { NextResponse } from 'next/server'

/**
 * Dynamic robots.txt generation.
 * 
 * Staging: Blocks all search engine indexing
 * Production: Allows indexing (with sensible defaults)
 */
export function GET() {
  const APP_ENV = process.env.NEXT_PUBLIC_APP_ENV || 'production'
  const isStaging = APP_ENV === 'staging'

  const stagingRobots = `# ContentForge AI - Staging Environment
# DO NOT INDEX - This is a private staging environment
User-agent: *
Disallow: /

User-agent: Googlebot
Disallow: /

User-agent: Bingbot
Disallow: /

User-agent: Slurp
Disallow: /

User-agent: DuckDuckBot
Disallow: /

User-agent: Baiduspider
Disallow: /

User-agent: YandexBot
Disallow: /
`

  const productionRobots = `# ContentForge AI
User-agent: *
Allow: /
Disallow: /api/
Disallow: /settings
Disallow: /admin
Disallow: /billing
Disallow: /*/edit

Sitemap: https://contentforge.ai/sitemap.xml
`

  const content = isStaging ? stagingRobots : productionRobots

  return new NextResponse(content, {
    headers: {
      'Content-Type': 'text/plain',
      'Cache-Control': isStaging
        ? 'no-store, no-cache'
        : 'public, max-age=86400',
    },
  })
}