# 📋 文件转移清单 - 完整版

## 🎯 转移目的
将训练好的模型部署到**华为 Ascend NPU**服务器进行高性能推理。

---

## ✅ 必须转移的文件 (总计约 1.5 GB)

### 1️⃣ 模型文件 (models/)
| 文件名 | 大小 | 必需 | 说明 |
|--------|------|------|------|
| `fold_0_best.pth` | 1.3 MB | ✅ | K折模型1 |
| `fold_1_best.pth` | 1.3 MB | ✅ | K折模型2 |
| `fold_2_best.pth` | 1.3 MB | ✅ | K折模型3 |
| `fold_3_best.pth` | 1.3 MB | ✅ | K折模型4 |
| `fold_4_best.pth` | 1.3 MB | ✅ | K折模型5 |
| `features_mean_std.npz` | <1 MB | ✅ | 特征标准化参数 |
| `uni_local.onnx` | 1.42 MB | ⚠️ | ONNX模型(如需转换) |
| `model_info.json` | <1 KB | ✅ | 模型元数据 |

**说明**:
- 5个 `.pth` 文件是集成模型,必需
- `features_mean_std.npz` 包含训练时的均值和标准差
- `uni_local.onnx` 仅在需要重新转换时才需要

### 2️⃣ 推理脚本 (scripts/)
| 文件名 | 必需 | 说明 |
|--------|------|------|
| `npu_inference.py` | ✅ | NPU推理主程序 |
| `model_converter.py` | ✅ | 模型转换工具 |
| `batch_inference.py` | ✅ | 批量推理脚本 |
| `benchmark.py` | ✅ | 性能测试工具 |
| `install_dependencies.sh` | ✅ | 依赖安装脚本 |

### 3️⃣ 配置文件 (config/)
| 文件名 | 必需 | 说明 |
|--------|------|------|
| `npu_config.yaml` | ✅ | NPU设备配置 |
| `inference_config.yaml` | ✅ | 推理参数配置 |

### 4️⃣ 依赖配置
| 文件名 | 必需 | 说明 |
|--------|------|------|
| `requirements.txt` | ✅ | Python依赖列表 |

### 5️⃣ 文档 (根目录 + docs/)
| 文件名 | 必需 | 说明 |
|--------|------|------|
| `README.md` | ✅ | 主文档 |
| `TRANSFER_CHECKLIST.md` | ✅ | 本清单 |
| `NPU_SETUP_GUIDE.md` | ✅ | 环境配置指南 |
| `QUICK_START.md` | ✅ | 快速开始 |
| `ACCELERATION_PRINCIPLE.md` | ✅ | 加速原理 |
| `docs/CANN_Installation.md` | ✅ | CANN安装 |
| `docs/Model_Conversion.md` | ✅ | 模型转换详解 |
| `docs/Performance_Tuning.md` | ✅ | 性能调优 |
| `docs/Troubleshooting.md` | ✅ | 故障排除 |

---

## ❌ 不需要转移的文件

### 训练相关文件 (不需要)
```
features_cpu/           # 训练时的特征缓存
  ├── train_features.npy
  ├── val_features.npy
  └── ...

results/                # 训练结果
  ├── training_curves.png
  ├── confusion_matrix.png
  └── ...

train_*.py              # 训练脚本
quick_extract.py        # 特征提取脚本
```

### 临时文件 (不需要)
```
__pycache__/            # Python缓存
*.pyc                   # 编译文件
.ipynb_checkpoints/     # Jupyter缓存
*.log                   # 日志文件
```

### 数据集 (不需要,除非要在NPU上重新训练)
```
../ICIAR2018_BACH_Challenge/
```

---

## 📦 打包步骤

### Windows 打包
```powershell
# 进入项目目录
cd d:\华为ict\huaweiict2

# 使用 7-Zip 打包
7z a -tzip NPU_Deployment_Package.zip NPU_Deployment_Package\

# 或使用 PowerShell 压缩
Compress-Archive -Path NPU_Deployment_Package -DestinationPath NPU_Deployment_Package.zip
```

### Linux 打包 (目标服务器)
```bash
cd /path/to/project

# 使用 tar.gz
tar -czf NPU_Deployment_Package.tar.gz NPU_Deployment_Package/

# 或使用 zip
zip -r NPU_Deployment_Package.zip NPU_Deployment_Package/
```

---

## 🚚 文件传输方式

### 方式1: U盘/移动硬盘 (推荐)
1. 将压缩包复制到U盘
2. 在目标服务器解压
```bash
unzip NPU_Deployment_Package.zip
# 或
tar -xzf NPU_Deployment_Package.tar.gz
```

### 方式2: SCP (网络传输)
```bash
# 从 Windows 上传到 Linux 服务器
scp NPU_Deployment_Package.zip user@server:/path/to/destination/

# 在服务器上解压
ssh user@server
cd /path/to/destination
unzip NPU_Deployment_Package.zip
```

