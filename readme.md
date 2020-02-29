
#Prepare
sudo apt-get install -y rar unrar
# brew install unrar for mac



# Convert dicom to numpy

## Usage
python customer/dicom2nii.py

## Python Version
tmp = np.load(test.npz)
tmp = tmp.f.arr_0
plt.imshow(tmp[0])

## 字段解释
sid: 对应于numpy的第一维
series: 对应于文件夹名字
SliceLocation: slice 对应位置


# Others


## Ubuntu

https://askubuntu.com/questions/1043618/how-do-i-install-dcm2niix



## Mac

https://www.nitrc.org/forum/message.php?msg_id=21470

# dicom2numpy
