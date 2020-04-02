from pyforest import *
from glob import glob
import os, sys
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from glob import glob
from tqdm import tqdm
import os, sys
import pydicom
import numpy as np
import pandas as pd
import rarfile
import zipfile

import shutil
import hashlib


def adjust_np_array(array, df):

    # print(f'/share/data/lung/lung_ct_npy_v2/**/*{npz_hash}.npz')
    # npz = glob(f'/share/data/lung/lung_ct_npy_v2/**/*{npz_hash}.npz', recursive=True)[0]
    # npz_hash = npz_hash.split('_')[-1].split('.')[0]
    #
    # tmp = np.load(npz)
    # array = tmp.f.arr_0
    #
    # #print(npz)
    # #npz_name = os.path.basename(npz)
    # npz_path = os.path.dirname(npz)
    # meta_file = f'{npz_path}/meta.csv'
    # df = pd.read_csv(meta_file)
    # df = df.loc[df.file_md5 == npz_hash].sort_values('SliceLocation', ascending=False)
    df = df.sort_values(['file_md5', 'series', 'SliceLocation'], ascending=False)
    new_array = np.zeros_like(array)

    for new_sn, old_sn in enumerate(df.sid):
        new_array[new_sn] = array[old_sn]

    return new_array



def get_match_list(input_fold):
    ex_list = list(glob(f'{input_fold}/**/*0000*', recursive=True))

    dcm_list0 = list(glob(f'{input_fold}/**/*.DCM', recursive=True))
    dcm_list1 = list(glob(f'{input_fold}/**/*.dcm', recursive=True))
    ex_list2 = list(glob(f'{input_fold}/**/000*', recursive=True))
    ex_list.extend(dcm_list0)
    ex_list.extend(dcm_list1)
    ex_list.extend(ex_list2)
    ex_list = [path for path in ex_list if os.path.isfile(path)]
    # if len(ex_list) == 0:
    #     print(f'Can not find DCM file with {input_fold}, Exception')
    return list(set(ex_list))



