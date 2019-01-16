# author='lwz'
# coding:utf-8
# !/usr/bin/env python3
import json
import os
import pickle as pkl
from warnings import warn
import time
from Send_msg import get_models, push_msg2models
from file_daily_manager import file_daily_manager


'''
文件监视器
监控文件变化
'''


class file_monitor(object):
    def __init__(self, conf_file='.\\tmp\\file_monitor.json', is_test=False):
        with open(conf_file, 'r') as fp:
            config_msg = json.load(fp, encoding='utf-8')
        self.cache_file = config_msg['cache_file']
        self.file_list = config_msg['file_list']
        self.models = get_models(is_test)  # 获取发送者类别
        self.is_test = is_test

        file_daily_manager(self.file_list.values())
        file_daily_manager(self.cache_file)
        
        if self.is_test:
            print("start test")
            self.file_updatetime = dict(zip(self.file_list.keys(), [0] * len(self.file_list)))
            self.file_read_rows = dict(zip(self.file_list.keys(), [0] * len(self.file_list)))
        elif os.path.exists(self.cache_file):
            print("we load cache file: ", self.cache_file)
            self.file_updatetime, self.file_read_rows = self.load_cache()
        else:
            print("we create cache file: ", self.cache_file)
            self.file_updatetime = dict(zip(self.file_list.keys(), [0] * len(self.file_list)))
            self.file_read_rows = dict(zip(self.file_list.keys(), [0] * len(self.file_list)))

    def load_cache(self):
        with open(self.cache_file, 'rb') as f:
            a, b = pkl.load(f)
        return a, b

    def dump_cache(self):
        with open(self.cache_file, 'wb') as f:
            pkl.dump((self.file_updatetime, self.file_read_rows), f)

    def create_file(self):
        for name in self.file_list.keys():
            f = open(self.file_list[name], 'w')
            f.close()
            print("we had create file: ", self.file_list[name])

    def get_time(self, time_=None):
        if time_ is None:
            time_ = time.time()

        clock = time.localtime(time_)
        return clock[3] * 10000 + clock[4] * 100 + clock[5]

    def get_day(self, time_=None):
        if time_ is None:
            time_ = time.time()

        clock = time.localtime(time_)
        return clock[0] * 10000 + clock[1] * 100 + clock[2]

    def main(self):
        report_time = 0
        if self.is_test:
            self.monitor()
            return
            
        clock = self.get_time()

        while clock < 151500:
            if clock < 90000:
                time.sleep(30)
                clock = self.get_time()
                print("{} please wait until 9:00:00".format(clock))
                continue
            else:
                self.monitor()
                self.dump_cache()
                time.sleep(1)

            if clock > report_time:
                timestr = time.strftime("%H:%M:%S", time.localtime())
                update_time = [{k: self.get_time(self.file_updatetime[k])} for k in self.file_updatetime.keys()]
                print("{} \n{}\n{}".format(timestr, update_time, self.file_read_rows))
                report_time = self.get_time(time.time()+30)

            clock = self.get_time()

        time.sleep(10)

    def monitor(self):
        update_context = dict()                                             # {name: context}
        for name in self.file_list:
            updatetime = os.path.getmtime(self.file_list[name])
            if updatetime > self.file_updatetime[name]:
                self.file_updatetime[name] = updatetime
                try:
                    f = open(self.file_list[name], 'r', encoding='utf-8')
                    contexts = f.read()
                except UnicodeDecodeError:
                    f = open(self.file_list[name], 'r', encoding='gbk')
                    contexts = f.read()
                    
                lines = contexts.split("\n")

                if lines[-1] is not '':  # 最后一个是''
                    print("last line error: ", print(lines[-1]))

                update_context[name] = lines[self.file_read_rows[name]:-1]
                self.file_read_rows[name] = len(lines[:-1])
                f.close()
                    
        if len(update_context) > 0:
            print("find file change: ", update_context.keys())
            push_msg2models(self.models, update_context)

if __name__ == '__main__':
    fm = file_monitor()
    fm.main()
