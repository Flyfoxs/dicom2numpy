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
    #print(f'{input_file}, {out_file}')


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
        pd.DataFrame().to_csv(f'{real_output}/done.csv')
        print(f'Done:{input_file}')
        return True




if __name__ == '__main__':

    # input_fold = '/Volumes/PhiHardisk /lung/My Passport'
    # output_fold = '/Volumes/PhiHardisk /lung_output'
    # tmp_fold = '/Volumes/PhiHardisk /tmp'
    #
    # input_fold = '/Users/felix/Documents/med_data/武汉肺科/input'
    # output_fold = '/Users/felix/Documents/med_data/武汉肺科/output'
    # tmp_fold =  '/Users/felix/Documents/med_data/武汉肺科/tmp'

    raw_fold = '/Volumes/My Passport/lung/raw'
    output_fold = '/Volumes/My Passport/lung/output'
    dicm_fold = '/Volumes/My Passport/lung/dicm'
    tmp_fold = '/Volumes/My Passport/lung/tmp'


    all_list = list(glob(f'{raw_fold}/**/*.rar', recursive=True))
    zip_list = list(glob(f'{raw_fold}/**/*.zip', recursive=True))
    all_list.extend(zip_list)
    for input_file in tqdm(sorted(all_list, reverse=True)):

        try:
            print(input_file)
            real_output = input_file.replace(raw_fold,dicm_fold)

            meta_file = f'{real_output}/done.csv'
            print(meta_file)
            if os.path.exists(meta_file):
                print(f'Already had done flag for archive file:{input_file}')
                continue
            os.makedirs(tmp_fold, exist_ok=True)
            extract(input_file, real_output)
        except Exception as e:
            print(f'Exception for file:{input_file}')
            raise e



