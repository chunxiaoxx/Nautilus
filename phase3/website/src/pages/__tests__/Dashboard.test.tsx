import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import Dashboard from '../Dashboard'
import * as useAuthHook from '../../hooks/useAuth'

// Mock useAuth hook
vi.mock('../../hooks/useAuth', () => ({
  useAuthCheck: vi.fn()
}))

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render welcome message with user email', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      createdAt: '2024-01-01T00:00:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    render(<Dashboard />)

    expect(screen.getByText(/欢迎回来, test@example.com/)).toBeInTheDocument()
  })

  it('should display user ID', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      createdAt: '2024-01-01T00:00:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    render(<Dashboard />)

    expect(screen.getByText('用户 ID')).toBeInTheDocument()
    expect(screen.getByText('123')).toBeInTheDocument()
  })

  it('should display user email in details', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
    createdAt: '2024-01-01T00:00:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    render(<Dashboard />)

    expect(screen.getByText('邮箱')).toBeInTheDocument()
    const emailElements = screen.getAllByText('test@example.com')
    expect(emailElements.length).toBeGreaterThanOrEqual(1)
  })

  it('should display wallet address when available', () => {
    const mockUser = {
   id: '123',
      email: 'test@example.com',
      username: 'testuser',
      walletAddress: '0x1234567890abcdef',
      createdAt: '2024-01-01T00:00:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    render(<Dashboard />)

    expect(screen.getByText('钱包地址')).toBeInTheDocument()
    expect(screen.getByText('0x1234567890abcdef')).toBeInTheDocument()
  })

  it('should not display wallet address when not available', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      createdAt: '2024-01-01T00:00:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    render(<Dashboard />)

    expect(screen.queryByText('钱包地址')).not.toBeInTheDocument()
  })

  it('should display registration date', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      createdAt: '2024-01-15T10:30:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    render(<Dashboard />)

    expect(screen.getByText('注册时间')).toBeInTheDocument()
    const dateElement = screen.getByText(/2024/)
    expect(dateElement).toBeInTheDocument()
  })

  it('should handle null user gracefully', () => {
    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false
    })

    render(<Dashboard />)

    expect(screen.getByText(/欢迎回来,/)).toBeInTheDocument()
  })

  it('should render user info grid layout', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      createdAt: '2024-01-01T00:00:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    const { container } = render(<Dashboard />)

    const grid = container.querySelector('.grid')
    expect(grid).toBeInTheDocument()
  })

  it('should format wallet address with monospace font', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      walletAddress: '0x1234567890abcdef',
      createdAt: '2024-01-01T00:00:00.000Z'
    }

    vi.mocked(useAuthHook.useAuthCheck).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false
    })

    render(<Dashboard />)

    const walletElement = screen.getByText('0x1234567890abcdef')
    expect(walletElement).toHaveClass('font-mono')
  })
})
