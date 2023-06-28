from pydantic import BaseModel
from typing import Optional

class ArchConfig(BaseModel):
    n_layers     : Optional[int]   = 3 # number of encoder layers
    n_heads      : Optional[int]   = 16 # number of heads
    d_model      : Optional[int]   = 16 # dimension of model
    d_ff         : Optional[int]   = 128 # dimension of fully connected network
    attn_dropout : Optional[float] = 0.0 # dropout applied to the attention weights
    dropout      : Optional[float] = 0.0 # dropout applied to all linear layers in the encoder except q,k&v projections
    patch_len    : Optional[int]   = 24 # length of the patch applied to the time series to create patches
    stride       : Optional[int]   = 24 # stride used when creating patches
    padding_patch: Optional[bool]  = "True" # padding_patch

class HyperParams(BaseModel):
    arch_config  : Optional[ArchConfig] = None
    batch_size   : Optional[int] = 16  # batch size
    fcst_history : Optional[int] = 400 # forecast history
    fcst_horizon : Optional[int] = 8   # forecast horizon

