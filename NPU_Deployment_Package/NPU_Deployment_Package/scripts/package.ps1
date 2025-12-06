# NPU 部署包打包工具 (Windows PowerShell)
# 使用方法: .\package.ps1

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "NPU 部署包打包工具" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# 检查目录
if (-not (Test-Path "NPU_Deployment_Package")) {
    Write-Host "错误: NPU_Deployment_Package 目录不存在!" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] 检查文件完整性..." -ForegroundColor Yellow

# 检查必需文件
$requiredFiles = @(
    "README.md",
    "TRANSFER_CHECKLIST.md",
    "QUICK_START.md",
    "models\fold_0_best.pth",
    "models\fold_1_best.pth",
    "models\fold_2_best.pth",
    "models\fold_3_best.pth",
    "models\fold_4_best.pth",
    "models\uni_local.onnx",
    "scripts\npu_inference.py",
    "requirements.txt"
)

$missingFiles = 0
foreach ($file in $requiredFiles) {
    $fullPath = Join-Path "NPU_Deployment_Package" $file
    if (-not (Test-Path $fullPath)) {
        Write-Host "  ✗ 缺少文件: $file" -ForegroundColor Red
        $missingFiles++
    }
}

if ($missingFiles -gt 0) {
    Write-Host "`n错误: 有 $missingFiles 个必需文件缺失!" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ 所有必需文件完整" -ForegroundColor Green

Write-Host "`n[2/4] 清理临时文件..." -ForegroundColor Yellow

# 清理缓存和临时文件
Get-ChildItem -Path "NPU_Deployment_Package" -Directory -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path "NPU_Deployment_Package" -File -Recurse -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem -Path "NPU_Deployment_Package" -File -Recurse -Filter ".DS_Store" | Remove-Item -Force

Write-Host "  ✓ 临时文件已清理" -ForegroundColor Green

Write-Host "`n[3/4] 创建压缩包..." -ForegroundColor Yellow

# 创建 ZIP 压缩包
if (Test-Path "NPU_Deployment_Package.zip") {
    Remove-Item "NPU_Deployment_Package.zip" -Force
}

Compress-Archive -Path "NPU_Deployment_Package" -DestinationPath "NPU_Deployment_Package.zip" -CompressionLevel Optimal

$zipSize = (Get-Item "NPU_Deployment_Package.zip").Length / 1MB
$zipSizeFormatted = [math]::Round($zipSize, 2)

Write-Host "  ✓ 压缩包已创建:" -ForegroundColor Green
Write-Host "    - NPU_Deployment_Package.zip ($zipSizeFormatted MB)" -ForegroundColor Green

Write-Host "`n[4/4] 生成校验和..." -ForegroundColor Yellow

# 生成 SHA256 校验和
$hash = Get-FileHash "NPU_Deployment_Package.zip" -Algorithm SHA256
$hash.Hash | Out-File "NPU_Deployment_Package.zip.sha256" -Encoding utf8

Write-Host "  ✓ 校验和文件已生成" -ForegroundColor Green

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✓ 打包完成!" -ForegroundColor Green
Write-Host "================================`n" -ForegroundColor Cyan

Write-Host "生成的文件:"
Get-Item "NPU_Deployment_Package.zip" | Format-Table Name, @{Label="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}

Write-Host "`n传输到目标服务器:"
Write-Host "  scp NPU_Deployment_Package.zip user@npu-server:/path/" -ForegroundColor Cyan

Write-Host "`n在目标服务器解压:"
Write-Host "  unzip NPU_Deployment_Package.zip" -ForegroundColor Cyan
Write-Host "  cd NPU_Deployment_Package" -ForegroundColor Cyan
Write-Host "  cat README.md" -ForegroundColor Cyan
Write-Host ""
