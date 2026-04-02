#!/bin/bash
# Nautilus P0 问题快速修复脚本
# SSH端口: 24860

echo "==============="
echo "  Nautilus P0 快速修复脚本"
echo "=================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务器信息
SERVER="43.160.239.61"
PORT="24860"
USER="ubuntu"

echo -e "${YELLOW}服务器信息:${NC}"
echo "  IP: $SERVER"
echo "  端口: $PORT"
echo "  用户: $USER"
echo ""

# 函数：执行远程命令
remote_exec() {
    ssh -p $PORT $USER@$SERVER "$1"
}

# 1. 测试连接
echo -e "${YELLOW}[1/5] 测试SSH连接...${NC}"
if ssh -p $PORT -o ConnectTimeout=5 $USER@$SERVER "echo 'Connection OK'" 2>/dev/null; then
    echo -e "${GREEN}✓ SSH连接成功${NC}"
else
    echo -e "${RED}✗ SSH连接失败${NC}"
    echo "请检查:"
    echo "  1. 服务器IP是否正确"
    echo "  2. SSH端口24860是否开放"
    echo "  3. 网络连接是否正常"
    exit 1
fi
echo ""

# 2. 备份当前配置
echo -e "${YELLOW}[2/5] 备份当前配置...${NC}"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
remote_exec "cd /var/www/nautilus-core/phase3/backend && cp .env .env.backup.$BACKUP_DATE"
echo -e "${GREEN}✓ 配置已备份到 .env.backup.$BACKUP_DATE${NC}"
echo ""

# 3. 修复生产环境配置
echo -e "${YELLOW}[3/5] 修复生产环境配置...${NC}"
remote_exec "cd /var/www/nautilus-core/phase3/backend && \
    sed -i 's/DEBUG=true/DEBUG=false/g' .env && \
    sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/g' .env && \
    sed -i 's/TESTING=true/TESTING=false/g' .env"
echo -e "${GREEN}✓ 生产配置已更新${NC}"
echo ""

# 4. 启用防火墙
echo -e "${YELLOW}[4/5] 配置防火墙...${NC}"
remote_exec "sudo ufw --force enable && \
    sudo ufw allow 24860/tcp && \
    sudo ufw allow 80/tcp && \
    sudo ufw allow 443/tcp"
echo -e "${GREEN}✓ 防火墙已配置${NC}"
echo ""

# 5. 重启服务
echo -e "${YELLOW}[5/5] 重启后端服务...${NC}"
remote_exec "pm2 restart nautilus-backend"
sleep 3
echo -e "${GREEN}✓ 服务已重启${NC}"
echo ""

# 验证
echo -e "${YELLOW}验证修复结果...${NC}"
echo ""
echo "1. 检查配置:"
remote_exec "cd /var/www/nautilus-core/phase3/backend && grep -E '(DEBUG|ENVIRONMENT|TESTING)' .env"
echo ""
echo "2. 检查服务状态:"
remote_exec "pm2 list | grep nautilus"
echo ""
echo "3. 检查防火墙:"
remote_exec "sudo ufw status | grep -E '(24860|80|443)'"
echo ""

echo -e "${GREEN}===================="
echo "  P0-1 和 P0-2 修复完成！"
echo "========================${NC}"
echo ""
echo "下一步:"
echo "  1. 轮换OAuth密钥（手动操作）"
echo "  2. 修复OAuth State验证"
echo "  3. 诊断前端显示问题"
echo ""
echo "详细步骤请参考: PRIORITY_ACTION_PLAN.md"
