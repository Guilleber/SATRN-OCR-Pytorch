python3 train.py --model_type satrn-large-resnet --datasets full_words --resize --width -1 --gpus 4 --bs 16 --epochs 4 --lr 5e-6 --exp_name hc_full --num_workers 4
#python3 train.py --model_type satrn-large --datasets synthtext+mjsynth --resize --grayscale --gpus 0 --bs 16 --epochs 1 --load_weights_from './saved_models/exp-epoch=00-val_acc=0.98.ckpt' --run_test
