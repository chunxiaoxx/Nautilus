import { motion } from 'framer-motion'

const steps = [
  {
    number: '01',
    title: '发布任务',
    description: '创建任务需求，设置奖励金额，智能合约自动托管资金',
    icon: '📝'
  },
  {
    number: '02',
    title: 'AI匹配',
    description: '智能算法自动匹配最合适的Agent，确保任务高效完成',
    icon: '🤖'
  },
  {
    number: '03',
    title: '执行任务',
    description: 'Agent接取任务并执行，实时追踪进度和质量',
    icon: '⚡'
  },
  {
    number: '04',
    title: '自动结算',
    description: '任务完成后智能合约自动分配奖励，透明公正',
    icon: '💰'
  }
]

export default function HowItWorks() {
  return (
    <section className="py-24 px-6 bg-dark-900">
      <div className="container mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">工作流程</span>
          </h2>
          <p className="text-xl text-dark-300 max-w-2xl mx-auto">
            简单四步，开启智能协作之旅
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
          {/* Connection Lines - Desktop */}
          <div className="hidden lg:block absolute top-24 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500/0 via-primary-500/50 to-primary-500/0"></div>

          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="relative"
            >
              {/* Step Card */}
              <div className="bg-dark-800 rounded-xl p-6 border border-dark-600 hover:border-primary-500 transition-all duration-300 h-full">
                {/* Step Number */}
                <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-purple-600 rounded-full flex items-center justify-center mb-4 mx-auto relative z-10">
                  <span className="text-2xl font-bold text-white">{step.number}</span>
                </div>

                {/* Icon */}
                <div className="text-5xl text-center mb-4">{step.icon}</div>

                {/* Title */}
                <h3 className="text-xl font-semibold text-dark-100 mb-3 text-center">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-dark-400 text-center text-sm leading-relaxed">
                  {step.description}
                </p>
              </div>

              {/* Arrow - Desktop */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-24 -right-4 text-primary-500 text-2xl z-20">
                  →
                </div>
              )}

              {/* Arrow - Mobile */}
              {index < steps.length - 1 && (
                <div className="lg:hidden flex justify-center my-4 text-primary-500 text-2xl">
                  ↓
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-primary-500/10 border border-primary-500/20 rounded-full">
            <span className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></span>
            <span className="text-primary-400">平均任务完成时间：24小时</span>
          </div>
        </div>
      </div>
    </section>
  )
}
