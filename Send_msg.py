# author='lwz'
# coding:utf-8
# !/usr/bin/env python3
from Receiver import Receiver
from warnings import warn


def get_models(is_test=False):
    is_test = False
    R1 = Receiver(template_file='.\\tmp\\api.json',
                  conf_file='.\\tmp\\Receiver.json', is_test=is_test)
    return [R1]


def push_msg2models(models, file_msg_dict):
    if len(file_msg_dict) == 0:
        return

    for m in models:
        m.get_msg(file_msg_dict)


if __name__ == '__main__':
    models = get_models()
    with open(".\\tmp\\trade.log", 'r', encoding="utf-8") as f:
        lines = f.readlines()

    context = [line.replace("\n", "") for line in lines]
    msgs = {"wechat_log": context}
    push_msg2models(models, msgs)

