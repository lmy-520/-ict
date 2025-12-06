# 华为 Ascend NPU 环境配置详细指南

## 📋 目录
1. [硬件要求](#硬件要求)
2. [系统准备](#系统准备)
3. [CANN 安装](#cann-安装)
4. [Python 环境配置](#python-环境配置)
5. [验证安装](#验证安装)
6. [常见问题](#常见问题)

---

## 🖥️ 硬件要求

### NPU 型号选择
| 型号 | 算力 | 功耗 | 适用场景 | 推荐度 |
|------|------|------|----------|--------|
| Ascend 310 | 22 TOPS | 8W | 边缘推理 | ⭐⭐⭐ |
| **Ascend 310P** | **44 TOPS** | **30W** | **服务器推理** | **⭐⭐⭐⭐⭐** |
| Ascend 910 | 256 TFLOPS | 310W | 训练+推理 | ⭐⭐⭐⭐ |
| Ascend 910B | 512 TFLOPS | 400W | 大模型训练 | ⭐⭐⭐⭐⭐ |

**推荐**: Ascend 310P (性价比最优,本项目最适合)

### 服务器配置
- **CPU**: x86_64 (Intel/AMD) 或 ARM64
- **内存**: ≥8GB (推荐 16GB+)
- **存储**: ≥20GB 可用空间
- **网络**: 有网络连接(下载依赖)

---

## 💿 系统准备

### 支持的操作系统
```
✅ Ubuntu 18.04 LTS
✅ Ubuntu 20.04 LTS  (推荐)
✅ EulerOS 2.8/2.10
✅ CentOS 7.6/8.2
✅ Kylin V10
```

### 系统更新
```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y

# CentOS/RedHat
sudo yum update -y

# 安装基础工具
sudo apt install -y wget curl git vim gcc g++ make cmake
```

### 检查系统信息
```bash
# 查看 OS 版本
cat /etc/os-release

# 查看内核版本
uname -r

# 查看 CPU 架构
uname -m

# 查看可用空间
df -h
```

---

## 🔧 CANN 安装

### 1. 下载 CANN 工具包

**官方下载页**: https://www.hiascend.com/software/cann

```bash
# 创建下载目录
mkdir -p ~/ascend_install
cd ~/ascend_install

# 下载 CANN Toolkit (示例版本 6.0.1)
# 需要先在官网注册并下载,然后上传到服务器

# 文件列表:
# - Ascend-cann-toolkit_6.0.1_linux-x86_64.run
# - Ascend-cann-kernels-910_6.0.1_linux.run
```

### 2. 安装驱动

```bash
# 安装 NPU 驱动
sudo chmod +x Ascend-hdk-*.run
sudo ./Ascend-hdk-*.run --full

# 重启系统
sudo reboot
```

### 3. 安装 CANN Toolkit

```bash
cd ~/ascend_install

# 安装 Toolkit
chmod +x Ascend-cann-toolkit_*.run
./Ascend-cann-toolkit_*.run --install

# 安装路径: /usr/local/Ascend/ascend-toolkit
```

安装选项:
```
Installation Path: /usr/local/Ascend/ascend-toolkit (默认)
Install Type: Full (选择完整安装)
```

### 4. 安装 CANN Kernels

```bash
# 安装算子库
chmod +x Ascend-cann-kernels-*.run
./Ascend-cann-kernels-*.run --install
```

### 5. 设置环境变量

```bash
# 方法1: 临时设置 (当前会话有效)
source /usr/local/Ascend/ascend-toolkit/set_env.sh

# 方法2: 永久设置 (推荐)
echo "source /usr/local/Ascend/ascend-toolkit/set_env.sh" >> ~/.bashrc
source ~/.bashrc
```

### 6. 验证 CANN 安装

```bash
# 检查环境变量
echo $ASCEND_HOME
# 输出: /usr/local/Ascend/ascend-toolkit

# 检查工具是否可用
which atc      # 模型转换工具
which msame    # 模型推理工具

# 查看版本
atc --version
```

---

## 🐍 Python 环境配置

### 1. 安装 Python 3.8/3.9

```bash
# Ubuntu
sudo apt install -y python3.8 python3.8-dev python3-pip

# 创建虚拟环境 (推荐)
python3.8 -m venv ~/npu_env
source ~/npu_env/bin/activate
```

### 2. 升级 pip

```bash
pip install --upgrade pip setuptools wheel
```

### 3. 安装 CANN Python 包

```bash
# 安装 ACL (Ascend Computing Language)
pip install /usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64/topi-*.whl
pip install /usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64/te-*.whl
pip install /usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64/hccl-*.whl

# 或使用 ais-bench
pip install ais-bench
```

### 4. 安装项目依赖

```bash
cd NPU_Deployment_Package
pip install -r requirements.txt
```

requirements.txt 内容:
```
torch>=1.11.0
torchvision>=0.12.0
onnx>=1.12.0
onnxruntime>=1.13.0
numpy>=1.21.0
pillow>=9.0.0
pyyaml>=6.0
tqdm>=4.64.0
opencv-python>=4.6.0
```

---

## ✅ 验证安装

### 1. 检查 NPU 设备

```bash
# 查看 NPU 信息
npu-smi info

# 预期输出示例:
# +-----------------------------------------------------------------------------+
# | npu-smi 1.0.0                       Version: 6.0.1                          |
# +----------------------+---------------+------------------------------------+
# | NPU  Name           | Health        | Power(W)    Temp(C)                |
# +======================+===============+====================================+
# | 0    Ascend310P3    | OK            | 15.2        42                     |
# +----------------------+---------------+------------------------------------+
```

### 2. 测试 Python ACL

创建测试文件 `test_acl.py`:
```python
import acl

# 初始化 ACL
ret = acl.init()
print(f"ACL 初始化: {'成功' if ret == 0 else '失败'}")

# 获取设备数量
device_count = acl.rt.get_device_count()
print(f"检测到 {device_count} 个 NPU 设备")

# 释放资源
acl.finalize()
```

运行测试:
```bash
python test_acl.py

# 预期输出:
# ACL 初始化: 成功
# 检测到 1 个 NPU 设备
```

### 3. 测试模型转换

```bash
# 创建简单的 ONNX 模型进行测试
cat > test_model.py << 'EOF'
import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)
    
    def forward(self, x):
        return self.fc(x)

model = SimpleModel()
dummy_input = torch.randn(1, 10)
torch.onnx.export(model, dummy_input, "test.onnx")
print("测试模型创建成功: test.onnx")
EOF

python test_model.py

# 转换为 OM 格式
atc --model=test.onnx \
    --framework=5 \
    --output=test \
    --soc_version=Ascend310P3 \
    --input_shape="x:1,10"

# 如果成功,会生成 test.om 文件
ls -lh test.om
```

---

## ❗ 常见问题

### 问题1: npu-smi: command not found
**原因**: 环境变量未设置或驱动未安装

**解决**:
```bash
# 设置环境变量
source /usr/local/Ascend/ascend-toolkit/set_env.sh

# 检查驱动
lsmod | grep drv_davinci
# 应该看到 drv_davinci_xxx

# 如果没有,重新安装驱动
```

### 问题2: atc 转换失败
**错误**: `[ERROR] Get soc version failed`

**解决**:
```bash
# 检查 soc_version 参数
# Ascend 310:  Ascend310
# Ascend 310P: Ascend310P3
# Ascend 910:  Ascend910

# 查看支持的版本
atc --help | grep soc_version
```

### 问题3: Python 导入 acl 失败
**错误**: `ModuleNotFoundError: No module named 'acl'`

**解决**:
```bash
# 安装 ACL Python 包
pip install /usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64/topi-*.whl

# 或使用 ais-bench
pip install ais-bench
```

### 问题4: NPU 设备不可用
**检查步骤**:
```bash
# 1. 检查驱动
lsmod | grep drv

# 2. 查看设备文件
ls -l /dev/davinci*

# 3. 检查权限
sudo usermod -aG HwHiAiUser $USER
# 注销重新登录

# 4. 重启服务
sudo systemctl restart ascend_init.service
```

### 问题5: 内存不足
**解决**:
```bash
# 减小 batch size
# 在 config/inference_config.yaml 中:
batch_size: 8  # 改为更小的值

# 或使用模型量化
python scripts/model_converter.py --precision int8
```

---

## 🔍 诊断工具

### 系统诊断脚本

创建 `diagnose.sh`:
```bash
#!/bin/bash
echo "=== Ascend NPU 环境诊断 ==="

echo -e "\n1. 操作系统信息"
cat /etc/os-release | grep PRETTY_NAME

echo -e "\n2. 内核版本"
uname -r

echo -e "\n3. CANN 环境变量"
echo "ASCEND_HOME: $ASCEND_HOME"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"

echo -e "\n4. NPU 驱动"
lsmod | grep drv_davinci

echo -e "\n5. NPU 设备"
ls -l /dev/davinci* 2>/dev/null || echo "未找到 NPU 设备"

echo -e "\n6. npu-smi"
which npu-smi && npu-smi info || echo "npu-smi 不可用"

echo -e "\n7. atc 工具"
which atc && atc --version || echo "atc 不可用"

echo -e "\n8. Python ACL"
python -c "import acl; print('ACL 可用')" 2>/dev/null || echo "ACL 不可用"

echo -e "\n=== 诊断完成 ==="
```

运行诊断:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## 📚 参考资料

- **CANN 官方文档**: https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/60RC1alpha002/overview/index.html
- **开发者论坛**: https://bbs.huaweicloud.com/forum/forum-726-1.html
- **示例代码**: https://gitee.com/ascend/samples
- **API 参考**: https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/60RC1alpha002/apiref/apiref/aclpythondevg_01_0001.html

---

## ✨ 下一步

环境配置完成后:

1. ✅ 阅读 `QUICK_START.md` 开始推理
2. ✅ 参考 `ACCELERATION_PRINCIPLE.md` 了解优化原理
3. ✅ 查看 `docs/Model_Conversion.md` 学习模型转换

🎉 **环境配置完成,可以开始在 NPU 上运行推理了!**
