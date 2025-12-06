"""
NPU 推理主程序 - 使用华为 Ascend NPU 进行高性能推理
支持单张图像和批量推理
"""

import sys
import time
import numpy as np
from pathlib import Path
import yaml
import argparse
from typing import List, Dict, Union
import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as transforms

# 尝试导入 ACL (Ascend Computing Language)
try:
    import acl
    ACL_AVAILABLE = True
except ImportError:
    ACL_AVAILABLE = False
    print("警告: ACL 未安装,将使用 CPU 模拟")


class DeepClassifier(nn.Module):
    """深度分类器网络"""
    def __init__(self, input_dim=1024, num_classes=4):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Dropout(0.5),
            
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.4),
            
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        return self.network(x)


class NPUInference:
    """NPU 推理器"""
    
    def __init__(self, model_paths: List[str], device_id: int = 0,
                 config_path: str = 'config/inference_config.yaml'):
        """
        初始化 NPU 推理器
        
        Args:
            model_paths: 模型文件路径列表 (5个fold模型)
            device_id: NPU设备ID
            config_path: 配置文件路径
        """
        self.device_id = device_id
        self.models = []
        self.config = self._load_config(config_path)
        
        # 类别名称
        self.classes = ['Normal', 'Benign', 'InSitu', 'Invasive']
        
        # 加载特征标准化参数
        norm_params = np.load('models/features_mean_std.npz')
        self.feature_mean = norm_params['mean']
        self.feature_std = norm_params['std']
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # 初始化 ACL/NPU
        if ACL_AVAILABLE:
            self._init_acl()
        
        # 加载模型
        self._load_models(model_paths)
        
        print(f"✓ NPU推理器初始化完成 (设备: {device_id}, 模型数: {len(self.models)})")
    
    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _init_acl(self):
        """初始化 ACL"""
        ret = acl.init()
        if ret != 0:
            raise RuntimeError(f"ACL 初始化失败: {ret}")
        
        ret = acl.rt.set_device(self.device_id)
        if ret != 0:
            raise RuntimeError(f"设置设备失败: {ret}")
        
        print(f"✓ ACL 初始化成功,使用设备: {self.device_id}")
    
    def _load_models(self, model_paths: List[str]):
        """加载所有fold模型"""
        for i, model_path in enumerate(model_paths):
            model = DeepClassifier()
            model.load_state_dict(torch.load(model_path, map_location='cpu'))
            model.eval()
            self.models.append(model)
            print(f"  加载模型 {i+1}/{len(model_paths)}: {Path(model_path).name}")
    
    def extract_uni_features(self, image: np.ndarray) -> np.ndarray:
        """
        使用 UNI 模型提取特征
        这里应该加载 UNI ONNX/OM 模型进行推理
        为简化,使用预提取的特征或模拟
        """
        # TODO: 实际部署时,这里应该:
        # 1. 加载 UNI 的 OM 模型
        # 2. 在 NPU 上运行推理
        # 3. 返回 1024 维特征
        
        # 当前使用模拟 (实际部署时需要替换)
        print("  [模拟] UNI 特征提取...")
        return np.random.randn(1024).astype(np.float32)
    
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """图像预处理"""
        img = Image.open(image_path).convert('RGB')
        img_tensor = self.transform(img)
        return img_tensor.unsqueeze(0)
    
    def predict(self, image_path: str, use_tta: bool = False) -> Dict:
        """
        单张图像推理
        
        Args:
            image_path: 图像路径
            use_tta: 是否使用测试时增强
        
        Returns:
            预测结果字典
        """
        start_time = time.time()
        
        # 1. 图像预处理
        img_tensor = self.preprocess_image(image_path)
        
        # 2. 提取 UNI 特征 (在 NPU 上)
        # 实际部署时,这里会调用 NPU 上的 UNI OM 模型
        features = self.extract_uni_features(img_tensor.numpy())
        
        # 3. 特征标准化
        features = (features - self.feature_mean) / self.feature_std
        features_tensor = torch.FloatTensor(features).unsqueeze(0)
        
        # 4. 集成预测 (5个fold模型)
        all_probs = []
        for model in self.models:
            with torch.no_grad():
                output = model(features_tensor)
                probs = torch.softmax(output, dim=1)
                all_probs.append(probs.numpy())
        
        # 5. 平均概率
        avg_probs = np.mean(all_probs, axis=0)[0]
        pred_class = avg_probs.argmax()
        confidence = avg_probs[pred_class]
        
        # 6. TTA (可选)
        if use_tta:
            tta_probs = self._predict_with_tta(features_tensor)
            avg_probs = (avg_probs + tta_probs) / 2
            pred_class = avg_probs.argmax()
            confidence = avg_probs[pred_class]
        
        inference_time = time.time() - start_time
        
        return {
            'image': Path(image_path).name,
            'class': self.classes[pred_class],
            'class_id': int(pred_class),
            'confidence': float(confidence),
            'probabilities': {
                cls: float(prob) for cls, prob in zip(self.classes, avg_probs)
            },
            'inference_time': inference_time
        }
    
    def _predict_with_tta(self, features: torch.Tensor, rounds: int = 10) -> np.ndarray:
        """测试时增强"""
        tta_probs = []
        for _ in range(rounds):
            # 添加轻微噪声
            noisy_features = features + torch.randn_like(features) * 0.01
            
            round_probs = []
            for model in self.models:
                with torch.no_grad():
                    output = model(noisy_features)
                    probs = torch.softmax(output, dim=1)
                    round_probs.append(probs.numpy())
            
            tta_probs.append(np.mean(round_probs, axis=0)[0])
        
        return np.mean(tta_probs, axis=0)
    
    def batch_predict(self, image_paths: List[str], 
                     batch_size: int = 16) -> List[Dict]:
        """
        批量推理
        
        Args:
            image_paths: 图像路径列表
            batch_size: 批大小
        
        Returns:
            预测结果列表
        """
        results = []
        total = len(image_paths)
        
        print(f"开始批量推理: {total} 张图像")
        
        for i, img_path in enumerate(image_paths, 1):
            result = self.predict(img_path)
            results.append(result)
            
            if i % 10 == 0 or i == total:
                print(f"  进度: {i}/{total} ({i/total*100:.1f}%)")
        
        return results
    
    def __del__(self):
        """清理资源"""
        if ACL_AVAILABLE:
            acl.rt.reset_device(self.device_id)
            acl.finalize()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NPU 推理程序')
    parser.add_argument('--image', type=str, required=True,
                       help='输入图像路径')
    parser.add_argument('--models', type=str, nargs='+',
                       default=[
                           'models/fold_0_best.pth',
                           'models/fold_1_best.pth',
                           'models/fold_2_best.pth',
                           'models/fold_3_best.pth',
                           'models/fold_4_best.pth'
                       ],
                       help='模型路径列表')
    parser.add_argument('--device', type=int, default=0,
                       help='NPU 设备 ID')
    parser.add_argument('--tta', action='store_true',
                       help='使用测试时增强')
    parser.add_argument('--config', type=str,
                       default='config/inference_config.yaml',
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 初始化推理器
    print("="*60)
    print("NPU 推理程序")
    print("="*60)
    
    inferencer = NPUInference(
        model_paths=args.models,
        device_id=args.device,
        config_path=args.config
    )
    
    # 推理
    print(f"\n推理图像: {args.image}")
    result = inferencer.predict(args.image, use_tta=args.tta)
    
    # 输出结果
    print("\n" + "="*60)
    print("推理结果:")
    print("="*60)
    print(f"  图像: {result['image']}")
    print(f"  预测类别: {result['class']}")
    print(f"  置信度: {result['confidence']:.2%}")
    print(f"  推理时间: {result['inference_time']*1000:.1f}ms")
    print("\n  各类别概率:")
    for cls, prob in result['probabilities'].items():
        print(f"    {cls:12s}: {prob:.4f} {'█' * int(prob * 50)}")
    print("="*60)


if __name__ == '__main__':
    main()
