import hashlib

from file_cache import *

from customer.dicom2nii import get_match_list
from pandas.errors import EmptyDataError

todo = glob(f'/Volumes/My Passport/lung/dicm/**/done.csv', recursive=True)
np.random.shuffle(todo)
todo_filter =[]
for done_file in todo:
    meta_file = done_file.replace('done.csv', 'meta.csv')
    if os.path.exists(meta_file):
        try:
            df = pd.read_csv(meta_file)
        except EmptyDataError as e:
            df = pd.DataFrame()
        except Exception as e:
            print(f'Exception on file:{meta_file}, with {e}')
            raise e
            #df = pd.DataFrame()
        print(f'Already have {len(df)} file in meta:{meta_file}')
    else:
        todo_filter.append(done_file)
    
for done_file in tqdm(todo_filter, total=len(todo_filter)):
    print(f'Processing:{done_file}')
    try: 
        input_fold = os.path.dirname(done_file)
        file_list = get_match_list(input_fold)
    
        meta = []
    
        for sid, file in enumerate(file_list):
            # print(sn, instance)
            try:
                ds = pydicom.dcmread(file, force=True)
                if 'StudyInstanceUID' not in ds:
                    print(f'It is not a real dicom file: {file}')
                    continue
            except Exception as e:
                print(f'Exception on file:{file}, {type(e)}')
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
    
            try:
                select_dict = [(item, ds.get(item) if item in dir(ds) else None) for item in select_col]
                static_dict = {
                    'dicom_path': file,
                    'StudyInstanceUID': ds.StudyInstanceUID,
                    'SeriesInstanceUID': ds.SeriesInstanceUID,
                    'SOPInstanceUID': ds.SOPInstanceUID,
                    'PatientName': hashlib.md5(ds.PatientName.encode()).hexdigest() if 'PatientName' in dir(ds) else None,
                }
            except Exception as e :
                print(f'Exception on file:{file}, {type(e)}')
                raise e
    
            static_dict.update(dict(select_dict))
            meta.append(static_dict)
    
        df = pd.DataFrame(meta)
        if len(df) > 0:
            df = df.sort_values(['PatientID', 'StudyDate', 'StudyInstanceUID', 'SeriesInstanceUID',  'SliceLocation'], ascending=False)
        df.to_csv(meta_file, index=False)
    except Exception as e:
        print(f'Exception on done_file:{done_file}, {type(e)}')
        raise e