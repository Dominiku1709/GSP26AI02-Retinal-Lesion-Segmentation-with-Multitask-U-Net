import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
import segmentation_models_pytorch as smp
from segmentation_models_pytorch.encoders import get_encoder
from segmentation_models_pytorch.decoders.unet.decoder import UnetDecoder
from segmentation_models_pytorch.decoders.unetplusplus.decoder import UnetPlusPlusDecoder


# --- Building Blocks ---

class DoubleConv(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
        )
    def forward(self, x):
        return self.block(x)

class ConvBNAct(nn.Module):
    def __init__(self, in_ch, out_ch, kernel_size=3, padding=0, dilation=1):
        super().__init__()
        if padding == 0 and kernel_size == 3:
            padding = dilation
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size, padding=padding, dilation=dilation, bias=False)
        self.bn  = nn.BatchNorm2d(out_ch)
        self.act = nn.ReLU(inplace=True)
    def forward(self, x):
        return self.act(self.bn(self.conv(x)))


# --- Attention & Pooling ---

class ChannelAttention(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        mid = max(channels // reduction, 8)
        self.mlp = nn.Sequential(
            nn.Linear(channels, mid, bias=False), nn.ReLU(inplace=True),
            nn.Linear(mid, channels, bias=False),
        )
    def forward(self, x):
        avg = F.adaptive_avg_pool2d(x, 1).flatten(1)
        mx  = F.adaptive_max_pool2d(x, 1).flatten(1)
        return x * torch.sigmoid(self.mlp(avg) + self.mlp(mx)).view(x.size(0), x.size(1), 1, 1)

class SpatialAttention(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size=7, padding=3, bias=False)
        self.bn   = nn.BatchNorm2d(1)
    def forward(self, x):
        avg = x.mean(dim=1, keepdim=True)
        mx, _ = x.max(dim=1, keepdim=True)
        return x * torch.sigmoid(self.bn(self.conv(torch.cat([avg, mx], dim=1))))

class CBAMBlock(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.channel_att = ChannelAttention(channels, reduction)
        self.spatial_att = SpatialAttention()
    def forward(self, x):
        return self.spatial_att(self.channel_att(x))

class GeMPooling(nn.Module):
    def __init__(self, p: float = 3.0, eps: float = 1e-6):
        super().__init__()
        self.p   = nn.Parameter(torch.ones(1) * p)
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.adaptive_avg_pool2d(
            x.float().clamp(min=self.eps).pow(self.p),
            output_size=1
        ).pow(1.0 / self.p)

class RefineBlock(nn.Module):
    def __init__(self, channels, dropout=0.1, use_cbam=True, drop_path_rate=0.1):
        super().__init__()
        self.block = nn.Sequential(
            ConvBNAct(channels, channels),
            nn.Dropout2d(dropout),
            ConvBNAct(channels, channels),
        )
        self.cbam      = CBAMBlock(channels) if use_cbam else nn.Identity()
        self.drop_path = drop_path_rate

    def forward(self, x):
        residual = self.block(x)
        if self.training and self.drop_path > 0:
            keep = torch.rand(x.size(0), 1, 1, 1, device=x.device) > self.drop_path
            residual = residual * keep.float() / (1 - self.drop_path)
        return self.cbam(x + residual)


# --- Classification Heads ---

class FusionClassificationHead(nn.Module):
    def __init__(self, in_channels_list, num_classes, hidden_dim=256, dropout=0.3):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.mlp = nn.Sequential(
            nn.Linear(sum(in_channels_list), hidden_dim), nn.LayerNorm(hidden_dim),
            nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )
    def forward(self, features):
        return self.mlp(torch.cat([self.pool(f).flatten(1) for f in features], dim=1))

class DedicatedClassificationBranch(nn.Module):
    def __init__(self, encoder_channels: Tuple, num_classes: int, dropout: float = 0.4):
        super().__init__()
        self.gem = GeMPooling(p=3.0)
        n_stages = min(4, len(encoder_channels))
        
        self.proj = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(c, 96, kernel_size=1, bias=False),
                nn.BatchNorm2d(96),
                nn.ReLU(inplace=True),
            )
            for c in encoder_channels[-n_stages:]
        ])
        
        fused_dim = 96 * n_stages
        hidden    = 384 
        
        self.head = nn.Sequential(
            nn.Linear(fused_dim, hidden),
            nn.LayerNorm(hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden // 2),
            nn.LayerNorm(hidden // 2),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(hidden // 2, num_classes),
        )

    def forward(self, encoder_features: List[torch.Tensor]) -> torch.Tensor:
        n_stages = len(self.proj)
        feats  = encoder_features[-n_stages:]
        pooled = [self.gem(proj(f)).flatten(1) for proj, f in zip(self.proj, feats)]
        return self.head(torch.cat(pooled, dim=1))

class ASPP(nn.Module):
    def __init__(self, in_channels, out_channels, inner_channels=256, dropout=0.1):
        super().__init__()
        self.b1 = ConvBNAct(in_channels, inner_channels, kernel_size=1,  padding=0)
        self.b2 = ConvBNAct(in_channels, inner_channels, kernel_size=3, dilation=6)
        self.b3 = ConvBNAct(in_channels, inner_channels, kernel_size=3, dilation=12)
        self.b4 = ConvBNAct(in_channels, inner_channels, kernel_size=3, dilation=18)
        self.image_pool = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, inner_channels, kernel_size=1, bias=False),
            nn.GroupNorm(1, inner_channels),
            nn.ReLU(inplace=True),
        )
        self.project = nn.Sequential(
            nn.Conv2d(inner_channels * 5, out_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Dropout2d(dropout),
        )

    def forward(self, x):
        h, w = x.shape[-2:]
        img  = F.interpolate(self.image_pool(x), size=(h, w), mode="bilinear", align_corners=False)
        return self.project(torch.cat([self.b1(x), self.b2(x), self.b3(x), self.b4(x), img], dim=1))


def _apply_seg_activation(logits, num_seg_classes):
    return torch.sigmoid(logits)

def _get_blocks_list(decoder_blocks):
    if isinstance(decoder_blocks, nn.ModuleDict):
        return list(decoder_blocks.values())
    return decoder_blocks

@torch.no_grad()
def _probe_dense_channels(encoder, aspp, decoder, in_channels, intermediates, fallback_ch):
    for k in intermediates:
        intermediates[k] = None
    dummy = torch.zeros(1, in_channels, 64, 64)
    try:
        feats = list(encoder(dummy))
        feats[-1] = aspp(feats[-1])
        try:
            decoder(*feats)
        except TypeError:
            decoder(feats)
        result = {i: (v.shape[1] if v is not None else fallback_ch[i]) for i, v in intermediates.items()}
    except Exception:
        result = {i: fallback_ch[i] for i in range(len(fallback_ch))}
    for k in intermediates:
        intermediates[k] = None
    return result


# --- Model 1: Vanilla U-Net ---

class VanillaMultitaskUNet(nn.Module):
    def __init__(self, in_channels=1, num_classes=3, num_seg_classes=1, dropout_rate=0.3):
        super().__init__()
        self.num_seg_classes = num_seg_classes
        self.inc   = DoubleConv(in_channels, 64)
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(64,   128))
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(128,  256))
        self.down3 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(256,  512))
        self.down4 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(512, 1024))
        self.up1      = nn.ConvTranspose2d(1024, 512, 2, 2)
        self.conv_up1 = DoubleConv(1024, 512)
        self.up2      = nn.ConvTranspose2d(512,  256, 2, 2)
        self.conv_up2 = DoubleConv(512,  256)
        self.up3      = nn.ConvTranspose2d(256,  128, 2, 2)
        self.conv_up3 = DoubleConv(256,  128)
        self.up4      = nn.ConvTranspose2d(128,   64, 2, 2)
        self.conv_up4 = DoubleConv(128,   64)
        self.seg_head     = nn.Conv2d(64,  num_seg_classes, 1)
        self.aux_seg_head = nn.Conv2d(256, num_seg_classes, 1)
        self.cls_head = FusionClassificationHead([1024, 64], num_classes, dropout=dropout_rate)

    @staticmethod
    def _pad_cat(skip, up):
        diffY = skip.size(2) - up.size(2)
        diffX = skip.size(3) - up.size(3)
        up = F.pad(up, [diffX//2, diffX-diffX//2, diffY//2, diffY-diffY//2])
        return torch.cat([skip, up], dim=1)

    def forward(self, x, apply_activation=False):
        x1 = self.inc(x)
        x2 = self.down1(x1); x3 = self.down2(x2)
        x4 = self.down3(x3); x5 = self.down4(x4)
        u1 = self.conv_up1(self._pad_cat(x4, self.up1(x5)))
        u2 = self.conv_up2(self._pad_cat(x3, self.up2(u1)))
        u3 = self.conv_up3(self._pad_cat(x2, self.up3(u2)))
        u4 = self.conv_up4(self._pad_cat(x1, self.up4(u3)))
        seg_logits = self.seg_head(u4)
        aux_seg    = F.interpolate(self.aux_seg_head(u2), size=x.shape[-2:], mode="bilinear", align_corners=False)
        cls_output = self.cls_head([x5, u4])
        if apply_activation:
            seg_logits = _apply_seg_activation(seg_logits, self.num_seg_classes)
            aux_seg    = _apply_seg_activation(aux_seg,    self.num_seg_classes)
        return {"seg_logits": seg_logits, "cls_output": cls_output, "aux_seg": aux_seg, "dense_aux": []}


# --- Model 2: ResNet50 U-Net ---

class ResNet50MultiTaskUNet(nn.Module):
    def __init__(self, in_channels=1, num_classes=3, num_seg_classes=1, dropout_rate=0.3):
        super().__init__()
        self.num_seg_classes = num_seg_classes
        self.unet = smp.Unet("resnet50", encoder_weights="imagenet", in_channels=in_channels, classes=num_seg_classes)
        resnet50_enc_ch = (3, 64, 256, 512, 1024, 2048)
        self.cbam_bottleneck = CBAMBlock(2048, reduction=16)
        
        blocks_list = _get_blocks_list(self.unet.decoder.blocks)
        def hook_fn(module, inp, out):
            module._hook_out = out
        blocks_list[2].register_forward_hook(hook_fn)
        
        self.aux_seg_head = nn.Conv2d(64, num_seg_classes, 1)
        self.seg_refine   = RefineBlock(16, dropout=dropout_rate, use_cbam=True)
        self.seg_head     = nn.Conv2d(16, num_seg_classes, 1)
        self.cls_branch   = DedicatedClassificationBranch(resnet50_enc_ch, num_classes, dropout=dropout_rate)

    def forward(self, x, apply_activation=False):
        features = list(self.unet.encoder(x))
        enc_raw  = [f.clone() for f in features]
        features[-1] = self.cbam_bottleneck(features[-1])
        try:
            dec = self.unet.decoder(*features)
        except TypeError:
            dec = self.unet.decoder(features)
            
        dec        = self.seg_refine(dec)
        seg_logits = self.seg_head(dec)
        blocks_list = _get_blocks_list(self.unet.decoder.blocks)
        inter_feat = blocks_list[2]._hook_out
        aux_seg    = F.interpolate(self.aux_seg_head(inter_feat), size=x.shape[-2:], mode="bilinear", align_corners=False)
        cls_output = self.cls_branch(enc_raw)
        
        if apply_activation:
            seg_logits = _apply_seg_activation(seg_logits, self.num_seg_classes)
            aux_seg    = _apply_seg_activation(aux_seg,    self.num_seg_classes)
        return {"seg_logits": seg_logits, "cls_output": cls_output, "aux_seg": aux_seg, "dense_aux": []}


# --- Model 3: EfficientNet-B3 U-Net ---

class ImprovedOctMultiTaskUNet(nn.Module):
    def __init__(self, in_channels=1, num_classes=3, num_seg_classes=1, dropout_rate=0.3):
        super().__init__()
        self.num_seg_classes = num_seg_classes
        self.encoder  = get_encoder(name="efficientnet-b3", in_channels=in_channels, depth=5, weights="imagenet")
        bottleneck_ch = self.encoder.out_channels[-1]
        decoder_ch    = (256, 128, 64, 32, 16)
        self.aspp = ASPP(bottleneck_ch, bottleneck_ch, inner_channels=256, dropout=dropout_rate)
        self.decoder = UnetDecoder(
            encoder_channels=self.encoder.out_channels, decoder_channels=decoder_ch,
            n_blocks=5, attention_type="scse",
        )
        
        blocks_list = _get_blocks_list(self.decoder.blocks)
        def hook_fn(module, inp, out):
            module._hook_out = out
        blocks_list[2].register_forward_hook(hook_fn)
        
        self.aux_seg_head  = nn.Conv2d(64, num_seg_classes, 1)
        self.seg_refine    = RefineBlock(decoder_ch[-1], dropout=dropout_rate, use_cbam=True)
        self.seg_head      = nn.Conv2d(decoder_ch[-1], num_seg_classes, 1)
        self.boundary_head = nn.Sequential(
            nn.Conv2d(decoder_ch[-1], 16, 3, padding=1, bias=False),
            nn.BatchNorm2d(16), nn.ReLU(inplace=True),
            nn.Conv2d(16, num_seg_classes, 1),
        )
        self.cls_branch = DedicatedClassificationBranch(self.encoder.out_channels, num_classes, dropout=dropout_rate)

    def forward(self, x, apply_activation=False):
        features = list(self.encoder(x))
        enc_raw  = [f.clone() for f in features]
        features[-1] = self.aspp(features[-1])
        try:
            dec = self.decoder(*features)
        except TypeError:
            dec = self.decoder(features)
            
        dec             = self.seg_refine(dec)
        seg_logits      = self.seg_head(dec)
        boundary_logits = self.boundary_head(dec)
        blocks_list     = _get_blocks_list(self.decoder.blocks)
        inter_feat      = blocks_list[2]._hook_out
        aux_seg         = F.interpolate(self.aux_seg_head(inter_feat), size=x.shape[-2:], mode="bilinear", align_corners=False)
        cls_output      = self.cls_branch(enc_raw)
        
        if apply_activation:
            seg_logits      = _apply_seg_activation(seg_logits,      self.num_seg_classes)
            boundary_logits = _apply_seg_activation(boundary_logits, self.num_seg_classes)
            aux_seg         = _apply_seg_activation(aux_seg,         self.num_seg_classes)
        return {"seg_logits": seg_logits, "boundary_logits": boundary_logits, "cls_output": cls_output, "aux_seg": aux_seg, "dense_aux": []}


# --- Model 4: UNet++ Multi-Task ---

class UNetPlusPlusMultiTask(nn.Module):
    def __init__(self, in_channels=1, num_classes=3, num_seg_classes=1, dropout_rate=0.3):
        super().__init__()
        self.num_seg_classes = num_seg_classes

        self.encoder = get_encoder(name="efficientnet-b3", in_channels=in_channels, depth=5, weights="imagenet")
        bottleneck_ch = self.encoder.out_channels[-1]
        decoder_ch    = (256, 128, 64, 32, 16)

        self.aspp = ASPP(bottleneck_ch, bottleneck_ch, inner_channels=256, dropout=dropout_rate)

        self.decoder = UnetPlusPlusDecoder(
            encoder_channels=self.encoder.out_channels, decoder_channels=decoder_ch,
            n_blocks=5, attention_type="scse",
        )

        self._dense_intermediates: Dict[int, Optional[torch.Tensor]] = {i: None for i in range(4)}

        _dec_blocks = self.decoder.blocks
        if isinstance(_dec_blocks, nn.ModuleDict):
            from collections import defaultdict
            depth_groups: dict = defaultdict(list)
            for key in _dec_blocks.keys():
                try:
                    depth = int(key.split('_')[0])
                    depth_groups[depth].append(key)
                except (ValueError, IndexError):
                    pass
            sorted_depths = sorted(depth_groups.keys())
            for i, depth in enumerate(sorted_depths[:4]):
                last_key = sorted(depth_groups[depth])[-1]
                if last_key in _dec_blocks:
                    _dec_blocks[last_key].register_forward_hook(
                        lambda m, inp, out, _i=i: self._dense_intermediates.update({_i: out})
                    )
        else:
            _blocks_list = list(_dec_blocks)
            for i in range(min(4, len(_blocks_list))):
                _blocks_list[i].register_forward_hook(
                    lambda m, inp, out, _i=i: self._dense_intermediates.update({_i: out})
                )

        _actual_ch = _probe_dense_channels(
            self.encoder, self.aspp, self.decoder,
            in_channels=in_channels, intermediates=self._dense_intermediates, fallback_ch=decoder_ch,
        )

        self.dense_aux_heads = nn.ModuleList([
            nn.Conv2d(_actual_ch[i], num_seg_classes, 1) for i in range(4)
        ])
        
        self.seg_refine    = RefineBlock(decoder_ch[-1], dropout=dropout_rate, use_cbam=True, drop_path_rate=0.1)
        self.seg_head      = nn.Conv2d(decoder_ch[-1], num_seg_classes, 1)
        self.boundary_head = nn.Sequential(
            nn.Conv2d(decoder_ch[-1], 16, 3, padding=1, bias=False),
            nn.BatchNorm2d(16), nn.ReLU(inplace=True),
            nn.Conv2d(16, num_seg_classes, 1),
        )
        self.cls_branch = DedicatedClassificationBranch(
            encoder_channels=self.encoder.out_channels, num_classes=num_classes, dropout=dropout_rate,
        )

    def forward(self, x, apply_activation=False):
        for k in self._dense_intermediates:
            self._dense_intermediates[k] = None

        features = list(self.encoder(x))
        enc_raw  = [f.clone() for f in features]
        features[-1] = self.aspp(features[-1])

        try:
            decoder_output = self.decoder(*features)
        except TypeError:
            decoder_output = self.decoder(features)

        decoder_output = self.seg_refine(decoder_output)
        target_size    = x.shape[-2:]

        dense_aux: List[torch.Tensor] = []
        for i, head in enumerate(self.dense_aux_heads):
            feat = self._dense_intermediates.get(i)
            if feat is None:
                dense_aux.append(torch.zeros(x.size(0), self.num_seg_classes, *target_size, device=x.device))
            else:
                dense_aux.append(F.interpolate(head(feat), size=target_size, mode="bilinear", align_corners=False))

        seg_logits      = self.seg_head(decoder_output)
        boundary_logits = self.boundary_head(decoder_output)
        cls_output      = self.cls_branch(enc_raw)

        if apply_activation:
            seg_logits      = _apply_seg_activation(seg_logits,      self.num_seg_classes)
            boundary_logits = _apply_seg_activation(boundary_logits, self.num_seg_classes)
            dense_aux       = [_apply_seg_activation(a,              self.num_seg_classes) for a in dense_aux]

        return {
            "seg_logits":      seg_logits,
            "boundary_logits": boundary_logits,
            "cls_output":      cls_output,
            "aux_seg":         dense_aux[3] if dense_aux else torch.zeros_like(seg_logits),
            "dense_aux":       dense_aux,
        }


# --- TTA Wrapper ---

class TTAWrapper(nn.Module):
    def __init__(self, model, use_flips=True, use_rot90=True):
        super().__init__()
        self.model     = model
        self.use_flips = use_flips
        self.use_rot90 = use_rot90

    @torch.no_grad()
    def forward(self, x):
        def _run(img):
            out  = self.model(img, apply_activation=True)
            seg  = out["seg_logits"]
            bdry = out.get("boundary_logits", torch.zeros_like(seg))
            return seg, bdry, out["cls_output"]

        aug_segs, aug_bdry, aug_cls = [], [], []
        s, b, c = _run(x); aug_segs.append(s); aug_bdry.append(b); aug_cls.append(c)
        
        if self.use_flips:
            s, b, c = _run(torch.flip(x, [-1]))
            aug_segs.append(torch.flip(s, [-1])); aug_bdry.append(torch.flip(b, [-1])); aug_cls.append(c)
            s, b, c = _run(torch.flip(x, [-2]))
            aug_segs.append(torch.flip(s, [-2])); aug_bdry.append(torch.flip(b, [-2])); aug_cls.append(c)
        if self.use_rot90:
            s, b, c = _run(torch.rot90(x, 1, [-2, -1]))
            aug_segs.append(torch.rot90(s, -1, [-2, -1]))
            aug_bdry.append(torch.rot90(b, -1, [-2, -1])); aug_cls.append(c)
            
        return {
            "seg_logits":      torch.stack(aug_segs).mean(0),
            "boundary_logits": torch.stack(aug_bdry).mean(0),
            "cls_output":      torch.stack(aug_cls).mean(0),
            "aux_seg":         torch.zeros_like(aug_segs[0]),
            "dense_aux":       [],
        }


# --- Factory ---

def build_model(model_name, in_channels=1, num_classes=3, num_seg_classes=1, dropout_rate=0.3):
    name = model_name.lower().strip()
    cfg  = dict(in_channels=in_channels, num_classes=num_classes, num_seg_classes=num_seg_classes, dropout_rate=dropout_rate)
    
    registry = {
        "vanilla":      (VanillaMultitaskUNet,  "Vanilla U-Net"),
        "resnet50":     (ResNet50MultiTaskUNet, "ResNet50 U-Net"),
        "effb3_custom": (ImprovedOctMultiTaskUNet, "EfficientNet-B3 U-Net"),
        "unet++":       (UNetPlusPlusMultiTask, "EfficientNet-B3 UNet++"),
    }
    
    if name not in registry:
        raise ValueError(f"Unknown model: '{model_name}'. Choose from: {list(registry.keys())}")
        
    cls, label = registry[name]
    print(f"Building Model: {label}")
    return cls(**cfg)