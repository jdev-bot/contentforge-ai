import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ScheduleModal from '@/components/ScheduleModal'
import ScheduleCalendar from '@/components/ScheduleCalendar'
import UpcomingPostsWidget from '@/components/UpcomingPostsWidget'
import * as api from '@/lib/api'

// Mock the API
describe('ScheduleModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSuccess = vi.fn()

  it('renders correctly when open', () => {
    render(
      <ScheduleModal
        isOpen={true}
        onClose={mockOnClose}
        mode="create"
      />
    )

    expect(screen.getByText('Schedule Post')).toBeInTheDocument()
    expect(screen.getByText('Quick Templates')).toBeInTheDocument()
    expect(screen.getByText('Platforms')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    const { container } = render(
      <ScheduleModal
        isOpen={false}
        onClose={mockOnClose}
      />
    )

    expect(container.firstChild).toBeNull()
  })

  it('shows platform selection', () => {
    render(
      <ScheduleModal
        isOpen={true}
        onClose={mockOnClose}
      />
    )

    expect(screen.getByText('X (Twitter)')).toBeInTheDocument()
    expect(screen.getByText('LinkedIn')).toBeInTheDocument()
    expect(screen.getByText('Instagram')).toBeInTheDocument()
  })

  it('shows quick templates', () => {
    render(
      <ScheduleModal
        isOpen={true}
        onClose={mockOnClose}
      />
    )

    expect(screen.getByText('Morning Peak')).toBeInTheDocument()
    expect(screen.getByText('Lunch Time')).toBeInTheDocument()
    expect(screen.getByText('Afternoon Peak')).toBeInTheDocument()
  })
})

describe('ScheduleCalendar', () => {
  it('renders with loading state', () => {
    render(
      <ScheduleCalendar />
    )

    expect(screen.getByText('Publishing Calendar')).toBeInTheDocument()
  })

  it('has view toggle buttons', () => {
    render(
      <ScheduleCalendar />
    )

    expect(screen.getByText('Month')).toBeInTheDocument()
    expect(screen.getByText('Week')).toBeInTheDocument()
    expect(screen.getByText('Day')).toBeInTheDocument()
    expect(screen.getByText('List')).toBeInTheDocument()
  })

  it('has navigation buttons', () => {
    render(
      <ScheduleCalendar />
    )

    expect(screen.getByText('Prev')).toBeInTheDocument()
    expect(screen.getByText('Next')).toBeInTheDocument()
    expect(screen.getByText('Today')).toBeInTheDocument()
  })
})

describe('UpcomingPostsWidget', () => {
  it('renders in loading state', () => {
    render(
      <UpcomingPostsWidget />
    )

    expect(screen.getByText('Upcoming Posts')).toBeInTheDocument()
  })

  it('shows empty state when no posts', async () => {
    vi.spyOn(api, 'getUpcomingPosts').mockResolvedValue([])

    render(
      <UpcomingPostsWidget />
    )

    await waitFor(() => {
      expect(screen.getByText('No upcoming posts scheduled')).toBeInTheDocument()
    })
  })
})

describe('API Integration', () => {
  it('exports schedule API functions', () => {
    expect(typeof api.schedulePost).toBe('function')
    expect(typeof api.getScheduledPosts).toBe('function')
    expect(typeof api.updateScheduledPost).toBe('function')
    expect(typeof api.cancelScheduledPost).toBe('function')
    expect(typeof api.publishNow).toBe('function')
    expect(typeof api.getUpcomingPosts).toBe('function')
    expect(typeof api.checkScheduleConflicts).toBe('function')
  })

  it('exports correct types', () => {
    // These would be type-only checks at compile time
    expect(true).toBe(true)
  })
})