def get_nii(input_fold, output_fold):
    os.makedirs(output_fold, exist_ok=True)
    meta_file = f'{output_fold}/meta.csv'
    if os.path.exists(meta_file):
        df = pd.read_csv(meta_file)
        print(f'Already had {len(df)} dicom files save to npz')
        return len(df)
    else:
        print(f'Begin to process:{input_fold}')

    # base_fold = f'{input_fold}/**/*.dcm'
    # base_fold = f'{input_fold}/**/*000*'
    sub_fold = set([os.path.dirname(file) for file in get_match_list(input_fold)])

    meta = []

    for sn, series in enumerate(sub_fold):
        print(series)
        try:
            file_list = get_match_list(series)
            if file_list:
                print(f'Can not find DCM from fold:{series}')
            file_cnt = len(file_list)
            img_numpy = None

            zip_path_hash = hashlib.md5(f'{output_fold}{series}'.encode()).hexdigest()

            print(f'MAP, {zip_path_hash}, {series}')
            for sid, instance in enumerate(file_list):
                #print(sn, instance)
                try:
                    ds = pydicom.dcmread(instance, force=True)
                    #ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
                    ds.file_meta.PlanarConfiguration = 0
                    img = ds.pixel_array

                    #
                     # .shape
                    #             sid = ds.SeriesInstanceUID
                    #             z = ds.SpacingBetweenSlices  #= z
                    #             [x, y] = ds.PixelSpacing
                    # print(f'seriesFold:{os.path.basename(file)},  PixelSpacing={ds.PixelSpacing} , SpacingBetweenSlices={ds.SpacingBetweenSlices}, Series:')
                    # print(img.shape)
                    if file_cnt > 1:
                        img_numpy = np.zeros((file_cnt, 512, 512)) if img_numpy is None else img_numpy
                        img_numpy[sid] = img
                    else:
                        img_numpy = np.zeros((file_cnt, 512, 512)) if img_numpy is None else img_numpy
                        img_numpy[0] = img
                except ValueError as e:
                    print(file_cnt, img_numpy.shape, img.shape, img_numpy.dtype, img.dtype, instance)
                    if img_numpy.shape[-1] != img.shape[-1] or img_numpy.shape[-2] != img.shape[-2]:
                        import cv2
                        if img.ndim == 3:
                            print(f'Exception(Shape Error), The image shape is {img.ndim} for file:{instance}')
                            img_numpy[sid] = cv2.resize(img[:,:,0], (512, 512)).astype(int)

                        else:
                            img_numpy[sid] = cv2.resize(img, (512, 512)).astype(int)
                    else:
                        print(f'Exception(ValueError) on file:{instance}')
                    print(e)
                    continue
                except AttributeError as e :
                    print(f'Exception(AttributeError) on file:{instance}')
                    print(e)
                    continue
                except Exception as e:
                    print(f'Exception on file:{instance}')
                    raise(e)

                select_col = [
                    'SpacingBetweenSlices',
                    'ImagePositionPatient',
                    'SliceLocation',
                    'SeriesNumber',
                    'InstanceNumber',
                    'PixelSpacing',
                    'RescaleIntercept',
                    'RescaleSlope',
                    'StudyDate',
                    'StudyTime',
                    'PatientID',
                    'StudyID',
                    'StationName',
                    'DeviceSerialNumber'
                ]

                select_dict = [(select_col, ds.get(item) if item in dir(ds) else None) for item in select_col]
                static_dict = {
                    'file_md5': zip_path_hash,
                    'series': os.path.basename(series),
                    'sid': sid,  # Z-index
                    'StudyInstanceUID': ds.StudyInstanceUID,
                    'SeriesInstanceUID': ds.SeriesInstanceUID,
                    'SOPInstanceUID': ds.SOPInstanceUID,
                    'PatientName': hashlib.md5(ds.PatientName.encode()).hexdigest() if 'PatientName' in dir(ds) else None ,
                }

                static_dict.update(dict(select_dict))
                meta.append(static_dict)


            #save_path = series.replace(input_fold, output_fold)
            # os.makedirs(save_path, exist_ok=True)
            #filename = os.path.basename(save_path)

            #save_path = f'{save_path}/{len(file_list):04}_{zip_path_hash}'
            save_path = f'{output_fold}/{len(file_list):04}_{zip_path_hash}'
            adjust_np_array(img_numpy, pd.DataFrame(meta))
            np.savez_compressed(save_path, img_numpy)
            print(f'{len(file_list)} dcm convert to npy and save_to {save_path}')
            # break
        except Exception as e:
            pass
            raise (e)
    if meta:
        df = pd.DataFrame(meta)
        df = df.sort_values(['file_md5', 'series', 'SliceLocation'], ascending=False)
        df.to_csv(meta_file, index=None)
        return df

if __name__ == '__main__':

    """"
    python 
    """
    # input_fold = '/Users/felix/Documents/med_data'
    # output_fold = '/Users/felix/Documents/output_dir'
    #
    #
    # input_fold = '/Users/felix/Downloads/CT'
    # output_fold = '/Users/felix/Downloads/CT_OUTPUT'
    #
    # input_fold = '/Users/felix/Downloads/CT'
    # output_fold = '/Users/felix/Downloads/CT_OUTPUT'

    dicm_fold = '/Volumes/My Passport/lung/dicm'
    output_fold = '/Volumes/My Passport/lung/output'


    for file in tqdm(glob(f'{dicm_fold}/**/done.csv',recursive=True)):
        pass

        file = file.replace('done.csv', '')
        real_output = file.replace(dicm_fold, output_fold)

        # meta_file = f'{real_output}/meta.csv'
        # if os.path.exists(meta_file):
        #     print(meta_file)
        #     df = pd.read_csv(meta_file)
        #     print(f'Already had {len(df)} dicom files save to npz')
        #     continue
        df = get_nii(file, real_output)
    print(f'Done for {dicm_fold}, {output_fold}')
    # print(df.head())