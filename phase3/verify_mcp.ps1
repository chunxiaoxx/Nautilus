Write-Host "验证MCP配置..." -ForegroundColor Green

# 检查配置文件
$mcpConfig = "$env:USERPROFILE\.claude\mcp_settings.json"
if (Test-Path $mcpConfig) {
    Write-Host "✓ MCP配置文件存在" -ForegroundColor Green

    # 读取配置
    $config = Get-Content $mcpConfig | ConvertFrom-Json
    $serverCount = $config.mcpServers.PSObject.Properties.Count
    Write-Host "✓ 配置了 $serverCount 个MCP服务器" -ForegroundColor Green

    # 列出服务器
    Write-Host "`n已配置的MCP服务器:" -ForegroundColor Yellow
    foreach ($server in $config.mcpServers.PSObject.Properties) {
        $disabled = if ($server.Value.disabled) { "(已禁用)" } else { "" }
        Write-Host "  - $($server.Name) $disabled" -ForegroundColor White
    }
} else {
    Write-Host "✗ MCP配置文件不存在" -ForegroundColor Red
}

# 检查工具
Write-Host "`n检查必需工具:" -ForegroundColor Yellow
$tools = @("uv", "gh", "node", "npm")
foreach ($tool in $tools) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) {
        Write-Host "  ✓ $tool" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $tool (未安装)" -ForegroundColor Red
    }
}

Write-Host "`n验证完成！" -ForegroundColor Green
