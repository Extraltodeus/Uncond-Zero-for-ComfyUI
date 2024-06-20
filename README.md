# Uncond-Zero-for-ComfyUI
Allows to sample without generating any uncond with Stable Diffusion!

This **doubles the generation speed** while removing the control provided by the negative prompt. Yet still preserves image quality.


![tensorrt_workflow](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/b76b02bf-2634-4206-8407-8637a36b04ed)


The combination of no-uncond with a [modified CLIP temperature](https://github.com/Extraltodeus/Stable-Diffusion-temperature-settings) (here set at 2) allows for more various images:

![____comfyui_123456_00166_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/ca7992f2-32da-44a6-8d90-df62f095439f)

# How to use:

Set your sampler CFG at 1 and connect the node like this:

![image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/ca96d323-1132-4848-9d1a-a9b6f5bfced4)


## Tips:

- dpmpp2m SDE seems to work best
- Nodes like the self-attention guidance making use of the uncond will not work.
- Combined with Tensort_RT you will reach new heights in terms of speed!
- I wouldn't be against [some support!](https://www.patreon.com/extraltodeus) :)

version 3 uses a modified version of Comfy's implementation of the rescaled CFG. I recommand this one with a scale at 1.

