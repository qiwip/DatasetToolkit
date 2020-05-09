# 说明

## 1.需要的python包

```bash
pip install h5py
pip install scipy
pip install numpy
```
因为程序依赖DDB, 所以还要安装MongoDB的py包:

```bash
pip instal pymongo
```

## 2.用法

先修改配置文件Config.json

```json
{
    "shots": {
        
        "train": [1, 2, 3],  # 训练集炮号
        "test": [4, 5],      # 测试集炮号
        "val": [6, 7, 8]     # 验证集炮号
    },
    "diagnosis": {
        "tags": [
            "\\ip",
            "\\Bt",
            "\\axuv_ca_01",
            "\\vs_c3_aa001",
            "\\vs_ha_aa001",
            "\\sxr_cb_024",
            "\\sxr_cc_049",
            "\\Ivfp",
            "\\Ihfp",
            "\\MA_POL_CA01T",
            "\\MA_POL_CA02T",
            "\\MA_POL_CA23T",
            "\\MA_POL_CA24T"
        ],
        "sample_rate": 100,      # 重采样频率(kHz)
        "start_time": 50         # 要保存的诊断的起始时间(ms)
    },
    "normalized": true,          # 是否归一化
    "directory": "./temp/hdf5"   # 输出文件的保存目录
}

```
然后运行```DataPreprocess.py```
后台运行可以执行如下命令:
```bash
nohup python -u DataPreprocess.py > stdio.out 2>&1 &
```
程序运行的输出将被保存至文件stdio.out中.

程序会在配置文件```directory```所设定的目录下新建```train```, ```test```和```val```三个文件夹，分别存放生成的hdf5文件.

其中, HDF5文件包含一个名为```diagnosis```的dataset, data为二维的numpy数组, shape为```[诊断个数, 诊断长度]```. HDF5的Attributes存放了这一炮的破裂相关信息. 所以, 读取生成的诊断数据可以使用如下代码:

```python
import h5py

path = './hdf5/1066343.hdf5'
f = h5py.File(path, 'r')
dataset = f.get('diagnosis')
data = dataset[:]
print(dataset.attrs.get('IsDisrupt'))
```

然后就可以进行数据切片之类的操作.
