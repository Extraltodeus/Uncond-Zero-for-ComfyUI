# Uncond-Zero-for-ComfyUI

Allows to sample without generating any negative prediction with Stable Diffusion!

I did this as a personnal challenge: How good can a generation be without a negative prediction while following these rules:

- no LCM/Turbo/Lightning or any similar method to develop the tool ✔
- Nothing making the sampling noticeably slower than if using euler with a CFG scale at 1. ✔
- Should work with "confusing prompts" which tends to make a mess like "macro shot of a glowing forest spirit,leafy appendages outlined with veins of light,eyes a deep,enigmatic glow amidst the foliage.," ✔
- Should allow to use a negative prompt despite not generating a negative prediction (Shout out to [Clybius](https://github.com/Clybius) who helped me getting started with the maths!) ✔
- Should work with max 12 steps ✔

The goal being to enhance the sampling and take even more advantages of other acceleration methods like the tensor RT engines.

With an RTX4070:

SDXL 1024x1024 / tensor rt: **9.67it/s**

LCM SD 1.5 512x512 / tensor rt: **37.50it/s**


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

The issue is that if you set it at 1, any prompt being longer will make it spam your CLI and ignore the extra.

If you set it at more than one during the creation and use a shorter conditioning it will generate noise while spamming the CLI.

So what this node does is simply allow you to set the desired context length. If your conditioning is longer it will crop it. If it is shorter it will concatenate an empty one until the length is reached.

## interrupt on NaN

![image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/70fdb4d2-64a8-4dca-a557-c45294f30197)

While I do not have seen any since the latest updates, tensor rt would sometimes throw a random black image. What this node does is that it cancels the sampling if any invalid value is detected. Also useful if you want to test Uncond Zero with bogus scales. The toggle will replace these values by 0 instead of cancelling.

# Examples

(all images are workflows)

## Nothing versus everything (SDXL/tensorrt):

![07851UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/2e376064-96b7-4803-92e8-50baf59d6a1c)![07847UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/596533a2-2e81-41ae-8100-100d06727f3c)

## SD 1.5 (merge) with LCM in 3 steps.

### Vanilla / Only with the prediction scaled / "pre_fix" Enabled added / Negative prompt added:

![07918UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/f9160e85-2f3c-404f-a7ba-a1ba950d82a4)![07917UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/4d4e5088-cc2c-4b07-9c02-acf4c2392f98)![07916UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/ea139f23-7e85-4013-9613-10d6db5cfba6)![07913UI_00001_ - Copie](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/14ddacde-aedb-429c-bdb5-f46bbb28816f)

Also just to show the difference in sharpness, everything except the "pre_fix":

![07919UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/a9508b05-e06e-4956-840b-77567b9b0c10)

## Negative prompt integration example:

Just "bad quality" (everything after will also have "bad quality" at the end):

![negative bad quality](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/f3d8a9ae-b51f-4a27-bf5a-65005d4164ab)

Summer in the negative:

![negative summer](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/c71509fa-4c8f-439f-b5ed-83dd9a132c97)

Winter:

![negative winter](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/ae68410b-57d1-4aaf-82cb-ef9052c6ba4a)

Water:

![water](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/b7d7ed84-d15b-4205-9f1a-dcd2f8f19c10)

Water, autumn:

![negative water, autumn](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/43dc13fe-cde4-4bb7-8f5a-3329506ee6f9)


## pre_fix

### off / 0.5 / 1

![combined_image](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/da973ee9-3da1-4447-9efd-4265bfe7a813)


## "skill issue"

You too! Discover how this man went from a bland face

![07922UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/dc6f6f09-29f2-47f7-babc-de7159704240)

To a smiling average dude:

![07834UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/b6049233-01c7-4905-a841-1f44861cc040)

To this very successful businessman!

![07841UI_00001_](https://github.com/Extraltodeus/Uncond-Zero-for-ComfyUI/assets/15731540/71e88533-7e7c-43de-98a5-43f48cf58035)

All is the same seed. First image is "a man with a sad face" without any modification.

The second is with all the modification enabled but the prompt is only "a smiling man".

The third one is "a smiling man wearing a suit, hiding behind a tree, hdr quality".

Or in short: a better prompt will actually give you a better result. While it may seem obvious, in general while using a negative prediction it makes it good even when the prompt is simple. While without it, it does not. If anything that is for me the biggest (if big) caveat as I am not allowed to be as lazy as I like and forces me to add at least like two or three words in my prompts to make them better sometimes 😪.

## Tips:

- Nodes like the self-attention guidance making use of the uncond will not work. Perturbed attention will (but not yet with tensor rt btw).
- I wouldn't be against [SOME support!](https://www.patreon.com/extraltodeus) :)


