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
    '''
    :param models:
    :param file_msg_dict: {name: context}
    :return:
    '''
    if len(file_msg_dict) == 0:
        return

    for m in models:
        m.get_msg(file_msg_dict)


if __name__ == '__main__':
    models = get_models()
    context = ['测试消息1\n', '测试消息2\n']
    msgs = {"Python_trade": context, "C++_cancel": context}
    push_msg2models(models, msgs)