### 方式3: FTP/SFTP
使用 FileZilla 等工具传输

### 方式4: 云存储
- 百度网盘
- 阿里云OSS
- 华为云OBS

---

## ✅ 转移后验证清单

### 1. 文件完整性检查
```bash
cd NPU_Deployment_Package

# 检查目录结构
tree -L 2

# 预期输出:
# .
# ├── README.md
# ├── models/
# │   ├── fold_0_best.pth
# │   ├── fold_1_best.pth
# │   └── ...
# ├── scripts/
# │   ├── npu_inference.py
# │   └── ...
# ├── config/
# └── docs/
```

### 2. 模型文件检查
```bash
# 检查所有必需文件是否存在
ls -lh models/*.pth
ls -lh models/features_mean_std.npz

# 预期: 5个 .pth 文件 + 1个 .npz 文件
```

### 3. 脚本权限设置
```bash
# 给 shell 脚本添加执行权限
chmod +x scripts/install_dependencies.sh
```

### 4. Python 依赖安装
```bash
# 安装依赖
pip install -r requirements.txt

# 验证关键包
python -c "import torch; print(torch.__version__)"
python -c "import numpy; print(numpy.__version__)"
```

---

## 📊 文件大小统计

| 类别 | 文件数 | 总大小 |
|------|--------|--------|
| 模型文件 | 7 | ~8 MB |
| 脚本文件 | 5 | ~50 KB |
| 配置文件 | 2 | ~5 KB |
| 文档文件 | 9 | ~100 KB |
| **总计** | **23** | **~8.2 MB** |

**压缩后**: 约 2-3 MB

---

## 🔒 安全注意事项

1. **模型文件保护**: 
   - 模型文件包含训练成果,避免泄露
   - 建议加密压缩: `7z a -p -mhe=on secure.7z NPU_Deployment_Package/`

2. **配置文件检查**:
   - 确保配置文件中没有敏感信息(密码、密钥等)

3. **传输安全**:
   - 使用 HTTPS/SFTP 等加密传输
   - 验证文件 MD5/SHA256 哈希值

```bash
# 生成哈希值
md5sum NPU_Deployment_Package.zip
sha256sum NPU_Deployment_Package.zip

# 在目标机器验证
md5sum NPU_Deployment_Package.zip
```

---

## 🎯 快速检查命令

在目标 NPU 服务器上运行:

```bash
#!/bin/bash
# check_deployment.sh - 快速验证脚本

echo "=== NPU 部署包完整性检查 ==="

# 1. 检查目录
if [ -d "NPU_Deployment_Package" ]; then
    echo "✅ 部署包目录存在"
else
    echo "❌ 部署包目录不存在!"
    exit 1
fi

cd NPU_Deployment_Package

# 2. 检查模型文件
echo -n "检查模型文件..."
if [ -f "models/fold_0_best.pth" ] && \
   [ -f "models/fold_1_best.pth" ] && \
   [ -f "models/fold_2_best.pth" ] && \
   [ -f "models/fold_3_best.pth" ] && \
   [ -f "models/fold_4_best.pth" ] && \
   [ -f "models/features_mean_std.npz" ]; then
    echo "✅ (6/6)"
else
    echo "❌ 缺少模型文件!"
fi

# 3. 检查脚本文件
echo -n "检查脚本文件..."
if [ -f "scripts/npu_inference.py" ] && \
   [ -f "scripts/model_converter.py" ]; then
    echo "✅"
else
    echo "❌ 缺少脚本文件!"
fi

# 4. 检查配置文件
echo -n "检查配置文件..."
if [ -f "config/npu_config.yaml" ] && \
   [ -f "config/inference_config.yaml" ]; then
    echo "✅"
else
    echo "❌ 缺少配置文件!"
fi

# 5. 检查文档
echo -n "检查文档..."
if [ -f "README.md" ] && \
   [ -f "NPU_SETUP_GUIDE.md" ]; then
    echo "✅"
else
    echo "❌ 缺少文档!"
fi

echo ""
echo "=== 检查完成 ==="
echo "如果所有项都是 ✅, 可以继续进行 NPU 配置"
```

---

## 📞 需要帮助?

如果在文件转移过程中遇到问题:

1. 检查 `docs/Troubleshooting.md`
2. 参考 `README.md` 的故障排除部分
3. 联系技术支持

---

## ✨ 总结

**核心转移文件**:
1. ✅ 5个模型文件 (fold_*.pth)
2. ✅ 特征参数 (features_mean_std.npz)
3. ✅ 推理脚本 (scripts/*.py)
4. ✅ 配置文件 (config/*.yaml)
5. ✅ 依赖列表 (requirements.txt)
6. ✅ 完整文档 (*.md + docs/)

**总大小**: ~8 MB (压缩后 2-3 MB)

**转移后步骤**:
1. 解压文件
2. 安装 CANN
3. 安装 Python 依赖
4. 转换模型
5. 运行推理

🎉 **完成后即可在 NPU 上实现高性能推理!**
