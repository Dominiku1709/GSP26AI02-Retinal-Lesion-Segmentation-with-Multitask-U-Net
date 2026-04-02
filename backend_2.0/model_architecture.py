#backend_2.0/model_acrhitecture.py
"""
Multi-Task U-Net Architecture cho OCT Retinal Lesion Segmentation

Features:
- Shared encoder (ResNet34 hoặc EfficientNet-B3)
- Dual decoder heads (Segmentation + Classification)
- Attention mechanisms
- Deep supervision
- Transfer learning

Target Performance:
- Classification Accuracy: ≥95%
- Segmentation Dice Score: >90%
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import segmentation_models_pytorch as smp
from typing import Dict, Optional, Tuple


class AttentionBlock(nn.Module):
    """
    Attention Gate để focus vào regions of interest
    Giúp model tập trung vào vùng tổn thương
    """
    
    def __init__(self, F_g: int, F_l: int, F_int: int):
        super(AttentionBlock, self).__init__()
        
        self.W_g = nn.Sequential(
            nn.Conv2d(F_g, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )
        
        self.W_x = nn.Sequential(
            nn.Conv2d(F_l, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )
        
        self.psi = nn.Sequential(
            nn.Conv2d(F_int, 1, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(1),
            nn.Sigmoid()
        )
        
        self.relu = nn.ReLU(inplace=True)
        
    def forward(self, g, x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = self.relu(g1 + x1)
        psi = self.psi(psi)
        
        return x * psi


class SCSEBlock(nn.Module):
    """
    Spatial and Channel Squeeze & Excitation
    Kết hợp channel attention và spatial attention
    """
    
    def __init__(self, channels: int, reduction: int = 16):
        super(SCSEBlock, self).__init__()
        
        # Channel Squeeze & Excitation
        self.cSE = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, channels // reduction, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels // reduction, channels, kernel_size=1),
            nn.Sigmoid()
        )
        
        # Spatial Squeeze & Excitation
        self.sSE = nn.Sequential(
            nn.Conv2d(channels, 1, kernel_size=1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return x * self.cSE(x) + x * self.sSE(x)


class DeepSupervisionBlock(nn.Module):
    """
    Deep Supervision để cải thiện gradient flow
    """
    
    def __init__(self, in_channels: int, out_channels: int):
        super(DeepSupervisionBlock, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        
    def forward(self, x, target_size: Tuple[int, int]):
        x = self.conv(x)
        x = F.interpolate(x, size=target_size, mode='bilinear', align_corners=True)
        return x


class MultiTaskUNet(nn.Module):
    """
    Multi-Task U-Net với Shared Encoder và Dual Decoder Heads
    """
    
    def __init__(self,
                 encoder_name: str = 'resnet34',
                 encoder_weights: str = 'imagenet',
                 num_classes: int = 3,
                 num_seg_classes: int = 2,
                 in_channels: int = 1,
                 use_attention: bool = True,
                 use_scse: bool = True,
                 use_deep_supervision: bool = True,
                 dropout_rate: float = 0.3):
        
        super(MultiTaskUNet, self).__init__()
        
        self.encoder_name = encoder_name
        self.num_classes = num_classes
        self.num_seg_classes = num_seg_classes
        self.use_attention = use_attention
        self.use_scse = use_scse
        self.use_deep_supervision = use_deep_supervision
        
        # ============================================================
        # SHARED ENCODER (Feature Extractor)
        # ============================================================
        
        self.encoder = smp.encoders.get_encoder(
            encoder_name,
            in_channels=in_channels,
            depth=5,
            weights=encoder_weights
        )
        
        # Get encoder output channels at each level
        self.encoder_channels = list(self.encoder.out_channels)
        
        # ============================================================
        # SEGMENTATION DECODER (FIXED LOGIC)
        # ============================================================
        
        self.decoder_blocks = nn.ModuleList()
        self.attention_blocks = nn.ModuleList() if use_attention else None
        self.scse_blocks = nn.ModuleList() if use_scse else None
        
        # Decoder channels (reverse pyramid)
        decoder_channels = [256, 128, 64, 32, 16]
        
        # Skip channels (từ encoder, đảo ngược, bỏ bottleneck)
        skip_channels = self.encoder_channels[:-1][::-1]
        
        # Input channel bắt đầu từ bottleneck
        prev_channels = self.encoder_channels[-1]
        
        for i in range(len(decoder_channels)):
            # [FIXED]: Tính toán channels cho việc Concatenation
            # Input của ConvBlock = Output lớp trước (Upsampled) + Skip Connection
            in_ch = prev_channels + skip_channels[i]
            out_ch = decoder_channels[i]
            
            # Decoder block
            self.decoder_blocks.append(
                nn.Sequential(
                    nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
                    nn.BatchNorm2d(out_ch),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
                    nn.BatchNorm2d(out_ch),
                    nn.ReLU(inplace=True)
                )
            )
            
            # Attention gate: Gate là feature map từ dưới lên, Input là skip connection
            if use_attention:
                self.attention_blocks.append(
                    AttentionBlock(
                        F_g=prev_channels, 
                        F_l=skip_channels[i], 
                        F_int=prev_channels // 2
                    )
                )
            
            # SCSE block
            if use_scse:
                self.scse_blocks.append(SCSEBlock(out_ch))
                
            # Cập nhật prev_channels cho vòng lặp sau (là output của block hiện tại)
            prev_channels = out_ch
        
        # Segmentation output head
        self.seg_head = nn.Conv2d(
            decoder_channels[-1],
            num_seg_classes,
            kernel_size=1
        )
        
        # Deep supervision heads
        if use_deep_supervision:
            self.deep_sup_heads = nn.ModuleList([
                DeepSupervisionBlock(ch, num_seg_classes)
                for ch in decoder_channels[:-1]
            ])
        
        # ============================================================
        # CLASSIFICATION HEAD
        # ============================================================
        
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        bottleneck_features = self.encoder_channels[-1]
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(bottleneck_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes)
        )
        
        self._init_weights()
        
    def _init_weights(self):
        """Initialize weights for decoder and classifier"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        """
        # ============================================================
        # ENCODER
        # ============================================================
        
        encoder_features = self.encoder(x)
        # encoder_features: [f0, f1, f2, f3, f4, f5(bottleneck)]
        
        # ============================================================
        # CLASSIFICATION BRANCH
        # ============================================================
        
        bottleneck = encoder_features[-1]
        cls_features = self.global_pool(bottleneck)
        cls_output = self.classifier(cls_features)
        
        # ============================================================
        # SEGMENTATION BRANCH (FIXED LOGIC)
        # ============================================================
        
        x_dec = encoder_features[-1] # Bắt đầu từ bottleneck
        skips = encoder_features[:-1][::-1] # Đảo ngược skip connections
        
        deep_sup_outputs = []
        
        for i, decoder_block in enumerate(self.decoder_blocks):
            skip = skips[i]
            
            # [FIXED]: Luôn Upsample cho mọi block để đảm bảo kích thước tăng dần
            x_dec = F.interpolate(x_dec, scale_factor=2, mode='bilinear', align_corners=True)
            
            # Xử lý padding nếu kích thước không khớp (do làm tròn số lẻ)
            if x_dec.shape[2:] != skip.shape[2:]:
                x_dec = F.interpolate(x_dec, size=skip.shape[2:], mode='bilinear', align_corners=True)
            
            # Apply attention gate
            if self.use_attention:
                skip = self.attention_blocks[i](g=x_dec, x=skip)
            
            # Concatenate
            x_dec = torch.cat([x_dec, skip], dim=1)
            
            # Apply decoder block
            x_dec = decoder_block(x_dec)
            
            # Apply SCSE
            if self.use_scse:
                x_dec = self.scse_blocks[i](x_dec)
            
            # Deep supervision
            if self.use_deep_supervision and i < len(self.decoder_blocks) - 1:
                deep_sup = self.deep_sup_heads[i](x_dec, target_size=x.shape[2:])
                deep_sup_outputs.append(deep_sup)
        
        # Final segmentation output
        seg_output = self.seg_head(x_dec)
        
        # Đảm bảo output size khớp input 100%
        if seg_output.shape[2:] != x.shape[2:]:
             seg_output = F.interpolate(seg_output, size=x.shape[2:], mode='bilinear', align_corners=True)
        
        outputs = {
            'seg_output': seg_output,
            'cls_output': cls_output
        }
        
        if self.use_deep_supervision and deep_sup_outputs:
            outputs['deep_sup_outputs'] = deep_sup_outputs
            
        return outputs
    
    def freeze_encoder(self):
        for param in self.encoder.parameters():
            param.requires_grad = False
    
    def unfreeze_encoder(self):
        for param in self.encoder.parameters():
            param.requires_grad = True
    
    def get_num_params(self) -> Dict[str, int]:
        total = sum(p.numel() for p in self.parameters())
        return {'total': total}


