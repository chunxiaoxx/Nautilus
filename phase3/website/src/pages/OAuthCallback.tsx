import { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { tokenUtils } from '../utils/token'

/**
 * OAuth callback handler.
 * Receives token from backend after Google/GitHub OAuth,
 * saves it to localStorage, and redirects to home.
 */
const OAuthCallback = () => {
  const [params] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const token = params.get('token')
    if (token) {
      tokenUtils.save(token, true)
      navigate('/', { replace: true })
    } else {
      navigate('/login', { replace: true })
    }
  }, [params, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <p className="text-white">登录中...</p>
    </div>
  )
}

export default OAuthCallback
