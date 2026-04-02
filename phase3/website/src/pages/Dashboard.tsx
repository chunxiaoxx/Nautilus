import { useAuthCheck } from '../hooks/useAuth'

const Dashboard = () => {
  const { user } = useAuthCheck()

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            欢迎回来, {user?.email}
          </h1>
          <div className="border-t border-gray-200 pt-4">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">用户 ID</dt>
                <dd className="mt-1 text-sm text-gray-900">{user?.id}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">邮箱</dt>
                <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
              </div>
              {user?.walletAddress && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">钱包地址</dt>
                  <dd className="mt-1 text-sm text-gray-900 font-mono">
                    {user.walletAddress}
                  </dd>
                </div>
              )}
              <div>
                <dt className="text-sm font-medium text-gray-500">注册时间</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(user?.createdAt || '').toLocaleDateString('zh-CN')}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
