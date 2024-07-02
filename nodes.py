import torch
from copy import deepcopy
from comfy.model_management import interrupt_current_processing

selfnorm = lambda x: x / x.norm()

def topk_average(latent, top_k=0.25):
    max_values = torch.topk(latent, k=int(len(latent)*top_k), largest=True).values
    min_values = torch.topk(latent, k=int(len(latent)*top_k), largest=False).values
    max_val = torch.mean(max_values).item()
    min_val = torch.mean(torch.abs(min_values)).item()
    value_range = (max_val + min_val) / 2
    return value_range

def normalized_pow(t,p):
    t_norm = t.norm()
    t_sign = t.sign()
    t_pow  = (t / t_norm).abs().pow(p)
    t_pow  = selfnorm(t_pow) * t_norm * t_sign
    return t_pow

def normalize_adjust(a,b,strength=1):
    norm_a = torch.linalg.norm(a)
    a = selfnorm(a)
    b = selfnorm(b)
    res = b - a * (a * b).sum()
    if res.isnan().any():
        res = torch.nan_to_num(res, nan=0.0)
    a = a - res * strength
    return a * norm_a

class uncondZeroNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                                "model": ("MODEL",),
                                "scale":     ("FLOAT",   {"default": 0.75, "min": 0.0, "max": 10.0, "step": 1/20, "round": 0.01}),
                                "pre_fix" :  ("BOOLEAN", {"default": True}),
                                "pre_scale": ("FLOAT",   {"default": 1.0,  "min": 0.0, "max":  2.0, "step": 1/10, "round":  0.1}),
                                # "exp_fix" :  ("BOOLEAN", {"default": False}),
                                # "exp_scale": ("FLOAT",   {"default": 0.75,  "min": 0.0, "max": 2.0, "step": 1/20, "round": 0.01}),
                              }
                              }
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"

    CATEGORY = "model_patches"

    def patch(self, model, scale, pre_fix, pre_scale, exp_fix=False, exp_scale=1):
        model_sampling = model.model.model_sampling
        sigma_max = model_sampling.sigma(model_sampling.timestep(model_sampling.sigma_max)).item()
        prev_cond = None

        def uncond_zero(args):
            nonlocal prev_cond
            if args["cond_scale"] > 1:
                print(f" CFG too high! You may be infering a negative for nothing!")
            cond   = args["cond_denoised"]
            x_orig = args["input"]
            sigma  = args["sigma"][0].item()
            first_step = True
            if sigma <= 1:
                return x_orig - cond
            if sigma < (sigma_max - 1):
                first_step = False

            result = torch.zeros_like(x_orig)

            for b in range(len(x_orig)):
                if exp_fix and exp_scale != 1:
                    cond[b] = normalized_pow(cond[b], exp_scale)

                for c in range(len(cond[b])):
                    if not first_step and pre_fix:
                        cond[b][c] = normalize_adjust(cond[b][c], prev_cond[b][c], pre_scale)
                    mes = topk_average(cond[b][c]) ** 0.5 # the square root is to dampen the variations
                    result[b][c] = x_orig[b][c] - cond[b][c] * scale / mes

            prev_cond = cond
            return result

        m = model.clone()
        m.set_model_sampler_cfg_function(uncond_zero)
        return (m, )

def sub_neg_to_pos(a, b, uncond_strength):
    norm_a = torch.linalg.norm(a)
    res = b - a * (a / norm_a * (b / norm_a)).sum()
    if res.isnan().any():
        res = torch.nan_to_num(res, nan=0.0)
    a = a - res * uncond_strength
    return a, res

# While this may look weird, among 26 different going from thoughtful to complete nonsense, this gave sharper results.
def post_cond_out(a, b, c, strength):
    if torch.equal(a, c) or torch.equal(b, c):
        return a, b
    
    a_delta = a - c
    b_delta = b - c

    _, res_a = sub_neg_to_pos(a_delta, b_delta, 1)
    _, res_b = sub_neg_to_pos(b_delta, a_delta, 1)

    res_a, _ = sub_neg_to_pos(res_a, a, 1)
    res_b, _ = sub_neg_to_pos(res_b, b, 1)

    a, _ = sub_neg_to_pos(a, res_a, strength)
    b, _ = sub_neg_to_pos(b, res_b, strength)
    return a, b

