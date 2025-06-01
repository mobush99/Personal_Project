import torch
import torch.nn as nn


class AbstractRecSys(nn.Module):
    def __init__(self, args, special_args):
        super(AbstractRecSys, self).__init__()