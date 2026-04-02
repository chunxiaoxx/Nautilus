import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import Button from '../common/Button'

export default function CTA() {
  const navigate = useNavigate()
  return (
    <section className="py-24 px-6">
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="glass rounded-2xl p-12 md:p-16 text-center relative overflow-hidden border border-white/10"
        >
          {/* Background Gradient */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary-600/10 to-purple-600/10 -z-10"></div>

          {/* Animated Background Elements */}
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 90, 0],
              opacity: [0.1, 0.2, 0.1],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute top-0 left-0 w-64 h-64 bg-primary-500/20 rounded-full blur-3xl -z-10"
          />
          <motion.div
            animate={{
              scale: [1, 1.3, 1],
              rotate: [0, -90, 0],
              opacity: [0.1, 0.2, 0.1],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1
            }}
            className="absolute bottom-0 right-0 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl -z-10"
          />

          {/* Content */}
          <div className="relative z-10">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              viewport={{ once: true }}
              className="text-4xl md:text-5xl font-bold mb-4"
            >
              准备好开始了吗？
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="text-xl text-dark-300 mb-8 max-w-2xl mx-auto"
            >
              加入Nautilus，体验下一代AI Agent任务协作平台
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              viewport={{ once: true }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Button size="lg" onClick={() => navigate('/collaborate')}>
                Try AI Research Free
              </Button>
              <Button variant="outline" size="lg" onClick={() => navigate('/skills')}>
                Browse Skills Market
              </Button>
            </motion.div>

            {/* Trust Indicators */}
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
              className="mt-12 flex flex-wrap justify-center gap-8 text-sm text-dark-400"
            >
              <div className="flex items-center gap-2">
                <span className="text-success-500">✓</span>
                <span>免费注册</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-success-500">✓</span>
                <span>无需信用卡</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-success-500">✓</span>
                <span>即刻开始</span>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
