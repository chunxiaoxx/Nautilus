#!/bin/bash
# Nautilus 诊断脚本

echo "=== Nautilus 系统诊断 ==="
echo ""

echo "1. 后端状态检查"
echo "----------------"
if curl -s http://localhost:8000/api/stats > /dev/null 2>&1; then
    echo "✅ 后端运行正常 (http://localhost:8000)"
    echo "   Stats API: $(curl -s http://localhost:8000/api/stats)"
else
    echo "❌ 后端未运行或无法访问"
fi
echo ""

echo "2. 前端状态检查"
echo "----------------"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端运行正常 (http://localhost:5173)"
else
    echo "❌ 前端未运行或无法访问"
fi
echo ""

echo "3. 数据库连接检查"
echo "----------------"
cd /c/Users/chunx/Projects/nautilus-core/phase3/backend
if python -c "import psycopg2; conn = psycopg2.connect('postgresql://nautilus:nautilus_staging_2024@localhost:5432/nautilus_staging'); print('✅ 数据库连接成功'); conn.close()" 2>/dev/null; then
    :
else
    echo "❌ 数据库连接失败"
fi
echo ""

echo "4. 前端路由检查"
echo "----------------"
for route in "" "login" "register" "tasks" "agents" "dashboard"; do
    if [ -z "$route" ]; then
        url="http://localhost:5173/"
        name="首页"
    else
        url="http://localhost:5173/$route"
        name="/$route"
    fi

    if curl -s "$url" | grep -q "<!DOCTYPE html>"; then
        echo "✅ $name 可访问"
    else
        echo "❌ $name 无法访问"
    fi
done
echo ""

echo "5. API端点检查"
echo "----------------"
for endpoint in "stats" "tasks" "agents"; do
    if curl -s "http://localhost:8000/api/$endpoint" > /dev/null 2>&1; then
        echo "✅ /api/$endpoint 可访问"
    else
        echo "❌ /api/$endpoint 无法访问"
    fi
done
echo ""

echo "=== 诊断完成 ==="
