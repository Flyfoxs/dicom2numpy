from glob import glob
import os, sys
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from glob import glob
import os, sys
import pydicom
import numpy as np
import pandas as pd
import rarfile
import zipfile

import shutil
import hashlib



def get_match_list(input_fold):
    ex_list = list(glob(f'{input_fold}/**/*000*', recursive=True))
    dcm_list = list(glob(f'{input_fold}/**/*.DCM', recursive=True))
    ex_list.extend(dcm_list)
    if ex_list:
        return ex_list
    else:
        raise Exception(f'Can not find DCM file with {input_fold}')


def get_nii(input_fold, output_fold):
    os.makedirs(output_fold, exist_ok=True)
    meta_file = f'{output_fold}/meta.csv'
    if os.path.exists(meta_file):
        df = pd.read_csv(meta_file)
        print(f'Already had {len(df)} dicom files save to npz')
        return len(df)

    # base_fold = f'{input_fold}/**/*.dcm'
    # base_fold = f'{input_fold}/**/*000*'
    sub_fold = set([os.path.dirname(file) for file in get_match_list(input_fold)])

    meta = []

    for sn, series in enumerate(sub_fold):
        # print(series)
        try:
            file_list = get_match_list(series)
            file_cnt = len(file_list)
            img_numpy = None
            zip_path_hash = hashlib.md5(f'{output_fold}{series}'.encode()).hexdigest()
            for sid, instance in enumerate(file_list):
                # print(sn, instance)

                ds = pydicom.dcmread(instance, force=True)
                ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
                img = ds.pixel_array  # .shape
                #             sid = ds.SeriesInstanceUID
                #             z = ds.SpacingBetweenSlices  #= z
                #             [x, y] = ds.PixelSpacing
                # print(f'seriesFold:{os.path.basename(file)},  PixelSpacing={ds.PixelSpacing} , SpacingBetweenSlices={ds.SpacingBetweenSlices}, Series:')
                # print(img.shape)
                if file_cnt > 1:
                    img_numpy = np.zeros((file_cnt, *img.shape)) if img_numpy is None else img_numpy
                    # print(file_cnt, img_numpy.shape, img.shape, img_numpy.dtype, img.dtype)
                    img_numpy[sid] = img
                else:
                    img_numpy = np.zeros((file_cnt, *img.shape)) if img_numpy is None else img_numpy
                    img_numpy[0] = img
                meta.append({
                    'file_md5': zip_path_hash,
                    'series': os.path.basename(series),
                    'sid': sid,  # Z-index
                    'StudyInstanceUID': ds.StudyInstanceUID,
                    'SeriesInstanceUID': ds.SeriesInstanceUID,
                    'SOPInstanceUID': ds.SOPInstanceUID,
                    'SpacingBetweenSlices': ds.SpacingBetweenSlices if 'SpacingBetweenSlices' in dir(ds) else None,

                    'ImagePositionPatient': ds.ImagePositionPatient if 'ImagePositionPatient' in dir(ds) else None,
                    'SliceLocation': ds.SliceLocation if 'SliceLocation' in dir(ds) else None,
                    'PixelSpacing': ds.PixelSpacing if 'PixelSpacing' in dir(ds) else None,
                    'RescaleIntercept': ds.RescaleIntercept if 'RescaleIntercept' in dir(ds) else None,
                    'RescaleSlope': ds.RescaleSlope if 'RescaleSlope' in dir(ds) else None,

                })
            #save_path = series.replace(input_fold, output_fold)
            # os.makedirs(save_path, exist_ok=True)
            #filename = os.path.basename(save_path)

            #save_path = f'{save_path}/{len(file_list):04}_{zip_path_hash}'
            save_path = f'{output_fold}/{len(file_list):04}_{zip_path_hash}'
            np.savez_compressed(save_path, img_numpy)
            print(f'{len(file_list)} dcm convert to npy and save_to {save_path}')
            # break
        except Exception as e:
            pass
            raise (e)

    df = pd.DataFrame(meta)
    df.to_csv(meta_file, index=None)
    return df

if __name__ == '__main__':
    input_fold = '/Users/felix/Documents/med_data'
    output_fold = '/Users/felix/Documents/output_dir'


    input_fold = '/Users/felix/Downloads/CT'
    output_fold = '/Users/felix/Downloads/CT_OUTPUT'

    df = get_nii(input_fold, output_fold)
    print(df.head())