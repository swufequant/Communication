# author='lwz'
# coding:utf-8
# !/usr/bin/env python3
import requests
import json
import os
import pandas as pd
import pickle as pkl
from warnings import warn
import time


'''
Warning-----所有警告的基类

DeprecationWarning----用于不再维护的特性

PendingDeprecationWarning----用于很快会废弃的特性

SyntaxWarning---用于有问题的语法

RuntimeWarning----用于运行时可能导致问题的事件

FutureWarning----关于将来语言或者库中可能的改变的有关警告

ImportWarning 关于导入模块时出现的问题的警告

UnicodeWarning---关于Unicode文本中的问题的警告

UserWarning---来自用户代码的警告
'''


class Receiver(object):
    '''
    get_msg --> send_msg(translate_msg->get_change_dict->msg_generator) --> push_msg
    '''
    def __init__(self, template_file='.\\tmp\\api.json',
                 conf_file='.\\tmp\\Receiver.json', is_test=False):
        with open(conf_file, 'r') as fp:
            config_msg = json.load(fp, encoding='utf-8')

        self.receivers = config_msg["receivers"]
        self.files = config_msg["files"]
        self.url = config_msg["url"]

        with open(template_file, 'r', encoding='utf-8') as f:
            self.template = json.load(f)
        self.send_msg_num = [0] * len(self.files)
        self.send_msg_num_max = 4               # 最多一次发送消息行数
        self.send_msg_len_max = 100             # 最多一次发送消息字数
        self.is_test = is_test

    def translate_msg(self, text):
        '''
        将更新的字符串转化为字典
        :param msg: ["600057,象屿股份,8.48,11:23:57,5_1\n]"]
        :return: [{"first":"600057,象屿股份,8.48,11:23:57,5_1\n"}]
        '''
        return {"text": text}

    def get_change_dict(self, msgs):
        '''
        获取信息字典并生成json对象——多个
        :param
        msgs =   [{"first":"600057,象屿股份,8.48,11:23:57,5_1\n"}]
        :return
            "openid": "openid",
            "first": "前面文字",
            "keyword1": "行情讯息",
            "keyword2": "2018-01-10 20:55:04",
            "remark": "后面文字",
            "tourl": ""
        '''
        first = ''
        for msg in msgs:
            first += msg["text"]

        change_dict = {}
        for k in self.template.keys():
            change_dict[k] = self.template[k]

        change_dict["first"] = first
        change_dict["keyword2"] = get_timestr()

        return change_dict

    def translate_msgs(self, msg_contexts):
        '''
        将更新的字符串转化为字典
        :param msg: ["600057,象屿股份,8.48,11:23:57,5_1\n"]
        :return
            "openid": "openid",
            "first": "前面文字",
            "keyword1": "行情讯息",
            "keyword2": "2018-01-10 20:55:04",
            "remark": "后面文字",
            "tourl": ""
        '''
        msg_dicts = list()
        change_dicts = list()
        sum_len = 0
        for i, text in enumerate(msg_contexts):
            if len(text) > 0:
                msg_dict = self.translate_msg(text)
                if len(msg_dict) > 0:
                    msg_dicts.append(msg_dict)
                    
            sum_len += len(text)
            
            if (len(msg_dicts) == self.send_msg_num_max) or \
                sum_len >= self.send_msg_len_max or \
               ((i + 1 == len(msg_contexts)) and len(msg_dicts) > 0):
                change_dicts.append(self.get_change_dict(msg_dicts))
                msg_dicts = list()
                sum_len = 0

        return change_dicts

    def msg_generator(self, change_dicts):
        '''
        从字典生成json
        :param change_dict:  模板里需要改变的内容如{"openid":"0ox8"}
        :return: 消息模板（数据类型 json）
        '''
        msg_json_list = []
        for change_dict in change_dicts:
            msg_json = {"comm": change_dict}
            msg_json_list.append(msg_json)

        return msg_json_list

    def push_msg(self, byte_json):
        '''
        推送序列化的消息
        :param byte_json: 序列化的json
        :return: ok or error
        '''
        r = requests.post(self.url, data=byte_json)
        if r.text != 'ok':
            warn('failed to send msg: {}'.format(json.loads(byte_json)), UserWarning)
            print(r.text)
        return r.text

    def send_msg(self, msgs=list()):
        '''
        发送消息
        :param msgs:  消息 每一行算一条消息
        :return:
        '''
        rev_list = []
        change_dicts = self.translate_msgs(msgs)
        msg_templates = self.msg_generator(change_dicts)

        if self.is_test:
            print("版本:", self.name)
            print('receiver:')
            for receiver in self.receivers.keys():
                print(receiver, ', ')
            for msg_template in msg_templates:
                print(msg_template["comm"]["first"])
        else:
            for receiver in self.receivers.values():
                for msg_template in msg_templates:
                    msg_template["comm"]["openid"] = receiver
                    byte_json = json.dumps(msg_template)
                    rev_list.append(self.push_msg(byte_json))

        return rev_list

    def get_msg(self, msgs=dict()):
        '''
        接受信息
        :param msgs:  [{"code": "600057", "name": "象屿股份", "price": "8.48",
                         "clock": "11:23:57", "strategy_name": "5_1"
                        },
                       {"code": "000971", "name": "高升控股", "price": "15.6",
                        "clock": "14:33:45", "strategy_name": "4_1"
                       }]
        :return:  2 (num of msg we get)
        '''
        if len(msgs) == 0:
            print("msgs we get from file monitore is empty")
        elif not isinstance(msgs, dict):
            warn(UserWarning, "msgs we get from file monitore is not a dict")
            return 0

        rev_msg = []
        for fn in self.files:  # 提取对应文件的更新信息
            if fn not in msgs.keys():
                # print("{} is not in the msgs".format(fn, self.files))
                pass
            else:
                rev_msg = rev_msg + msgs[fn]

        msg_n = len(rev_msg)
        if msg_n > 0:
            self.send_msg(rev_msg)

        return msg_n

    def __setattr__(self, key, value):
        if key == "template__":
            warn("we can not change the value of {}".format(key), UserWarning)
        else:
            super().__setattr__(key, value)


def get_timestr():
    time_ = time.time()
    ms = str(int((time_ % 1) * 1000)).zfill(3)
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_))
    timestr = "{}.{}".format(timestr, ms)
    return timestr


if __name__ == '__main__':
    rev = Receiver(is_test=False)
    rev.name = "default"
    with open(".\\tmp\\trade.log", 'r', encoding="utf-8") as f:
        context = f.readlines()
    msgs = {"wechat_log": context}
    rev.get_msg(msgs)