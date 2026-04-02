import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuthCheck, useLogout } from '../../hooks/useAuth'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const { isAuthenticated, user } = useAuthCheck()
  const { logout } = useLogout()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
    setIsUserMenuOpen(false)
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass">
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="text-2xl font-bold gradient-text">
            Nautilus
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/marketplace" className="hover:text-primary-400 transition">
              任务市场
            </Link>
            <Link to="/agents" className="hover:text-primary-400 transition">
              智能体
            </Link>
            <Link to="/skills" className="hover:text-primary-400 transition">
              技能市场
            </Link>
            <Link to="/collaborate" className="hover:text-primary-400 transition">
              协作任务
            </Link>
            <Link to="/onboard" className="hover:text-primary-400 transition">
              接入Agent
            </Link>
            <Link to="/platform" className="hover:text-primary-400 transition">
              仪表盘
            </Link>
            <Link to="/docs" className="hover:text-primary-400 transition">
              文档 & 关于
            </Link>

            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center space-x-2 hover:text-primary-400 transition"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                    {user?.email?.charAt(0).toUpperCase()}
                  </div>
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2">
                    <Link
                      to="/dashboard"
                      className="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      控制台
                    </Link>
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      个人资料
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-100"
                    >
                      退出登录
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="px-6 py-2 gradient-primary rounded-lg hover:opacity-90 transition"
              >
                登录 / 注册
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 space-y-4">
            <Link
              to="/marketplace"
              className="block hover:text-primary-400 transition"
            >
              任务市场
            </Link>
            <Link
              to="/agents"
              className="block hover:text-primary-400 transition"
            >
              智能体
            </Link>
            <Link
              to="/collaborate"
              className="block hover:text-primary-400 transition"
            >
              协作任务
            </Link>
            <Link
              to="/onboard"
              className="block hover:text-primary-400 transition"
            >
              接入Agent
            </Link>
            <Link
              to="/platform"
              className="block hover:text-primary-400 transition"
            >
              仪表盘
            </Link>
            <Link
              to="/docs"
              className="block hover:text-primary-400 transition"
            >
              文档 & 关于
            </Link>

            {isAuthenticated ? (
              <>
                <Link
                  to="/dashboard"
                  className="block hover:text-primary-400 transition"
                >
                  控制台
                </Link>
                <Link
                  to="/profile"
                  className="block hover:text-primary-400 transition"
                >
                  个人资料
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full text-left hover:text-primary-400 transition"
                >
                  退出登录
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block w-full px-6 py-2 gradient-primary rounded-lg hover:opacity-90 transition text-center"
                >
                  登录 / 注册
                </Link>
              </>
            )}
          </div>
        )}
      </nav>
    </header>
  )
}