def create_model(config: Dict) -> MultiTaskUNet:
    """Factory function"""
    model = MultiTaskUNet(
        encoder_name=config.get('encoder_name', 'resnet34'),
        encoder_weights=config.get('encoder_weights', 'imagenet'),
        num_classes=config.get('num_classes', 3),
        num_seg_classes=config.get('num_seg_classes', 2),
        in_channels=config.get('in_channels', 1),
        use_attention=config.get('use_attention', True),
        use_scse=config.get('use_scse', True),
        use_deep_supervision=config.get('use_deep_supervision', True),
        dropout_rate=config.get('dropout_rate', 0.3)
    )
    return model


if __name__ == "__main__":
    print("="*60)
    print("Multi-Task U-Net Model Test")
    print("="*60)
    
    config = {'in_channels': 1}
    model = create_model(config)
    
    batch_size = 2
    x = torch.randn(batch_size, 1, 512, 512)
    print(f"\nInput shape: {x.shape}")
    
    outputs = model(x)
    
    print("\nOutput shapes:")
    print(f"  Segmentation: {outputs['seg_output'].shape}")
    print(f"  Classification: {outputs['cls_output'].shape}")
    
    # Simple check
    expected_seg_shape = (batch_size, 2, 512, 512)
    if outputs['seg_output'].shape == expected_seg_shape:
        print("\n✓ Model test passed!")
    else:
        print(f"\n✗ Model test failed! Expected {expected_seg_shape}, got {outputs['seg_output'].shape}")