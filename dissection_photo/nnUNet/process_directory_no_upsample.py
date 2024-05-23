import torch
from argparse import ArgumentParser
import os
import glob
import cv2
import numpy as np
import sys
sys.path.insert(0, os.path.split(__file__)[0])
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor

def main(args):

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Create output and temporary directories as needed
    if os.path.isdir(args.out_dir) is False:
        os.mkdir(args.out_dir)
    tempdir = args.out_dir + '/tmp/'
    if os.path.isdir(tempdir):
        os.system('rm -rf ' + tempdir)
    os.mkdir(tempdir)

    # List images
    g = sorted(glob.glob(os.path.join(args.in_dir,'*.JPG')) + \
        glob.glob(os.path.join(args.in_dir, '*.jpg')) + \
        glob.glob(os.path.join(args.in_dir, '*.PNG')) + \
        glob.glob(os.path.join(args.in_dir, '*.png')) + \
        glob.glob(os.path.join(args.in_dir, '*.TIF')) +
        glob.glob(os.path.join(args.in_dir, '*.tif')))

    # Downsample
    print('Downsampling ' + str(len(g)) + ' files')
    for input in g:
        I = cv2.imread(input)
        Id = cv2.resize(I, [0,0], fx = 0.2, fy = 0.2, interpolation=cv2.INTER_AREA)
        head, tail = os.path.split(input)
        cv2.imwrite(os.path.join(tempdir, tail[:-4] + '_0000.png'), Id[:, :, 2])
        cv2.imwrite(os.path.join(tempdir, tail[:-4] + '_0001.png'), Id[:, :, 1])
        cv2.imwrite(os.path.join(tempdir, tail[:-4] + '_0002.png'), Id[:, :, 0])

    # nnUnet
    print('Loading model')
    perform_everything_on_device = True if device=='cuda' else False
    predictor = nnUNetPredictor(device=torch.device(device), \
                                perform_everything_on_device=perform_everything_on_device, \
                                verbose=False, verbose_preprocessing=False)

    # This it for two reasons:
    # 1. speed (otherwise CPU takes forever).
    # 2. cpu crashes with multi-fold prediction
    if device=='cpu':
        predictor.initialize_from_trained_model_folder(args.model_path, use_folds=(0,))
    else:
        predictor.initialize_from_trained_model_folder(args.model_path, use_folds=(0, 1, 2, 3, 4))


    print('Predicting!')
    predictor.predict_from_files(tempdir, args.out_dir, save_probabilities=True)\

    print('Cleaning up')
    os.system('rm -rf ' + tempdir)

    print('All done')



if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("--in_dir", type=str, dest="in_dir", default=None)
    parser.add_argument("--out_dir", type=str, dest="out_dir", default=None)
    parser.add_argument("--model_path", type=str, dest="model_path", default=None)

    args = parser.parse_args()

    main(args)
