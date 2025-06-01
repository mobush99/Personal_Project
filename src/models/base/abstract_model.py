from cmath import cos
import numpy as np
import math
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parameter import Parameter
from scipy.special import lambertw
import scipy.sparse as sp

"""
This module has been inspired by Agent4Rec
"""

class AbstractModel(nn.Module):
    def __init__(self, args, data):
        super(AbstractModel, self).__init__()
        print("AbstractModel Initiation Activated")

        self.name = args.modeltype
        self.args = args
        self.device = torch.device(args.cuda)
        self.data = data

        self.Graph = data.getSparseGraph()

        #HyperParameters
        self.emb_dim = args.embed_size
        self.decay = args.regs
        self.train_norm = args.train_norm
        self.pred_norm = args.pred_norm
        self.n_layers = args.n_layer    # 0:MF
        self.modeltype = args.modeltype
        self.batch_size = args.batch_size

        self.init_embedding()

    def init_embedding(self):
        self.embed_user = nn.Embedding(self.data.n_users, self.emb_dim)
        self.embed_item = nn.Embedding(self.data.n_items, self.emb_dim)

        nn.init.xavier_uniform_(self.embed_user.weight)
        nn.init.xavier_uniform_(self.embed_item.weight)

    def compute(self):
        users_emb = self.embed_user.weight
        items_emb = self.embed_item.weight
        all_emb = torch.cat([users_emb, items_emb])

        embs = [all_emb]
        g_droped = self.Graph

        for layer in range(self.n_layers):
            print(g_droped.device, all_emb.device)
            all_emb = torch.sparse.mm(g_droped, all_emb)
            embs.append(all_emb)
        embs = torch.stack(embs, dim=1)

        meaned_embs = torch.mean(embs, dim=1)
        users, items = torch.split(meaned_embs, [self.n_users, self.n_items])

        return users, items

    def forward(self):
        # MUST BE IMPLEMENTED: at descendent classes
        raise NotImplementedError

    def predict(self, users, items=None):
        if items is None:
            items = list(range(self.data.n_items))
        all_users, all_items = self.compute()
        users = all_users[torch.tensor(users).cuda(self.device)]
        items = all_items[torch.tensor(items).cuda(self.device)]
        if self.pred_norm == True:
            users = F.normalize(users, dim = -1)
            items = F.normalize(items, dim = -1)
        items = torch.transpose(items, 0, 1)
        rate_batch = torch.matmul(users, items)
        return rate_batch.cpu().detach().numpy()
    



