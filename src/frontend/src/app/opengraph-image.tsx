import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'ContentForge AI Dashboard'
export const size = {
  width: 1200,
  height: 630,
}

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: '#f9fafb',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          padding: '40px',
        }}
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '32px',
          }}
        >
          <span
            style={{
              fontSize: '32px',
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
              backgroundClip: 'text',
              color: 'transparent',
            }}
          >
            ContentForge
          </span>
        </div>

        <div style={{ display: 'flex', gap: '24px', flex: 1 }}>
          {/* Sidebar */}
          <div
            style={{
              width: '240px',
              background: 'white',
              borderRadius: '12px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            {['Content', 'Projects', 'Distributions', 'Analytics', 'Settings'].map((item, i) => (
              <div
                key={item}
                style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background: i === 0 ? '#eff6ff' : 'transparent',
                  color: i === 0 ? '#3b82f6' : '#374151',
                  fontWeight: i === 0 ? '600' : '400',
                }}
              >
                {item}
              </div>
            ))}
          </div>

          {/* Main Content */}
          <div
            style={{
              flex: 1,
              background: 'white',
              borderRadius: '12px',
              padding: '32px',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '24px',
              }}
            >
              <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
                Your Content
              </h2>
              <div
                style={{
                  background: '#3b82f6',
                  color: 'white',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                }}
              >
                + New Content
              </div>
            </div>

            {/* Content Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {[
                { title: 'Blog Post: AI Trends', status: 'completed', date: 'Apr 11, 2025' },
                { title: 'Product Documentation', status: 'processing', date: 'Apr 10, 2025' },
                { title: 'Social Media Campaign', status: 'pending', date: 'Apr 9, 2025' },
              ].map((item) => (
                <div
                  key={item.title}
                  style={{
                    border: '1px solid #e5e7eb',
                    borderRadius: '12px',
                    padding: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                  }}
                >
                  <div
                    style={{
                      width: '40px',
                      height: '40px',
                      background: '#dbeafe',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    📄
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                      {item.title}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                      {item.date}
                    </div>
                  </div>
                  <span
                    style={{
                      padding: '4px 12px',
                      borderRadius: '9999px',
                      fontSize: '12px',
                      fontWeight: '500',
                      background:
                        item.status === 'completed'
                          ? '#dcfce7'
                          : item.status === 'processing'
                          ? '#dbeafe'
                          : '#fef3c7',
                      color:
                        item.status === 'completed'
                          ? '#166534'
                          : item.status === 'processing'
                          ? '#1e40af'
                          : '#92400e',
                    }}
                  >
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  )
}
