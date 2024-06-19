import torch

class uncondZeroNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                                "model": ("MODEL",),
                                "scale": ("FLOAT", {"default": 1, "min": 0.0, "max": 10.0, "step": 0.01, "round": 0.01}),
                                "method":(["uncond_zero","rescale_cfg"],),
                              }}
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"

    CATEGORY = "model_patches"

    def patch(self, model, scale, method):
        def uncond_zero(args):
            cond   = args["cond_denoised"]
            x_orig = args["input"]
            x_orig -= x_orig.mean()
            cond   -= cond.mean()
            return x_orig - (cond / cond.std() ** .5) * scale
        
        new_scale = 1 / (model.model.latent_format.scale_factor * 8)
        #Taken and adapted from comfy_extras/nodes_model_advanced
        def rescale_cfg(args):
            x_orig = args["input"]
            x_orig -= x_orig.mean()

            cond = args["cond_denoised"]
            cond -= cond.mean()

            cond = x_orig - (cond / cond.std() ** .5) * scale

            sigma = args["sigma"]
            sigma = sigma.view(sigma.shape[:1] + (1,) * (cond.ndim - 1))
            
            #rescale cfg has to be done on v-pred model output
            x = x_orig / (sigma * sigma + 1.0)
            uncond = x / sigma
            cond = ((x - (x_orig - cond)) * (sigma ** 2 + 1.0) ** 0.5) / (sigma)

            #rescalecfg
            x_cfg = uncond + new_scale * (cond - uncond)
            ro_pos = torch.std(cond, dim=(1,2,3), keepdim=True)
            ro_cfg = torch.std(x_cfg, dim=(1,2,3), keepdim=True)

            x_rescaled = x_cfg * (ro_pos / ro_cfg)

            return x_orig - (x - x_rescaled * sigma / (sigma * sigma + 1.0) ** 0.5)

        m = model.clone()
        m.set_model_sampler_cfg_function({"uncond_zero":uncond_zero,"rescale_cfg":rescale_cfg}[method])
        return (m, )