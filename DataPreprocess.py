import os
import json
import h5py
import numpy as np
from DDB.Data import Reader
from DDB.Service import Query
from scipy import signal
import traceback


class DataGenerator:
    """
    生成训练数据集所需的数据, 截取起始时间到破裂或下降点的诊断, 经过重采样、归一化之后保存到hdf5文件
    """
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'Config.json'), 'r') as json_file:
            config = json.load(json_file)
        self._shots = dict()

        self._shots['train'] = config['shots']['train']
        self._shots['test'] = config['shots']['test']
        self._shots['val'] = config['shots']['test']

        self._tags = config['diagnosis']['tags']
        # 截取信号的起始时间(ms)
        self._start_time = config['diagnosis']['start_time']
        # 重采样的信号频率(kHz)
        self._sample_rate = config['diagnosis']['sample_rate']
        self._normalized = config['normalized']
        self._directory = config['directory']
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

        # 复制配置文件到输出路径
        with open(os.path.join(self._directory, 'Config.json'), 'w') as json_file:
            json.dump(config, json_file, indent=4)
        exit()
        ddb = Query()
        if self._normalized:
            self._normalize_param = ddb.get_normalize_parm(self._tags)

    def generate(self):
        data_reader = Reader()
        ddb = Query()
        for categories, shots in self._shots.items():
            if not os.path.exists(os.path.join(self._directory, categories)):
                os.makedirs(os.path.join(self._directory, categories))
            for shot in shots:
                print(shot)
                try:
                    tags = ddb.tag(shot)
                    if tags['IsDisrupt']:
                        t1 = tags['CqTime']
                    else:
                        t1 = tags['RampDownTime']
                    new_dig_length = int((t1 * 1000 - self._start_time) * self._sample_rate)
                    data = data_reader.read_many(shot, self._tags)
                    digs = []
                    for tag, (dig, time) in data.items():
                        dig = dig[(self._start_time/1000 <= time) & (time <= t1)]
                        # 归一化
                        if self._normalized:
                            dig = (dig - self._normalize_param[tag]['min']) / \
                                  (self._normalize_param[tag]['max'] - self._normalize_param[tag]['min'])
                        # 重采样
                        digs.append(signal.resample(dig, new_dig_length))

                    digs = np.array(digs)

                    f = h5py.File(os.path.join(self._directory, categories, '{}.hdf5'.format(shot)))
                    dataset = f.create_dataset('diagnosis', data=digs)
                    for key, value in tags.items():
                        dataset.attrs.create(key, value)
                    f.close()

                except Exception as e:
                    print(e)
                    traceback.print_exc()


if __name__ == '__main__':
    data_generator = DataGenerator()
    data_generator.generate()
