module.exports = {
  apps: [{
    name: 'nautilus-backend',
    script: 'uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    interpreter: 'python3',
    cwd: '/home/ubuntu/nautilus-mvp/phase3/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true
  }]
};
