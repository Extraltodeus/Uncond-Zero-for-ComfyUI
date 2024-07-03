# WIP / Come back later

# Uncond-Zero-for-ComfyUI

Allows to sample without generating any negative prediction with Stable Diffusion!

I did this as a personnal challenge: How good can a generation be without a negative prediction while following these rules:

- no LCM/Turbo/Lightning or any similar method to develop the tool
- Nothing making the sampling noticeably slower than if using euler with a CFG scale at 1.
- Should work with "confusing prompts" which tends to make a mess like "macro shot of a glowing forest spirit,leafy appendages outlined with veins of light,eyes a deep,enigmatic glow amidst the foliage.,"
- Should allow to use a negative prompt despite not generating a negative prediction (Shout out to [Clybius](https://github.com/Clybius) who helped me getting started with the maths!)

# How to use:

Set your sampler CFG at 1

## Tips:

- Nodes like the self-attention guidance making use of the uncond will not work.
- Combined with Tensort_RT you will reach new heights in terms of speed!
- I wouldn't be against [some support!](https://www.patreon.com/extraltodeus) :)


