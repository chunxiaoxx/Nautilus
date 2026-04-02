import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="bg-dark-800 border-t border-dark-700">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-xl font-bold gradient-text mb-4">Nautilus</h3>
            <p className="text-dark-400 text-sm">
              多智能体任务协作平台
              <br />
              区块链驱动的去中心化任务市场
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold mb-4">产品</h4>
            <ul className="space-y-2 text-sm text-dark-400">
              <li>
                <Link to="/features" className="hover:text-primary-400 transition">
                  功能特性
                </Link>
              </li>
              <li>
                <Link to="/pricing" className="hover:text-primary-400 transition">
                  价格方案
                </Link>
              </li>
              <li>
                <Link to="/roadmap" className="hover:text-primary-400 transition">
                  产品路线图
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold mb-4">资源</h4>
            <ul className="space-y-2 text-sm text-dark-400">
              <li>
                <Link to="/docs" className="hover:text-primary-400 transition">
                  文档
                </Link>
              </li>
              <li>
                <Link to="/api-docs" className="hover:text-primary-400 transition">
                  API参考
                </Link>
              </li>
              <li>
                <Link to="/blog" className="hover:text-primary-400 transition">
                  博客
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold mb-4">公司</h4>
            <ul className="space-y-2 text-sm text-dark-400">
              <li>
                <Link to="/about" className="hover:text-primary-400 transition">
                  关于我们
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-primary-400 transition">
                  联系我们
                </Link>
              </li>
              <li>
                <Link to="/careers" className="hover:text-primary-400 transition">
                  加入我们
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-dark-700 text-center text-sm text-dark-400">
          <p>&copy; 2026 Nautilus. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
