# WIP / Come back later

# Uncond-Zero-for-ComfyUI

Allows to sample without generating any negative prediction with Stable Diffusion!

I did this as a personnal challenge: How good can a generation be without a negative prediction while following these rules:

- no LCM/Turbo/Lightning or any similar method to develop the tool ✔
- Nothing making the sampling noticeably slower than if using euler with a CFG scale at 1. ✔
- Should work with "confusing prompts" which tends to make a mess like "macro shot of a glowing forest spirit,leafy appendages outlined with veins of light,eyes a deep,enigmatic glow amidst the foliage.," ✔
- Should allow to use a negative prompt despite not generating a negative prediction (Shout out to [Clybius](https://github.com/Clybius) who helped me getting started with the maths!) ✔

The goal being to enhance the sampling and take even more advantages of other acceleration methods like the tensor RT engines.

### ⚠ Examples will be at the bottom ⚠

# Nodes

## Uncond Zero

To connect like a normal model patch. Generally right after the model loader.

![image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/53e6b2e3-db02-474c-a2ee-80c6a37e0b3d)

- Scale: basically similar to the CFG scale. I implemented a logic inspired from my other node [AutomaticCFG](https://github.com/Extraltodeus/ComfyUI-AutomaticCFG) with a few modifications so to adapt it to not using any negative.
- "pre_fix": Uses the previous step to modify the current one. This is the main trick to get a better quality / sharpness.
- "pre_scale": How strong will the effect be. Recommanded: 1 for sde/ancestral samplers, 1.5 if you want to use something like dpmpp2m.

## Conditioning combine positive and negative

Affects the positive conditioning with the negative.

![image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/554b9f78-d882-4c1c-b411-7fda48347278)

It threats equally the negative conditioning in case you would want to use it during normal sampling but its main purpose it only for the positive.

Caveat: The combination will go as far as the shortest conditioning. Meaning the is your negative is 3 x 77 tokens and your positive only 2 * 77, only 2 / 3 of your negative will be taken into account.

## Conditioning crop or fill

![image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/bef97878-7280-4500-8790-caaf34e231cf)

This node allows to use longer or shorter prompts with Tensor RT engines.

When creating a tensor rt engine, you can set the context length.

Here, "context_opt" set at 4:

![image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/08a39c5c-aa44-4cc5-a1d1-2cb3d448707a)

This is how long your context will be. Meaning, how many times 77 tokens you can use.

The issue is that if you set it at 1, any prompt being longer will make it:
- spam your CLI
- ignore it

If you set it at more than one during the creation and use a shorter conditioning it will generate noise while spamming the CLI.

So what this node does is simply allow you to set the desired context length. If you conditioning is longer it will crop it. If it is shorter it will concatenate an empty one until the length is reached.

## interrupt on NaN

![image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/70fdb4d2-64a8-4dca-a557-c45294f30197)

While I do not have seen any since the latest updates, tensor rt would sometimes throw a random black image. What this node does is that it cancels the sampling if any invalid value is detected. Also useful if you want to test Uncond Zero with bogus scales. The toggle will replace these values by 0 instead of cancelling.

# Examples (WIP)


## Tips:

- Nodes like the self-attention guidance making use of the uncond will not work.
- Combined with Tensort_RT you will reach new heights in terms of speed!
- I wouldn't be against [some support!](https://www.patreon.com/extraltodeus) :)


