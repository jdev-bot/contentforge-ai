import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'ContentForge AI Login'
export const size = {
  width: 1200,
  height: 630,
}

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px',
        }}
      >
        <div
          style={{
            background: 'white',
            borderRadius: '16px',
            padding: '40px 60px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            minWidth: '500px',
          }}
        >
          <h1
            style={{
              fontSize: '48px',
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
              backgroundClip: 'text',
              color: 'transparent',
              margin: '0 0 16px 0',
            }}
          >
            ContentForge
          </h1>
          <p
            style={{
              fontSize: '24px',
              color: '#6b7280',
              margin: '0',
            }}
          >
            Transform Your Content with AI
          </p>
          <div
            style={{
              marginTop: '32px',
              padding: '16px 32px',
              background: '#3b82f6',
              color: 'white',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: '500',
            }}
          >
            Sign In to Continue
          </div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  )
}