class cond_combine_pos_neg:
    def __init__(self):
        pass
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive_conditioning": ("CONDITIONING", ),
                "negative_conditioning": ("CONDITIONING", ),
                "empty_conditioning": ("CONDITIONING",),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }
    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING","CONDITIONING",)
    RETURN_NAMES = ("positive","negative",)
    CATEGORY = "conditioning"
    def exec(self, positive_conditioning, negative_conditioning, empty_conditioning, strength):
        if strength == 0:
            return(positive_conditioning,negative_conditioning,)
        cond_copy_1 = deepcopy(positive_conditioning)
        cond_copy_2 = deepcopy(negative_conditioning)
        cond_copy_3 = deepcopy(empty_conditioning)
        s = 1
        for x in range(min(len(cond_copy_1),len(cond_copy_2))):
            n_cond_slices = min(cond_copy_1[x][0].shape[1],cond_copy_2[x][0].shape[1]) // 77
            for n in range(n_cond_slices):
                if cond_copy_1[x][0].shape[-1] == 2048:
                    cond_copy_1[x][0][...,n*77+s:(n+1)*77,0:768],    cond_copy_2[x][0][...,n*77+s:(n+1)*77,0:768]    = post_cond_out(cond_copy_1[x][0][...,n*77+s:(n+1)*77,0:768],    cond_copy_2[x][0][...,n*77+s:(n+1)*77,0:768],    cond_copy_3[0][0][...,s:77,0:768],    strength)
                    cond_copy_1[x][0][...,n*77+s:(n+1)*77,768:2048], cond_copy_2[x][0][...,n*77+s:(n+1)*77,768:2048] = post_cond_out(cond_copy_1[x][0][...,n*77+s:(n+1)*77,768:2048], cond_copy_2[x][0][...,n*77+s:(n+1)*77,768:2048], cond_copy_3[0][0][...,s:77,768:2048], strength)
                else:
                    cond_copy_1[x][0][...,n*77+s:(n+1)*77,:], cond_copy_2[x][0][...,n*77+s:(n+1)*77,:] = post_cond_out(cond_copy_1[x][0][...,n*77+s:(n+1)*77,:], cond_copy_2[x][0][...,n*77+s:(n+1)*77,:],cond_copy_3[0][0][...,s:77,:], strength)
        return (cond_copy_1,cond_copy_2,)

class conditioningCropAdd:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", ),
                "empty_conditioning": ("CONDITIONING", ),
                "context_length" : ("INT", {"default": 1, "min": 1, "max": 12, "step": 1}),
                "enabled" : ("BOOLEAN", {"default": True}),
            }
        }
    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("CONDITIONING",)
    CATEGORY = "conditioning"
    def exec(self, conditioning, empty_conditioning, context_length, enabled):
        if not enabled: return (conditioning, )
        cond_copy = deepcopy(conditioning)
        for x in range(len(cond_copy)):
            n_cond_slices = cond_copy[x][0].shape[1] // 77
            if n_cond_slices == context_length:
                continue
            elif n_cond_slices > context_length:
                cropped_cond = cond_copy[x][0][...,0:context_length*77,:]
                cond_copy[x][0] = cropped_cond
            else:
                for y in range(context_length - n_cond_slices):
                    cond_copy[x][0] = torch.cat((cond_copy[x][0][..., 0:(y + context_length) * 77, :], empty_conditioning[0][0][...,0:77,:]), dim=-2)
        return (cond_copy,)

class interruptNaNpatch:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                                "model": ("MODEL",),
                                "replace_values" : ("BOOLEAN", {"default": True}),
                              }}
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"

    CATEGORY = "model_patches"

    def patch(self, model, replace_values, **kwargs):
        def interrupt_on_nan(args):
            denoised = args["denoised"]
            if torch.isnan(denoised).any() or torch.isinf(denoised).any():
                if replace_values:
                    denoised = torch.nan_to_num(denoised, nan=0.0)
                else:
                    interrupt_current_processing()
            return denoised
        m = model.clone()
        m.set_model_sampler_post_cfg_function(interrupt_on_nan)
        return (m, )