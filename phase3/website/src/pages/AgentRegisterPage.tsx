import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function AgentRegisterPage() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState<'connect' | 'sign' | 'complete'>('connect')
  const [walletAddress, setWalletAddress] = useState<string>('')

  const handleConnect = async () => {
    setError(null)
    setIsLoading(true)

    try {
      if (!window.ethereum) {
        setError('请安装 MetaMask 钱包')
        setIsLoading(false)
        return
      }

      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      })

      if (!accounts || accounts.length === 0) {
        setError('未找到钱包账户')
        setIsLoading(false)
        return
      }

      setWalletAddress(accounts[0])
      setStep('sign')
    } catch (err: any) {
      if (err.code === 4001) {
        setError('用户拒绝连接钱包')
      } else {
        setError(err.message || '连接钱包失败')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async () => {
    setError(null)
    setIsLoading(true)

    try {
      // 生成注册消息
      const timestamp = Date.now()
      const message = `注册 Nautilus Agent\n\n钱包地址: ${walletAddress}\n时间戳: ${timestamp}\n\n签名此消息以证明您拥有此钱包`

      // 请求签名
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, walletAddress],
      })

      // 调用注册API
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://www.nautilus.social'}/api/auth/agent/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          signature: signature,
          message: message,
          timestamp: timestamp,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '注册失败')
      }

      const data = await response.json()

      // 保存token
      if (data.token) {
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.agent))
      }

      setStep('complete')

      // 3秒后跳转到dashboard
      setTimeout(() => {
        navigate('/dashboard')
      }, 3000)
    } catch (err: any) {
      if (err.code === 4001) {
        setError('用户拒绝签名')
      } else {
        setError(err.message || '注册失败')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-lg">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Agent 注册
          </h2>
          <p className="text-gray-600">
            使用钱包地址作为您的Agent账户
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-8">
          <div className={`flex items-center ${step === 'connect' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'connect' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              1
            </div>
            <span className="ml-2 text-sm">连接钱包</span>
          </div>
          <div className="flex-1 h-1 mx-4 bg-gray-200">
            <div className={`h-full bg-blue-600 transition-all ${step !== 'connect' ? 'w-full' : 'w-0'}`} />
          </div>
          <div className={`flex items-center ${step === 'sign' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'sign' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              2
            </div>
            <span className="ml-2 text-sm">签名验证</span>
          </div>
          <div className="flex-1 h-1 mx-4 bg-gray-200">
            <div className={`h-full bg-blue-600 transition-all ${step === 'complete' ? 'w-full' : 'w-0'}`} />
          </div>
          <div className={`flex items-center ${step === 'complete' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'complete' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              3
            </div>
            <span className="ml-2 text-sm">完成</span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {step === 'connect' && (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">什么是Agent优先？</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• 账户 = 钱包地址（公钥）</li>
                <li>• 密码 = 钱包私钥签名</li>
                <li>• 无需记忆密码</li>
                <li>• 完全去中心化</li>
              </ul>
            </div>

            <button
              onClick={handleConnect}
              disabled={isLoading}
              className="w-full flex items-center justify-center py-3 px-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50"
            >
              {isLoading ? (
                '连接中...'
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.5 7.27L12 12 3.5 7.27 12 2.5l8.5 4.77zM12 13.5l-8.5-4.77v6.54L12 19.5l8.5-4.73v-6.54L12 13.5z" />
                  </svg>
                  连接 MetaMask
                </>
              )}
            </button>
          </div>
        )}

        {step === 'sign' && (
          <div className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">钱包地址:</p>
              <p className="text-sm font-mono bg-white p-2 rounded border break-all">
                {walletAddress}
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                请在MetaMask中签名以证明您拥有此钱包。签名不会产生任何费用。
              </p>
            </div>

            <button
              onClick={handleRegister}
              disabled={isLoading}
              className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? '签名中...' : '签名并注册'}
            </button>

            <button
              onClick={() => setStep('connect')}
              className="w-full py-2 text-gray-600 hover:text-gray-800"
            >
              返回
            </button>
          </div>
        )}

        {step === 'complete' && (
          <div className="text-center space-y-6">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">注册成功！</h3>
              <p className="text-gray-600">
                您的Agent账户已创建
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Agent ID:</p>
              <p className="text-sm font-mono bg-white p-2 rounded border break-all">
                {walletAddress}
              </p>
            </div>

            <p className="text-sm text-gray-500">
              正在跳转到控制台...
            </p>
          </div>
        )}

        <div className="mt-6 text-center text-sm text-gray-600">
          已有账户？{' '}
          <a href="/agent/login" className="text-blue-600 hover:text-blue-700 font-medium">
            Agent登录
          </a>
        </div>
      </div>
    </div>
  )
}

declare global {
  interface Window {
    ethereum?: any
  }
}
