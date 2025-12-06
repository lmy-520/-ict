#!/bin/bash
# NPU 部署包一键打包脚本
# 在 Linux/Mac 上运行

echo "================================"
echo "NPU 部署包打包工具"
echo "================================"
echo ""

# 检查目录
if [ ! -d "NPU_Deployment_Package" ]; then
    echo "错误: NPU_Deployment_Package 目录不存在!"
    exit 1
fi

echo "[1/4] 检查文件完整性..."

# 检查必需文件
required_files=(
    "README.md"
    "TRANSFER_CHECKLIST.md"
    "QUICK_START.md"
    "models/fold_0_best.pth"
    "models/fold_1_best.pth"
    "models/fold_2_best.pth"
    "models/fold_3_best.pth"
    "models/fold_4_best.pth"
    "models/uni_local.onnx"
    "scripts/npu_inference.py"
    "requirements.txt"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [ ! -f "NPU_Deployment_Package/$file" ]; then
        echo "  ✗ 缺少文件: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo "错误: 有 $missing_files 个必需文件缺失!"
    exit 1
fi

echo "  ✓ 所有必需文件完整"

echo ""
echo "[2/4] 清理临时文件..."

# 清理缓存和临时文件
find NPU_Deployment_Package -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find NPU_Deployment_Package -name "*.pyc" -delete 2>/dev/null
find NPU_Deployment_Package -name ".DS_Store" -delete 2>/dev/null

echo "  ✓ 临时文件已清理"

echo ""
echo "[3/4] 创建压缩包..."

# 创建 tar.gz
tar -czf NPU_Deployment_Package.tar.gz NPU_Deployment_Package/
tar_size=$(du -h NPU_Deployment_Package.tar.gz | cut -f1)

# 创建 zip
zip -r -q NPU_Deployment_Package.zip NPU_Deployment_Package/
zip_size=$(du -h NPU_Deployment_Package.zip | cut -f1)

echo "  ✓ 压缩包已创建:"
echo "    - NPU_Deployment_Package.tar.gz ($tar_size)"
echo "    - NPU_Deployment_Package.zip ($zip_size)"

echo ""
echo "[4/4] 生成校验和..."

# 生成 MD5
md5sum NPU_Deployment_Package.tar.gz > NPU_Deployment_Package.tar.gz.md5
md5sum NPU_Deployment_Package.zip > NPU_Deployment_Package.zip.md5

echo "  ✓ 校验和文件已生成"

echo ""
echo "================================"
echo "✓ 打包完成!"
echo "================================"
echo ""
echo "生成的文件:"
ls -lh NPU_Deployment_Package.tar.gz NPU_Deployment_Package.zip
echo ""
echo "传输到目标服务器:"
echo "  scp NPU_Deployment_Package.tar.gz user@npu-server:/path/"
echo ""
echo "在目标服务器解压:"
echo "  tar -xzf NPU_Deployment_Package.tar.gz"
echo "  cd NPU_Deployment_Package"
echo "  cat ../README.md"
echo ""
