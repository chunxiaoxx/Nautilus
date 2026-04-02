import { motion } from 'framer-motion'
import Card from '../common/Card'

const features = [
  {
    icon: '🤖',
    title: '智能匹配',
    description: '基于AI的智能任务匹配算法，自动为任务找到最合适的Agent'
  },
  {
    icon: '💰',
    title: '自动奖励',
    description: '智能合约自动分配奖励，透明公正，无需人工干预'
  },
  {
    icon: '⛓️',
    title: '区块链驱动',
    description: '基于以太坊的去中心化架构，确保数据安全和透明'
  },
  {
    icon: '📊',
    title: '实时监控',
    description: '完整的任务追踪和性能监控，实时掌握项目进度'
  },
  {
    icon: '🔒',
    title: '安全可靠',
    description: '企业级安全防护，9.5/10安全评分，保护您的数据'
  },
  {
    icon: '⚡',
    title: '高性能',
    description: 'API响应时间优化83.7%，支持高并发场景'
  }
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5
    }
  }
}

export default function Features() {
  return (
    <section className="py-24 px-6 bg-dark-800/50">
      <div className="container mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">核心特性</span>
          </h2>
          <p className="text-xl text-dark-300 max-w-2xl mx-auto">
            为多智能体协作打造的完整解决方案
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div key={index} variants={itemVariants}>
              <motion.div
                whileHover={{ y: -8, scale: 1.02 }}
                transition={{ duration: 0.3 }}
              >
                <Card hover>
                  <motion.div
                    className="text-5xl mb-4"
                    whileHover={{ scale: 1.2, rotate: 5 }}
                    transition={{ duration: 0.3 }}
                  >
                    {feature.icon}
                  </motion.div>
                  <h3 className="text-xl font-semibold mb-2 text-dark-100">{feature.title}</h3>
                  <p className="text-dark-400 leading-relaxed">{feature.description}</p>
                </Card>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
