from glob import glob
import os, sys
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def get_nii(input_fold, output_fold):
    base_fold = f'{input_fold}/**/*.dcm'
    print(base_fold)
    sub_fold = set([os.path.dirname(file) for file in glob(base_fold, recursive=True)])

    meta = []

    for sn, series in enumerate(sub_fold):
        # print(series)
        try:
            file_list = sorted(glob(f'{series}/*.dcm'))
            file_cnt = len(file_list)
            img_numpy = None
            for sid, instance in enumerate(file_list):
                # print(sn, instance)
                ds = pydicom.dcmread(instance)
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
                    img_numpy = img
                meta.append({
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
            save_path = series.replace(input_fold, output_fold)
            os.makedirs(save_path, exist_ok=True)
            filename = os.path.basename(save_path)
            save_path = f'{save_path}/{filename}'
            np.savez_compressed(save_path, img_numpy)
            print(save_path)
            # break
        except Exception as e:
            pass
            raise (e)

    df = pd.DataFrame(meta)
    df.to_csv(f'{output_fold}/meta.csv', index=None)
    return df

if __name__ == '__main__':
    input_fold = '/Users/felix/Documents/med_data'
    output_fold = '/Users/felix/Documents/output_dir'


    input_fold = '/Users/felix/Downloads/CT'
    output_fold = '/Users/felix/Downloads/CT_OUTPUT'

    df = get_nii(input_fold, output_fold)
    print(df.head())