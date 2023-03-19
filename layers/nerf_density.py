import torch
import util
import numpy as np
import os, sys, time
import torch
import torch.nn.functional as torch_F
import torchvision
import torchvision.transforms.functional as torchvision_F
import tqdm
from easydict import EasyDict as edict
import cv2
import camera


class NeRF(torch.nn.Module):
    def __init__(self, opt):
        super(NeRF, self).__init__()
        input_3D_dim = 3 + 6 * opt.arch.posenc.L_3D if opt.arch.posenc else 3

        # point-wise feature
        self.mlp_feat = torch.nn.ModuleList()
        L = util.get_layer_dims(opt.arch.layers_feat)
        for li, (k_in, k_out) in enumerate(L):
            if li == 0: k_in = input_3D_dim
            if li in opt.arch.skip: k_in += input_3D_dim
            if li == len(L) - 1: k_out += 1
            linear = torch.nn.Linear(k_in, k_out)
            if opt.arch.tf_init:
                self.tensorflow_init_weights(linear, out="first" if li == len(L) - 1 else None)
            self.mlp_feat.append(linear)

    @staticmethod
    def tensorflow_init_weights(linear, out=None):
        # use Xavier init instead of Kaiming init
        relu_gain = torch.nn.init.calculate_gain("relu")  # sqrt(2)
        if out == "all":
            torch.nn.init.xavier_uniform_(linear.weight)
        elif out == "first":
            torch.nn.init.xavier_uniform_(linear.weight[:1])
            torch.nn.init.xavier_uniform_(linear.weight[1:], gain=relu_gain)
        else:
            torch.nn.init.xavier_uniform_(linear.weight, gain=relu_gain)
        torch.nn.init.zeros_(linear.bias)

    def forward(self, opt, points_3D, ray_unit=None, mode=None):  # [B,...,3]
        if opt.arch.posenc:
            points_enc = self.positional_encoding(opt, points_3D, L=opt.arch.posenc.L_3D)
            points_enc = torch.cat([points_3D, points_enc], dim=-1)  # [B,...,6L+3]
        else:
            points_enc = points_3D
        feat = points_enc
        # extract coordinate-based features
        for li, layer in enumerate(self.mlp_feat):
            if li in opt.arch.skip:
                feat = torch.cat([feat, points_enc], dim=-1)
            feat = layer(feat)
            if li == len(self.mlp_feat) - 1:
                density = feat[..., 0]
                if opt.nerf.density_noise_reg and mode == "train":
                    density += torch.randn_like(density) * opt.nerf.density_noise_reg
                density_activ = getattr(torch_F, opt.arch.density_activ)  # relu_,abs_,sigmoid_,exp_....
                density = density_activ(density)
                feat = feat[..., 1:]
            feat = torch_F.relu(feat)
        return density

    def forward_samples(self, opt, center, ray, depth_samples, mode=None):
        # This points are measured in world frame, depth_samples from difference view have no effect
        points_3D_samples = camera.get_3D_points_from_depth(opt,
                                                            center,
                                                            ray,
                                                            depth_samples,
                                                            multi_samples=True)  # [B,HW,N,3]
        if opt.nerf.view_dep:
            ray_unit = torch_F.normalize(ray, dim=-1)  # [B,HW,3]
            ray_unit_samples = ray_unit[..., None, :].expand_as(points_3D_samples)  # [B,HW,N,3]
        else:
            ray_unit_samples = None
        density_samples = self.forward(opt, points_3D_samples, ray_unit=ray_unit_samples,
                                       mode=mode)  # [B,HW,N],[B,HW,N,3]
        return density_samples

    @staticmethod
    def composite(opt, ray, density_samples, depth_samples):
        ray_length = ray.norm(dim=-1, keepdim=True)  # [B,HW,1]
        # volume rendering: compute probability (using quadrature)
        depth_intv_samples = depth_samples[..., 1:, 0] - depth_samples[..., :-1, 0]  # [B,HW,N-1]
        depth_intv_samples = torch.cat([depth_intv_samples, torch.empty_like(depth_intv_samples[..., :1]).fill_(1e10)],
                                       dim=2)  # [B,HW,N]
        dist_samples = depth_intv_samples * ray_length  # [B,HW,N]
        sigma_delta = density_samples * dist_samples  # [B,HW,N]
        alpha = 1 - (-sigma_delta).exp_()  # [B,HW,N]
        T = (-torch.cat([torch.zeros_like(sigma_delta[..., :1]), sigma_delta[..., :-1]], dim=2).cumsum(
            dim=2)).exp_()  # [B,HW,N], cumulative summation along the ray direction, which is dim 2 in this scenario
        prob = (T * alpha)[..., None]  # [B,HW,N,1]
        # integrate RGB and depth weighted by probability
        depth = (depth_samples * prob).sum(dim=2)  # [B,HW,1]
        opacity = prob.sum(dim=2)  # [B,HW,1]
        return depth, opacity, prob  # [B,HW,K]

    @staticmethod
    def positional_encoding(opt, x, L):  # [B,...,N]
        shape = x.shape
        freq = 2 ** torch.arange(L, dtype=torch.float32, device=opt.device) * np.pi  # [L]
        spectrum = x[..., None] * freq  # [B,...,N,L]
        sin, cos = spectrum.sin(), spectrum.cos()  # [B,...,N,L]
        input_enc = torch.stack([sin, cos], dim=-2)  # [B,...,N,2,L]
        input_enc = input_enc.view(*shape[:-1], -1)  # [B,...,2NL]
        return input_enc

    # @staticmethod
    # def _freeze_module(module):
    #     for param in module.parameters():
    #         param.requires_grad = False
