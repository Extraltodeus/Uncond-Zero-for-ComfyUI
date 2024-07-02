from .nodes import *

NODE_CLASS_MAPPINGS = {
    "Uncond Zero":uncondZeroNode,
    "Conditioning combine positive and negative":cond_combine_pos_neg,
    "Conditioning crop or fill":conditioningCropAdd,
    "interrupt on NaN": interruptNaNpatch,
}
