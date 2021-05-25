import pytorch_lightning as pl

import torch
from torch.utils.data import DataLoader, Dataset

import jsonlines
from PIL import Image
import random
import numpy as np

from dataset import OCRDataset


class Tokenizer:
    def ids2tokens(self, ids):
        return [[self.vocab[idx] for idx in seq if idx not in [self.go_token_idx, self.end_token_idx]] for seq in ids]

    def decode(self, ids):
        tokens = self.ids2tokens(ids)
        return self.detokenize(tokens)

    def tokens2ids(self, tokens):
        return [[self.token_to_idx[token] for token in seq] for seq in tokens]

    def pad(self, ids):
        max_len = max([len(seq) for seq in ids])
        bs = len(ids)
        padded_ids = self.end_token_idx * np.ones((bs, max_len), dtype=np.int8)
        mask = (padded_ids == padded_ids)
        for i in range(bs):
            for j in range(len(ids[i])):
                padded_ids[i, j] = ids[i][j]
                mask[i][j] = False
        return padded_ids, mask

    def encode(self, sentences):
        tokens = self.tokenize(sentences)
        ids = self.tokens2ids(tokens)
        return self.pad(ids)


class CharTokenizer(Tokenizer):
    def __init__(self, hparams):
       self.vocab = ["GO", "END"] + list(open("./ressources/charset.txt", 'r').read())
       self.token_to_id = {token: i for i, token in enumerate(self.vocab)}
       self.go_token_idx = self.token_to_idx["GO"]
       self.end_token_idx = self.token_to_idx["END"]

    def tokenize(self, sentences):
        return [list(seq) for seq in sentences]

    def detokenize(self, tokens):
        return [''.join(seq) for seq in tokens]


def normalize_imgs(imgs):
    return [(img/255.) - 0.5 for img in imgs]


def pad_imgs(imgs):
    bs = len(imgs)
    shapes = [img.shape for img in imgs]
    channels = shapes[0][2]
    max_h = max([s[0] for s in shapes])
    max_w = max([s[1] for s in shapes])
    padded_imgs = np.zeros((bs, channels, max_h, max_w), dtype=np.float64)
    mask = (padded_imgs == padded_imgs)
    for n in range(bs):
        for h in range(shapes[bs][0]):
            for w in range(shapes[bs][1]):
                for c in range(channels):
                    padded_imgs[n, c, h, w] = imgs[n][h, w, c]
                    mask[n, c, h, w] = False
    return padded_imgs, mask


class OCRDataModule(pl.LightningDataModule):
    def __init__(self, hparams, folder_path, tokenizer):
        super().__init__()
        self.hparams = hparams
        self.tokenizer = tokenizer
        self.folder_path = folder_path

    def collate_fn(self, batch):
        imgs = [el['raw_img'] for el in batch]
        tgts = [el['raw_label'] for el in batch]
        imgs = normalize_imgs(imgs)
        imgs, img_mask = pad_imgs(imgs)
        tgts, tgt_mask = self.tokenizer.encode(tgts)

        return {'img': torch.from_numpy(imgs),
                'img_padding_mask': torch.from_numpy(img_mask),
                'tgt': torch.from_numpy(tgts),
                'tgt_padding_mask': torch.from_numpy(tgt_mask)}

    def setup(self, stage=None):
        if stage in (None, 'fit'):
            self.train_dataset = OCRDataset(self.folder_path + 'train.jsonl', self.hparams)
            self.val_dataset = OCRDataset(self.folder_path + 'val.jsonl', self.hparams, is_train=False)

        if stage in (None, 'test'):
            self.test_dataset = OCRDataset(self.folder_path + 'test.jsonl', self.hparams, is_train=False)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.hparams.bs, shuffle=True, collate_fn=self.collate_fn)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.hparams.bs, collate_fn=self.collate_fn)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.hparams.bs, collate_fn=self.collate_fn)
