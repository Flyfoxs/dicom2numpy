#coding=utf-8
from glob import glob
import os, sys
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import rarfile
import zipfile

import shutil
import hashlib
from customer.dicom2nii import *
from tqdm import tqdm


def extract(input_file, out_file):
    print(f'{input_file}')

    if input_file.endswith('rar'):
        rf = rarfile.RarFile(input_file)
        rf.extractall(out_file)
    elif input_file.endswith('zip'):
        extracting = zipfile.ZipFile(input_file)
        extracting.extractall(out_file)

    if out_file in input_file:
        os.remove(input_file)
        print(f'rm file:{input_file}')

    all_list = list(glob(f'{out_file}/**/*.rar', recursive=True))
    zip_list = list(glob(f'{out_file}/**/*.zip', recursive=True))
    all_list.extend(zip_list)

    if all_list:
        for file in all_list:
            if os.path.exists(file):
                extract(file, out_file)
    else:
        return True


if __name__ == '__main__':

    input_fold = '/Volumes/PhiHardisk /lung/My Passport'
    output_fold = '/Volumes/PhiHardisk /lung_output'
    tmp_fold = '/Volumes/PhiHardisk /tmp'

    input_fold = '/Users/felix/Documents/med_data/武汉肺科/input'
    output_fold = '/Users/felix/Documents/med_data/武汉肺科/output'
    tmp_fold =  '/Users/felix/Documents/med_data/武汉肺科/tmp'

    input_fold = '/Volumes/My Passport/lung/raw'
    output_fold = '/Volumes/My Passport/lung/output'
    tmp_fold = '/Volumes/My Passport/lung/tmp'


    all_list = list(glob(f'{input_fold}/**/*.rar', recursive=True))
    zip_list = list(glob(f'{input_fold}/**/*.zip', recursive=True))
    all_list.extend(zip_list)
    for input_file in tqdm(sorted(all_list)):
        print(input_file)
        tmp_output_fold = input_file
        tmp_output_fold = tmp_output_fold.replace(input_fold, output_fold)

        meta_file = f'{tmp_output_fold}/meta.csv'
        if os.path.exists(meta_file):
            print(meta_file)
            df = pd.read_csv(meta_file)
            print(f'Already had {len(df)} dicom files save to npz')
            continue

        if os.path.exists(tmp_fold):
            shutil.rmtree(tmp_fold)
        os.makedirs(tmp_fold, exist_ok=True)

        extract(input_file, tmp_fold)

        print('=======',tmp_output_fold)
        get_nii(tmp_fold, tmp_output_fold)

        if os.path.exists(tmp_fold):
            shutil.rmtree(tmp_fold)


