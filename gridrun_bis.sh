python3 train.py --model_type satrn-large-resnet --datasets full_words --resize --width -1 --gpus 4 --bs 16 --epochs 4 --save_best_model --lr 5e-6 --exp_name full_words --num_workers 4 --resume_from './saved_models/full_words-epoch=02-val_cer=0.12.ckpt'
#python3 train.py --model_type satrn-large --datasets synthtext+mjsynth --resize --grayscale --gpus 0 --bs 16 --epochs 1 --load_weights_from './saved_models/exp-epoch=00-val_acc=0.98.ckpt' --run_test
