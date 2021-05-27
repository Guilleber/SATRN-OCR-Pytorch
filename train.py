import pytorch_lightning as pl

import torch

import argparse

from datamodule import OCRDataModule, CharTokenizer
from model import SATRNModel
import parameters


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model_type', type=str, help="Model type: must match one in parameters.py")
    parser.add_argument('-d', '--datasets', type=str, help="Datasets to use for training. Must match one in parameters.py")
    perser.add_argument('--exp_name', type=str, default=None)
    parser.add_argument('--load_weights_from', type=str, default=None)
    
    parser.add_argument('--bs', type=int, help="mini-batch size", default=4)
    parser.add_argument('--gpus', type=int, default=-1)
    parser.add_argument('-h', '--height', type=int, default=32)
    parser.add_argument('-w', '--width', type=int, default=100)

    parser.add_argument('--lr', type=float, help="learning rate", default=3e-4)

    parser.add_argument('--grayscale', help="transform images to grayscale", action='store_true')
    parser.add_argument('--resize', help="resize images to [--width] x [--height]", action='store_true')
    parser.add_argument('--save_best_model', action='store_true')

    args = parser.parse_args()

    args = argparse.Namespace(**vars(args), **parameters.models[args.model_type])

    tokenizer = CharTokenizer()
    args.vocab_size = tokenizer.vocab_size
    args.go_token_idx = tokenizer.go_token_idx
    args.end_token_idx = tokenizer.end_token_idx

    datamodule = OCRDataModule(args, parameters.datasets[args.datasets], tokenizer)
    model = SATRNModel(args)

    # reproducibility
    pl.seed_everything(42, workers=True)

    # saves best model
    callbacks = []
    checkpoint_callback = pl.ModelCheckpoint(monitor='val_acc',
                                             dirpath='./saved_models/',
                                             filename=args.exp_name + '-{epoch:02d}-{val_acc:2.2f}',
                                             save_top_k=1,
                                             verbose=True,
                                             mode='max')
    callbacks.append(checkpoint_callback)

    # early stopping
    early_stopping_callback = pl.EarlyStopping(monitor='val_acc',
                                               min_delta=0.0,
                                               patience=2,
                                               mode='max')
    callbacks.append(early_stopping_callback)

    trainer = pl.Trainer(gpus=args.gpus,
                         accelerator='dp',
                         checkpoint_callback=args.save_best_model,
                         callbacks=callbacks)
    trainer.fit(model, datamodule)
